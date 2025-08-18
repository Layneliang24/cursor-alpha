@echo off
echo 正在清除Cursor缓存...

echo 关闭Cursor进程...
taskkill /f /im "Cursor.exe" 2>nul

echo 删除用户数据目录...
rmdir /s /q "%APPDATA%\Cursor" 2>nul
rmdir /s /q "%LOCALAPPDATA%\Cursor" 2>nul

echo 删除临时文件...
for /d %%i in ("%TEMP%\Cursor*") do rmdir /s /q "%%i" 2>nul
del /q "%TEMP%\Cursor*" 2>nul

echo 清除项目Python缓存...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f"

echo 清除完成！
echo 现在可以重新安装Cursor了。
pause