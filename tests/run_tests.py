#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试执行主脚本
提供一键执行所有测试的功能
"""

import os
import sys
import subprocess
import argparse
import time
from datetime import datetime
from pathlib import Path

# 添加backend目录到Python路径
project_root = Path(__file__).parent.parent
backend_dir = project_root / 'backend'
sys.path.insert(0, str(backend_dir))

# 设置环境变量
os.environ['TESTING'] = 'true'
os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'


class TestRunner:
    """测试运行器类"""
    
    def __init__(self):
        self.project_root = project_root
        self.tests_dir = project_root / 'tests'
        self.reports_dir = self.tests_dir / 'reports'
        self.start_time = None
        self.end_time = None
        
    def setup_environment(self):
        """设置测试环境"""
        print("🔧 设置测试环境...")
        
        # 创建必要的目录
        directories = [
            'tests/reports/html',
            'tests/reports/json',
            'tests/temp_media',
            'tests/temp_static'
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"  ✓ 创建目录: {directory}")
            except Exception as e:
                print(f"  ⚠️  目录 {directory} 创建失败: {e}")
        
        print("✅ 测试环境设置完成")
    
    def run_command(self, command, description):
        """运行命令并返回结果"""
        print(f"\n🚀 {description}")
        print(f"执行命令: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print(f"✅ {description} 成功")
                return True, result.stdout
            else:
                print(f"❌ {description} 失败")
                print(f"错误输出: {result.stderr}")
                return False, result.stderr
                
        except Exception as e:
            print(f"❌ 执行命令时出错: {e}")
            return False, str(e)
    
    def run_full_test_suite(self):
        """运行完整测试套件"""
        print("\n" + "="*60)
        print("🧪 开始执行完整测试套件")
        print("="*60)
        
        self.start_time = time.time()
        
        # 1. 运行所有测试
        command = "python -m pytest tests/ -v --html=tests/reports/html/full_report.html"
        success, output = self.run_command(command, "完整测试套件")
        
        if not success:
            print("❌ 完整测试套件执行失败")
            return False
        
        # 2. 生成覆盖率报告
        coverage_command = "python -m pytest tests/ --cov=. --cov-report=html:tests/reports/html/coverage"
        coverage_success, coverage_output = self.run_command(coverage_command, "覆盖率报告")
        
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        
        print(f"\n⏱️  完整测试套件执行完成，耗时: {execution_time:.2f}秒")
        return True
    
    def run_regression_tests(self):
        """运行回归测试"""
        print("\n" + "="*60)
        print("🔄 开始执行回归测试")
        print("="*60)
        
        self.start_time = time.time()
        
        command = "python -m pytest tests/regression/ -v --html=tests/reports/html/regression_report.html"
        success, output = self.run_command(command, "回归测试")
        
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        
        if success:
            print(f"✅ 回归测试执行完成，耗时: {execution_time:.2f}秒")
        else:
            print(f"❌ 回归测试执行失败，耗时: {execution_time:.2f}秒")
        
        return success
    
    def run_new_feature_tests(self):
        """运行新功能测试"""
        print("\n" + "="*60)
        print("🆕 开始执行新功能测试")
        print("="*60)
        
        self.start_time = time.time()
        
        command = "python -m pytest tests/new_features/ -v --html=tests/reports/html/new_feature_report.html"
        success, output = self.run_command(command, "新功能测试")
        
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        
        if success:
            print(f"✅ 新功能测试执行完成，耗时: {execution_time:.2f}秒")
        else:
            print(f"❌ 新功能测试执行失败，耗时: {execution_time:.2f}秒")
        
        return success
    
    def run_module_tests(self, module_name):
        """运行指定模块的测试"""
        print(f"\n" + "="*60)
        print(f"📦 开始执行 {module_name} 模块测试")
        print("="*60)
        
        self.start_time = time.time()
        
        module_path = f"tests/regression/{module_name}/"
        module_full_path = self.tests_dir / 'regression' / module_name
        
        if not module_full_path.exists():
            print(f"❌ 模块路径不存在: {module_path}")
            print(f"实际检查路径: {module_full_path}")
            return False
        
        command = f"python -m pytest {module_path} -v --html=tests/reports/html/{module_name}_report.html"
        success, output = self.run_command(command, f"{module_name} 模块测试")
        
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        
        if success:
            print(f"✅ {module_name} 模块测试执行完成，耗时: {execution_time:.2f}秒")
        else:
            print(f"❌ {module_name} 模块测试执行失败，耗时: {execution_time:.2f}秒")
        
        return success
    
    def run_unit_tests(self):
        """运行单元测试"""
        print("\n" + "="*60)
        print("🔬 开始执行单元测试")
        print("="*60)
        
        self.start_time = time.time()
        
        command = "python -m pytest tests/unit/ -v --html=tests/reports/html/unit_report.html"
        success, output = self.run_command(command, "单元测试")
        
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        
        if success:
            print(f"✅ 单元测试执行完成，耗时: {execution_time:.2f}秒")
        else:
            print(f"❌ 单元测试执行失败，耗时: {execution_time:.2f}秒")
        
        return success
    
    def run_api_tests(self):
        """运行API测试"""
        print("\n" + "="*60)
        print("🌐 开始执行API测试")
        print("="*60)
        
        self.start_time = time.time()
        
        command = "python -m pytest tests/ -k 'api' -v --html=tests/reports/html/api_report.html"
        success, output = self.run_command(command, "API测试")
        
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        
        if success:
            print(f"✅ API测试执行完成，耗时: {execution_time:.2f}秒")
        else:
            print(f"❌ API测试执行失败，耗时: {execution_time:.2f}秒")
        
        return success
    
    def run_frontend_tests(self):
        """运行前端测试"""
        print("\n" + "="*60)
        print("🎨 开始执行前端测试")
        print("="*60)
        
        self.start_time = time.time()
        
        # 检查是否有前端测试
        frontend_test_dir = self.tests_dir / 'frontend'
        if frontend_test_dir.exists():
            command = "npm run test:frontend"
            success, output = self.run_command(command, "前端测试")
        else:
            print("⚠️  前端测试目录不存在，跳过前端测试")
            return True
        
        self.end_time = time.time()
        execution_time = self.end_time - self.start_time
        
        if success:
            print(f"✅ 前端测试执行完成，耗时: {execution_time:.2f}秒")
        else:
            print(f"❌ 前端测试执行失败，耗时: {execution_time:.2f}秒")
        
        return success
    
    def generate_summary_report(self):
        """生成测试总结报告"""
        print("\n" + "="*60)
        print("📊 生成测试总结报告")
        print("="*60)
        
        summary_file = self.reports_dir / 'html' / 'test_summary.html'
        
        summary_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>测试执行总结报告</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .report-links {{ margin: 20px 0; }}
        .report-links a {{ display: block; margin: 10px 0; padding: 10px; background-color: #e7f3ff; text-decoration: none; border-radius: 3px; }}
        .report-links a:hover {{ background-color: #d1e7ff; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Alpha项目测试执行总结报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <h2>📋 测试执行概览</h2>
        <p>本报告汇总了Alpha项目的所有测试执行结果，包括单元测试、集成测试、API测试和前端测试。</p>
    </div>
    
    <div class="report-links">
        <h2>📊 详细测试报告</h2>
        <a href="full_report.html">完整测试套件报告</a>
        <a href="regression_report.html">回归测试报告</a>
        <a href="new_feature_report.html">新功能测试报告</a>
        <a href="unit_report.html">单元测试报告</a>
        <a href="api_report.html">API测试报告</a>
        <a href="coverage/index.html">代码覆盖率报告</a>
    </div>
    
    <div class="summary">
        <h2>📈 测试覆盖率目标</h2>
        <ul>
            <li>单元测试覆盖率: ≥80%</li>
            <li>API测试覆盖率: ≥90%</li>
            <li>关键功能测试覆盖率: 100%</li>
            <li>回归测试通过率: 100%</li>
        </ul>
    </div>
</body>
</html>
        """
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            print(f"✅ 测试总结报告生成完成: {summary_file}")
        except Exception as e:
            print(f"❌ 生成测试总结报告失败: {e}")
    
    def show_report_locations(self):
        """显示报告文件位置"""
        print("\n" + "="*60)
        print("📁 测试报告文件位置")
        print("="*60)
        
        reports = [
            ("完整测试套件报告", "tests/reports/html/full_report.html"),
            ("回归测试报告", "tests/reports/html/regression_report.html"),
            ("新功能测试报告", "tests/reports/html/new_feature_report.html"),
            ("单元测试报告", "tests/reports/html/unit_report.html"),
            ("API测试报告", "tests/reports/html/api_report.html"),
            ("代码覆盖率报告", "tests/reports/html/coverage/index.html"),
            ("测试总结报告", "tests/reports/html/test_summary.html"),
        ]
        
        for name, path in reports:
            full_path = self.project_root / path
            if full_path.exists():
                print(f"✅ {name}: {path}")
            else:
                print(f"❌ {name}: {path} (文件不存在)")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Alpha项目测试执行器')
    parser.add_argument('--mode', choices=['full', 'regression', 'new-feature', 'unit', 'api', 'frontend'], 
                       default='full', help='测试模式')
    parser.add_argument('--module', help='指定模块名称（用于模块测试）')
    parser.add_argument('--setup-only', action='store_true', help='仅设置环境，不执行测试')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        # 设置测试环境
        runner.setup_environment()
        
        if args.setup_only:
            print("✅ 环境设置完成，退出")
            return
        
        # 根据模式执行测试
        if args.module:
            # 如果指定了模块，优先运行模块测试
            success = runner.run_module_tests(args.module)
        elif args.mode == 'full':
            success = runner.run_full_test_suite()
        elif args.mode == 'regression':
            success = runner.run_regression_tests()
        elif args.mode == 'new-feature':
            success = runner.run_new_feature_tests()
        elif args.mode == 'unit':
            success = runner.run_unit_tests()
        elif args.mode == 'api':
            success = runner.run_api_tests()
        elif args.mode == 'frontend':
            success = runner.run_frontend_tests()
        
        # 生成总结报告
        runner.generate_summary_report()
        
        # 显示报告位置
        runner.show_report_locations()
        
        if success:
            print("\n🎉 所有测试执行完成！")
            sys.exit(0)
        else:
            print("\n💥 测试执行过程中出现错误！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  测试执行被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试执行过程中出现未预期的错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
