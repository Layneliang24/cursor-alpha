@echo off
echo ========================================
echo    Alpha 技术共享平台 - 后端启动脚本
echo ========================================
echo.

cd /d "S:\WorkShop\cursor\alpha\backend"

echo [1/4] 检查Python环境...
py --version
if errorlevel 1 (
    echo 错误：未找到Python环境
    pause
    exit /b 1
)

echo.
echo [2/4] 安装依赖包...
pip install -r requirements.txt

echo.
echo [3/4] 执行数据库迁移...
py manage.py makemigrations
py manage.py migrate

echo.
echo [4/4] 创建测试数据...
py create_test_data.py

echo.
echo ========================================
echo 🚀 启动Django开发服务器...
echo ========================================
echo.
echo 访问地址：
echo 网站首页: http://127.0.0.1:8000/
echo API接口: http://127.0.0.1:8000/api/
echo 管理后台: http://127.0.0.1:8000/admin/
echo.
echo 按 Ctrl+Break 停止服务器
echo.

py manage.py runserver 8000

pause