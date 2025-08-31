#!/usr/bin/env python
"""
测试数据库设置脚本
自动处理测试数据库的创建和清理，避免交互式提示
"""

import os
import sys
import django
import MySQLdb
from django.conf import settings
from django.core.management import execute_from_command_line

def setup_django():
    """设置Django环境"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings_test')
    django.setup()

def clean_test_database():
    """清理测试数据库，避免交互式提示"""
    try:
        # 获取数据库配置
        db_config = settings.DATABASES['default']
        test_db_name = db_config.get('TEST', {}).get('NAME', 'test_alpha_db')
        
        # 连接到MySQL服务器（不指定数据库）
        connection = MySQLdb.connect(
            host=db_config['HOST'],
            user=db_config['USER'],
            passwd=db_config['PASSWORD'],
            port=int(db_config['PORT']),
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # 强制删除测试数据库（如果存在）
        print(f"🗑️  正在清理测试数据库: {test_db_name}")
        cursor.execute(f"DROP DATABASE IF EXISTS `{test_db_name}`")
        
        # 创建新的测试数据库
        print(f"🆕 正在创建测试数据库: {test_db_name}")
        cursor.execute(f"CREATE DATABASE `{test_db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        cursor.close()
        connection.close()
        
        print(f"✅ 测试数据库 {test_db_name} 准备完成")
        return True
        
    except Exception as e:
        print(f"❌ 清理测试数据库失败: {e}")
        return False

def run_tests():
    """运行测试"""
    try:
        print("🧪 开始运行测试...")
        
        # 设置环境变量，避免交互式提示
        os.environ['DJANGO_TEST_PROCESSES'] = '1'
        
        # 运行测试
        execute_from_command_line(['manage.py', 'test', '--verbosity=2', '--keepdb'])
        
        print("✅ 测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 启动测试数据库设置...")
    
    # 设置Django环境
    setup_django()
    
    # 清理测试数据库
    if not clean_test_database():
        sys.exit(1)
    
    # 运行测试
    if len(sys.argv) > 1 and sys.argv[1] == '--run-tests':
        if not run_tests():
            sys.exit(1)
    
    print("🎉 测试数据库设置完成")

if __name__ == '__main__':
    main()
