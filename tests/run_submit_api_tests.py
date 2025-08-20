#!/usr/bin/env python
"""
Submit API完整测试套件运行脚本

包含：
1. 单元测试
2. 集成测试  
3. 回归测试
4. 性能测试
"""

import os
import sys
import django
import subprocess
import time
from datetime import datetime

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

def run_test_suite():
    """运行完整的Submit API测试套件"""
    
    print("=" * 80)
    print("Submit API 完整测试套件")
    print("=" * 80)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试文件列表
    test_files = [
        {
            'name': 'Submit API 单元测试',
            'file': 'tests/unit/test_typing_practice_submit.py',
            'description': '基本功能、边界条件、错误处理测试'
        },
        {
            'name': 'Submit API 集成测试', 
            'file': 'tests/integration/test_typing_practice_submit_integration.py',
            'description': '与其他系统组件的集成测试'
        },
        {
            'name': 'Submit API 回归测试',
            'file': 'tests/regression/english/test_typing_practice_submit_regression.py',
            'description': '防止关键功能回归的测试'
        }
    ]
    
    results = []
    total_start_time = time.time()
    
    for test_info in test_files:
        print(f"正在运行: {test_info['name']}")
        print(f"描述: {test_info['description']}")
        print(f"文件: {test_info['file']}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # 运行pytest
            cmd = [
                'python', '-m', 'pytest', 
                test_info['file'],
                '-v',
                '--tb=short',
                '--disable-warnings'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if result.returncode == 0:
                status = "✅ 通过"
                print(f"状态: {status}")
                print(f"耗时: {duration:.2f}秒")
            else:
                status = "❌ 失败"
                print(f"状态: {status}")
                print(f"耗时: {duration:.2f}秒")
                print("错误输出:")
                print(result.stderr)
                print("标准输出:")
                print(result.stdout)
            
            results.append({
                'name': test_info['name'],
                'file': test_info['file'],
                'status': status,
                'duration': duration,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            })
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            status = f"❌ 异常: {str(e)}"
            print(f"状态: {status}")
            
            results.append({
                'name': test_info['name'],
                'file': test_info['file'],
                'status': status,
                'duration': duration,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e)
            })
        
        print()
    
    # 生成测试报告
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    print("=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    passed = sum(1 for r in results if r['returncode'] == 0)
    failed = len(results) - passed
    
    for result in results:
        print(f"{result['status']} {result['name']}")
        print(f"   文件: {result['file']}")
        print(f"   耗时: {result['duration']:.2f}秒")
        if result['returncode'] != 0:
            print(f"   错误: {result['stderr'][:100]}...")
        print()
    
    print(f"总计: {len(results)} 个测试套件")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print(f"总耗时: {total_duration:.2f}秒")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 保存详细报告
    save_detailed_report(results, total_duration)
    
    return failed == 0

def save_detailed_report(results, total_duration):
    """保存详细测试报告"""
    
    report_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = os.path.join(report_dir, f'submit_api_test_report_{timestamp}.md')
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Submit API 测试报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**总耗时**: {total_duration:.2f}秒\n\n")
        
        f.write("## 测试结果概览\n\n")
        passed = sum(1 for r in results if r['returncode'] == 0)
        failed = len(results) - passed
        
        f.write(f"- 总测试套件数: {len(results)}\n")
        f.write(f"- 通过: {passed}\n")
        f.write(f"- 失败: {failed}\n")
        f.write(f"- 成功率: {(passed/len(results)*100):.1f}%\n\n")
        
        f.write("## 详细结果\n\n")
        
        for result in results:
            f.write(f"### {result['name']}\n\n")
            f.write(f"- **文件**: `{result['file']}`\n")
            f.write(f"- **状态**: {result['status']}\n")
            f.write(f"- **耗时**: {result['duration']:.2f}秒\n")
            f.write(f"- **返回码**: {result['returncode']}\n\n")
            
            if result['stdout']:
                f.write("**标准输出**:\n")
                f.write("```\n")
                f.write(result['stdout'])
                f.write("\n```\n\n")
            
            if result['stderr']:
                f.write("**错误输出**:\n")
                f.write("```\n")
                f.write(result['stderr'])
                f.write("\n```\n\n")
    
    print(f"详细报告已保存到: {report_file}")

def run_quick_validation():
    """快速验证测试"""
    print("运行快速验证...")
    
    try:
        # 检查Django设置
        from django.conf import settings
        print("✅ Django设置正常")
        
        # 检查数据库连接
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ 数据库连接正常")
        
        # 检查模型导入
        from apps.english.models import TypingWord, TypingSession, TypingPracticeRecord
        print("✅ 模型导入正常")
        
        # 检查API客户端
        from rest_framework.test import APIClient
        client = APIClient()
        print("✅ API客户端正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

if __name__ == '__main__':
    print("Submit API 测试套件启动器")
    print()
    
    # 快速验证
    if not run_quick_validation():
        print("快速验证失败，退出测试")
        sys.exit(1)
    
    print()
    
    # 运行完整测试套件
    success = run_test_suite()
    
    if success:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n💥 部分测试失败，请检查报告")
        sys.exit(1)
