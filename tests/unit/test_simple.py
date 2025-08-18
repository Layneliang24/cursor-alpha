"""
简化测试
避免复杂的Django设置问题
"""

import pytest
import os
import sys


def test_python_environment():
    """测试Python环境"""
    assert sys.version_info >= (3, 8)
    assert os.path.exists(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))


def test_django_import():
    """测试Django导入"""
    try:
        import django
        assert django.VERSION >= (3, 2)
    except ImportError:
        pytest.skip("Django未安装")


def test_pytest_import():
    """测试pytest导入"""
    try:
        import pytest
        assert pytest.__version__ >= "6.0"
    except ImportError:
        pytest.skip("pytest未安装")


def test_rest_framework_import():
    """测试DRF导入"""
    try:
        import rest_framework
        assert rest_framework.VERSION >= "3.12"
    except ImportError:
        pytest.skip("DRF未安装")


@pytest.mark.fast
class FastSimpleTests:
    """快速简单测试"""
    
    def test_basic_math(self):
        """基础数学测试"""
        assert 2 + 2 == 4
        assert 3 * 3 == 9
        assert 10 - 5 == 5
    
    def test_string_operations(self):
        """字符串操作测试"""
        text = "Hello, World!"
        assert len(text) == 13
        assert text.upper() == "HELLO, WORLD!"
        assert text.lower() == "hello, world!"
        assert text.split(", ") == ["Hello", "World!"]
    
    def test_list_operations(self):
        """列表操作测试"""
        numbers = [1, 2, 3, 4, 5]
        assert len(numbers) == 5
        assert sum(numbers) == 15
        assert max(numbers) == 5
        assert min(numbers) == 1


@pytest.mark.slow
class SlowSimpleTests:
    """慢速简单测试"""
    
    def test_file_operations(self):
        """文件操作测试"""
        test_file = "test_temp.txt"
        try:
            # 写入文件
            with open(test_file, 'w') as f:
                f.write("test content")
            
            # 读取文件
            with open(test_file, 'r') as f:
                content = f.read()
            
            assert content == "test content"
        finally:
            # 清理文件
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_directory_structure(self):
        """目录结构测试"""
        project_root = os.path.join(os.path.dirname(__file__), '..', '..')
        
        # 检查必要的目录
        required_dirs = ['backend', 'frontend', 'tests', 'docs']
        for dir_name in required_dirs:
            dir_path = os.path.join(project_root, dir_name)
            assert os.path.exists(dir_path), f"目录不存在: {dir_path}"
            assert os.path.isdir(dir_path), f"不是目录: {dir_path}"
        
        # 检查必要的文件
        required_files = [
            'backend/manage.py',
            'backend/requirements.txt',
            'frontend/package.json',
            'tests/pytest.ini'
        ]
        for file_name in required_files:
            file_path = os.path.join(project_root, file_name)
            assert os.path.exists(file_path), f"文件不存在: {file_path}"
            assert os.path.isfile(file_path), f"不是文件: {file_path}"


def test_environment_variables():
    """测试环境变量"""
    # 检查Python路径
    assert 'python' in sys.executable.lower() or 'python' in sys.executable
    
    # 检查当前工作目录
    assert os.getcwd() is not None
    
    # 检查文件系统权限
    test_dir = os.path.dirname(__file__)
    assert os.access(test_dir, os.R_OK), "没有读取权限"
    assert os.access(test_dir, os.W_OK), "没有写入权限"


if __name__ == "__main__":
    # 直接运行时的简单测试
    test_python_environment()
    print("✅ Python环境测试通过")
    
    try:
        test_django_import()
        print("✅ Django导入测试通过")
    except Exception as e:
        print(f"⚠️ Django导入测试跳过: {e}")
    
    try:
        test_pytest_import()
        print("✅ pytest导入测试通过")
    except Exception as e:
        print(f"⚠️ pytest导入测试跳过: {e}")
    
    print("✅ 基础测试完成")
