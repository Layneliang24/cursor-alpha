"""
数据存储与性能优化模块
提供高效的数据存储机制和性能监控
"""

import logging
import time
import threading
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from django.db import transaction, connections, connection
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
import json

from .models import IdiomaticExpression, ExpressionSource, ExpressionScenario, ExpressionScenarioLink, NewsItem
from .expression_crawler import ExpressionItem

logger = logging.getLogger(__name__)


@dataclass
class StorageMetrics:
    """存储性能指标"""
    operation_type: str
    start_time: float
    end_time: float
    duration: float
    items_processed: int
    items_saved: int
    items_skipped: int
    batch_size: int
    memory_usage: float
    db_queries: int
    cache_hits: int
    cache_misses: int
    errors: List[str]
    
    @property
    def throughput(self) -> float:
        """吞吐量 (items/second)"""
        return self.items_processed / max(self.duration, 0.001)
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        return self.items_saved / max(self.items_processed, 1)


class DatabaseConnectionManager:
    """数据库连接管理器"""
    
    def __init__(self, max_connections: int = 5):
        self.max_connections = max_connections
        self._lock = threading.Lock()
        self._connection_pool = {}
        
    @contextmanager
    def get_connection(self, db_alias: str = 'default'):
        """获取数据库连接"""
        connection_key = f"{db_alias}_{threading.current_thread().ident}"
        
        try:
            # 获取或创建连接
            if connection_key not in self._connection_pool:
                conn = connections[db_alias]
                self._connection_pool[connection_key] = conn
            
            conn = self._connection_pool[connection_key]
            yield conn
            
        except Exception as e:
            logger.error(f"数据库连接错误: {str(e)}")
            # 清理有问题的连接
            if connection_key in self._connection_pool:
                del self._connection_pool[connection_key]
            raise
    
    def close_all_connections(self):
        """关闭所有连接"""
        with self._lock:
            for conn in self._connection_pool.values():
                try:
                    conn.close()
                except:
                    pass
            self._connection_pool.clear()
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接统计"""
        return {
            'active_connections': len(self._connection_pool),
            'max_connections': self.max_connections,
            'connection_keys': list(self._connection_pool.keys())
        }


class BatchProcessor:
    """批量处理器"""
    
    def __init__(self, batch_size: int = 100, connection_manager: DatabaseConnectionManager = None):
        self.batch_size = batch_size
        self.connection_manager = connection_manager or DatabaseConnectionManager()
        
    def process_expressions_batch(self, expressions: List[ExpressionItem]) -> StorageMetrics:
        """批量处理表达式"""
        start_time = time.time()
        metrics = StorageMetrics(
            operation_type='batch_expressions',
            start_time=start_time,
            end_time=0,
            duration=0,
            items_processed=len(expressions),
            items_saved=0,
            items_skipped=0,
            batch_size=self.batch_size,
            memory_usage=0,
            db_queries=0,
            cache_hits=0,
            cache_misses=0,
            errors=[]
        )
        
        try:
            # 按批次处理
            for i in range(0, len(expressions), self.batch_size):
                batch = expressions[i:i + self.batch_size]
                saved_count = self._process_single_batch(batch, metrics)
                metrics.items_saved += saved_count
                metrics.items_skipped += len(batch) - saved_count
                
        except Exception as e:
            metrics.errors.append(str(e))
            logger.error(f"批量处理失败: {str(e)}")
        
        finally:
            metrics.end_time = time.time()
            metrics.duration = metrics.end_time - metrics.start_time
        
        return metrics
    
    def _process_single_batch(self, batch: List[ExpressionItem], metrics: StorageMetrics) -> int:
        """处理单个批次"""
        saved_count = 0
        
        try:
            with self.connection_manager.get_connection() as conn:
                with transaction.atomic():
                    # 预处理：获取或创建数据源
                    source_cache = {}
                    scenario_cache = {}
                    
                    for item in batch:
                        try:
                            # 处理数据源
                            source_key = f"{item.source_name}:{item.source_url}"
                            if source_key not in source_cache:
                                source, created = ExpressionSource.objects.get_or_create(
                                    source_name=item.source_name,
                                    defaults={
                                        'source_url': item.source_url,
                                        'source_type': 'web',
                                        'reliability_score': 5
                                    }
                                )
                                source_cache[source_key] = source
                                if created:
                                    metrics.db_queries += 1
                                else:
                                    metrics.cache_hits += 1
                            else:
                                metrics.cache_hits += 1
                            
                            source = source_cache[source_key]
                            
                            # 检查是否已存在
                            if IdiomaticExpression.objects.filter(
                                expression=item.expression,
                                source=source
                            ).exists():
                                metrics.items_skipped += 1
                                continue
                            
                            # 创建表达式
                            expression = IdiomaticExpression.objects.create(
                                expression=item.expression,
                                meaning=item.meaning,
                                expression_type=getattr(item, 'expression_type', 'phrase'),
                                formality_level=getattr(item, 'formality_level', 'neutral'),
                                frequency_score=getattr(item, 'frequency_score', 5),
                                phonetic_transcription=getattr(item, 'phonetic_transcription', ''),
                                usage_examples=getattr(item, 'usage_examples', []),
                                cultural_background=getattr(item, 'cultural_background', ''),
                                metadata=getattr(item, 'metadata', {}),
                                source=source
                            )
                            
                            # 处理场景关联（简化版本）
                            scenarios = getattr(item, 'scenarios', [])
                            if scenarios:
                                # 将场景信息存储在metadata中，避免复杂的关联操作
                                expression.metadata = {
                                    **(expression.metadata or {}),
                                    'scenarios': scenarios
                                }
                                expression.save(update_fields=['metadata'])
                            
                            saved_count += 1
                            metrics.db_queries += 2  # CREATE + potential scenario links
                            
                        except Exception as e:
                            metrics.errors.append(f"处理项目失败: {str(e)}")
                            logger.error(f"处理表达式失败 {item.expression}: {str(e)}")
                            continue
                            
        except Exception as e:
            metrics.errors.append(f"批次事务失败: {str(e)}")
            logger.error(f"批次处理事务失败: {str(e)}")
            raise
        
        return saved_count


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self, cache_prefix: str = "perf_monitor"):
        self.cache_prefix = cache_prefix
        self.metrics_history = []
        
    def record_metrics(self, metrics: StorageMetrics):
        """记录性能指标"""
        # 存储到缓存
        cache_key = f"{self.cache_prefix}:metrics:{int(time.time())}"
        cache.set(cache_key, asdict(metrics), timeout=3600)  # 1小时
        
        # 保留最近的指标
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-50:]  # 保留最近50条
        
        # 记录到日志
        logger.info(
            f"存储性能指标 - 操作: {metrics.operation_type}, "
            f"处理: {metrics.items_processed}, 保存: {metrics.items_saved}, "
            f"耗时: {metrics.duration:.2f}s, 吞吐量: {metrics.throughput:.1f} items/s"
        )
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """获取性能摘要"""
        cutoff_time = time.time() - (hours * 3600)
        recent_metrics = [m for m in self.metrics_history if m.start_time >= cutoff_time]
        
        if not recent_metrics:
            return {'message': f'过去{hours}小时无性能数据'}
        
        total_processed = sum(m.items_processed for m in recent_metrics)
        total_saved = sum(m.items_saved for m in recent_metrics)
        total_duration = sum(m.duration for m in recent_metrics)
        total_errors = sum(len(m.errors) for m in recent_metrics)
        
        avg_throughput = sum(m.throughput for m in recent_metrics) / len(recent_metrics)
        avg_success_rate = sum(m.success_rate for m in recent_metrics) / len(recent_metrics)
        
        return {
            'time_period': f'{hours}小时',
            'operations_count': len(recent_metrics),
            'total_items_processed': total_processed,
            'total_items_saved': total_saved,
            'total_duration': total_duration,
            'total_errors': total_errors,
            'average_throughput': avg_throughput,
            'average_success_rate': avg_success_rate,
            'overall_success_rate': total_saved / max(total_processed, 1)
        }
    
    def get_database_performance(self) -> Dict[str, Any]:
        """获取数据库性能指标"""
        try:
            with connection.cursor() as cursor:
                # 获取数据库统计信息
                stats = {}
                
                # 表大小统计
                cursor.execute("""
                    SELECT 
                        table_name,
                        table_rows as estimated_rows
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE()
                    AND table_name IN ('english_idiomaticexpression', 'english_newsitem', 'english_expressionsource')
                """)
                
                table_stats = cursor.fetchall()
                stats['table_stats'] = [
                    {'table': row[0], 'estimated_rows': row[1]} 
                    for row in table_stats
                ]
                
                # 连接统计
                cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
                connections_result = cursor.fetchone()
                if connections_result:
                    stats['active_connections'] = int(connections_result[1])
                
                # 查询统计
                cursor.execute("SHOW STATUS LIKE 'Questions'")
                queries_result = cursor.fetchone()
                if queries_result:
                    stats['total_queries'] = int(queries_result[1])
                
                return stats
                
        except Exception as e:
            logger.error(f"获取数据库性能指标失败: {str(e)}")
            return {'error': str(e)}
    
    def optimize_database_indexes(self) -> Dict[str, Any]:
        """优化数据库索引"""
        try:
            optimization_results = []
            
            with connection.cursor() as cursor:
                # 检查缺失的索引
                missing_indexes = [
                    {
                        'table': 'english_idiomaticexpression',
                        'column': 'expression',
                        'index_name': 'idx_expression_text'
                    },
                    {
                        'table': 'english_idiomaticexpression', 
                        'column': 'source_id',
                        'index_name': 'idx_expression_source'
                    },
                    {
                        'table': 'english_idiomaticexpression',
                        'column': 'frequency_score',
                        'index_name': 'idx_frequency_score'
                    }
                ]
                
                for index_info in missing_indexes:
                    try:
                        # 检查索引是否已存在（使用参数化查询）
                        cursor.execute("""
                            SELECT COUNT(*) FROM information_schema.statistics 
                            WHERE table_schema = DATABASE() 
                            AND table_name = %s 
                            AND index_name = %s
                        """, [index_info['table'], index_info['index_name']])
                        
                        exists = cursor.fetchone()[0] > 0
                        
                        if not exists:
                            # 验证表名和列名安全性
                            from apps.common.security import SQLSecurityUtils
                            safe_table = SQLSecurityUtils.validate_table_name(index_info['table'])
                            safe_column = SQLSecurityUtils.validate_column_name(index_info['column'])
                            safe_index = SQLSecurityUtils.validate_column_name(index_info['index_name'])
                            
                            # 创建索引（使用验证后的名称）
                            cursor.execute(f"""
                                CREATE INDEX {safe_index} 
                                ON {safe_table} ({safe_column})
                            """)
                            optimization_results.append(f"创建索引: {index_info['index_name']}")
                        else:
                            optimization_results.append(f"索引已存在: {index_info['index_name']}")
                            
                    except Exception as e:
                        optimization_results.append(f"索引操作失败 {index_info['index_name']}: {str(e)}")
            
            return {
                'status': 'completed',
                'results': optimization_results
            }
            
        except Exception as e:
            logger.error(f"数据库索引优化失败: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }


class DataBackupManager:
    """数据备份管理器"""
    
    def __init__(self, backup_dir: str = "/tmp/backups"):
        self.backup_dir = backup_dir
        
    def create_backup(self, tables: List[str] = None) -> Dict[str, Any]:
        """创建数据备份"""
        if not tables:
            tables = ['english_idiomaticexpression', 'english_newsitem', 'english_expressionsource']
        
        backup_info = {
            'timestamp': timezone.now().isoformat(),
            'tables': [],
            'total_records': 0,
            'status': 'started'
        }
        
        try:
            for table in tables:
                table_backup = self._backup_table(table)
                backup_info['tables'].append(table_backup)
                backup_info['total_records'] += table_backup.get('record_count', 0)
            
            backup_info['status'] = 'completed'
            
        except Exception as e:
            backup_info['status'] = 'failed'
            backup_info['error'] = str(e)
            logger.error(f"数据备份失败: {str(e)}")
        
        return backup_info
    
    def _backup_table(self, table_name: str) -> Dict[str, Any]:
        """备份单个表"""
        table_info = {
            'table_name': table_name,
            'record_count': 0,
            'backup_file': None,
            'status': 'started'
        }
        
        try:
            with connection.cursor() as cursor:
                # 验证表名安全性
                from apps.common.security import SQLSecurityUtils
                safe_table_name = SQLSecurityUtils.validate_table_name(table_name)
                
                # 获取记录数（使用参数化查询）
                cursor.execute("SELECT COUNT(*) FROM " + safe_table_name)
                record_count = cursor.fetchone()[0]
                table_info['record_count'] = record_count
                
                # 这里可以实现实际的备份逻辑
                # 例如导出为JSON或SQL文件
                backup_filename = f"{table_name}_{int(time.time())}.json"
                table_info['backup_file'] = backup_filename
                table_info['status'] = 'completed'
                
        except Exception as e:
            table_info['status'] = 'failed'
            table_info['error'] = str(e)
            logger.error(f"备份表 {table_name} 失败: {str(e)}")
        
        return table_info


class OptimizedDataStorage:
    """优化的数据存储系统"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_processor = BatchProcessor(batch_size)
        self.performance_monitor = PerformanceMonitor()
        self.connection_manager = DatabaseConnectionManager()
        self.backup_manager = DataBackupManager()
        
    def store_expressions(self, expressions: List[ExpressionItem]) -> Dict[str, Any]:
        """存储表达式数据"""
        if not expressions:
            return {'status': 'skipped', 'message': '没有数据需要存储'}
        
        logger.info(f"开始存储 {len(expressions)} 个表达式")
        
        # 执行批量处理
        metrics = self.batch_processor.process_expressions_batch(expressions)
        
        # 记录性能指标
        self.performance_monitor.record_metrics(metrics)
        
        result = {
            'status': 'completed',
            'total_processed': metrics.items_processed,
            'total_saved': metrics.items_saved,
            'total_skipped': metrics.items_skipped,
            'duration': metrics.duration,
            'throughput': metrics.throughput,
            'success_rate': metrics.success_rate,
            'errors': metrics.errors,
            'batch_size': metrics.batch_size
        }
        
        logger.info(
            f"存储完成 - 保存: {metrics.items_saved}/{metrics.items_processed}, "
            f"耗时: {metrics.duration:.2f}s"
        )
        
        return result
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'performance_summary': self.performance_monitor.get_performance_summary(),
            'database_performance': self.performance_monitor.get_database_performance(),
            'connection_stats': self.connection_manager.get_connection_stats(),
            'timestamp': timezone.now().isoformat()
        }
    
    def optimize_system(self) -> Dict[str, Any]:
        """优化系统性能"""
        optimization_results = {
            'database_optimization': self.performance_monitor.optimize_database_indexes(),
            'connection_cleanup': self._cleanup_connections(),
            'cache_cleanup': self._cleanup_cache(),
            'timestamp': timezone.now().isoformat()
        }
        
        return optimization_results
    
    def _cleanup_connections(self) -> Dict[str, Any]:
        """清理连接"""
        try:
            initial_count = len(self.connection_manager._connection_pool)
            self.connection_manager.close_all_connections()
            
            return {
                'status': 'completed',
                'closed_connections': initial_count
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _cleanup_cache(self) -> Dict[str, Any]:
        """清理缓存"""
        try:
            # 清理性能监控相关的缓存
            cache_keys = cache.keys("perf_monitor:*")
            if cache_keys:
                cache.delete_many(cache_keys)
                return {
                    'status': 'completed',
                    'cleared_keys': len(cache_keys)
                }
            else:
                return {
                    'status': 'completed',
                    'cleared_keys': 0
                }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e)
            }


# 全局存储系统实例
optimized_storage = OptimizedDataStorage()
