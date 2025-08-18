#!/usr/bin/env python3
"""
修复测试目录结构问题
解决.gitignore规则导致的测试目录缺失问题
"""

import os
import subprocess
import sys

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔧 修复测试目录结构问题...")
    
    # 1. 修改.gitignore文件
    print("1. 修改.gitignore文件...")
    gitignore_path = ".gitignore"
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 注释掉测试文件忽略规则
        content = content.replace("# Test files\ntest_*.py\n*test.py", 
                                "# Test files (excluding actual test files)\n# test_*.py\n# *test.py")
        
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("   ✅ .gitignore文件已更新")
    
    # 2. 添加测试目录
    test_dirs = [
        "tests/integration/",
        "tests/new_features/", 
        "tests/regression/",
        "tests/unit/auth/",
        "tests/factories/",
        "tests/utils/"
    ]
    
    print("2. 添加测试目录...")
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            success, stdout, stderr = run_command(f'git add -f "{test_dir}"')
            if success:
                print(f"   ✅ 已添加 {test_dir}")
            else:
                print(f"   ❌ 添加 {test_dir} 失败: {stderr}")
    
    # 3. 添加重要的测试文件
    test_files = [
        "tests/conftest.py",
        "tests/test_quick_validation.py", 
        "tests/test_settings.py",
        "tests/test_settings_mysql.py",
        "tests/test_simple_validation.py"
    ]
    
    print("3. 添加测试文件...")
    for test_file in test_files:
        if os.path.exists(test_file):
            success, stdout, stderr = run_command(f'git add -f "{test_file}"')
            if success:
                print(f"   ✅ 已添加 {test_file}")
            else:
                print(f"   ❌ 添加 {test_file} 失败: {stderr}")
    
    # 4. 添加.gitignore文件
    print("4. 添加.gitignore文件...")
    success, stdout, stderr = run_command('git add .gitignore')
    if success:
        print("   ✅ 已添加 .gitignore")
    else:
        print(f"   ❌ 添加 .gitignore 失败: {stderr}")
    
    # 5. 提交更改
    print("5. 提交更改...")
    commit_msg = """fix: 修复.gitignore规则，添加缺失的测试目录结构

- 修改.gitignore文件，允许测试文件被提交
- 添加tests/integration/目录及其测试文件
- 添加tests/new_features/目录及其测试文件  
- 添加tests/regression/目录及其测试文件
- 添加tests/unit/auth/目录
- 添加tests/factories/和tests/utils/目录
- 添加重要的测试配置文件"""
    
    success, stdout, stderr = run_command('git commit -m "' + commit_msg.replace('\n', '\\n') + '"')
    if success:
        print("   ✅ 更改已提交")
    else:
        print(f"   ❌ 提交失败: {stderr}")
    
    # 6. 推送到远程
    print("6. 推送到远程仓库...")
    success, stdout, stderr = run_command('git push origin main')
    if success:
        print("   ✅ 已推送到远程仓库")
    else:
        print(f"   ❌ 推送失败: {stderr}")
    
    print("\n🎉 修复完成！")
    print("现在远程仓库应该包含完整的测试目录结构了。")

if __name__ == "__main__":
    main() 