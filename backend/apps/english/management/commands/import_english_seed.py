import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.english.models import (
    Word, WordCategory, WordCategoryLink, WordTag, WordTagLink, WordExample,
    WordRelation, News
)
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Import english seed data from tests/fixtures/english_seed.json'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='tests/fixtures/english_seed.json')

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = Path(options['file'])
        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            return
        data = json.loads(file_path.read_text(encoding='utf-8'))

        # words
        words_map = {}
        for w in data.get('words', []):
            obj, _ = Word.objects.update_or_create(
                word=w['word'],
                defaults={
                    'phonetic': w.get('phonetic'),
                    'part_of_speech': w.get('part_of_speech'),
                    'definition': w.get('definition'),
                    'example': w.get('example'),
                    'difficulty_level': w.get('difficulty_level', 'beginner'),
                    'frequency_rank': w.get('frequency_rank', 0),
                    'category_hint': w.get('category_hint'),
                    'source_url': w.get('source_url'),
                    'source_api': w.get('source_api'),
                    'license': w.get('license'),
                    'quality_score': w.get('quality_score', 0.0),
                }
            )
            words_map[w.get('id', obj.id)] = obj
        self.stdout.write(self.style.SUCCESS(f'Imported words: {len(words_map)}'))

        # categories
        cats_map = {}
        for c in data.get('categories', []):
            obj, _ = WordCategory.objects.update_or_create(name=c['name'])
            cats_map[c.get('id', obj.id)] = obj
        # links word-category
        for link in data.get('word_category_links', []):
            w = words_map.get(link['word_id'])
            cat = cats_map.get(link['category_id'])
            if w and cat:
                WordCategoryLink.objects.get_or_create(word=w, category=cat)

        # tags
        tags_map = {}
        for t in data.get('tags', []):
            obj, _ = WordTag.objects.update_or_create(name=t['name'])
            tags_map[t.get('id', obj.id)] = obj
        # links word-tag
        for link in data.get('word_tag_links', []):
            w = words_map.get(link['word_id'])
            tg = tags_map.get(link['tag_id'])
            if w and tg:
                WordTagLink.objects.get_or_create(word=w, tag=tg)

        # examples
        for ex in data.get('examples', []):
            w = words_map.get(ex['word_id'])
            if w:
                WordExample.objects.get_or_create(
                    word=w, sentence=ex['sentence'],
                    defaults={
                        'translation': ex.get('translation'),
                        'source_url': ex.get('source_url'),
                        'quality_score': ex.get('quality_score', 0.0)
                    }
                )

        # relations
        for rel in data.get('relations', []):
            w = words_map.get(rel['word_id'])
            rw = words_map.get(rel['related_word_id'])
            if w and rw:
                WordRelation.objects.get_or_create(
                    word=w, related_word=rw, relation_type=rel['relation_type'],
                    defaults={'note': rel.get('note')}
                )

        # news
        for n in data.get('news', []):
            News.objects.update_or_create(
                title=n['title'],
                defaults={
                    'summary': n.get('summary'),
                    'content': n.get('content'),
                    'category': n.get('category'),
                    'difficulty_level': n.get('difficulty_level', 'intermediate'),
                    'publish_date': n.get('publish_date'),
                    'word_count': n.get('word_count', 0),
                    'source': n.get('source'),
                    'source_url': n.get('source_url'),
                    'license': n.get('license'),
                    'quality_score': n.get('quality_score', 0.0)
                }
            )

        self.stdout.write(self.style.SUCCESS('English seed data import finished.'))
