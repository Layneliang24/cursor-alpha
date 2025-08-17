Write-Host "运行新闻相关测试..." -ForegroundColor Green
Write-Host ""

Set-Location backend

Write-Host "1. 运行BBC新闻保存测试..." -ForegroundColor Yellow
python -m pytest ..\tests\unit\test_bbc_news_save.py -v
Write-Host ""

Write-Host "2. 运行TechCrunch和图片清理测试..." -ForegroundColor Yellow
python -m pytest ..\tests\unit\test_techcrunch_and_image_cleanup.py -v
Write-Host ""

Write-Host "3. 运行CNN爬虫测试..." -ForegroundColor Yellow
python -m pytest ..\tests\unit\test_cnn_crawler.py -v
Write-Host ""

Write-Host "4. 运行集成测试..." -ForegroundColor Yellow
python -m pytest ..\tests\integration\test_fixes_verification.py -v
Write-Host ""

Write-Host "5. 运行BBC修复验证测试..." -ForegroundColor Yellow
python -m pytest ..\tests\integration\test_bbc_fix_verification.py -v
Write-Host ""

Write-Host "测试完成！" -ForegroundColor Green
Read-Host "按任意键继续"




