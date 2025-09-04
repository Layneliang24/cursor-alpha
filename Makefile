# Alpha Platform 测试体系 Makefile
# 提供一键测试、覆盖率、代码质量检查等命令

.PHONY: help test test-backend test-frontend test-e2e cov lint format clean install

# 默认目标
help:
	@echo "Alpha Platform 测试体系命令:"
	@echo ""
	@echo "测试相关:"
	@echo "  test          - 运行所有测试 (后端 + 前端 + E2E)"
	@echo "  test-backend  - 运行后端测试"
	@echo "  test-frontend - 运行前端单元测试"
	@echo "  test-e2e      - 运行端到端测试"
	@echo "  test-fast     - 快速测试 (跳过慢速测试)"
	@echo ""
	@echo "覆盖率相关:"
	@echo "  cov           - 生成覆盖率报告"
	@echo "  cov-backend   - 生成后端覆盖率报告"
	@echo "  cov-frontend  - 生成前端覆盖率报告"
	@echo "  cov-open      - 打开覆盖率报告"
	@echo ""
	@echo "代码质量:"
	@echo "  lint          - 代码质量检查"
	@echo "  format        - 代码格式化"
	@echo "  complexity    - 代码复杂度分析"
	@echo ""
	@echo "环境管理:"
	@echo "  install       - 安装依赖"
	@echo "  clean         - 清理临时文件"
	@echo "  reset         - 重置测试环境"

# 安装依赖
install:
	@echo "安装后端依赖..."
	pip install -r backend/requirements.txt
	@echo "安装前端依赖..."
	npm install
	@echo "安装Playwright浏览器..."
	npx playwright install

# 运行所有测试
test: test-backend test-frontend test-e2e
	@echo "✅ 所有测试完成!"

# 运行后端测试
test-backend:
	@echo "🧪 运行后端测试..."
	cd backend && python -m pytest tests/ -v --tb=short --strict-markers

# 运行前端单元测试
test-frontend:
	@echo "🧪 运行前端单元测试..."
	npm run test:unit

# 运行端到端测试
test-e2e:
	@echo "🧪 运行端到端测试..."
	npm run test:e2e

# 快速测试 (跳过慢速测试)
test-fast:
	@echo "🚀 运行快速测试..."
	cd backend && python -m pytest tests/ -v --tb=short -m "not slow" --strict-markers

# 生成覆盖率报告
cov: cov-backend cov-frontend
	@echo "📊 覆盖率报告生成完成!"

# 生成后端覆盖率报告
cov-backend:
	@echo "📊 生成后端覆盖率报告..."
	cd backend && python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing --cov-config=.coveragerc

# 生成前端覆盖率报告
cov-frontend:
	@echo "📊 生成前端覆盖率报告..."
	npm run test:coverage

# 打开覆盖率报告
cov-open:
	@echo "🌐 打开覆盖率报告..."
	cd backend && python -m webbrowser -t "htmlcov/index.html"

# 代码质量检查
lint:
	@echo "🔍 检查代码质量..."
	@echo "检查后端代码..."
	cd backend && flake8 . --max-line-length=120 --extend-ignore=E203,W503
	@echo "检查前端代码..."
	npm run lint

# 代码格式化
format:
	@echo "✨ 格式化代码..."
	@echo "格式化后端代码..."
	cd backend && black . --line-length=120
	cd backend && isort .
	@echo "格式化前端代码..."
	npm run format

# 代码复杂度分析
complexity:
	@echo "📈 分析代码复杂度..."
	cd backend && radon cc . -a -nc
	cd backend && radon mi . -a
	cd backend && radon hal . -a

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "node_modules/.cache" -exec rm -rf {} +

# 重置测试环境
reset: clean
	@echo "🔄 重置测试环境..."
	cd backend && python manage.py flush --noinput
	cd backend && python manage.py migrate
	@echo "✅ 测试环境重置完成!"

# 测试环境验证
verify:
	@echo "🔍 验证测试环境..."
	@echo "检查Python版本..."
	python --version
	@echo "检查Django版本..."
	cd backend && python -c "import django; print(f'Django {django.get_version()}')"
	@echo "检查pytest版本..."
	pytest --version
	@echo "检查Node版本..."
	node --version
	@echo "检查npm版本..."
	npm --version
	@echo "✅ 测试环境验证完成!"

# 性能测试
test-perf:
	@echo "⚡ 运行性能测试..."
	cd backend && python -m pytest tests/performance/ -v --tb=short

# 安全测试
test-security:
	@echo "🔒 运行安全测试..."
	cd backend && python -m pytest tests/security/ -v --tb=short

# 压力测试
test-stress:
	@echo "💪 运行压力测试..."
	cd backend && python -m pytest tests/stress/ -v --tb=short

# 测试报告
test-report:
	@echo "📋 生成测试报告..."
	cd backend && python -m pytest tests/ --html=test_report.html --self-contained-html
	@echo "✅ 测试报告生成完成: test_report.html"

# 测试覆盖率阈值检查
cov-check:
	@echo "🎯 检查覆盖率阈值..."
	cd backend && python -m pytest tests/ --cov=. --cov-fail-under=80 --cov-report=term-missing
	@echo "✅ 覆盖率检查完成 (阈值: 80%)"

# 并行测试
test-parallel:
	@echo "🚀 运行并行测试..."
	cd backend && python -m pytest tests/ -n auto --dist=loadfile

# 测试调试
test-debug:
	@echo "🐛 调试测试..."
	cd backend && python -m pytest tests/ -v --tb=long --pdb

# 测试重试
test-retry:
	@echo "🔄 重试失败的测试..."
	cd backend && python -m pytest tests/ --reruns 3 --reruns-delay 1

# 测试超时
test-timeout:
	@echo "⏰ 设置测试超时..."
	cd backend && python -m pytest tests/ --timeout=300

# 测试标记
test-markers:
	@echo "🏷️ 显示测试标记..."
	cd backend && python -m pytest --markers

# 测试收集
test-collect:
	@echo "📦 收集测试..."
	cd backend && python -m pytest tests/ --collect-only

# 测试依赖
test-deps:
	@echo "📋 检查测试依赖..."
	cd backend && python -m pytest tests/ --durations=10

# 测试配置
test-config:
	@echo "⚙️ 显示测试配置..."
	cd backend && python -m pytest tests/ --setup-show

# 测试环境
test-env:
	@echo "🌍 显示测试环境..."
	cd backend && python -c "import os; print('Environment variables:'); [print(f'{k}={v}') for k, v in os.environ.items() if 'TEST' in k.upper()]"