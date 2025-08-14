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
# 方式1：一键启动所有服务
./start-all.bat

# 方式2：分别启动
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
- **待办事项**: `docs/TODO.md`
- **Fundus集成**: `docs/FUNDUS_INTEGRATION.md`
- **新闻爬虫总结**: `docs/新闻爬虫功能完成总结.md`
- **爬虫架构设计**: `docs/新闻爬虫架构设计文档.md`

---

*最后更新：2024年12月*
