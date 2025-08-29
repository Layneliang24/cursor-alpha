"""
地道表达数据质量控制模块
包含数据清洗、质量评估、去重机制
"""

import hashlib
import re
import difflib
from typing import List, Dict, Optional, Tuple, Set
import logging
from django.utils import timezone
from django.conf import settings
import json
from datetime import datetime, timedelta

# 可选的Redis导入
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

from .expression_crawler import ExpressionItem

logger = logging.getLogger(__name__)


class DataCleaner:
    """数据清洗器"""
    
    def __init__(self):
        self.html_pattern = re.compile(r'<[^>]+>')
        self.special_chars_pattern = re.compile(r'[^\w\s\.\,\!\?\;\:\-\(\)\"\'\$\%\/\[\]]')
        self.multiple_spaces_pattern = re.compile(r'\s+')
        
    def clean_expression(self, expression: str) -> str:
        """清洗表达式文本"""
        if not expression:
            return ""
        
        # 去除HTML标签
        text = self.html_pattern.sub('', expression)
        
        # 去除多余的空白字符
        text = self.multiple_spaces_pattern.sub(' ', text)
        
        # 去除首尾空白
        text = text.strip()
        
        # 去除编号和项目符号
        text = re.sub(r'^\d+\.\s*', '', text)
        text = re.sub(r'^[•·▪▫]\s*', '', text)
        
        # 去除末尾的括号内容（如果是语法说明）
        text = re.sub(r'\s*\([^)]*\)$', '', text)
        
        return text
    
    def clean_meaning(self, meaning: str) -> str:
        """清洗含义文本"""
        if not meaning:
            return ""
        
        # 基础清洗
        text = self.html_pattern.sub('', meaning)
        text = self.multiple_spaces_pattern.sub(' ', text)
        text = text.strip()
        
        # 去除常见的无用前缀
        prefixes_to_remove = [
            'definition:', 'meaning:', 'means:', 'refers to:',
            '定义：', '含义：', '意思是：', '指的是：'
        ]
        
        text_lower = text.lower()
        for prefix in prefixes_to_remove:
            if text_lower.startswith(prefix.lower()):
                text = text[len(prefix):].strip()
                break
        
        return text
    
    def clean_examples(self, examples: List[str]) -> List[str]:
        """清洗示例列表"""
        cleaned_examples = []
        
        for example in examples:
            if not example:
                continue
                
            # 基础清洗
            text = self.html_pattern.sub('', example)
            text = self.multiple_spaces_pattern.sub(' ', text)
            text = text.strip()
            
            # 去除示例编号
            text = re.sub(r'^\d+\.\s*', '', text)
            text = re.sub(r'^Example\s*\d*:\s*', '', text, flags=re.IGNORECASE)
            
            # 过滤太短或太长的示例
            if 5 <= len(text) <= 200:
                cleaned_examples.append(text)
        
        return cleaned_examples
    
    def clean_expression_item(self, item: ExpressionItem) -> ExpressionItem:
        """清洗整个表达式项目"""
        item.expression = self.clean_expression(item.expression)
        item.meaning = self.clean_meaning(item.meaning)
        item.usage_examples = self.clean_examples(item.usage_examples)
        
        # 清洗音标
        if item.phonetic_transcription:
            item.phonetic_transcription = item.phonetic_transcription.strip()
        
        # 清洗文化背景
        if item.cultural_background:
            item.cultural_background = self.clean_meaning(item.cultural_background)
        
        return item


