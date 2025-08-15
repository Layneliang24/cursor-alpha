@echo off
echo ========================================
echo Alpha 项目测试运行脚本
echo ========================================

cd backend

echo.
echo 1. 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: Python未安装或未配置PATH
    pause
    exit /b 1
)

echo.
echo 2. 安装测试依赖...
pip install pytest pytest-django pytest-cov factory-boy faker

echo.
echo 3. 运行数据库迁移...
python manage.py migrate

echo.
echo 4. 运行测试...
cd tests
pytest --cov=apps --cov-report=html --cov-report=term-missing

echo.
echo 5. 测试完成！
echo 覆盖率报告位置: tests/htmlcov/index.html
echo.
pause
