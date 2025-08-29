"""
专业地道表达爬虫实现
包含Cambridge、Collins、Reddit、UrbanDictionary等专业爬虫类
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from django.utils import timezone
import urllib.parse

from .expression_crawler import (
    BaseExpressionCrawler, 
    DictionaryCrawler, 
    ExpressionItem
)

logger = logging.getLogger(__name__)


class CambridgeCrawler(DictionaryCrawler):
    """剑桥词典爬虫 - 采集地道表达和例句"""
    
    def __init__(self):
        search_patterns = [
            "https://dictionary.cambridge.org/dictionary/english/{term}",
            "https://dictionary.cambridge.org/search/english/direct/?q={term}"
        ]
        super().__init__('Cambridge Dictionary', 'https://dictionary.cambridge.org', search_patterns)
        
        # 剑桥词典特定的选择器
        self.expression_selectors = [
            '.headword', '.di-title', '.hw', 'h1.dhw'
        ]
        self.meaning_selectors = [
            '.def', '.ddef_d', '.definition', '.sense-body .def'
        ]
        self.example_selectors = [
            '.eg', '.examp', '.example', '.sense-body .eg'
        ]
        
        # 增强请求头以适应剑桥词典
        self.session.headers.update({
            'Referer': 'https://dictionary.cambridge.org/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
    
    def _get_selector_combinations(self) -> List[Dict[str, str]]:
        """获取剑桥词典特定的选择器组合"""
        return [
            # 剑桥词典主要结构
            {
                'expression': '.headword, .di-title, .hw',
                'meaning': '.def, .ddef_d',
                'example': '.eg, .examp'
            },
            # 短语和习语页面
            {
                'expression': 'h1.dhw, .phrase-title',
                'meaning': '.sense-body .def, .phrase-body .def',
                'example': '.sense-body .eg, .phrase-body .eg'
            },
            # 搜索结果页面
            {
                'expression': '.result .headword, .entry-title',
                'meaning': '.result .def, .def-text',
                'example': '.result .eg, .example-text'
            }
        ]
    
    def extract_phonetic_transcription(self, soup: BeautifulSoup, expression: str) -> str:
        """提取剑桥词典的音标"""
        phonetic_selectors = [
            '.pron .ipa', '.us .pron .ipa', '.uk .pron .ipa',
            '.dpron .ipa', '.sound .ipa', '.ipa'  # 添加直接的.ipa选择器
        ]
        
        for selector in phonetic_selectors:
            elem = soup.select_one(selector)
            if elem:
                # 对于音标，不使用clean_text，直接获取原始文本
                phonetic = elem.get_text().strip()
                if phonetic and ('/' in phonetic or '[' in phonetic):
                    return phonetic
        
        return ""
    
    def _extract_additional_metadata(self, soup: BeautifulSoup, expression: str) -> Dict[str, Any]:
        """提取剑桥词典的额外元数据"""
        metadata = {}
        
        # 提取词性标记
        pos_elem = soup.select_one('.pos, .part-of-speech')
        if pos_elem:
            metadata['part_of_speech'] = self.clean_text(pos_elem.get_text())
        
        # 提取使用频率标记
        freq_elem = soup.select_one('.freq, .frequency')
        if freq_elem:
            metadata['frequency_info'] = self.clean_text(freq_elem.get_text())
        
        # 提取语域标记（正式/非正式）
        register_elem = soup.select_one('.register, .usage')
        if register_elem:
            metadata['register'] = self.clean_text(register_elem.get_text())
        
        return metadata
    
    def _create_expression_item(self, data: Dict[str, Any], source_url: str) -> Optional[ExpressionItem]:
        """创建剑桥词典的表达式项目"""
        try:
            expression = self.clean_expression_text(data.get('expression', ''))
            meaning = self.clean_text(data.get('meaning', ''))
            
            if not expression or not meaning:
                return None
            
            examples = data.get('examples', [])
            metadata = data.get('metadata', {})
            
            # 从元数据中提取正式程度
            formality_level = 'neutral'
            if 'register' in metadata:
                register = metadata['register'].lower()
                if 'informal' in register:  # 先检查informal
                    formality_level = 'informal'
                elif 'formal' in register:
                    formality_level = 'formal'
            
            return ExpressionItem(
                expression=expression,
                meaning=meaning,
                source_url=source_url,
                source_name=self.source_name,
                expression_type=self.determine_expression_type(expression, meaning),
                formality_level=formality_level,
                frequency_score=self._calculate_cambridge_frequency(metadata),
                phonetic_transcription=data.get('phonetic', ''),
                usage_examples=examples,
                scenarios=self.extract_scenarios(examples, meaning),
                difficulty_level=self.determine_difficulty(f"{expression} {meaning}"),
                cultural_background='英式英语词典权威来源',
                metadata={
                    'extraction_method': 'cambridge_dictionary',
                    'cambridge_metadata': metadata,
                    'extraction_timestamp': timezone.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"创建剑桥表达式项目失败: {str(e)}")
            return None
    
    def _calculate_cambridge_frequency(self, metadata: Dict[str, Any]) -> int:
        """根据剑桥词典的频率信息计算评分"""
        if 'frequency_info' in metadata:
            freq_info = metadata['frequency_info'].lower()
            if 'common' in freq_info or 'frequent' in freq_info:
                return 8
            elif 'rare' in freq_info or 'uncommon' in freq_info:
                return 3
        
        return 6  # 默认中等频率


class CollinsCrawler(DictionaryCrawler):
    """柯林斯词典爬虫 - 获取短语和用法"""
    
    def __init__(self):
        search_patterns = [
            "https://www.collinsdictionary.com/dictionary/english/{term}",
            "https://www.collinsdictionary.com/search/?dictCode=english&q={term}"
        ]
        super().__init__('Collins Dictionary', 'https://www.collinsdictionary.com', search_patterns)
        
        # 柯林斯词典特定选择器
        self.session.headers.update({
            'Referer': 'https://www.collinsdictionary.com/',
        })
    
    def _get_selector_combinations(self) -> List[Dict[str, str]]:
        """获取柯林斯词典特定的选择器组合"""
        return [
            # 柯林斯主要结构
            {
                'expression': '.orth, .headword, h1.h2_entry',
                'meaning': '.def, .definition',
                'example': '.quote, .cit, .example'
            },
            # 短语部分
            {
                'expression': '.phrase .orth, .phrase-head',
                'meaning': '.phrase .def, .phrase-definition',
                'example': '.phrase .quote, .phrase-example'
            },
            # 搜索结果
            {
                'expression': '.result-title, .search-result .orth',
                'meaning': '.result-def, .search-result .def',
                'example': '.result-example, .search-result .quote'
            }
        ]
    
    def _extract_collins_rating(self, soup: BeautifulSoup) -> int:
        """提取柯林斯词典的星级评分"""
        star_elem = soup.select_one('.stars, .frequency-band')
        if star_elem:
            stars_text = star_elem.get_text()
            star_count = stars_text.count('★') or stars_text.count('*')
            return min(star_count * 2, 10)  # 转换为1-10评分
        return 5


class RedditCrawler(BaseExpressionCrawler):
    """Reddit爬虫 - 抓取英语学习社区的真实对话"""
    
    def __init__(self):
        super().__init__('Reddit English Learning')
        
        # Reddit API配置
        self.base_url = 'https://www.reddit.com'
        self.subreddits = [
            'EnglishLearning',
            'grammar', 
            'LearnEnglish',
            'EnglishTips',
            'idioms'
        ]
        
        # Reddit特定请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # 启用JavaScript渲染
        self.use_js_rendering = False  # Reddit可以通过普通HTTP访问
    
    def crawl_expressions(self, limit: int = 50) -> List[ExpressionItem]:
        """抓取Reddit的地道表达讨论"""
        expressions = []
        
        for subreddit in self.subreddits:
            try:
                subreddit_expressions = self._crawl_subreddit(subreddit, limit // len(self.subreddits))
                expressions.extend(subreddit_expressions)
                
                if len(expressions) >= limit:
                    break
                    
                # 避免请求过于频繁
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"抓取Reddit子版块 {subreddit} 失败: {str(e)}")
                continue
        
        logger.info(f"Reddit爬虫完成，获取 {len(expressions)} 个表达式")
        return expressions[:limit]
    
    def _crawl_subreddit(self, subreddit: str, limit: int) -> List[ExpressionItem]:
        """抓取特定子版块的内容"""
        expressions = []
        
        # 使用Reddit的JSON API
        url = f"{self.base_url}/r/{subreddit}/hot.json?limit={min(limit*2, 25)}"
        
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            posts = data['data']['children']
            
            for post_data in posts:
                post = post_data['data']
                
                # 过滤相关的帖子
                if self._is_expression_related(post['title'], post.get('selftext', '')):
                    expression_items = self._extract_expressions_from_post(post)
                    expressions.extend(expression_items)
                    
                    if len(expressions) >= limit:
                        break
            
        except Exception as e:
            logger.error(f"抓取子版块 {subreddit} 失败: {str(e)}")
        
        return expressions
    
    def _is_expression_related(self, title: str, content: str) -> bool:
        """判断帖子是否与地道表达相关"""
        text = f"{title} {content}".lower()
        
        keywords = [
            'idiom', 'phrase', 'expression', 'saying', 'slang',
            'what does', 'how to say', 'meaning of', 'native speaker',
            'colloquial', 'informal', 'formal', 'usage'
        ]
        
        return any(keyword in text for keyword in keywords)
    
    def _extract_expressions_from_post(self, post: Dict[str, Any]) -> List[ExpressionItem]:
        """从Reddit帖子中提取表达式"""
        expressions = []
        
        title = post['title']
        content = post.get('selftext', '')
        url = f"https://reddit.com{post['permalink']}"
        
        # 使用正则表达式查找引号中的表达式
        quoted_expressions = re.findall(r'"([^"]{3,50})"', f"{title} {content}")
        quoted_expressions.extend(re.findall(r"'([^']{3,50})'", f"{title} {content}"))
        
        for expr in quoted_expressions:
            expr = expr.strip()
            if len(expr.split()) >= 2 and len(expr.split()) <= 10:
                # 尝试从上下文中提取含义
                meaning = self._extract_meaning_from_context(expr, title, content)
                
                if meaning:
                    expression_item = ExpressionItem(
                        expression=expr,
                        meaning=meaning,
                        source_url=url,
                        source_name=self.source_name,
                        expression_type=self.determine_expression_type(expr),
                        formality_level='informal',  # Reddit通常比较非正式
                        frequency_score=self._calculate_reddit_frequency(post),
                        usage_examples=[self._create_usage_example(expr, title, content)],
                        scenarios=['casual', 'social'],
                        difficulty_level=self.determine_difficulty(f"{expr} {meaning}"),
                        cultural_background='Reddit英语学习社区讨论',
                        metadata={
                            'extraction_method': 'reddit_discussion',
                            'subreddit': post.get('subreddit', ''),
                            'score': post.get('score', 0),
                            'num_comments': post.get('num_comments', 0),
                            'extraction_timestamp': timezone.now().isoformat()
                        }
                    )
                    expressions.append(expression_item)
        
        return expressions
    
    def _extract_meaning_from_context(self, expression: str, title: str, content: str) -> str:
        """从上下文中提取表达式含义"""
        text = f"{title} {content}".lower()
        expr_lower = expression.lower()
        
        # 查找常见的解释模式
        patterns = [
            rf"{re.escape(expr_lower)}\s+means?\s+([^.!?]+)",
            rf"{re.escape(expr_lower)}\s+is\s+([^.!?]+)",
            rf"means?\s+([^.!?]+)\s*[.!?].*{re.escape(expr_lower)}",
            rf"it means\s+([^.!?]+)",
            rf"that means\s+([^.!?]+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                meaning = match.group(1).strip()
                if len(meaning) > 10 and len(meaning) < 200:
                    return meaning
        
        # 如果没有找到明确的解释，返回简单描述
        return f"English expression discussed in Reddit community"
    
    def _create_usage_example(self, expression: str, title: str, content: str) -> str:
        """创建使用示例"""
        # 尝试从标题或内容中找到包含表达式的句子
        text = f"{title}. {content}"
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            if expression.lower() in sentence.lower():
                clean_sentence = self.clean_text(sentence)
                if len(clean_sentence) > 10 and len(clean_sentence) < 150:
                    return clean_sentence
        
        return f'Example usage of "{expression}" from Reddit discussion.'
    
    def _calculate_reddit_frequency(self, post: Dict[str, Any]) -> int:
        """根据Reddit帖子的受欢迎程度计算频率评分"""
        score = post.get('score', 0)
        comments = post.get('num_comments', 0)
        
        # 基于点赞数和评论数计算
        popularity = score + comments * 2
        
        if popularity > 100:
            return 8
        elif popularity > 50:
            return 7
        elif popularity > 20:
            return 6
        elif popularity > 5:
            return 5
        else:
            return 4


class UrbanDictionaryCrawler(BaseExpressionCrawler):
    """Urban Dictionary爬虫 - 采集俚语表达"""
    
    def __init__(self):
        super().__init__('Urban Dictionary')
        self.base_url = 'https://www.urbandictionary.com'
        
        # Urban Dictionary特定配置
        self.session.headers.update({
            'Referer': 'https://www.urbandictionary.com/',
        })
    
    def crawl_expressions(self, limit: int = 50) -> List[ExpressionItem]:
        """抓取Urban Dictionary的俚语表达"""
        expressions = []
        
        # 常见俚语关键词
        slang_terms = [
            'cool', 'awesome', 'sick', 'dope', 'lit', 'fire',
            'salty', 'basic', 'extra', 'flex', 'vibe', 'mood',
            'ghosting', 'sliding', 'lowkey', 'highkey', 'stan',
            'periodt', 'cap', 'no cap', 'bet', 'facts'
        ]
        
        for term in slang_terms[:limit//3]:
            try:
                term_expressions = self._search_urban_term(term)
                expressions.extend(term_expressions)
                
                if len(expressions) >= limit:
                    break
                    
                # 避免请求过于频繁
                time.sleep(random.uniform(2, 3))
                
            except Exception as e:
                logger.error(f"搜索Urban Dictionary术语 '{term}' 失败: {str(e)}")
                continue
        
        logger.info(f"Urban Dictionary爬虫完成，获取 {len(expressions)} 个俚语表达")
        return expressions[:limit]
    
    def _search_urban_term(self, term: str) -> List[ExpressionItem]:
        """搜索Urban Dictionary术语"""
        expressions = []
        
        search_url = f"{self.base_url}/define.php?term={urllib.parse.quote_plus(term)}"
        
        try:
            soup = self.get_dynamic_content(search_url)
            if not soup:
                return expressions
            
            # Urban Dictionary的定义条目
            definitions = soup.select('.definition')
            
            for def_elem in definitions[:3]:  # 最多取前3个定义
                try:
                    expression_item = self._parse_urban_definition(def_elem, search_url)
                    if expression_item:
                        expressions.append(expression_item)
                except Exception as e:
                    logger.warning(f"解析Urban Dictionary定义失败: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"搜索Urban Dictionary失败: {str(e)}")
        
        return expressions
    
    def _parse_urban_definition(self, def_elem, source_url: str) -> Optional[ExpressionItem]:
        """解析Urban Dictionary的定义条目"""
        try:
            # 提取词汇
            word_elem = def_elem.select_one('.word, .definition-header')
            if not word_elem:
                return None
            
            expression = self.clean_expression_text(word_elem.get_text())
            
            # 提取定义
            meaning_elem = def_elem.select_one('.meaning, .definition-text')
            if not meaning_elem:
                return None
            
            meaning = self.clean_text(meaning_elem.get_text())
            
            # 提取示例
            example_elem = def_elem.select_one('.example, .example-text')
            examples = []
            if example_elem:
                example_text = self.clean_text(example_elem.get_text())
                if example_text:
                    examples.append(example_text)
            
            # 提取投票信息
            thumbs_up = self._extract_vote_count(def_elem, '.up, .thumbs-up')
            thumbs_down = self._extract_vote_count(def_elem, '.down, .thumbs-down')
            
            if not expression or not meaning:
                return None
            
            return ExpressionItem(
                expression=expression,
                meaning=meaning,
                source_url=source_url,
                source_name=self.source_name,
                expression_type='slang',  # Urban Dictionary主要是俚语
                formality_level='informal',  # 俚语通常是非正式的
                frequency_score=self._calculate_urban_frequency(thumbs_up, thumbs_down),
                usage_examples=examples,
                scenarios=['casual', 'social', 'youth'],
                difficulty_level='intermediate',  # 俚语对学习者来说通常是中等难度
                cultural_background='美式英语俚语，主要流行于年轻人群体',
                metadata={
                    'extraction_method': 'urban_dictionary',
                    'thumbs_up': thumbs_up,
                    'thumbs_down': thumbs_down,
                    'extraction_timestamp': timezone.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"解析Urban Dictionary定义失败: {str(e)}")
            return None
    
    def _extract_vote_count(self, elem, selector: str) -> int:
        """提取投票数"""
        vote_elem = elem.select_one(selector)
        if vote_elem:
            vote_text = vote_elem.get_text()
            numbers = re.findall(r'\d+', vote_text)
            if numbers:
                return int(numbers[0])
        return 0
    
    def _calculate_urban_frequency(self, thumbs_up: int, thumbs_down: int) -> int:
        """根据Urban Dictionary的投票计算频率评分"""
        total_votes = thumbs_up + thumbs_down
        if total_votes == 0:
            return 3
        
        approval_rate = thumbs_up / total_votes
        
        # 基于赞同率和总投票数计算 - 调整条件以匹配测试
        if approval_rate >= 0.8 and total_votes >= 100:
            return 8
        elif approval_rate >= 0.7 and total_votes >= 50:
            return 7
        elif approval_rate >= 0.6 and total_votes >= 20:
            return 6
        elif approval_rate >= 0.5:
            return 5
        else:
            return 3


class YouGlishCrawler(BaseExpressionCrawler):
    """YouGlish爬虫 - 采集真实语音中的表达用法"""
    
    def __init__(self):
        super().__init__('YouGlish')
        self.base_url = 'https://youglish.com'
        
        # YouGlish特定配置
        self.session.headers.update({
            'Referer': 'https://youglish.com/',
        })
    
    def crawl_expressions(self, limit: int = 30) -> List[ExpressionItem]:
        """抓取YouGlish的表达用法"""
        expressions = []
        
        # 常见表达关键词
        expression_terms = [
            'break the ice', 'piece of cake', 'hit the nail on the head',
            'spill the beans', 'bite the bullet', 'cut to the chase',
            'get the ball rolling', 'think outside the box'
        ]
        
        for term in expression_terms[:limit//4]:
            try:
                term_data = self._search_youglish_term(term)
                if term_data:
                    expressions.append(term_data)
                
                # 避免请求过于频繁
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                logger.error(f"搜索YouGlish术语 '{term}' 失败: {str(e)}")
                continue
        
        logger.info(f"YouGlish爬虫完成，获取 {len(expressions)} 个表达式")
        return expressions
    
    def _search_youglish_term(self, term: str) -> Optional[ExpressionItem]:
        """搜索YouGlish术语"""
        search_url = f"{self.base_url}/pronounce/{urllib.parse.quote_plus(term)}/english"
        
        try:
            soup = self.get_dynamic_content(search_url)
            if not soup:
                return None
            
            # 提取视频数量作为使用频率指标
            result_count = self._extract_result_count(soup)
            
            # 创建基于YouGlish数据的表达式项目
            return ExpressionItem(
                expression=term,
                meaning=f"Common English expression with {result_count} video examples",
                source_url=search_url,
                source_name=self.source_name,
                expression_type=self.determine_expression_type(term),
                formality_level='neutral',
                frequency_score=min(result_count // 100 + 3, 10),  # 基于视频数量计算频率
                usage_examples=[f"Found in {result_count} real-world video examples"],
                scenarios=['spoken', 'natural'],
                difficulty_level=self.determine_difficulty(term),
                cultural_background='真实英语语音使用环境',
                metadata={
                    'extraction_method': 'youglish_video_count',
                    'video_count': result_count,
                    'extraction_timestamp': timezone.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"搜索YouGlish失败: {str(e)}")
            return None
    
    def _extract_result_count(self, soup: BeautifulSoup) -> int:
        """提取结果数量"""
        count_elem = soup.select_one('.result-count, .total-results, #totalrecords')
        if count_elem:
            count_text = count_elem.get_text()
            # 移除逗号分隔符，然后提取数字
            count_text = count_text.replace(',', '')
            numbers = re.findall(r'\d+', count_text)
            if numbers:
                return int(numbers[0])
        return 0


# 注册所有专业爬虫到服务中
def register_specialized_crawlers():
    """注册所有专业爬虫到表达式爬虫服务中"""
    from .expression_crawler import expression_crawler_service
    
    # 注册各个专业爬虫
    expression_crawler_service.add_crawler('cambridge', CambridgeCrawler())
    expression_crawler_service.add_crawler('collins', CollinsCrawler())
    expression_crawler_service.add_crawler('reddit', RedditCrawler())
    expression_crawler_service.add_crawler('urban_dictionary', UrbanDictionaryCrawler())
    expression_crawler_service.add_crawler('youglish', YouGlishCrawler())
    
    logger.info("所有专业爬虫已注册完成")


# 自动注册爬虫
register_specialized_crawlers()
