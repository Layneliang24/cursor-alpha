"""
Celery任务监控和管理系统
提供任务状态查询、监控和管理功能
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from celery import current_app
from celery.result import AsyncResult
from celery.events.state import State
from django.utils import timezone
from django.core.cache import cache
from django.db import models
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class TaskInfo:
    """任务信息数据类"""
    task_id: str
    name: str
    state: str
    args: List[Any]
    kwargs: Dict[str, Any]
    result: Any
    traceback: Optional[str]
    timestamp: float
    runtime: Optional[float]
    worker: Optional[str]
    queue: Optional[str]
    retries: int
    eta: Optional[str]
    expires: Optional[str]


@dataclass
class WorkerInfo:
    """工作进程信息数据类"""
    name: str
    status: str
    active_tasks: int
    processed_tasks: int
    load_avg: List[float]
    pool: Dict[str, Any]


@dataclass
class QueueInfo:
    """队列信息数据类"""
    name: str
    pending_tasks: int
    active_tasks: int
    failed_tasks: int
    success_tasks: int


class TaskMonitor:
    """任务监控器"""
    
    def __init__(self):
        self.app = current_app
        self.state = State()
        
    def get_task_info(self, task_id: str) -> Optional[TaskInfo]:
        """获取任务信息"""
        try:
            result = AsyncResult(task_id, app=self.app)
            
            # 获取任务详细信息
            task_info = TaskInfo(
                task_id=task_id,
                name=result.name or 'Unknown',
                state=result.state,
                args=getattr(result, 'args', []),
                kwargs=getattr(result, 'kwargs', {}),
                result=result.result,
                traceback=result.traceback,
                timestamp=getattr(result, 'timestamp', 0),
                runtime=getattr(result, 'runtime', None),
                worker=getattr(result, 'worker', None),
                queue=getattr(result, 'queue', None),
                retries=getattr(result, 'retries', 0),
                eta=getattr(result, 'eta', None),
                expires=getattr(result, 'expires', None)
            )
            
            return task_info
            
        except Exception as e:
            logger.error(f"获取任务信息失败 {task_id}: {str(e)}")
            return None
    
    def get_active_tasks(self) -> List[TaskInfo]:
        """获取活跃任务列表"""
        try:
            inspect = self.app.control.inspect()
            active_tasks = inspect.active()
            
            if not active_tasks:
                return []
            
            task_list = []
            for worker, tasks in active_tasks.items():
                for task in tasks:
                    task_info = TaskInfo(
                        task_id=task['id'],
                        name=task['name'],
                        state='ACTIVE',
                        args=task.get('args', []),
                        kwargs=task.get('kwargs', {}),
                        result=None,
                        traceback=None,
                        timestamp=task.get('time_start', 0),
                        runtime=None,
                        worker=worker,
                        queue=task.get('delivery_info', {}).get('routing_key'),
                        retries=task.get('retries', 0),
                        eta=task.get('eta'),
                        expires=task.get('expires')
                    )
                    task_list.append(task_info)
            
            return task_list
            
        except Exception as e:
            logger.error(f"获取活跃任务失败: {str(e)}")
            return []
    
    def get_scheduled_tasks(self) -> List[TaskInfo]:
        """获取计划任务列表"""
        try:
            inspect = self.app.control.inspect()
            scheduled_tasks = inspect.scheduled()
            
            if not scheduled_tasks:
                return []
            
            task_list = []
            for worker, tasks in scheduled_tasks.items():
                for task in tasks:
                    task_info = TaskInfo(
                        task_id=task['request']['id'],
                        name=task['request']['task'],
                        state='SCHEDULED',
                        args=task['request'].get('args', []),
                        kwargs=task['request'].get('kwargs', {}),
                        result=None,
                        traceback=None,
                        timestamp=0,
                        runtime=None,
                        worker=worker,
                        queue=task['request'].get('delivery_info', {}).get('routing_key'),
                        retries=task['request'].get('retries', 0),
                        eta=task.get('eta'),
                        expires=task.get('expires')
                    )
                    task_list.append(task_info)
            
            return task_list
            
        except Exception as e:
            logger.error(f"获取计划任务失败: {str(e)}")
            return []
    
    def get_failed_tasks(self, limit: int = 100) -> List[TaskInfo]:
        """获取失败任务列表"""
        try:
            # 从缓存中获取失败任务记录
            failed_tasks_key = "celery:failed_tasks"
            failed_task_ids = cache.get(failed_tasks_key, [])
            
            task_list = []
            for task_id in failed_task_ids[:limit]:
                task_info = self.get_task_info(task_id)
                if task_info and task_info.state in ['FAILURE', 'RETRY']:
                    task_list.append(task_info)
            
            return task_list
            
        except Exception as e:
            logger.error(f"获取失败任务失败: {str(e)}")
            return []
    
    def get_worker_stats(self) -> List[WorkerInfo]:
        """获取工作进程统计"""
        try:
            inspect = self.app.control.inspect()
            stats = inspect.stats()
            
            if not stats:
                return []
            
            worker_list = []
            for worker_name, worker_stats in stats.items():
                worker_info = WorkerInfo(
                    name=worker_name,
                    status='online',
                    active_tasks=worker_stats.get('total', {}).get('tasks.active', 0),
                    processed_tasks=worker_stats.get('total', {}).get('tasks.processed', 0),
                    load_avg=worker_stats.get('rusage', {}).get('load_avg', [0, 0, 0]),
                    pool=worker_stats.get('pool', {})
                )
                worker_list.append(worker_info)
            
            return worker_list
            
        except Exception as e:
            logger.error(f"获取工作进程统计失败: {str(e)}")
            return []
    
    def get_queue_stats(self) -> List[QueueInfo]:
        """获取队列统计"""
        try:
            # 这里需要根据实际的消息代理实现
            # Redis作为代理时的实现
            from django_celery_results.models import TaskResult
            
            queue_stats = {}
            
            # 从任务结果中统计
            recent_time = timezone.now() - timedelta(hours=24)
            recent_tasks = TaskResult.objects.filter(date_created__gte=recent_time)
            
            for task in recent_tasks:
                queue_name = getattr(task, 'task_kwargs', {}).get('queue', 'default')
                
                if queue_name not in queue_stats:
                    queue_stats[queue_name] = {
                        'pending': 0,
                        'active': 0,
                        'success': 0,
                        'failed': 0
                    }
                
                if task.status == 'PENDING':
                    queue_stats[queue_name]['pending'] += 1
                elif task.status == 'SUCCESS':
                    queue_stats[queue_name]['success'] += 1
                elif task.status == 'FAILURE':
                    queue_stats[queue_name]['failed'] += 1
                elif task.status in ['STARTED', 'RETRY']:
                    queue_stats[queue_name]['active'] += 1
            
            queue_list = []
            for queue_name, stats in queue_stats.items():
                queue_info = QueueInfo(
                    name=queue_name,
                    pending_tasks=stats['pending'],
                    active_tasks=stats['active'],
                    success_tasks=stats['success'],
                    failed_tasks=stats['failed']
                )
                queue_list.append(queue_info)
            
            return queue_list
            
        except Exception as e:
            logger.error(f"获取队列统计失败: {str(e)}")
            return []
    
    def revoke_task(self, task_id: str, terminate: bool = False) -> bool:
        """撤销任务"""
        try:
            self.app.control.revoke(task_id, terminate=terminate)
            logger.info(f"任务 {task_id} 已撤销 (terminate={terminate})")
            return True
        except Exception as e:
            logger.error(f"撤销任务失败 {task_id}: {str(e)}")
            return False
    
    def purge_queue(self, queue_name: str) -> int:
        """清空队列"""
        try:
            result = self.app.control.purge()
            logger.info(f"队列 {queue_name} 已清空")
            return result
        except Exception as e:
            logger.error(f"清空队列失败 {queue_name}: {str(e)}")
            return 0
    
    def get_task_history(self, task_name: str = None, limit: int = 100) -> List[TaskInfo]:
        """获取任务历史"""
        try:
            from django_celery_results.models import TaskResult
            
            query = TaskResult.objects.all()
            if task_name:
                query = query.filter(task_name=task_name)
            
            query = query.order_by('-date_created')[:limit]
            
            task_list = []
            for task_result in query:
                task_info = TaskInfo(
                    task_id=task_result.task_id,
                    name=task_result.task_name,
                    state=task_result.status,
                    args=task_result.task_args or [],
                    kwargs=task_result.task_kwargs or {},
                    result=task_result.result,
                    traceback=task_result.traceback,
                    timestamp=task_result.date_created.timestamp() if task_result.date_created else 0,
                    runtime=(task_result.date_done - task_result.date_created).total_seconds() 
                            if task_result.date_done and task_result.date_created else None,
                    worker=None,
                    queue=None,
                    retries=0,
                    eta=None,
                    expires=None
                )
                task_list.append(task_info)
            
            return task_list
            
        except Exception as e:
            logger.error(f"获取任务历史失败: {str(e)}")
            return []


class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.monitor = TaskMonitor()
    
    def submit_crawl_expressions_task(self, sources: List[str] = None, 
                                   max_items_per_source: int = 50,
                                   quality_threshold: float = 0.6,
                                   priority: int = 1) -> str:
        """提交爬取表达式任务"""
        from .tasks import crawl_expressions_task
        
        task = crawl_expressions_task.apply_async(
            args=[sources, max_items_per_source, quality_threshold],
            priority=priority,
            queue='expressions'
        )
        
        logger.info(f"提交爬取表达式任务: {task.id}")
        return task.id
    
    def submit_crawl_news_task(self, source: str = 'bbc',
                             crawler_type: str = 'traditional',
                             max_articles: int = 20,
                             priority: int = 1) -> str:
        """提交爬取新闻任务"""
        from .tasks import crawl_news_task
        
        task = crawl_news_task.apply_async(
            args=[source, crawler_type, max_articles],
            priority=priority,
            queue='news'
        )
        
        logger.info(f"提交爬取新闻任务: {task.id}")
        return task.id
    
    def submit_quality_processing_task(self, expression_ids: List[int] = None,
                                     quality_threshold: float = 0.6,
                                     priority: int = 0) -> str:
        """提交数据质量处理任务"""
        from .tasks import process_data_quality_task
        
        task = process_data_quality_task.apply_async(
            args=[expression_ids, quality_threshold],
            priority=priority,
            queue='quality'
        )
        
        logger.info(f"提交数据质量处理任务: {task.id}")
        return task.id
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取监控面板数据"""
        try:
            active_tasks = self.monitor.get_active_tasks()
            scheduled_tasks = self.monitor.get_scheduled_tasks()
            failed_tasks = self.monitor.get_failed_tasks(limit=10)
            worker_stats = self.monitor.get_worker_stats()
            queue_stats = self.monitor.get_queue_stats()
            
            # 统计数据
            stats = {
                'active_count': len(active_tasks),
                'scheduled_count': len(scheduled_tasks),
                'failed_count': len(failed_tasks),
                'worker_count': len(worker_stats),
                'queue_count': len(queue_stats)
            }
            
            # 按任务类型统计
            task_type_stats = {}
            for task in active_tasks + scheduled_tasks:
                task_type = task.name.split('.')[-1] if '.' in task.name else task.name
                task_type_stats[task_type] = task_type_stats.get(task_type, 0) + 1
            
            return {
                'stats': stats,
                'task_type_stats': task_type_stats,
                'active_tasks': [asdict(task) for task in active_tasks],
                'scheduled_tasks': [asdict(task) for task in scheduled_tasks],
                'failed_tasks': [asdict(task) for task in failed_tasks],
                'worker_stats': [asdict(worker) for worker in worker_stats],
                'queue_stats': [asdict(queue) for queue in queue_stats],
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取监控面板数据失败: {str(e)}")
            return {
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }


# 全局任务管理器实例
task_manager = TaskManager()
