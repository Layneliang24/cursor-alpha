# Alpha技术共享平台 - 统一指南

## 📋 目录
- [项目启动指南](#项目启动指南)
- [本地测试指南](#本地测试指南)
- [部署指南](#部署指南)
- [故障排除](#故障排除)
- [开发规范](#开发规范)

---

## 🚀 项目启动指南

### 快速启动
```bash
# 方式1：一键启动所有服务（推荐）
./start-simple.bat

# 方式2：PowerShell启动
./start-all.ps1

# 方式3：分别启动
./start-backend.bat  # 启动后端
./start-frontend.bat # 启动前端
```

### 环境要求
- Docker & Docker Compose
- Node.js 18+
- Python 3.9+
- MySQL 8.0+

### 启动步骤
1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd cursor-alpha
   ```

2. **启动数据库**
   ```bash
   docker-compose up -d mysql redis
   ```

3. **启动后端**
   ```bash
   cd backend
   python manage.py migrate
   python manage.py runserver
   ```

4. **启动前端**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 🧪 测试系统使用指南

### 一键测试执行

#### 完整测试套件
```bash
# 运行所有测试
python tests/run_tests.py --mode=full

# 运行回归测试
python tests/run_tests.py --mode=regression

# 运行指定模块测试
python tests/run_tests.py --module=english
python tests/run_tests.py --module=auth
```

#### 测试报告查看
```bash
# 测试报告位置
tests/reports/html/
├── full_report.html          # 完整测试报告
├── regression_report.html    # 回归测试报告
├── auth_report.html          # 认证模块报告
├── english_report.html       # 英语模块报告
└── test_summary.html         # 测试总结报告
```

### 测试目录结构
```
tests/
├── regression/              # 回归测试
│   ├── english/            # 英语学习模块测试
│   │   ├── test_data_analysis.py    # 数据分析测试
│   │   ├── test_pause_resume.py     # 暂停/继续测试
│   │   └── test_pronunciation.py    # 发音功能测试
│   └── auth/               # 认证模块测试
│       ├── test_user_authentication.py  # 用户认证测试
│       └── test_permissions.py          # 权限管理测试
├── new_features/           # 新功能测试
├── unit/                  # 单元测试
├── integration/           # 集成测试
├── resources/             # 测试资源
├── reports/               # 测试报告
│   ├── html/             # HTML报告
│   └── json/             # JSON报告
├── run_tests.py          # 一键测试脚本
├── pytest.ini           # pytest配置
└── test_settings_mysql.py # MySQL测试配置
```

### 测试类型说明

#### 1. 回归测试 (`tests/regression/`)
- **目的**：确保新功能不会破坏现有功能
- **覆盖范围**：核心业务功能
- **执行频率**：每次代码提交前

#### 2. 新功能测试 (`tests/new_features/`)
- **目的**：验证新开发功能的正确性
- **覆盖范围**：新功能的所有特性
- **执行频率**：新功能开发完成后

#### 3. 单元测试 (`tests/unit/`)
- **目的**：测试独立的代码单元
- **覆盖范围**：函数、方法、类
- **执行频率**：代码修改时

#### 4. 集成测试 (`tests/integration/`)
- **目的**：测试组件间的交互
- **覆盖范围**：API接口、数据库操作
- **执行频率**：接口变更时

### 测试覆盖统计

#### 当前覆盖情况
- **总功能数**: 89个
- **已有测试**: 16个 ✅
- **总体覆盖率**: 18.0%
- **高优先级功能覆盖率**: 50.0%

#### 模块覆盖情况
- **英语学习模块**: 15.4% ✅ (8/52个功能)
- **用户认证模块**: 100% ✅ (8/8个功能)
- **个人主页模块**: 0% ❌ (0/20个功能)
- **文章管理模块**: 0% ❌ (0/8个功能)
- **分类管理模块**: 0% ❌ (0/6个功能)

### 测试编写规范

#### 测试文件命名
```python
# 格式：test_功能名.py
test_data_analysis.py      # 数据分析测试
test_user_authentication.py # 用户认证测试
test_permissions.py        # 权限管理测试
```

#### 测试类命名
```python
# 格式：Test功能名类型
class TestDataAnalysisAPI(TestCase):      # API测试
class TestDataAnalysisService(TestCase):  # 服务层测试
class TestDataAnalysisUnit(TestCase):     # 单元测试
class TestDataAnalysisIntegration(TestCase): # 集成测试
```

#### 测试方法命名
```python
# 格式：test_具体测试场景
def test_data_overview_api(self):         # API接口测试
def test_accuracy_trend_data_generation(self): # 数据生成测试
def test_date_range_validation(self):     # 数据验证测试
```

### 测试环境配置

#### MySQL测试数据库
```python
# tests/test_settings_mysql.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test_alpha_db',
        'USER': 'root',
        'PASSWORD': 'meimei520',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

#### pytest配置
```ini
# tests/pytest.ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = tests.test_settings_mysql
pythonpath = backend
addopts = -v --tb=short
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    api: marks tests as API tests
```

### 故障排除

#### 常见问题
1. **ImportError**: 检查Python路径和模块导入
2. **数据库连接失败**: 确认MySQL服务运行和配置正确
3. **权限错误**: 检查文件权限和数据库用户权限
4. **测试失败**: 查看详细错误信息和测试报告

#### 调试技巧
```bash
# 运行单个测试文件
python -m pytest tests/regression/english/test_data_analysis.py -v

# 运行单个测试方法
python -m pytest tests/regression/english/test_data_analysis.py::TestDataAnalysisAPI::test_data_overview_api -v

# 显示详细错误信息
python -m pytest tests/regression/ -v --tb=long
```

### 功能测试
1. **导航测试**
   - 访问 http://localhost:5173
   - 测试所有菜单项
   - 验证移动端响应式效果

2. **英语学习模块测试**
   - 词汇学习：http://localhost:5173/english/vocabulary
   - 智能练习：http://localhost:5173/english/practice
   - **新闻爬取测试**：http://localhost:5173/english/news-dashboard
     - 测试爬取设置（选择新闻源、设置爬取数量）
     - 验证新闻爬取功能（Fundus爬虫）
     - 检查新闻图片显示
     - 测试新闻管理功能（删除、可见性设置）
   - 阅读训练：http://localhost:5173/english/reading

3. **新闻爬虫测试**
   ```bash
   # 使用传统爬虫
   python manage.py crawl_news --source bbc --crawler traditional
   
   # 使用Fundus爬虫（推荐，数据质量更高）
   python manage.py crawl_news --source bbc --crawler fundus
   
   # 使用两种爬虫
   python manage.py crawl_news --source all --crawler both
   
   # 测试模式（不保存到数据库）
   python manage.py crawl_news --source bbc --crawler fundus --dry-run --verbose
   
   # 支持的新闻源
   # 传统爬虫: bbc, cnn, reuters, techcrunch, local_test, xinhua
   # Fundus爬虫: bbc, cnn, reuters, techcrunch, the_guardian, the_new_york_times, wired, ars_technica, hacker_news, stack_overflow
   
   # 图片功能
   # - 自动下载新闻图片到 media/news_images/ 目录
   # - 支持多种图片格式（jpg, png, gif等）
   # - 使用唯一文件名避免重复
   # - 图片可通过 /media/news_images/ 路径访问
   # - 新闻内容和图片严格对应，确保完整性

   # 新闻管理功能
   # - 支持单条新闻删除（同时删除对应图片）
# - 支持批量删除新闻
# - 按来源筛选（BBC、TechCrunch、The Guardian等）
# - 按难度筛选（初级、中级、高级）
# - 显示难度标签和统计信息

# 测试功能
# - 单元测试：tests/unit/test_news_functionality.py
# - 集成测试：tests/integration/test_news_integration.py
# - 调试脚本：quick_debug.py, simple_test.py, test_service.py
# - 测试覆盖：API端点、数据库操作、图片文件、抓取功能

# 图片显示修复
# - 修复了后端URL配置中的媒体文件重复配置问题
# - 修复了Vite代理配置，正确处理/api/media/路径重写
# - 图片现在可以通过前端代理正确访问：/api/media/news_images/xxx.jpg
# - 前端图片URL构建逻辑：getImageUrl()函数处理本地和外部图片
   ```

4. **API测试**
   ```bash
   # 健康检查
   curl http://localhost:8000/api/v1/health/
   
   # 用户认证
   curl -X POST http://localhost:8000/api/v1/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username":"testuser","password":"testpass123"}'
   ```

### 测试账号
- **用户名**: `testuser`
- **密码**: `testpass123`
- **邮箱**: `test@example.com`

### 创建测试数据
```bash
cd backend
python manage.py import_english_seed --file ../tests/fixtures/english_seed.json
```

---

## 🚀 部署指南

### 生产环境部署
1. **环境配置**
   ```bash
   cp production.env.example production.env
   # 编辑 production.env 文件
   ```

2. **Docker部署**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Kubernetes部署**
   ```bash
   kubectl apply -f k8s/
   ```

### 监控配置
- Prometheus + Grafana 监控
- 日志聚合
- 性能指标收集

---

## 🔧 故障排除

### 启动脚本问题
1. **start-all.bat 无法启动**
   - **问题**: 字符编码问题导致中文显示乱码
   - **解决方案**: 使用 `start-simple.bat`（推荐）或 `start-all.ps1`
   - **原因**: Windows批处理文件在PowerShell环境中的编码问题

2. **PowerShell执行策略限制**
   ```powershell
   # 查看执行策略
   Get-ExecutionPolicy
   
   # 临时允许脚本执行
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### 常见问题
1. **端口冲突**
   - 检查 8000, 5173, 3306, 6379 端口占用
   - 修改 docker-compose.yml 中的端口映射

2. **数据库连接失败**
   ```bash
   docker-compose logs mysql
   docker-compose restart mysql
   ```

3. **前端构建失败**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Python依赖问题**
   ```bash
   cd backend
   pip install -r requirements.txt
   python manage.py migrate
   ```

5. **新闻爬虫网络问题**
   - **问题**: 网络代理或防火墙导致无法访问外部新闻源
   - **解决方案**: 
     - 检查网络代理设置
     - 使用本地测试源：`python manage.py crawl_news --source local_test --crawler traditional`
     - 传统爬虫支持生成高质量新闻，可作为备选方案
   - **测试命令**:
     ```bash
     # 测试传统爬虫（推荐）
     python manage.py crawl_news --source local_test --crawler traditional --dry-run
     
     # 测试Fundus爬虫（需要网络访问）
     python manage.py crawl_news --source bbc --crawler fundus --dry-run
     ```

### 日志查看
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## 📝 开发规范

### 代码规范
- 后端：遵循 PEP 8 规范
- 前端：使用 ESLint + Prettier
- 提交信息：使用 Conventional Commits

### 测试规范
- 单元测试覆盖率 > 80%
- 集成测试覆盖关键路径
- E2E测试覆盖用户流程

## 🧪 测试指南

### 测试环境搭建
```bash
# 安装测试依赖
cd backend
pip install pytest pytest-django pytest-cov factory-boy faker

cd frontend
npm install --save-dev vitest @vue/test-utils jsdom
```

### 运行测试
```bash
# 后端测试
cd tests
pytest                           # 运行所有测试
pytest unit/                     # 运行单元测试
pytest integration/              # 运行集成测试
pytest --cov=backend --cov-report=html  # 生成覆盖率报告

# 前端测试
cd frontend
npm run test:unit               # 运行单元测试
npm run test:coverage           # 生成覆盖率报告
```

### 测试报告
- **后端覆盖率报告**: `tests/htmlcov/index.html`
- **前端覆盖率报告**: `frontend/coverage/index.html`

### 测试数据管理
```bash
# 创建测试数据
python manage.py create_test_data

# 清理测试数据
python manage.py flush --noinput
```

### 常见测试问题
1. **数据库连接问题**
   ```bash
   # 使用测试数据库
   export DJANGO_SETTINGS_MODULE=alpha.test_settings
   ```

2. **测试数据冲突**
   ```bash
   # 重置测试数据库
   python manage.py test --keepdb
   ```

---

*最后更新：2025-01-17*
*更新内容：新增测试系统使用指南，包含一键测试执行、测试覆盖统计、测试编写规范等*

3. **前端测试环境**
   ```bash
   # 确保Node.js版本兼容
   node --version  # 需要 16+
   ```

### 文档规范
- API文档：使用 OpenAPI 3.0
- 代码注释：使用 docstring
- 更新日志：记录所有变更

---

## 📞 支持

如有问题，请：
1. 查看本文档的故障排除部分
2. 检查项目 Issues
3. 联系开发团队

---

## 📚 相关文档

- **项目概述**: `README.md`
- **开发规范**: `docs/DOCUMENTATION_STANDARDS.md`
- **测试规范**: `docs/TESTING_STANDARDS.md`
- **待办事项**: `docs/TODO.md`
- **Fundus集成**: `docs/FUNDUS_INTEGRATION.md`
- **新闻爬虫总结**: `docs/新闻爬虫功能完成总结.md`
- **爬虫架构设计**: `docs/新闻爬虫架构设计文档.md`
- **Qwerty Learn集成**: `docs/QWERTY_LEARN_INTEGRATION_PLAN.md`

---

*最后更新：2024年12月*

   cd backend
   pip install -r requirements.txt
   python manage.py migrate
   ```

5. **新闻爬虫网络问题**
   - **问题**: 网络代理或防火墙导致无法访问外部新闻源
   - **解决方案**: 
     - 检查网络代理设置
     - 使用本地测试源：`python manage.py crawl_news --source local_test --crawler traditional`
     - 传统爬虫支持生成高质量新闻，可作为备选方案
   - **测试命令**:
     ```bash
     # 测试传统爬虫（推荐）
     python manage.py crawl_news --source local_test --crawler traditional --dry-run
     
     # 测试Fundus爬虫（需要网络访问）
     python manage.py crawl_news --source bbc --crawler fundus --dry-run
     ```

### 日志查看
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## 📝 开发规范

### 代码规范
- 后端：遵循 PEP 8 规范
- 前端：使用 ESLint + Prettier
- 提交信息：使用 Conventional Commits

### 测试规范
- 单元测试覆盖率 > 80%
- 集成测试覆盖关键路径
- E2E测试覆盖用户流程

## 🧪 测试指南

### 测试环境搭建
```bash
# 安装测试依赖
cd backend
pip install pytest pytest-django pytest-cov factory-boy faker

cd frontend
npm install --save-dev vitest @vue/test-utils jsdom
```

### 运行测试
```bash
# 后端测试
cd tests
pytest                           # 运行所有测试
pytest unit/                     # 运行单元测试
pytest integration/              # 运行集成测试
pytest --cov=backend --cov-report=html  # 生成覆盖率报告

# 前端测试
cd frontend
npm run test:unit               # 运行单元测试
npm run test:coverage           # 生成覆盖率报告
```

### 测试报告
- **后端覆盖率报告**: `tests/htmlcov/index.html`
- **前端覆盖率报告**: `frontend/coverage/index.html`

### 测试数据管理
```bash
# 创建测试数据
python manage.py create_test_data

# 清理测试数据
python manage.py flush --noinput
```

### 常见测试问题
1. **数据库连接问题**
   ```bash
   # 使用测试数据库
   export DJANGO_SETTINGS_MODULE=alpha.test_settings
   ```

2. **测试数据冲突**
   ```bash
   # 重置测试数据库
   python manage.py test --keepdb
   ```

---

*最后更新：2025-01-17*
*更新内容：新增测试系统使用指南，包含一键测试执行、测试覆盖统计、测试编写规范等*

3. **前端测试环境**
   ```bash
   # 确保Node.js版本兼容
   node --version  # 需要 16+
   ```

### 文档规范
- API文档：使用 OpenAPI 3.0
- 代码注释：使用 docstring
- 更新日志：记录所有变更

---

## 📞 支持

如有问题，请：
1. 查看本文档的故障排除部分
2. 检查项目 Issues
3. 联系开发团队

---

## 📚 相关文档

- **项目概述**: `README.md`
- **开发规范**: `docs/DOCUMENTATION_STANDARDS.md`
- **测试规范**: `docs/TESTING_STANDARDS.md`
- **待办事项**: `docs/TODO.md`
- **Fundus集成**: `docs/FUNDUS_INTEGRATION.md`
- **新闻爬虫总结**: `docs/新闻爬虫功能完成总结.md`
- **爬虫架构设计**: `docs/新闻爬虫架构设计文档.md`
- **Qwerty Learn集成**: `docs/QWERTY_LEARN_INTEGRATION_PLAN.md`

---

*最后更新：2024年12月*
