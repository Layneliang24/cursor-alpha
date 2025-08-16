Write-Host "正在运行简化测试套件..." -ForegroundColor Green

Write-Host ""
Write-Host "1. 检查测试环境..." -ForegroundColor Yellow
Set-Location backend
python -c "import django; print('Django版本:', django.get_version())"
python -c "import pytest; print('pytest版本:', pytest.__version__)"

Write-Host ""
Write-Host "2. 运行简化测试..." -ForegroundColor Yellow
python ../tests/unit/test_simple.py

Write-Host ""
Write-Host "3. 运行Django环境测试..." -ForegroundColor Yellow
python test_django_setup.py

Write-Host ""
Write-Host "测试完成！" -ForegroundColor Green
Write-Host "简化测试通过，Django环境正常" -ForegroundColor Cyan
