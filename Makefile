# Alpha项目统一测试与构建

.PHONY: help test test-backend test-frontend test-coverage lint clean install dev build flaky-test flaky-analyze flaky-stability flaky-isolate release release-dry-run release-debug changelog version-check commit commit-retry req-pipeline req-pipeline-dry req-pipeline-text req-example req-template

# 默认目标
help:
	@echo "Alpha项目可用命令:"
	@echo "  make install     - 安装所有依赖"
	@echo "  make test        - 运行所有测试"
	@echo "  make test-backend - 仅运行后端测试"
	@echo "  make test-frontend - 仅运行前端测试"
	@echo "  make test-coverage - 运行测试并生成覆盖率报告"
	@echo "  make lint        - 运行代码风格检查"
	@echo "  make dev         - 启动开发服务器"
	@echo "  make build       - 构建项目"
	@echo "  make clean       - 清理临时文件"
	@echo "  make flaky-test  - 运行flaky测试检测"
	@echo "  make flaky-analyze - 分析flaky测试报告"
	@echo "  make flaky-stability - 运行稳定性检查"
	@echo "  make flaky-isolate - 跳过已知flaky测试运行"
	@echo "  make release     - 执行语义化发布"
	@echo "  make release-dry-run - 语义化发布预演"
	@echo "  make release-debug - 语义化发布调试模式"
	@echo "  make changelog   - 生成CHANGELOG"
	@echo "  make version-check - 检查下一个版本号"
	@echo "  make commit      - 交互式提交"
	@echo "  make commit-retry - 重试上次提交"
	@echo "  make req-pipeline - 运行需求→测试→实现流水线"
	@echo "  make req-pipeline-dry - 预览需求→测试→实现流水线"
	@echo "  make req-pipeline-text - 从文本运行需求流水线"
	@echo "  make req-example - 运行示例需求流水线"
	@echo "  make req-template - 查看需求模板"

# 安装依赖
install:
	@echo "📦 安装Python依赖..."
	pip install -r requirements.txt
	pip install pytest pytest-cov flake8 black isort
	@echo "📦 安装前端依赖..."
	cd frontend && npm install

# 运行所有测试
test:
	@echo "🧪 运行所有测试..."
	python run_all_tests.py

# 仅运行后端测试
test-backend:
	@echo "🧪 运行后端测试..."
	python run_all_tests.py --backend-only

# 仅运行前端测试
test-frontend:
	@echo "🧪 运行前端测试..."
	python run_all_tests.py --frontend-only

# 运行测试并生成覆盖率报告
test-coverage:
	@echo "📊 运行测试并生成覆盖率报告..."
	python run_all_tests.py
	@echo "📈 覆盖率报告已生成:"
	@echo "  - 后端: htmlcov/index.html"
	@echo "  - 前端: frontend/coverage/index.html"

# 代码风格检查
lint:
	@echo "🔍 运行代码风格检查..."
	python -m flake8 backend --max-line-length=127 --exclude=migrations
	python -m black backend --check
	python -m isort backend --check-only
	cd frontend && npm run lint:check
	cd frontend && npm run format:check

# 类型检查
type-check:
	@echo "🔍 运行类型检查..."
	python -m mypy backend/apps --ignore-missing-imports
	cd frontend && npm run type-check

# 安全检查
security-check:
	@echo "🔒 运行安全检查..."
	python -m bandit -r backend/ -x tests/,migrations/

# API契约校验
api-contract-check:
	@echo "🔍 运行API契约校验..."
	cd backend && python ../scripts/api_contract_check.py --project-root .. --fail-on-incompatible

# 完整的代码质量检查
quality-check: lint type-check security-check api-contract-check
	@echo "✅ 代码质量检查完成"

# 代码格式化
format:
	@echo "🎨 格式化代码..."
	python -m black backend
	python -m isort backend
	cd frontend && npm run format
	cd frontend && npm run lint

