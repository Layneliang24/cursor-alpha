@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Alpha 项目一键部署脚本
echo ========================================
echo.

:: 设置颜色
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

:: 检查是否在项目根目录
if not exist "backend" (
    echo %RED%错误: 请在项目根目录运行此脚本%RESET%
    pause
    exit /b 1
)

echo %BLUE%第一步: 环境检查%RESET%
echo.

:: 检查Python
echo 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%错误: Python未安装或未配置PATH%RESET%
    echo 请安装Python 3.8+并配置环境变量
    pause
    exit /b 1
)
python --version
echo %GREEN%✓ Python环境正常%RESET%
echo.

:: 检查Node.js
echo 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%错误: Node.js未安装或未配置PATH%RESET%
    echo 请安装Node.js 16+并配置环境变量
    pause
    exit /b 1
)
node --version
echo %GREEN%✓ Node.js环境正常%RESET%
echo.

:: 检查Git
echo 检查Git环境...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %YELLOW%警告: Git未安装，某些功能可能受限%RESET%
) else (
    git --version
    echo %GREEN%✓ Git环境正常%RESET%
)
echo.

echo %BLUE%第二步: 后端环境搭建%RESET%
echo.

cd backend

:: 检查虚拟环境
if not exist "venv" (
    echo 创建Python虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo %RED%错误: 虚拟环境创建失败%RESET%
        pause
        exit /b 1
    )
    echo %GREEN%✓ 虚拟环境创建成功%RESET%
) else (
    echo %GREEN%✓ 虚拟环境已存在%RESET%
)

:: 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo %RED%错误: 虚拟环境激活失败%RESET%
    pause
    exit /b 1
)
echo %GREEN%✓ 虚拟环境激活成功%RESET%

:: 升级pip
echo 升级pip...
python -m pip install --upgrade pip
echo %GREEN%✓ pip升级完成%RESET%

:: 安装依赖
echo 安装Python依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo %YELLOW%警告: 部分依赖安装失败，尝试使用国内镜像%RESET%
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
    if %errorlevel% neq 0 (
        echo %RED%错误: 依赖安装失败%RESET%
        pause
        exit /b 1
    )
)
echo %GREEN%✓ Python依赖安装完成%RESET%

:: 安装测试依赖
echo 安装测试依赖...
pip install pytest pytest-django pytest-cov factory-boy faker
echo %GREEN%✓ 测试依赖安装完成%RESET%

:: 数据库迁移
echo 运行数据库迁移...
python manage.py migrate
if %errorlevel% neq 0 (
    echo %RED%错误: 数据库迁移失败%RESET%
    pause
    exit /b 1
)
echo %GREEN%✓ 数据库迁移完成%RESET%

:: 创建超级用户（可选）
echo.
set /p create_superuser="是否创建超级用户? (y/n): "
if /i "!create_superuser!"=="y" (
    echo 创建超级用户...
    python manage.py createsuperuser
    echo %GREEN%✓ 超级用户创建完成%RESET%
)

cd ..

echo.
echo %BLUE%第三步: 前端环境搭建%RESET%
echo.

cd frontend

:: 安装npm依赖
echo 安装Node.js依赖...
npm install
if %errorlevel% neq 0 (
    echo %YELLOW%警告: npm安装失败，尝试清除缓存后重试%RESET%
    npm cache clean --force
    npm install
    if %errorlevel% neq 0 (
        echo %RED%错误: npm依赖安装失败%RESET%
        pause
        exit /b 1
    )
)
echo %GREEN%✓ Node.js依赖安装完成%RESET%

cd ..

echo.
echo %BLUE%第四步: 测试环境验证%RESET%
echo.

cd backend

:: 运行基础测试
echo 运行基础测试验证环境...
python -m pytest ../tests/unit/test_basic.py -v
if %errorlevel% neq 0 (
    echo %YELLOW%警告: 基础测试失败，请检查环境配置%RESET%
) else (
    echo %GREEN%✓ 基础测试通过%RESET%
)

cd ..

echo.
echo %BLUE%第五步: 创建启动脚本%RESET%
echo.

:: 创建后端启动脚本
echo @echo off > start_backend.bat
echo echo 启动Django后端服务器... >> start_backend.bat
echo cd backend >> start_backend.bat
echo call venv\Scripts\activate.bat >> start_backend.bat
echo python manage.py runserver >> start_backend.bat
echo pause >> start_backend.bat

:: 创建前端启动脚本
echo @echo off > start_frontend.bat
echo echo 启动Vue前端服务器... >> start_frontend.bat
echo cd frontend >> start_frontend.bat
echo npm run dev >> start_frontend.bat
echo pause >> start_frontend.bat

:: 创建测试运行脚本
echo @echo off > run_tests.bat
echo echo 运行项目测试... >> run_tests.bat
echo cd backend >> run_tests.bat
echo call venv\Scripts\activate.bat >> run_tests.bat
echo python -m pytest ../tests/ --cov=apps --cov-report=html --cov-report=term-missing >> run_tests.bat
echo echo. >> run_tests.bat
echo echo 测试完成！覆盖率报告位置: tests/htmlcov/index.html >> run_tests.bat
echo pause >> run_tests.bat

echo %GREEN%✓ 启动脚本创建完成%RESET%

echo.
echo ========================================
echo %GREEN%🎉 项目部署完成！%RESET%
echo ========================================
echo.
echo %BLUE%可用的命令:%RESET%
echo   start_backend.bat    - 启动后端服务器
echo   start_frontend.bat   - 启动前端服务器
echo   run_tests.bat        - 运行所有测试
echo.
echo %BLUE%访问地址:%RESET%
echo   后端API: http://localhost:8000
echo   前端页面: http://localhost:5173
echo   Django管理后台: http://localhost:8000/admin
echo.
echo %BLUE%文档位置:%RESET%
echo   部署指南: docs/DEPLOYMENT_GUIDE.md
echo   测试指南: docs/TESTING_STANDARDS.md
echo   项目指南: docs/GUIDE.md
echo.
echo %YELLOW%注意: 首次启动可能需要一些时间来编译前端资源%RESET%
echo.
pause
