"""
数据存储与性能优化测试
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.core.cache import cache
from django.utils import timezone

from apps.english.data_storage import (
    StorageMetrics,
    DatabaseConnectionManager,
    BatchProcessor,
    PerformanceMonitor,
    DataBackupManager,
    OptimizedDataStorage
)
from apps.english.expression_crawler import ExpressionItem
from apps.english.models import IdiomaticExpression, ExpressionSource, ExpressionScenario, News


class StorageMetricsTest(TestCase):
    """存储指标测试"""
    
    def test_storage_metrics_creation(self):
        """测试存储指标创建"""
        start_time = time.time()
        end_time = start_time + 10
        
        metrics = StorageMetrics(
            operation_type='test_operation',
            start_time=start_time,
            end_time=end_time,
            duration=10.0,
            items_processed=100,
            items_saved=95,
            items_skipped=5,
            batch_size=50,
            memory_usage=1024.0,
            db_queries=10,
            cache_hits=20,
            cache_misses=5,
            errors=[]
        )
        
        # 验证基本属性
        self.assertEqual(metrics.operation_type, 'test_operation')
        self.assertEqual(metrics.items_processed, 100)
        self.assertEqual(metrics.items_saved, 95)
        self.assertEqual(metrics.items_skipped, 5)
        
        # 验证计算属性
        self.assertEqual(metrics.throughput, 10.0)  # 100/10
        self.assertEqual(metrics.success_rate, 0.95)  # 95/100
    
    def test_throughput_calculation(self):
        """测试吞吐量计算"""
        metrics = StorageMetrics(
            operation_type='test',
            start_time=0, end_time=0, duration=5.0,
            items_processed=50, items_saved=0, items_skipped=0,
            batch_size=10, memory_usage=0, db_queries=0,
            cache_hits=0, cache_misses=0, errors=[]
        )
        
        self.assertEqual(metrics.throughput, 10.0)  # 50/5
    
    def test_success_rate_calculation(self):
        """测试成功率计算"""
        metrics = StorageMetrics(
            operation_type='test',
            start_time=0, end_time=0, duration=1.0,
            items_processed=20, items_saved=18, items_skipped=2,
            batch_size=10, memory_usage=0, db_queries=0,
            cache_hits=0, cache_misses=0, errors=[]
        )
        
        self.assertEqual(metrics.success_rate, 0.9)  # 18/20


class DatabaseConnectionManagerTest(TestCase):
    """数据库连接管理器测试"""
    
    def setUp(self):
        self.manager = DatabaseConnectionManager(max_connections=3)
    
    def test_connection_manager_creation(self):
        """测试连接管理器创建"""
        self.assertEqual(self.manager.max_connections, 3)
        self.assertEqual(len(self.manager._connection_pool), 0)
    
    def test_get_connection_stats(self):
        """测试获取连接统计"""
        stats = self.manager.get_connection_stats()
        
        self.assertIn('active_connections', stats)
        self.assertIn('max_connections', stats)
        self.assertIn('connection_keys', stats)
        self.assertEqual(stats['max_connections'], 3)
        self.assertEqual(stats['active_connections'], 0)
    
    def test_close_all_connections(self):
        """测试关闭所有连接"""
        # 模拟一些连接
        mock_conn = Mock()
        self.manager._connection_pool['test_conn'] = mock_conn
        
        self.manager.close_all_connections()
        
        # 验证连接被关闭
        mock_conn.close.assert_called_once()
        self.assertEqual(len(self.manager._connection_pool), 0)


class BatchProcessorTest(TransactionTestCase):
    """批量处理器测试"""
    
    def setUp(self):
        self.processor = BatchProcessor(batch_size=5)
        cache.clear()
    
    def test_batch_processor_creation(self):
        """测试批量处理器创建"""
        self.assertEqual(self.processor.batch_size, 5)
        self.assertIsNotNone(self.processor.connection_manager)
    
    @patch('apps.english.data_storage.IdiomaticExpression')
    @patch('apps.english.data_storage.ExpressionSource')
    def test_process_expressions_batch(self, mock_source_model, mock_expression_model):
        """测试批量处理表达式"""
        # 设置模拟
        mock_source_instance = Mock()
        mock_source_model.objects.get_or_create.return_value = (mock_source_instance, True)
        mock_expression_model.objects.filter.return_value.exists.return_value = False
        mock_expression_instance = Mock()
        mock_expression_model.objects.create.return_value = mock_expression_instance
        
        # 创建测试数据
        expressions = [
            ExpressionItem(
                expression=f'test expression {i}',
                meaning=f'test meaning {i}',
                source_url='https://test.com',
                source_name='TestSource'
            )
            for i in range(3)
        ]
        
        # 执行批量处理
        metrics = self.processor.process_expressions_batch(expressions)
        
        # 验证结果
        self.assertEqual(metrics.operation_type, 'batch_expressions')
        self.assertEqual(metrics.items_processed, 3)
        self.assertGreaterEqual(metrics.duration, 0)
        self.assertIsInstance(metrics.errors, list)
    
    def test_empty_batch_processing(self):
        """测试空批次处理"""
        metrics = self.processor.process_expressions_batch([])
        
        self.assertEqual(metrics.items_processed, 0)
        self.assertEqual(metrics.items_saved, 0)
        self.assertEqual(metrics.items_skipped, 0)


class PerformanceMonitorTest(TestCase):
    """性能监控器测试"""
    
    def setUp(self):
        self.monitor = PerformanceMonitor()
        cache.clear()
    
    def test_performance_monitor_creation(self):
        """测试性能监控器创建"""
        self.assertEqual(self.monitor.cache_prefix, "perf_monitor")
        self.assertEqual(len(self.monitor.metrics_history), 0)
    
    def test_record_metrics(self):
        """测试记录性能指标"""
        metrics = StorageMetrics(
            operation_type='test_record',
            start_time=time.time(),
            end_time=time.time() + 1,
            duration=1.0,
            items_processed=10,
            items_saved=9,
            items_skipped=1,
            batch_size=5,
            memory_usage=512.0,
            db_queries=5,
            cache_hits=3,
            cache_misses=2,
            errors=[]
        )
        
        self.monitor.record_metrics(metrics)
        
        # 验证指标被记录
        self.assertEqual(len(self.monitor.metrics_history), 1)
        self.assertEqual(self.monitor.metrics_history[0], metrics)
    
    def test_get_performance_summary_empty(self):
        """测试获取空的性能摘要"""
        summary = self.monitor.get_performance_summary(hours=1)
        
        self.assertIn('message', summary)
        self.assertIn('过去1小时无性能数据', summary['message'])
    
    def test_get_performance_summary_with_data(self):
        """测试获取有数据的性能摘要"""
        # 添加测试指标
        current_time = time.time()
        metrics = StorageMetrics(
            operation_type='test_summary',
            start_time=current_time,
            end_time=current_time + 2,
            duration=2.0,
            items_processed=20,
            items_saved=18,
            items_skipped=2,
            batch_size=10,
            memory_usage=1024.0,
            db_queries=8,
            cache_hits=5,
            cache_misses=3,
            errors=[]
        )
        
        self.monitor.record_metrics(metrics)
        
        # 获取摘要
        summary = self.monitor.get_performance_summary(hours=1)
        
        # 验证摘要内容
        self.assertIn('operations_count', summary)
        self.assertIn('total_items_processed', summary)
        self.assertIn('total_items_saved', summary)
        self.assertIn('average_throughput', summary)
        self.assertIn('average_success_rate', summary)
        
        self.assertEqual(summary['operations_count'], 1)
        self.assertEqual(summary['total_items_processed'], 20)
        self.assertEqual(summary['total_items_saved'], 18)
    
    @patch('apps.english.data_storage.connection')
    def test_get_database_performance(self, mock_connection):
        """测试获取数据库性能指标"""
        # 设置模拟
        mock_cursor = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # 模拟查询结果
        mock_cursor.fetchall.return_value = [
            ('english_idiomaticexpression', 1000),
            ('english_newsitem', 500)
        ]
        mock_cursor.fetchone.side_effect = [
            ('Threads_connected', '10'),
            ('Questions', '50000')
        ]
        
        # 执行测试
        performance = self.monitor.get_database_performance()
        
        # 验证结果
        self.assertIn('table_stats', performance)
        self.assertIn('active_connections', performance)
        self.assertIn('total_queries', performance)
        self.assertEqual(performance['active_connections'], 10)
        self.assertEqual(performance['total_queries'], 50000)
    
    @patch('apps.english.data_storage.connection')
    def test_optimize_database_indexes(self, mock_connection):
        """测试数据库索引优化"""
        # 设置模拟
        mock_cursor = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        # 模拟索引不存在的情况
        mock_cursor.fetchone.return_value = (0,)  # 索引不存在
        
        # 执行优化
        result = self.monitor.optimize_database_indexes()
        
        # 验证结果
        self.assertIn('status', result)
        self.assertIn('results', result)
        self.assertEqual(result['status'], 'completed')


class DataBackupManagerTest(TestCase):
    """数据备份管理器测试"""
    
    def setUp(self):
        self.backup_manager = DataBackupManager()
    
    def test_backup_manager_creation(self):
        """测试备份管理器创建"""
        self.assertEqual(self.backup_manager.backup_dir, "/tmp/backups")
    
    @patch('apps.english.data_storage.connection')
    def test_create_backup(self, mock_connection):
        """测试创建备份"""
        # 设置模拟
        mock_cursor = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (100,)  # 模拟记录数
        
        # 执行备份
        backup_info = self.backup_manager.create_backup(['test_table'])
        
        # 验证结果
        self.assertIn('timestamp', backup_info)
        self.assertIn('tables', backup_info)
        self.assertIn('total_records', backup_info)
        self.assertIn('status', backup_info)
        
        self.assertEqual(len(backup_info['tables']), 1)
        self.assertEqual(backup_info['total_records'], 100)
    
    @patch('apps.english.data_storage.connection')
    def test_backup_table(self, mock_connection):
        """测试备份单个表"""
        # 设置模拟
        mock_cursor = Mock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (50,)
        
        # 执行表备份
        table_info = self.backup_manager._backup_table('test_table')
        
        # 验证结果
        self.assertEqual(table_info['table_name'], 'test_table')
        self.assertEqual(table_info['record_count'], 50)
        self.assertIn('backup_file', table_info)
        self.assertEqual(table_info['status'], 'completed')


class OptimizedDataStorageTest(TransactionTestCase):
    """优化数据存储系统测试"""
    
    def setUp(self):
        self.storage = OptimizedDataStorage(batch_size=5)
        cache.clear()
    
    def test_optimized_storage_creation(self):
        """测试优化存储系统创建"""
        self.assertIsNotNone(self.storage.batch_processor)
        self.assertIsNotNone(self.storage.performance_monitor)
        self.assertIsNotNone(self.storage.connection_manager)
        self.assertIsNotNone(self.storage.backup_manager)
    
    def test_store_expressions_empty(self):
        """测试存储空表达式列表"""
        result = self.storage.store_expressions([])
        
        self.assertEqual(result['status'], 'skipped')
        self.assertIn('没有数据需要存储', result['message'])
    
    @patch.object(BatchProcessor, 'process_expressions_batch')
    def test_store_expressions_with_data(self, mock_process_batch):
        """测试存储表达式数据"""
        # 设置模拟
        mock_metrics = StorageMetrics(
            operation_type='test_store',
            start_time=time.time(),
            end_time=time.time() + 1,
            duration=1.0,
            items_processed=5,
            items_saved=4,
            items_skipped=1,
            batch_size=5,
            memory_usage=512.0,
            db_queries=10,
            cache_hits=5,
            cache_misses=0,
            errors=[]
        )
        mock_process_batch.return_value = mock_metrics
        
        # 创建测试数据
        expressions = [
            ExpressionItem(
                expression='test expression',
                meaning='test meaning',
                source_url='https://test.com',
                source_name='TestSource'
            )
        ]
        
        # 执行存储
        result = self.storage.store_expressions(expressions)
        
        # 验证结果
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['total_processed'], 5)
        self.assertEqual(result['total_saved'], 4)
        self.assertEqual(result['total_skipped'], 1)
        self.assertIn('duration', result)
        self.assertIn('throughput', result)
        self.assertIn('success_rate', result)
        
        # 验证方法被调用
        mock_process_batch.assert_called_once_with(expressions)
    
    def test_get_system_status(self):
        """测试获取系统状态"""
        status = self.storage.get_system_status()
        
        self.assertIn('performance_summary', status)
        self.assertIn('database_performance', status)
        self.assertIn('connection_stats', status)
        self.assertIn('timestamp', status)
    
    @patch.object(PerformanceMonitor, 'optimize_database_indexes')
    def test_optimize_system(self, mock_optimize_db):
        """测试优化系统性能"""
        # 设置模拟
        mock_optimize_db.return_value = {
            'status': 'completed',
            'results': ['创建索引: test_index']
        }
        
        # 执行优化
        result = self.storage.optimize_system()
        
        # 验证结果
        self.assertIn('database_optimization', result)
        self.assertIn('connection_cleanup', result)
        self.assertIn('cache_cleanup', result)
        self.assertIn('timestamp', result)
        
        # 验证数据库优化被调用
        mock_optimize_db.assert_called_once()
    
    def test_cleanup_connections(self):
        """测试清理连接"""
        # 添加一些模拟连接
        self.storage.connection_manager._connection_pool['test'] = Mock()
        
        result = self.storage._cleanup_connections()
        
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['closed_connections'], 1)
        self.assertEqual(len(self.storage.connection_manager._connection_pool), 0)
    
    def test_cleanup_cache(self):
        """测试清理缓存"""
        # 添加一些测试缓存
        cache.set('perf_monitor:test1', 'value1', 60)
        cache.set('perf_monitor:test2', 'value2', 60)
        cache.set('other:key', 'value', 60)
        
        result = self.storage._cleanup_cache()
        
        self.assertEqual(result['status'], 'completed')
        # 注意：实际的cleared_keys数量可能因缓存实现而异


class IntegrationTest(TransactionTestCase):
    """集成测试"""
    
    def setUp(self):
        self.storage = OptimizedDataStorage(batch_size=3)
        cache.clear()
    
    def test_full_storage_workflow(self):
        """测试完整的存储工作流程"""
        # 准备测试数据
        expressions = [
            ExpressionItem(
                expression='break the ice',
                meaning='to start a conversation',
                source_url='https://test.com',
                source_name='TestSource',
                expression_type='idiom',
                formality_level='neutral',
                frequency_score=7,
                usage_examples=['Let me break the ice.'],
                scenarios=['social']
            ),
            ExpressionItem(
                expression='piece of cake',
                meaning='very easy',
                source_url='https://test.com',
                source_name='TestSource',
                expression_type='idiom',
                formality_level='informal',
                frequency_score=8,
                usage_examples=['This test is a piece of cake.'],
                scenarios=['casual']
            )
        ]
        
        # 执行存储
        with patch('apps.english.data_storage.IdiomaticExpression') as mock_expression:
            with patch('apps.english.data_storage.ExpressionSource') as mock_source:
                # 设置模拟
                mock_source_instance = Mock()
                mock_source.objects.get_or_create.return_value = (mock_source_instance, True)
                mock_expression.objects.filter.return_value.exists.return_value = False
                mock_expression_instance = Mock()
                mock_expression.objects.create.return_value = mock_expression_instance
                
                result = self.storage.store_expressions(expressions)
        
        # 验证结果
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['total_processed'], 2)
        self.assertGreaterEqual(result['duration'], 0)
        self.assertGreater(result['throughput'], 0)
        
        # 验证性能监控记录了指标
        self.assertGreater(len(self.storage.performance_monitor.metrics_history), 0)
        
        # 获取系统状态
        status = self.storage.get_system_status()
        self.assertIn('performance_summary', status)
        
        # 执行系统优化
        optimization_result = self.storage.optimize_system()
        self.assertIn('database_optimization', optimization_result)
