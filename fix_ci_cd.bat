@echo off
echo ========================================
echo CI/CD 环境变量配置助手
echo ========================================

echo.
echo 当前CI/CD报错：缺少必需的环境变量
echo 请按照以下步骤配置GitHub Secrets：
echo.

echo 1. 生成SSH密钥对（如果还没有）
echo    ssh-keygen -t rsa -b 4096 -C "deploy@alpha.com"
echo.

echo 2. 查看公钥（添加到服务器）
echo    cat ~/.ssh/id_rsa.pub
echo.

echo 3. 查看私钥（添加到GitHub Secrets）
echo    cat ~/.ssh/id_rsa
echo.

echo 4. 在GitHub仓库中设置以下Secrets：
echo    - HOST: 服务器IP地址
echo    - USERNAME: SSH用户名
echo    - SSH_KEY: SSH私钥内容
echo    - PORT: SSH端口（通常是22）
echo    - PROJECT_DIR: 项目部署目录
echo.

echo 5. 配置服务器：
echo    - 创建部署用户
echo    - 添加SSH公钥
echo    - 设置项目目录权限
echo.

echo 详细配置指南请查看：docs/CI_CD_SETUP.md
echo.

echo 临时解决方案：
echo - 使用测试CI配置：.github/workflows/test.yml
echo - 只进行测试，不进行部署
echo - 避免环境变量问题
echo.

pause
