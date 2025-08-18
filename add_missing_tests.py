#!/usr/bin/env python3
"""
添加缺失的测试文件到git
"""

import os
import subprocess

def add_test_files():
    """添加所有测试文件到git"""
    
    # 测试文件列表
    test_files = [
        "tests/unit/test_data_analysis.py",
        "tests/unit/test_article_management.py", 
        "tests/unit/test_english_learning.py",
        "tests/unit/test_models.py",
        "tests/unit/test_typing_practice.py",
        "tests/unit/test_news_dashboard.py",
        "tests/unit/test_user_auth.py",
        "tests/unit/test_techcrunch_and_image_cleanup.py",
        "tests/unit/test_bbc_news_save.py",
        "tests/unit/test_mysql_connection.py",
        "tests/unit/test_news_visibility_removal.py",
        "tests/unit/test_fundus_crawler.py",
        "tests/unit/test_bbc_simple.py",
        "tests/unit/test_cnn_crawler.py",
        "tests/unit/test_simple.py",
        "tests/unit/test_basic.py",
        "tests/unit/test_typing_practice_fix.md"
    ]
    
    print("添加测试文件到git...")
    
    for test_file in test_files:
        if os.path.exists(test_file):
            try:
                result = subprocess.run(f'git add -f "{test_file}"', shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ 已添加: {test_file}")
                else:
                    print(f"❌ 添加失败: {test_file} - {result.stderr}")
            except Exception as e:
                print(f"❌ 错误: {test_file} - {e}")
        else:
            print(f"⚠️  文件不存在: {test_file}")
    
    # 添加.gitignore
    try:
        result = subprocess.run('git add .gitignore', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 已添加: .gitignore")
        else:
            print(f"❌ 添加.gitignore失败: {result.stderr}")
    except Exception as e:
        print(f"❌ 错误: .gitignore - {e}")
    
    print("\n完成！")

if __name__ == "__main__":
    add_test_files() 