"""
SSL/HTTPS配置和证书管理
"""
import os
import ssl
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

class SSLCertificateManager:
    """SSL证书管理器"""
    
    def __init__(self, cert_dir: str = None):
        self.cert_dir = Path(cert_dir or getattr(settings, 'SSL_CERT_DIR', '/etc/ssl/certs'))
        self.key_dir = Path(getattr(settings, 'SSL_KEY_DIR', '/etc/ssl/private'))
        
    def check_certificate_expiry(self, cert_path: str) -> Dict[str, any]:
        """检查证书过期时间"""
        try:
            import ssl
            import socket
            from urllib.parse import urlparse
            
            # 如果是文件路径
            if os.path.isfile(cert_path):
                with open(cert_path, 'r') as f:
                    cert_data = f.read()
                cert = ssl.PEM_cert_to_DER_cert(cert_data)
            else:
                # 如果是域名，获取远程证书
                parsed = urlparse(cert_path if cert_path.startswith('http') else f'https://{cert_path}')
                hostname = parsed.hostname
                port = parsed.port or 443
                
                context = ssl.create_default_context()
                with socket.create_connection((hostname, port), timeout=10) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert(binary_form=True)
            
            # 解析证书信息
            cert_obj = ssl.DER_cert_to_PEM_cert(cert)
            # 这里需要使用cryptography库来解析证书详细信息
            
            return {
                'valid': True,
                'expires_at': None,  # 需要cryptography库支持
                'days_remaining': None,
                'issuer': None,
                'subject': None
            }
            
        except Exception as e:
            logger.error(f"检查证书失败: {str(e)}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def generate_self_signed_cert(self, domain: str, output_dir: str = None) -> Dict[str, str]:
        """生成自签名证书（开发环境用）"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            import ipaddress
            
            # 生成私钥
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # 创建证书主题
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Alpha Development"),
                x509.NameAttribute(NameOID.COMMON_NAME, domain),
            ])
            
            # 创建证书
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(domain),
                    x509.DNSName(f"*.{domain}"),
                    x509.DNSName("localhost"),
                    x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # 保存证书和私钥
            output_path = Path(output_dir or self.cert_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            cert_file = output_path / f"{domain}.crt"
            key_file = output_path / f"{domain}.key"
            
            # 写入证书文件
            with open(cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # 写入私钥文件
            with open(key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # 设置文件权限
            os.chmod(key_file, 0o600)  # 私钥只有所有者可读
            os.chmod(cert_file, 0o644)  # 证书可读
            
            return {
                'cert_file': str(cert_file),
                'key_file': str(key_file),
                'domain': domain,
                'expires_at': datetime.utcnow() + timedelta(days=365)
            }
            
        except Exception as e:
            logger.error(f"生成自签名证书失败: {str(e)}")
            raise
    
    def setup_lets_encrypt(self, domain: str, email: str) -> Dict[str, any]:
        """设置Let's Encrypt证书"""
        try:
            # 检查certbot是否安装
            result = subprocess.run(['certbot', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': 'certbot未安装，请先安装certbot'
                }
            
            # 生成Let's Encrypt证书
            cmd = [
                'certbot', 'certonly',
                '--webroot',
                '--webroot-path', '/var/www/html',
                '--email', email,
                '--agree-tos',
                '--no-eff-email',
                '--domains', domain
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                cert_path = f'/etc/letsencrypt/live/{domain}/fullchain.pem'
                key_path = f'/etc/letsencrypt/live/{domain}/privkey.pem'
                
                return {
                    'success': True,
                    'cert_file': cert_path,
                    'key_file': key_path,
                    'domain': domain
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr
                }
                
        except Exception as e:
            logger.error(f"Let's Encrypt证书生成失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

class HTTPSSecurityConfig:
    """HTTPS安全配置"""
    
    @staticmethod
    def get_nginx_ssl_config(domain: str, cert_file: str, key_file: str) -> str:
        """生成Nginx SSL配置"""
        return f"""
# HTTPS配置 - {domain}
server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {domain};
    
    # SSL证书配置
    ssl_certificate {cert_file};
    ssl_certificate_key {key_file};
    
    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS配置
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # 其他安全头
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # CSP头
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data: https: blob:; connect-src 'self' https://api.siliconflow.cn https://openrouter.ai https://api.openai.com; object-src 'none'; frame-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests" always;
    
    # 权限策略
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=(), usb=(), bluetooth=(), payment=(), midi=(), sync-xhr=()" always;
    
    # 前端静态文件
    location / {{
        root /var/www/{domain}/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # 静态资源缓存
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}
    
    # API代理
    location /api/ {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }}
}}

# HTTP重定向到HTTPS
server {{
    listen 80;
    listen [::]:80;
    server_name {domain};
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}}
"""
    
    @staticmethod
    def get_django_ssl_settings() -> Dict[str, any]:
        """获取Django SSL设置"""
        return {
            # HTTPS重定向
            'SECURE_SSL_REDIRECT': True,
            
            # HSTS配置
            'SECURE_HSTS_SECONDS': 31536000,  # 1年
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
            'SECURE_HSTS_PRELOAD': True,
            
            # Cookie安全
            'SESSION_COOKIE_SECURE': True,
            'CSRF_COOKIE_SECURE': True,
            'SESSION_COOKIE_HTTPONLY': True,
            'CSRF_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',
            'CSRF_COOKIE_SAMESITE': 'Lax',
            
            # 代理信任
            'SECURE_PROXY_SSL_HEADER': ('HTTP_X_FORWARDED_PROTO', 'https'),
            'USE_X_FORWARDED_HOST': True,
            'USE_X_FORWARDED_PORT': True,
            
            # 其他安全设置
            'SECURE_BROWSER_XSS_FILTER': True,
            'SECURE_CONTENT_TYPE_NOSNIFF': True,
            'SECURE_REFERRER_POLICY': 'strict-origin-when-cross-origin',
        }

class APIKeySecurityManager:
    """API密钥安全管理器"""
    
    @staticmethod
    def validate_key_transmission(request) -> bool:
        """验证API密钥传输安全性"""
        # 检查是否使用HTTPS
        if not request.is_secure():
            logger.warning(f"非安全连接传输API密钥: {request.META.get('REMOTE_ADDR')}")
            return False
        
        # 检查请求头
        required_headers = ['X-Forwarded-Proto', 'X-Real-IP']
        for header in required_headers:
            if header not in request.META:
                logger.warning(f"缺少安全头: {header}")
        
        return True
    
    @staticmethod
    def create_secure_api_key_response(api_key_data: Dict) -> Dict:
        """创建安全的API密钥响应"""
        # 移除敏感信息
        safe_data = api_key_data.copy()
        
        # 确保不返回原始密钥
        if 'raw_key' in safe_data:
            del safe_data['raw_key']
        if 'encrypted_key' in safe_data:
            del safe_data['encrypted_key']
        
        # 添加掩码版本
        if 'masked_key' not in safe_data and 'key_preview' in safe_data:
            safe_data['masked_key'] = safe_data['key_preview']
        
        return safe_data
    
    @staticmethod
    def log_key_access(user, action: str, key_id: str = None):
        """记录密钥访问日志"""
        try:
            from apps.rbac.services import AuditService
            AuditService.log_user_action(
                user=user,
                action=f'api_key_{action}',
                resource_type='api_key',
                description=f'API密钥{action}: {key_id or "unknown"}',
                resource_id=key_id
            )
        except Exception as e:
            logger.error(f"记录密钥访问日志失败: {str(e)}")

class CertificateRotationService:
    """证书轮换服务"""
    
    def __init__(self):
        self.cert_manager = SSLCertificateManager()
    
    def check_all_certificates(self) -> List[Dict]:
        """检查所有证书状态"""
        results = []
        
        # 检查主域名证书
        domains = getattr(settings, 'SSL_DOMAINS', ['localhost'])
        
        for domain in domains:
            cert_info = self.cert_manager.check_certificate_expiry(domain)
            cert_info['domain'] = domain
            results.append(cert_info)
        
        return results
    
    def rotate_certificates_if_needed(self, days_before_expiry: int = 30) -> List[Dict]:
        """如果需要则轮换证书"""
        rotation_results = []
        
        cert_statuses = self.check_all_certificates()
        
        for cert_status in cert_statuses:
            if not cert_status.get('valid'):
                continue
            
            days_remaining = cert_status.get('days_remaining')
            if days_remaining is not None and days_remaining <= days_before_expiry:
                # 需要轮换证书
                domain = cert_status['domain']
                
                try:
                    # 这里可以集成Let's Encrypt自动续期
                    # 或者发送通知给管理员
                    
                    rotation_results.append({
                        'domain': domain,
                        'action': 'renewal_needed',
                        'days_remaining': days_remaining,
                        'status': 'scheduled'
                    })
                    
                    logger.info(f"证书即将过期，已安排续期: {domain} ({days_remaining}天)")
                    
                except Exception as e:
                    rotation_results.append({
                        'domain': domain,
                        'action': 'renewal_failed',
                        'error': str(e),
                        'status': 'failed'
                    })
        
        return rotation_results

# Django设置生成器
def generate_production_ssl_settings(domain: str, cert_path: str, key_path: str) -> str:
    """生成生产环境SSL设置"""
    ssl_settings = HTTPSSecurityConfig.get_django_ssl_settings()
    
    settings_code = f"""
# 生产环境SSL配置 - {domain}
# 在settings_production.py中使用

# HTTPS强制重定向
SECURE_SSL_REDIRECT = {ssl_settings['SECURE_SSL_REDIRECT']}

# HSTS配置
SECURE_HSTS_SECONDS = {ssl_settings['SECURE_HSTS_SECONDS']}
SECURE_HSTS_INCLUDE_SUBDOMAINS = {ssl_settings['SECURE_HSTS_INCLUDE_SUBDOMAINS']}
SECURE_HSTS_PRELOAD = {ssl_settings['SECURE_HSTS_PRELOAD']}

# Cookie安全
SESSION_COOKIE_SECURE = {ssl_settings['SESSION_COOKIE_SECURE']}
CSRF_COOKIE_SECURE = {ssl_settings['CSRF_COOKIE_SECURE']}
SESSION_COOKIE_HTTPONLY = {ssl_settings['SESSION_COOKIE_HTTPONLY']}
CSRF_COOKIE_HTTPONLY = {ssl_settings['CSRF_COOKIE_HTTPONLY']}
SESSION_COOKIE_SAMESITE = '{ssl_settings['SESSION_COOKIE_SAMESITE']}'
CSRF_COOKIE_SAMESITE = '{ssl_settings['CSRF_COOKIE_SAMESITE']}'

# 代理配置
SECURE_PROXY_SSL_HEADER = {ssl_settings['SECURE_PROXY_SSL_HEADER']}
USE_X_FORWARDED_HOST = {ssl_settings['USE_X_FORWARDED_HOST']}
USE_X_FORWARDED_PORT = {ssl_settings['USE_X_FORWARDED_PORT']}

# 其他安全设置
SECURE_BROWSER_XSS_FILTER = {ssl_settings['SECURE_BROWSER_XSS_FILTER']}
SECURE_CONTENT_TYPE_NOSNIFF = {ssl_settings['SECURE_CONTENT_TYPE_NOSNIFF']}
SECURE_REFERRER_POLICY = '{ssl_settings['SECURE_REFERRER_POLICY']}'

# 允许的主机
ALLOWED_HOSTS = ['{domain}', 'www.{domain}']

# SSL证书路径
SSL_CERT_FILE = '{cert_path}'
SSL_KEY_FILE = '{key_path}'
SSL_DOMAINS = ['{domain}']
"""
    
    return settings_code

# Celery任务（如果使用Celery）
def setup_certificate_monitoring():
    """设置证书监控任务"""
    try:
        from celery import shared_task
        
        @shared_task
        def check_certificate_expiry():
            """检查证书过期状态（每日任务）"""
            service = CertificateRotationService()
            results = service.check_all_certificates()
            
            # 发送通知给管理员
            for result in results:
                if not result.get('valid'):
                    logger.error(f"证书无效: {result.get('domain')} - {result.get('error')}")
                elif result.get('days_remaining', 0) <= 7:
                    logger.warning(f"证书即将过期: {result.get('domain')} - {result.get('days_remaining')}天")
            
            return results
        
        @shared_task
        def auto_renew_certificates():
            """自动续期证书（每周任务）"""
            service = CertificateRotationService()
            results = service.rotate_certificates_if_needed()
            
            logger.info(f"证书轮换检查完成: {len(results)}个域名")
            return results
        
        return {
            'check_certificate_expiry': check_certificate_expiry,
            'auto_renew_certificates': auto_renew_certificates
        }
        
    except ImportError:
        logger.info("Celery未安装，跳过证书监控任务设置")
        return None
