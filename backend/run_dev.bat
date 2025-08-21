@echo off
chcp 65001 >nul
echo 🚀 启动 Alpha 项目开发环境...
echo.

REM 检查 Python 环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：Python 未安装或未添加到 PATH
    pause
    exit /b 1
)

REM 检查 Django 环境
if not exist "manage.py" (
    echo ❌ 错误：请在 backend 目录下运行此脚本
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo 🔥 启动 Django 开发服务器（支持热重载）...
echo 📝 提示：修改代码后服务器会自动重载
echo 🛑 按 Ctrl+C 停止服务
echo.

REM 尝试使用 django-extensions 的 runserver_plus
echo 尝试启动 runserver_plus...
python manage.py runserver_plus --reloader-type=stat --verbosity=2 0.0.0.0:8000

REM 如果 runserver_plus 失败，使用标准 Django 服务器
if errorlevel 1 (
    echo.
    echo 💡 runserver_plus 启动失败，尝试使用标准 Django 服务器...
    echo.
    python manage.py runserver --verbosity=2 0.0.0.0:8000
)

echo.
echo 🛑 服务已停止
pause
