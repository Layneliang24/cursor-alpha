@echo off
echo ========================================
echo    Alpha 技术共享平台启动脚本
echo ========================================
echo.

cd /d "S:\WorkShop\cursor\alpha"

echo [1/4] 安装Python依赖...
pip install -r backend/requirements.txt

echo.
echo [2/4] 运行数据库迁移...
cd backend
python manage.py makemigrations
python manage.py migrate

echo.
echo [3/4] 创建超级用户...
echo 请按提示创建管理员账号...
python manage.py createsuperuser

echo.
echo [4/4] 启动Django服务器...
echo 后端服务将在 http://127.0.0.1:8000 启动
echo API文档: http://127.0.0.1:8000/api/swagger/
echo 管理员后台: http://127.0.0.1:8000/admin/
echo.
echo 按 Ctrl+C 停止服务器
echo.

python manage.py runserver

pause 