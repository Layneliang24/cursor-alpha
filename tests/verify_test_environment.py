#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试环境验证脚本
验证测试环境的所有组件是否正常工作
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(title):
    """打印标题"""
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def print_section(title):
    """打印章节标题"""
    print(f"\n📋 {title}")
    print("-" * 40)

def check_python_environment():
    """检查Python环境"""
    print_section("Python环境检查")
    
    # Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version >= (3, 8):
        print("✅ Python版本满足要求")
    else:
        print("❌ Python版本过低，需要3.8+")
        return False
    
    # Python路径
    print(f"Python路径: {sys.executable}")
    print(f"当前工作目录: {os.getcwd()}")
    
    return True

def check_django_environment():
    """检查Django环境"""
    print_section("Django环境检查")
    
    try:
        import django
        print(f"Django版本: {django.get_version()}")
        
        # 测试Django设置
        os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings_simple'
        django.setup()
        
        from django.conf import settings
        print(f"Django设置模块: {settings.SETTINGS_MODULE}")
        print(f"测试模式: {settings.TESTING}")
        print(f"调试模式: {settings.DEBUG}")
        print(f"数据库引擎: {settings.DATABASES['default']['ENGINE']}")
        
        print("✅ Django环境配置成功")
        return True
        
    except Exception as e:
        print(f"❌ Django环境配置失败: {e}")
        return False

def check_test_frameworks():
    """检查测试框架"""
    print_section("测试框架检查")
    
    frameworks = {
        'pytest': 'pytest',
        'pytest-django': 'pytest_django',
        'pytest-cov': 'pytest_cov',
        'factory-boy': 'factory_boy',
        'faker': 'faker'
    }
    
    all_available = True
    for name, module in frameworks.items():
        try:
            __import__(module)
            print(f"✅ {name}: 已安装")
        except ImportError:
            print(f"❌ {name}: 未安装")
            all_available = False
    
    return all_available

def check_test_configuration():
    """检查测试配置"""
    print_section("测试配置检查")
    
    config_files = [
        'tests/pytest.ini',
        'tests/test_settings_simple.py',
        'tests/test_settings_mysql.py',
        'tests/conftest.py'
    ]
    
    all_exist = True
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"✅ {config_file}: 存在")
        else:
            print(f"❌ {config_file}: 不存在")
            all_exist = False
    
    return all_exist

def check_test_structure():
    """检查测试目录结构"""
    print_section("测试目录结构检查")
    
    test_dirs = [
        'tests/unit',
        'tests/integration', 
        'tests/e2e',
        'tests/factories',
        'tests/fixtures',
        'tests/reports'
    ]
    
    all_exist = True
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            print(f"✅ {test_dir}: 存在")
        else:
            print(f"❌ {test_dir}: 不存在")
            all_exist = False
    
    return all_exist

def run_basic_test():
    """运行基本测试"""
    print_section("基本测试执行")
    
    try:
        # 创建一个简单的测试文件
        test_file = Path('tests/test_basic_environment.py')
        test_content = '''#!/usr/bin/env python3
import pytest
import django
from django.test import TestCase

class TestBasicEnvironment(TestCase):
    def test_django_import(self):
        """测试Django是否可以正常导入"""
        assert django.VERSION >= (4, 0)
    
    def test_test_settings(self):
        """测试测试设置是否正确"""
        from django.conf import settings
        assert settings.TESTING == True
        assert settings.DEBUG == False
    
    def test_database_config(self):
        """测试数据库配置"""
        from django.conf import settings
        assert 'default' in settings.DATABASES
        assert 'ENGINE' in settings.DATABASES['default']
'''
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print("✅ 创建基本测试文件")
        
        # 运行测试
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'tests/test_basic_environment.py', 
            '-v', '--tb=short'
        ], capture_output=True, text=True, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("✅ 基本测试执行成功")
            print("测试输出:")
            print(result.stdout)
        else:
            print("❌ 基本测试执行失败")
            print("错误输出:")
            print(result.stderr)
            return False
        
        # 清理测试文件
        test_file.unlink()
        print("✅ 清理测试文件")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本测试执行出错: {e}")
        return False

def main():
    """主函数"""
    print_header("测试环境验证")
    
    checks = [
        ("Python环境", check_python_environment),
        ("Django环境", check_django_environment),
        ("测试框架", check_test_frameworks),
        ("测试配置", check_test_configuration),
        ("测试结构", check_test_structure),
        ("基本测试", run_basic_test)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 检查出错: {e}")
            results.append((name, False))
    
    # 总结
    print_header("验证结果总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总体结果: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("🎉 测试环境验证完全通过！")
        return True
    else:
        print("⚠️  测试环境存在一些问题，需要修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


