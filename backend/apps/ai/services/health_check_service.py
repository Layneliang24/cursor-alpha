"""
健康检查服务
负责检查AI提供商的健康状态
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.core.cache import cache
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..models import AIProvider

logger = logging.getLogger(__name__)


class HealthCheckService:
    """健康检查服务"""
    
    def __init__(self):
        self.timeout = 30  # 30秒超时
        self.cache_timeout = 300  # 5分钟缓存
        self.max_workers = 5  # 最大并发检查数
    
    def check_provider(self, provider: AIProvider) -> Dict[str, Any]:
        """检查单个提供商的健康状态"""
        start_time = time.time()
        
        try:
            # 根据提供商类型执行不同的健康检查
            if provider.provider_type == 'openai':
                result = self._check_openai_provider(provider)
            elif provider.provider_type == 'anthropic':
                result = self._check_anthropic_provider(provider)
            elif provider.provider_type == 'google':
                result = self._check_google_provider(provider)
            elif provider.provider_type == 'azure':
                result = self._check_azure_provider(provider)
            elif provider.provider_type == 'local':
                result = self._check_local_provider(provider)
            elif provider.provider_type in ['chenmoai', 'openrouter', 'siliconflow']:
                result = self._check_openai_compatible_provider(provider)
            else:
                result = self._check_generic_provider(provider)
            
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            result['response_time'] = round(response_time, 2)
            
            # 更新提供商健康状态
            provider.update_health_status(
                is_healthy=result['is_healthy'],
                response_time=response_time / 1000  # 转换为秒
            )
            
            # 缓存结果
            cache_key = f"health_check_{provider.id}"
            cache.set(cache_key, result, self.cache_timeout)
            
            logger.info(
                f"提供商 {provider.display_name} 健康检查完成，"
                f"状态: {'健康' if result['is_healthy'] else '不健康'}，"
                f"响应时间: {response_time:.2f}ms"
            )
            
            return result
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"检查提供商 {provider.display_name} 健康状态失败: {error_message}")
            
            # 更新为不健康状态
            provider.update_health_status(False)
            
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': False,
                'error': error_message,
                'response_time': (time.time() - start_time) * 1000,
                'checked_at': timezone.now().isoformat()
            }
    
    def check_all_providers(self) -> List[Dict[str, Any]]:
        """并发检查所有活跃提供商的健康状态"""
        providers = AIProvider.objects.filter(is_active=True)
        results = []
        
        logger.info(f"开始检查 {providers.count()} 个提供商的健康状态")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有检查任务
            future_to_provider = {
                executor.submit(self.check_provider, provider): provider
                for provider in providers
            }
            
            # 收集结果
            for future in as_completed(future_to_provider):
                provider = future_to_provider[future]
                try:
                    result = future.result(timeout=self.timeout)
                    results.append(result)
                except Exception as e:
                    logger.error(f"检查提供商 {provider.display_name} 时发生异常: {str(e)}")
                    results.append({
                        'provider_id': provider.id,
                        'provider_name': provider.display_name,
                        'is_healthy': False,
                        'error': f'检查超时或异常: {str(e)}',
                        'response_time': self.timeout * 1000,
                        'checked_at': timezone.now().isoformat()
                    })
        
        # 统计结果
        healthy_count = sum(1 for r in results if r['is_healthy'])
        logger.info(
            f"健康检查完成，{healthy_count}/{len(results)} 个提供商健康"
        )
        
        return results
    
    def get_cached_health_status(self, provider: AIProvider) -> Optional[Dict[str, Any]]:
        """获取缓存的健康状态"""
        cache_key = f"health_check_{provider.id}"
        return cache.get(cache_key)
    
    def _check_openai_provider(self, provider: AIProvider) -> Dict[str, Any]:
        """检查OpenAI提供商"""
        try:
            import openai
            
            # 获取API密钥
            api_key = self._get_provider_api_key(provider)
            if not api_key:
                raise Exception("未找到有效的API密钥")
            
            client = openai.OpenAI(
                api_key=api_key,
                base_url=provider.base_url if provider.base_url else None,
                timeout=self.timeout
            )
            
            # 发送简单的completions请求测试连接
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1,
                timeout=self.timeout
            )
            
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': True,
                'message': '连接正常',
                'model_tested': 'gpt-3.5-turbo',
                'response_id': response.id if hasattr(response, 'id') else None,
                'checked_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': False,
                'error': str(e),
                'checked_at': timezone.now().isoformat()
            }
    
    def _check_anthropic_provider(self, provider: AIProvider) -> Dict[str, Any]:
        """检查Anthropic提供商"""
        try:
            import anthropic
            
            api_key = self._get_provider_api_key(provider)
            if not api_key:
                raise Exception("未找到有效的API密钥")
            
            client = anthropic.Anthropic(
                api_key=api_key,
                timeout=self.timeout
            )
            
            # 发送简单的消息测试连接
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "Hello"}]
            )
            
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': True,
                'message': '连接正常',
                'model_tested': 'claude-3-haiku-20240307',
                'response_id': response.id if hasattr(response, 'id') else None,
                'checked_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': False,
                'error': str(e),
                'checked_at': timezone.now().isoformat()
            }
    
    def _check_google_provider(self, provider: AIProvider) -> Dict[str, Any]:
        """检查Google提供商"""
        try:
            import google.generativeai as genai
            
            api_key = self._get_provider_api_key(provider)
            if not api_key:
                raise Exception("未找到有效的API密钥")
            
            genai.configure(api_key=api_key)
            
            # 获取可用模型列表作为健康检查
            models = list(genai.list_models())
            
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': True,
                'message': f'连接正常，发现 {len(models)} 个模型',
                'models_count': len(models),
                'checked_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': False,
                'error': str(e),
                'checked_at': timezone.now().isoformat()
            }
    
    def _check_azure_provider(self, provider: AIProvider) -> Dict[str, Any]:
        """检查Azure OpenAI提供商"""
        try:
            import openai
            
            api_key = self._get_provider_api_key(provider)
            if not api_key:
                raise Exception("未找到有效的API密钥")
            
            client = openai.AzureOpenAI(
                api_key=api_key,
                api_version=provider.api_version or "2023-12-01-preview",
                azure_endpoint=provider.base_url,
                timeout=self.timeout
            )
            
            # 获取部署列表作为健康检查
            # 注意：这里需要根据实际的Azure部署情况调整
            response = client.chat.completions.create(
                model="gpt-35-turbo",  # 使用常见的部署名称
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1
            )
            
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': True,
                'message': '连接正常',
                'model_tested': 'gpt-35-turbo',
                'response_id': response.id if hasattr(response, 'id') else None,
                'checked_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': False,
                'error': str(e),
                'checked_at': timezone.now().isoformat()
            }
    
    def _check_local_provider(self, provider: AIProvider) -> Dict[str, Any]:
        """检查本地提供商（如Ollama）"""
        try:
            import requests
            
            # 对于Ollama，检查/api/tags端点
            base_url = provider.base_url.rstrip('/')
            health_url = f"{base_url}/api/tags"
            
            response = requests.get(
                health_url,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            data = response.json()
            models = data.get('models', [])
            
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': True,
                'message': f'连接正常，发现 {len(models)} 个模型',
                'models_count': len(models),
                'checked_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': False,
                'error': str(e),
                'checked_at': timezone.now().isoformat()
            }
    
    def _check_openai_compatible_provider(self, provider: AIProvider) -> Dict[str, Any]:
        """检查OpenAI兼容的提供商"""
        try:
            import openai
            
            api_key = self._get_provider_api_key(provider)
            if not api_key:
                raise Exception("未找到有效的API密钥")
            
            client = openai.OpenAI(
                api_key=api_key,
                base_url=provider.base_url,
                timeout=self.timeout
            )
            
            # 尝试获取模型列表
            try:
                models = client.models.list()
                model_names = [model.id for model in models.data]
                test_model = model_names[0] if model_names else "gpt-3.5-turbo"
            except:
                # 如果无法获取模型列表，使用默认模型
                test_model = "gpt-3.5-turbo"
                model_names = []
            
            # 发送测试请求
            response = client.chat.completions.create(
                model=test_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1
            )
            
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': True,
                'message': '连接正常',
                'model_tested': test_model,
                'models_available': len(model_names),
                'response_id': response.id if hasattr(response, 'id') else None,
                'checked_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': False,
                'error': str(e),
                'checked_at': timezone.now().isoformat()
            }
    
    def _check_generic_provider(self, provider: AIProvider) -> Dict[str, Any]:
        """检查通用提供商（HTTP健康检查）"""
        try:
            import requests
            
            # 尝试访问基础URL
            response = requests.get(
                provider.base_url,
                timeout=self.timeout,
                headers={'User-Agent': 'HealthCheck/1.0'}
            )
            
            is_healthy = response.status_code < 500
            
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': is_healthy,
                'message': f'HTTP {response.status_code}',
                'status_code': response.status_code,
                'checked_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'provider_id': provider.id,
                'provider_name': provider.display_name,
                'is_healthy': False,
                'error': str(e),
                'checked_at': timezone.now().isoformat()
            }
    
    def _get_provider_api_key(self, provider: AIProvider) -> Optional[str]:
        """获取提供商的API密钥"""
        try:
            # 获取提供商的第一个活跃API密钥
            api_key = provider.api_keys.filter(is_active=True).first()
            if api_key:
                return api_key.get_key()
            return None
        except Exception as e:
            logger.error(f"获取提供商 {provider.display_name} API密钥失败: {str(e)}")
            return None


class HealthCheckScheduler:
    """健康检查调度器"""
    
    def __init__(self):
        self.health_service = HealthCheckService()
        self.default_interval = 300  # 5分钟
    
    def schedule_health_checks(self):
        """调度所有提供商的健康检查"""
        try:
            results = self.health_service.check_all_providers()
            
            # 记录结果到日志
            healthy_count = sum(1 for r in results if r['is_healthy'])
            total_count = len(results)
            
            logger.info(
                f"定期健康检查完成: {healthy_count}/{total_count} 个提供商健康"
            )
            
            # 可以在这里添加告警逻辑
            if healthy_count < total_count * 0.5:  # 如果超过50%的提供商不健康
                logger.warning(
                    f"警告：超过一半的提供商不健康 ({healthy_count}/{total_count})"
                )
                # 这里可以发送告警通知
            
            return results
            
        except Exception as e:
            logger.error(f"定期健康检查失败: {str(e)}")
            return []
    
    def check_provider_recovery(self, provider: AIProvider) -> bool:
        """检查提供商是否已恢复"""
        if provider.is_healthy:
            return True
        
        # 执行健康检查
        result = self.health_service.check_provider(provider)
        return result['is_healthy']
