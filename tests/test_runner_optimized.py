"""
优化的测试运行器

提供多种测试运行模式：
1. 快速测试 - 只运行核心功能测试
2. 完整测试 - 运行所有测试
3. 并行测试 - 使用多进程加速测试
4. 覆盖率测试 - 生成覆盖率报告
5. 性能测试 - 专门的性能回归测试
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
import argparse
from dataclasses import dataclass
from enum import Enum


class TestLevel(Enum):
    """测试级别"""
    SMOKE = "smoke"      # 冒烟测试 - 最基本的功能
    FAST = "fast"        # 快速测试 - 核心功能
    FULL = "full"        # 完整测试 - 所有测试
    FRONTEND = "frontend"  # 前端测试
    REGRESSION = "regression"  # 回归测试
    PERFORMANCE = "performance"  # 性能测试


@dataclass
class TestSuite:
    """测试套件定义"""
    name: str
    description: str
    test_paths: List[str]
    expected_time: int  # 预期执行时间（秒）
    parallel_safe: bool = True  # 是否支持并行执行


class TestConfiguration:
    """测试配置管理"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_root = Path(__file__).parent
        
        # 定义测试套件
        self.test_suites = {
            TestLevel.SMOKE: TestSuite(
                name="冒烟测试",
                description="最基本的功能验证，确保系统可以启动",
                test_paths=[
                    "tests/unit/test_basic.py",
                    "tests/unit/test_mysql_connection.py",
                    "tests/unit/test_simple.py"
                ],
                expected_time=10,
                parallel_safe=True
            ),
            
            TestLevel.FAST: TestSuite(
                name="快速测试",
                description="核心功能测试，适合开发过程中频繁运行",
                test_paths=[
                    "tests/unit/test_basic.py",
                    "tests/unit/test_models.py", 
                    "tests/unit/test_mysql_connection.py",
                    "tests/unit/test_simple.py",
                    "tests/unit/test_data_analysis.py",
                    "tests/unit/test_links_module.py",
                    "tests/unit/test_common_module.py",
                    "tests/unit/test_user_auth.py",
                    "tests/regression/auth/test_permissions.py",
                    "tests/regression/auth/test_user_authentication.py"
                ],
                expected_time=45,
                parallel_safe=True
            ),
            
            TestLevel.FRONTEND: TestSuite(
                name="前端测试",
                description="前端组件和功能测试",
                test_paths=[
                    "frontend/src/components/__tests__/",
                    "frontend/src/utils/__tests__/"
                ],
                expected_time=30,
                parallel_safe=True
            ),
            
            TestLevel.REGRESSION: TestSuite(
                name="回归测试",
                description="确保新变更不会破坏现有功能",
                test_paths=[
                    "tests/regression/",
                    "tests/unit/test_data_analysis.py",
                    "tests/unit/test_user_auth.py",
                    "tests/integration/test_api.py"
                ],
                expected_time=60,
                parallel_safe=True
            ),
            
            TestLevel.PERFORMANCE: TestSuite(
                name="性能测试",
                description="性能回归测试和基准测试",
                test_paths=[
                    "tests/performance/",
                    "tests/data_management/test_data_factory.py::TestDataFactoryIntegrationTest::test_bulk_data_performance"
                ],
                expected_time=30,
                parallel_safe=False
            ),
            
            TestLevel.FULL: TestSuite(
                name="完整测试",
                description="运行所有测试用例",
                test_paths=["tests/"],
                expected_time=180,
                parallel_safe=False
            )
        }
    
    def get_stable_tests(self) -> List[str]:
        """获取稳定测试列表"""
        return [
            "tests/unit/test_basic.py",
            "tests/unit/test_models.py",
            "tests/unit/test_mysql_connection.py", 
            "tests/unit/test_simple.py",
            "tests/unit/test_data_analysis.py",
            "tests/unit/test_cnn_crawler.py",
            "tests/unit/test_news_visibility_removal.py",
            "tests/unit/test_fundus_crawler.py",
            "tests/unit/test_links_module.py",
            "tests/unit/test_common_module.py",
            "tests/integration/test_news_api.py",
            "tests/integration/test_fixes_verification.py",
            "tests/regression/english/test_pronunciation.py",
            "tests/regression/english/test_data_analysis_regression.py",
            "tests/regression/auth/test_permissions.py",
            "tests/regression/auth/test_user_authentication.py",
            "tests/unit/test_jobs.py",
            "tests/unit/test_todos.py",
            "tests/unit/test_typing_practice_submit.py"
        ]


