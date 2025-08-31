#!/bin/bash

# Alpha项目开发环境一键配置脚本
# 确保任何新环境都能快速搭建符合规范的开发环境

echo "🚀 开始配置Alpha项目开发环境..."

# 检查必要工具
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 未安装，请先安装 $1"
        exit 1
    else
        echo "✅ $1 已安装"
    fi
}

echo "📋 检查必要工具..."
check_tool "node"
check_tool "npm"
check_tool "python"
check_tool "git"

# 检查项目结构
if [ ! -f ".cursorrules" ]; then
    echo "❌ 未找到.cursorrules文件，请确保在项目根目录执行"
    exit 1
fi

echo "✅ 项目结构检查通过"

# 安装Task Master
echo "📦 安装Task Master..."
if ! command -v task-master &> /dev/null; then
    npm install -g task-master-ai
    echo "✅ Task Master安装完成"
else
    echo "✅ Task Master已安装"
fi

# 配置Task Master
echo "⚙️ 配置Task Master..."
if [ ! -f ".taskmaster/config.json" ]; then
    task-master init --yes --rules cursor,windsurf
    echo "✅ Task Master初始化完成"
else
    echo "✅ Task Master已配置"
fi

# 检查并安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    echo "✅ 前端依赖安装完成"
else
    echo "✅ 前端依赖已安装"
fi

# 检查并安装后端依赖
echo "📦 安装后端依赖..."
cd ../backend
if [ ! -d "venv" ]; then
    python -m venv venv
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    pip install -r requirements.txt
    echo "✅ 后端依赖安装完成"
else
    echo "✅ 后端依赖已安装"
fi

# 检查测试环境
echo "🧪 检查测试环境..."
cd ../tests
if [ ! -d "venv" ]; then
    python -m venv venv
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    pip install -r requirements.txt
    echo "✅ 测试环境配置完成"
else
    echo "✅ 测试环境已配置"
fi

# 创建必要目录
echo "📁 创建必要目录..."
cd ..
mkdir -p logs
mkdir -p tests/data
mkdir -p .taskmaster/docs
mkdir -p .taskmaster/templates
echo "✅ 目录结构创建完成"

# 配置Git钩子
echo "🔗 配置Git钩子..."
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# 提交前自动检查
echo "🔍 执行提交前检查..."

# 检查是否有测试文件
if ! find . -name "*.spec.ts" -o -name "test_*.py" | grep -q .; then
    echo "⚠️ 警告：没有找到测试文件，请确保已编写相应测试"
fi

# 运行快速测试
echo "🧪 运行快速测试..."
cd frontend && npm run test:fe -- --run --reporter=basic
if [ $? -ne 0 ]; then
    echo "❌ 前端测试失败，请修复后再提交"
    exit 1
fi

echo "✅ 提交前检查通过"
EOF

chmod +x .git/hooks/pre-commit
echo "✅ Git钩子配置完成"

echo "🎉 开发环境配置完成！"
echo ""
echo "📋 下一步操作："
echo "1. 运行 'task-master list' 查看当前任务"
echo "2. 运行 './scripts/run-tests.sh' 执行完整测试"
echo "3. 查看 docs/README.md 了解项目详情"
echo ""
echo "🔧 常用命令："
echo "- task-master next    # 查看下一个任务"
echo "- npm run test:fe     # 运行前端测试"
echo "- python tests/run_tests.py  # 运行后端测试"
