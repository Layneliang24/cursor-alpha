@echo off
echo 设置远程仓库并推送...
echo.

REM 添加远程仓库（请替换为您的实际仓库地址）
git remote add origin https://github.com/Layneliang24/alpha-project.git

REM 重命名分支为main
git branch -M main

REM 推送到远程仓库
git push -u origin main

echo.
echo 推送完成！
pause