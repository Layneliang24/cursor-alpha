"""
地道表达爬虫服务
基于现有新闻爬虫架构扩展，支持多源地道表达数据采集
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union, Any
import logging
import time
import random
from django.utils import timezone
from django.conf import settings
import json
from dateutil import parser as date_parser
import urllib.parse
from abc import ABC, abstractmethod

# 继承现有新闻爬虫的基础功能
from .news_crawler import EnhancedNewsCrawler

logger = logging.getLogger(__name__)


class ExpressionItem:
    """地道表达条目数据类"""
    
    def __init__(self, 
                 expression: str, 
                 meaning: str, 
                 source_url: str, 
                 source_name: str,
                 expression_type: str = 'phrase',
                 formality_level: str = 'neutral',
                 frequency_score: int = 5,
                 phonetic_transcription: str = '',
                 usage_examples: List[str] = None,
                 scenarios: List[str] = None,
                 metadata: Dict[str, Any] = None,
                 difficulty_level: str = 'intermediate',
                 cultural_background: str = '',
                 created_at: Optional[datetime] = None):
        
        self.expression = expression
        self.meaning = meaning
        self.source_url = source_url
        self.source_name = source_name
        self.expression_type = expression_type
        self.formality_level = formality_level
        self.frequency_score = frequency_score
        self.phonetic_transcription = phonetic_transcription
        self.usage_examples = usage_examples or []
        self.scenarios = scenarios or []
        self.metadata = metadata or {}
        self.difficulty_level = difficulty_level
        self.cultural_background = cultural_background
        self.created_at = created_at or timezone.now()


class BaseExpressionCrawler(EnhancedNewsCrawler, ABC):
    """地道表达爬虫基类 - 继承新闻爬虫的核心功能"""
    
    def __init__(self, source_name: str):
        super().__init__(source_name)
        
        # 扩展请求头，适配更多网站
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })
        
        # 地道表达特有的配置
        self.expression_selectors = []
        self.meaning_selectors = []
        self.example_selectors = []
        
        # 支持JavaScript渲染的动态内容（可选）
        self.use_js_rendering = False
        
    @abstractmethod
    def crawl_expressions(self, limit: int = 50) -> List[ExpressionItem]:
        """抓取地道表达列表 - 抽象方法，子类必须实现"""
        pass
    
    def get_dynamic_content(self, url: str) -> Optional[BeautifulSoup]:
        """获取JavaScript渲染后的动态内容"""
        try:
            if not self.use_js_rendering:
                # 使用标准请求
                response = self.session.get(url, timeout=20)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'lxml')
            
            # 使用requests-html处理JavaScript（如果需要）
            try:
                from requests_html import HTMLSession
                session = HTMLSession()
                r = session.get(url)
                r.html.render(timeout=20)
                return BeautifulSoup(r.html.html, 'lxml')
            except ImportError:
                logger.warning("requests-html未安装，使用标准请求")
                response = self.session.get(url, timeout=20)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'lxml')
                
        except Exception as e:
            logger.error(f"获取动态内容失败 {url}: {str(e)}")
            return None
    
    def extract_expression_data(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """从页面中提取表达式数据的通用方法"""
        expressions = []
        
        # 尝试不同的选择器策略
        for selector_set in self._get_selector_combinations():
            try:
                items = self._extract_with_selectors(soup, selector_set, base_url)
                if items:
                    expressions.extend(items)
                    break  # 找到有效数据就停止尝试其他选择器
            except Exception as e:
                logger.warning(f"选择器 {selector_set} 提取失败: {str(e)}")
                continue
        
        return expressions
    
    def _get_selector_combinations(self) -> List[Dict[str, str]]:
        """获取不同的选择器组合策略"""
        return [
            # 通用选择器组合
            {
                'expression': '.expression, .phrase, .idiom, .term',
                'meaning': '.meaning, .definition, .explanation, .description',
                'example': '.example, .usage, .sentence, .sample'
            },
            # 词典网站选择器
            {
                'expression': 'h1, .headword, .entry-title',
                'meaning': '.sense, .def, .meaning-text',
                'example': '.example-sentence, .quote'
            },
            # 学习网站选择器
            {
                'expression': '.title, .expression-text, .phrase-text',
                'meaning': '.translation, .chinese, .explanation-text',
                'example': '.example-text, .usage-example'
            }
        ]
    
    def _extract_with_selectors(self, soup: BeautifulSoup, selectors: Dict[str, str], base_url: str) -> List[Dict[str, Any]]:
        """使用指定选择器提取数据"""
        expressions = []
        
        expression_elements = soup.select(selectors['expression'])
        
        for expr_elem in expression_elements:
            try:
                expression_text = self.clean_text(expr_elem.get_text())
                if not expression_text or len(expression_text) < 2:
                    continue
                
                # 查找对应的含义
                meaning_text = self._find_related_meaning(expr_elem, selectors['meaning'])
                if not meaning_text:
                    continue
                
                # 查找使用示例
                examples = self._find_related_examples(expr_elem, selectors['example'])
                
                expressions.append({
                    'expression': expression_text,
                    'meaning': meaning_text,
                    'examples': examples,
                    'source_url': base_url
                })
                
            except Exception as e:
                logger.warning(f"提取表达式失败: {str(e)}")
                continue
        
        return expressions
    
    def _find_related_meaning(self, expr_elem, meaning_selector: str) -> str:
        """查找与表达式相关的含义"""
        # 尝试在同一父元素中查找
        parent = expr_elem.parent
        if parent:
            meaning_elem = parent.select_one(meaning_selector)
            if meaning_elem:
                return self.clean_text(meaning_elem.get_text())
        
        # 尝试在下一个兄弟元素中查找
        next_sibling = expr_elem.find_next_sibling()
        if next_sibling:
            meaning_elem = next_sibling.select_one(meaning_selector)
            if meaning_elem:
                return self.clean_text(meaning_elem.get_text())
        
        # 尝试在整个文档中查找最近的含义元素
        all_meanings = expr_elem.find_parent().select(meaning_selector)
        if all_meanings:
            return self.clean_text(all_meanings[0].get_text())
        
        return ""
    
    def _find_related_examples(self, expr_elem, example_selector: str) -> List[str]:
        """查找与表达式相关的使用示例"""
        examples = []
        
        # 在父元素中查找示例
        parent = expr_elem.parent
        if parent:
            example_elems = parent.select(example_selector)
            for elem in example_elems[:3]:  # 最多3个示例
                example_text = self.clean_text(elem.get_text())
                if example_text and len(example_text) > 10:
                    examples.append(example_text)
        
        return examples
    
    def determine_expression_type(self, expression: str, meaning: str = "") -> str:
        """根据表达式内容判断类型"""
        expression_lower = expression.lower()
        meaning_lower = meaning.lower()
        
        # 习语特征
        if any(word in expression_lower for word in ['as', 'like', 'break', 'make', 'get', 'take']):
            if len(expression.split()) >= 3:
                return 'idiom'
        
        # 俚语特征
        if any(word in meaning_lower for word in ['slang', 'informal', 'casual', 'colloquial']):
            return 'slang'
        
        # 固定搭配特征
        if any(pattern in expression_lower for pattern in ['of', 'to', 'for', 'with', 'in']):
            if len(expression.split()) == 2:
                return 'collocation'
        
        # 谚语特征
        if ',' in expression or len(expression.split()) > 6:
            return 'proverb'
        
        # 默认为短语
        return 'phrase'
    
    def determine_formality_level(self, expression: str, meaning: str = "", examples: List[str] = None) -> str:
        """判断表达式的正式程度"""
        text_to_analyze = f"{expression} {meaning} {' '.join(examples or [])}"
        text_lower = text_to_analyze.lower()
        
        informal_indicators = ['informal', 'casual', 'slang', 'colloquial', 'spoken']
        formal_indicators = ['formal', 'academic', 'professional', 'business', 'official']
        
        # 先检查非正式指标，避免 "informal" 被 "formal" 匹配
        if any(indicator in text_lower for indicator in informal_indicators):
            return 'informal'
        elif any(indicator in text_lower for indicator in formal_indicators):
            return 'formal'
        else:
            return 'neutral'
    
    def calculate_frequency_score(self, expression: str, source_context: str = "") -> int:
        """计算使用频率评分 (1-10)"""
        # 基于表达式长度的基础评分
        word_count = len(expression.split())
        if word_count <= 2:
            base_score = 8  # 短表达式通常使用频率高
        elif word_count <= 4:
            base_score = 6
        else:
            base_score = 4  # 长表达式通常使用频率低
        
        # 根据常见词汇调整评分
        common_words = ['get', 'make', 'take', 'go', 'come', 'have', 'be', 'do']
        if any(word in expression.lower().split() for word in common_words):
            base_score += 2
        
        # 根据来源上下文调整
        context_lower = source_context.lower()
        if 'common' in context_lower or 'frequent' in context_lower:
            base_score += 1
        elif 'rare' in context_lower or 'uncommon' in context_lower:
            base_score -= 2
        
        return max(1, min(10, base_score))
    
    def extract_phonetic_transcription(self, soup: BeautifulSoup, expression: str) -> str:
        """提取音标"""
        phonetic_selectors = [
            '.phonetic', '.pronunciation', '.ipa', 
            '[class*="phonetic"]', '[class*="pronunciation"]',
            '.pron', '.sound'
        ]
        
        for selector in phonetic_selectors:
            elem = soup.select_one(selector)
            if elem:
                phonetic = self.clean_text(elem.get_text())
                # 验证音标格式
                if phonetic and ('/' in phonetic or '[' in phonetic):
                    return phonetic
        
        return ""
    
    def extract_scenarios(self, examples: List[str], meaning: str = "") -> List[str]:
        """从示例中提取使用场景"""
        scenarios = []
        text_to_analyze = f"{meaning} {' '.join(examples)}"
        text_lower = text_to_analyze.lower()
        
        scenario_keywords = {
            'business': ['business', 'meeting', 'professional'],
            'workplace': ['work', 'office', 'job', 'career', 'workplace', 'colleague', 'boss'],
            'casual': ['friend', 'family', 'casual', 'everyday', 'informal'],
            'academic': ['study', 'school', 'university', 'academic', 'research'],
            'social': ['party', 'social', 'gathering', 'conversation'],
            'travel': ['travel', 'trip', 'vacation', 'airport', 'hotel']
        }
        
        for scenario, keywords in scenario_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                scenarios.append(scenario)
        
        return scenarios[:3]  # 最多3个场景
    
    def clean_expression_text(self, text: str) -> str:
        """清理表达式文本"""
        if not text:
            return ""
        
        # 基础清理
        text = self.clean_text(text)
        
        # 去除编号和标记
        text = re.sub(r'^\d+\.\s*', '', text)  # 去除开头的数字
        text = re.sub(r'^[•·▪▫]\s*', '', text)  # 去除项目符号
        text = re.sub(r'\([^)]*\)$', '', text)  # 去除末尾的括号内容
        
        # 去除多余的标点
        text = re.sub(r'^[,，.。;；:：]+', '', text)
        text = re.sub(r'[,，.。;；:：]+$', '', text)
        
        return text.strip()


class DictionaryCrawler(BaseExpressionCrawler):
    """通用词典网站爬虫基类"""
    
    def __init__(self, source_name: str, base_url: str, search_patterns: List[str]):
        super().__init__(source_name)
        self.base_url = base_url
        self.search_patterns = search_patterns  # 搜索URL模式
        
    def crawl_expressions(self, limit: int = 50) -> List[ExpressionItem]:
        """抓取词典中的地道表达"""
        expressions = []
        
        # 常见地道表达关键词
        search_terms = [
            'break the ice', 'piece of cake', 'hit the books', 'cost an arm and a leg',
            'it\'s raining cats and dogs', 'kill two birds with one stone',
            'let the cat out of the bag', 'a blessing in disguise', 'call it a day',
            'cut corners', 'easy does it', 'get out of hand', 'hang in there',
            'it\'s not rocket science', 'keep an eye on', 'once in a blue moon'
        ]
        
        for term in search_terms[:limit//3]:  # 控制搜索数量
            try:
                expressions_from_term = self._search_expression(term)
                expressions.extend(expressions_from_term)
                
                if len(expressions) >= limit:
                    break
                    
                # 避免请求过于频繁
                time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                logger.error(f"搜索表达式 '{term}' 失败: {str(e)}")
                continue
        
        logger.info(f"{self.source_name} 爬虫完成，获取 {len(expressions)} 个表达式")
        return expressions[:limit]
    
    def _search_expression(self, term: str) -> List[ExpressionItem]:
        """搜索特定表达式"""
        expressions = []
        
        for pattern in self.search_patterns:
            try:
                search_url = pattern.format(term=urllib.parse.quote_plus(term))
                soup = self.get_dynamic_content(search_url)
                
                if soup:
                    raw_data = self.extract_expression_data(soup, search_url)
                    
                    for data in raw_data:
                        expression_item = self._create_expression_item(data, search_url)
                        if expression_item:
                            expressions.append(expression_item)
                
            except Exception as e:
                logger.warning(f"搜索模式 {pattern} 失败: {str(e)}")
                continue
        
        return expressions
    
    def _create_expression_item(self, data: Dict[str, Any], source_url: str) -> Optional[ExpressionItem]:
        """创建表达式项目"""
        try:
            expression = self.clean_expression_text(data.get('expression', ''))
            meaning = self.clean_text(data.get('meaning', ''))
            
            if not expression or not meaning:
                return None
            
            examples = data.get('examples', [])
            
            return ExpressionItem(
                expression=expression,
                meaning=meaning,
                source_url=source_url,
                source_name=self.source_name,
                expression_type=self.determine_expression_type(expression, meaning),
                formality_level=self.determine_formality_level(expression, meaning, examples),
                frequency_score=self.calculate_frequency_score(expression),
                usage_examples=examples,
                scenarios=self.extract_scenarios(examples, meaning),
                difficulty_level=self.determine_difficulty(f"{expression} {meaning}"),
                metadata={
                    'extraction_method': 'dictionary_search',
                    'search_term': data.get('search_term', ''),
                    'extraction_timestamp': timezone.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"创建表达式项目失败: {str(e)}")
            return None


class ExpressionCrawlerService:
    """地道表达爬虫服务管理器"""
    
    def __init__(self):
        self.crawlers = {}
        self._register_crawlers()
    
    def _register_crawlers(self):
        """注册所有可用的爬虫"""
        # 这里将在后续子任务中添加具体的爬虫实现
        pass
    
    def add_crawler(self, name: str, crawler: BaseExpressionCrawler):
        """添加爬虫"""
        self.crawlers[name] = crawler
        logger.info(f"注册爬虫: {name}")
    
    def crawl_expressions(self, source: str = None, limit: int = 100) -> List[ExpressionItem]:
        """抓取地道表达"""
        if source and source in self.crawlers:
            return self.crawlers[source].crawl_expressions(limit)
        
        # 抓取所有源的表达式
        all_expressions = []
        for name, crawler in self.crawlers.items():
            try:
                expressions = crawler.crawl_expressions(limit // len(self.crawlers))
                all_expressions.extend(expressions)
                logger.info(f"{name} 抓取完成: {len(expressions)} 个表达式")
            except Exception as e:
                logger.error(f"抓取 {name} 失败: {str(e)}")
                continue
        
        return all_expressions
    
    def save_expressions_to_db(self, expressions: List[ExpressionItem]) -> int:
        """保存表达式到数据库"""
        from .models import IdiomaticExpression, ExpressionSource
        
        saved_count = 0
        
        for item in expressions:
            try:
                # 检查是否已存在
                if IdiomaticExpression.objects.filter(
                    expression=item.expression,
                    source_url=item.source_url
                ).exists():
                    logger.info(f"表达式已存在，跳过: {item.expression}")
                    continue
                
                # 获取或创建数据源
                source, created = ExpressionSource.objects.get_or_create(
                    source_name=item.source_name,
                    defaults={
                        'source_url': item.source_url,
                        'source_type': 'dictionary',
                        'reliability_score': 8.0,
                        'description': f'数据来源：{item.source_name}'
                    }
                )
                
                # 创建地道表达记录
                expression = IdiomaticExpression.objects.create(
                    expression=item.expression,
                    meaning=item.meaning,
                    source_url=item.source_url,
                    expression_type=item.expression_type,
                    formality_level=item.formality_level,
                    frequency_score=item.frequency_score,
                    phonetic_transcription=item.phonetic_transcription,
                    difficulty_level=item.difficulty_level,
                    cultural_background=item.cultural_background,
                    usage_examples='\n'.join(item.usage_examples),
                    metadata=item.metadata
                )
                
                # 关联数据源
                source.expressions.add(expression)
                
                saved_count += 1
                logger.info(f"保存表达式成功: {expression.expression}")
                
            except Exception as e:
                logger.error(f"保存表达式失败 {item.expression}: {str(e)}")
        
        logger.info(f"表达式保存完成，成功保存 {saved_count} 个")
        return saved_count


# 全局服务实例
expression_crawler_service = ExpressionCrawlerService()
