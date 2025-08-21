@echo off
chcp 65001 >nul
echo 🎨 启动 Alpha 前端开发环境...
echo.

REM 检查 Node.js 环境
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：Node.js 未安装或未添加到 PATH
    pause
    exit /b 1
)

REM 检查 npm 环境
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：npm 未安装或未添加到 PATH
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo 🔥 启动 Vite 开发服务器（支持热重载）...
echo 📝 提示：修改代码后浏览器会自动刷新
echo 🛑 按 Ctrl+C 停止服务
echo.

REM 启动开发服务器
npm run dev

echo.
echo 🛑 服务已停止
pause
