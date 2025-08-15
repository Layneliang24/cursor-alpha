#!/bin/bash

# Alpha 项目一键部署脚本 (Linux/macOS)

# 设置颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "Alpha 项目一键部署脚本"
echo "========================================"
echo

# 检查是否在项目根目录
if [ ! -d "backend" ]; then
    echo -e "${RED}错误: 请在项目根目录运行此脚本${NC}"
    exit 1
fi

echo -e "${BLUE}第一步: 环境检查${NC}"
echo

# 检查Python
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: Python3未安装${NC}"
    echo "请安装Python 3.8+"
    exit 1
fi
python3 --version
echo -e "${GREEN}✓ Python环境正常${NC}"
echo

# 检查Node.js
echo "检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: Node.js未安装${NC}"
    echo "请安装Node.js 16+"
    exit 1
fi
node --version
echo -e "${GREEN}✓ Node.js环境正常${NC}"
echo

# 检查npm
echo "检查npm环境..."
if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: npm未安装${NC}"
    exit 1
fi
npm --version
echo -e "${GREEN}✓ npm环境正常${NC}"
echo

# 检查Git
echo "检查Git环境..."
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}警告: Git未安装，某些功能可能受限${NC}"
else
    git --version
    echo -e "${GREEN}✓ Git环境正常${NC}"
fi
echo

echo -e "${BLUE}第二步: 后端环境搭建${NC}"
echo

cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 虚拟环境创建失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
else
    echo -e "${GREEN}✓ 虚拟环境已存在${NC}"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 虚拟环境激活失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 虚拟环境激活成功${NC}"

# 升级pip
echo "升级pip..."
python -m pip install --upgrade pip
echo -e "${GREEN}✓ pip升级完成${NC}"

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}警告: 部分依赖安装失败，尝试使用国内镜像${NC}"
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: 依赖安装失败${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Python依赖安装完成${NC}"

# 安装测试依赖
echo "安装测试依赖..."
pip install pytest pytest-django pytest-cov factory-boy faker
echo -e "${GREEN}✓ 测试依赖安装完成${NC}"

# 数据库迁移
echo "运行数据库迁移..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 数据库迁移失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 数据库迁移完成${NC}"

# 创建超级用户（可选）
echo
read -p "是否创建超级用户? (y/n): " create_superuser
if [[ $create_superuser =~ ^[Yy]$ ]]; then
    echo "创建超级用户..."
    python manage.py createsuperuser
    echo -e "${GREEN}✓ 超级用户创建完成${NC}"
fi

cd ..

echo
echo -e "${BLUE}第三步: 前端环境搭建${NC}"
echo

cd frontend

# 安装npm依赖
echo "安装Node.js依赖..."
npm install
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}警告: npm安装失败，尝试清除缓存后重试${NC}"
    npm cache clean --force
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: npm依赖安装失败${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Node.js依赖安装完成${NC}"

cd ..

echo
echo -e "${BLUE}第四步: 测试环境验证${NC}"
echo

cd backend

# 运行基础测试
echo "运行基础测试验证环境..."
python -m pytest ../tests/unit/test_basic.py -v
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}警告: 基础测试失败，请检查环境配置${NC}"
else
    echo -e "${GREEN}✓ 基础测试通过${NC}"
fi

cd ..

echo
echo -e "${BLUE}第五步: 创建启动脚本${NC}"
echo

# 创建后端启动脚本
cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "启动Django后端服务器..."
cd backend
source venv/bin/activate
python manage.py runserver
EOF
chmod +x start_backend.sh

# 创建前端启动脚本
cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "启动Vue前端服务器..."
cd frontend
npm run dev
EOF
chmod +x start_frontend.sh

# 创建测试运行脚本
cat > run_tests.sh << 'EOF'
#!/bin/bash
echo "运行项目测试..."
cd backend
source venv/bin/activate
python -m pytest ../tests/ --cov=apps --cov-report=html --cov-report=term-missing
echo
echo "测试完成！覆盖率报告位置: tests/htmlcov/index.html"
EOF
chmod +x run_tests.sh

echo -e "${GREEN}✓ 启动脚本创建完成${NC}"

echo
echo "========================================"
echo -e "${GREEN}🎉 项目部署完成！${NC}"
echo "========================================"
echo
echo -e "${BLUE}可用的命令:${NC}"
echo "  ./start_backend.sh   - 启动后端服务器"
echo "  ./start_frontend.sh  - 启动前端服务器"
echo "  ./run_tests.sh       - 运行所有测试"
echo
echo -e "${BLUE}访问地址:${NC}"
echo "  后端API: http://localhost:8000"
echo "  前端页面: http://localhost:5173"
echo "  Django管理后台: http://localhost:8000/admin"
echo
echo -e "${BLUE}文档位置:${NC}"
echo "  部署指南: docs/DEPLOYMENT_GUIDE.md"
echo "  测试指南: docs/TESTING_STANDARDS.md"
echo "  项目指南: docs/GUIDE.md"
echo
echo -e "${YELLOW}注意: 首次启动可能需要一些时间来编译前端资源${NC}"
echo
