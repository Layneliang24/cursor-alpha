#!/usr/bin/env python3
"""
修复pyproject.toml文件的语法错误
"""

def fix_pyproject():
    with open('pyproject.toml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复语法错误
    content = content.replace('"if __name__ == .__main__.:"', '"if __name__ == .__main__.:"')
    
    with open('pyproject.toml', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ pyproject.toml语法错误已修复")

if __name__ == "__main__":
    fix_pyproject()


