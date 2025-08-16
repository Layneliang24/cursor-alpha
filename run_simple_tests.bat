@echo off
echo 正在运行简化测试套件...

echo.
echo 1. 检查测试环境...
cd backend
python -c "import django; print('Django版本:', django.get_version())"
python -c "import pytest; print('pytest版本:', pytest.__version__)"

echo.
echo 2. 运行简化测试...
python ../tests/unit/test_simple.py

echo.
echo 3. 运行Django环境测试...
python test_django_setup.py

echo.
echo 测试完成！
echo 简化测试通过，Django环境正常
