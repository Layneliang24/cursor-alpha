# 🚀 项目部署与测试指南

## 📋 目录
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [详细部署步骤](#详细部署步骤)
- [测试环境搭建](#测试环境搭建)
- [常见问题解决](#常见问题解决)
- [验证清单](#验证清单)

## 🖥️ 环境要求

### 基础环境
- **操作系统**: Windows 10/11, macOS, Linux
- **Python**: 3.8+ (推荐 3.9+)
- **Node.js**: 16+ (推荐 18+)
- **Git**: 最新版本

### 推荐工具
- **IDE**: VSCode, PyCharm
- **数据库**: SQLite (开发), MySQL (生产)
- **包管理器**: pip, npm

## ⚡ 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd cursor-alpha
```

### 2. 一键部署脚本
```bash
# Windows
setup_project.bat

# Linux/macOS
./setup_project.sh
```

### 3. 验证部署
```bash
# 运行测试
run_tests.bat

# 启动服务
start_backend.bat
start_frontend.bat
```

## 🔧 详细部署步骤

### 第一步：环境检查
```bash
# 检查Python版本
python --version

# 检查Node.js版本
node --version

# 检查npm版本
npm --version

# 检查Git版本
git --version
```

### 第二步：后端环境搭建
```bash
cd backend

# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 3. 升级pip
python -m pip install --upgrade pip

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置数据库
python manage.py migrate

# 6. 创建超级用户
python manage.py createsuperuser
```

### 第三步：前端环境搭建
```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 检查依赖安装
npm list --depth=0
```

### 第四步：测试环境配置
```bash
cd backend

# 1. 安装测试依赖
pip install pytest pytest-django pytest-cov factory-boy faker

# 2. 验证测试环境
python -m pytest --version
```

## 🧪 测试环境搭建

### 测试目录结构
```
tests/
├── conftest.py              # 全局配置
├── factories/               # 测试数据工厂
│   ├── user_factory.py
│   ├── article_factory.py
│   └── category_factory.py
├── unit/                    # 单元测试
│   ├── test_basic.py
│   └── test_models.py
├── integration/             # 集成测试
│   └── test_api.py
└── e2e/                     # 端到端测试
    └── test_user_flows.py
```

### 运行测试
```bash
# 1. 基础测试（验证环境）
cd tests
python -m pytest unit/test_basic.py -v

# 2. 单元测试
python -m pytest unit/ -v

# 3. 集成测试
python -m pytest integration/ -v

# 4. 所有测试
python -m pytest --cov=apps --cov-report=html

# 5. 使用批处理脚本
cd ..
run_tests.bat
```

### 测试覆盖率
```bash
# 生成覆盖率报告
python -m pytest --cov=apps --cov-report=html --cov-report=term-missing

# 查看报告
# 打开 tests/htmlcov/index.html
```

## 🔍 常见问题解决

### Python环境问题
```bash
# 问题：ModuleNotFoundError
# 解决：检查虚拟环境是否激活
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# 问题：pip安装失败
# 解决：使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
```

### 数据库问题
```bash
# 问题：数据库连接失败
# 解决：检查settings.py中的数据库配置
# 开发环境使用SQLite，生产环境使用MySQL

# 问题：迁移失败
# 解决：重置数据库
python manage.py flush --noinput
python manage.py migrate
```

### 测试问题
```bash
# 问题：测试找不到模块
# 解决：确保在正确的目录运行
cd backend
python -m pytest tests/unit/test_basic.py

# 问题：fixture未找到
# 解决：检查conftest.py是否正确配置
```

### 前端问题
```bash
# 问题：npm install失败
# 解决：清除缓存
npm cache clean --force
npm install

# 问题：端口被占用
# 解决：修改端口或关闭占用进程
# 修改 vite.config.js 中的端口配置
```

## ✅ 验证清单

### 环境验证
- [ ] Python 3.8+ 已安装
- [ ] Node.js 16+ 已安装
- [ ] Git 已安装
- [ ] 虚拟环境已创建并激活

### 后端验证
- [ ] 依赖包安装完成
- [ ] 数据库迁移成功
- [ ] 超级用户创建成功
- [ ] Django服务器能正常启动

### 前端验证
- [ ] npm依赖安装完成
- [ ] 开发服务器能正常启动
- [ ] 页面能正常访问

### 测试验证
- [ ] 测试环境配置完成
- [ ] 基础测试通过
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 覆盖率报告生成

### 功能验证
- [ ] 用户注册/登录功能正常
- [ ] 文章CRUD功能正常
- [ ] API接口响应正常
- [ ] 前端页面交互正常

## 📞 技术支持

### 日志文件位置
- **Django日志**: `backend/logs/django.log`
- **测试日志**: `tests/test.log`
- **前端日志**: 浏览器开发者工具

### 联系方式
- **项目文档**: `docs/` 目录
- **问题反馈**: GitHub Issues
- **技术讨论**: GitHub Discussions

## 🚀 生产部署

### 环境变量配置
```bash
# 创建环境变量文件
cp .env.example .env

# 配置生产环境变量
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://user:password@host:port/dbname
```

### 数据库配置
```bash
# 生产环境使用MySQL
pip install mysqlclient

# 配置MySQL连接
# 修改 settings.py 中的数据库配置
```

### 静态文件收集
```bash
python manage.py collectstatic
```

### 服务启动
```bash
# 使用Gunicorn启动
gunicorn alpha.wsgi:application

# 使用Nginx反向代理
# 配置nginx.conf
```

---

**注意**: 本指南适用于开发环境。生产环境部署请参考 `docs/PRODUCTION_DEPLOYMENT.md`
