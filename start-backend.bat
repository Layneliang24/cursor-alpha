@echo off
chcp 65001 >nul
echo ========================================
echo       Alpha 项目后端启动脚本
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python 未安装或不在PATH中
    echo 请安装Python 3.8+并添加到系统PATH
    pause
    exit /b 1
)

:: 进入后端目录
if not exist "backend\manage.py" (
    echo [错误] 找不到 backend\manage.py 文件
    echo 请确保在项目根目录执行此脚本
    pause
    exit /b 1
)

cd backend
echo [信息] 切换到后端目录: %CD%

:: 检查虚拟环境（可选）
if exist "venv\Scripts\activate.bat" (
    echo [信息] 发现虚拟环境，正在激活...
    call venv\Scripts\activate.bat
)

:: 安装依赖（如果需要）
if not exist "requirements.txt" (
    echo [警告] 找不到 requirements.txt 文件
) else (
    echo [信息] 检查Python依赖...
    pip install -r requirements.txt --quiet
)

:: 数据库迁移
echo [信息] 执行数据库迁移...
python manage.py migrate --verbosity=0

:: 创建测试数据（可选）
echo [信息] 创建测试数据...
python manage.py import_english_seed --file ../tests/fixtures/english_seed.json --verbosity=0

:: 启动开发服务器
echo.
echo ========================================
echo    Django 后端服务器启动中...
echo    访问地址: http://localhost:8000
echo    API文档: http://localhost:8000/api/docs/
echo    按 Ctrl+C 停止服务器
echo ========================================
echo.

python manage.py runserver 0.0.0.0:8000

pause
