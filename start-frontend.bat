@echo off
chcp 65001 >nul
echo ========================================
echo       Alpha 项目前端启动脚本
echo ========================================
echo.

:: 检查Node.js是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Node.js 未安装或不在PATH中
    echo 请安装Node.js 16+并添加到系统PATH
    pause
    exit /b 1
)

:: 检查npm是否安装
npm --version >nul 2>&1
if errorlevel 1 (
    echo [错误] npm 未安装或不在PATH中
    pause
    exit /b 1
)

:: 进入前端目录
if not exist "frontend\package.json" (
    echo [错误] 找不到 frontend\package.json 文件
    echo 请确保在项目根目录执行此脚本
    pause
    exit /b 1
)

cd frontend
echo [信息] 切换到前端目录: %CD%

:: 安装依赖（如果需要）
if not exist "node_modules" (
    echo [信息] 首次运行，正在安装依赖...
    npm install
) else (
    echo [信息] 检查并更新依赖...
    npm install --silent
)

:: 启动开发服务器
echo.
echo ========================================
echo     Vite 前端服务器启动中...
echo     访问地址: http://localhost:5173
echo     按 Ctrl+C 停止服务器
echo ========================================
echo.

npm run dev

pause