class QualityAssessor:
    """数据质量评估器"""
    
    def __init__(self):
        self.min_expression_length = 2
        self.max_expression_length = 100
        self.min_meaning_length = 5
        self.max_meaning_length = 500
        
    def assess_expression_quality(self, item: ExpressionItem) -> Dict[str, float]:
        """评估表达式质量，返回各项评分"""
        scores = {}
        
        # 1. 内容完整性评分 (0-1)
        scores['completeness'] = self._assess_completeness(item)
        
        # 2. 语法正确性评分 (0-1)
        scores['grammar'] = self._assess_grammar(item)
        
        # 3. 相关性评分 (0-1)
        scores['relevance'] = self._assess_relevance(item)
        
        # 4. 信息丰富度评分 (0-1)
        scores['richness'] = self._assess_richness(item)
        
        # 5. 可信度评分 (0-1)
        scores['credibility'] = self._assess_credibility(item)
        
        # 计算综合质量分数
        weights = {
            'completeness': 0.3,
            'grammar': 0.2,
            'relevance': 0.2,
            'richness': 0.15,
            'credibility': 0.15
        }
        
        scores['overall'] = sum(scores[key] * weights[key] for key in weights)
        
        return scores
    
    def _assess_completeness(self, item: ExpressionItem) -> float:
        """评估内容完整性"""
        score = 0.0
        
        # 检查必要字段
        if item.expression and len(item.expression.strip()) >= self.min_expression_length:
            score += 0.4
        
        if item.meaning and len(item.meaning.strip()) >= self.min_meaning_length:
            score += 0.4
        
        # 检查可选字段
        if item.usage_examples and len(item.usage_examples) > 0:
            score += 0.1
        
        if item.scenarios and len(item.scenarios) > 0:
            score += 0.05
        
        if item.phonetic_transcription:
            score += 0.05
        
        return min(score, 1.0)
    
    def _assess_grammar(self, item: ExpressionItem) -> float:
        """评估语法正确性（简单启发式）"""
        score = 1.0
        
        # 检查表达式
        if item.expression:
            # 过长的表达式可能有问题
            if len(item.expression) > self.max_expression_length:
                score -= 0.3
            
            # 检查是否包含过多特殊字符
            special_char_ratio = len(re.findall(r'[^a-zA-Z\s\'\-]', item.expression)) / max(len(item.expression), 1)
            if special_char_ratio > 0.3:
                score -= 0.2
        
        # 检查含义
        if item.meaning:
            if len(item.meaning) > self.max_meaning_length:
                score -= 0.2
            
            # 检查是否以大写字母开头（基本语法）
            if item.meaning and not item.meaning[0].isupper():
                score -= 0.1
        
        return max(score, 0.0)
    
    def _assess_relevance(self, item: ExpressionItem) -> float:
        """评估内容相关性"""
        score = 0.5  # 基础分
        
        # 检查表达式和含义的相关性
        if item.expression and item.meaning:
            expression_words = set(item.expression.lower().split())
            meaning_words = set(item.meaning.lower().split())
            
            # 简单的词汇重叠检查
            common_words = expression_words.intersection(meaning_words)
            if common_words:
                score += 0.2
        
        # 检查示例的相关性
        if item.usage_examples and item.expression:
            for example in item.usage_examples:
                if item.expression.lower() in example.lower():
                    score += 0.1
                    break
        
        # 检查类型分类的合理性
        if item.expression_type:
            if self._is_type_reasonable(item.expression, item.expression_type):
                score += 0.2
        
        return min(score, 1.0)
    
    def _assess_richness(self, item: ExpressionItem) -> float:
        """评估信息丰富度"""
        score = 0.0
        
        # 基于字段数量
        fields = [
            item.expression, item.meaning, item.usage_examples,
            item.scenarios, item.phonetic_transcription, 
            item.cultural_background, item.metadata
        ]
        
        non_empty_fields = sum(1 for field in fields if field)
        score += non_empty_fields / len(fields) * 0.6
        
        # 基于内容长度
        total_content_length = 0
        if item.meaning:
            total_content_length += len(item.meaning)
        if item.usage_examples:
            total_content_length += sum(len(ex) for ex in item.usage_examples)
        
        if total_content_length > 50:
            score += 0.2
        if total_content_length > 150:
            score += 0.2
        
        return min(score, 1.0)
    
    def _assess_credibility(self, item: ExpressionItem) -> float:
        """评估可信度"""
        score = 0.5  # 基础分
        
        # 基于数据源
        trusted_sources = ['cambridge', 'collins', 'oxford', 'merriam-webster']
        if any(source in item.source_name.lower() for source in trusted_sources):
            score += 0.3
        
        # 基于频率评分
        if item.frequency_score >= 7:
            score += 0.1
        elif item.frequency_score <= 3:
            score -= 0.1
        
        # 基于元数据完整性
        if item.metadata and len(item.metadata) > 2:
            score += 0.1
        
        return min(max(score, 0.0), 1.0)
    
    def _is_type_reasonable(self, expression: str, expression_type: str) -> bool:
        """检查表达式类型分类是否合理"""
        if not expression or not expression_type:
            return False
        
        word_count = len(expression.split())
        
        # 简单的启发式规则
        if expression_type == 'idiom' and word_count >= 3:
            return True
        elif expression_type == 'phrase' and 2 <= word_count <= 8:
            return True
        elif expression_type == 'slang' and word_count <= 3:
            return True
        elif expression_type == 'collocation' and word_count == 2:
            return True
        elif expression_type == 'proverb' and word_count >= 5:
            return True
        
        return False
    
    def is_high_quality(self, item: ExpressionItem, threshold: float = 0.6) -> bool:
        """判断是否为高质量数据"""
        scores = self.assess_expression_quality(item)
        return scores['overall'] >= threshold


