#!/usr/bin/env python
"""
测试学习报告生成系统
"""

import os
import sys
import django
from datetime import datetime, timedelta

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils import timezone
from apps.english.models import IdiomaticExpression, UserExpressionProgress
from apps.english.report_views import LearningReportViewSet
from apps.english.services.learning_analytics import LearningAnalyticsService


def create_test_data():
    """创建测试数据"""
    print("创建测试数据...")
    
    # 创建测试用户
    user, created = User.objects.get_or_create(
        username='test_learner',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'Learner'
        }
    )
    
    if created:
        print(f"创建测试用户: {user.username}")
    
    # 创建测试表达
    expressions_data = [
        {
            'expression': 'break the ice',
            'meaning': '打破僵局，开始交谈',
            'category': 'social',
            'difficulty_level': 3,
            'popularity_score': 8.5
        },
        {
            'expression': 'piece of cake',
            'meaning': '轻而易举的事',
            'category': 'daily',
            'difficulty_level': 2,
            'popularity_score': 9.0
        },
        {
            'expression': 'hit the nail on the head',
            'meaning': '说到点子上',
            'category': 'business',
            'difficulty_level': 4,
            'popularity_score': 7.5
        },
        {
            'expression': 'spill the beans',
            'meaning': '泄露秘密',
            'category': 'daily',
            'difficulty_level': 3,
            'popularity_score': 6.8
        },
        {
            'expression': 'think outside the box',
            'meaning': '跳出思维定式',
            'category': 'business',
            'difficulty_level': 4,
            'popularity_score': 8.2
        }
    ]
    
    expressions = []
    for expr_data in expressions_data:
        expression, created = IdiomaticExpression.objects.get_or_create(
            expression=expr_data['expression'],
            defaults=expr_data
        )
        expressions.append(expression)
        if created:
            print(f"创建表达: {expression.expression}")
    
    # 创建学习进度记录
    print("创建学习进度记录...")
    base_date = timezone.now() - timedelta(days=30)
    
    for i, expression in enumerate(expressions):
        for day in range(30):
            record_date = base_date + timedelta(days=day)
            
            # 模拟学习进度
            attempts = min(day // 3 + 1, 10)
            accuracy = max(0.4, min(0.95, 0.6 + (day * 0.01) + (i * 0.05)))
            mastery = max(0.1, min(0.9, accuracy * 0.8 + (day * 0.008)))
            
            # 计算掌握度（0-100整数）
            mastery_int = int(mastery * 100)
            
            progress, created = UserExpressionProgress.objects.get_or_create(
                user=user,
                expression=expression,
                defaults={
                    'mastery_level': mastery_int,
                    'review_count': attempts,
                    'correct_count': int(attempts * accuracy),
                    'total_attempts': attempts,
                    'consecutive_correct': max(0, attempts - 2),
                    'study_duration': (15 + (i * 3)) * 60,  # 转换为秒
                    'difficulty_rating': 3,  # 1-5 整数值，3表示中等难度
                    'learning_efficiency': round(accuracy * mastery, 2),
                    'engagement_score': int(min(90, 70 + (day * 0.5))),
                    'retention_rate': round(max(0.6, mastery * 0.9), 2),
                    'average_response_time': round(5.0 + (i * 0.5), 2),
                    'max_consecutive_correct': max(0, attempts - 1),
                    'last_reviewed': record_date,
                    'updated_at': record_date
                }
            )
            
            if created and day % 10 == 0:
                print(f"  创建进度记录: {expression.expression} - Day {day}")
    
    print(f"测试数据创建完成！用户: {user.username}")
    return user


def test_report_generation():
    """测试报告生成"""
    print("\n=== 测试报告生成功能 ===")
    
    # 创建测试数据
    user = create_test_data()
    
    # 创建报告视图集实例
    viewset = LearningReportViewSet()
    
    # 模拟请求对象
    class MockRequest:
        def __init__(self, user):
            self.user = user
            self.query_params = {
                'start_date': (timezone.now() - timedelta(days=30)).date().isoformat(),
                'end_date': timezone.now().date().isoformat(),
                'format': 'json'
            }
    
    request = MockRequest(user)
    
    try:
        # 测试报告数据生成
        print("生成报告数据...")
        start_date = datetime.strptime(request.query_params['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.query_params['end_date'], '%Y-%m-%d').date()
        
        report_data = viewset._generate_report_data(user, start_date, end_date)
        
        print(f"✅ 报告生成成功!")
        print(f"   用户: {report_data['report_info']['username']}")
        print(f"   时间范围: {report_data['report_info']['start_date']} 至 {report_data['report_info']['end_date']}")
        print(f"   总表达数: {report_data['summary']['total_expressions']}")
        print(f"   掌握表达数: {report_data['summary']['mastered_expressions']}")
        print(f"   掌握率: {report_data['summary']['mastery_rate']:.1%}")
        print(f"   总学习时长: {report_data['summary']['total_study_time']:.1f} 分钟")
        print(f"   学习连续天数: {report_data['summary']['learning_streak']}")
        print(f"   每日进度记录: {len(report_data['daily_progress'])} 天")
        print(f"   薄弱环节: {len(report_data['weak_areas'])} 个")
        print(f"   学习建议: {len(report_data['recommendations'])} 条")
        
        # 显示一些具体数据
        if report_data['weak_areas']:
            print(f"\n薄弱环节示例:")
            for area in report_data['weak_areas'][:3]:
                print(f"  - {area['expression']}: 掌握度 {area['mastery_level']:.2f}, 准确率 {area['accuracy_rate']:.1%}")
        
        if report_data['recommendations']:
            print(f"\n学习建议:")
            for rec in report_data['recommendations']:
                print(f"  - [{rec['priority']}] {rec['title']}: {rec['description']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 报告生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_learning_analytics():
    """测试学习分析服务"""
    print("\n=== 测试学习分析服务 ===")
    
    try:
        analytics_service = LearningAnalyticsService()
        
        # 获取测试用户的进度记录
        user = User.objects.get(username='test_learner')
        progress_records = UserExpressionProgress.objects.filter(user=user)
        
        print(f"找到 {progress_records.count()} 条学习记录")
        
        # 测试各种分析功能
        for record in progress_records[:3]:
            print(f"\n分析表达: {record.expression.expression}")
            
            # 计算掌握度
            mastery = analytics_service.calculate_mastery_level(record.user, record.expression)
            print(f"  掌握度: {mastery.mastery_level.name} (置信度: {mastery.confidence_score:.3f})")
            
            # 计算学习效率
            efficiency = analytics_service.calculate_learning_efficiency(record)
            print(f"  学习效率: {efficiency:.3f}")
            
            # 分析遗忘曲线
            forgetting_curve = analytics_service.analyze_forgetting_curve(record.user, record.expression)
            print(f"  遗忘率: {forgetting_curve.forgetting_rate:.3f}, 半衰期: {forgetting_curve.half_life:.1f}天")
        
        print("✅ 学习分析服务测试通过!")
        return True
        
    except Exception as e:
        print(f"❌ 学习分析服务测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("=== 学习报告生成系统测试 ===")
    
    # 测试学习分析服务
    analytics_success = test_learning_analytics()
    
    # 测试报告生成
    report_success = test_report_generation()
    
    # 总结
    print(f"\n=== 测试总结 ===")
    print(f"学习分析服务: {'✅ 通过' if analytics_success else '❌ 失败'}")
    print(f"报告生成功能: {'✅ 通过' if report_success else '❌ 失败'}")
    
    if analytics_success and report_success:
        print("\n🎉 所有测试通过！学习报告生成系统运行正常。")
        return True
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
