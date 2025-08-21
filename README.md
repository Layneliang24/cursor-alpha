# Alpha技术共享平台

## 📋 项目概述

**Alpha技术共享平台** 是一个综合性的技术学习和分享平台，集成了英语学习、求职管理、待办笔记、AI助手和搜索功能。

## 🎯 核心功能

### 📚 英语学习模块
- 词汇学习和记忆系统
- 智能练习和复习算法
- 英语新闻阅读和爬虫
- 学习进度跟踪

### 💼 求职管理模块
- 职位信息管理
- 简历投递跟踪
- 面试安排提醒
- 求职进度统计

### 📝 待办笔记模块
- 任务清单管理
- 笔记记录和整理
- 提醒和通知系统
- 标签和分类

### 🤖 AI助手模块
- 智能对话系统
- 学习辅助功能
- 内容生成和优化
- 个性化推荐

### 🔍 搜索模块
- 跨模块内容搜索
- 智能推荐
- 搜索历史记录
- 结果高亮显示



## 🎨 界面设计

### 整体布局
- **顶部**: 导航菜单和用户信息
- **左侧**: 功能模块侧边栏
- **主区域**: 内容展示和操作界面
- **响应式**: 支持移动端和桌面端

### 界面特点
- 现代化的设计风格
- 响应式布局，适配各种设备
- 直观的用户交互
- 丰富的数据可视化

## 🔧 技术架构

### 前端技术栈
- **框架**: Vue.js 3 + TypeScript
- **UI组件**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **构建工具**: Vite

### 后端技术栈
- **框架**: Django + Django REST Framework
- **数据库**: MySQL + Redis
- **异步任务**: Celery
- **API文档**: OpenAPI 3.0

### 部署技术
- **容器化**: Docker + Docker Compose
- **编排**: Kubernetes
- **监控**: Prometheus + Grafana
- **反向代理**: Nginx

## 📦 项目结构

```
cursor-alpha/
├── backend/                # 后端代码
│   ├── apps/              # Django应用
│   │   ├── api/           # 核心API
│   │   ├── english/       # 英语学习模块
│   │   ├── jobs/          # 求职模块
│   │   ├── todos/         # 待办笔记模块
│   │   ├── ai/            # AI助手模块
│   │   └── common/        # 公共模块
│   └── alpha/             # Django项目配置
├── frontend/              # 前端代码
│   ├── src/               # 源代码
│   │   ├── components/    # Vue组件
│   │   ├── views/         # 页面视图
│   │   ├── stores/        # Pinia状态管理
│   │   └── utils/         # 工具函数
│   └── public/            # 静态资源
├── docs/                  # 文档目录
│   ├── GUIDE.md           # 统一指南
│   ├── TODO.md            # 待办清单
│   └── spec/              # 规范文档
├── tests/                 # 测试目录
│   ├── unit/              # 单元测试
│   ├── integration/       # 集成测试
│   ├── e2e/               # 端到端测试
│   └── fixtures/          # 测试数据
├── docker-compose.yml     # Docker编排
├── k8s/                   # Kubernetes配置
└── README.md              # 项目说明
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 8.0+ (生产环境)
- Redis 6.0+ (生产环境)

### 一键部署 (推荐)

#### Windows 用户
```bash
# 1. 克隆项目
git clone <repository-url>
cd cursor-alpha

# 2. 运行一键部署脚本
setup_project.bat

# 3. 验证部署
python check_environment.py
python verify_tests.py
```

#### Linux/macOS 用户
```bash
# 1. 克隆项目
git clone <repository-url>
cd cursor-alpha

# 2. 运行一键部署脚本
chmod +x setup_project.sh
./setup_project.sh

# 3. 验证部署
python check_environment.py
python verify_tests.py
```

### 手动安装步骤

1. **环境检查**
```bash
python check_environment.py
```

2. **后端设置**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

3. **前端设置**
```bash
cd frontend
npm install
npm run dev
```

4. **测试验证**
```bash
# 运行测试
run_tests.bat  # Windows
# 或 ./run_tests.sh  # Linux/macOS

# 验证测试流程
python verify_tests.py
```

5. **启动服务（推荐使用热重载脚本）**
```bash
# 方式1：使用热重载脚本（推荐）
# 在项目根目录运行
start_dev.bat

# 方式2：手动启动
# 后端（支持热重载）
cd backend
python run_dev.py
# 或
run_dev.bat

# 前端（支持热重载）
cd frontend
run_dev.bat
# 或
npm run dev
```

### 🔥 热重载功能

- **后端热重载**：修改 Python 代码后，Django 服务器自动重启
- **前端热重载**：修改 Vue 组件后，浏览器自动刷新
- **开发体验**：无需手动重启服务，提升开发效率

详细说明请查看：[热重载指南](docs/HOT_RELOAD_GUIDE.md)

### 详细指南
请查看 [docs/GUIDE.md](docs/GUIDE.md) 获取详细的使用指南和开发文档。

### 部署指南
请查看 [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) 获取完整的部署说明。

### 测试指南
请查看 [docs/TESTING_STANDARDS.md](docs/TESTING_STANDARDS.md) 了解测试规范和流程。

### 待办事项
请查看 [docs/TODO.md](docs/TODO.md) 了解项目进度和后续计划。

## 📊 数据流程

### 查询流程
1. **用户输入参数** → 2. **参数验证** → 3. **查询模板渲染** → 4. **Kibana API调用** → 5. **数据解析** → 6. **结果展示**

### 错误处理
- 网络连接异常
- 认证失败
- 查询超时
- 数据格式错误
- 权限不足

## 🎯 用户体验设计

### 交互设计原则
1. **简洁明了**: 界面简洁，操作直观
2. **快速响应**: 查询结果快速返回
3. **错误友好**: 清晰的错误提示和解决建议
4. **数据可视化**: 图表展示，便于分析

### 快捷键支持
- `Ctrl + Enter`: 执行查询
- `Ctrl + S`: 保存配置
- `Ctrl + E`: 导出结果
- `F5`: 刷新数据

### 历史记录功能
- 保存最近10次查询
- 支持查询条件复用
- 查询结果缓存

## 🔒 安全设计

### 数据安全
- 敏感信息加密存储
- 连接信息本地保存
- 查询日志审计

### 权限控制
- 用户角色管理
- 功能模块权限
- 数据访问控制

## 📈 性能优化

### 查询优化
- 查询结果分页
- 数据缓存机制
- 异步查询处理

### 界面优化
- 虚拟滚动
- 懒加载
- 防抖处理

## 🚀 部署方案

### 打包发布
- Electron Builder打包
- 自动更新机制
- 安装程序制作

### 配置管理
- 配置文件热更新
- 多环境配置支持
- 配置导入导出

## 📋 开发计划

### Phase 1 (2周)
- [ ] 基础框架搭建
- [ ] Kibana连接模块
- [ ] 基础设置界面

### Phase 2 (3周)
- [ ] 盈亏计算模块
- [ ] 风控日志模块
- [ ] 资金流水模块

### Phase 3 (2周)
- [ ] 持仓信息模块
- [ ] 购买力模块
- [ ] 条件单模块

### Phase 4 (1周)
- [ ] 数据可视化
- [ ] 导出功能
- [ ] 性能优化

## 📞 技术支持

### 文档支持
- 用户使用手册
- API文档
- 故障排除指南

### 维护计划
- 定期功能更新
- Bug修复
- 性能优化

## 📄 许可证

MIT License

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个项目。

---

**版本**: v1.0  
**创建日期**: 2024-01-15  
**最后更新**: 2024-01-15