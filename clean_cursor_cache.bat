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

:: 核弹级清理模式
echo ██ 正在执行深度清理...

echo [×] 用户配置文件
rmdir /s /q "%APPDATA%\Cursor\User Data" 2>nul
rmdir /s /q "%APPDATA%\Cursor\Local Storage" 2>nul

echo [×] 浏览器扩展数据
rmdir /s /q "%LOCALAPPDATA%\Cursor\Extensions" 2>nul
rmdir /s /q "%LOCALAPPDATA%\Cursor\Extension State" 2>nul

echo [×] 用户偏好设置
reg delete "HKCU\Software\Cursor" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Cursor" /f >nul 2>&1
PowerShell -Command "Remove-Item -Path 'HKCU:\Environment\Cursor*' -Force" 2>nul

:: 应用程序日志
echo [√] 程序日志文件
del /q "%APPDATA%\Cursor\*.log" 2>nul
del /q "%APPDATA%\Cursor\*.log.*" 2>nul

:: 临时文件
echo [√] 临时工作文件
PowerShell -Command "Remove-Item -Path $env:TEMP\Cursor* -Recurse -Force -ErrorAction SilentlyContinue"

echo ---------------------------------
echo 操作安全提示：
echo █ 已删除：用户配置/扩展数据/本地存储
█ 已清除：注册表设置/环境变量
█ 保留：软件安装目录与激活信息
echo ---------------------------------

start "" "%LOCALAPPDATA%\Programs\Cursor\Cursor.exe"
echo 缓存清理完成！10秒后自动关闭...
timeout /t 10 >nul
exit