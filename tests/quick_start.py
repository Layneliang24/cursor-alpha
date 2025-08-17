#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试系统快速开始脚本
用于快速验证测试环境是否正常工作
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ['TESTING'] = 'true'
os.environ['DJANGO_SETTINGS_MODULE'] = 'alpha.settings'


def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python版本过低: {version.major}.{version.minor}")
        print("需要Python 3.8+")
        return False
    else:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True


def check_dependencies():
    """检查依赖包"""
    print("\n📦 检查依赖包...")
    
    required_packages = [
        'pytest',
        'pytest-django',
        'django',
        'rest_framework'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r tests/requirements.txt")
        return False
    
    return True


def check_django_settings():
    """检查Django设置"""
    print("\n⚙️  检查Django设置...")
    
    try:
        import django
        django.setup()
        
        from django.conf import settings
        print(f"✅ Django版本: {django.get_version()}")
        print(f"✅ 项目名称: {settings.BASE_DIR.name}")
        print(f"✅ 数据库引擎: {settings.DATABASES['default']['ENGINE']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Django设置检查失败: {e}")
        return False


def check_test_directories():
    """检查测试目录结构"""
    print("\n📁 检查测试目录结构...")
    
    tests_dir = project_root / 'tests'
    required_dirs = [
        'regression',
        'new_features',
        'resources/fixtures',
        'resources/mocks',
        'reports/html',
        'reports/json',
        'utils'
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        full_path = tests_dir / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path}")
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"\n⚠️  缺少目录: {', '.join(missing_dirs)}")
        print("正在创建缺失的目录...")
        
        for dir_path in missing_dirs:
            full_path = tests_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建目录: {dir_path}")
    
    return True


