#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Django管理命令：生成OpenAPI规范
"""

import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import extend_schema
from drf_spectacular.generators import SchemaGenerator
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory


class Command(BaseCommand):
    help = '生成OpenAPI规范文件'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='generated_openapi.json',
            help='输出文件路径 (默认: generated_openapi.json)'
        )
        parser.add_argument(
            '--format',
            choices=['json', 'yaml'],
            default='json',
            help='输出格式 (默认: json)'
        )
        parser.add_argument(
            '--pretty',
            action='store_true',
            help='格式化输出'
        )
    
    def handle(self, *args, **options):
        output_file = options['output']
        output_format = options['format']
        pretty = options['pretty']
        
        try:
            # 生成OpenAPI规范
            self.stdout.write('正在生成OpenAPI规范...')
            
            generator = SchemaGenerator(
                title=getattr(settings, 'SPECTACULAR_SETTINGS', {}).get('TITLE', 'API'),
                description=getattr(settings, 'SPECTACULAR_SETTINGS', {}).get('DESCRIPTION', ''),
                version=getattr(settings, 'SPECTACULAR_SETTINGS', {}).get('VERSION', '1.0.0'),
            )
            
            # 创建一个虚拟请求
            factory = APIRequestFactory()
            request = factory.get('/')
            
            # 添加必要的属性
            from django.contrib.auth.models import AnonymousUser
            request.user = AnonymousUser()
            request.auth = None
            
            # 生成规范
            schema = generator.get_schema(request=request, public=True)
            
            # 确保输出目录存在
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            if output_format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    if pretty:
                        json.dump(schema, f, indent=2, ensure_ascii=False)
                    else:
                        json.dump(schema, f, ensure_ascii=False)
            elif output_format == 'yaml':
                import yaml
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(schema, f, default_flow_style=False, allow_unicode=True)
            
            self.stdout.write(
                self.style.SUCCESS(f'OpenAPI规范已生成: {output_path.absolute()}')
            )
            
            # 显示统计信息
            paths_count = len(schema.get('paths', {}))
            components_count = len(schema.get('components', {}).get('schemas', {}))
            
            self.stdout.write('统计信息:')
            self.stdout.write(f'  - API路径数量: {paths_count}')
            self.stdout.write(f'  - 组件数量: {components_count}')
            
        except Exception as e:
            raise CommandError(f'生成OpenAPI规范失败: {e}')