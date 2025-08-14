from __future__ import annotations

from celery import shared_task


@shared_task
def crawl_english_news(source: str = 'bbc', crawler_type: str = 'traditional', max_articles: int = 10) -> dict:
    """
    抓取英语新闻的异步任务
    :param source: 新闻源 ('bbc', 'cnn', 'reuters', 'all')
    :param crawler_type: 爬虫类型 ('traditional', 'fundus', 'both')
    :return: 抓取结果
    """
    try:
        import logging
        from django.core.management import call_command
        from io import StringIO
        
        logger = logging.getLogger(__name__)
        logger.info(f"开始抓取 {source} 新闻 (使用 {crawler_type} 爬虫)")
        
        # 使用Django管理命令来抓取新闻
        out = StringIO()
        call_command(
            'crawl_news', 
            source=source, 
            crawler=crawler_type,
            max_articles=max_articles,
            verbosity=0,
            stdout=out
        )
        
        # 解析输出获取统计信息
        output = out.getvalue()
        total_found = 0
        saved_count = 0
        skipped_count = 0
        
        # 简单的输出解析
        if '抓取完成！共找到' in output:
            import re
            match = re.search(r'共找到 (\d+) 条新闻', output)
            if match:
                total_found = int(match.group(1))
        
        if '新增' in output and '条新闻' in output:
            import re
            match = re.search(r'新增 (\d+) 条新闻', output)
            if match:
                saved_count = int(match.group(1))
        
        skipped_count = max(total_found - saved_count, 0)
        
        logger.info(f"成功抓取并保存 {source} 新闻 {saved_count} 条")
        
        return {
            'ok': True,
            'source': source,
            'crawler': crawler_type,
            'message': f'成功抓取 {source} 新闻',
            'total_found': total_found,
            'saved_count': saved_count,
            'skipped_count': skipped_count
        }
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"抓取 {source} 新闻失败: {str(e)}")
        
        return {
            'ok': False,
            'source': source,
            'crawler': crawler_type,
            'message': f'抓取失败: {str(e)}',
            'error': str(e)
        }


