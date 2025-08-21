#!/usr/bin/env python3
"""回归测试脚本 - 验证稳定功能不受影响"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_regression_tests():
    """运行回归测试"""
    print("🔄 运行回归测试...")
    
    # 回归测试文件列表（核心稳定功能）
    regression_tests = [
        # 基础功能 - 核心稳定
        "tests/unit/test_basic.py",               # 基础功能
        "tests/unit/test_models.py",              # 模型测试
        "tests/unit/test_mysql_connection.py",    # MySQL连接
        "tests/unit/test_simple.py",              # 简单验证
        
        # 数据分析功能 - 核心稳定
        "tests/unit/test_data_analysis.py",       # 数据分析
        
        # 核心API功能 - 稳定
        "tests/integration/test_api.py",          # API集成测试
        "tests/unit/test_news_dashboard.py",      # 新闻仪表板
        
        # 用户认证功能 - 大部分稳定
        "tests/unit/test_user_auth.py",           # 用户认证
        
        # 打字练习功能 - 稳定
        "tests/unit/test_typing_practice_submit.py",  # 打字练习提交
        
        # 发音功能 - 稳定
        "tests/regression/english/test_pronunciation.py",  # 发音功能
        "tests/regression/english/test_data_analysis_regression.py",  # 数据分析回归
    ]
    
    # 确保reports目录存在
    reports_dir = project_root / "tests" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        sys.executable, "-m", "pytest",
        "--tb=short",
        "--disable-warnings",
        "-v",
        "--html=tests/reports/regression_report.html",
        "--self-contained-html"
    ]
    
    # 添加回归测试文件
    for test_file in regression_tests:
        test_path = project_root / test_file
        if test_path.exists():
            cmd.append(str(test_path))
        else:
            print(f"⚠️  警告: 测试文件不存在 {test_file}")
    
    print(f"执行命令: {' '.join(cmd)}")
    print(f"📋 运行 {len(regression_tests)} 个回归测试文件")
    print("💡 验证核心稳定功能不受影响")
    
    try:
        result = subprocess.run(cmd, cwd=project_root, timeout=600)
        if result.returncode == 0:
            print("✅ 所有回归测试通过！")
            return True
        else:
            print("❌ 部分回归测试失败")
            return False
    except Exception as e:
        print(f"❌ 测试执行异常: {e}")
        return False

if __name__ == "__main__":
    success = run_regression_tests()
    sys.exit(0 if success else 1)
