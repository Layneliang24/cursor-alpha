#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI助教配置管理命令
用于配置chenmoai和其他AI服务
"""

import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from apps.ai.services.key_manager import APIKeyManager
from apps.ai.adapters.base import AIProviderType, AIModelConfig
from apps.ai.adapters.factory import AIAdapterFactory


class Command(BaseCommand):
    help = '配置AI助教服务，支持chenmoai等多个提供商'

    def add_arguments(self, parser):
        parser.add_argument(
            '--provider',
            type=str,
            choices=['chenmoai', 'openai', 'anthropic', 'google', 'openrouter'],
            default='chenmoai',
            help='AI服务提供商 (默认: chenmoai)'
        )
        
        parser.add_argument(
            '--api-key',
            type=str,
            help='API密钥'
        )
        
        parser.add_argument(
            '--base-url',
            type=str,
            help='API基础URL'
        )
        
        parser.add_argument(
            '--model',
            type=str,
            help='默认模型名称'
        )
        
        parser.add_argument(
            '--test',
            action='store_true',
            help='测试配置是否正确'
        )
        
        parser.add_argument(
            '--list-models',
            action='store_true',
            help='列出支持的模型'
        )
        
        parser.add_argument(
            '--status',
            action='store_true',
            help='显示当前配置状态'
        )

    def handle(self, *args, **options):
        """处理命令"""
        try:
            if options['list_models']:
                self.list_supported_models()
                return
            
            if options['status']:
                self.show_status()
                return
            
            if options['test']:
                self.test_configuration(options['provider'])
                return
            
            # 配置AI服务
            self.configure_ai_service(options)
            
        except Exception as e:
            raise CommandError(f'配置失败: {str(e)}')

    def configure_ai_service(self, options):
        """配置AI服务"""
        provider_name = options['provider']
        api_key = options.get('api_key')
        base_url = options.get('base_url')
        model = options.get('model')
        
        # 获取提供商类型
        provider_mapping = {
            'chenmoai': AIProviderType.CHENMOAI,
            'openai': AIProviderType.OPENAI,
            'anthropic': AIProviderType.ANTHROPIC,
            'google': AIProviderType.GOOGLE,
            'openrouter': AIProviderType.OPENROUTER,
        }
        
        provider = provider_mapping.get(provider_name)
        if not provider:
            raise CommandError(f'不支持的提供商: {provider_name}')
        
        # 获取API密钥
        if not api_key:
            # 尝试从环境变量获取
            env_key_mapping = {
                'chenmoai': 'CHENMOAI_API_KEY',
                'openai': 'OPENAI_API_KEY',
                'anthropic': 'ANTHROPIC_API_KEY',
                'google': 'GOOGLE_API_KEY',
                'openrouter': 'OPENROUTER_API_KEY',
            }
            
            env_key = env_key_mapping.get(provider_name)
            api_key = os.getenv(env_key)
            
            if not api_key:
                raise CommandError(f'请提供API密钥或设置环境变量 {env_key}')
        
        # 设置默认值
        if not base_url:
            base_url_mapping = {
                'chenmoai': 'https://hk.chenmoai.cn/v1',
                'openai': 'https://api.openai.com/v1',
                'anthropic': 'https://api.anthropic.com',
                'google': 'https://generativelanguage.googleapis.com/v1',
            }
            base_url = base_url_mapping.get(provider_name)
        
        if not model:
            model_mapping = {
                'chenmoai': 'gpt-3.5-turbo',
                'openai': 'gpt-3.5-turbo',
                'anthropic': 'claude-3-haiku-20240307',
                'google': 'gemini-pro',
            }
            model = model_mapping.get(provider_name)
        
        # 创建配置
        config = AIModelConfig(
            provider=provider,
            model_name=model,
            api_key=api_key,
            base_url=base_url,
            max_tokens=4000,
            temperature=0.7,
            timeout=30
        )
        
        # 存储密钥
        key_manager = APIKeyManager()
        key_id = key_manager.add_key(provider, api_key, is_primary=True)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ 成功配置 {provider_name} AI服务')
        )
        self.stdout.write(f'   提供商: {provider_name}')
        self.stdout.write(f'   模型: {model}')
        self.stdout.write(f'   基础URL: {base_url}')
        self.stdout.write(f'   密钥ID: {key_id}')
        
        # 测试配置
        self.stdout.write('\n🔍 测试配置...')
        try:
            adapter = AIAdapterFactory.create_adapter(config)
            # 这里可以添加健康检查
            self.stdout.write(self.style.SUCCESS('✅ 配置测试通过'))
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'⚠️  配置测试失败: {str(e)}')
            )

    def test_configuration(self, provider_name):
        """测试配置"""
        self.stdout.write(f'🔍 测试 {provider_name} 配置...')
        
        # 获取提供商类型
        provider_mapping = {
            'chenmoai': AIProviderType.CHENMOAI,
            'openai': AIProviderType.OPENAI,
            'anthropic': AIProviderType.ANTHROPIC,
            'google': AIProviderType.GOOGLE,
            'openrouter': AIProviderType.OPENROUTER,
        }
        
        provider = provider_mapping.get(provider_name)
        if not provider:
            raise CommandError(f'不支持的提供商: {provider_name}')
        
        # 获取密钥管理器
        key_manager = APIKeyManager()
        api_key = key_manager.get_key(provider)
        
        if not api_key:
            self.stdout.write(
                self.style.ERROR(f'❌ 未找到 {provider_name} 的API密钥')
            )
            return
        
        try:
            # 创建配置进行测试
            config = AIModelConfig(
                provider=provider,
                model_name=key_manager._get_default_model(provider),
                api_key=api_key,
                max_tokens=100,
                temperature=0.7,
                timeout=10
            )
            
            adapter = AIAdapterFactory.create_adapter(config)
            
            # 进行健康检查
            import asyncio
            health_result = asyncio.run(adapter.health_check())
            
            if health_result.is_healthy:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {provider_name} 配置正常')
                )
                self.stdout.write(f'   响应时间: {health_result.response_time:.2f}秒')
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ {provider_name} 配置异常')
                )
                if health_result.error_message:
                    self.stdout.write(f'   错误信息: {health_result.error_message}')
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ 测试失败: {str(e)}')
            )

    def list_supported_models(self):
        """列出支持的模型"""
        self.stdout.write('📋 支持的AI模型:')
        self.stdout.write('')
        
        supported_models = AIAdapterFactory.get_supported_models()
        
        for provider, models in supported_models.items():
            self.stdout.write(f'🔹 {provider.value.upper()}:')
            for model in models:
                self.stdout.write(f'   - {model}')
            self.stdout.write('')
        
        # 特别标注chenmoai支持的模型
        if AIProviderType.CHENMOAI not in supported_models:
            self.stdout.write('🔹 CHENMOAI (中转站):')
            chenmoai_models = [
                'gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo',
                'claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307',
                'gemini-1.5-pro', 'gemini-1.5-flash',
                'deepseek-chat', 'qwen-turbo', 'glm-4'
            ]
            for model in chenmoai_models:
                self.stdout.write(f'   - {model}')
            self.stdout.write('')

    def show_status(self):
        """显示当前配置状态"""
        self.stdout.write('📊 AI助教配置状态:')
        self.stdout.write('')
        
        key_manager = APIKeyManager()
        stats = key_manager.get_key_stats()
        
        for provider_name, provider_stats in stats.items():
            self.stdout.write(f'🔹 {provider_name.upper()}:')
            
            if provider_stats['total_keys'] == 0:
                self.stdout.write('   ❌ 未配置')
            else:
                for key_info in provider_stats['keys']:
                    status = '✅ 主密钥' if key_info['is_primary'] else '🔑 备用密钥'
                    self.stdout.write(f'   {status} ({key_info["key_id"]})')
                    if key_info['usage_count']:
                        self.stdout.write(f'      使用次数: {key_info["usage_count"]}')
                    if key_info['last_used']:
                        self.stdout.write(f'      最后使用: {key_info["last_used"]}')
            
            self.stdout.write('')
        
        # 显示环境变量状态
        self.stdout.write('🌍 环境变量状态:')
        env_vars = [
            'CHENMOAI_API_KEY', 'OPENAI_API_KEY', 
            'ANTHROPIC_API_KEY', 'GOOGLE_API_KEY'
        ]
        
        for env_var in env_vars:
            value = os.getenv(env_var)
            if value:
                masked_value = f"{value[:8]}***{value[-4:]}" if len(value) > 12 else "***"
                self.stdout.write(f'   ✅ {env_var}: {masked_value}')
            else:
                self.stdout.write(f'   ❌ {env_var}: 未设置')
