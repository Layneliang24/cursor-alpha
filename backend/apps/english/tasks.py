from __future__ import annotations

from celery import shared_task


@shared_task
def crawl_english_news(source: str = 'bbc') -> dict:
    # 占位任务：后续接入实际抓取逻辑
    # 返回结构方便前端提示
    return {
        'ok': True,
        'source': source,
        'message': 'crawl scheduled'
    }


