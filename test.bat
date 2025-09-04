@echo off
setlocal enabledelayedexpansion

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="test" goto test
if "%1"=="test-backend" goto test-backend
if "%1"=="test-frontend" goto test-frontend
if "%1"=="test-e2e" goto test-e2e
if "%1"=="cov" goto cov
if "%1"=="cov-backend" goto cov-backend
if "%1"=="cov-frontend" goto cov-frontend
if "%1"=="lint" goto lint
if "%1"=="format" goto format
if "%1"=="complexity" goto complexity
if "%1"=="clean" goto clean
if "%1"=="install" goto install
if "%1"=="verify" goto verify
goto help

:help
echo Alpha Platform 测试体系命令:
echo.
echo 测试相关:
echo   test          - 运行所有测试 (后端 + 前端 + E2E)
echo   test-backend  - 运行后端测试
echo   test-frontend - 运行前端单元测试
echo   test-e2e      - 运行端到端测试
echo.
echo 覆盖率相关:
echo   cov           - 生成覆盖率报告
echo   cov-backend   - 生成后端覆盖率报告
echo   cov-frontend  - 生成前端覆盖率报告
echo.
echo 代码质量:
echo   lint          - 代码质量检查
echo   format        - 代码格式化
echo   complexity    - 代码复杂度分析
echo.
echo 环境管理:
echo   install       - 安装依赖
echo   clean         - 清理临时文件
echo   verify        - 验证测试环境
goto end

:test
echo 🧪 运行所有测试...
call :test-backend
call :test-frontend
call :test-e2e
echo ✅ 所有测试完成!
goto end

:test-backend
echo 🧪 运行后端测试...
cd backend
python -m pytest tests/ -v --tb=short --strict-markers
cd ..
goto end

:test-frontend
echo 🧪 运行前端单元测试...
npm run test:unit
goto end

:test-e2e
echo 🧪 运行端到端测试...
npm run test:e2e
goto end

:cov
echo 📊 生成覆盖率报告...
call :cov-backend
call :cov-frontend
echo 📊 覆盖率报告生成完成!
goto end

:cov-backend
echo 📊 生成后端覆盖率报告...
cd backend
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing --cov-config=.coveragerc
cd ..
goto end

:cov-frontend
echo 📊 生成前端覆盖率报告...
npm run test:coverage
goto end

:lint
echo 🔍 检查代码质量...
echo 检查后端代码...
cd backend
flake8 . --max-line-length=120 --extend-ignore=E203,W503
cd ..
echo 检查前端代码...
npm run lint
goto end

:format
echo ✨ 格式化代码...
echo 格式化后端代码...
cd backend
black . --line-length=120
isort .
cd ..
echo 格式化前端代码...
npm run format
goto end

:complexity
echo 📈 分析代码复杂度...
cd backend
radon cc . -a -nc
radon mi . -a
radon hal . -a
cd ..
goto end

:clean
echo 🧹 清理临时文件...
for /r . %%i in (*.pyc) do del "%%i" 2>nul
for /d /r . %%i in (__pycache__) do rmdir /s /q "%%i" 2>nul
del .coverage 2>nul
for /d /r . %%i in (htmlcov) do rmdir /s /q "%%i" 2>nul
for /d /r . %%i in (.pytest_cache) do rmdir /s /q "%%i" 2>nul
goto end

:install
echo 📦 安装依赖...
echo 安装后端依赖...
pip install -r backend/requirements.txt
echo 安装前端依赖...
npm install
echo 安装Playwright浏览器...
npx playwright install
goto end

:verify
echo 🔍 验证测试环境...
echo 检查Python版本...
python --version
echo 检查Django版本...
cd backend
python -c "import django; print(f'Django {django.get_version()}')"
cd ..
echo 检查pytest版本...
pytest --version
echo 检查Node版本...
node --version
echo 检查npm版本...
npm --version
echo ✅ 测试环境验证完成!
goto end

:end
endlocal
