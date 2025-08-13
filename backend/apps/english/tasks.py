from __future__ import annotations

from celery import shared_task


@shared_task
def crawl_english_news(source: str = 'bbc') -> dict:
    """
    抓取英语新闻的异步任务
    :param source: 新闻源 ('bbc', 'cnn', 'reuters', 'all')
    :return: 抓取结果
    """
    try:
        from .news_crawler import real_news_crawler_service
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"开始抓取 {source} 新闻")
        
        # 抓取真实新闻
        if source == 'all':
            news_items = real_news_crawler_service.crawl_all_sources()
        else:
            news_items = real_news_crawler_service.crawl_news(source)
        
        if not news_items:
            logger.warning(f"未抓取到任何 {source} 真实新闻")
            return {
                'ok': False,
                'source': source,
                'message': f'未抓取到任何 {source} 真实新闻',
                'count': 0
            }
        
        # 保存到数据库
        saved_count = real_news_crawler_service.save_news_to_db(news_items)
        
        logger.info(f"成功抓取并保存 {source} 新闻 {saved_count} 条")
        
        return {
            'ok': True,
            'source': source,
            'message': f'成功抓取 {source} 新闻',
            'total_found': len(news_items),
            'saved_count': saved_count,
            'skipped_count': len(news_items) - saved_count
        }
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"抓取 {source} 新闻失败: {str(e)}")
        
        return {
            'ok': False,
            'source': source,
            'message': f'抓取失败: {str(e)}',
            'error': str(e)
        }