# 启动开发服务器
dev:
	@echo "🚀 启动开发服务器..."
	@echo "后端: http://localhost:8000"
	@echo "前端: http://localhost:5173"
	@echo "请在不同终端中运行:"
	@echo "  终端1: cd backend && python manage.py runserver"
	@echo "  终端2: cd frontend && npm run dev"

# 构建项目
build:
	@echo "🏗️  构建项目..."
	cd frontend && npm run build
	@echo "✅ 前端构建完成: frontend/dist/"

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf frontend/coverage/
	rm -rf frontend/dist/
	rm -rf .pytest_cache/
	rm -rf **/__pycache__/
	rm -rf **/*.pyc
	@echo "✅ 清理完成"

# 快速检查（CI用）
ci-check:
	@echo "🔄 CI快速检查..."
	make quality-check
	python run_all_tests.py --fail-under=70

# Pre-commit安装
install-hooks:
	@echo "🪝 安装pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "✅ Pre-commit hooks安装完成"

# Flaky测试管理
flaky-test:
	@echo "🔄 运行flaky测试检测..."
	python scripts/flaky_test_manager.py --action test

flaky-analyze:
	@echo "📊 分析flaky测试报告..."
	python scripts/flaky_test_manager.py --action analyze
	@echo "📈 Flaky测试报告已生成: tests/reports/flaky/comprehensive_flaky_report.html"

flaky-stability:
	@echo "🔍 运行稳定性检查..."
	python scripts/flaky_test_manager.py --action stability --iterations 5

flaky-isolate:
	@echo "🚫 跳过已知flaky测试运行..."
	python scripts/flaky_test_manager.py --action test --isolate-flaky

# 语义化发布
release:
	@echo "🚀 执行语义化发布..."
	npm run release

release-dry-run:
	@echo "🔍 语义化发布预演..."
	npm run release:dry-run

release-debug:
	@echo "🐛 语义化发布调试模式..."
	npm run release:debug

changelog:
	@echo "📋 生成CHANGELOG..."
	npm run changelog

version-check:
	@echo "🔍 检查下一个版本号..."
	npm run version:check

commit:
	@echo "📝 交互式提交..."
	npm run commit

commit-retry:
	@echo "🔄 重试上次提交..."
	npm run commit:retry

# 需求到测试流水线命令
req-pipeline:
	@echo "🔄 运行需求→测试→实现流水线..."
	@if [ -z "$(REQ)" ]; then \
		echo "❌ 请指定需求文件: make req-pipeline REQ=path/to/requirement.md"; \
		exit 1; \
	fi
	python scripts/req_to_test_pipeline.py --input "$(REQ)"

req-pipeline-dry:
	@echo "🔍 预览需求→测试→实现流水线..."
	@if [ -z "$(REQ)" ]; then \
		echo "❌ 请指定需求文件: make req-pipeline-dry REQ=path/to/requirement.md"; \
		exit 1; \
	fi
	python scripts/req_to_test_pipeline.py --input "$(REQ)" --dry-run

req-pipeline-text:
	@echo "🔄 从文本运行需求→测试→实现流水线..."
	@if [ -z "$(TEXT)" ]; then \
		echo "❌ 请指定需求文本: make req-pipeline-text TEXT='标题: 功能名称...'"; \
		exit 1; \
	fi
	python scripts/req_to_test_pipeline.py --input "$(TEXT)" --input-type text

req-example:
	@echo "📋 运行示例需求流水线..."
	python scripts/req_to_test_pipeline.py --input scripts/templates/example_requirement.md --dry-run

req-template:
	@echo "📝 查看需求模板..."
	@if command -v cat >/dev/null 2>&1; then \
		cat scripts/templates/requirement_template.md; \
	else \
		type scripts/templates/requirement_template.md; \
	fi

# 生产环境构建
ci-build:
	@echo "🏭 生产环境构建..."
	make clean
	make install
	make ci-check
	make build
	@echo "✅ 生产环境构建完成"