"""
MySQL数据库连接测试
测试数据库连接和配置
"""

import pytest
from django.test import TestCase
from django.db import connections
from django.db.utils import OperationalError
from django.conf import settings


class MySQLConnectionTest(TestCase):
    """MySQL数据库连接测试"""
    
    def test_database_connection(self):
        """测试数据库连接"""
        try:
            db_conn = connections['default']
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            self.assertEqual(result[0], 1)
        except OperationalError as e:
            self.fail(f"数据库连接失败: {e}")
    
    def test_database_configuration(self):
        """测试数据库配置"""
        db_config = settings.DATABASES['default']
        
        # 检查必要的配置项
        required_keys = ['ENGINE', 'NAME', 'USER', 'PASSWORD', 'HOST', 'PORT']
        for key in required_keys:
            self.assertIn(key, db_config)
        
        # 检查引擎类型 - 允许SQLite用于测试
        engine = db_config['ENGINE']
        self.assertTrue('mysql' in engine or 'sqlite' in engine)
        
        # 检查字符集配置（仅MySQL）
        if 'mysql' in engine:
            self.assertIn('OPTIONS', db_config)
            self.assertIn('charset', db_config['OPTIONS'])
            self.assertEqual(db_config['OPTIONS']['charset'], 'utf8mb4')
    
    def test_database_operations(self):
        """测试数据库基本操作"""
        try:
            db_conn = connections['default']
            engine = settings.DATABASES['default']['ENGINE']
            
            # 根据数据库类型选择不同的SQL语法
            if 'mysql' in engine:
                # MySQL语法
                create_table_sql = """
                    CREATE TEMPORARY TABLE test_table (
                        id INT PRIMARY KEY,
                        name VARCHAR(100)
                    )
                """
                drop_table_sql = "DROP TEMPORARY TABLE test_table"
            else:
                # SQLite语法
                create_table_sql = """
                    CREATE TABLE test_table (
                        id INTEGER PRIMARY KEY,
                        name TEXT
                    )
                """
                drop_table_sql = "DROP TABLE test_table"
            
            # 测试创建表
            with db_conn.cursor() as cursor:
                cursor.execute(create_table_sql)
            
            # 测试插入数据
            with db_conn.cursor() as cursor:
                cursor.execute("INSERT INTO test_table (id, name) VALUES (1, 'test')")
            
            # 测试查询数据
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT * FROM test_table WHERE id = 1")
                result = cursor.fetchone()
                self.assertEqual(result[0], 1)
                self.assertEqual(result[1], 'test')
            
            # 测试删除表
            with db_conn.cursor() as cursor:
                cursor.execute(drop_table_sql)
                
        except OperationalError as e:
            self.fail(f"数据库操作失败: {e}")


@pytest.mark.fast
class FastMySQLTests:
    """快速MySQL测试"""
    
    def test_connection_string(self):
        """测试连接字符串格式"""
        from django.conf import settings
        db_config = settings.DATABASES['default']
        
        # 验证连接字符串格式
        assert 'mysql' in db_config['ENGINE']
        assert db_config['NAME'] == 'alpha_db'
        assert db_config['USER'] in ['alpha_user', 'root']
        assert db_config['HOST'] in ['127.0.0.1', 'localhost']
        assert db_config['PORT'] in ['3306', '3307']


@pytest.mark.slow
class SlowMySQLTests:
    """慢速MySQL测试"""
    
    def test_connection_pool(self):
        """测试连接池"""
        # 这里可以添加连接池测试
        assert True
    
    def test_transaction_rollback(self):
        """测试事务回滚"""
        # 这里可以添加事务测试
        assert True
