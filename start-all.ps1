# Alpha 项目一键启动脚本 (PowerShell版本)
Write-Host "========================================" -ForegroundColor Green
Write-Host "      Alpha 项目一键启动脚本" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""
Write-Host "此脚本将同时启动前端和后端服务" -ForegroundColor Yellow
Write-Host "请确保在项目根目录执行此脚本" -ForegroundColor Yellow
Write-Host ""

# 检查项目结构
if (-not (Test-Path "backend\manage.py")) {
    Write-Host "[错误] 找不到后端项目文件" -ForegroundColor Red
    Read-Host "按任意键继续"
    exit 1
}

if (-not (Test-Path "frontend\package.json")) {
    Write-Host "[错误] 找不到前端项目文件" -ForegroundColor Red
    Read-Host "按任意键继续"
    exit 1
}

# 启动后端服务（在新窗口）
Write-Host "[信息] 启动后端服务..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    cd backend
    python manage.py migrate --verbosity=0
    python manage.py create_test_learning_data --verbosity=0
    python manage.py runserver 0.0.0.0:8000
}

# 等待3秒
Start-Sleep -Seconds 3

# 启动前端服务（在新窗口）
Write-Host "[信息] 启动前端服务..." -ForegroundColor Cyan
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    cd frontend
    if (-not (Test-Path "node_modules")) {
        npm install
    }
    npm run dev
}

Write-Host ""
Write-Host "=======================================" -ForegroundColor Green
Write-Host "          服务启动完成！" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green
Write-Host ""
Write-Host "后端服务: http://localhost:8000" -ForegroundColor Yellow
Write-Host "前端服务: http://localhost:5173" -ForegroundColor Yellow
Write-Host "API文档:  http://localhost:8000/api/docs/" -ForegroundColor Yellow
Write-Host ""
Write-Host "服务已在后台启动，请等待服务完全启动" -ForegroundColor Yellow
Write-Host "如需查看服务状态，请运行: Get-Job" -ForegroundColor Yellow
Write-Host "如需停止服务，请运行: Stop-Job -Name 'backend', 'frontend'" -ForegroundColor Yellow
Write-Host ""

# 显示服务状态
Write-Host "当前服务状态:" -ForegroundColor Cyan
Get-Job | Format-Table -AutoSize

Read-Host "按任意键继续"
