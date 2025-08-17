from django.core.management.base import BaseCommand
from django.db import transaction
import json
import os
from apps.english.models import TypingWord


class Command(BaseCommand):
    help = '从Qwerty Learner项目导入词库数据'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dicts-path',
            type=str,
            default='../qwerty-learner/public/dicts',
            help='Qwerty Learner词库文件路径'
        )
        parser.add_argument(
            '--categories',
            nargs='+',
            default=['CET4_T', 'CET6_T', 'TOEFL_3_T', 'GRE_3_T', 'IELTS_3_T', 'SAT_3_T', 'TOEIC'],
            help='要导入的词库类别'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行模式，不实际导入数据'
        )
    
    def handle(self, *args, **options):
        dicts_path = options['dicts_path']
        categories = options['categories']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('试运行模式，不会实际导入数据'))
        
        # 检查词库路径是否存在
        if not os.path.exists(dicts_path):
            self.stdout.write(
                self.style.ERROR(f'词库路径不存在: {dicts_path}')
            )
            return
        
        total_imported = 0
        total_skipped = 0
        
        for category in categories:
            dict_file = os.path.join(dicts_path, f'{category}.json')
            if os.path.exists(dict_file):
                imported, skipped = self.import_dict_file(dict_file, category, dry_run)
                total_imported += imported
                total_skipped += skipped
            else:
                self.stdout.write(
                    self.style.WARNING(f'词库文件不存在: {dict_file}')
                )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'导入完成！总计导入: {total_imported} 个单词，跳过: {total_skipped} 个'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'试运行完成！将导入: {total_imported} 个单词，跳过: {total_skipped} 个'
                )
            )
    
    def import_dict_file(self, file_path, category, dry_run=False):
        """导入单个词库文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                words_data = json.load(f)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'读取文件失败 {file_path}: {str(e)}')
            )
            return 0, 0
        
        imported_count = 0
        skipped_count = 0
        
        self.stdout.write(f'开始导入 {category} 词库，共 {len(words_data)} 个单词...')
        
        for i, word_data in enumerate(words_data, 1):
            try:
                # 检查必要字段 - 适配Qwerty Learner的数据结构
                if 'name' not in word_data:
                    self.stdout.write(
                        self.style.WARNING(f'跳过第 {i} 条数据：缺少name字段')
                    )
                    skipped_count += 1
                    continue
                
                word_text = word_data['name'].strip()
                if not word_text:
                    skipped_count += 1
                    continue
                
                # 处理翻译字段 - 可能是数组或字符串
                translation = word_data.get('trans', '')
                if isinstance(translation, list):
                    translation = '; '.join(translation)
                elif not isinstance(translation, str):
                    translation = str(translation)
                
                # 处理音标字段 - 优先使用美式音标
                phonetic = word_data.get('usphone', '') or word_data.get('ukphone', '')
                
                # 准备数据
                word_dict = {
                    'word': word_text,
                    'translation': translation,
                    'phonetic': phonetic,
                    'category': category,
                    'difficulty': self.determine_difficulty(word_data, category),
                    'frequency': word_data.get('frequency', 0)
                }
                
                if not dry_run:
                    # 使用事务确保数据一致性
                    with transaction.atomic():
                        word, created = TypingWord.objects.get_or_create(
                            word=word_text,
                            defaults=word_dict
                        )
                        if created:
                            imported_count += 1
                        else:
                            # 更新现有记录
                            for key, value in word_dict.items():
                                if key != 'word':  # 不更新word字段
                                    setattr(word, key, value)
                            word.save()
                            skipped_count += 1
                else:
                    # 试运行模式，只检查是否存在
                    if TypingWord.objects.filter(word=word_text).exists():
                        skipped_count += 1
                    else:
                        imported_count += 1
                
                # 显示进度
                if i % 100 == 0:
                    self.stdout.write(f'已处理 {i}/{len(words_data)} 个单词...')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'处理第 {i} 条数据时出错: {str(e)}')
                )
                skipped_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'成功导入 {category} 词库: {imported_count} 个新单词，跳过: {skipped_count} 个'
            )
        )
        
        return imported_count, skipped_count
    
    def determine_difficulty(self, word_data, category):
        """根据单词特征确定难度"""
        word = word_data.get('name', '')
        frequency = word_data.get('frequency', 0)
        
        # 根据词库类别判断难度
        if category in ['CET4_T', 'TOEIC']:
            base_difficulty = 'beginner'
        elif category in ['CET6_T', 'IELTS_3_T']:
            base_difficulty = 'intermediate'
        elif category in ['TOEFL_3_T', 'GRE_3_T', 'SAT_3_T']:
            base_difficulty = 'advanced'
        else:
            base_difficulty = 'intermediate'
        
        # 根据单词长度和词频调整
        word_length = len(word)
        
        if word_length <= 4 or frequency > 1000:
            return 'beginner'
        elif word_length <= 8 or frequency > 500:
            return 'intermediate'
        else:
            return 'advanced'
