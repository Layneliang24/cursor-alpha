Write-Host "正在切换到 MySQL 数据库..." -ForegroundColor Green

Write-Host ""
Write-Host "1. 检查 MySQL 服务状态..." -ForegroundColor Yellow
docker-compose ps mysql

Write-Host ""
Write-Host "2. 启动 MySQL 服务（如果未运行）..." -ForegroundColor Yellow
docker-compose up -d mysql

Write-Host ""
Write-Host "3. 等待 MySQL 服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "4. 检查数据库连接..." -ForegroundColor Yellow
Set-Location backend
python manage.py wait_for_db

Write-Host ""
Write-Host "5. 执行数据库迁移..." -ForegroundColor Yellow
python manage.py migrate

Write-Host ""
Write-Host "6. 创建超级用户（如果需要）..." -ForegroundColor Yellow
python manage.py create_superuser_if_not_exists --username admin --email admin@example.com --password admin123456

Write-Host ""
Write-Host "7. 启动后端服务..." -ForegroundColor Yellow
python manage.py runserver 0.0.0.0:8000

Write-Host ""
Write-Host "MySQL 数据库切换完成！" -ForegroundColor Green
Write-Host "数据库配置：" -ForegroundColor Cyan
Write-Host "- 主机: 127.0.0.1:3307 (Docker) 或 127.0.0.1:3306 (本地)" -ForegroundColor White
Write-Host "- 数据库: alpha_db" -ForegroundColor White
Write-Host "- 用户: alpha_user" -ForegroundColor White
Write-Host "- 密码: alphapassword123" -ForegroundColor White
