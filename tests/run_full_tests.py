#!/usr/bin/env python3
"""完整测试脚本 - 运行所有测试用例"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_full_tests():
    """运行完整测试套件"""
    print("🚀 运行完整测试套件...")
    
    # 确保reports目录存在
    reports_dir = project_root / "tests" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--tb=short",
        "--disable-warnings",
        "-v",
        "--html=tests/reports/full_test_report.html",
        "--self-contained-html"
    ]
    
    # 只有在安装了pytest-json-report插件时才添加json报告
    try:
        import pytest_jsonreport
        cmd.extend(["--json-report", "--json-report-file=tests/reports/full_test_report.json"])
    except ImportError:
        print("💡 提示: 安装 pytest-json-report 可生成JSON格式测试报告")
    
    print(f"执行命令: {' '.join(cmd)}")
    print("📋 运行所有测试用例")
    print("💡 生成详细测试报告")
    
    try:
        result = subprocess.run(cmd, cwd=project_root, timeout=1800)  # 30分钟超时
        if result.returncode == 0:
            print("✅ 所有测试通过！")
            return True
        else:
            print("❌ 部分测试失败")
            return False
    except Exception as e:
        print(f"❌ 测试执行异常: {e}")
        return False

if __name__ == "__main__":
    success = run_full_tests()
    sys.exit(0 if success else 1)
