"""
初始化系统提示模板管理命令
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.ai.models import PromptTemplate

User = get_user_model()


class Command(BaseCommand):
    help = '初始化系统提示模板'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制重新创建模板（删除现有模板）',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        if force:
            # 删除现有系统模板
            deleted_count = PromptTemplate.objects.filter(is_system=True).count()
            PromptTemplate.objects.filter(is_system=True).delete()
            self.stdout.write(
                self.style.WARNING(f'已删除 {deleted_count} 个现有系统模板')
            )
        
        # 获取系统用户（如果没有则创建一个）
        system_user, created = User.objects.get_or_create(
            username='system',
            defaults={
                'email': 'system@example.com',
                'is_active': True,
                'is_staff': False,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('创建了系统用户')
            )
        
        # 定义系统模板
        templates = [
            {
                'name': '通用助手',
                'category': 'general',
                'description': '通用AI助手，友好且有帮助',
                'content': '你是一个有用、准确且友好的AI助手。请用清晰、简洁的方式回答用户的问题，并在需要时提供详细的解释。如果不确定答案，请诚实地说明。',
            },
            {
                'name': '代码助手',
                'category': 'coding',
                'description': '专业的编程助手',
                'content': '你是一个专业的编程助手。请帮助用户解决编程问题，提供清晰的代码示例，解释最佳实践，并在必要时提供调试建议。请确保代码的可读性和效率。',
            },
            {
                'name': '写作助手',
                'category': 'writing',
                'description': '专业的写作和编辑助手',
                'content': '你是一个专业的写作助手。请帮助用户改进文本的清晰度、流畅性和表达力。提供建设性的反馈，纠正语法错误，并建议更好的表达方式。保持原文的语调和意图。',
            },
            {
                'name': '分析助手',
                'category': 'analysis',
                'description': '数据分析和问题解决专家',
                'content': '你是一个专业的分析助手。请帮助用户分析数据、识别模式、得出结论，并提供基于证据的见解。使用逻辑推理，提供清晰的分析步骤和结论。',
            },
            {
                'name': '翻译助手',
                'category': 'translation',
                'description': '专业的多语言翻译助手',
                'content': '你是一个专业的翻译助手。请提供准确、自然的翻译，保持原文的语调、风格和含义。如果遇到文化特定的表达，请提供适当的解释或等效表达。',
            },
            {
                'name': '创意助手',
                'category': 'creative',
                'description': '创意写作和头脑风暴助手',
                'content': '你是一个富有创意的助手。请帮助用户进行头脑风暴、创意写作、故事构思和创新思考。提供原创的想法，激发用户的创造力，并鼓励探索不同的可能性。',
            },
            {
                'name': '简洁回答',
                'category': 'general',
                'description': '提供简洁明了的回答',
                'content': '请提供简洁、直接的回答。避免冗长的解释，除非用户明确要求详细信息。重点关注核心问题和关键信息。',
            },
            {
                'name': '详细解释',
                'category': 'general',
                'description': '提供详细的解释和分析',
                'content': '请提供详细、全面的回答。包括背景信息、步骤说明、示例和相关考虑因素。帮助用户深入理解主题。',
            },
        ]
        
        created_count = 0
        for template_data in templates:
            template, created = PromptTemplate.objects.get_or_create(
                name=template_data['name'],
                is_system=True,
                defaults={
                    'category': template_data['category'],
                    'description': template_data['description'],
                    'content': template_data['content'],
                    'is_public': True,
                    'is_active': True,
                    'created_by': system_user,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'创建模板: {template.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'模板已存在: {template.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'初始化完成！共创建了 {created_count} 个系统模板。'
            )
        )
