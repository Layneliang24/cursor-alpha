Write-Host "正在运行测试套件..." -ForegroundColor Green

Write-Host ""
Write-Host "1. 检查测试环境..." -ForegroundColor Yellow
Set-Location backend
python -c "import django; print('Django版本:', django.get_version())"
python -c "import pytest; print('pytest版本:', pytest.__version__)"

Write-Host ""
Write-Host "2. 运行单元测试..." -ForegroundColor Yellow
python -m pytest ../tests/unit/ -v --tb=short

Write-Host ""
Write-Host "3. 运行集成测试..." -ForegroundColor Yellow
python -m pytest ../tests/integration/ -v --tb=short

Write-Host ""
Write-Host "4. 生成覆盖率报告..." -ForegroundColor Yellow
python -m pytest ../tests/ --cov=apps --cov-report=html --cov-report=term-missing

Write-Host ""
Write-Host "5. 运行快速测试..." -ForegroundColor Yellow
python -m pytest ../tests/ -m fast -v

Write-Host ""
Write-Host "测试完成！" -ForegroundColor Green
Write-Host "覆盖率报告位置: htmlcov/index.html" -ForegroundColor Cyan
