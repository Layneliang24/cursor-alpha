#!/bin/bash

# Alpha项目SSL配置脚本
# 用于设置HTTPS、SSL证书和安全配置

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
DOMAIN=${1:-"localhost"}
EMAIL=${2:-"admin@example.com"}
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
NGINX_AVAILABLE="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"
SSL_CERT_DIR="/etc/ssl/certs"
SSL_KEY_DIR="/etc/ssl/private"

echo -e "${BLUE}🔒 Alpha项目SSL配置脚本${NC}"
echo -e "${BLUE}================================${NC}"
echo "域名: $DOMAIN"
echo "邮箱: $EMAIL"
echo "项目根目录: $PROJECT_ROOT"
echo ""

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        echo -e "${RED}⚠️  不建议以root用户运行此脚本${NC}"
        echo "请使用sudo运行具体命令"
        read -p "继续执行? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检查系统依赖
check_dependencies() {
    echo -e "${YELLOW}🔍 检查系统依赖...${NC}"
    
    local missing_deps=()
    
    # 检查Nginx
    if ! command -v nginx &> /dev/null; then
        missing_deps+=("nginx")
    fi
    
    # 检查OpenSSL
    if ! command -v openssl &> /dev/null; then
        missing_deps+=("openssl")
    fi
    
    # 检查certbot（Let's Encrypt）
    if ! command -v certbot &> /dev/null; then
        echo -e "${YELLOW}⚠️  certbot未安装，将无法申请Let's Encrypt证书${NC}"
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}❌ 缺少依赖: ${missing_deps[*]}${NC}"
        echo "Ubuntu/Debian安装命令:"
        echo "sudo apt update && sudo apt install ${missing_deps[*]}"
        echo ""
        echo "CentOS/RHEL安装命令:"
        echo "sudo yum install ${missing_deps[*]}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 依赖检查通过${NC}"
}

# 创建SSL目录
create_ssl_dirs() {
    echo -e "${YELLOW}📁 创建SSL目录...${NC}"
    
    sudo mkdir -p "$SSL_CERT_DIR"
    sudo mkdir -p "$SSL_KEY_DIR"
    sudo mkdir -p "$PROJECT_ROOT/ssl"
    
    echo -e "${GREEN}✅ SSL目录创建完成${NC}"
}

# 生成自签名证书（开发环境）
generate_self_signed_cert() {
    echo -e "${YELLOW}🔐 生成自签名证书 ($DOMAIN)...${NC}"
    
    local cert_file="$PROJECT_ROOT/ssl/$DOMAIN.crt"
    local key_file="$PROJECT_ROOT/ssl/$DOMAIN.key"
    local config_file="$PROJECT_ROOT/ssl/$DOMAIN.conf"
    
    # 创建证书配置文件
    cat > "$config_file" << EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=CN
ST=Beijing
L=Beijing
O=Alpha Development
OU=Development Team
CN=$DOMAIN

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = $DOMAIN
DNS.2 = *.$DOMAIN
DNS.3 = localhost
DNS.4 = 127.0.0.1
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
    
    # 生成私钥
    openssl genrsa -out "$key_file" 2048
    
    # 生成证书
    openssl req -new -x509 -key "$key_file" -out "$cert_file" -days 365 -config "$config_file" -extensions v3_req
    
    # 设置权限
    chmod 600 "$key_file"
    chmod 644 "$cert_file"
    
    echo -e "${GREEN}✅ 自签名证书生成完成${NC}"
    echo "   证书文件: $cert_file"
    echo "   私钥文件: $key_file"
    echo "   有效期: 365天"
}

# 申请Let's Encrypt证书（生产环境）
generate_letsencrypt_cert() {
    echo -e "${YELLOW}🌐 申请Let's Encrypt证书 ($DOMAIN)...${NC}"
    
    if ! command -v certbot &> /dev/null; then
        echo -e "${RED}❌ certbot未安装，无法申请Let's Encrypt证书${NC}"
        return 1
    fi
    
    # 创建webroot目录
    sudo mkdir -p /var/www/html
    
    # 申请证书
    sudo certbot certonly \
        --webroot \
        --webroot-path /var/www/html \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --domains "$DOMAIN" \
        --non-interactive
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Let's Encrypt证书申请成功${NC}"
        echo "   证书文件: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
        echo "   私钥文件: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
        
        # 设置自动续期
        setup_certbot_renewal
    else
        echo -e "${RED}❌ Let's Encrypt证书申请失败${NC}"
        echo "回退到自签名证书..."
        generate_self_signed_cert
    fi
}

