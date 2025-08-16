@echo off
echo ========================================
echo CI/CD 配置诊断工具
echo ========================================

echo.
echo 正在检查CI/CD配置...
echo.

echo 1. 检查GitHub Actions配置文件...
if exist ".github\workflows\deploy.yml" (
    echo ✅ deploy.yml 存在
) else (
    echo ❌ deploy.yml 不存在
)

if exist ".github\workflows\test.yml" (
    echo ✅ test.yml 存在
) else (
    echo ❌ test.yml 不存在
)

echo.
echo 2. 检查必需的环境变量...
echo 当前deploy.yml需要以下Secrets：
echo    - HOST
echo    - USERNAME  
echo    - SSH_KEY
echo    - PORT
echo    - PROJECT_DIR
echo    - PASS_PHRASE (可选)

echo.
echo 3. 可能的解决方案：
echo.
echo 方案A: 检查GitHub Secrets
echo    1. 进入GitHub仓库
echo    2. 点击 Settings → Secrets and variables → Actions
echo    3. 检查以下Secrets是否存在且不为空：
echo       - HOST
echo       - USERNAME
echo       - SSH_KEY
echo       - PORT
echo       - PROJECT_DIR
echo.
echo 方案B: 重新设置Secrets
echo    1. 删除现有的Secrets
echo    2. 重新添加Secrets
echo    3. 确保SSH_KEY包含完整的私钥内容
echo.
echo 方案C: 使用测试配置
echo    1. 暂时禁用deploy.yml
echo    2. 使用test.yml进行测试
echo    3. 解决Secrets问题后再启用部署
echo.

echo 4. 快速修复步骤：
echo.
echo 步骤1: 检查GitHub Secrets
echo    访问: https://github.com/[用户名]/[仓库名]/settings/secrets/actions
echo.
echo 步骤2: 验证SSH连接
echo    ssh -i ~/.ssh/id_rsa [用户名]@[服务器IP]
echo.
echo 步骤3: 测试部署配置
echo    手动运行: .github/workflows/deploy.yml
echo.

echo 5. 临时解决方案：
echo    - 使用测试CI配置避免部署错误
echo    - 在本地运行测试: run_tests.bat
echo    - 查看详细配置指南: docs/CI_CD_SETUP.md
echo.

pause
