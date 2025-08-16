"""
Fundus新闻爬虫服务
集成Fundus框架，提供高质量的新闻爬取功能
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings

# Fundus imports
from fundus import PublisherCollection, Crawler

logger = logging.getLogger(__name__)


class FundusNewsItem:
    """Fundus新闻条目数据类，兼容现有NewsItem接口"""
    
    def __init__(self, title: str, content: str, url: str, source: str, 
                 published_at: Optional[datetime] = None, summary: str = '',
                 difficulty_level: str = 'intermediate', tags: List[str] = None,
                 image_url: str = '', image_alt: str = ''):
        self.title = title
        self.content = content
        self.url = url
        self.source = source
        # 避免Django设置依赖
        if published_at is None:
            from datetime import datetime
            self.published_at = datetime.now()
        else:
            self.published_at = published_at
        self.summary = summary
        self.difficulty_level = difficulty_level
        self.tags = tags or []
        self.image_url = image_url
        self.image_alt = image_alt


class FundusCrawlerService:
    """Fundus爬虫服务"""
    
    def __init__(self):
        self.publishers = PublisherCollection()
        # 延迟初始化crawler，避免在导入时出错
        self._crawler = None
        
        # 支持的新闻源配置
        self.supported_publishers = {
            'bbc': 'BBC',
            'cnn': 'CNN',
            'reuters': 'Reuters',
            'techcrunch': 'TechCrunch',
            'the_guardian': 'The Guardian',
            'the_new_york_times': 'The New York Times',
            'wired': 'Wired',
            'ars_technica': 'Ars Technica',
            'hacker_news': 'Hacker News',
            'stack_overflow': 'Stack Overflow Blog'
        }
        
        logger.info(f"Fundus爬虫服务初始化完成，支持 {len(self.supported_publishers)} 个新闻源")
    
    def get_available_publishers(self) -> List[str]:
        """获取可用的发布者列表"""
        available = []
        try:
            for pub_id, pub_name in self.supported_publishers.items():
                if self._get_publisher(pub_id):
                    available.append(pub_id)
        except Exception as e:
            logger.warning(f"获取可用发布者时出错: {e}")
            # 返回支持的发布者列表作为备选
            available = list(self.supported_publishers.keys())
        return available
    
    def _get_publisher(self, publisher_id: str):
        """获取发布者对象"""
        try:
            # 支持通用标识：country.PublisherName
            if '.' in publisher_id:
                country_key, publisher_name = publisher_id.split('.', 1)
                country_obj = getattr(self.publishers, country_key, None)
                if country_obj:
                    return getattr(country_obj, publisher_name, None)

            # 映射发布者ID到实际的Fundus发布者
            publisher_mapping = {
                'bbc': ('uk', 'BBC'),
                'cnn': ('us', 'CNN'),
                'reuters': ('us', 'Reuters'),
                'techcrunch': ('us', 'TechCrunch'),
                'the_guardian': ('uk', 'TheGuardian'),
                'the_new_york_times': ('us', 'NYTimes'),
                'wired': ('us', 'Wired'),
                'ars_technica': ('us', 'ArsTechnica'),
                'hacker_news': ('us', 'HackerNews'),
                'stack_overflow': ('us', 'StackOverflow')
            }
            
            if publisher_id in publisher_mapping:
                country, pub_name = publisher_mapping[publisher_id]
                country_obj = getattr(self.publishers, country, None)
                if country_obj:
                    return getattr(country_obj, pub_name, None)
            return None
        except Exception as e:
            logger.error(f"获取发布者 {publisher_id} 失败: {str(e)}")
            return None
    
    def crawl_publisher(self, publisher_id: str, max_articles: int = 10) -> List[FundusNewsItem]:
        """爬取指定发布者的新闻"""
        # 允许两类：1) 预设支持的发布者；2) 通用 country.PublisherName 标识
        if (publisher_id not in self.supported_publishers) and ('.' not in publisher_id):
            logger.error(f"不支持的发布者: {publisher_id}")
            return []
        
        try:
            logger.info(f"开始爬取 {publisher_id} 的新闻...")
            
            # 获取发布者
            publisher = self._get_publisher(publisher_id)
            if not publisher:
                logger.error(f"发布者 {publisher_id} 在Fundus中不可用")
                return []
            
            # 创建爬虫
            crawler = Crawler(publisher)
            
            # 爬取文章
            articles = []
            for article in crawler.crawl(max_articles=max_articles):
                try:
                    fundus_item = self._convert_fundus_article(article, publisher_id)
                    if fundus_item:
                        articles.append(fundus_item)
                        logger.info(f"成功解析 {publisher_id} 文章: {fundus_item.title[:50]}...")
                except Exception as e:
                    logger.error(f"转换文章失败: {str(e)}")
                    continue
            
            logger.info(f"{publisher_id} 爬取完成，共获取 {len(articles)} 条新闻")
            return articles
            
        except Exception as e:
            logger.error(f"爬取 {publisher_id} 失败: {str(e)}")
            return []

    def list_all_publishers(self) -> List[dict]:
        """列出Fundus中经过测试验证的可用发布者
        返回: [{ id, label, country, name }]
        """
        publishers: List[dict] = []
        try:
            # 导入经过测试验证的发布者列表
            try:
                import os
                import sys
                # 获取当前文件所在目录的上级目录（backend目录）
                backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                sys.path.insert(0, backend_dir)
                from available_publishers import AVAILABLE_PUBLISHERS
                tested_publishers = AVAILABLE_PUBLISHERS
            except ImportError:
                # 如果配置文件不存在，回退到原来的方法
                logger.warning("未找到测试验证的发布者配置文件，使用原始方法")
                tested_publishers = []
                for country_key in dir(self.publishers):
                    if country_key.startswith('_'):
                        continue
                    try:
                        country_obj = getattr(self.publishers, country_key)
                        for pub_name in dir(country_obj):
                            if pub_name.startswith('_'):
                                continue
                            try:
                                pub_obj = getattr(country_obj, pub_name)
                                if hasattr(pub_obj, 'name'):
                                    pub_id = f"{country_key}.{pub_name}"
                                    tested_publishers.append(pub_id)
                            except Exception:
                                continue
                    except Exception:
                        continue
            
            # 只返回经过测试验证的发布者
            for pub_id in tested_publishers:
                try:
                    country_key, pub_name = pub_id.split('.', 1)
                    label = f"{pub_name} ({country_key.upper()})"
                    publishers.append({
                        "id": pub_id,
                        "label": label,
                        "country": country_key,
                        "name": pub_name,
                    })
                except Exception:
                    continue
                    
        except Exception as e:
            logger.warning(f"枚举Fundus发布者失败: {e}")
        
        # 将预设支持的发布者置顶
        preferred_ids = set(self.supported_publishers.keys())
        def sort_key(item):
            # 预设的优先，其他按国家+名称排序
            return (0 if item["id"] in preferred_ids else 1, item["country"], item["name"])
        publishers.sort(key=sort_key)
        return publishers
    
    def crawl_all_supported(self, max_articles_per_publisher: int = 5) -> List[FundusNewsItem]:
        """爬取所有支持的发布者"""
        all_articles = []
        available_publishers = self.get_available_publishers()
        
        logger.info(f"开始爬取所有支持的发布者，共 {len(available_publishers)} 个")
        
        for publisher_id in available_publishers:
            try:
                articles = self.crawl_publisher(publisher_id, max_articles_per_publisher)
                all_articles.extend(articles)
                logger.info(f"{publisher_id} 爬取完成: {len(articles)} 条新闻")
            except Exception as e:
                logger.error(f"爬取 {publisher_id} 失败: {str(e)}")
                continue
        
        # 按发布时间排序
        all_articles.sort(key=lambda x: x.published_at, reverse=True)
        
        logger.info(f"所有发布者爬取完成，共获取 {len(all_articles)} 条新闻")
        return all_articles
    
    def _convert_fundus_article(self, article, publisher_id: str) -> Optional[FundusNewsItem]:
        """转换Fundus文章为项目格式"""
        try:
            # 提取基本信息
            title = article.title if article.title else "Untitled"
            content = str(article.body) if article.body else ""
            
            # 检查内容质量
            if not content or len(content.split()) < 50:
                logger.warning(f"文章内容太短，跳过: {title[:50]}")
                return None
            
            # 提取发布时间
            published_at = datetime.now()
            if article.publishing_date:
                try:
                    published_at = article.publishing_date
                    if published_at.tzinfo is None:
                        published_at = published_at.replace(tzinfo=timezone.utc)
                except:
                    published_at = datetime.now()
            
            # 提取摘要
            summary = self._extract_summary(content)
            
            # 判断难度等级
            difficulty_level = self._determine_difficulty(content)
            
            # 提取标签
            tags = self._extract_tags(content, publisher_id)
            
            # 提取图片信息
            image_url, image_alt = self._extract_image_info(article)
            
            # 尝试从article对象获取URL
            url = ""
            try:
                if hasattr(article, 'url') and article.url:
                    url = article.url
                elif hasattr(article, 'meta') and article.meta:
                    # 从meta中获取URL
                    if 'url' in article.meta:
                        url = article.meta['url']
                    elif 'og:url' in article.meta:
                        url = article.meta['og:url']
                    elif 'link' in article.meta:
                        url = article.meta['link']
            except:
                pass
            
            # 如果还是没有URL，使用标题生成一个唯一标识
            if not url:
                import hashlib
                url = f"fundus_{publisher_id}_{hashlib.md5(title.encode()).hexdigest()[:16]}"
            
            return FundusNewsItem(
                title=title,
                content=content,
                url=url,
                source=self.supported_publishers.get(publisher_id, publisher_id),
                published_at=published_at,
                summary=summary,
                difficulty_level=difficulty_level,
                tags=tags,
                image_url=image_url,
                image_alt=image_alt
            )
            
        except Exception as e:
            logger.error(f"转换Fundus文章失败: {str(e)}")
            return None
    
    def _extract_summary(self, content: str, max_length: int = 200) -> str:
        """提取文章摘要"""
        if not content:
            return ""
        
        import re
        sentences = re.split(r'[.!?]+', content)
        summary = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(summary + sentence) <= max_length:
                summary += sentence + ". "
            else:
                break
        
        return summary.strip()
    
    def _determine_difficulty(self, content: str) -> str:
        """根据内容判断难度等级"""
        if not content:
            return 'intermediate'
        
        import re
        word_count = len(content.split())
        complex_words = len(re.findall(r'\b\w{8,}\b', content))
        complex_ratio = complex_words / max(word_count, 1)
        
        sentences = re.split(r'[.!?]+', content)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)
        
        if complex_ratio < 0.15 and word_count < 400 and avg_sentence_length < 15:
            return 'beginner'
        elif complex_ratio > 0.3 or word_count > 1000 or avg_sentence_length > 25:
            return 'advanced'
        else:
            return 'intermediate'
    
    def _extract_tags(self, content: str, source: str) -> List[str]:
        """从内容中提取标签"""
        import re
        tags = ['news', 'english', source.lower()]
        
        keywords = {
            'technology': ['technology', 'tech', 'digital', 'ai', 'artificial intelligence', 'computer', 'internet', 'software', 'data'],
            'business': ['business', 'economy', 'market', 'finance', 'company', 'trade', 'investment', 'economic'],
            'health': ['health', 'medical', 'doctor', 'hospital', 'medicine', 'disease', 'healthcare', 'patient'],
            'science': ['science', 'research', 'study', 'scientist', 'discovery', 'experiment', 'scientific'],
            'politics': ['politics', 'government', 'minister', 'parliament', 'election', 'political', 'policy'],
            'environment': ['environment', 'climate', 'green', 'pollution', 'carbon', 'environmental', 'energy'],
            'world': ['world', 'international', 'global', 'country', 'nation', 'foreign'],
            'breaking': ['breaking', 'urgent', 'alert', 'latest', 'developing']
        }
        
        content_lower = content.lower()
        for category, words in keywords.items():
            if any(word in content_lower for word in words):
                tags.append(category)
        
        return tags[:8]
    
    def _extract_image_info(self, article) -> tuple:
        """提取图片信息"""
        image_url = ""
        image_alt = ""
        
        try:
            # 尝试从文章元数据中提取图片
            if hasattr(article, 'meta') and article.meta:
                # 优先使用Open Graph图片
                if 'og:image' in article.meta:
                    image_url = article.meta['og:image']
                    image_alt = article.meta.get('og:image:alt', '')
                elif 'twitter:image' in article.meta:
                    image_url = article.meta['twitter:image']
                    image_alt = article.meta.get('twitter:image:alt', '')
                elif 'image' in article.meta:
                    image_url = article.meta['image']
                
                # 验证图片URL的有效性
                if image_url and not image_url.startswith('http'):
                    # 如果是相对路径，尝试构建完整URL
                    if hasattr(article, 'url') and article.url:
                        from urllib.parse import urljoin, urlparse
                        parsed_url = urlparse(article.url)
                        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                        image_url = urljoin(base_url, image_url)
                    else:
                        image_url = ""
                        
        except Exception as e:
            logger.warning(f"图片信息提取失败: {str(e)}")
            image_url = ""
            image_alt = ""
        
        return image_url, image_alt
    
    def _download_and_save_image(self, image_url: str, news_title: str) -> str:
        """下载并保存图片到本地"""
        if not image_url:
            return ""
        
        try:
            import os
            import requests
            from django.conf import settings
            from urllib.parse import urlparse
            import hashlib
            
            # 创建图片保存目录
            image_dir = os.path.join(settings.MEDIA_ROOT, 'news_images')
            os.makedirs(image_dir, exist_ok=True)
            
            # 生成文件名
            parsed_url = urlparse(image_url)
            file_extension = os.path.splitext(parsed_url.path)[1] or '.jpg'
            if not file_extension.startswith('.'):
                file_extension = '.' + file_extension
            
            # 使用标题和URL的哈希值生成唯一文件名
            title_hash = hashlib.md5(news_title.encode()).hexdigest()[:8]
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
            filename = f"{title_hash}_{url_hash}{file_extension}"
            filepath = os.path.join(image_dir, filename)
            
            # 如果文件已存在，直接返回路径
            if os.path.exists(filepath):
                return f'news_images/{filename}'
            
            # 下载图片
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"图片下载成功: {filename}")
            return f'news_images/{filename}'
            
        except Exception as e:
            logger.warning(f"图片下载失败 {image_url}: {str(e)}")
            return ""
    
    def save_news_to_db(self, news_items: List[FundusNewsItem]) -> int:
        """保存新闻到数据库（覆盖式）：
        - 若URL不存在：创建
        - 若URL已存在：覆盖更新（标题、正文、摘要、难度、词数、图片等）
        """
        from .models import News

        saved_count = 0

        for item in news_items:
            try:
                # 删除字数限制，只要内容不为空就保存
                word_count = len(item.content.split()) if item.content else 0
                if not item.content or word_count == 0:
                    logger.warning(f"新闻内容为空，跳过: {item.title[:50]}")
                    continue

                # 统一处理图片：尝试下载到本地；失败则保留原外链
                new_local_image_path = self._download_and_save_image(item.image_url, item.title) if item.image_url else ""
                image_alt = item.image_alt[:200] if item.image_alt else ""

                # 查找是否已存在相同URL
                existing = News.objects.filter(source_url=item.url).first()
                if existing:
                    # 覆盖更新
                    # 如果需要替换为本地图片，清理旧本地文件
                    try:
                        if new_local_image_path:
                            if existing.image_url and existing.image_url.startswith('news_images/') and existing.image_url != new_local_image_path:
                                import os
                                from django.conf import settings
                                old_path = os.path.join(settings.MEDIA_ROOT, existing.image_url)
                                if os.path.exists(old_path):
                                    os.remove(old_path)
                            existing.image_url = new_local_image_path
                        elif item.image_url:
                            # 没有成功下载，但有外链，则记录外链
                            existing.image_url = item.image_url
                    except Exception as _img_err:
                        logger.warning(f"更新图片时出错: {_img_err}")

                    existing.title = item.title or existing.title
                    existing.content = item.content or existing.content
                    existing.summary = item.summary or existing.summary
                    existing.difficulty_level = item.difficulty_level or existing.difficulty_level
                    existing.word_count = word_count
                    existing.reading_time_minutes = max(1, word_count // 200)
                    existing.key_vocabulary = ', '.join(item.tags[:5]) if item.tags else existing.key_vocabulary
                    existing.comprehension_questions = self._generate_comprehension_questions(item.content)
                    existing.image_alt = image_alt or existing.image_alt
                    if item.published_at:
                        try:
                            existing.publish_date = item.published_at.date()
                        except Exception:
                            pass
                    # 规范source（保持已有值或覆盖为更规范）
                    existing.source = item.source or existing.source
                    existing.save(update_fields=[
                        'title', 'content', 'summary', 'difficulty_level', 'word_count',
                        'reading_time_minutes', 'key_vocabulary', 'comprehension_questions',
                        'image_url', 'image_alt', 'publish_date', 'source'
                    ])
                    saved_count += 1
                    logger.info(f"更新Fundus新闻成功({word_count}词): {existing.title[:50]}...")
                    continue

                # 不存在则创建
                news = News.objects.create(
                    title=item.title,
                    content=item.content,
                    source_url=item.url,
                    source=item.source,
                    publish_date=item.published_at.date() if item.published_at else timezone.now().date(),
                    summary=item.summary,
                    difficulty_level=item.difficulty_level,
                    word_count=word_count,
                    reading_time_minutes=max(1, word_count // 200),
                    key_vocabulary=', '.join(item.tags[:5]) if item.tags else '',
                    comprehension_questions=self._generate_comprehension_questions(item.content),
                    image_url=new_local_image_path if new_local_image_path else item.image_url,
                    image_alt=image_alt
                )

                saved_count += 1
                logger.info(f"保存Fundus新闻成功({word_count}词): {news.title[:50]}...")

            except Exception as e:
                logger.error(f"保存/更新Fundus新闻失败 {item.title[:50]}: {str(e)}")

        logger.info(f"Fundus新闻保存完成，保存/更新 {saved_count} 条")
        return saved_count
    
    def _generate_comprehension_questions(self, content: str) -> list:
        """生成理解问题"""
        if not content or len(content) < 150:
            return [
                "What is the main topic of this article?",
                "What are the key points mentioned?"
            ]
        
        questions = [
            "What is the main topic discussed in this article?",
            "Who are the key people or organizations mentioned?",
            "What are the main facts or events described?",
            "What might be the implications of the events described?"
        ]
        
        word_count = len(content.split())
        if word_count > 400:
            questions.append("What evidence or examples are provided to support the main points?")
        if word_count > 600:
            questions.append("How might this news affect different stakeholders?")
        
        return questions[:5]


# 全局Fundus服务实例 - 延迟初始化
fundus_crawler_service = None

def get_fundus_service():
    """获取Fundus服务实例"""
    global fundus_crawler_service
    if fundus_crawler_service is None:
        fundus_crawler_service = FundusCrawlerService()
    return fundus_crawler_service
