# -*- coding: utf-8 -*-
"""
批量修复测试文件中的API路径
将 /api/english/ 替换为 /api/v1/english/
"""

import os
import re
from pathlib import Path

def fix_api_paths_in_file(file_path):
    """修复单个文件中的API路径"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换API路径
        old_pattern = r'/api/english/'
        new_pattern = '/api/v1/english/'
        
        if old_pattern in content:
            new_content = content.replace(old_pattern, new_pattern)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 已修复: {file_path}")
            return True
        else:
            print(f"⏭️  无需修复: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败: {file_path} - {e}")
        return False

def main():
    """主函数"""
    tests_dir = Path(__file__).parent
    
    # 需要修复的文件
    files_to_fix = [
        'regression/english/test_pronunciation.py',
        'regression/english/test_pause_resume.py',
    ]
    
    fixed_count = 0
    total_count = len(files_to_fix)
    
    for file_path in files_to_fix:
        full_path = tests_dir / file_path
        if full_path.exists():
            if fix_api_paths_in_file(full_path):
                fixed_count += 1
        else:
            print(f"⚠️  文件不存在: {full_path}")
    
    print(f"\n📊 修复完成: {fixed_count}/{total_count} 个文件")

if __name__ == '__main__':
    main()
"""
批量修复测试文件中的API路径
将 /api/english/ 替换为 /api/v1/english/
"""

import os
import re
from pathlib import Path

def fix_api_paths_in_file(file_path):
    """修复单个文件中的API路径"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换API路径
        old_pattern = r'/api/english/'
        new_pattern = '/api/v1/english/'
        
        if old_pattern in content:
            new_content = content.replace(old_pattern, new_pattern)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 已修复: {file_path}")
            return True
        else:
            print(f"⏭️  无需修复: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败: {file_path} - {e}")
        return False

def main():
    """主函数"""
    tests_dir = Path(__file__).parent
    
    # 需要修复的文件
    files_to_fix = [
        'regression/english/test_pronunciation.py',
        'regression/english/test_pause_resume.py',
    ]
    
    fixed_count = 0
    total_count = len(files_to_fix)
    
    for file_path in files_to_fix:
        full_path = tests_dir / file_path
        if full_path.exists():
            if fix_api_paths_in_file(full_path):
                fixed_count += 1
        else:
            print(f"⚠️  文件不存在: {full_path}")
    
    print(f"\n📊 修复完成: {fixed_count}/{total_count} 个文件")

if __name__ == '__main__':
    main()