# 设置certbot自动续期
setup_certbot_renewal() {
    echo -e "${YELLOW}⏰ 设置证书自动续期...${NC}"
    
    # 检查crontab是否已存在续期任务
    if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
        # 添加续期任务到crontab（每天检查两次）
        (crontab -l 2>/dev/null; echo "0 2,14 * * * certbot renew --quiet && systemctl reload nginx") | crontab -
        echo -e "${GREEN}✅ 自动续期任务已添加到crontab${NC}"
    else
        echo -e "${YELLOW}⚠️  续期任务已存在${NC}"
    fi
}

# 生成DH参数（提高安全性）
generate_dhparam() {
    local dhparam_file="/etc/ssl/dhparam.pem"
    
    if [ ! -f "$dhparam_file" ]; then
        echo -e "${YELLOW}🔐 生成DH参数（可能需要几分钟）...${NC}"
        sudo openssl dhparam -out "$dhparam_file" 2048
        echo -e "${GREEN}✅ DH参数生成完成${NC}"
    else
        echo -e "${YELLOW}⚠️  DH参数文件已存在${NC}"
    fi
}

# 配置Nginx
setup_nginx() {
    echo -e "${YELLOW}🌐 配置Nginx...${NC}"
    
    local nginx_config="$NGINX_AVAILABLE/alpha-ssl"
    local cert_file key_file
    
    # 确定证书文件路径
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        cert_file="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
        key_file="/etc/letsencrypt/live/$DOMAIN/privkey.pem"
        echo "使用Let's Encrypt证书"
    else
        cert_file="$PROJECT_ROOT/ssl/$DOMAIN.crt"
        key_file="$PROJECT_ROOT/ssl/$DOMAIN.key"
        echo "使用自签名证书"
    fi
    
    # 复制Nginx配置模板
    sudo cp "$PROJECT_ROOT/nginx_alpha_ssl.conf" "$nginx_config"
    
    # 替换配置文件中的占位符
    sudo sed -i "s/yourdomain.com/$DOMAIN/g" "$nginx_config"
    sudo sed -i "s|/etc/ssl/certs/yourdomain.com.crt|$cert_file|g" "$nginx_config"
    sudo sed -i "s|/etc/ssl/private/yourdomain.com.key|$key_file|g" "$nginx_config"
    sudo sed -i "s|/var/www/yourdomain.com|$PROJECT_ROOT|g" "$nginx_config"
    
    # 启用站点
    sudo ln -sf "$nginx_config" "$NGINX_ENABLED/alpha-ssl"
    
    # 删除默认站点（如果存在）
    sudo rm -f "$NGINX_ENABLED/default"
    
    # 测试Nginx配置
    if sudo nginx -t; then
        echo -e "${GREEN}✅ Nginx配置测试通过${NC}"
        
        # 重新加载Nginx
        sudo systemctl reload nginx
        echo -e "${GREEN}✅ Nginx配置已应用${NC}"
    else
        echo -e "${RED}❌ Nginx配置测试失败${NC}"
        exit 1
    fi
}

# 配置Django SSL设置
setup_django_ssl() {
    echo -e "${YELLOW}🐍 配置Django SSL设置...${NC}"
    
    local settings_file="$PROJECT_ROOT/backend/alpha/settings_local.py"
    
    # 创建本地设置文件
    cat > "$settings_file" << EOF
# 本地SSL设置
# 此文件会被.gitignore忽略，不会提交到版本控制

from .settings_production_ssl import *

# 域名配置
ALLOWED_HOSTS = ['$DOMAIN', 'www.$DOMAIN', 'localhost', '127.0.0.1']

# SSL证书路径
SSL_DOMAINS = ['$DOMAIN']

# 如果使用自签名证书，在开发环境中禁用某些检查
import ssl
if DEBUG:
    ssl._create_default_https_context = ssl._create_unverified_context
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

print("🔒 SSL配置已加载 - 域名: $DOMAIN")
EOF
    
    echo -e "${GREEN}✅ Django SSL配置已创建${NC}"
    echo "   配置文件: $settings_file"
    echo "   请在生产环境中使用: python manage.py runserver --settings=alpha.settings_local"
}

# 设置防火墙
setup_firewall() {
    echo -e "${YELLOW}🔥 配置防火墙...${NC}"
    
    if command -v ufw &> /dev/null; then
        # 使用ufw
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        echo -e "${GREEN}✅ UFW防火墙规则已添加${NC}"
    elif command -v firewall-cmd &> /dev/null; then
        # 使用firewalld
        sudo firewall-cmd --permanent --add-service=http
        sudo firewall-cmd --permanent --add-service=https
        sudo firewall-cmd --reload
        echo -e "${GREEN}✅ Firewalld防火墙规则已添加${NC}"
    else
        echo -e "${YELLOW}⚠️  未检测到防火墙管理工具，请手动开放80和443端口${NC}"
    fi
}

