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

## 🧪 本地测试指南

### 功能测试
1. **导航测试**
   - 访问 http://localhost:5173
   - 测试所有菜单项
   - 验证移动端响应式效果

2. **英语学习模块测试**
   - 词汇学习：http://localhost:5173/english/vocabulary
   - 智能练习：http://localhost:5173/english/practice
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
python manage.py create_test_learning_data
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
