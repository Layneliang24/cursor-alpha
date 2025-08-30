"""
学习报告生成API视图
提供学习报告的生成、下载和管理功能
"""

from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
import json
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64

from .models import UserExpressionProgress, IdiomaticExpression
from .services.learning_analytics import LearningAnalyticsService


class LearningReportViewSet(viewsets.ViewSet):
    """学习报告生成和管理"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="生成学习报告",
        description="生成指定时间范围内的学习报告，支持多种格式",
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='报告开始日期 (YYYY-MM-DD)',
                required=False
            ),
            OpenApiParameter(
                name='end_date', 
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='报告结束日期 (YYYY-MM-DD)',
                required=False
            ),
            OpenApiParameter(
                name='format',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='报告格式: json, pdf, excel',
                required=False,
                default='json'
            ),
            OpenApiParameter(
                name='include_charts',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='是否包含图表 (PDF格式)',
                required=False,
                default=False
            )
        ],
        tags=['Reports']
    )
    @action(detail=False, methods=['get'])
    def generate(self, request):
        """生成学习报告"""
        try:
            # 获取参数
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            report_format = request.query_params.get('format', 'json')
            include_charts = request.query_params.get('include_charts', 'false').lower() == 'true'
            
            # 设置默认日期范围（最近30天）
            if not end_date:
                end_date = timezone.now().date()
            else:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                
            if not start_date:
                start_date = end_date - timedelta(days=30)
            else:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            
            # 生成报告数据
            report_data = self._generate_report_data(request.user, start_date, end_date)
            
            # 根据格式返回不同响应
            if report_format == 'pdf':
                return self._generate_pdf_report(report_data, include_charts)
            elif report_format == 'excel':
                return self._generate_excel_report(report_data)
            else:
                return Response(report_data)
                
        except Exception as e:
            return Response(
                {'error': f'生成报告失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="获取报告模板",
        description="获取可用的报告模板列表",
        tags=['Reports']
    )
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """获取报告模板"""
        templates = [
            {
                'id': 'weekly',
                'name': '周报',
                'description': '每周学习进度报告',
                'default_period': 7
            },
            {
                'id': 'monthly',
                'name': '月报',
                'description': '月度学习总结报告',
                'default_period': 30
            },
            {
                'id': 'quarterly',
                'name': '季报',
                'description': '季度学习分析报告',
                'default_period': 90
            },
            {
                'id': 'custom',
                'name': '自定义',
                'description': '自定义时间范围报告',
                'default_period': None
            }
        ]
        
        return Response({
            'templates': templates,
            'supported_formats': ['json', 'pdf', 'excel']
        })
    
    def _generate_report_data(self, user, start_date, end_date):
        """生成报告数据"""
        analytics_service = LearningAnalyticsService()
        
        # 获取用户在指定时间范围内的学习进度
        progress_records = UserExpressionProgress.objects.filter(
            user=user,
            updated_at__date__range=[start_date, end_date]
        ).select_related('expression')
        
        # 基础统计
        total_expressions = progress_records.count()
        mastered_expressions = progress_records.filter(mastery_level__gte=80).count()  # 掌握度>=80
        total_study_time = sum(record.study_duration or 0 for record in progress_records) / 60  # 转换为分钟
        total_attempts = sum(record.total_attempts or 0 for record in progress_records)
        
        # 学习效率分析
        efficiency_data = []
        for record in progress_records:
            if record.total_attempts > 0:
                efficiency = analytics_service.calculate_learning_efficiency(record)
                efficiency_data.append({
                    'expression': record.expression.expression,
                    'efficiency': efficiency,
                    'mastery_level': record.mastery_level,
                    'attempts': record.total_attempts
                })
        
        # 按日统计
        daily_stats = {}
        for record in progress_records:
            date_key = record.updated_at.date().isoformat()
            if date_key not in daily_stats:
                daily_stats[date_key] = {
                    'date': date_key,
                    'expressions_practiced': 0,
                    'study_time': 0,
                    'total_attempts': 0,
                    'accuracy_sum': 0,
                    'accuracy_count': 0
                }
            
            daily_stats[date_key]['expressions_practiced'] += 1
            daily_stats[date_key]['study_time'] += (record.study_duration or 0) / 60  # 转换为分钟
            daily_stats[date_key]['total_attempts'] += record.total_attempts or 0
            
            # 计算准确率
            accuracy = (record.correct_count / record.total_attempts) if record.total_attempts > 0 else 0
            daily_stats[date_key]['accuracy_sum'] += accuracy
            daily_stats[date_key]['accuracy_count'] += 1
        
        # 计算平均准确率
        for stats in daily_stats.values():
            if stats['accuracy_count'] > 0:
                stats['average_accuracy'] = stats['accuracy_sum'] / stats['accuracy_count']
            else:
                stats['average_accuracy'] = 0
            # 清理临时字段
            del stats['accuracy_sum']
            del stats['accuracy_count']
        
        # 薄弱环节分析
        weak_areas = []
        for record in progress_records.filter(mastery_level__lt=60):  # 掌握度<60
            accuracy = (record.correct_count / record.total_attempts) if record.total_attempts > 0 else 0
            weak_areas.append({
                'expression': record.expression.expression,
                'category': record.expression.category,
                'mastery_level': record.mastery_level / 100.0,  # 转换为0-1范围
                'accuracy_rate': accuracy,
                'attempts': record.total_attempts or 0,
                'last_practiced': record.updated_at.isoformat()
            })
        
        # 学习建议
        recommendations = self._generate_recommendations(progress_records, analytics_service)
        
        return {
            'report_info': {
                'user_id': user.id,
                'username': user.username,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'generated_at': timezone.now().isoformat(),
                'period_days': (end_date - start_date).days + 1
            },
            'summary': {
                'total_expressions': total_expressions,
                'mastered_expressions': mastered_expressions,
                'mastery_rate': mastered_expressions / total_expressions if total_expressions > 0 else 0,
                'total_study_time': total_study_time,
                'total_attempts': total_attempts,
                'average_study_time_per_day': total_study_time / ((end_date - start_date).days + 1),
                'learning_streak': self._calculate_learning_streak(user, end_date)
            },
            'daily_progress': sorted(daily_stats.values(), key=lambda x: x['date']),
            'efficiency_analysis': efficiency_data,
            'weak_areas': weak_areas[:10],  # 前10个薄弱环节
            'recommendations': recommendations,
            'achievements': self._get_user_achievements(user, progress_records),
            'learning_patterns': self._analyze_learning_patterns(progress_records)
        }
    
    def _generate_recommendations(self, progress_records, analytics_service):
        """生成学习建议"""
        recommendations = []
        
        # 分析薄弱环节
        weak_records = progress_records.filter(mastery_level__lt=60)  # 掌握度<60
        if weak_records.exists():
            recommendations.append({
                'type': 'practice',
                'priority': 'high',
                'title': '重点练习薄弱表达',
                'description': f'您有{weak_records.count()}个表达需要重点练习',
                'action': {
                    'type': 'practice_weak',
                    'target_ids': list(weak_records.values_list('expression_id', flat=True)[:5])
                }
            })
        
        # 分析学习频率
        recent_records = progress_records.filter(
            updated_at__gte=timezone.now() - timedelta(days=7)
        )
        if recent_records.count() < 3:
            recommendations.append({
                'type': 'frequency',
                'priority': 'medium',
                'title': '增加学习频率',
                'description': '建议每天至少练习3个表达以保持学习效果',
                'action': {
                    'type': 'set_daily_goal',
                    'suggested_goal': 5
                }
            })
        
        # 分析学习时间
        avg_study_time = sum(r.study_duration or 0 for r in recent_records) / max(recent_records.count(), 1)
        if avg_study_time < 10:  # 少于10分钟
            recommendations.append({
                'type': 'time',
                'priority': 'low',
                'title': '延长学习时间',
                'description': '建议每次学习时间不少于15分钟以提高效果',
                'action': {
                    'type': 'time_reminder',
                    'suggested_duration': 15
                }
            })
        
        return recommendations
    
    def _calculate_learning_streak(self, user, end_date):
        """计算学习连续天数"""
        streak = 0
        current_date = end_date
        
        while True:
            # 检查当天是否有学习记录
            has_activity = UserExpressionProgress.objects.filter(
                user=user,
                updated_at__date=current_date
            ).exists()
            
            if has_activity:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
                
            # 防止无限循环，最多查询100天
            if streak >= 100:
                break
        
        return streak
    
    def _get_user_achievements(self, user, progress_records):
        """获取用户成就"""
        achievements = []
        
        total_expressions = progress_records.count()
        mastered_count = progress_records.filter(mastery_level__gte=0.8).count()
        
        # 学习数量成就
        if total_expressions >= 100:
            achievements.append({
                'id': 'learner_100',
                'title': '学习达人',
                'description': '学习了100个表达',
                'icon': 'el-icon-medal',
                'unlocked': True,
                'unlocked_at': timezone.now().isoformat()
            })
        elif total_expressions >= 50:
            achievements.append({
                'id': 'learner_50',
                'title': '勤奋学习者',
                'description': '学习了50个表达',
                'icon': 'el-icon-star-on',
                'unlocked': True,
                'unlocked_at': timezone.now().isoformat()
            })
        
        # 掌握度成就
        if mastered_count >= 50:
            achievements.append({
                'id': 'master_50',
                'title': '表达大师',
                'description': '掌握了50个表达',
                'icon': 'el-icon-trophy',
                'unlocked': True,
                'unlocked_at': timezone.now().isoformat()
            })
        
        # 连续学习成就
        streak = self._calculate_learning_streak(user, timezone.now().date())
        if streak >= 30:
            achievements.append({
                'id': 'streak_30',
                'title': '持之以恒',
                'description': '连续学习30天',
                'icon': 'el-icon-timer',
                'unlocked': True,
                'unlocked_at': timezone.now().isoformat()
            })
        elif streak >= 7:
            achievements.append({
                'id': 'streak_7',
                'title': '坚持不懈',
                'description': '连续学习7天',
                'icon': 'el-icon-check',
                'unlocked': True,
                'unlocked_at': timezone.now().isoformat()
            })
        
        return achievements
    
    def _analyze_learning_patterns(self, progress_records):
        """分析学习模式"""
        patterns = {}
        
        # 按小时分析学习时间偏好
        hour_stats = {}
        for record in progress_records:
            hour = record.updated_at.hour
            hour_stats[hour] = hour_stats.get(hour, 0) + 1
        
        if hour_stats:
            best_hour = max(hour_stats, key=hour_stats.get)
            patterns['best_learning_time'] = {
                'hour': best_hour,
                'label': f'{best_hour}:00-{best_hour+1}:00',
                'frequency': hour_stats[best_hour]
            }
        
        # 分析学习难度偏好
        difficulty_stats = {}
        for record in progress_records:
            difficulty = record.difficulty_rating or 'unknown'
            difficulty_stats[difficulty] = difficulty_stats.get(difficulty, 0) + 1
        
        patterns['difficulty_preference'] = difficulty_stats
        
        # 分析学习效率趋势
        efficiency_trend = []
        sorted_records = progress_records.order_by('updated_at')
        
        for i, record in enumerate(sorted_records):
            if i >= 5:  # 至少5个记录才计算趋势
                recent_records = sorted_records[i-4:i+1]
                avg_efficiency = sum(r.learning_efficiency or 0 for r in recent_records) / 5
                efficiency_trend.append({
                    'date': record.updated_at.date().isoformat(),
                    'efficiency': avg_efficiency
                })
        
        patterns['efficiency_trend'] = efficiency_trend[-30:]  # 最近30个数据点
        
        return patterns
    
    def _generate_pdf_report(self, report_data, include_charts=False):
        """生成PDF报告"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # 标题
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # 居中
        )
        
        story.append(Paragraph('学习报告', title_style))
        story.append(Spacer(1, 20))
        
        # 报告信息
        info = report_data['report_info']
        info_text = f"""
        <b>用户:</b> {info['username']}<br/>
        <b>报告期间:</b> {info['start_date']} 至 {info['end_date']}<br/>
        <b>生成时间:</b> {datetime.fromisoformat(info['generated_at']).strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>统计天数:</b> {info['period_days']} 天
        """
        story.append(Paragraph(info_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # 学习概览
        summary = report_data['summary']
        summary_data = [
            ['指标', '数值'],
            ['学习表达总数', str(summary['total_expressions'])],
            ['已掌握表达', str(summary['mastered_expressions'])],
            ['掌握率', f"{summary['mastery_rate']:.1%}"],
            ['总学习时长', f"{summary['total_study_time']:.1f} 分钟"],
            ['平均每日学习', f"{summary['average_study_time_per_day']:.1f} 分钟"],
            ['学习连续天数', str(summary['learning_streak'])]
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph('学习概览', styles['Heading2']))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # 薄弱环节
        if report_data['weak_areas']:
            story.append(Paragraph('薄弱环节分析', styles['Heading2']))
            weak_data = [['表达', '分类', '掌握度', '准确率', '练习次数']]
            
            for area in report_data['weak_areas'][:10]:
                weak_data.append([
                    area['expression'],
                    area['category'],
                    f"{area['mastery_level']:.2f}",
                    f"{area['accuracy_rate']:.1%}",
                    str(area['attempts'])
                ])
            
            weak_table = Table(weak_data)
            weak_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightcoral),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(weak_table)
            story.append(Spacer(1, 20))
        
        # 学习建议
        if report_data['recommendations']:
            story.append(Paragraph('学习建议', styles['Heading2']))
            for i, rec in enumerate(report_data['recommendations'], 1):
                rec_text = f"<b>{i}. {rec['title']}</b><br/>{rec['description']}"
                story.append(Paragraph(rec_text, styles['Normal']))
                story.append(Spacer(1, 10))
        
        # 生成PDF
        doc.build(story)
        buffer.seek(0)
        
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f"learning_report_{info['start_date']}_{info['end_date']}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    def _generate_excel_report(self, report_data):
        """生成Excel报告"""
        try:
            import pandas as pd
            from io import BytesIO
            
            buffer = BytesIO()
            
            # 创建Excel writer
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                # 概览表
                summary_df = pd.DataFrame([report_data['summary']])
                summary_df.to_excel(writer, sheet_name='学习概览', index=False)
                
                # 每日进度表
                if report_data['daily_progress']:
                    daily_df = pd.DataFrame(report_data['daily_progress'])
                    daily_df.to_excel(writer, sheet_name='每日进度', index=False)
                
                # 效率分析表
                if report_data['efficiency_analysis']:
                    efficiency_df = pd.DataFrame(report_data['efficiency_analysis'])
                    efficiency_df.to_excel(writer, sheet_name='效率分析', index=False)
                
                # 薄弱环节表
                if report_data['weak_areas']:
                    weak_df = pd.DataFrame(report_data['weak_areas'])
                    weak_df.to_excel(writer, sheet_name='薄弱环节', index=False)
            
            buffer.seek(0)
            
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            info = report_data['report_info']
            filename = f"learning_report_{info['start_date']}_{info['end_date']}.xlsx"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except ImportError:
            return Response(
                {'error': '缺少pandas依赖，无法生成Excel报告'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LearningGoalViewSet(viewsets.ViewSet):
    """学习目标管理"""
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="获取学习目标列表",
        description="获取用户的学习目标列表",
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='目标状态: active, completed, paused',
                required=False
            )
        ],
        tags=['Learning Goals']
    )
    def list(self, request):
        """获取学习目标列表"""
        # 这里应该有实际的模型，暂时返回模拟数据
        goals = [
            {
                'id': 1,
                'title': '掌握商务英语表达',
                'description': '学习并掌握50个常用商务英语表达',
                'target_expressions': 50,
                'current_progress': 23,
                'status': 'active',
                'priority': 'high',
                'deadline': '2025-09-30',
                'created_at': '2025-08-01T00:00:00Z',
                'completion_rate': 0.46
            },
            {
                'id': 2,
                'title': '日常对话提升',
                'description': '提升日常英语对话能力',
                'target_expressions': 30,
                'current_progress': 15,
                'status': 'active',
                'priority': 'medium',
                'deadline': '2025-10-15',
                'created_at': '2025-08-15T00:00:00Z',
                'completion_rate': 0.50
            }
        ]
        
        # 根据状态过滤
        status_filter = request.query_params.get('status')
        if status_filter:
            goals = [g for g in goals if g['status'] == status_filter]
        
        return Response({
            'results': goals,
            'count': len(goals)
        })
    
    @extend_schema(
        summary="创建学习目标",
        description="创建新的学习目标",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string', 'description': '目标标题'},
                    'description': {'type': 'string', 'description': '目标描述'},
                    'target_expressions': {'type': 'integer', 'description': '目标表达数量'},
                    'priority': {'type': 'string', 'enum': ['low', 'medium', 'high'], 'description': '优先级'},
                    'deadline': {'type': 'string', 'format': 'date', 'description': '截止日期'}
                },
                'required': ['title', 'target_expressions', 'deadline']
            }
        },
        tags=['Learning Goals']
    )
    def create(self, request):
        """创建学习目标"""
        data = request.data
        
        # 验证必需字段
        required_fields = ['title', 'target_expressions', 'deadline']
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'缺少必需字段: {field}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 创建目标（这里应该保存到数据库）
        goal = {
            'id': len(request.user.username) + len(data['title']),  # 模拟ID
            'title': data['title'],
            'description': data.get('description', ''),
            'target_expressions': data['target_expressions'],
            'current_progress': 0,
            'status': 'active',
            'priority': data.get('priority', 'medium'),
            'deadline': data['deadline'],
            'created_at': timezone.now().isoformat(),
            'completion_rate': 0.0
        }
        
        return Response(goal, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="更新学习目标",
        description="更新学习目标信息或进度",
        tags=['Learning Goals']
    )
    def update(self, request, pk=None):
        """更新学习目标"""
        # 这里应该更新实际的数据库记录
        return Response({
            'message': '目标更新成功',
            'goal_id': pk
        })
    
    @extend_schema(
        summary="删除学习目标",
        description="删除指定的学习目标",
        tags=['Learning Goals']
    )
    def destroy(self, request, pk=None):
        """删除学习目标"""
        # 这里应该删除实际的数据库记录
        return Response({
            'message': '目标删除成功'
        }, status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        summary="目标进度追踪",
        description="获取目标的详细进度追踪数据",
        tags=['Learning Goals']
    )
    @action(detail=True, methods=['get'])
    def progress_tracking(self, request, pk=None):
        """目标进度追踪"""
        # 模拟进度追踪数据
        tracking_data = {
            'goal_id': pk,
            'progress_history': [
                {'date': '2025-08-01', 'progress': 0, 'daily_target': 2},
                {'date': '2025-08-02', 'progress': 3, 'daily_target': 2},
                {'date': '2025-08-03', 'progress': 5, 'daily_target': 2},
                {'date': '2025-08-04', 'progress': 8, 'daily_target': 2},
                {'date': '2025-08-05', 'progress': 10, 'daily_target': 2}
            ],
            'milestones': [
                {'percentage': 25, 'reached': True, 'date': '2025-08-10'},
                {'percentage': 50, 'reached': False, 'estimated_date': '2025-09-01'},
                {'percentage': 75, 'reached': False, 'estimated_date': '2025-09-15'},
                {'percentage': 100, 'reached': False, 'estimated_date': '2025-09-30'}
            ],
            'current_pace': {
                'expressions_per_day': 1.2,
                'projected_completion': '2025-10-15',
                'on_track': False,
                'days_behind': 5
            }
        }
        
        return Response(tracking_data)
