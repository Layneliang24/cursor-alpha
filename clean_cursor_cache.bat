@echo off
chcp 65001 >nul
echo ██ Cursor智能缓存清理工具 v2.1

:: 请求管理员权限
fltmc >nul 2>&1 || (
    echo 正在请求管理员权限...
    PowerShell -Command "Start-Process cmd -ArgumentList '/c %~s0' -Verb RunAs"
    exit /b
)

echo 正在安全终止Cursor进程...
taskkill /im "Cursor.exe" >nul 2>&1
timeout /t 3 /nobreak >nul
taskkill /f /im "Cursor.exe" 2>nul

echo ---------------------------------
echo 正在清理以下缓存内容：

:: 浏览器类型缓存
echo [√] 浏览器缓存文件
rmdir /s /q "%LOCALAPPDATA%\Cursor\Cache" 2>nul
rmdir /s /q "%LOCALAPPDATA%\Cursor\Code Cache" 2>nul
rmdir /s /q "%LOCALAPPDATA%\Cursor\GPUCache" 2>nul

:: 应用程序日志
echo [√] 程序日志文件
del /q "%APPDATA%\Cursor\*.log" 2>nul
del /q "%APPDATA%\Cursor\*.log.*" 2>nul

:: 临时文件
echo [√] 临时工作文件
PowerShell -Command "Remove-Item -Path $env:TEMP\Cursor* -Recurse -Force -ErrorAction SilentlyContinue"

echo ---------------------------------
echo 操作安全提示：
echo 1. 已保留用户配置文件和扩展程序
echo 2. 已保留历史记录和自定义设置
echo ---------------------------------

start "" "%LOCALAPPDATA%\Programs\Cursor\Cursor.exe"
echo 缓存清理完成！10秒后自动关闭...
timeout /t 10 >nul
exit