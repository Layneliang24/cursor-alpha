#!/bin/bash

# Alpha项目开发方法论验证脚本
# 确保当前环境完全符合开发规范

echo "🔍 开始验证开发方法论合规性..."

VALIDATION_FAILED=0

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 验证函数
validate_step() {
    local step_name="$1"
    local check_command="$2"
    local error_message="$3"
    
    echo -n "📋 检查 $step_name... "
    
    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 通过${NC}"
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        echo -e "${RED}   错误：$error_message${NC}"
        VALIDATION_FAILED=1
        return 1
    fi
}

echo "===================="
echo "🏗️ 基础环境验证"
echo "===================="

validate_step "Task Master安装" "command -v task-master" "请运行: npm install -g task-master-ai"
validate_step "Node.js环境" "command -v node" "请安装Node.js 18+"
validate_step "Python环境" "command -v python" "请安装Python 3.9+"
validate_step "Git配置" "git config user.name" "请配置Git用户信息"

echo ""
echo "===================="
echo "📁 项目结构验证"
echo "===================="

validate_step "核心规则文件" "test -f .cursorrules" "缺少.cursorrules文件"
validate_step "Task Master配置" "test -f .taskmaster/config.json" "请运行task-master init初始化"
validate_step "前端package.json" "test -f frontend/package.json" "前端项目结构异常"
validate_step "后端requirements.txt" "test -f backend/requirements.txt" "后端项目结构异常"
validate_step "测试目录" "test -d tests" "缺少tests目录"
validate_step "文档目录" "test -d docs" "缺少docs目录"

echo ""
echo "===================="
echo "🧪 测试框架验证"
echo "===================="

validate_step "前端测试配置" "test -f frontend/vitest.config.ts" "前端测试框架未配置"
validate_step "E2E测试配置" "test -f frontend/playwright.config.ts" "E2E测试框架未配置"
validate_step "后端测试配置" "test -f tests/pytest.ini" "后端测试框架未配置"
validate_step "前端测试文件" "find frontend -name '*.spec.ts' | head -1" "缺少前端测试文件"
validate_step "后端测试文件" "find tests -name 'test_*.py' | head -1" "缺少后端测试文件"

echo ""
echo "===================="
echo "📚 文档完整性验证"
echo "===================="

validate_step "开发文档" "test -f docs/DEVELOPMENT.md" "缺少开发文档"
validate_step "测试规范" "test -f docs/TESTING_STANDARDS.md" "缺少测试规范"
validate_step "API文档" "test -f docs/API.md" "缺少API文档"
validate_step "FAQ文档" "test -f docs/FAQ.md" "缺少FAQ文档"
validate_step "入门指南" "test -f docs/METHODOLOGY_ONBOARDING.md" "缺少入门指南"

echo ""
echo "===================="
echo "⚙️ 配置一致性验证"
echo "===================="

# 检查Task Master配置
if [ -f ".taskmaster/config.json" ]; then
    # 检查是否配置了中文响应
    if grep -q '"responseLanguage": "Chinese"' .taskmaster/config.json; then
        echo -e "📋 检查Task Master语言配置... ${GREEN}✅ 通过${NC}"
    else
        echo -e "📋 检查Task Master语言配置... ${RED}❌ 失败${NC}"
        echo -e "${RED}   错误：请配置responseLanguage为Chinese${NC}"
        VALIDATION_FAILED=1
    fi
    
    # 检查是否配置了AI模型
    if grep -q '"main"' .taskmaster/config.json; then
        echo -e "📋 检查AI模型配置... ${GREEN}✅ 通过${NC}"
    else
        echo -e "📋 检查AI模型配置... ${RED}❌ 失败${NC}"
        echo -e "${RED}   错误：请运行task-master models --setup配置AI模型${NC}"
        VALIDATION_FAILED=1
    fi
fi

# 检查Git钩子
if [ -f ".git/hooks/pre-commit" ]; then
    echo -e "📋 检查Git钩子... ${GREEN}✅ 通过${NC}"
else
    echo -e "📋 检查Git钩子... ${YELLOW}⚠️ 建议${NC}"
    echo -e "${YELLOW}   建议：运行./scripts/setup-dev-environment.sh配置Git钩子${NC}"
fi

echo ""
echo "===================="
echo "🧪 功能性验证"
echo "===================="

# 验证Task Master功能
if command -v task-master > /dev/null 2>&1; then
    if task-master list > /dev/null 2>&1; then
        echo -e "📋 检查Task Master功能... ${GREEN}✅ 通过${NC}"
    else
        echo -e "📋 检查Task Master功能... ${RED}❌ 失败${NC}"
        echo -e "${RED}   错误：Task Master无法正常运行，请检查配置${NC}"
        VALIDATION_FAILED=1
    fi
fi

# 验证前端测试
if [ -d "frontend/node_modules" ]; then
    echo -e "📋 检查前端依赖... ${GREEN}✅ 通过${NC}"
else
    echo -e "📋 检查前端依赖... ${RED}❌ 失败${NC}"
    echo -e "${RED}   错误：请运行cd frontend && npm install${NC}"
    VALIDATION_FAILED=1
fi

# 验证后端环境
if [ -f "backend/manage.py" ]; then
    echo -e "📋 检查后端结构... ${GREEN}✅ 通过${NC}"
else
    echo -e "📋 检查后端结构... ${RED}❌ 失败${NC}"
    echo -e "${RED}   错误：后端Django项目结构异常${NC}"
    VALIDATION_FAILED=1
fi

echo ""
echo "===================="
echo "📊 验证结果"
echo "===================="

if [ $VALIDATION_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有验证通过！开发环境完全符合方法论要求${NC}"
    echo ""
    echo "🚀 您现在可以开始开发："
    echo "1. task-master next    # 查看下一个任务"
    echo "2. 遵循TDD流程开发"
    echo "3. 运行测试验证"
    echo "4. 提交代码"
    echo ""
else
    echo -e "${RED}⚠️ 验证失败！请修复上述问题后重新验证${NC}"
    echo ""
    echo "🔧 修复建议："
    echo "1. 运行 ./scripts/setup-dev-environment.sh 自动修复环境问题"
    echo "2. 查看 docs/METHODOLOGY_ONBOARDING.md 了解详细步骤"
    echo "3. 修复后重新运行此脚本验证"
    echo ""
    exit 1
fi

echo "📋 方法论合规性验证完成！"
