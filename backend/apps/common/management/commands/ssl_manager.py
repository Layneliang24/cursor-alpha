"""
SSL证书管理命令
用于生成、检查和管理SSL证书
"""
import os
import sys
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.common.ssl_config import (
    SSLCertificateManager, 
    HTTPSSecurityConfig, 
    CertificateRotationService,
    generate_production_ssl_settings
)

class Command(BaseCommand):
    help = 'SSL证书管理工具'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            type=str,
            choices=['generate', 'check', 'renew', 'config', 'status'],
            help='要执行的操作'
        )
        
        parser.add_argument(
            '--domain',
            type=str,
            default='localhost',
            help='域名（默认：localhost）'
        )
        
        parser.add_argument(
            '--email',
            type=str,
            help='Let\'s Encrypt注册邮箱'
        )
        
        parser.add_argument(
            '--output-dir',
            type=str,
            help='证书输出目录'
        )
        
        parser.add_argument(
            '--self-signed',
            action='store_true',
            help='生成自签名证书（开发环境用）'
        )
        
        parser.add_argument(
            '--nginx-config',
            action='store_true',
            help='生成Nginx配置'
        )
        
        parser.add_argument(
            '--django-config',
            action='store_true',
            help='生成Django配置'
        )

    def handle(self, *args, **options):
        action = options['action']
        domain = options['domain']
        
        try:
            if action == 'generate':
                self.generate_certificate(options)
            elif action == 'check':
                self.check_certificates(options)
            elif action == 'renew':
                self.renew_certificates(options)
            elif action == 'config':
                self.generate_configs(options)
            elif action == 'status':
                self.show_status(options)
                
        except Exception as e:
            raise CommandError(f'操作失败: {str(e)}')

    def generate_certificate(self, options):
        """生成证书"""
        domain = options['domain']
        email = options.get('email')
        output_dir = options.get('output_dir')
        self_signed = options['self_signed']
        
        cert_manager = SSLCertificateManager()
        
        if self_signed:
            self.stdout.write(f'正在为 {domain} 生成自签名证书...')
            
            result = cert_manager.generate_self_signed_cert(
                domain=domain,
                output_dir=output_dir
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ 自签名证书生成成功:')
            )
            self.stdout.write(f'  证书文件: {result["cert_file"]}')
            self.stdout.write(f'  私钥文件: {result["key_file"]}')
            self.stdout.write(f'  过期时间: {result["expires_at"]}')
            
        else:
            if not email:
                raise CommandError('Let\'s Encrypt证书需要提供邮箱地址 (--email)')
            
            self.stdout.write(f'正在为 {domain} 申请 Let\'s Encrypt 证书...')
            
            result = cert_manager.setup_lets_encrypt(
                domain=domain,
                email=email
            )
            
            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Let\'s Encrypt证书申请成功:')
                )
                self.stdout.write(f'  证书文件: {result["cert_file"]}')
                self.stdout.write(f'  私钥文件: {result["key_file"]}')
            else:
                raise CommandError(f'证书申请失败: {result["error"]}')

    def check_certificates(self, options):
        """检查证书状态"""
        domain = options['domain']
        
        self.stdout.write(f'正在检查 {domain} 的证书状态...')
        
        cert_manager = SSLCertificateManager()
        result = cert_manager.check_certificate_expiry(domain)
        
        if result['valid']:
            self.stdout.write(
                self.style.SUCCESS(f'✅ 证书有效')
            )
            if result.get('expires_at'):
                self.stdout.write(f'  过期时间: {result["expires_at"]}')
            if result.get('days_remaining'):
                days = result['days_remaining']
                if days <= 7:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  证书即将过期: {days}天')
                    )
                elif days <= 30:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  证书将在30天内过期: {days}天')
                    )
                else:
                    self.stdout.write(f'  剩余天数: {days}天')
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ 证书无效: {result.get("error", "未知错误")}')
            )

    def renew_certificates(self, options):
        """续期证书"""
        self.stdout.write('正在检查需要续期的证书...')
        
        rotation_service = CertificateRotationService()
        results = rotation_service.rotate_certificates_if_needed()
        
        if not results:
            self.stdout.write(
                self.style.SUCCESS('✅ 所有证书都在有效期内，无需续期')
            )
        else:
            for result in results:
                domain = result['domain']
                status = result['status']
                
                if status == 'scheduled':
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  {domain}: 已安排续期')
                    )
                elif status == 'failed':
                    self.stdout.write(
                        self.style.ERROR(f'❌ {domain}: 续期失败 - {result.get("error")}')
                    )

    def generate_configs(self, options):
        """生成配置文件"""
        domain = options['domain']
        nginx_config = options['nginx_config']
        django_config = options['django_config']
        
        if not nginx_config and not django_config:
            # 默认生成所有配置
            nginx_config = True
            django_config = True
        
        # 假设证书路径
        cert_file = f'/etc/ssl/certs/{domain}.crt'
        key_file = f'/etc/ssl/private/{domain}.key'
        
        if nginx_config:
            self.stdout.write(f'生成 Nginx 配置 ({domain}):')
            self.stdout.write('=' * 50)
            
            config = HTTPSSecurityConfig.get_nginx_ssl_config(
                domain=domain,
                cert_file=cert_file,
                key_file=key_file
            )
            
            self.stdout.write(config)
            self.stdout.write('=' * 50)
            
            # 保存到文件
            config_file = f'nginx_{domain.replace(".", "_")}.conf'
            with open(config_file, 'w') as f:
                f.write(config)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Nginx配置已保存到: {config_file}')
            )
        
        if django_config:
            self.stdout.write(f'\\n生成 Django SSL 配置 ({domain}):')
            self.stdout.write('=' * 50)
            
            config = generate_production_ssl_settings(
                domain=domain,
                cert_path=cert_file,
                key_path=key_file
            )
            
            self.stdout.write(config)
            self.stdout.write('=' * 50)
            
            # 保存到文件
            config_file = f'settings_ssl_{domain.replace(".", "_")}.py'
            with open(config_file, 'w') as f:
                f.write(config)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Django SSL配置已保存到: {config_file}')
            )

    def show_status(self, options):
        """显示SSL状态概览"""
        self.stdout.write('SSL证书状态概览')
        self.stdout.write('=' * 50)
        
        # 检查Django SSL设置
        ssl_enabled = getattr(settings, 'SECURE_SSL_REDIRECT', False)
        hsts_enabled = getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0
        
        self.stdout.write(f'Django SSL重定向: {"✅ 启用" if ssl_enabled else "❌ 禁用"}')
        self.stdout.write(f'HSTS配置: {"✅ 启用" if hsts_enabled else "❌ 禁用"}')
        
        # 检查环境
        debug_mode = getattr(settings, 'DEBUG', True)
        if debug_mode:
            self.stdout.write(
                self.style.WARNING('⚠️  当前为开发模式，SSL设置可能未完全启用')
            )
        else:
            self.stdout.write('✅ 生产模式')
        
        # 检查证书文件
        cert_dirs = [
            '/etc/ssl/certs',
            '/etc/letsencrypt/live',
            './ssl',
            getattr(settings, 'SSL_CERT_DIR', None)
        ]
        
        self.stdout.write('\\n证书目录检查:')
        for cert_dir in cert_dirs:
            if cert_dir and os.path.exists(cert_dir):
                cert_files = [f for f in os.listdir(cert_dir) 
                             if f.endswith(('.crt', '.pem'))]
                if cert_files:
                    self.stdout.write(f'  ✅ {cert_dir}: {len(cert_files)} 个证书文件')
                else:
                    self.stdout.write(f'  ⚠️  {cert_dir}: 目录存在但无证书文件')
            else:
                self.stdout.write(f'  ❌ {cert_dir}: 目录不存在')
        
        # 检查域名配置
        domains = getattr(settings, 'SSL_DOMAINS', [])
        if domains:
            self.stdout.write(f'\\n配置的域名: {", ".join(domains)}')
        else:
            self.stdout.write('\\n⚠️  未配置SSL域名')
        
        # 安全建议
        self.stdout.write('\\n安全建议:')
        if debug_mode:
            self.stdout.write('  - 生产环境请设置 DEBUG = False')
        if not ssl_enabled:
            self.stdout.write('  - 启用 SECURE_SSL_REDIRECT = True')
        if not hsts_enabled:
            self.stdout.write('  - 配置 HSTS: SECURE_HSTS_SECONDS = 31536000')
        
        # 检查常见安全设置
        security_settings = [
            ('SECURE_BROWSER_XSS_FILTER', '启用XSS过滤器'),
            ('SECURE_CONTENT_TYPE_NOSNIFF', '启用内容类型嗅探保护'),
            ('SESSION_COOKIE_SECURE', '启用安全Cookie'),
            ('CSRF_COOKIE_SECURE', '启用CSRF安全Cookie'),
        ]
        
        missing_settings = []
        for setting, description in security_settings:
            if not getattr(settings, setting, False):
                missing_settings.append(f'  - {setting}: {description}')
        
        if missing_settings:
            self.stdout.write('\\n缺少的安全设置:')
            for setting in missing_settings:
                self.stdout.write(setting)
        else:
            self.stdout.write('\\n✅ 所有推荐的安全设置都已启用')