class TestRunner:
    """优化的测试运行器"""
    
    def __init__(self):
        self.config = TestConfiguration()
        self.start_time = None
        self.results = {}
    
    def run_tests(self, 
                  level: TestLevel = TestLevel.FAST,
                  parallel: bool = False,
                  coverage: bool = False,
                  verbose: bool = True,
                  fail_fast: bool = False,
                  custom_paths: Optional[List[str]] = None) -> Dict:
        """
        运行测试
        
        Args:
            level: 测试级别
            parallel: 是否并行执行
            coverage: 是否生成覆盖率报告
            verbose: 是否详细输出
            fail_fast: 是否遇到失败立即停止
            custom_paths: 自定义测试路径
            
        Returns:
            测试结果字典
        """
        self.start_time = time.time()
        
        # 获取测试套件
        if custom_paths:
            suite = TestSuite(
                name="自定义测试",
                description="用户指定的测试路径",
                test_paths=custom_paths,
                expected_time=60,
                parallel_safe=True
            )
        else:
            suite = self.config.test_suites[level]
            
        # 特殊处理前端测试
        if level == TestLevel.FRONTEND:
            return self._run_frontend_tests(suite, parallel, coverage, verbose, fail_fast)
        
        print(f"🚀 开始执行 {suite.name}")
        print(f"📝 描述: {suite.description}")
        print(f"⏱️  预期时间: {suite.expected_time}秒")
        print(f"📁 测试路径: {len(suite.test_paths)}个")
        
        if parallel and suite.parallel_safe:
            print("⚡ 并行模式: 启用")
        
        # 构建pytest命令
        cmd = self._build_pytest_command(
            suite, parallel, coverage, verbose, fail_fast
        )
        
        # 执行测试
        result = self._execute_tests(cmd)
        
        # 处理结果
        execution_time = time.time() - self.start_time
        self.results = {
            'suite_name': suite.name,
            'execution_time': execution_time,
            'expected_time': suite.expected_time,
            'success': result['returncode'] == 0,
            'output': result['output'],
            'error': result['error']
        }
        
        # 输出结果
        self._print_results()
        
        # 如果失败，显示错误信息
        if not self.results['success'] and verbose:
            print("\n" + "="*60)
            print("🔍 错误详情:")
            print("="*60)
            if self.results['error']:
                print("STDERR:")
                print(self.results['error'])
            if self.results['output']:
                print("STDOUT:")
                print(self.results['output'])
        
        return self.results
    
    def _run_frontend_tests(self, suite: TestSuite, parallel: bool, 
                           coverage: bool, verbose: bool, fail_fast: bool) -> Dict:
        """运行前端测试"""
        print(f"🌐 开始执行前端测试...")
        
        try:
            # 调用前端测试运行器
            frontend_runner_path = self.config.project_root / "tests" / "frontend_test_runner.py"
            
            if not frontend_runner_path.exists():
                return {
                    'suite_name': suite.name,
                    'execution_time': 0,
                    'expected_time': suite.expected_time,
                    'success': False,
                    'output': '',
                    'error': '前端测试运行器不存在'
                }
            
            # 构建前端测试命令
            cmd = ['python', str(frontend_runner_path)]
            
            if coverage:
                cmd.append('--coverage')
            else:
                cmd.append('--no-coverage')
                
            if verbose:
                cmd.append('--verbose')
                
            # 执行前端测试
            result = subprocess.run(
                cmd,
                cwd=self.config.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            execution_time = time.time() - self.start_time
            
            return {
                'suite_name': suite.name,
                'execution_time': execution_time,
                'expected_time': suite.expected_time,
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
            
        except Exception as e:
            execution_time = time.time() - self.start_time
            return {
                'suite_name': suite.name,
                'execution_time': execution_time,
                'expected_time': suite.expected_time,
                'success': False,
                'output': '',
                'error': f'前端测试执行异常: {str(e)}'
            }
    
    def _build_pytest_command(self, suite: TestSuite, parallel: bool, 
                            coverage: bool, verbose: bool, fail_fast: bool) -> List[str]:
        """构建pytest命令"""
        cmd = ['python', '-m', 'pytest']
        
        # 添加测试路径
        cmd.extend(suite.test_paths)
        
        # 并行执行
        if parallel and suite.parallel_safe:
            try:
                import pytest_xdist
                cmd.extend(['-n', 'auto'])  # 自动检测CPU核心数
            except ImportError:
                print("⚠️  警告: pytest-xdist未安装，跳过并行执行")
        
        # 覆盖率报告
        if coverage:
            cmd.extend([
                '--cov=backend',
                '--cov-report=html:tests/coverage_html',
                '--cov-report=term-missing',
                '--cov-fail-under=80'
            ])
        
        # 详细输出
        if verbose:
            cmd.append('-v')
        else:
            cmd.append('-q')
        
        # 快速失败
        if fail_fast:
            cmd.append('-x')
        
        # 其他有用的选项
        cmd.extend([
            '--tb=short',  # 简短的错误追踪
            '--disable-warnings',  # 禁用警告
            '--cache-clear',  # 清除缓存
        ])
        
        return cmd
    
    def _execute_tests(self, cmd: List[str]) -> Dict:
        """执行测试命令"""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.config.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10分钟超时
            )
            
            return {
                'returncode': result.returncode,
                'output': result.stdout,
                'error': result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {
                'returncode': -1,
                'output': '',
                'error': '测试执行超时'
            }
        except Exception as e:
            return {
                'returncode': -1,
                'output': '',
                'error': f'执行错误: {str(e)}'
            }
    
    def _print_results(self):
        """打印测试结果"""
        print("\n" + "="*60)
        print(f"📊 测试结果总结")
        print("="*60)
        
        print(f"🏷️  套件名称: {self.results['suite_name']}")
        print(f"⏱️  执行时间: {self.results['execution_time']:.2f}秒")
        print(f"📈 预期时间: {self.results['expected_time']}秒")
        
        if self.results['success']:
            print("✅ 测试状态: 通过")
            performance_ratio = self.results['execution_time'] / self.results['expected_time']
            if performance_ratio < 0.8:
                print("🚀 性能: 超预期 (比预期快)")
            elif performance_ratio > 1.2:
                print("🐌 性能: 低于预期 (比预期慢)")
            else:
                print("⚡ 性能: 符合预期")
        else:
            print("❌ 测试状态: 失败")
        
        # 解析测试输出中的统计信息
        if self.results['output']:
            self._parse_test_statistics(self.results['output'])
    
    def _parse_test_statistics(self, output: str):
        """解析测试统计信息"""
        lines = output.split('\n')
        
        for line in lines:
            if 'passed' in line and ('failed' in line or 'error' in line):
                print(f"📈 详细结果: {line.strip()}")
                break
            elif 'passed' in line and 'warning' in line:
                print(f"📈 详细结果: {line.strip()}")
                break
    
    def run_custom_suite(self, name: str, paths: List[str], **kwargs) -> Dict:
        """运行自定义测试套件"""
        return self.run_tests(custom_paths=paths, **kwargs)
    
    def run_by_tag(self, tag: str, **kwargs) -> Dict:
        """按标签运行测试"""
        custom_paths = [f"tests/ -m {tag}"]
        return self.run_tests(custom_paths=custom_paths, **kwargs)
    
    def run_changed_tests(self, **kwargs) -> Dict:
        """运行变更相关的测试"""
        # 这里可以集成git diff来找到变更的文件
        # 然后运行相关的测试
        print("🔍 检测代码变更...")
        # 简化实现，运行快速测试
        return self.run_tests(level=TestLevel.FAST, **kwargs)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="优化的测试运行器")
    
    parser.add_argument(
        '--level', '-l',
        choices=['smoke', 'fast', 'full', 'frontend', 'regression', 'performance'],
        default='fast',
        help='测试级别 (默认: fast)'
    )
    
    parser.add_argument(
        '--parallel', '-p',
        action='store_true',
        help='启用并行执行'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='生成覆盖率报告'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        default=True,
        help='详细输出'
    )
    
    parser.add_argument(
        '--fail-fast', '-x',
        action='store_true',
        help='遇到失败立即停止'
    )
    
    parser.add_argument(
        '--paths',
        nargs='+',
        help='自定义测试路径'
    )
    
    parser.add_argument(
        '--tag', '-t',
        help='按标签运行测试'
    )
    
    parser.add_argument(
        '--changed',
        action='store_true',
        help='只运行变更相关的测试'
    )
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = TestRunner()
    
    # 根据参数执行测试
    if args.changed:
        result = runner.run_changed_tests(
            parallel=args.parallel,
            coverage=args.coverage,
            verbose=args.verbose,
            fail_fast=args.fail_fast
        )
    elif args.tag:
        result = runner.run_by_tag(
            args.tag,
            parallel=args.parallel,
            coverage=args.coverage,
            verbose=args.verbose,
            fail_fast=args.fail_fast
        )
    elif args.paths:
        result = runner.run_custom_suite(
            "自定义测试",
            args.paths,
            parallel=args.parallel,
            coverage=args.coverage,
            verbose=args.verbose,
            fail_fast=args.fail_fast
        )
    else:
        level = TestLevel(args.level)
        result = runner.run_tests(
            level=level,
            parallel=args.parallel,
            coverage=args.coverage,
            verbose=args.verbose,
            fail_fast=args.fail_fast
        )
    
    # 返回适当的退出码
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()


# 使用示例:
"""
# 快速测试（默认）
python tests/test_runner_optimized.py

# 冒烟测试
python tests/test_runner_optimized.py --level smoke

# 并行执行完整测试
python tests/test_runner_optimized.py --level full --parallel

# 生成覆盖率报告
python tests/test_runner_optimized.py --coverage

# 运行特定路径的测试
python tests/test_runner_optimized.py --paths tests/unit/test_links_module.py

# 按标签运行测试
python tests/test_runner_optimized.py --tag unit

# 只运行变更相关的测试
python tests/test_runner_optimized.py --changed
"""

print("✅ 优化的测试运行器创建完成")