#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.english.models import Dictionary, TypingWord

def check_database_status():
    """检查数据库状态"""
    print("=== 数据库状态检查 ===")
    
    # 检查字典
    dictionaries = Dictionary.objects.all()
    print(f"字典总数: {dictionaries.count()}")
    
    # 检查单词
    words = TypingWord.objects.all()
    print(f"单词总数: {words.count()}")
    
    # 检查TOEFL字典
    toefl_dict = Dictionary.objects.filter(category='TOEFL').first()
    if toefl_dict:
        print(f"TOEFL字典: {toefl_dict.name} (ID: {toefl_dict.id})")
        toefl_words = TypingWord.objects.filter(dictionary=toefl_dict)
        print(f"TOEFL单词数: {toefl_words.count()}")
        
        # 检查章节
        chapters = toefl_words.values_list('chapter', flat=True).distinct()
        print(f"TOEFL章节: {list(chapters)}")
        
        # 检查第1章
        chapter1_words = toefl_words.filter(chapter=1)
        print(f"TOEFL第1章单词数: {chapter1_words.count()}")
    else:
        print("TOEFL字典不存在")
    
    # 检查CET4字典
    cet4_dict = Dictionary.objects.filter(category='CET4').first()
    if cet4_dict:
        print(f"CET4字典: {cet4_dict.name} (ID: {cet4_dict.id})")
        cet4_words = TypingWord.objects.filter(dictionary=cet4_dict)
        print(f"CET4单词数: {cet4_words.count()}")
    else:
        print("CET4字典不存在")

if __name__ == "__main__":
    check_database_status()
