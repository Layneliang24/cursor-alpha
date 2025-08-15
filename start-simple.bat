@echo off
echo ========================================
echo       Alpha Project Startup Script
echo ========================================
echo.
echo This script will start both frontend and backend services
echo Please ensure you are in the project root directory
echo.

:: Check project structure
if not exist "backend\manage.py" (
    echo [ERROR] Backend project files not found
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo [ERROR] Frontend project files not found
    pause
    exit /b 1
)

:: Start backend service (in new window)
echo [INFO] Starting backend service...
start "Alpha Backend" cmd /k "cd /d %CD% && cd backend && python manage.py migrate --verbosity=0 && python manage.py import_english_seed --file ../tests/fixtures/english_seed.json --verbosity=0 && python manage.py runserver 0.0.0.0:8000"

:: Wait 3 seconds
timeout /t 3 /nobreak >nul

:: Start frontend service (in new window)
echo [INFO] Starting frontend service...
start "Alpha Frontend" cmd /k "cd /d %CD% && cd frontend && npm install --silent && npm run dev"

echo.
echo ========================================
echo          Services Started!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/api/docs/
echo.
echo Two service windows have been opened
echo Please wait for services to fully start
echo To stop services, close the corresponding windows
echo.
pause

