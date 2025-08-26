#!/usr/bin/env python3
"""
将采集的地道表达数据导入到数据库
"""

import os
import sys
import json
import django
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.english.models import Expression
from django.db import transaction
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def import_expressions_from_json(json_file_path: str):
    """从JSON文件导入表达数据到数据库"""
    
    if not Path(json_file_path).exists():
        logger.error(f"文件不存在: {json_file_path}")
        return
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"开始导入 {len(data)} 条表达数据...")
    
    success_count = 0
    error_count = 0
    
    with transaction.atomic():
        for item in data:
            try:
                # 检查是否已存在
                existing = Expression.objects.filter(
                    expression=item.get('expression', '').strip()
                ).first()
                
                if existing:
                    logger.info(f"表达已存在，跳过: {item.get('expression')}")
                    continue
                
                # 创建新的表达记录
                expression = Expression.objects.create(
                    expression=item.get('expression', '').strip(),
                    meaning=item.get('meaning', ''),
                    category=item.get('category', 'general'),
                    difficulty_level=item.get('difficulty_level', 'intermediate'),
                    usage_frequency=item.get('usage_frequency', 'medium'),
                    cultural_background=item.get('cultural_notes', ''),
                    usage_examples=json.dumps(item.get('usage_examples', []), ensure_ascii=False),
                    source_url=item.get('source_url', ''),
                    source_api=item.get('source', ''),
                    quality_score=item.get('quality_score', 0.0)
                )
                
                success_count += 1
                logger.info(f"成功导入: {expression.expression}")
                
            except Exception as e:
                error_count += 1
                logger.error(f"导入失败 {item.get('expression', 'unknown')}: {e}")
    
    logger.info(f"导入完成！成功: {success_count}, 失败: {error_count}")


def create_sample_data():
    """创建示例数据（如果数据库为空）"""
    
    if Expression.objects.count() > 0:
        logger.info("数据库中已有表达数据，跳过示例数据创建")
        return
    
    sample_expressions = [
        {
            "expression": "break the ice",
            "meaning": "打破僵局，开始交谈",
            "category": "idiom",
            "difficulty_level": "intermediate",
            "usage_examples": [
                "I told a joke to break the ice at the meeting.",
                "She used a funny story to break the ice with her new colleagues."
            ],
            "cultural_notes": "这个习语来源于破冰船，比喻打破人际交往中的冷漠和隔阂。",
            "usage_frequency": "high",
            "quality_score": 0.9
        },
        {
            "expression": "hit the nail on the head",
            "meaning": "一针见血，说到点子上",
            "category": "idiom",
            "difficulty_level": "intermediate",
            "usage_examples": [
                "You really hit the nail on the head with that analysis.",
                "His comment hit the nail on the head - that's exactly the problem."
            ],
            "cultural_notes": "这个习语来源于木工，比喻说话或做事准确到位。",
            "usage_frequency": "medium",
            "quality_score": 0.8
        },
        {
            "expression": "piece of cake",
            "meaning": "小菜一碟，轻而易举",
            "category": "idiom",
            "difficulty_level": "beginner",
            "usage_examples": [
                "Don't worry, this test will be a piece of cake.",
                "Fixing this computer issue was a piece of cake for him."
            ],
            "cultural_notes": "这个习语比喻某事像吃蛋糕一样简单愉快。",
            "usage_frequency": "high",
            "quality_score": 0.9
        },
        {
            "expression": "cost an arm and a leg",
            "meaning": "花费巨大，代价高昂",
            "category": "idiom",
            "difficulty_level": "intermediate",
            "usage_examples": [
                "That new car cost an arm and a leg.",
                "The medical treatment cost an arm and a leg, but it was worth it."
            ],
            "cultural_notes": "这个习语夸张地表示某物价格昂贵，需要付出巨大代价。",
            "usage_frequency": "medium",
            "quality_score": 0.8
        },
        {
            "expression": "break a leg",
            "meaning": "祝你好运（常用于表演艺术）",
            "category": "idiom",
            "difficulty_level": "intermediate",
            "usage_examples": [
                "Good luck with your performance tonight - break a leg!",
                "Break a leg on your job interview tomorrow!"
            ],
            "cultural_notes": "这个习语在戏剧界常用，据说源于迷信，认为说'好运'会带来厄运。",
            "usage_frequency": "medium",
            "quality_score": 0.7
        }
    ]
    
    logger.info("创建示例数据...")
    
    with transaction.atomic():
        for item in sample_expressions:
            try:
                expression = Expression.objects.create(
                    expression=item['expression'],
                    meaning=item['meaning'],
                    category=item['category'],
                    difficulty_level=item['difficulty_level'],
                    usage_frequency=item['usage_frequency'],
                    cultural_background=item['cultural_notes'],
                    usage_examples=json.dumps(item['usage_examples'], ensure_ascii=False),
                    source_api='sample_data',
                    quality_score=item['quality_score']
                )
                logger.info(f"创建示例数据: {expression.expression}")
            except Exception as e:
                logger.error(f"创建示例数据失败: {e}")


def main():
    """主函数"""
    logger.info("开始导入地道表达数据...")
    
    # 1. 创建示例数据（如果数据库为空）
    create_sample_data()
    
    # 2. 导入采集的数据
    data_dir = Path("data/expressions")
    
    if data_dir.exists():
        # 按优先级导入数据
        import_files = [
            "merged_expressions.json",
            "urban_dictionary_expressions.json", 
            "free_dictionary_expressions.json",
            "ai_generated_expressions.json"
        ]
        
        for filename in import_files:
            file_path = data_dir / filename
            if file_path.exists():
                logger.info(f"导入文件: {filename}")
                import_expressions_from_json(str(file_path))
            else:
                logger.info(f"文件不存在，跳过: {filename}")
    else:
        logger.info("数据目录不存在，跳过数据导入")
    
    # 3. 显示统计信息
    total_count = Expression.objects.count()
    logger.info(f"数据库中总共有 {total_count} 条表达数据")
    
    # 按分类统计
    from django.db.models import Count
    category_stats = Expression.objects.values('category').annotate(count=Count('id'))
    logger.info("按分类统计:")
    for stat in category_stats:
        logger.info(f"  {stat['category']}: {stat['count']} 条")


if __name__ == '__main__':
    main() 