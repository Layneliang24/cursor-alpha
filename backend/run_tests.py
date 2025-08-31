#!/usr/bin/env python
"""
简化的测试运行器
自动处理测试数据库问题，避免交互式提示
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并实时输出"""
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=cwd
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        return process.poll() == 0
    except Exception as e:
        print(f"❌ 命令执行失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 启动自动化测试...")
    
    # 确保在backend目录
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # 设置环境变量
    os.environ['DJANGO_SETTINGS_MODULE'] = 'alpha.settings_test'
    os.environ['PYTHONPATH'] = str(backend_dir)
    
    # 运行测试，不使用--keepdb，每次重新创建数据库避免冲突
    test_cmd = f"{sys.executable} manage.py test --verbosity=2 --noinput"
    
    print(f"🔧 执行命令: {test_cmd}")
    
    if run_command(test_cmd):
        print("✅ 测试完成")
        return 0
    else:
        print("❌ 测试失败")
        return 1

if __name__ == '__main__':
    sys.exit(main())
