from django.core.management.base import BaseCommand
from django.db import transaction
import json
import os
from apps.english.models import Dictionary, TypingWord


class Command(BaseCommand):
    help = '从Qwerty Learner项目导入词库数据（支持词库管理和章节功能）'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dicts-path',
            type=str,
            default='frontend/public/dicts',
            help='词库文件路径'
        )
        parser.add_argument(
            '--dicts',
            nargs='+',
            default=[
                'CET4_T', 'CET6_T', 'TOEFL_3_T', 'GRE_3_T', 'IELTS_3_T', 
                'SAT_3_T', 'TOEIC', 'kaoyan', 'kaoyan_2024', 'kaoyanshanguo_2023',
                'top2000words', 'voa', 'nce-new-1', 'nce-new-2', 'nce-new-3', 'nce-new-4'
            ],
            help='要导入的词库列表'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='试运行模式，不实际导入数据'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='清除现有词库数据'
        )
    
    def handle(self, *args, **options):
        dicts_path = options['dicts_path']
        dicts = options['dicts']
        dry_run = options['dry_run']
        clear_existing = options['clear_existing']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('试运行模式，不会实际导入数据'))
        
        # 检查词库路径是否存在
        if not os.path.exists(dicts_path):
            self.stdout.write(
                self.style.ERROR(f'词库路径不存在: {dicts_path}')
            )
            return
        
        # 清除现有数据
        if clear_existing and not dry_run:
            self.stdout.write('清除现有词库数据...')
            TypingWord.objects.all().delete()
            Dictionary.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('现有数据已清除'))
        
        # 定义词库配置
        dict_configs = {
            'CET4_T': {
                'name': 'CET-4',
                'description': '大学英语四级词库',
                'category': '中国考试',
                'language': 'en',
                'difficulty': 'intermediate'
            },
            'CET6_T': {
                'name': 'CET-6',
                'description': '大学英语六级词库',
                'category': '中国考试',
                'language': 'en',
                'difficulty': 'intermediate'
            },
            'TOEFL_3_T': {
                'name': 'TOEFL',
                'description': '托福考试词库',
                'category': '国际考试',
                'language': 'en',
                'difficulty': 'advanced'
            },
            'GRE_3_T': {
                'name': 'GRE',
                'description': 'GRE考试词库',
                'category': '国际考试',
                'language': 'en',
                'difficulty': 'advanced'
            },
            'IELTS_3_T': {
                'name': 'IELTS',
                'description': '雅思考试词库',
                'category': '国际考试',
                'language': 'en',
                'difficulty': 'advanced'
            },
            'SAT_3_T': {
                'name': 'SAT',
                'description': 'SAT考试词库',
                'category': '国际考试',
                'language': 'en',
                'difficulty': 'advanced'
            },
            'TOEIC': {
                'name': 'TOEIC',
                'description': '托业考试词库',
                'category': '国际考试',
                'language': 'en',
                'difficulty': 'intermediate'
            },
            'kaoyan': {
                'name': '考研英语',
                'description': '研究生英语入学考试词库',
                'category': '中国考试',
                'language': 'en',
                'difficulty': 'advanced'
            },
            'kaoyan_2024': {
                'name': '考研英语 2024',
                'description': '研究生英语入学考试词库 2024',
                'category': '中国考试',
                'language': 'en',
                'difficulty': 'advanced'
            },
            'kaoyanshanguo_2023': {
                'name': '考研闪过 2023',
                'description': '高中低频词2023',
                'category': '中国考试',
                'language': 'en',
                'difficulty': 'advanced'
            },
            'top2000words': {
                'name': 'Top 2000 Words',
                'description': '英语高频词汇2000词',
                'category': '基础词汇',
                'language': 'en',
                'difficulty': 'beginner'
            },
            'voa': {
                'name': 'VOA',
                'description': 'VOA英语词汇',
                'category': '新闻英语',
                'language': 'en',
                'difficulty': 'intermediate'
            },
            'nce-new-1': {
                'name': '新概念英语 第一册',
                'description': '新概念英语第一册词汇',
                'category': '教材词汇',
                'language': 'en',
                'difficulty': 'beginner'
            },
            'nce-new-2': {
                'name': '新概念英语 第二册',
                'description': '新概念英语第二册词汇',
                'category': '教材词汇',
                'language': 'en',
                'difficulty': 'intermediate'
            },
            'nce-new-3': {
                'name': '新概念英语 第三册',
                'description': '新概念英语第三册词汇',
                'category': '教材词汇',
                'language': 'en',
                'difficulty': 'intermediate'
            },
            'nce-new-4': {
                'name': '新概念英语 第四册',
                'description': '新概念英语第四册词汇',
                'category': '教材词汇',
                'language': 'en',
                'difficulty': 'advanced'
            }
        }
        
        total_imported = 0
        total_skipped = 0
        
        for dict_id in dicts:
            dict_file = os.path.join(dicts_path, f'{dict_id}.json')
            if os.path.exists(dict_file):
                if dict_id in dict_configs:
                    imported, skipped = self.import_dict_file(
                        dict_file, dict_id, dict_configs[dict_id], dry_run
                    )
                    total_imported += imported
                    total_skipped += skipped
                else:
                    self.stdout.write(
                        self.style.WARNING(f'词库 {dict_id} 未配置，跳过')
                    )
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
    
    def import_dict_file(self, file_path, dict_id, config, dry_run=False):
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
        
        self.stdout.write(f'开始导入 {config["name"]} 词库，共 {len(words_data)} 个单词...')
        
        # 创建或获取词库
        if not dry_run:
            dictionary, created = Dictionary.objects.get_or_create(
                name=config['name'],
                defaults={
                    'description': config['description'],
                    'category': config['category'],
                    'language': config['language'],
                    'total_words': len(words_data),
                    'source_file': os.path.basename(file_path)
                }
            )
            if created:
                self.stdout.write(f'创建新词库: {dictionary.name}')
            else:
                self.stdout.write(f'使用现有词库: {dictionary.name}')
        else:
            dictionary = None
        
        # 计算章节数（每章25个单词，让用户练习更轻松）
        words_per_chapter = 25
        chapter_count = (len(words_data) + words_per_chapter - 1) // words_per_chapter
        
        if not dry_run:
            dictionary.chapter_count = chapter_count
            dictionary.total_words = len(words_data)
            dictionary.save()
        
        for i, word_data in enumerate(words_data, 1):
            try:
                # 检查必要字段
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
                
                # 处理翻译字段
                translation = word_data.get('trans', '')
                if isinstance(translation, list):
                    translation = '; '.join(translation)
                elif not isinstance(translation, str):
                    translation = str(translation)
                
                # 处理音标字段
                phonetic = word_data.get('usphone', '') or word_data.get('ukphone', '')
                
                # 计算章节
                chapter = ((i - 1) // words_per_chapter) + 1
                
                # 准备数据
                word_dict = {
                    'word': word_text,
                    'translation': translation,
                    'phonetic': phonetic,
                    'dictionary': dictionary,
                    'chapter': chapter,
                    'difficulty': self.determine_difficulty(word_data, config['difficulty']),
                    'frequency': word_data.get('frequency', 0)
                }
                
                if not dry_run:
                    # 使用事务确保数据一致性
                    with transaction.atomic():
                        word, created = TypingWord.objects.get_or_create(
                            word=word_text,
                            dictionary=dictionary,
                            defaults=word_dict
                        )
                        if created:
                            imported_count += 1
                        else:
                            # 更新现有记录
                            for key, value in word_dict.items():
                                if key not in ['word', 'dictionary']:  # 不更新word和dictionary字段
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
                f'成功导入 {config["name"]} 词库: {imported_count} 个新单词，跳过: {skipped_count} 个，章节数: {chapter_count}'
            )
        )
        
        return imported_count, skipped_count
    
    def determine_difficulty(self, word_data, base_difficulty):
        """根据单词特征确定难度"""
        word = word_data.get('name', '')
        frequency = word_data.get('frequency', 0)
        
        # 根据单词长度和词频调整
        word_length = len(word)
        
        if word_length <= 4 or frequency > 1000:
            return 'beginner'
        elif word_length <= 8 or frequency > 500:
            return 'intermediate'
        else:
            return 'advanced'
