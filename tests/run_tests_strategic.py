#!/usr/bin/env python
"""
战略性测试执行脚本
支持分层执行、标记过滤和性能优化
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_settings_mysql')
os.environ.setdefault('TESTING', 'true')


class TestExecutor:
    """测试执行器"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'duration': 0
        }
    
    def run_tests(self, test_path, markers=None, parallel=False, coverage=False):
        """运行测试"""
        print(f"🚀 开始执行测试: {test_path}")
        print(f"⏰ 开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 构建pytest命令
        cmd = [sys.executable, '-m', 'pytest', test_path, '-v', '--tb=short']
        
        # 添加标记过滤
        if markers:
            marker_expr = ' and '.join(markers)
            cmd.extend(['-m', marker_expr])
        
        # 添加并行执行
        if parallel:
            cmd.extend(['-n', 'auto'])
        
        # 添加覆盖率
        if coverage:
            cmd.extend(['--cov=backend', '--cov-report=html', '--cov-report=term'])
        
        # 执行测试
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=Path(__file__).parent.parent
            )
            
            # 解析结果
            self._parse_results(result)
            
            # 显示结果
            self._display_results()
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ 执行测试时出错: {e}")
            return False
    
    def _parse_results(self, result):
        """解析测试结果"""
        output_lines = result.stdout.split('\n')
        
        for line in output_lines:
            if 'PASSED' in line:
                self.results['passed'] += 1
                self.results['total'] += 1
            elif 'FAILED' in line:
                self.results['failed'] += 1
                self.results['total'] += 1
            elif 'SKIPPED' in line:
                self.results['skipped'] += 1
                self.results['total'] += 1
        
        end_time = datetime.now()
        self.results['duration'] = (end_time - self.start_time).total_seconds()
    
    def _display_results(self):
        """显示测试结果"""
        print("\n" + "=" * 60)
        print("📊 测试执行结果")
        print("=" * 60)
        print(f"✅ 通过: {self.results['passed']}")
        print(f"❌ 失败: {self.results['failed']}")
        print(f"⏭️  跳过: {self.results['skipped']}")
        print(f"📈 总计: {self.results['total']}")
        print(f"⏱️  耗时: {self.results['duration']:.2f}秒")
        
        if self.results['total'] > 0:
            pass_rate = (self.results['passed'] / self.results['total']) * 100
            print(f"📊 通过率: {pass_rate:.1f}%")
        
        print("=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='战略性测试执行脚本')
    parser.add_argument(
        '--type', 
        choices=['unit', 'integration', 'e2e', 'all'],
        default='unit',
        help='测试类型'
    )
    parser.add_argument(
        '--priority',
        choices=['critical', 'high', 'medium', 'low', 'all'],
        default='all',
        help='测试优先级'
    )
    parser.add_argument(
        '--module',
        choices=['auth', 'english', 'articles', 'all'],
        default='all',
        help='测试模块'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='并行执行测试'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='生成覆盖率报告'
    )
    parser.add_argument(
        '--fast',
        action='store_true',
        help='只运行快速测试'
    )
    
    args = parser.parse_args()
    
    print("🧪 战略性测试执行脚本")
    print("=" * 60)
    print(f"测试类型: {args.type}")
    print(f"优先级: {args.priority}")
    print(f"模块: {args.module}")
    print(f"并行执行: {args.parallel}")
    print(f"覆盖率: {args.coverage}")
    print(f"快速模式: {args.fast}")
    print("=" * 60)
    
    # 确定测试路径
    if args.type == 'all':
        test_path = 'tests/'
    else:
        test_path = f'tests/{args.type}/'
    
    # 构建标记过滤
    markers = []
    
    if args.priority != 'all':
        markers.append(args.priority)
    
    if args.module != 'all':
        markers.append(args.module)
    
    if args.fast:
        markers.append('fast')
    
    # 执行测试
    executor = TestExecutor()
    success = executor.run_tests(
        test_path=test_path,
        markers=markers if markers else None,
        parallel=args.parallel,
        coverage=args.coverage
    )
    
    if success:
        print("\n🎉 所有测试都通过了！")
    else:
        print("\n⚠️  有测试失败，请检查")
    
    return success


def run_quick_feedback():
    """快速反馈测试 - 只运行关键和快速的单元测试"""
    print("⚡ 快速反馈测试")
    print("=" * 40)
    
    executor = TestExecutor()
    success = executor.run_tests(
        test_path='tests/unit/',
        markers=['critical', 'fast'],
        parallel=True
    )
    
    return success


def run_integration_validation():
    """集成验证测试 - 运行集成测试"""
    print("🔗 集成验证测试")
    print("=" * 40)
    
    executor = TestExecutor()
    success = executor.run_tests(
        test_path='tests/integration/',
        parallel=True,
        coverage=True
    )
    
    return success


def run_full_validation():
    """完整验证测试 - 运行所有测试"""
    print("🔄 完整验证测试")
    print("=" * 40)
    
    executor = TestExecutor()
    success = executor.run_tests(
        test_path='tests/',
        parallel=True,
        coverage=True
    )
    
    return success


def run_critical_tests():
    """关键功能测试 - 只运行关键测试"""
    print("🚨 关键功能测试")
    print("=" * 40)
    
    executor = TestExecutor()
    success = executor.run_tests(
        test_path='tests/',
        markers=['critical'],
        parallel=True
    )
    
    return success


if __name__ == '__main__':
    # 如果没有命令行参数，显示使用示例
    if len(sys.argv) == 1:
        print("🧪 测试执行脚本使用示例:")
        print("=" * 60)
        print("1. 快速反馈测试 (关键功能):")
        print("   python tests/run_tests_strategic.py --type unit --priority critical --fast")
        print()
        print("2. 用户认证模块测试:")
        print("   python tests/run_tests_strategic.py --type unit --module auth")
        print()
        print("3. 集成测试:")
        print("   python tests/run_tests_strategic.py --type integration --coverage")
        print()
        print("4. 完整测试套件:")
        print("   python tests/run_tests_strategic.py --type all --parallel --coverage")
        print()
        print("5. 高优先级测试:")
        print("   python tests/run_tests_strategic.py --priority high --parallel")
        print()
        print("6. 英语学习模块快速测试:")
        print("   python tests/run_tests_strategic.py --module english --fast --parallel")
        print("=" * 60)
        
        # 运行快速反馈测试作为默认
        print("\n🚀 运行默认快速反馈测试...")
        run_quick_feedback()
    else:
        main() 