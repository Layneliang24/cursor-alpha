#!/usr/bin/env python
import os
import sys
import json
import django
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.english.models import Dictionary, TypingWord

def backup_database():
    """备份数据库中的字典和单词数据"""
    print("=== 开始备份数据库 ===")
    
    # 备份字典数据
    dictionaries = Dictionary.objects.all()
    dict_data = []
    for dict_obj in dictionaries:
        dict_data.append({
            'id': dict_obj.id,
            'name': dict_obj.name,
            'category': dict_obj.category,
            'description': dict_obj.description,
            'language': dict_obj.language,
            'total_words': dict_obj.total_words,
            'chapter_count': dict_obj.chapter_count,
            'is_active': dict_obj.is_active,
            'source_file': dict_obj.source_file
        })
    
    # 备份单词数据
    words = TypingWord.objects.all()
    word_data = []
    for word_obj in words:
        word_data.append({
            'id': word_obj.id,
            'word': word_obj.word,
            'translation': word_obj.translation,
            'phonetic': word_obj.phonetic,
            'difficulty': word_obj.difficulty,
            'chapter': word_obj.chapter,
            'frequency': word_obj.frequency,
            'dictionary_id': word_obj.dictionary.id
        })
    
    # 创建备份数据
    backup = {
        'timestamp': datetime.now().isoformat(),
        'dictionaries': dict_data,
        'words': word_data
    }
    
    # 保存到文件
    backup_file = f'database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup, f, ensure_ascii=False, indent=2)
    
    print(f"备份完成: {backup_file}")
    print(f"字典数量: {len(dict_data)}")
    print(f"单词数量: {len(word_data)}")
    
    return backup_file

def restore_database(backup_file):
    """从备份文件恢复数据库"""
    print(f"=== 开始恢复数据库: {backup_file} ===")
    
    with open(backup_file, 'r', encoding='utf-8') as f:
        backup = json.load(f)
    
    # 清空现有数据
    TypingWord.objects.all().delete()
    Dictionary.objects.all().delete()
    
    # 恢复字典数据
    for dict_data in backup['dictionaries']:
        Dictionary.objects.create(**dict_data)
    
    # 恢复单词数据
    for word_data in backup['words']:
        TypingWord.objects.create(**word_data)
    
    print("数据库恢复完成")
    print(f"恢复字典数量: {len(backup['dictionaries'])}")
    print(f"恢复单词数量: {len(backup['words'])}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'restore':
        if len(sys.argv) > 2:
            restore_database(sys.argv[2])
        else:
            print("请指定备份文件路径")
    else:
        backup_database()
