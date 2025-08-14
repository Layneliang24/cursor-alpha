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
        if publisher_id not in self.supported_publishers:
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
            
            return FundusNewsItem(
                title=title,
                content=content,
                url="",  # Fundus Article对象没有url属性
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
                if 'image' in article.meta:
                    image_url = article.meta['image']
                elif 'og:image' in article.meta:
                    image_url = article.meta['og:image']
                elif 'twitter:image' in article.meta:
                    image_url = article.meta['twitter:image']
        except:
            pass
        
        return image_url, image_alt
    
    def save_news_to_db(self, news_items: List[FundusNewsItem]) -> int:
        """保存新闻到数据库"""
        from .models import News
        
        saved_count = 0
        
        for item in news_items:
            try:
                # 检查是否已存在相同URL的新闻
                if News.objects.filter(source_url=item.url).exists():
                    logger.info(f"新闻已存在，跳过: {item.title[:50]}...")
                    continue
                
                # 确认内容长度
                word_count = len(item.content.split()) if item.content else 0
                if word_count < 50:
                    logger.warning(f"新闻内容太短({word_count}词)，跳过: {item.title[:50]}")
                    continue
                
                # 创建新闻记录
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
                    image_url=item.image_url,
                    image_alt=item.image_alt
                )
                
                saved_count += 1
                logger.info(f"保存Fundus新闻成功({word_count}词): {news.title[:50]}...")
                
            except Exception as e:
                logger.error(f"保存Fundus新闻失败 {item.title[:50]}: {str(e)}")
        
        logger.info(f"Fundus新闻保存完成，成功保存 {saved_count} 条")
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
