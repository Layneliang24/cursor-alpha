param(
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Alpha Platform 测试体系命令:" -ForegroundColor Green
    Write-Host ""
    Write-Host "测试相关:" -ForegroundColor Yellow
    Write-Host "  test          - 运行所有测试 (后端 + 前端 + E2E)"
    Write-Host "  test-backend  - 运行后端测试"
    Write-Host "  test-frontend - 运行前端单元测试"
    Write-Host "  test-e2e      - 运行端到端测试"
    Write-Host ""
    Write-Host "覆盖率相关:" -ForegroundColor Yellow
    Write-Host "  cov           - 生成覆盖率报告"
    Write-Host "  cov-backend   - 生成后端覆盖率报告"
    Write-Host "  cov-frontend  - 生成前端覆盖率报告"
    Write-Host ""
    Write-Host "代码质量:" -ForegroundColor Yellow
    Write-Host "  lint          - 代码质量检查"
    Write-Host "  format        - 代码格式化"
    Write-Host "  complexity    - 代码复杂度分析"
    Write-Host ""
    Write-Host "环境管理:" -ForegroundColor Yellow
    Write-Host "  install       - 安装依赖"
    Write-Host "  clean         - 清理临时文件"
    Write-Host "  verify        - 验证测试环境"
}

function Test-Backend {
    Write-Host "🧪 运行后端测试..." -ForegroundColor Blue
    Set-Location backend
    python -m pytest tests/ -v --tb=short --strict-markers
    Set-Location ..
}

function Test-Frontend {
    Write-Host "🧪 运行前端单元测试..." -ForegroundColor Blue
    npm run test:unit
}

function Test-E2E {
    Write-Host "🧪 运行端到端测试..." -ForegroundColor Blue
    npm run test:e2e
}

function Test-All {
    Write-Host "🧪 运行所有测试..." -ForegroundColor Blue
    Test-Backend
    Test-Frontend
    Test-E2E
    Write-Host "✅ 所有测试完成!" -ForegroundColor Green
}

function Get-Coverage {
    Write-Host "📊 生成覆盖率报告..." -ForegroundColor Blue
    Get-CoverageBackend
    Get-CoverageFrontend
    Write-Host "📊 覆盖率报告生成完成!" -ForegroundColor Green
}

function Get-CoverageBackend {
    Write-Host "📊 生成后端覆盖率报告..." -ForegroundColor Blue
    Set-Location backend
    python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing --cov-config=.coveragerc
    Set-Location ..
}

function Get-CoverageFrontend {
    Write-Host "📊 生成前端覆盖率报告..." -ForegroundColor Blue
    npm run test:coverage
}

function Test-Lint {
    Write-Host "🔍 检查代码质量..." -ForegroundColor Blue
    Write-Host "检查后端代码..." -ForegroundColor Yellow
    Set-Location backend
    flake8 . --max-line-length=120 --extend-ignore=E203,W503
    Set-Location ..
    Write-Host "检查前端代码..." -ForegroundColor Yellow
    npm run lint
}

function Format-Code {
    Write-Host "✨ 格式化代码..." -ForegroundColor Blue
    Write-Host "格式化后端代码..." -ForegroundColor Yellow
    Set-Location backend
    black . --line-length=120
    isort .
    Set-Location ..
    Write-Host "格式化前端代码..." -ForegroundColor Yellow
    npm run format
}

function Test-Complexity {
    Write-Host "📈 分析代码复杂度..." -ForegroundColor Blue
    Set-Location backend
    radon cc . -a -nc
    radon mi . -a
    radon hal . -a
    Set-Location ..
}

function Clean-Files {
    Write-Host "🧹 清理临时文件..." -ForegroundColor Blue
    Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item ".coverage" -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Directory -Name "htmlcov" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Directory -Name ".pytest_cache" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

function Install-Dependencies {
    Write-Host "📦 安装依赖..." -ForegroundColor Blue
    Write-Host "安装后端依赖..." -ForegroundColor Yellow
    pip install -r backend/requirements.txt
    Write-Host "安装前端依赖..." -ForegroundColor Yellow
    npm install
    Write-Host "安装Playwright浏览器..." -ForegroundColor Yellow
    npx playwright install
}

function Test-Verify {
    Write-Host "🔍 验证测试环境..." -ForegroundColor Blue
    Write-Host "检查Python版本..." -ForegroundColor Yellow
    python --version
    Write-Host "检查Django版本..." -ForegroundColor Yellow
    Set-Location backend
    python -c "import django; print(f'Django {django.get_version()}')"
    Set-Location ..
    Write-Host "检查pytest版本..." -ForegroundColor Yellow
    pytest --version
    Write-Host "检查Node版本..." -ForegroundColor Yellow
    node --version
    Write-Host "检查npm版本..." -ForegroundColor Yellow
    npm --version
    Write-Host "✅ 测试环境验证完成!" -ForegroundColor Green
}

# 主执行逻辑
switch ($Command) {
    "help" { Show-Help }
    "test" { Test-All }
    "test-backend" { Test-Backend }
    "test-frontend" { Test-Frontend }
    "test-e2e" { Test-E2E }
    "cov" { Get-Coverage }
    "cov-backend" { Get-CoverageBackend }
    "cov-frontend" { Get-CoverageFrontend }
    "lint" { Test-Lint }
    "format" { Format-Code }
    "complexity" { Test-Complexity }
    "clean" { Clean-Files }
    "install" { Install-Dependencies }
    "verify" { Test-Verify }
    default { 
        Write-Host "❌ 未知命令: $Command" -ForegroundColor Red
        Show-Help
    }
}
