#!/usr/bin/env python3
"""
地道表达数据采集脚本
支持多种数据源的数据采集和处理
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/expression_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class ExpressionData:
    """地道表达数据结构"""
    expression: str
    meaning: str
    category: str
    difficulty_level: str
    usage_examples: List[str]
    cultural_notes: Optional[str] = None
    pronunciation_guide: Optional[str] = None
    source: str = "unknown"
    quality_score: float = 0.0


class UrbanDictionaryCollector:
    """Urban Dictionary数据采集器"""
    
    def __init__(self):
        self.base_url = "https://api.urbandictionary.com/v0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_trending_words(self) -> List[str]:
        """获取热门词汇列表"""
        try:
            response = self.session.get(f"{self.base_url}/trending")
            if response.status_code == 200:
                data = response.json()
                return [item['word'] for item in data.get('list', [])]
            return []
        except Exception as e:
            logger.error(f"获取热门词汇失败: {e}")
            return []
    
    def get_word_definition(self, word: str) -> Optional[ExpressionData]:
        """获取词汇定义"""
        try:
            response = self.session.get(f"{self.base_url}/define", params={'term': word})
            if response.status_code == 200:
                data = response.json()
                definitions = data.get('list', [])
                
                if definitions:
                    # 选择评分最高的定义
                    best_def = max(definitions, key=lambda x: x.get('thumbs_up', 0))
                    
                    return ExpressionData(
                        expression=best_def.get('word', ''),
                        meaning=best_def.get('definition', ''),
                        category='slang',
                        difficulty_level='intermediate',
                        usage_examples=[best_def.get('example', '')],
                        cultural_notes=best_def.get('author', ''),
                        source='urban_dictionary',
                        quality_score=min(best_def.get('thumbs_up', 0) / 100, 1.0)
                    )
            return None
        except Exception as e:
            logger.error(f"获取词汇定义失败 {word}: {e}")
            return None
    
    def collect_trending_expressions(self, limit: int = 100) -> List[ExpressionData]:
        """采集热门地道表达"""
        expressions = []
        trending_words = self.get_trending_words()[:limit]
        
        for word in trending_words:
            expression_data = self.get_word_definition(word)
            if expression_data:
                expressions.append(expression_data)
                logger.info(f"采集到表达: {word}")
            
            # 避免请求过于频繁
            time.sleep(1)
        
        return expressions


class FreeDictionaryCollector:
    """Free Dictionary API数据采集器"""
    
    def __init__(self):
        self.base_url = "https://api.dictionaryapi.dev/api/v2/entries"
        self.session = requests.Session()
    
    def get_word_info(self, word: str) -> Optional[ExpressionData]:
        """获取词汇信息"""
        try:
            response = self.session.get(f"{self.base_url}/en/{word}")
            if response.status_code == 200:
                data = response.json()
                
                if data and isinstance(data, list):
                    word_data = data[0]
                    meanings = word_data.get('meanings', [])
                    
                    if meanings:
                        meaning = meanings[0]
                        definition = meaning.get('definitions', [{}])[0].get('definition', '')
                        examples = [def_obj.get('example', '') for def_obj in meaning.get('definitions', []) if def_obj.get('example')]
                        
                        return ExpressionData(
                            expression=word_data.get('word', ''),
                            meaning=definition,
                            category=meaning.get('partOfSpeech', 'general'),
                            difficulty_level='beginner',
                            usage_examples=examples,
                            source='free_dictionary_api'
                        )
            return None
        except Exception as e:
            logger.error(f"获取词汇信息失败 {word}: {e}")
            return None
    
    def collect_idioms(self, idiom_list: List[str]) -> List[ExpressionData]:
        """采集习语列表"""
        expressions = []
        
        for idiom in idiom_list:
            expression_data = self.get_word_info(idiom)
            if expression_data:
                expression_data.category = 'idiom'
                expression_data.difficulty_level = 'intermediate'
                expressions.append(expression_data)
                logger.info(f"采集到习语: {idiom}")
            
            time.sleep(0.5)  # 避免请求过于频繁
        
        return expressions


class AIGenerator:
    """AI数据生成器"""
    
    def __init__(self, api_key: str):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.available = True
        except ImportError:
            logger.warning("OpenAI库未安装，AI生成功能不可用")
            self.available = False
    
    def generate_expressions(self, category: str, count: int = 10) -> List[ExpressionData]:
        """生成地道表达"""
        if not self.available:
            return []
        
        prompt = f"""
        生成{count}个{category}类别的英语地道表达，以JSON格式返回：
        {{
            "expressions": [
                {{
                    "expression": "表达内容",
                    "meaning": "中文含义",
                    "category": "{category}",
                    "difficulty_level": "beginner/intermediate/advanced",
                    "usage_examples": ["例句1", "例句2"],
                    "cultural_notes": "文化背景说明"
                }}
            ]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            data = json.loads(content)
            
            expressions = []
            for item in data.get('expressions', []):
                expression = ExpressionData(
                    expression=item.get('expression', ''),
                    meaning=item.get('meaning', ''),
                    category=item.get('category', category),
                    difficulty_level=item.get('difficulty_level', 'intermediate'),
                    usage_examples=item.get('usage_examples', []),
                    cultural_notes=item.get('cultural_notes', ''),
                    source='ai_generated',
                    quality_score=0.8
                )
                expressions.append(expression)
            
            return expressions
            
        except Exception as e:
            logger.error(f"AI生成失败: {e}")
            return []


class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        self.output_dir = Path("data/expressions")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_expressions(self, expressions: List[ExpressionData], filename: str):
        """保存表达数据到JSON文件"""
        data = []
        for expr in expressions:
            data.append({
                'expression': expr.expression,
                'meaning': expr.meaning,
                'category': expr.category,
                'difficulty_level': expr.difficulty_level,
                'usage_examples': expr.usage_examples,
                'cultural_notes': expr.cultural_notes,
                'pronunciation_guide': expr.pronunciation_guide,
                'source': expr.source,
                'quality_score': expr.quality_score,
                'collected_at': datetime.now().isoformat()
            })
        
        output_file = self.output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"保存了 {len(data)} 条表达数据到 {output_file}")
    
    def load_expressions(self, filename: str) -> List[ExpressionData]:
        """从JSON文件加载表达数据"""
        input_file = self.output_dir / filename
        if not input_file.exists():
            return []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        expressions = []
        for item in data:
            expression = ExpressionData(
                expression=item.get('expression', ''),
                meaning=item.get('meaning', ''),
                category=item.get('category', ''),
                difficulty_level=item.get('difficulty_level', ''),
                usage_examples=item.get('usage_examples', []),
                cultural_notes=item.get('cultural_notes'),
                pronunciation_guide=item.get('pronunciation_guide'),
                source=item.get('source', ''),
                quality_score=item.get('quality_score', 0.0)
            )
            expressions.append(expression)
        
        return expressions
    
    def merge_and_deduplicate(self, expression_lists: List[List[ExpressionData]]) -> List[ExpressionData]:
        """合并和去重表达数据"""
        all_expressions = {}
        
        for expressions in expression_lists:
            for expr in expressions:
                key = expr.expression.lower().strip()
                if key not in all_expressions:
                    all_expressions[key] = expr
                else:
                    # 如果已存在，选择质量分数更高的
                    if expr.quality_score > all_expressions[key].quality_score:
                        all_expressions[key] = expr
        
        return list(all_expressions.values())


def main():
    """主函数"""
    logger.info("开始采集地道表达数据...")
    
    processor = DataProcessor()
    
    # 1. 采集Urban Dictionary数据
    logger.info("开始采集Urban Dictionary数据...")
    urban_collector = UrbanDictionaryCollector()
    urban_expressions = urban_collector.collect_trending_expressions(limit=50)
    processor.save_expressions(urban_expressions, "urban_dictionary_expressions.json")
    
    # 2. 采集Free Dictionary数据
    logger.info("开始采集Free Dictionary数据...")
    free_collector = FreeDictionaryCollector()
    
    # 常见习语列表
    common_idioms = [
        "break the ice", "hit the nail on the head", "let the cat out of the bag",
        "piece of cake", "cost an arm and a leg", "break a leg",
        "hit the sack", "miss the boat", "pull someone's leg",
        "so far so good", "speak of the devil", "the last straw"
    ]
    
    free_expressions = free_collector.collect_idioms(common_idioms)
    processor.save_expressions(free_expressions, "free_dictionary_expressions.json")
    
    # 3. AI生成数据（如果可用）
    logger.info("开始AI生成数据...")
    ai_generator = AIGenerator(api_key=os.getenv('OPENAI_API_KEY', ''))
    
    categories = ['business', 'daily', 'academic', 'emotional']
    ai_expressions = []
    
    for category in categories:
        category_expressions = ai_generator.generate_expressions(category, count=5)
        ai_expressions.extend(category_expressions)
    
    if ai_expressions:
        processor.save_expressions(ai_expressions, "ai_generated_expressions.json")
    
    # 4. 合并所有数据
    logger.info("合并和去重数据...")
    all_expressions = processor.merge_and_deduplicate([
        urban_expressions,
        free_expressions,
        ai_expressions
    ])
    
    processor.save_expressions(all_expressions, "merged_expressions.json")
    
    # 5. 生成统计报告
    logger.info("生成统计报告...")
    stats = {
        'total_expressions': len(all_expressions),
        'by_source': {},
        'by_category': {},
        'by_difficulty': {}
    }
    
    for expr in all_expressions:
        # 按来源统计
        stats['by_source'][expr.source] = stats['by_source'].get(expr.source, 0) + 1
        
        # 按分类统计
        stats['by_category'][expr.category] = stats['by_category'].get(expr.category, 0) + 1
        
        # 按难度统计
        stats['by_difficulty'][expr.difficulty_level] = stats['by_difficulty'].get(expr.difficulty_level, 0) + 1
    
    # 保存统计报告
    stats_file = processor.output_dir / "collection_stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    logger.info(f"数据采集完成！总共采集了 {len(all_expressions)} 条地道表达")
    logger.info(f"统计报告已保存到: {stats_file}")
    
    return all_expressions


if __name__ == '__main__':
    main() 