class DuplicateDetector:
    """重复数据检测器"""
    
    def __init__(self):
        self.redis_client = self._get_redis_client()
        self.similarity_threshold = 0.85
        
    def _get_redis_client(self):
        """获取Redis客户端"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis未安装，使用内存存储")
            return None
            
        try:
            if hasattr(settings, 'REDIS_URL'):
                return redis.from_url(settings.REDIS_URL)
            else:
                return redis.Redis(
                    host=getattr(settings, 'REDIS_HOST', 'localhost'),
                    port=getattr(settings, 'REDIS_PORT', 6379),
                    db=getattr(settings, 'REDIS_DB', 0),
                    decode_responses=True
                )
        except Exception as e:
            logger.warning(f"Redis连接失败，使用内存存储: {str(e)}")
            return None
    
    def generate_content_hash(self, item: ExpressionItem) -> str:
        """生成内容哈希"""
        content = f"{item.expression}|{item.meaning}|{item.source_name}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def generate_url_hash(self, url: str) -> str:
        """生成URL哈希"""
        return hashlib.md5(url.encode('utf-8')).hexdigest()
    
    def is_duplicate_by_hash(self, item: ExpressionItem) -> bool:
        """基于哈希检测重复"""
        if not self.redis_client:
            return False
        
        content_hash = self.generate_content_hash(item)
        url_hash = self.generate_url_hash(item.source_url)
        
        try:
            # 检查内容哈希
            if self.redis_client.exists(f"content_hash:{content_hash}"):
                return True
            
            # 检查URL哈希
            if self.redis_client.exists(f"url_hash:{url_hash}"):
                return True
            
            return False
        except Exception as e:
            logger.error(f"Redis哈希检查失败: {str(e)}")
            return False
    
    def is_duplicate_by_similarity(self, item: ExpressionItem, existing_items: List[ExpressionItem]) -> Tuple[bool, Optional[ExpressionItem]]:
        """基于语义相似度检测重复"""
        for existing_item in existing_items:
            similarity = self._calculate_similarity(item, existing_item)
            if similarity >= self.similarity_threshold:
                return True, existing_item
        
        return False, None
    
    def _calculate_similarity(self, item1: ExpressionItem, item2: ExpressionItem) -> float:
        """计算两个表达式项目的相似度"""
        # 表达式相似度
        expr_similarity = difflib.SequenceMatcher(None, item1.expression.lower(), item2.expression.lower()).ratio()
        
        # 含义相似度
        meaning_similarity = difflib.SequenceMatcher(None, item1.meaning.lower(), item2.meaning.lower()).ratio()
        
        # 综合相似度（表达式权重更高）
        return expr_similarity * 0.7 + meaning_similarity * 0.3
    
    def mark_as_processed(self, item: ExpressionItem, expiry_days: int = 30):
        """标记为已处理"""
        if not self.redis_client:
            return
        
        content_hash = self.generate_content_hash(item)
        url_hash = self.generate_url_hash(item.source_url)
        
        try:
            expiry_seconds = expiry_days * 24 * 60 * 60
            
            # 存储内容哈希
            self.redis_client.setex(
                f"content_hash:{content_hash}",
                expiry_seconds,
                json.dumps({
                    'expression': item.expression,
                    'source': item.source_name,
                    'processed_at': timezone.now().isoformat()
                })
            )
            
            # 存储URL哈希
            self.redis_client.setex(
                f"url_hash:{url_hash}",
                expiry_seconds,
                json.dumps({
                    'url': item.source_url,
                    'processed_at': timezone.now().isoformat()
                })
            )
            
        except Exception as e:
            logger.error(f"Redis标记失败: {str(e)}")
    
    def get_duplicate_stats(self) -> Dict[str, int]:
        """获取重复数据统计"""
        if not self.redis_client:
            return {'content_duplicates': 0, 'url_duplicates': 0}
        
        try:
            content_count = len(self.redis_client.keys("content_hash:*"))
            url_count = len(self.redis_client.keys("url_hash:*"))
            
            return {
                'content_duplicates': content_count,
                'url_duplicates': url_count
            }
        except Exception as e:
            logger.error(f"获取重复统计失败: {str(e)}")
            return {'content_duplicates': 0, 'url_duplicates': 0}


class DataProcessor:
    """数据处理器 - 整合清洗、质量评估和去重"""
    
    def __init__(self):
        self.cleaner = DataCleaner()
        self.quality_assessor = QualityAssessor()
        self.duplicate_detector = DuplicateDetector()
        
    def process_expression_items(self, items: List[ExpressionItem], quality_threshold: float = 0.6) -> Dict[str, List[ExpressionItem]]:
        """处理表达式项目列表"""
        results = {
            'accepted': [],
            'rejected_quality': [],
            'rejected_duplicate': [],
            'rejected_invalid': []
        }
        
        for item in items:
            try:
                # 1. 数据清洗
                cleaned_item = self.cleaner.clean_expression_item(item)
                
                # 2. 基础有效性检查
                if not self._is_valid_item(cleaned_item):
                    results['rejected_invalid'].append(cleaned_item)
                    continue
                
                # 3. 重复检测
                if self.duplicate_detector.is_duplicate_by_hash(cleaned_item):
                    results['rejected_duplicate'].append(cleaned_item)
                    continue
                
                # 4. 质量评估
                if not self.quality_assessor.is_high_quality(cleaned_item, quality_threshold):
                    results['rejected_quality'].append(cleaned_item)
                    continue
                
                # 5. 通过所有检查
                results['accepted'].append(cleaned_item)
                
                # 6. 标记为已处理
                self.duplicate_detector.mark_as_processed(cleaned_item)
                
            except Exception as e:
                logger.error(f"处理表达式项目失败: {str(e)}")
                results['rejected_invalid'].append(item)
        
        return results
    
    def _is_valid_item(self, item: ExpressionItem) -> bool:
        """检查项目基础有效性"""
        if not item.expression or not item.expression.strip():
            return False
        
        if not item.meaning or not item.meaning.strip():
            return False
        
        if len(item.expression.strip()) < 2:
            return False
        
        if len(item.meaning.strip()) < 5:
            return False
        
        return True
    
    def generate_quality_report(self, processing_results: Dict[str, List[ExpressionItem]]) -> Dict[str, any]:
        """生成质量报告"""
        total_items = sum(len(items) for items in processing_results.values())
        
        if total_items == 0:
            return {'total_items': 0, 'acceptance_rate': 0.0}
        
        accepted_count = len(processing_results['accepted'])
        
        report = {
            'total_items': total_items,
            'accepted_count': accepted_count,
            'rejected_quality_count': len(processing_results['rejected_quality']),
            'rejected_duplicate_count': len(processing_results['rejected_duplicate']),
            'rejected_invalid_count': len(processing_results['rejected_invalid']),
            'acceptance_rate': accepted_count / total_items,
            'duplicate_stats': self.duplicate_detector.get_duplicate_stats(),
            'timestamp': timezone.now().isoformat()
        }
        
        # 质量分数统计
        if accepted_count > 0:
            quality_scores = []
            for item in processing_results['accepted']:
                scores = self.quality_assessor.assess_expression_quality(item)
                quality_scores.append(scores['overall'])
            
            report['avg_quality_score'] = sum(quality_scores) / len(quality_scores)
            report['min_quality_score'] = min(quality_scores)
            report['max_quality_score'] = max(quality_scores)
        
        return report


# 全局数据处理器实例
data_processor = DataProcessor()
