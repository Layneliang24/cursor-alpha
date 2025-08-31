"""
AI配置管理相关的Celery任务
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from .config_models import APIKey, AIProvider

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def check_api_key_expiry(self, notification_days: int = 7):
    """
    检查API密钥过期情况并发送提醒
    
    Args:
        notification_days: 提前多少天发送过期提醒
    """
    try:
        logger.info(f'开始检查API密钥过期情况，提前{notification_days}天提醒')
        
        # 计算检查时间范围
        now = timezone.now()
        warning_date = now + timedelta(days=notification_days)
        
        # 查找即将过期和已过期的密钥
        expiring_soon = APIKey.objects.filter(
            expires_at__lte=warning_date,
            expires_at__gt=now,
            is_active=True
        ).select_related('provider', 'user')
        
        expired_keys = APIKey.objects.filter(
            expires_at__lte=now,
            is_active=True
        ).select_related('provider', 'user')
        
        # 处理即将过期的密钥
        if expiring_soon.exists():
            logger.warning(f'发现{expiring_soon.count()}个即将过期的API密钥')
            _send_expiry_notifications(expiring_soon, 'warning')
        
        # 处理已过期的密钥
        if expired_keys.exists():
            logger.error(f'发现{expired_keys.count()}个已过期的API密钥')
            _send_expiry_notifications(expired_keys, 'expired')
            
            # 自动禁用过期密钥
            expired_keys.update(is_active=False)
            logger.info(f'已自动禁用{expired_keys.count()}个过期密钥')
        
        # 返回检查结果
        result = {
            'check_time': now.isoformat(),
            'expiring_soon_count': expiring_soon.count(),
            'expired_count': expired_keys.count(),
            'notification_days': notification_days
        }
        
        logger.info(f'API密钥过期检查完成: {result}')
        return result
        
    except Exception as exc:
        logger.error(f'API密钥过期检查失败: {exc}')
        # 重试机制
        if self.request.retries < self.max_retries:
            logger.info(f'正在重试检查任务，第{self.request.retries + 1}次')
            raise self.retry(countdown=60 * (self.request.retries + 1))
        else:
            logger.error('API密钥过期检查达到最大重试次数，任务失败')
            raise


@shared_task
def cleanup_old_api_keys(days_to_keep: int = 365):
    """
    清理旧的API密钥记录
    
    Args:
        days_to_keep: 保留多少天的记录
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # 查找要清理的密钥（已禁用且过期很久的）
        old_keys = APIKey.objects.filter(
            is_active=False,
            updated_at__lt=cutoff_date,
            expires_at__lt=cutoff_date
        )
        
        count = old_keys.count()
        if count > 0:
            # 备份要删除的密钥信息
            backup_data = []
            for key in old_keys:
                backup_data.append({
                    'key_id': key.key_id,
                    'name': key.name,
                    'provider': key.provider.name,
                    'user': key.user.username,
                    'masked_key': key.masked_key,
                    'created_at': key.created_at.isoformat(),
                    'deleted_at': timezone.now().isoformat()
                })
            
            # 保存备份
            backup_file = f'logs/deleted_api_keys_{datetime.now().strftime("%Y%m%d")}.json'
            import os
            import json
            os.makedirs('logs', exist_ok=True)
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            # 删除旧密钥
            old_keys.delete()
            
            logger.info(f'清理了{count}个旧API密钥，备份到{backup_file}')
            return {'cleaned_count': count, 'backup_file': backup_file}
        else:
            logger.info('没有需要清理的旧API密钥')
            return {'cleaned_count': 0}
            
    except Exception as exc:
        logger.error(f'API密钥清理失败: {exc}')
        raise


@shared_task
def health_check_api_keys():
    """
    检查API密钥的健康状态
    """
    try:
        logger.info('开始API密钥健康检查')
        
        # 获取所有活跃的密钥
        active_keys = APIKey.objects.filter(is_active=True).select_related('provider')
        
        health_results = []
        
        for key in active_keys:
            try:
                # 这里可以扩展为实际的API健康检查
                # 例如调用各个提供商的简单API来验证密钥有效性
                is_valid = key.validate_key()
                
                health_result = {
                    'key_id': key.key_id,
                    'name': key.name,
                    'provider': key.provider.name,
                    'is_valid': is_valid,
                    'check_time': timezone.now().isoformat()
                }
                
                health_results.append(health_result)
                
                # 更新最后使用时间（如果验证成功）
                if is_valid:
                    key.last_used = timezone.now()
                    key.save(update_fields=['last_used'])
                
            except Exception as e:
                logger.error(f'密钥健康检查失败 {key.name}: {e}')
                health_results.append({
                    'key_id': key.key_id,
                    'name': key.name,
                    'provider': key.provider.name,
                    'is_valid': False,
                    'error': str(e),
                    'check_time': timezone.now().isoformat()
                })
        
        # 统计结果
        valid_count = sum(1 for r in health_results if r.get('is_valid'))
        total_count = len(health_results)
        
        logger.info(f'API密钥健康检查完成: {valid_count}/{total_count} 有效')
        
        return {
            'total_checked': total_count,
            'valid_count': valid_count,
            'invalid_count': total_count - valid_count,
            'results': health_results
        }
        
    except Exception as exc:
        logger.error(f'API密钥健康检查失败: {exc}')
        raise


def _send_expiry_notifications(keys: List[APIKey], notification_type: str):
    """
    发送密钥过期通知
    
    Args:
        keys: 需要通知的密钥列表
        notification_type: 通知类型 ('warning' 或 'expired')
    """
    try:
        # 按用户分组通知
        user_keys = {}
        for key in keys:
            user_email = key.user.email
            if user_email not in user_keys:
                user_keys[user_email] = []
            user_keys[user_email].append(key)
        
        # 发送邮件通知
        for user_email, user_key_list in user_keys.items():
            if notification_type == 'warning':
                subject = 'API密钥即将过期提醒'
                message_template = 'API密钥即将过期，请及时更新：\n\n'
            else:
                subject = 'API密钥已过期警告'
                message_template = 'API密钥已过期，请立即更新：\n\n'
            
            # 构建邮件内容
            message = message_template
            for key in user_key_list:
                expiry_str = key.expires_at.strftime('%Y-%m-%d %H:%M') if key.expires_at else '未设置'
                message += f'- {key.name} ({key.provider.display_name}): {key.masked_key}\n'
                message += f'  过期时间: {expiry_str}\n\n'
            
            message += '请登录系统更新您的API密钥。\n'
            message += '如有疑问，请联系技术支持。'
            
            # 发送邮件（如果配置了邮件设置）
            if hasattr(settings, 'EMAIL_HOST') and settings.EMAIL_HOST:
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user_email],
                        fail_silently=False
                    )
                    logger.info(f'已发送密钥过期通知到: {user_email}')
                except Exception as e:
                    logger.error(f'发送邮件失败到 {user_email}: {e}')
            else:
                logger.warning(f'邮件未配置，跳过通知到: {user_email}')
                # 可以在这里添加其他通知方式，如系统内消息、Slack等
        
    except Exception as e:
        logger.error(f'发送过期通知失败: {e}')
        raise
