# 🖥️ 新机器部署指南

## 📋 概述

本指南专门针对在新机器上部署Alpha项目并确保测试流程能够顺利执行。通过本指南，您可以：

1. **快速搭建开发环境**
2. **验证测试流程完整性**
3. **确保项目在新机器上正常运行**
4. **建立标准化的部署流程**

## 🎯 目标

确保新机器上的测试流程能够：
- ✅ 顺序执行所有测试步骤
- ✅ 可靠地生成测试报告
- ✅ 验证项目功能完整性
- ✅ 提供清晰的错误诊断

## 🚀 快速部署流程

### 第一步：环境检查

在新机器上运行环境检查脚本：

```bash
# 克隆项目
git clone <repository-url>
cd cursor-alpha

# 运行环境检查
python check_environment.py
```

**预期结果**：所有检查项都应该通过，如果有失败项，请按照提示解决。

### 第二步：一键部署

#### Windows 环境
```bash
# 运行一键部署脚本
setup_project.bat
```

#### Linux/macOS 环境
```bash
# 设置执行权限
chmod +x setup_project.sh

# 运行一键部署脚本
./setup_project.sh
```

**预期结果**：
- ✅ Python虚拟环境创建成功
- ✅ 后端依赖安装完成
- ✅ 前端依赖安装完成
- ✅ 数据库迁移成功
- ✅ 基础测试通过

### 第三步：测试流程验证

运行测试流程验证脚本：

```bash
python verify_tests.py
```

**预期结果**：
- ✅ 测试结构检查通过
- ✅ 后端环境检查通过
- ✅ 数据库连接验证通过
- ✅ 基础测试通过
- ✅ 单元测试通过
- ✅ 集成测试通过
- ✅ 覆盖率报告生成成功

## 🔧 详细步骤说明

### 1. 环境要求验证

确保新机器满足以下要求：

| 组件 | 版本要求 | 验证命令 |
|------|----------|----------|
| Python | 3.8+ | `python --version` |
| Node.js | 16+ | `node --version` |
| npm | 最新 | `npm --version` |
| Git | 最新 | `git --version` |

### 2. 项目结构验证

确保项目包含以下关键文件和目录：

```
cursor-alpha/
├── backend/                 # 后端代码
│   ├── requirements.txt     # Python依赖
│   ├── manage.py           # Django管理脚本
│   └── alpha/              # Django项目配置
├── frontend/               # 前端代码
│   ├── package.json        # Node.js依赖
│   └── src/                # 源代码
├── tests/                  # 测试目录
│   ├── conftest.py         # 测试配置
│   ├── unit/               # 单元测试
│   ├── integration/        # 集成测试
│   └── factories/          # 测试数据工厂
├── docs/                   # 文档目录
├── setup_project.bat       # Windows部署脚本
├── setup_project.sh        # Linux/macOS部署脚本
├── check_environment.py    # 环境检查脚本
└── verify_tests.py         # 测试验证脚本
```

### 3. 依赖安装验证

#### 后端依赖
```bash
cd backend
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 验证关键依赖
python -c "import django; print(django.get_version())"
python -c "import pytest; print(pytest.__version__)"
python -c "import factory_boy; print(factory_boy.__version__)"
```

#### 前端依赖
```bash
cd frontend
npm list --depth=0
```

### 4. 数据库配置验证

```bash
cd backend
python manage.py showmigrations
python manage.py migrate
```

### 5. 测试执行验证

#### 基础测试
```bash
cd backend
python -m pytest ../tests/unit/test_basic.py -v
```

**预期输出**：
```
============================= test session starts =============================
collecting ... collected 11 items

tests/unit/test_basic.py::TestBasicFunctionality::test_django_setup PASSED
tests/unit/test_basic.py::TestBasicFunctionality::test_database_connection PASSED
...
============================== 11 passed in 2.34s ==============================
```

#### 单元测试
```bash
python -m pytest ../tests/unit/ -v
```

#### 集成测试
```bash
python -m pytest ../tests/integration/ -v
```

#### 覆盖率测试
```bash
python -m pytest ../tests/ --cov=apps --cov-report=html --cov-report=term-missing
```

## 🔍 故障排除

### 常见问题及解决方案

#### 1. Python环境问题

**问题**：`ModuleNotFoundError: No module named 'xxx'`

**解决方案**：
```bash
# 确保虚拟环境已激活
cd backend
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 重新安装依赖
pip install -r requirements.txt
```

#### 2. 数据库连接问题

**问题**：`django.db.utils.OperationalError`

**解决方案**：
```bash
# 检查数据库配置
python manage.py check

# 重新运行迁移
python manage.py migrate
```

#### 3. 测试导入问题

**问题**：`ImportError: cannot import name 'xxx'`

**解决方案**：
```bash
# 确保在正确的目录运行测试
cd backend
python -m pytest ../tests/unit/test_basic.py

# 检查conftest.py配置
cat ../tests/conftest.py
```

#### 4. 前端依赖问题

**问题**：`npm ERR!`

**解决方案**：
```bash
cd frontend
npm cache clean --force
npm install
```

### 诊断命令

```bash
# 检查Python环境
python --version
pip list

# 检查Node.js环境
node --version
npm list --depth=0

# 检查项目结构
ls -la
tree -L 2

# 检查测试环境
cd backend
python -m pytest --version
python -c "import django; print(django.get_version())"
```

## 📊 验证清单

在新机器上完成部署后，请确认以下项目：

### 环境验证
- [ ] Python 3.8+ 已安装并配置
- [ ] Node.js 16+ 已安装并配置
- [ ] Git 已安装并配置
- [ ] 项目目录结构完整

### 后端验证
- [ ] 虚拟环境创建成功
- [ ] 所有Python依赖安装完成
- [ ] Django项目配置正确
- [ ] 数据库迁移成功
- [ ] 测试依赖安装完成

### 前端验证
- [ ] Node.js依赖安装完成
- [ ] 开发服务器能正常启动
- [ ] 页面能正常访问

### 测试验证
- [ ] 基础测试全部通过
- [ ] 单元测试全部通过
- [ ] 集成测试全部通过
- [ ] 覆盖率报告生成成功
- [ ] 测试数据工厂正常工作

### 功能验证
- [ ] 后端API能正常响应
- [ ] 前端页面能正常加载
- [ ] 用户认证功能正常
- [ ] 数据库操作正常

## 🎯 成功标准

新机器部署成功的标志：

1. **环境检查脚本**：所有检查项通过
2. **部署脚本**：无错误完成
3. **测试验证脚本**：所有验证项通过
4. **手动测试**：基础功能正常

## 📞 技术支持

如果遇到问题，请：

1. **查看日志**：检查错误信息和堆栈跟踪
2. **参考文档**：
   - [部署指南](DEPLOYMENT_GUIDE.md)
   - [测试标准](TESTING_STANDARDS.md)
   - [项目指南](GUIDE.md)
3. **运行诊断**：使用 `check_environment.py` 和 `verify_tests.py`
4. **检查配置**：确认环境变量和配置文件

## 🔄 持续集成

为了确保测试流程的可靠性，建议：

1. **定期验证**：每周运行一次完整测试
2. **环境同步**：保持开发环境的一致性
3. **文档更新**：及时更新部署文档
4. **自动化**：考虑使用CI/CD流水线

---

**注意**：本指南适用于开发环境。生产环境部署请参考 [生产部署指南](PRODUCTION_DEPLOYMENT.md)。
