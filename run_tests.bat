@echo off
echo 正在运行测试套件...

echo.
echo 1. 检查测试环境...
cd backend
python -c "import django; print('Django版本:', django.get_version())"
python -c "import pytest; print('pytest版本:', pytest.__version__)"

echo.
echo 2. 运行单元测试...
python -m pytest ../tests/unit/ -v --tb=short

echo.
echo 3. 运行集成测试...
python -m pytest ../tests/integration/ -v --tb=short

echo.
echo 4. 生成覆盖率报告...
python -m pytest ../tests/ --cov=apps --cov-report=html --cov-report=term-missing

echo.
echo 5. 运行快速测试...
python -m pytest ../tests/ -m fast -v

echo.
echo 测试完成！
echo 覆盖率报告位置: htmlcov/index.html
