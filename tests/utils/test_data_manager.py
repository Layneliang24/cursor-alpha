"""
测试数据管理器

提供统一的测试数据创建、管理和清理功能：
1. 测试数据工厂管理
2. 数据库状态管理
3. 测试环境隔离
4. 数据清理和重置
"""

import os
import json
from typing import Dict, List, Any, Optional, Type
from pathlib import Path
from contextlib import contextmanager
from dataclasses import dataclass
import tempfile
import shutil

from django.test import TestCase, TransactionTestCase
from django.db import transaction, connection
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.conf import settings

from tests.factories import (
    UserFactory, UserProfileFactory, CategoryFactory, ArticleFactory,
    DictionaryFactory, WordFactory, TypingWordFactory, ExpressionFactory,
    NewsFactory, TypingSessionFactory, UserTypingStatsFactory
)


User = get_user_model()


@dataclass
class TestDataSet:
    """测试数据集定义"""
    name: str
    description: str
    data: Dict[str, Any]
    dependencies: List[str] = None  # 依赖的其他数据集
    cleanup_order: List[str] = None  # 清理顺序


class TestDataManager:
    """测试数据管理器"""
    
    def __init__(self):
        self.data_sets = {}
        self.created_objects = {}
        self.temp_files = []
        self.backup_path = None
        
        # 注册标准数据集
        self._register_standard_datasets()
    
    def _register_standard_datasets(self):
        """注册标准测试数据集"""
        
        # 基础用户数据集
        self.register_dataset(TestDataSet(
            name="basic_users",
            description="基础用户数据：管理员、普通用户、测试用户",
            data={
                "admin_user": {
                    "factory": UserFactory,
                    "params": {
                        "username": "admin",
                        "email": "admin@test.com",
                        "is_staff": True,
                        "is_superuser": True
                    }
                },
                "normal_user": {
                    "factory": UserFactory,
                    "params": {
                        "username": "user",
                        "email": "user@test.com"
                    }
                },
                "test_user": {
                    "factory": UserFactory,
                    "params": {
                        "username": "testuser",
                        "email": "testuser@test.com"
                    }
                }
            }
        ))
        
        # 文章系统数据集
        self.register_dataset(TestDataSet(
            name="article_system",
            description="文章系统数据：分类、文章、标签",
            data={
                "tech_category": {
                    "factory": CategoryFactory,
                    "params": {
                        "name": "技术",
                        "description": "技术相关文章"
                    }
                },
                "life_category": {
                    "factory": CategoryFactory,
                    "params": {
                        "name": "生活",
                        "description": "生活相关文章"
                    }
                },
                "sample_article": {
                    "factory": ArticleFactory,
                    "params": {
                        "title": "测试文章",
                        "content": "这是一篇测试文章的内容",
                        "category": "@tech_category",  # 引用其他对象
                        "author": "@normal_user"
                    }
                }
            },
            dependencies=["basic_users"]
        ))
        
        # 英语学习数据集
        self.register_dataset(TestDataSet(
            name="english_learning",
            description="英语学习数据：词典、单词、表达式",
            data={
                "cet4_dict": {
                    "factory": DictionaryFactory,
                    "params": {
                        "name": "CET4",
                        "description": "大学英语四级词汇"
                    }
                },
                "sample_words": {
                    "factory": TypingWordFactory,
                    "count": 10,
                    "params": {
                        "dictionary": "@cet4_dict",
                        "difficulty": "easy"
                    }
                },
                "sample_expressions": {
                    "factory": ExpressionFactory,
                    "count": 5,
                    "params": {
                        "difficulty": "intermediate"
                    }
                }
            }
        ))
        
        # 打字练习数据集
        self.register_dataset(TestDataSet(
            name="typing_practice",
            description="打字练习数据：会话、统计",
            data={
                "practice_sessions": {
                    "factory": TypingSessionFactory,
                    "count": 20,
                    "params": {
                        "user": "@test_user",
                        "word": "@sample_words[0]",  # 引用数组中的元素
                        "is_correct": True
                    }
                },
                "user_stats": {
                    "factory": UserTypingStatsFactory,
                    "params": {
                        "user": "@test_user",
                        "total_words_practiced": 100,
                        "total_correct_words": 85,
                        "average_wpm": 45.5
                    }
                }
            },
            dependencies=["basic_users", "english_learning"]
        ))
    
    def register_dataset(self, dataset: TestDataSet):
        """注册测试数据集"""
        self.data_sets[dataset.name] = dataset
    
    @contextmanager
    def isolated_test_environment(self):
        """创建隔离的测试环境"""
        # 备份当前数据库状态
        self.backup_database()
        
        try:
            yield self
        finally:
            # 恢复数据库状态
            self.restore_database()
            # 清理临时文件
            self.cleanup_temp_files()
    
    def create_dataset(self, name: str, **kwargs) -> Dict[str, Any]:
        """创建测试数据集"""
        if name not in self.data_sets:
            raise ValueError(f"未知的数据集: {name}")
        
        dataset = self.data_sets[name]
        
        # 检查并创建依赖的数据集
        if dataset.dependencies:
            for dep in dataset.dependencies:
                if dep not in self.created_objects:
                    self.create_dataset(dep)
        
        # 创建数据集中的对象
        created_objects = {}
        
        for obj_name, obj_config in dataset.data.items():
            factory = obj_config["factory"]
            params = obj_config.get("params", {})
            count = obj_config.get("count", 1)
            
            # 解析参数中的引用
            resolved_params = self._resolve_references(params)
            
            # 创建对象
            if count == 1:
                obj = factory(**resolved_params, **kwargs)
                created_objects[obj_name] = obj
            else:
                objects = []
                for i in range(count):
                    obj = factory(**resolved_params, **kwargs)
                    objects.append(obj)
                created_objects[obj_name] = objects
        
        # 保存创建的对象
        self.created_objects[name] = created_objects
        
        return created_objects
    
    def _resolve_references(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """解析参数中的对象引用"""
        resolved = {}
        
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("@"):
                # 解析引用：@dataset.object 或 @object
                ref = value[1:]  # 去掉@符号
                
                if "[" in ref and "]" in ref:
                    # 数组引用：@object[index]
                    obj_name, index_part = ref.split("[")
                    index = int(index_part.rstrip("]"))
                    resolved[key] = self._get_referenced_object(obj_name)[index]
                else:
                    # 简单引用：@object
                    resolved[key] = self._get_referenced_object(ref)
            else:
                resolved[key] = value
        
        return resolved
    
    def _get_referenced_object(self, ref: str):
        """获取引用的对象"""
        # 在所有创建的对象中查找
        for dataset_name, objects in self.created_objects.items():
            if ref in objects:
                return objects[ref]
        
        raise ValueError(f"找不到引用的对象: {ref}")
    
    def get_object(self, dataset_name: str, object_name: str):
        """获取指定数据集中的对象"""
        if dataset_name not in self.created_objects:
            raise ValueError(f"数据集 {dataset_name} 尚未创建")
        
        if object_name not in self.created_objects[dataset_name]:
            raise ValueError(f"对象 {object_name} 在数据集 {dataset_name} 中不存在")
        
        return self.created_objects[dataset_name][object_name]
    
    def cleanup_dataset(self, name: str):
        """清理指定数据集"""
        if name not in self.created_objects:
            return
        
        dataset = self.data_sets[name]
        objects = self.created_objects[name]
        
        # 按照清理顺序删除对象
        cleanup_order = dataset.cleanup_order or list(objects.keys())
        
        for obj_name in reversed(cleanup_order):
            if obj_name in objects:
                obj = objects[obj_name]
                if isinstance(obj, list):
                    for item in obj:
                        self._safe_delete(item)
                else:
                    self._safe_delete(obj)
        
        del self.created_objects[name]
    
    def _safe_delete(self, obj):
        """安全删除对象"""
        try:
            if hasattr(obj, 'delete'):
                obj.delete()
        except Exception as e:
            # 记录但不抛出异常
            print(f"警告: 删除对象时出错 {obj}: {e}")
    
    def cleanup_all(self):
        """清理所有创建的数据"""
        # 按照依赖关系的反向顺序清理
        cleanup_order = self._get_cleanup_order()
        
        for dataset_name in cleanup_order:
            self.cleanup_dataset(dataset_name)
    
    def _get_cleanup_order(self) -> List[str]:
        """获取清理顺序（依赖关系的反向）"""
        # 简单实现：按照创建顺序的反向
        return list(reversed(self.created_objects.keys()))
    
    def backup_database(self):
        """备份数据库状态"""
        if not settings.DATABASES['default']['ENGINE'].endswith('sqlite3'):
            # 非SQLite数据库，跳过备份
            return
        
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            self.backup_path = f"{db_path}.backup_{os.getpid()}"
            shutil.copy2(db_path, self.backup_path)
    
    def restore_database(self):
        """恢复数据库状态"""
        if self.backup_path and os.path.exists(self.backup_path):
            db_path = settings.DATABASES['default']['NAME']
            shutil.copy2(self.backup_path, db_path)
            os.remove(self.backup_path)
            self.backup_path = None
    
    def create_temp_file(self, content: str, suffix: str = ".tmp") -> str:
        """创建临时文件"""
        fd, path = tempfile.mkstemp(suffix=suffix)
        try:
            with os.fdopen(fd, 'w') as f:
                f.write(content)
        except:
            os.close(fd)
            raise
        
        self.temp_files.append(path)
        return path
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        for path in self.temp_files:
            if os.path.exists(path):
                os.remove(path)
        self.temp_files.clear()
    
    def reset_database(self):
        """重置数据库到初始状态"""
        # 清理所有数据
        self.cleanup_all()
        
        # 重置数据库
        with connection.cursor() as cursor:
            # 获取所有表名
            tables = connection.introspection.table_names()
            
            # 删除所有数据（保留表结构）
            for table in tables:
                if not table.startswith('django_'):
                    cursor.execute(f'DELETE FROM {table}')
        
        # 运行迁移确保数据库结构正确
        call_command('migrate', verbosity=0, interactive=False)


class EnhancedTestCase(TestCase):
    """增强的测试用例基类"""
    
    def setUp(self):
        """测试前准备"""
        super().setUp()
        self.data_manager = TestDataManager()
        
        # 自动创建基础数据集
        if hasattr(self, 'required_datasets'):
            for dataset_name in self.required_datasets:
                self.data_manager.create_dataset(dataset_name)
    
    def tearDown(self):
        """测试后清理"""
        self.data_manager.cleanup_all()
        super().tearDown()
    
    def create_test_data(self, dataset_name: str, **kwargs):
        """创建测试数据"""
        return self.data_manager.create_dataset(dataset_name, **kwargs)
    
    def get_test_object(self, dataset_name: str, object_name: str):
        """获取测试对象"""
        return self.data_manager.get_object(dataset_name, object_name)


class IsolatedTestCase(TransactionTestCase):
    """隔离的测试用例（用于需要真实事务的测试）"""
    
    def setUp(self):
        """测试前准备"""
        super().setUp()
        self.data_manager = TestDataManager()
    
    def tearDown(self):
        """测试后清理"""
        self.data_manager.cleanup_all()
        super().tearDown()
    
    @contextmanager
    def isolated_environment(self):
        """创建隔离环境"""
        with self.data_manager.isolated_test_environment():
            yield self.data_manager


# 全局数据管理器实例
global_data_manager = TestDataManager()


def create_test_dataset(name: str, **kwargs):
    """便捷函数：创建测试数据集"""
    return global_data_manager.create_dataset(name, **kwargs)


def cleanup_test_data():
    """便捷函数：清理测试数据"""
    global_data_manager.cleanup_all()


# 装饰器：自动管理测试数据
def with_test_data(*dataset_names):
    """装饰器：自动创建和清理测试数据"""
    def decorator(test_func):
        def wrapper(self, *args, **kwargs):
            data_manager = getattr(self, 'data_manager', global_data_manager)
            
            # 创建数据集
            for dataset_name in dataset_names:
                data_manager.create_dataset(dataset_name)
            
            try:
                return test_func(self, *args, **kwargs)
            finally:
                # 清理数据集
                for dataset_name in dataset_names:
                    data_manager.cleanup_dataset(dataset_name)
        
        return wrapper
    return decorator


print("✅ 测试数据管理器创建完成")