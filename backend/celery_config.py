"""
Celery配置文件
用于异步任务处理和调度
"""

import os
from celery import Celery
from django.conf import settings

# 设置默认的Django settings模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 创建Celery实例
app = Celery('english_learning')

# 使用Django的settings配置Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现任务
app.autodiscover_tasks()

# Celery配置
app.conf.update(
    # 消息代理设置
    broker_url=getattr(settings, 'CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    result_backend=getattr(settings, 'CELERY_RESULT_BACKEND', 'redis://localhost:6379/1'),
    
    # 任务设置
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    
    # 任务执行设置
    task_always_eager=False,  # 在测试环境中可能需要设置为True
    task_eager_propagates=True,
    task_ignore_result=False,
    
    # 工作进程设置
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    
    # 任务路由
    task_routes={
        'apps.english.tasks.crawl_expressions_task': {'queue': 'expressions'},
        'apps.english.tasks.crawl_news_task': {'queue': 'news'},
        'apps.english.tasks.process_data_quality_task': {'queue': 'quality'},
        'apps.english.tasks.cleanup_task': {'queue': 'maintenance'},
    },
    
    # 队列设置
    task_default_queue='default',
    task_queues={
        'expressions': {
            'exchange': 'expressions',
            'exchange_type': 'direct',
            'routing_key': 'expressions',
        },
        'news': {
            'exchange': 'news', 
            'exchange_type': 'direct',
            'routing_key': 'news',
        },
        'quality': {
            'exchange': 'quality',
            'exchange_type': 'direct', 
            'routing_key': 'quality',
        },
        'maintenance': {
            'exchange': 'maintenance',
            'exchange_type': 'direct',
            'routing_key': 'maintenance',
        },
    },
    
    # 任务超时设置
    task_soft_time_limit=300,  # 5分钟软限制
    task_time_limit=600,       # 10分钟硬限制
    
    # 任务重试设置
    task_default_retry_delay=60,  # 1分钟重试延迟
    task_max_retries=3,
    
    # 监控设置
    worker_send_task_events=True,
    task_send_sent_event=True,
    
    # 定时任务设置
    beat_schedule={
        'crawl-expressions-daily': {
            'task': 'apps.english.tasks.scheduled_crawl_expressions',
            'schedule': 3600.0 * 24,  # 每天执行一次
            'options': {'queue': 'expressions'}
        },
        'crawl-news-hourly': {
            'task': 'apps.english.tasks.scheduled_crawl_news', 
            'schedule': 3600.0,  # 每小时执行一次
            'options': {'queue': 'news'}
        },
        'cleanup-old-data': {
            'task': 'apps.english.tasks.cleanup_old_data',
            'schedule': 3600.0 * 24 * 7,  # 每周执行一次
            'options': {'queue': 'maintenance'}
        },
    },
)


@app.task(bind=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')


# Celery信号处理
from celery.signals import task_prerun, task_postrun, task_failure, task_success

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """任务开始前的处理"""
    print(f'Task {task.name}[{task_id}] is about to start')

@task_postrun.connect  
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
    """任务完成后的处理"""
    print(f'Task {task.name}[{task_id}] finished with state: {state}')

@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    """任务成功处理"""
    print(f'Task {sender.name} succeeded with result: {result}')

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwargs):
    """任务失败处理"""
    print(f'Task {sender.name}[{task_id}] failed: {exception}')
