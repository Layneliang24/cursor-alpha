#!/usr/bin/env python
"""
开发环境启动脚本 - 支持热重载
使用方法: python run_dev.py
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    """主函数"""
    print("🚀 启动 Alpha 项目开发环境...")
    
    # 检查 Django 环境
    if not os.path.exists('manage.py'):
        print("❌ 错误：请在 backend 目录下运行此脚本")
        sys.exit(1)
    
    # 检查依赖
    try:
        import django
        print(f"✅ Django 版本: {django.get_version()}")
    except ImportError:
        print("❌ 错误：Django 未安装")
        sys.exit(1)
    
    # 启动开发服务器（支持热重载）
    print("🔥 启动 Django 开发服务器（支持热重载）...")
    print("📝 提示：修改代码后服务器会自动重载")
    print("🛑 按 Ctrl+C 停止服务")
    print("-" * 50)
    
    try:
        # 使用 django-extensions 的 runserver_plus
        cmd = [
            sys.executable, 'manage.py', 'runserver_plus',
            '--reloader-type=stat',  # 使用 stat 方式检测文件变化（Windows 兼容）
            '--verbosity=2',
            '0.0.0.0:8000'  # 地址和端口作为位置参数
        ]
        
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        print("💡 尝试使用标准 Django 服务器...")
        
        try:
            cmd = [
                sys.executable, 'manage.py', 'runserver',
                '--verbosity=2',
                '0.0.0.0:8000'  # 地址和端口作为位置参数
            ]
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e2:
            print(f"❌ 标准服务器也启动失败: {e2}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
        sys.exit(0)

if __name__ == '__main__':
    main()
