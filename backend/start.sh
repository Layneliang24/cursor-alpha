#!/bin/bash

# 生产环境启动脚本
echo "🚀 启动Alpha项目..."

# 等待数据库准备就绪
echo "⏳ 等待MySQL数据库连接..."
python manage.py wait_for_db

# 运行数据库迁移
echo "🗄️ 运行数据库迁移..."
python manage.py migrate

# 收集静态文件
echo "📁 收集静态文件..."
python manage.py collectstatic --noinput

# 创建超级用户（如果不存在）
echo "👤 检查超级用户..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户创建成功: admin/admin123')
else:
    print('超级用户已存在')
"

# 启动Gunicorn服务器
echo "🌐 启动Gunicorn服务器..."
exec gunicorn alpha.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class gthread \
    --threads 2 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
