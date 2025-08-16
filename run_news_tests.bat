@echo off
echo 运行新闻相关测试...
echo.

cd backend

echo 1. 运行BBC新闻保存测试...
python -m pytest ..\tests\unit\test_bbc_news_save.py -v
echo.

echo 2. 运行TechCrunch和图片清理测试...
python -m pytest ..\tests\unit\test_techcrunch_and_image_cleanup.py -v
echo.

echo 3. 运行CNN爬虫测试...
python -m pytest ..\tests\unit\test_cnn_crawler.py -v
echo.

echo 4. 运行集成测试...
python -m pytest ..\tests\integration\test_fixes_verification.py -v
echo.

echo 5. 运行BBC修复验证测试...
python -m pytest ..\tests\integration\test_bbc_fix_verification.py -v
echo.

echo 测试完成！
pause

