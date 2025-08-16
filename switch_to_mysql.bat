@echo off
echo 正在切换到 MySQL 数据库...

echo.
echo 1. 检查 MySQL 服务状态...
docker-compose ps mysql

echo.
echo 2. 启动 MySQL 服务（如果未运行）...
docker-compose up -d mysql

echo.
echo 3. 等待 MySQL 服务启动...
timeout /t 10 /nobreak

echo.
echo 4. 检查数据库连接...
cd backend
python manage.py wait_for_db

echo.
echo 5. 执行数据库迁移...
python manage.py migrate

echo.
echo 6. 创建超级用户（如果需要）...
python manage.py create_superuser_if_not_exists --username admin --email admin@example.com --password admin123456

echo.
echo 7. 启动后端服务...
python manage.py runserver 0.0.0.0:8000

echo.
echo MySQL 数据库切换完成！
echo 数据库配置：
echo - 主机: 127.0.0.1:3307 (Docker) 或 127.0.0.1:3306 (本地)
echo - 数据库: alpha_db
echo - 用户: alpha_user
echo - 密码: alphapassword123
