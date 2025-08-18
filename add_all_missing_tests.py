#!/usr/bin/env python3
"""
添加所有缺失的测试文件和目录到git
"""

import os
import subprocess

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def add_directory_files(directory):
    """添加目录中的所有文件"""
    if not os.path.exists(directory):
        print(f"❌ 目录不存在: {directory}")
        return False
    
    print(f"\n📁 添加目录: {directory}/")
    success_count = 0
    total_count = 0
    
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.py') or filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                relative_path = os.path.relpath(filepath, '.')
                total_count += 1
                
                success, stdout, stderr = run_command(f'git add -f "{relative_path}"')
                if success:
                    print(f"   ✅ {relative_path}")
                    success_count += 1
                else:
                    print(f"   ❌ {relative_path} - {stderr}")
    
    print(f"   📊 成功: {success_count}/{total_count}")
    return success_count > 0

def add_specific_files():
    """添加特定的重要文件"""
    important_files = [
        # 测试配置文件
        "tests/conftest.py",
        "tests/test_quick_validation.py",
        "tests/test_settings.py",
        "tests/test_settings_mysql.py", 
        "tests/test_simple_validation.py",
        "tests/pytest.ini",
        "tests/pytest_simple.ini",
        
        # 测试运行脚本
        "tests/run_tests_strategic.py",
        "tests/run_new_tests.py",
        "tests/run_fixed_tests.py",
        "tests/run_tests.py",
        "tests/run_module_tests.py",
        "tests/quick_start.py",
        
        # 测试文档
        "tests/TEST_MANAGEMENT_STRATEGY.md",
        "tests/TEST_IMPROVEMENT_PLAN.md",
        "tests/DATA_ANALYSIS_TEST_SUMMARY.md",
        "tests/CURRENT_TEST_STATUS.md",
        "tests/TEST_FIX_SUMMARY.md",
        "tests/TEST_EXECUTION_SUMMARY.md",
        "tests/TEST_COVERAGE_ANALYSIS.md",
        "tests/MODEL_FIELD_FIX_SUMMARY.md",
        "tests/TEST_CASE_SUPPLEMENTATION_REPORT.md",
        "tests/TEST_CASES.md",
        "tests/FUNCTION_COVERAGE_ANALYSIS.md",
        "tests/MYSQL_TEST_SETUP.md",
        "tests/README.md",
        
        # 其他重要文件
        "tests/requirements.txt",
        "tests/verify_fixes.py",
        "tests/fix_api_paths.py"
    ]
    
    print("\n📄 添加重要文件:")
    success_count = 0
    
    for file in important_files:
        if os.path.exists(file):
            success, stdout, stderr = run_command(f'git add -f "{file}"')
            if success:
                print(f"   ✅ {file}")
                success_count += 1
            else:
                print(f"   ❌ {file} - {stderr}")
        else:
            print(f"   ⚠️  {file} (不存在)")
    
    print(f"   📊 成功: {success_count}")
    return success_count > 0

def main():
    print("🔧 添加所有缺失的测试文件...")
    
    # 1. 添加.gitignore文件
    print("\n1. 添加.gitignore文件...")
    success, stdout, stderr = run_command('git add .gitignore')
    if success:
        print("   ✅ .gitignore已添加")
    else:
        print(f"   ❌ .gitignore添加失败: {stderr}")
    
    # 2. 添加所有测试目录
    test_directories = [
        "tests/unit",
        "tests/integration",
        "tests/new_features", 
        "tests/regression",
        "tests/factories",
        "tests/utils",
        "tests/unit/auth"
    ]
    
    print("\n2. 添加测试目录...")
    for directory in test_directories:
        add_directory_files(directory)
    
    # 3. 添加重要文件
    print("\n3. 添加重要文件...")
    add_specific_files()
    
    # 4. 提交更改
    print("\n4. 提交更改...")
    commit_msg = """feat: 添加完整的测试目录结构和文件

- 添加tests/unit/目录下的所有测试文件
- 添加tests/integration/目录下的集成测试文件
- 添加tests/new_features/目录下的新功能测试
- 添加tests/regression/目录下的回归测试文件
- 添加tests/factories/目录下的测试工厂文件
- 添加tests/utils/目录下的测试工具文件
- 添加所有测试配置文件和运行脚本
- 添加测试文档和报告文件
- 修复.gitignore规则，允许测试文件被提交"""
    
    success, stdout, stderr = run_command('git commit -m "' + commit_msg.replace('\n', '\\n') + '"')
    if success:
        print("   ✅ 更改已提交")
    else:
        print(f"   ❌ 提交失败: {stderr}")
    
    # 5. 推送到远程
    print("\n5. 推送到远程仓库...")
    success, stdout, stderr = run_command('git push origin main')
    if success:
        print("   ✅ 已推送到远程仓库")
    else:
        print(f"   ❌ 推送失败: {stderr}")
    
    print("\n🎉 完成！现在远程仓库应该包含完整的测试目录结构了。")

if __name__ == "__main__":
    main() 