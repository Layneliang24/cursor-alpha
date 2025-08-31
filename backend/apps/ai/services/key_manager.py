"""
API密钥管理器

提供API密钥的安全存储、加密、轮换和管理功能
"""

import os
import json
import base64
import secrets
import logging
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import BaseCache

from ..adapters.base import AIProviderType

logger = logging.getLogger(__name__)


class APIKeyManager:
    """
    API密钥管理器
    
    功能：
    1. API密钥的AES加密存储
    2. 密钥轮换机制
    3. 多密钥管理和负载均衡
    4. 密钥安全性验证
    """
    
    def __init__(self):
        """初始化密钥管理器"""
        self._encryption_key = self._get_or_create_encryption_key()
        self._fernet = Fernet(self._encryption_key)
        self._key_cache = {}
        self._key_rotation_schedule = {}
        self._cache_available = True
        
        # 测试缓存连接
        try:
            self._safe_cache_get('test_key')
        except Exception as e:
            logger.warning(f"缓存连接失败，将使用内存存储: {e}")
            self._cache_available = False
        
        # 从环境变量和配置加载密钥
        self._load_keys_from_env()
    
    def _safe_cache_get(self, key: str, default=None):
        """安全地从缓存获取数据"""
        if not self._cache_available:
            return self._key_cache.get(key, default)
        
        try:
            return cache.get(key, default)
        except Exception as e:
            logger.warning(f"缓存读取失败: {e}")
            return self._key_cache.get(key, default)
    
    def _safe_cache_set(self, key: str, value, timeout=None):
        """安全地向缓存存储数据"""
        # 始终存储到内存缓存
        self._key_cache[key] = value
        
        if not self._cache_available:
            return
        
        try:
            cache.set(key, value, timeout=timeout)
        except Exception as e:
            logger.warning(f"缓存写入失败: {e}")
    
    def _safe_cache_delete(self, key: str):
        """安全地从缓存删除数据"""
        # 从内存缓存删除
        self._key_cache.pop(key, None)
        
        if not self._cache_available:
            return
        
        try:
            cache.delete(key)
        except Exception as e:
            logger.warning(f"缓存删除失败: {e}")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """获取或创建加密密钥"""
        # 从Django settings获取密钥或生成新的
        secret_key = getattr(settings, 'SECRET_KEY', 'default-secret-key')
        
        # 使用PBKDF2从Django SECRET_KEY派生加密密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'taskmaster-ai-salt',  # 固定salt，确保密钥一致性
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        return key
    
    def _load_keys_from_env(self):
        """从环境变量加载API密钥"""
        # 支持的提供商和对应的环境变量名
        env_mapping = {
            AIProviderType.OPENAI: ['OPENAI_API_KEY'],
            AIProviderType.ANTHROPIC: ['ANTHROPIC_API_KEY', 'CLAUDE_API_KEY'],
            AIProviderType.GOOGLE: ['GOOGLE_API_KEY', 'GEMINI_API_KEY'],
            AIProviderType.AZURE: ['AZURE_OPENAI_API_KEY'],
            AIProviderType.LOCAL: ['OLLAMA_API_KEY'],
            AIProviderType.CHENMOAI: ['CHENMOAI_API_KEY'],
            AIProviderType.OPENROUTER: ['OPENROUTER_API_KEY'],
        }
        
        for provider, env_vars in env_mapping.items():
            for env_var in env_vars:
                api_key = os.getenv(env_var)
                if api_key:
                    # 加密存储密钥
                    self._store_encrypted_key(provider, api_key, is_primary=True)
                    logger.info(f"从环境变量加载 {provider.value} API密钥")
                    break
    
    def _store_encrypted_key(
        self,
        provider: AIProviderType,
        api_key: str,
        is_primary: bool = False,
        expires_at: Optional[datetime] = None
    ) -> str:
        """
        存储加密的API密钥
        
        Args:
            provider: AI提供商
            api_key: API密钥
            is_primary: 是否为主密钥
            expires_at: 过期时间
            
        Returns:
            密钥ID
        """
        try:
            # 生成密钥ID
            key_id = f"{provider.value}_{secrets.token_hex(8)}"
            
            # 加密密钥
            encrypted_key = self._fernet.encrypt(api_key.encode())
            
            # 存储密钥信息
            key_info = {
                'provider': provider.value,
                'encrypted_key': base64.b64encode(encrypted_key).decode(),
                'is_primary': is_primary,
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat() if expires_at else None,
                'usage_count': 0,
                'last_used': None
            }
            
            # 缓存密钥信息（加密状态）
            cache_key = f"ai_key_{key_id}"
            self._safe_cache_set(cache_key, key_info, timeout=86400 * 30)  # 30天
            
            # 更新提供商的密钥列表
            provider_keys = self._get_provider_keys(provider)
            if key_id not in provider_keys:
                provider_keys.append(key_id)
                self._set_provider_keys(provider, provider_keys)
            
            # 如果是主密钥，更新缓存
            if is_primary:
                self._key_cache[provider] = api_key
            
            logger.info(f"存储 {provider.value} API密钥: {key_id}")
            return key_id
            
        except Exception as e:
            logger.error(f"存储API密钥失败: {e}")
            raise
    
    def get_key(self, provider: AIProviderType, key_id: Optional[str] = None) -> Optional[str]:
        """
        获取API密钥
        
        Args:
            provider: AI提供商
            key_id: 指定密钥ID，None时返回主密钥
            
        Returns:
            解密的API密钥
        """
        try:
            # 优先从缓存获取
            if not key_id and provider in self._key_cache:
                return self._key_cache[provider]
            
            # 获取密钥ID
            if not key_id:
                key_id = self._get_primary_key_id(provider)
                if not key_id:
                    return None
            
            # 从缓存获取加密密钥
            cache_key = f"ai_key_{key_id}"
            key_info = self._safe_cache_get(cache_key)
            
            if not key_info:
                logger.warning(f"密钥 {key_id} 不存在或已过期")
                return None
            
            # 检查过期时间
            if key_info.get('expires_at'):
                expires_at = datetime.fromisoformat(key_info['expires_at'])
                if datetime.now() > expires_at:
                    logger.warning(f"密钥 {key_id} 已过期")
                    return None
            
            # 解密密钥
            encrypted_key = base64.b64decode(key_info['encrypted_key'])
            decrypted_key = self._fernet.decrypt(encrypted_key).decode()
            
            # 更新使用统计
            key_info['usage_count'] += 1
            key_info['last_used'] = datetime.now().isoformat()
            self._safe_cache_set(cache_key, key_info, timeout=86400 * 30)
            
            # 缓存解密后的密钥
            if key_info.get('is_primary'):
                self._key_cache[provider] = decrypted_key
            
            return decrypted_key
            
        except Exception as e:
            logger.error(f"获取API密钥失败: {e}")
            return None
    
    def _get_primary_key_id(self, provider: AIProviderType) -> Optional[str]:
        """获取提供商的主密钥ID"""
        provider_keys = self._get_provider_keys(provider)
        
        for key_id in provider_keys:
            cache_key = f"ai_key_{key_id}"
            key_info = self._safe_cache_get(cache_key)
            
            if key_info and key_info.get('is_primary'):
                return key_id
        
        # 如果没有主密钥，返回第一个可用密钥
        return provider_keys[0] if provider_keys else None
    
    def _get_provider_keys(self, provider: AIProviderType) -> List[str]:
        """获取提供商的所有密钥ID"""
        cache_key = f"ai_provider_keys_{provider.value}"
        return self._safe_cache_get(cache_key, [])
    
    def _set_provider_keys(self, provider: AIProviderType, key_ids: List[str]):
        """设置提供商的密钥ID列表"""
        cache_key = f"ai_provider_keys_{provider.value}"
        self._safe_cache_set(cache_key, key_ids, timeout=86400 * 30)
    
    def add_key(
        self,
        provider: AIProviderType,
        api_key: str,
        is_primary: bool = False,
        expires_at: Optional[datetime] = None
    ) -> str:
        """
        添加新的API密钥
        
        Args:
            provider: AI提供商
            api_key: API密钥
            is_primary: 是否设为主密钥
            expires_at: 过期时间
            
        Returns:
            密钥ID
        """
        return self._store_encrypted_key(provider, api_key, is_primary, expires_at)
    
    def remove_key(self, key_id: str) -> bool:
        """
        移除API密钥
        
        Args:
            key_id: 密钥ID
            
        Returns:
            是否移除成功
        """
        try:
            cache_key = f"ai_key_{key_id}"
            key_info = self._safe_cache_get(cache_key)
            
            if not key_info:
                logger.warning(f"密钥 {key_id} 不存在")
                return False
            
            provider = AIProviderType(key_info['provider'])
            
            # 从提供商密钥列表中移除
            provider_keys = self._get_provider_keys(provider)
            if key_id in provider_keys:
                provider_keys.remove(key_id)
                self._set_provider_keys(provider, provider_keys)
            
            # 删除缓存
            self._safe_cache_delete(cache_key)
            
            # 如果是主密钥，清除缓存
            if key_info.get('is_primary') and provider in self._key_cache:
                del self._key_cache[provider]
            
            logger.info(f"移除API密钥: {key_id}")
            return True
            
        except Exception as e:
            logger.error(f"移除API密钥失败: {e}")
            return False
    
    def rotate_keys(self, provider: AIProviderType) -> bool:
        """
        轮换提供商的API密钥
        
        Args:
            provider: AI提供商
            
        Returns:
            是否轮换成功
        """
        try:
            provider_keys = self._get_provider_keys(provider)
            if len(provider_keys) < 2:
                logger.warning(f"提供商 {provider.value} 密钥数量不足，无法轮换")
                return False
            
            # 找到当前主密钥
            current_primary = None
            for key_id in provider_keys:
                cache_key = f"ai_key_{key_id}"
                key_info = self._safe_cache_get(cache_key)
                if key_info and key_info.get('is_primary'):
                    current_primary = key_id
                    break
            
            if not current_primary:
                logger.warning(f"提供商 {provider.value} 没有主密钥")
                return False
            
            # 选择下一个密钥作为主密钥
            current_index = provider_keys.index(current_primary)
            next_index = (current_index + 1) % len(provider_keys)
            next_primary = provider_keys[next_index]
            
            # 更新密钥状态
            self._set_primary_key(current_primary, False)
            self._set_primary_key(next_primary, True)
            
            # 清除缓存，强制重新获取
            if provider in self._key_cache:
                del self._key_cache[provider]
            
            logger.info(f"轮换 {provider.value} API密钥: {current_primary} -> {next_primary}")
            return True
            
        except Exception as e:
            logger.error(f"轮换API密钥失败: {e}")
            return False
    
    def _set_primary_key(self, key_id: str, is_primary: bool):
        """设置密钥的主密钥状态"""
        cache_key = f"ai_key_{key_id}"
        key_info = self._safe_cache_get(cache_key)
        
        if key_info:
            key_info['is_primary'] = is_primary
            self._safe_cache_set(cache_key, key_info, timeout=86400 * 30)
    
    def get_key_stats(self, provider: Optional[AIProviderType] = None) -> Dict[str, any]:
        """
        获取密钥统计信息
        
        Args:
            provider: 指定提供商，None时返回所有
            
        Returns:
            密钥统计信息
        """
        stats = {}
        
        providers_to_check = [provider] if provider else list(AIProviderType)
        
        for prov in providers_to_check:
            provider_keys = self._get_provider_keys(prov)
            provider_stats = {
                'total_keys': len(provider_keys),
                'keys': []
            }
            
            for key_id in provider_keys:
                cache_key = f"ai_key_{key_id}"
                key_info = self._safe_cache_get(cache_key)
                
                if key_info:
                    # 不返回实际密钥，只返回统计信息
                    key_stat = {
                        'key_id': key_id,
                        'is_primary': key_info.get('is_primary', False),
                        'created_at': key_info.get('created_at'),
                        'expires_at': key_info.get('expires_at'),
                        'usage_count': key_info.get('usage_count', 0),
                        'last_used': key_info.get('last_used')
                    }
                    provider_stats['keys'].append(key_stat)
            
            stats[prov.value] = provider_stats
        
        return stats
    
    def validate_key(self, provider: AIProviderType, api_key: str) -> bool:
        """
        验证API密钥有效性
        
        Args:
            provider: AI提供商
            api_key: API密钥
            
        Returns:
            密钥是否有效
        """
        try:
            # 创建临时配置进行验证
            from ..adapters import AIModelConfig, AIAdapterFactory
            
            temp_config = AIModelConfig(
                model=self._get_default_model(provider),
                api_key=api_key,
                max_tokens=100,
                timeout=10
            )
            
            # 创建适配器并进行健康检查
            adapter = AIAdapterFactory.create_adapter(provider, temp_config)
            health_result = adapter.health_check()
            
            return health_result.is_healthy
            
        except Exception as e:
            logger.error(f"验证API密钥失败: {e}")
            return False
    
    def _get_default_model(self, provider: AIProviderType) -> str:
        """获取提供商的默认模型"""
        default_models = {
            AIProviderType.OPENAI: 'gpt-3.5-turbo',
            AIProviderType.ANTHROPIC: 'claude-3-haiku-20240307',
            AIProviderType.GOOGLE: 'gemini-pro',
            AIProviderType.AZURE: 'gpt-35-turbo',
            AIProviderType.LOCAL: 'llama2',
            AIProviderType.CHENMOAI: 'gpt-3.5-turbo',
            AIProviderType.OPENROUTER: 'google/gemma-2-9b-it:free'
        }
        return default_models.get(provider, 'gpt-3.5-turbo')
    
    def schedule_key_rotation(
        self,
        provider: AIProviderType,
        interval_days: int = 30
    ):
        """
        安排密钥轮换
        
        Args:
            provider: AI提供商
            interval_days: 轮换间隔（天）
        """
        next_rotation = datetime.now() + timedelta(days=interval_days)
        self._key_rotation_schedule[provider] = next_rotation
        
        logger.info(f"安排 {provider.value} 密钥轮换: {next_rotation}")
    
    def check_rotation_schedule(self):
        """检查并执行预定的密钥轮换"""
        now = datetime.now()
        
        for provider, next_rotation in list(self._key_rotation_schedule.items()):
            if now >= next_rotation:
                try:
                    if self.rotate_keys(provider):
                        # 重新安排下次轮换
                        self.schedule_key_rotation(provider)
                        logger.info(f"自动轮换 {provider.value} 密钥完成")
                    else:
                        # 轮换失败，延迟1小时再试
                        self._key_rotation_schedule[provider] = now + timedelta(hours=1)
                        
                except Exception as e:
                    logger.error(f"自动轮换 {provider.value} 密钥失败: {e}")
                    # 延迟1小时再试
                    self._key_rotation_schedule[provider] = now + timedelta(hours=1)
    
    def get_rotation_schedule(self) -> Dict[str, str]:
        """获取密钥轮换计划"""
        return {
            provider.value: next_rotation.isoformat()
            for provider, next_rotation in self._key_rotation_schedule.items()
        }
    
    def backup_keys(self, backup_path: str) -> bool:
        """
        备份加密的API密钥
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否备份成功
        """
        try:
            backup_data = {
                'created_at': datetime.now().isoformat(),
                'providers': {}
            }
            
            for provider in AIProviderType:
                provider_keys = self._get_provider_keys(provider)
                provider_data = []
                
                for key_id in provider_keys:
                    cache_key = f"ai_key_{key_id}"
                    key_info = self._safe_cache_get(cache_key)
                    if key_info:
                        provider_data.append({
                            'key_id': key_id,
                            'encrypted_key': key_info['encrypted_key'],
                            'is_primary': key_info.get('is_primary', False),
                            'created_at': key_info.get('created_at'),
                            'expires_at': key_info.get('expires_at')
                        })
                
                if provider_data:
                    backup_data['providers'][provider.value] = provider_data
            
            # 写入备份文件
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"API密钥备份完成: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"备份API密钥失败: {e}")
            return False
    
    def restore_keys(self, backup_path: str) -> bool:
        """
        从备份恢复API密钥
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            是否恢复成功
        """
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            for provider_name, keys_data in backup_data.get('providers', {}).items():
                provider = AIProviderType(provider_name)
                
                for key_data in keys_data:
                    key_id = key_data['key_id']
                    cache_key = f"ai_key_{key_id}"
                    
                    # 恢复密钥信息
                    key_info = {
                        'provider': provider_name,
                        'encrypted_key': key_data['encrypted_key'],
                        'is_primary': key_data.get('is_primary', False),
                        'created_at': key_data.get('created_at'),
                        'expires_at': key_data.get('expires_at'),
                        'usage_count': 0,  # 重置使用计数
                        'last_used': None
                    }
                    
                    self._safe_cache_set(cache_key, key_info, timeout=86400 * 30)
                
                # 更新提供商密钥列表
                provider_keys = [key_data['key_id'] for key_data in keys_data]
                self._set_provider_keys(provider, provider_keys)
            
            # 清除内存缓存，强制重新加载
            self._key_cache.clear()
            
            logger.info(f"API密钥恢复完成: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"恢复API密钥失败: {e}")
            return False
    
    def cleanup_expired_keys(self) -> int:
        """
        清理过期的API密钥
        
        Returns:
            清理的密钥数量
        """
        cleaned_count = 0
        now = datetime.now()
        
        try:
            for provider in AIProviderType:
                provider_keys = self._get_provider_keys(provider)
                valid_keys = []
                
                for key_id in provider_keys:
                    cache_key = f"ai_key_{key_id}"
                    key_info = self._safe_cache_get(cache_key)
                    
                    if key_info:
                        expires_at = key_info.get('expires_at')
                        if expires_at:
                            expiry_time = datetime.fromisoformat(expires_at)
                            if now > expiry_time:
                                # 密钥已过期，删除
                                self._safe_cache_delete(cache_key)
                                cleaned_count += 1
                                logger.info(f"清理过期密钥: {key_id}")
                                continue
                        
                        valid_keys.append(key_id)
                    else:
                        # 密钥信息不存在，从列表中移除
                        cleaned_count += 1
                
                # 更新有效密钥列表
                if len(valid_keys) != len(provider_keys):
                    self._set_provider_keys(provider, valid_keys)
            
            if cleaned_count > 0:
                # 清除内存缓存
                self._key_cache.clear()
                logger.info(f"清理过期密钥完成，共清理 {cleaned_count} 个")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"清理过期密钥失败: {e}")
            return 0
