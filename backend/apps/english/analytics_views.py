"""
学习数据分析API视图模块

提供数据可视化API接口，返回ECharts兼容的JSON格式数据
支持多种图表类型：学习进度趋势、表达掌握分布、学习时间分析等
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal

from django.utils import timezone
from django.core.cache import cache
from django.db.models import Count, Avg, Sum, F, Q, Max, Min
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, Extract
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.openapi import OpenApiTypes

from .models import UserExpressionProgress, IdiomaticExpression
from .services import LearningAnalyticsService, MasteryLevel

User = get_user_model()
logger = logging.getLogger(__name__)


class LearningAnalyticsAPIViews:
    """学习分析API视图类"""
    
    def __init__(self):
        self.analytics_service = LearningAnalyticsService()
        self.cache_timeout = 300  # 5分钟缓存
        
    def get_cache_key(self, user_id: int, view_name: str, params: str = "") -> str:
        """生成缓存键"""
        return f"analytics:{user_id}:{view_name}:{params}"
    
    def format_echarts_response(
        self, 
        chart_type: str,
        title: str,
        data: Dict[str, Any],
        success: bool = True,
        message: str = ""
    ) -> Dict[str, Any]:
        """格式化ECharts兼容的响应数据"""
        return {
            "success": success,
            "message": message,
            "data": {
                "chart_type": chart_type,
                "title": title,
                "timestamp": timezone.now().isoformat(),
                "chart_data": data
            }
        }


# 创建视图实例
analytics_views = LearningAnalyticsAPIViews()


@extend_schema(
    summary="学习进度趋势分析",
    description="返回用户学习进度趋势数据，支持按天、周、月聚合",
    parameters=[
        OpenApiParameter(
            name="period",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="时间周期：day(天)、week(周)、month(月)",
            enum=["day", "week", "month"],
            default="day"
        ),
        OpenApiParameter(
            name="days",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="统计天数，默认30天",
            default=30
        )
    ],
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "message": {"type": "string"},
                "data": {
                    "type": "object",
                    "properties": {
                        "chart_type": {"type": "string"},
                        "title": {"type": "string"},
                        "chart_data": {
                            "type": "object",
                            "properties": {
                                "xAxis": {
                                    "type": "object",
                                    "properties": {
                                        "type": {"type": "string"},
                                        "data": {"type": "array", "items": {"type": "string"}}
                                    }
                                },
                                "series": {"type": "array"}
                            }
                        }
                    }
                }
            }
        }
    },
    tags=["学习数据分析"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def progress_trend(request):
    """学习进度趋势API"""
    try:
        user = request.user
        period = request.GET.get('period', 'day')
        days = int(request.GET.get('days', 30))
        
        # 生成缓存键
        cache_key = analytics_views.get_cache_key(
            user.id, 'progress_trend', f"{period}_{days}"
        )
        
        # 尝试从缓存获取，如果Redis连接失败则跳过缓存
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except Exception as e:
            logger.warning(f"缓存获取失败，跳过缓存: {e}")
            cached_data = None
        
        # 计算时间范围
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # 根据周期选择聚合函数
        if period == 'week':
            trunc_func = TruncWeek
            date_format = '%Y-W%U'
        elif period == 'month':
            trunc_func = TruncMonth
            date_format = '%Y-%m'
        else:  # day
            trunc_func = TruncDay
            date_format = '%Y-%m-%d'
        
        # 查询学习进度数据
        progress_data = UserExpressionProgress.objects.filter(
            user=user,
            updated_at__gte=start_date,
            updated_at__lte=end_date
        ).annotate(
            period=trunc_func('updated_at')
        ).values('period').annotate(
            total_expressions=Count('id'),
            avg_accuracy=Avg(F('correct_count') * 100.0 / F('total_attempts')),
            total_study_time=Sum('study_duration'),
            avg_efficiency=Avg('learning_efficiency')
        ).order_by('period')
        
        # 格式化数据为ECharts格式
        dates = []
        expressions_data = []
        accuracy_data = []
        study_time_data = []
        efficiency_data = []
        
        for item in progress_data:
            period_date = item['period']
            if period_date:
                dates.append(period_date.strftime(date_format))
                expressions_data.append(item['total_expressions'] or 0)
                accuracy_data.append(round(float(item['avg_accuracy'] or 0), 1))
                study_time_data.append(round(float(item['total_study_time'] or 0) / 60, 1))  # 转换为分钟
                efficiency_data.append(round(float(item['avg_efficiency'] or 0), 1))
        
        # 构建ECharts配置
        chart_data = {
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "cross"}
            },
            "legend": {
                "data": ["学习表达数", "平均准确率(%)", "学习时长(分钟)", "学习效率"]
            },
            "xAxis": {
                "type": "category",
                "data": dates
            },
            "yAxis": [
                {
                    "type": "value",
                    "name": "数量/时长",
                    "position": "left"
                },
                {
                    "type": "value",
                    "name": "百分比",
                    "position": "right",
                    "max": 100
                }
            ],
            "series": [
                {
                    "name": "学习表达数",
                    "type": "bar",
                    "data": expressions_data,
                    "yAxisIndex": 0
                },
                {
                    "name": "平均准确率(%)",
                    "type": "line",
                    "data": accuracy_data,
                    "yAxisIndex": 1,
                    "smooth": True
                },
                {
                    "name": "学习时长(分钟)",
                    "type": "bar",
                    "data": study_time_data,
                    "yAxisIndex": 0
                },
                {
                    "name": "学习效率",
                    "type": "line",
                    "data": efficiency_data,
                    "yAxisIndex": 1,
                    "smooth": True
                }
            ]
        }
        
        response_data = analytics_views.format_echarts_response(
            "line_bar_combo",
            f"学习进度趋势 - 最近{days}天",
            chart_data
        )
        
        # 缓存结果，如果Redis连接失败则跳过缓存
        try:
            cache.set(cache_key, response_data, analytics_views.cache_timeout)
        except Exception as e:
            logger.warning(f"缓存设置失败，跳过缓存: {e}")
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"获取学习进度趋势失败: {e}")
        return Response(
            analytics_views.format_echarts_response(
                "line_bar_combo",
                "学习进度趋势",
                {},
                success=False,
                message=str(e)
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="表达掌握分布分析",
    description="返回用户表达掌握度分布数据，显示不同掌握等级的表达数量",
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {
                    "type": "object",
                    "properties": {
                        "chart_data": {
                            "type": "object",
                            "properties": {
                                "series": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string"},
                                            "data": {"type": "array"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    tags=["学习数据分析"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mastery_distribution(request):
    """表达掌握分布API"""
    try:
        user = request.user
        
        # 生成缓存键
        cache_key = analytics_views.get_cache_key(user.id, 'mastery_distribution')
        
        # 尝试从缓存获取，如果Redis连接失败则跳过缓存
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except Exception as e:
            logger.warning(f"缓存获取失败，跳过缓存: {e}")
            cached_data = None
        
        # 获取用户所有学习进度
        progress_list = UserExpressionProgress.objects.filter(user=user)
        
        # 计算掌握度分布
        mastery_counts = {level.name: 0 for level in MasteryLevel}
        total_expressions = 0
        
        for progress in progress_list:
            mastery_analysis = analytics_views.analytics_service.calculate_mastery_level(
                user, progress.expression
            )
            mastery_counts[mastery_analysis.mastery_level.name] += 1
            total_expressions += 1
        
        # 格式化为ECharts饼图数据
        pie_data = []
        colors = {
            'UNKNOWN': '#95a5a6',
            'BEGINNER': '#e74c3c',
            'BASIC': '#f39c12',
            'INTERMEDIATE': '#f1c40f',
            'ADVANCED': '#2ecc71',
            'EXPERT': '#9b59b6'
        }
        
        mastery_labels = {
            'UNKNOWN': '未知',
            'BEGINNER': '初学者',
            'BASIC': '基础',
            'INTERMEDIATE': '中级',
            'ADVANCED': '高级',
            'EXPERT': '专家'
        }
        
        for level_name, count in mastery_counts.items():
            if count > 0:
                pie_data.append({
                    "name": mastery_labels[level_name],
                    "value": count,
                    "itemStyle": {"color": colors[level_name]}
                })
        
        # 构建ECharts配置
        chart_data = {
            "tooltip": {
                "trigger": "item",
                "formatter": "{a} <br/>{b}: {c} ({d}%)"
            },
            "legend": {
                "orient": "vertical",
                "left": "left",
                "data": [item["name"] for item in pie_data]
            },
            "series": [
                {
                    "name": "掌握度分布",
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "center": ["60%", "50%"],
                    "data": pie_data,
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 10,
                            "shadowOffsetX": 0,
                            "shadowColor": "rgba(0, 0, 0, 0.5)"
                        }
                    },
                    "label": {
                        "formatter": "{b}: {c}\n({d}%)"
                    }
                }
            ]
        }
        
        response_data = analytics_views.format_echarts_response(
            "pie",
            f"表达掌握分布 (总计: {total_expressions}个)",
            chart_data
        )
        
        # 缓存结果，如果Redis连接失败则跳过缓存
        try:
            cache.set(cache_key, response_data, analytics_views.cache_timeout)
        except Exception as e:
            logger.warning(f"缓存设置失败，跳过缓存: {e}")
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"获取掌握分布失败: {e}")
        return Response(
            analytics_views.format_echarts_response(
                "pie",
                "表达掌握分布",
                {},
                success=False,
                message=str(e)
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="学习时间分析",
    description="返回用户学习时间分析数据，包括每日学习时长、最佳学习时间段等",
    parameters=[
        OpenApiParameter(
            name="analysis_type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="分析类型：daily(每日时长)、hourly(小时分布)、weekly(每周分布)",
            enum=["daily", "hourly", "weekly"],
            default="daily"
        ),
        OpenApiParameter(
            name="days",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="统计天数，默认30天",
            default=30
        )
    ],
    responses={200: {"description": "学习时间分析数据"}},
    tags=["学习数据分析"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def time_analysis(request):
    """学习时间分析API"""
    try:
        user = request.user
        analysis_type = request.GET.get('analysis_type', 'daily')
        days = int(request.GET.get('days', 30))
        
        # 生成缓存键
        cache_key = analytics_views.get_cache_key(
            user.id, 'time_analysis', f"{analysis_type}_{days}"
        )
        
        # 尝试从缓存获取，如果Redis连接失败则跳过缓存
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except Exception as e:
            logger.warning(f"缓存获取失败，跳过缓存: {e}")
            cached_data = None
        
        # 计算时间范围
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # 根据分析类型构建不同的图表
        if analysis_type == 'hourly':
            chart_data = _build_hourly_analysis(user, start_date, end_date)
            title = "学习时间段分布"
            chart_type = "bar"
        elif analysis_type == 'weekly':
            chart_data = _build_weekly_analysis(user, start_date, end_date)
            title = "每周学习分布"
            chart_type = "radar"
        else:  # daily
            chart_data = _build_daily_analysis(user, start_date, end_date)
            title = f"每日学习时长 - 最近{days}天"
            chart_type = "line"
        
        response_data = analytics_views.format_echarts_response(
            chart_type,
            title,
            chart_data
        )
        
        # 缓存结果，如果Redis连接失败则跳过缓存
        try:
            cache.set(cache_key, response_data, analytics_views.cache_timeout)
        except Exception as e:
            logger.warning(f"缓存设置失败，跳过缓存: {e}")
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"获取学习时间分析失败: {e}")
        return Response(
            analytics_views.format_echarts_response(
                "line",
                "学习时间分析",
                {},
                success=False,
                message=str(e)
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="学习效率分析",
    description="返回用户学习效率分析数据，包括各维度效率指标",
    responses={200: {"description": "学习效率分析数据"}},
    tags=["学习数据分析"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def efficiency_analysis(request):
    """学习效率分析API"""
    try:
        user = request.user
        
        # 生成缓存键
        cache_key = analytics_views.get_cache_key(user.id, 'efficiency_analysis')
        
        # 尝试从缓存获取，如果Redis连接失败则跳过缓存
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except Exception as e:
            logger.warning(f"缓存获取失败，跳过缓存: {e}")
            cached_data = None
        
        # 获取学习效率数据
        efficiency_metrics = analytics_views.analytics_service.compute_learning_efficiency(user)
        
        # 构建雷达图数据
        indicators = [
            {"name": "总体效率", "max": 100},
            {"name": "时间效率", "max": 100},
            {"name": "准确率效率", "max": 100},
            {"name": "记忆效率", "max": 100},
            {"name": "进步速度", "max": 100}
        ]
        
        radar_data = [
            efficiency_metrics.overall_efficiency,
            efficiency_metrics.time_efficiency,
            efficiency_metrics.accuracy_efficiency,
            efficiency_metrics.retention_efficiency,
            efficiency_metrics.progress_velocity
        ]
        
        chart_data = {
            "tooltip": {},
            "radar": {
                "indicator": indicators,
                "radius": "70%"
            },
            "series": [
                {
                    "name": "学习效率",
                    "type": "radar",
                    "data": [
                        {
                            "value": radar_data,
                            "name": "当前效率",
                            "itemStyle": {"color": "#3498db"},
                            "areaStyle": {"opacity": 0.3}
                        }
                    ]
                }
            ]
        }
        
        response_data = analytics_views.format_echarts_response(
            "radar",
            "学习效率分析",
            chart_data
        )
        
        # 添加额外信息
        response_data["data"]["metrics"] = {
            "optimal_session_duration": efficiency_metrics.optimal_session_duration,
            "peak_performance_time": efficiency_metrics.peak_performance_time,
            "overall_score": efficiency_metrics.overall_efficiency
        }
        
        # 缓存结果，如果Redis连接失败则跳过缓存
        try:
            cache.set(cache_key, response_data, analytics_views.cache_timeout)
        except Exception as e:
            logger.warning(f"缓存设置失败，跳过缓存: {e}")
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"获取学习效率分析失败: {e}")
        return Response(
            analytics_views.format_echarts_response(
                "radar",
                "学习效率分析",
                {},
                success=False,
                message=str(e)
            ),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="学习洞察建议",
    description="返回个性化学习洞察和建议",
    parameters=[
        OpenApiParameter(
            name="limit",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="返回洞察数量，默认10个",
            default=10
        )
    ],
    responses={200: {"description": "学习洞察数据"}},
    tags=["学习数据分析"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def learning_insights(request):
    """学习洞察API"""
    try:
        user = request.user
        limit = int(request.GET.get('limit', 10))
        
        # 生成缓存键
        cache_key = analytics_views.get_cache_key(user.id, 'learning_insights', str(limit))
        
        # 尝试从缓存获取，如果Redis连接失败则跳过缓存
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except Exception as e:
            logger.warning(f"缓存获取失败，跳过缓存: {e}")
            cached_data = None
        
        # 获取学习洞察
        insights = analytics_views.analytics_service.generate_learning_insights(user, limit)
        
        # 格式化洞察数据
        insights_data = []
        for insight in insights:
            insights_data.append({
                "type": insight.insight_type,
                "title": insight.title,
                "description": insight.description,
                "priority": insight.priority,
                "actionable": insight.actionable,
                "data": insight.data
            })
        
        response_data = {
            "success": True,
            "message": "",
            "data": {
                "total_insights": len(insights_data),
                "insights": insights_data,
                "timestamp": timezone.now().isoformat()
            }
        }
        
        # 缓存结果，如果Redis连接失败则跳过缓存
        try:
            cache.set(cache_key, response_data, analytics_views.cache_timeout)
        except Exception as e:
            logger.warning(f"缓存设置失败，跳过缓存: {e}")
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"获取学习洞察失败: {e}")
        return Response(
            {
                "success": False,
                "message": str(e),
                "data": {"insights": []}
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== 辅助函数 ====================

def _build_daily_analysis(user: User, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """构建每日学习时长分析"""
    daily_data = UserExpressionProgress.objects.filter(
        user=user,
        updated_at__gte=start_date,
        updated_at__lte=end_date
    ).annotate(
        date=TruncDay('updated_at')
    ).values('date').annotate(
        total_time=Sum('study_duration'),
        expression_count=Count('id')
    ).order_by('date')
    
    dates = []
    times = []
    counts = []
    
    for item in daily_data:
        if item['date']:
            dates.append(item['date'].strftime('%m-%d'))
            times.append(round(float(item['total_time'] or 0) / 60, 1))  # 转换为分钟
            counts.append(item['expression_count'] or 0)
    
    return {
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["学习时长(分钟)", "学习表达数"]},
        "xAxis": {"type": "category", "data": dates},
        "yAxis": [
            {"type": "value", "name": "时长(分钟)"},
            {"type": "value", "name": "表达数", "position": "right"}
        ],
        "series": [
            {
                "name": "学习时长(分钟)",
                "type": "line",
                "data": times,
                "smooth": True,
                "yAxisIndex": 0
            },
            {
                "name": "学习表达数",
                "type": "bar",
                "data": counts,
                "yAxisIndex": 1
            }
        ]
    }


def _build_hourly_analysis(user: User, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """构建小时分布分析"""
    # 这里简化处理，实际应该根据学习记录的时间戳分析
    progress_list = UserExpressionProgress.objects.filter(
        user=user,
        updated_at__gte=start_date,
        updated_at__lte=end_date
    )
    
    # 统计最佳学习时间段分布
    time_distribution = {}
    for progress in progress_list:
        best_time = progress.best_learning_time or 'morning'
        time_distribution[best_time] = time_distribution.get(best_time, 0) + 1
    
    time_labels = {
        'morning': '上午(6-12时)',
        'afternoon': '下午(12-18时)',
        'evening': '晚上(18-24时)',
        'night': '深夜(0-6时)'
    }
    
    categories = []
    values = []
    
    for time_key, count in time_distribution.items():
        categories.append(time_labels.get(time_key, time_key))
        values.append(count)
    
    return {
        "tooltip": {"trigger": "axis"},
        "xAxis": {"type": "category", "data": categories},
        "yAxis": {"type": "value", "name": "学习次数"},
        "series": [
            {
                "name": "学习分布",
                "type": "bar",
                "data": values,
                "itemStyle": {"color": "#3498db"}
            }
        ]
    }


def _build_weekly_analysis(user: User, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """构建每周学习分布分析"""
    weekly_data = UserExpressionProgress.objects.filter(
        user=user,
        updated_at__gte=start_date,
        updated_at__lte=end_date
    ).annotate(
        weekday=Extract('updated_at', 'week_day')
    ).values('weekday').annotate(
        total_time=Sum('study_duration'),
        expression_count=Count('id')
    ).order_by('weekday')
    
    weekday_names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    weekday_data = [0] * 7
    
    for item in weekly_data:
        weekday = int(item['weekday']) - 1  # 调整为0-6
        if 0 <= weekday < 7:
            weekday_data[weekday] = round(float(item['total_time'] or 0) / 60, 1)
    
    return {
        "tooltip": {},
        "radar": {
            "indicator": [{"name": name, "max": max(weekday_data) * 1.2 if weekday_data else 100} 
                         for name in weekday_names],
            "radius": "70%"
        },
        "series": [
            {
                "name": "每周学习分布",
                "type": "radar",
                "data": [
                    {
                        "value": weekday_data,
                        "name": "学习时长(分钟)",
                        "itemStyle": {"color": "#2ecc71"},
                        "areaStyle": {"opacity": 0.3}
                    }
                ]
            }
        ]
    }
