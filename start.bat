@echo off
echo ========================================
echo    Alpha 技术共享平台启动脚本
echo ========================================
echo.

cd /d "S:\WorkShop\cursor\alpha"

:: 检查Python依赖
if not exist "backend\venv\" (
    echo [1/5] 首次运行，安装Python依赖...
    pip install -r backend/requirements.txt
) else (
    echo [1/5] Python依赖已安装，跳过...
)

echo.
echo [2/5] 检查Node.js依赖...
cd frontend
if not exist "node_modules\" (
    echo 安装前端依赖...
    npm install
) else (
    echo 前端依赖已安装，跳过...
)

echo.
echo [3/5] 检查数据库迁移...
cd ..\backend
python manage.py migrate --check >nul 2>&1
if errorlevel 1 (
    echo 需要运行数据库迁移...
    python manage.py makemigrations
    python manage.py migrate
) else (
    echo 数据库已是最新状态...
)

echo.
echo [4/5] 启动后端服务器...
echo 后端服务: http://127.0.0.1:8000
echo API文档: http://127.0.0.1:8000/api/swagger/
echo 管理员后台: http://127.0.0.1:8000/admin/
start "Django后端" cmd /k "python manage.py runserver"

echo.
echo [5/5] 启动前端服务器...
cd ..\frontend
echo 前端服务: http://127.0.0.1:5173
start "Vue前端" cmd /k "npm run dev"

echo.
echo ========================================
echo 服务已启动：
echo 前端: http://127.0.0.1:5173
echo 后端: http://127.0.0.1:8000
echo ========================================
echo.
echo 关闭此窗口不会停止服务
echo 要停止服务请关闭对应的命令行窗口
echo.

pause 