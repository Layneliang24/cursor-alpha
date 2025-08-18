# -*- coding: utf-8 -*-
"""
快速验证测试脚本
用于快速验证新创建的测试脚本是否能正常运行
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
backend_dir = project_root / 'backend'
sys.path.insert(0, str(backend_dir))

# 设置环境变量
os.environ['TESTING'] = 'true'
os.environ['DJANGO_SETTINGS_MODULE'] = 'alpha.settings'


def run_quick_validation():
    """运行快速验证"""
    print("🚀 开始快速验证测试脚本...")
    print("="*60)
    
    # 检查测试文件是否存在
    test_files = [
        'tests/regression/english/test_data_analysis.py',
        'tests/regression/english/test_pronunciation.py',
        'tests/regression/english/test_pause_resume.py'
    ]
    
    print("📁 检查测试文件...")
    for test_file in test_files:
        file_path = project_root / test_file
        if file_path.exists():
            print(f"✅ {test_file}")
        else:
            print(f"❌ {test_file} (文件不存在)")
            return False
    
    print("\n🧪 运行语法检查...")
    
    # 检查Python语法
    for test_file in test_files:
        file_path = project_root / test_file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), str(file_path), 'exec')
            print(f"✅ {test_file} 语法正确")
        except SyntaxError as e:
            print(f"❌ {test_file} 语法错误: {e}")
            return False
        except Exception as e:
            print(f"⚠️  {test_file} 检查时出现异常: {e}")
    
    print("\n🔍 检查导入依赖...")
    
    # 检查关键导入
    try:
        import pytest
        print("✅ pytest")
    except ImportError:
        print("❌ pytest (未安装)")
        return False
    
    try:
        import django
        print("✅ django")
    except ImportError:
        print("❌ django (未安装)")
        return False
    
    try:
        from rest_framework import status
        print("✅ djangorestframework")
    except ImportError:
        print("❌ djangorestframework (未安装)")
        return False
    
    print("\n🎯 运行简单测试...")
    
    # 运行一个简单的测试来验证环境
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', 'tests/test_quick_validation.py::test_basic_functionality', '-v'],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ 基本测试通过")
        else:
            print("❌ 基本测试失败")
            print("错误输出:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  测试超时")
        return False
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
        return False
    
    print("\n🎉 快速验证完成！")
    return True


def test_basic_functionality():
    """基本功能测试"""
    # 这是一个简单的测试，用于验证测试环境
    assert 1 + 1 == 2
    assert "hello" + " world" == "hello world"
    
    # 测试路径操作
    from pathlib import Path
    current_file = Path(__file__)
    assert current_file.exists()
    assert current_file.name == "test_quick_validation.py"


if __name__ == '__main__':
    try:
        success = run_quick_validation()
        if success:
            print("\n🎯 下一步建议:")
            print("1. 运行完整测试套件: python tests/run_tests.py")
            print("2. 运行英语模块测试: python tests/run_module_tests.py english")
            print("3. 查看测试报告: tests/reports/html/")
            sys.exit(0)
        else:
            print("\n💥 快速验证失败，请检查上述问题")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证过程中出现未预期的错误: {e}")
        sys.exit(1)

"""
快速验证测试脚本
用于快速验证新创建的测试脚本是否能正常运行
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
backend_dir = project_root / 'backend'
sys.path.insert(0, str(backend_dir))

# 设置环境变量
os.environ['TESTING'] = 'true'
os.environ['DJANGO_SETTINGS_MODULE'] = 'alpha.settings'


def run_quick_validation():
    """运行快速验证"""
    print("🚀 开始快速验证测试脚本...")
    print("="*60)
    
    # 检查测试文件是否存在
    test_files = [
        'tests/regression/english/test_data_analysis.py',
        'tests/regression/english/test_pronunciation.py',
        'tests/regression/english/test_pause_resume.py'
    ]
    
    print("📁 检查测试文件...")
    for test_file in test_files:
        file_path = project_root / test_file
        if file_path.exists():
            print(f"✅ {test_file}")
        else:
            print(f"❌ {test_file} (文件不存在)")
            return False
    
    print("\n🧪 运行语法检查...")
    
    # 检查Python语法
    for test_file in test_files:
        file_path = project_root / test_file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), str(file_path), 'exec')
            print(f"✅ {test_file} 语法正确")
        except SyntaxError as e:
            print(f"❌ {test_file} 语法错误: {e}")
            return False
        except Exception as e:
            print(f"⚠️  {test_file} 检查时出现异常: {e}")
    
    print("\n🔍 检查导入依赖...")
    
    # 检查关键导入
    try:
        import pytest
        print("✅ pytest")
    except ImportError:
        print("❌ pytest (未安装)")
        return False
    
    try:
        import django
        print("✅ django")
    except ImportError:
        print("❌ django (未安装)")
        return False
    
    try:
        from rest_framework import status
        print("✅ djangorestframework")
    except ImportError:
        print("❌ djangorestframework (未安装)")
        return False
    
    print("\n🎯 运行简单测试...")
    
    # 运行一个简单的测试来验证环境
    try:
        result = subprocess.run(
            ['python', '-m', 'pytest', 'tests/test_quick_validation.py::test_basic_functionality', '-v'],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ 基本测试通过")
        else:
            print("❌ 基本测试失败")
            print("错误输出:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  测试超时")
        return False
    except Exception as e:
        print(f"❌ 运行测试时出错: {e}")
        return False
    
    print("\n🎉 快速验证完成！")
    return True


def test_basic_functionality():
    """基本功能测试"""
    # 这是一个简单的测试，用于验证测试环境
    assert 1 + 1 == 2
    assert "hello" + " world" == "hello world"
    
    # 测试路径操作
    from pathlib import Path
    current_file = Path(__file__)
    assert current_file.exists()
    assert current_file.name == "test_quick_validation.py"


if __name__ == '__main__':
    try:
        success = run_quick_validation()
        if success:
            print("\n🎯 下一步建议:")
            print("1. 运行完整测试套件: python tests/run_tests.py")
            print("2. 运行英语模块测试: python tests/run_module_tests.py english")
            print("3. 查看测试报告: tests/reports/html/")
            sys.exit(0)
        else:
            print("\n💥 快速验证失败，请检查上述问题")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  验证被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证过程中出现未预期的错误: {e}")
        sys.exit(1)