# 验证SSL配置
verify_ssl() {
    echo -e "${YELLOW}🔍 验证SSL配置...${NC}"
    
    # 检查证书文件
    local cert_file key_file
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
        cert_file="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
        key_file="/etc/letsencrypt/live/$DOMAIN/privkey.pem"
    else
        cert_file="$PROJECT_ROOT/ssl/$DOMAIN.crt"
        key_file="$PROJECT_ROOT/ssl/$DOMAIN.key"
    fi
    
    if [ -f "$cert_file" ] && [ -f "$key_file" ]; then
        echo -e "${GREEN}✅ SSL证书文件存在${NC}"
        
        # 检查证书有效期
        local expiry_date
        expiry_date=$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)
        echo "   证书过期时间: $expiry_date"
        
        # 检查证书和私钥匹配
        local cert_hash key_hash
        cert_hash=$(openssl x509 -in "$cert_file" -noout -modulus | openssl md5)
        key_hash=$(openssl rsa -in "$key_file" -noout -modulus | openssl md5)
        
        if [ "$cert_hash" = "$key_hash" ]; then
            echo -e "${GREEN}✅ 证书和私钥匹配${NC}"
        else
            echo -e "${RED}❌ 证书和私钥不匹配${NC}"
        fi
    else
        echo -e "${RED}❌ SSL证书文件不存在${NC}"
    fi
    
    # 检查Nginx状态
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✅ Nginx服务运行中${NC}"
    else
        echo -e "${RED}❌ Nginx服务未运行${NC}"
    fi
    
    # 测试HTTPS连接
    echo "测试HTTPS连接..."
    if curl -k -s "https://$DOMAIN/health/" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ HTTPS连接测试成功${NC}"
    else
        echo -e "${YELLOW}⚠️  HTTPS连接测试失败（可能Django未启动）${NC}"
    fi
}

# 显示使用说明
show_usage() {
    echo -e "${BLUE}使用方法:${NC}"
    echo "  $0 <域名> [邮箱]"
    echo ""
    echo -e "${BLUE}示例:${NC}"
    echo "  $0 localhost                    # 开发环境（自签名证书）"
    echo "  $0 example.com admin@example.com # 生产环境（Let's Encrypt证书）"
    echo ""
    echo -e "${BLUE}选项:${NC}"
    echo "  --dev         强制使用自签名证书"
    echo "  --prod        强制使用Let's Encrypt证书"
    echo "  --skip-nginx  跳过Nginx配置"
    echo "  --help        显示此帮助信息"
}

# 主函数
main() {
    local use_self_signed=false
    local use_letsencrypt=false
    local skip_nginx=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev)
                use_self_signed=true
                shift
                ;;
            --prod)
                use_letsencrypt=true
                shift
                ;;
            --skip-nginx)
                skip_nginx=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                if [ -z "$DOMAIN" ]; then
                    DOMAIN="$1"
                elif [ -z "$EMAIL" ]; then
                    EMAIL="$1"
                fi
                shift
                ;;
        esac
    done
    
    # 检查参数
    if [ "$DOMAIN" = "localhost" ]; then
        use_self_signed=true
    fi
    
    echo "开始SSL配置..."
    
    check_root
    check_dependencies
    create_ssl_dirs
    
    # 生成证书
    if [ "$use_self_signed" = true ]; then
        generate_self_signed_cert
    elif [ "$use_letsencrypt" = true ]; then
        generate_letsencrypt_cert
    else
        # 自动选择
        if [ "$DOMAIN" = "localhost" ] || [[ $DOMAIN =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            generate_self_signed_cert
        else
            generate_letsencrypt_cert
        fi
    fi
    
    # 生成DH参数
    generate_dhparam
    
    # 配置服务
    if [ "$skip_nginx" != true ]; then
        setup_nginx
    fi
    
    setup_django_ssl
    setup_firewall
    
    # 验证配置
    verify_ssl
    
    echo ""
    echo -e "${GREEN}🎉 SSL配置完成！${NC}"
    echo ""
    echo -e "${BLUE}后续步骤:${NC}"
    echo "1. 启动Django服务: cd backend && python manage.py runserver --settings=alpha.settings_local"
    echo "2. 访问: https://$DOMAIN"
    echo "3. 检查SSL评级: https://www.ssllabs.com/ssltest/"
    echo ""
    echo -e "${BLUE}管理命令:${NC}"
    echo "- 检查证书: python manage.py ssl_manager status"
    echo "- 续期证书: python manage.py ssl_manager renew"
    echo "- 生成配置: python manage.py ssl_manager config --domain=$DOMAIN"
    echo ""
    
    if [ "$DOMAIN" = "localhost" ]; then
        echo -e "${YELLOW}⚠️  开发环境提示:${NC}"
        echo "- 浏览器会显示证书不受信任的警告，这是正常的"
        echo "- 可以点击'高级'然后'继续访问'来忽略警告"
        echo "- 或者将自签名证书添加到系统信任列表"
    fi
}

# 如果直接执行脚本
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
