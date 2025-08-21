#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中各词典各章节的实际单词数量
验证前端显示的单词数量是否准确

作者: Claude-4-sonnet
创建时间: 2025-08-21
"""

import os
import sys
import django

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, '..', '..', 'backend')
sys.path.insert(0, backend_dir)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.english.models import Dictionary, TypingWord


def check_chapter_word_counts():
    """检查各词典各章节的单词数量"""
    print("🔍 检查数据库中各词典各章节的实际单词数量")
    print("=" * 80)
    
    # 获取所有词典
    dictionaries = Dictionary.objects.filter(is_deleted=False).order_by('id')
    
    for dictionary in dictionaries:
        print(f"\n📚 词典: {dictionary.name} (ID: {dictionary.id})")
        print(f"   总单词数: {dictionary.total_words}")
        print(f"   章节数: {dictionary.chapter_count}")
        print("-" * 50)
        
        # 检查每个章节的实际单词数量
        for chapter in range(1, dictionary.chapter_count + 1):
            word_count = TypingWord.objects.filter(
                dictionary_id=dictionary.id,
                chapter=chapter
            ).count()
            
            print(f"   第{chapter}章: {word_count}个单词")
            
            # 显示前几个单词作为示例
            if word_count > 0:
                words = TypingWord.objects.filter(
                    dictionary_id=dictionary.id,
                    chapter=chapter
                )[:3]
                
                word_list = [f"{word.word}({word.translation})" for word in words]
                print(f"     示例: {', '.join(word_list)}")
                
                if word_count > 3:
                    print(f"     ... 还有 {word_count - 3} 个单词")
        
        print()
    
    print("=" * 80)
    print("💡 分析结果:")
    print("1. 前端硬编码每章25个单词")
    print("2. 实际数据库中每章单词数量可能不同")
    print("3. 需要修复前端逻辑，实时获取每章实际单词数量")


def check_specific_dictionary(dictionary_name):
    """检查特定词典的详细信息"""
    try:
        dictionary = Dictionary.objects.get(name=dictionary_name, is_deleted=False)
        print(f"\n🔍 详细检查词典: {dictionary.name}")
        print("=" * 60)
        
        # 检查每章的单词
        for chapter in range(1, dictionary.chapter_count + 1):
            words = TypingWord.objects.filter(
                dictionary_id=dictionary.id,
                chapter=chapter
            )
            
            print(f"\n第{chapter}章:")
            print(f"  单词数量: {words.count()}")
            
            if words.exists():
                print("  单词列表:")
                for i, word in enumerate(words, 1):
                    print(f"    {i}. {word.word} - {word.translation}")
                    if i >= 5:  # 只显示前5个
                        remaining = words.count() - 5
                        if remaining > 0:
                            print(f"    ... 还有 {remaining} 个单词")
                        break
        
    except Dictionary.DoesNotExist:
        print(f"❌ 词典 '{dictionary_name}' 不存在")


if __name__ == "__main__":
    print("数据库章节单词数量检查脚本")
    print("=" * 80)
    
    # 检查所有词典
    check_chapter_word_counts()
    
    # 详细检查测试词典
    print("\n" + "=" * 80)
    check_specific_dictionary("测试词典")
    
    print("\n✅ 检查完成！")
