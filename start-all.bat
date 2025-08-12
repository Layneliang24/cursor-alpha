@echo off
echo ========================================
echo       Alpha 项目一键启动脚本
echo ========================================
echo.
echo 此脚本将同时启动前端和后端服务
echo 请确保在项目根目录执行此脚本
echo.
pause

:: 检查项目结构
if not exist "backend\manage.py" (
    echo [错误] 找不到后端项目文件
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo [错误] 找不到前端项目文件
    pause
    exit /b 1
)

:: 启动后端服务（在新窗口）
echo [信息] 启动后端服务...
start "Alpha Backend" cmd /c "start-backend.bat"

:: 等待2秒
timeout /t 2 /nobreak >nul

:: 启动前端服务（在新窗口）
echo [信息] 启动前端服务...
start "Alpha Frontend" cmd /c "start-frontend.bat"

echo.
echo ========================================
echo          服务启动完成！
echo ========================================
echo.
echo 后端服务: http://localhost:8000
echo 前端服务: http://localhost:5173
echo API文档:  http://localhost:8000/api/docs/
echo.
echo 两个服务窗口已打开，请等待服务完全启动
echo 如需停止服务，请关闭对应的窗口
echo.
pause
