#!/usr/bin/env python3
"""
检查所有测试目录的文件情况
"""

import os
import subprocess

def check_directory(directory):
    """检查目录中的文件"""
    if not os.path.exists(directory):
        print(f"❌ 目录不存在: {directory}")
        return
    
    print(f"\n📁 {directory}/")
    files = []
    
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.py') or filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                relative_path = os.path.relpath(filepath, '.')
                files.append(relative_path)
    
    if files:
        for file in sorted(files):
            size = os.path.getsize(file)
            print(f"   📄 {file} ({size} bytes)")
    else:
        print("   (空目录)")

def check_git_status():
    """检查git状态"""
    print("\n🔍 Git状态检查:")
    try:
        result = subprocess.run('git status --porcelain', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            test_files = [line for line in lines if 'tests/' in line]
            if test_files:
                print("   Git跟踪的测试文件:")
                for file in test_files:
                    print(f"   {file}")
            else:
                print("   (没有测试文件被Git跟踪)")
    except Exception as e:
        print(f"   ❌ Git状态检查失败: {e}")

def main():
    print("🔍 检查所有测试目录...")
    
    # 检查主要测试目录
    test_directories = [
        "tests/unit",
        "tests/integration", 
        "tests/new_features",
        "tests/regression",
        "tests/factories",
        "tests/utils",
        "tests/unit/auth"
    ]
    
    for directory in test_directories:
        check_directory(directory)
    
    # 检查tests根目录的文件
    print("\n📁 tests/ (根目录文件)")
    test_root_files = [
        "tests/conftest.py",
        "tests/test_quick_validation.py",
        "tests/test_settings.py", 
        "tests/test_settings_mysql.py",
        "tests/test_simple_validation.py",
        "tests/run_tests_strategic.py",
        "tests/run_new_tests.py",
        "tests/run_fixed_tests.py",
        "tests/TEST_MANAGEMENT_STRATEGY.md",
        "tests/TEST_IMPROVEMENT_PLAN.md",
        "tests/DATA_ANALYSIS_TEST_SUMMARY.md",
        "tests/CURRENT_TEST_STATUS.md"
    ]
    
    for file in test_root_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   📄 {file} ({size} bytes)")
    
    # 检查git状态
    check_git_status()
    
    print("\n✅ 检查完成！")

if __name__ == "__main__":
    main() 