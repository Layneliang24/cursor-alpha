@echo off
chcp 65001 >nul
echo 🚀 Alpha 项目开发环境启动器
echo.

REM 检查目录结构
if not exist "backend" (
    echo ❌ 错误：backend 目录不存在
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ 错误：frontend 目录不存在
    pause
    exit /b 1
)

echo ✅ 项目结构检查通过
echo.
echo 请选择启动方式：
echo 1. 启动后端服务（Django + 热重载）
echo 2. 启动前端服务（Vite + 热重载）
echo 3. 启动前后端服务（需要两个终端）
echo 4. 退出
echo.

set /p choice=请输入选择 (1-4): 

if "%choice%"=="1" (
    echo.
    echo 🔥 启动后端服务...
    cd backend
    call run_dev.bat
) else if "%choice%"=="2" (
    echo.
    echo 🎨 启动前端服务...
    cd frontend
    call run_dev.bat
) else if "%choice%"=="3" (
    echo.
    echo 📝 提示：需要打开两个终端窗口
    echo 终端1：运行 start_dev.bat 选择 1（后端）
    echo 终端2：运行 start_dev.bat 选择 2（前端）
    echo.
    echo 按任意键继续...
    pause >nul
) else if "%choice%"=="4" (
    echo 👋 再见！
    exit /b 0
) else (
    echo ❌ 无效选择
    pause
    exit /b 1
)
