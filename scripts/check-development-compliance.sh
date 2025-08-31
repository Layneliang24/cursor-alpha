#!/bin/bash

# Alpha项目开发合规性检查脚本
# 在每次开发前后自动检查是否遵循开发方法论

echo "🔍 开始开发合规性检查..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

COMPLIANCE_SCORE=0
TOTAL_CHECKS=0

# 计分函数
score_check() {
    local check_name="$1"
    local check_command="$2"
    local points="$3"
    local suggestion="$4"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + points))
    echo -n "📋 $check_name... "
    
    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ (+$points)${NC}"
        COMPLIANCE_SCORE=$((COMPLIANCE_SCORE + points))
        return 0
    else
        echo -e "${RED}❌ (0/$points)${NC}"
        if [ -n "$suggestion" ]; then
            echo -e "${YELLOW}   💡 建议: $suggestion${NC}"
        fi
        return 1
    fi
}

echo ""
echo "===================="
echo "🎯 Task Master使用合规性"
echo "===================="

score_check "Task Master已初始化" "test -f .taskmaster/config.json" 10 "运行: task-master init"
score_check "存在任务文件" "test -f .taskmaster/tasks/tasks.json" 10 "创建PRD并解析: task-master parse-prd"
score_check "最近7天有任务更新" "find .taskmaster -name '*.json' -mtime -7 | head -1" 5 "定期更新任务状态"

# 检查是否有标签管理
if [ -f ".taskmaster/tasks/tasks.json" ]; then
    if grep -q '"tags"' .taskmaster/tasks/tasks.json; then
        score_check "使用标签化管理" "grep -q '\"tags\"' .taskmaster/tasks/tasks.json" 5 ""
    else
        score_check "使用标签化管理" "false" 5 "考虑使用task-master add-tag管理不同特性"
    fi
fi

echo ""
echo "===================="
echo "🧪 测试驱动开发合规性"
echo "===================="

# 检查测试文件数量和质量
FRONTEND_TESTS=$(find frontend -name "*.spec.ts" 2>/dev/null | wc -l)
BACKEND_TESTS=$(find tests -name "test_*.py" 2>/dev/null | wc -l)

if [ "$FRONTEND_TESTS" -gt 15 ]; then
    score_check "前端测试文件充足" "true" 10 ""
elif [ "$FRONTEND_TESTS" -gt 5 ]; then
    score_check "前端测试文件基本" "true" 5 "增加更多组件测试"
else
    score_check "前端测试文件不足" "false" 10 "至少需要15个测试文件"
fi

if [ "$BACKEND_TESTS" -gt 50 ]; then
    score_check "后端测试文件充足" "true" 10 ""
elif [ "$BACKEND_TESTS" -gt 20 ]; then
    score_check "后端测试文件基本" "true" 5 "增加更多API测试"
else
    score_check "后端测试文件不足" "false" 10 "至少需要50个测试文件"
fi

# 检查最近提交是否包含测试
RECENT_COMMIT=$(git log --oneline -1 --name-only)
if echo "$RECENT_COMMIT" | grep -q -E "(test_|\.spec\.ts|\.test\.js)"; then
    score_check "最近提交包含测试" "true" 10 ""
else
    score_check "最近提交包含测试" "false" 10 "每次代码提交都应包含相应测试"
fi

echo ""
echo "===================="
echo "📚 文档同步合规性"
echo "===================="

# 检查文档更新
score_check "README文档存在" "test -f docs/README.md" 5 "创建项目概览文档"
score_check "API文档存在" "test -f docs/API.md" 5 "维护API接口文档"
score_check "FAQ文档存在" "test -f docs/FAQ.md" 5 "记录常见问题和解决方案"

# 检查文档是否最近更新
if find docs -name "*.md" -mtime -7 | head -1 > /dev/null 2>&1; then
    score_check "文档最近有更新" "true" 5 ""
else
    score_check "文档最近有更新" "false" 5 "开发新功能时应同步更新文档"
fi

echo ""
echo "===================="
echo "🔧 代码质量合规性"
echo "===================="

# 检查Git提交规范
RECENT_COMMIT_MSG=$(git log --oneline -1 --pretty=format:"%s")
if echo "$RECENT_COMMIT_MSG" | grep -q -E "^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?:"; then
    score_check "Git提交信息规范" "true" 5 ""
else
    score_check "Git提交信息规范" "false" 5 "使用格式: type(scope): description"
fi

# 检查是否有未提交的更改
if git diff --quiet && git diff --cached --quiet; then
    score_check "工作区干净" "true" 5 ""
else
    score_check "工作区干净" "false" 5 "及时提交代码变更"
fi

echo ""
echo "===================="
echo "📊 合规性评分"
echo "===================="

COMPLIANCE_PERCENTAGE=$((COMPLIANCE_SCORE * 100 / TOTAL_CHECKS))

echo -e "${BLUE}总分: $COMPLIANCE_SCORE / $TOTAL_CHECKS${NC}"
echo -e "${BLUE}合规率: $COMPLIANCE_PERCENTAGE%${NC}"

if [ $COMPLIANCE_PERCENTAGE -ge 90 ]; then
    echo -e "${GREEN}🏆 优秀！完全符合开发方法论要求${NC}"
elif [ $COMPLIANCE_PERCENTAGE -ge 75 ]; then
    echo -e "${YELLOW}👍 良好！基本符合开发方法论要求${NC}"
    echo -e "${YELLOW}💡 建议优化上述标记的项目${NC}"
elif [ $COMPLIANCE_PERCENTAGE -ge 60 ]; then
    echo -e "${YELLOW}⚠️ 及格！需要改进以提高合规性${NC}"
    echo -e "${YELLOW}🔧 请重点关注测试和文档部分${NC}"
else
    echo -e "${RED}❌ 不及格！严重偏离开发方法论${NC}"
    echo -e "${RED}🚨 建议运行 ./scripts/setup-dev-environment.sh 重新配置${NC}"
fi

echo ""
echo "===================="
echo "🎯 下一步建议"
echo "===================="

if [ $COMPLIANCE_PERCENTAGE -lt 90 ]; then
    echo "📋 改进建议："
    echo "1. 运行 ./scripts/validate-methodology.sh 详细诊断"
    echo "2. 查看 docs/METHODOLOGY_ONBOARDING.md 学习标准流程"
    echo "3. 使用 task-master next 开始标准化开发"
    echo "4. 确保每次提交都包含相应测试"
fi

echo ""
echo "📞 需要帮助？"
echo "- 查看 docs/FAQ.md 了解常见问题"
echo "- 查看 docs/DEVELOPMENT.md 了解开发规范"
echo "- 运行 task-master research --query='如何提高开发合规性' 获取AI建议"

echo ""
echo "🎉 合规性检查完成！"