def run_simple_test():
    """运行简单测试"""
    print("\n🧪 运行简单测试...")
    
    # 创建一个简单的测试文件
    test_file = project_root / 'tests' / 'test_quick_start.py'
    
    test_content = '''# -*- coding: utf-8 -*-
"""
快速开始测试文件
"""

import pytest
from django.test import TestCase


class TestQuickStart(TestCase):
    """快速开始测试类"""
    
    def test_basic_functionality(self):
        """测试基本功能"""
        assert 1 + 1 == 2
        assert "hello" + " world" == "hello world"
    
    def test_django_environment(self):
        """测试Django环境"""
        from django.conf import settings
        assert hasattr(settings, 'BASE_DIR')
        assert hasattr(settings, 'DATABASES')
    
    def test_project_structure(self):
        """测试项目结构"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        assert project_root.exists()
        assert (project_root / 'backend').exists()
        assert (project_root / 'frontend').exists()
'''
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ 创建测试文件")
        
        # 运行测试
        result = subprocess.run(
            ['python', '-m', 'pytest', str(test_file), '-v'],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            print("✅ 简单测试通过")
            return True
        else:
            print("❌ 简单测试失败")
            print("错误输出:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        return False


def show_next_steps():
    """显示下一步操作"""
    print("\n" + "="*60)
    print("🎯 测试环境设置完成！")
    print("="*60)
    
    print("\n📋 可用的测试命令:")
    print("1. 运行所有测试:")
    print("   python tests/run_tests.py")
    
    print("\n2. 运行回归测试:")
    print("   python tests/run_tests.py --mode regression")
    
    print("\n3. 运行新功能测试:")
    print("   python tests/run_tests.py --mode new-feature")
    
    print("\n4. 运行特定模块测试:")
    print("   python tests/run_module_tests.py --list")
    print("   python tests/run_module_tests.py english")
    
    print("\n5. 生成测试报告:")
    print("   python tests/utils/generate_report.py")
    
    print("\n📚 相关文档:")
    print("- 测试体系设计: docs/TESTING_SYSTEM.md")
    print("- 测试用例库: tests/TEST_CASES.md")
    print("- 功能覆盖分析: tests/FUNCTION_COVERAGE_ANALYSIS.md")
    print("- 测试使用指南: tests/README.md")
    
    print("\n🚀 下一步建议:")
    print("1. 查看功能覆盖分析文档，了解需要补充的测试用例")
    print("2. 按照优先级顺序补充单元测试、API测试等")
    print("3. 建立CI/CD流程，实现自动化测试")
    print("4. 定期运行回归测试，确保系统稳定性")


def main():
    """主函数"""
    print("🚀 Alpha项目测试系统快速开始")
    print("="*60)
    
    checks = [
        ("Python版本检查", check_python_version),
        ("依赖包检查", check_dependencies),
        ("Django设置检查", check_django_settings),
        ("测试目录检查", check_test_directories),
        ("简单测试运行", run_simple_test),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} 出现异常: {e}")
            all_passed = False
    
    if all_passed:
        show_next_steps()
        print("\n🎉 所有检查通过！测试环境已准备就绪。")
        return True
    else:
        print("\n💥 部分检查失败，请根据上述提示解决问题。")
        return False


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 出现未预期的错误: {e}")
        sys.exit(1)
# -*- coding: utf-8 -*-
"""
测试系统快速开始脚本
用于快速验证测试环境是否正常工作
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ['TESTING'] = 'true'
os.environ['DJANGO_SETTINGS_MODULE'] = 'alpha.settings'


def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python版本过低: {version.major}.{version.minor}")
        print("需要Python 3.8+")
        return False
    else:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True


def check_dependencies():
    """检查依赖包"""
    print("\n📦 检查依赖包...")
    
    required_packages = [
        'pytest',
        'pytest-django',
        'django',
        'rest_framework'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r tests/requirements.txt")
        return False
    
    return True


def check_django_settings():
    """检查Django设置"""
    print("\n⚙️  检查Django设置...")
    
    try:
        import django
        django.setup()
        
        from django.conf import settings
        print(f"✅ Django版本: {django.get_version()}")
        print(f"✅ 项目名称: {settings.BASE_DIR.name}")
        print(f"✅ 数据库引擎: {settings.DATABASES['default']['ENGINE']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Django设置检查失败: {e}")
        return False


def check_test_directories():
    """检查测试目录结构"""
    print("\n📁 检查测试目录结构...")
    
    tests_dir = project_root / 'tests'
    required_dirs = [
        'regression',
        'new_features',
        'resources/fixtures',
        'resources/mocks',
        'reports/html',
        'reports/json',
        'utils'
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        full_path = tests_dir / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path}")
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"\n⚠️  缺少目录: {', '.join(missing_dirs)}")
        print("正在创建缺失的目录...")
        
        for dir_path in missing_dirs:
            full_path = tests_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建目录: {dir_path}")
    
    return True


def run_simple_test():
    """运行简单测试"""
    print("\n🧪 运行简单测试...")
    
    # 创建一个简单的测试文件
    test_file = project_root / 'tests' / 'test_quick_start.py'
    
    test_content = '''# -*- coding: utf-8 -*-
"""
快速开始测试文件
"""

import pytest
from django.test import TestCase


class TestQuickStart(TestCase):
    """快速开始测试类"""
    
    def test_basic_functionality(self):
        """测试基本功能"""
        assert 1 + 1 == 2
        assert "hello" + " world" == "hello world"
    
    def test_django_environment(self):
        """测试Django环境"""
        from django.conf import settings
        assert hasattr(settings, 'BASE_DIR')
        assert hasattr(settings, 'DATABASES')
    
    def test_project_structure(self):
        """测试项目结构"""
        from pathlib import Path
        project_root = Path(__file__).parent.parent
        assert project_root.exists()
        assert (project_root / 'backend').exists()
        assert (project_root / 'frontend').exists()
'''
    
    try:
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print("✅ 创建测试文件")
        
        # 运行测试
        result = subprocess.run(
            ['python', '-m', 'pytest', str(test_file), '-v'],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            print("✅ 简单测试通过")
            return True
        else:
            print("❌ 简单测试失败")
            print("错误输出:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        return False


def show_next_steps():
    """显示下一步操作"""
    print("\n" + "="*60)
    print("🎯 测试环境设置完成！")
    print("="*60)
    
    print("\n📋 可用的测试命令:")
    print("1. 运行所有测试:")
    print("   python tests/run_tests.py")
    
    print("\n2. 运行回归测试:")
    print("   python tests/run_tests.py --mode regression")
    
    print("\n3. 运行新功能测试:")
    print("   python tests/run_tests.py --mode new-feature")
    
    print("\n4. 运行特定模块测试:")
    print("   python tests/run_module_tests.py --list")
    print("   python tests/run_module_tests.py english")
    
    print("\n5. 生成测试报告:")
    print("   python tests/utils/generate_report.py")
    
    print("\n📚 相关文档:")
    print("- 测试体系设计: docs/TESTING_SYSTEM.md")
    print("- 测试用例库: tests/TEST_CASES.md")
    print("- 功能覆盖分析: tests/FUNCTION_COVERAGE_ANALYSIS.md")
    print("- 测试使用指南: tests/README.md")
    
    print("\n🚀 下一步建议:")
    print("1. 查看功能覆盖分析文档，了解需要补充的测试用例")
    print("2. 按照优先级顺序补充单元测试、API测试等")
    print("3. 建立CI/CD流程，实现自动化测试")
    print("4. 定期运行回归测试，确保系统稳定性")


def main():
    """主函数"""
    print("🚀 Alpha项目测试系统快速开始")
    print("="*60)
    
    checks = [
        ("Python版本检查", check_python_version),
        ("依赖包检查", check_dependencies),
        ("Django设置检查", check_django_settings),
        ("测试目录检查", check_test_directories),
        ("简单测试运行", run_simple_test),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} 出现异常: {e}")
            all_passed = False
    
    if all_passed:
        show_next_steps()
        print("\n🎉 所有检查通过！测试环境已准备就绪。")
        return True
    else:
        print("\n💥 部分检查失败，请根据上述提示解决问题。")
        return False


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 出现未预期的错误: {e}")
        sys.exit(1)
