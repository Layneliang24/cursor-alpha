# Alpha 项目全局待办清单

> 本文档跟踪 Alpha 项目（博客 + 英语学习 + 求职 + 代办/笔记 + AI + 搜索）全局进度与后续工作安排。面向后续模块化扩展，避免局部优化带来冲突。

## 一、已完成工作 ✅

### 后端全局骨架
- ✅ 健康检查接口：`GET /api/health/`（应用/数据库/可选 Redis）
- ✅ API 文档：`/api/swagger/`、`/api/redoc/`
- ✅ 统一异常处理器：`apps/api/exceptions.py`（全局配置 `REST_FRAMEWORK.EXCEPTION_HANDLER`）
- ✅ 统一响应方法：`apps/api/response.py`（success/error）
- ✅ 公共模型基类：`apps/common/models.py`（`TimestampedModel`、`SoftDeleteModel`、`OwnedModel`）

### 英语学习模块（后端）
- ✅ 完整的模型、序列化、视图、路由、权限、分页系统
- ✅ 软删除/审计字段支持
- ✅ 复习流程：`GET /api/v1/english/progress/review/` 列表、`POST /api/v1/english/progress/{id}/review/` 打卡
- ✅ 种子数据导入命令：`import_english_seed`
- ✅ **新闻爬虫系统**：
  - ✅ 混合模式新闻抓取（真实RSS + 高质量生成）
  - ✅ 多新闻源支持（China Daily、新华社英语、生成新闻）
  - ✅ 图片抓取和显示功能
  - ✅ 智能内容过滤和质量保证
  - ✅ 自动生成理解题目和关键词汇
  - ✅ 新闻抓取API：`POST /api/v1/english/news/crawl/`
  - ✅ Fundus爬虫框架集成完成（支持150+个高质量新闻源）
  - ✅ 支持多种爬虫类型（traditional/fundus/both）
  - ✅ 延迟初始化机制，避免导入错误

### Celery/Redis 异步任务
- ✅ `alpha/celery.py` 启动配置
- ✅ `CELERY_BROKER_URL`/`CELERY_RESULT_BACKEND` 环境变量配置
- ✅ docker-compose 新增 `redis`、`celery`、`celery_beat` 服务

### 多模块占位骨架（后端）
- ✅ 求职模块：`/api/v1/jobs/`（占位 ViewSet）
- ✅ 代办/笔记模块：`/api/v1/todos/`（占位 ViewSet）
- ✅ AI 模块：`/api/v1/ai/conversations/`（占位 ViewSet）
- ✅ 搜索模块：`/api/v1/search/`（占位 API）

### 前端（英语模块）
- ✅ API 封装、Pinia store、路由配置
- ✅ 页面骨架：Words/WordDetail/Expressions/NewsList/NewsDetail
- ✅ 顶部导航与侧边栏入口（英语学习、英语新闻）
- ✅ **新闻管理界面**：
  - ✅ 多源新闻抓取下拉菜单（China Daily、新华社、TechCrunch等）
  - ✅ 新闻列表图片显示和预览
  - ✅ 抓取进度反馈和统计信息
  - ✅ 新闻详情页面和阅读体验
- ✅ "复习/打卡"对话框交互

### 测试与质量
- ✅ pytest 基础配置与冒烟用例（health、api-root、jobs/todos 占位）
- ✅ Debug Toolbar 在 pytest 下自动禁用
- ✅ PowerShell/curl、登录表单等问题排查与修正

### 部署与运维
- ✅ Docker Compose 配置（开发/生产环境）
- ✅ Kubernetes 部署配置
- ✅ 监控系统配置（Prometheus + Grafana）
- ✅ 权限系统设计

## 二、进行中工作 🔄

- 🔄 将英语模块部分 ViewSet 接入统一响应工具（逐步替换，保持兼容）
- ✅ 新闻爬虫功能本地测试和优化
- ✅ 项目文件结构整理和规范化
- ✅ Fundus爬虫框架集成完成
- ✅ 启动脚本问题修复和优化

## 三、下一阶段规划（2-3 周）📋

### 后端全局优化
- [ ] 统一分页响应结构与查询参数规范（page/page_size/order_by/q 等）
- [ ] 统一权限与审计中间件（操作人/资源/动作/结果）
- [ ] 统一速率限制与缓存策略（结合 `docs/spec/rate_limit.yaml`）
- [ ] 配置 GitHub Actions：Lint + Pytest（最小 CI）

### 英语学习模块完善
- [ ] 复习算法升级为 SM-2（参数化），增加可视化进度字段
- [ ] **新闻爬虫优化**：
  - ✅ 集成Fundus爬虫框架，提升数据质量
  - ✅ 支持多种爬虫类型（传统爬虫 + Fundus爬虫）
  - ✅ 增加更多国内可访问的英语新闻源
  - ✅ 完成新闻爬虫架构设计文档（包含Firecrawl、Crawl4AI方案）
  - ✅ Fundus包依赖已添加到requirements.txt
- ✅ 修复Fundus服务实例化问题
- ✅ 解决网络代理问题，Fundus爬虫现在可以正常访问外部新闻源
- ✅ 增强图片下载功能，支持自动下载和本地保存新闻图片
- ✅ 前端新闻模块完全支持Fundus爬虫，包括图片显示功能
- ✅ 新闻管理功能：删除新闻、批量删除、分类筛选
- ✅ 单元测试和集成测试覆盖所有新闻功能
- [ ] 验证Fundus抓取新闻时图片下载功能
- [ ] 修复前端新闻列表和详情页图片显示
  - [ ] 新闻内容去重和更新机制
  - [ ] 新闻分类和标签系统
  - [ ] 新闻阅读统计和学习记录
  - [ ] 评估Firecrawl集成需求（中期规划）
  - [ ] 评估Crawl4AI集成需求（长期规划）

- [ ] **Qwerty Learn集成**：
  - ✅ 完成Qwerty Learn集成计划文档
  - [ ] 第一阶段：基础集成（2-3周）
    - [ ] 数据模型设计（词汇、学习进度）
    - [ ] 核心API开发（词汇管理、学习进度）
    - [ ] SM-2算法实现
    - [ ] 基础前端界面
  - [ ] 第二阶段：智能增强（2-3周）
    - [ ] AI集成（例句生成、难度评估）
    - [ ] 推荐系统（基于内容、协同过滤）
    - [ ] 学习数据分析
    - [ ] 用户体验优化
  - [ ] 第三阶段：高级功能（2-3周）
    - [ ] 学习社区功能
    - [ ] 内容生成（基于新闻的词汇提取）
    - [ ] 移动端适配
    - [ ] 系统深度集成
- [ ] 完善单词来源爬取/同步任务（Wiktionary 等），加入版权/来源合规标记
- [ ] 模型继承公共基类并补全索引（查询性能）
- [ ] 后端契约测试与权限测试

### 求职模块（Jobs）
- [ ] 设计数据表（职位、公司、投递、状态流转、标签）与迁移
- [ ] 基础 CRUD API（列表/详情/创建/更新/删除）与筛选（地域/标签/状态）
- [ ] Celery 任务：职位订阅/同步（可选）
- [ ] 基础前端页面骨架与路由

### 代办/笔记模块（Todos/Notes）
- [ ] 设计数据表（清单、任务、标签、提醒、笔记）与迁移
- [ ] 基础 CRUD API 与筛选（优先级/标签/到期）
- [ ] 定时提醒（Celery Beat）与通知占位（后续接入）
- [ ] 基础前端页面骨架与路由

### AI 模块
- [ ] 会话与消息数据表（版本与来源字段）
- [ ] 简单对话流 API（后端占位实现 + 前端聊天面板骨架）
- [ ] 与英语模块的联动：例句生成/纠错/打分（配额与速率限制）

### 搜索模块
- [ ] 简单关键词检索（跨文章/单词/表达/新闻）
- [ ] 搜索结果聚合与高亮（后续可接入 ES/Meilisearch）

### 部署与运维
- [ ] 生产环境 docker-compose 清单与 .env 模板对齐 `docs/spec/env.yaml`
- [ ] 轻量监控（Prometheus/Grafana 可选）与日志切割
- [ ] 备份策略（数据库/媒体）

### 测试与质量
- [ ] 各模块最小 API 契约测试覆盖
- [ ] 端到端（E2E）基础场景（登录 → 浏览 → 操作）
- [ ] 性能冒烟测试（分页列表、抓取任务）

### 文档整理
- ✅ 统一所有指南文件到 `docs/GUIDE.md`
- ✅ 整理测试文件到 `tests/` 目录
- ✅ 清理重复的说明文件和启动脚本
- ✅ 建立文档更新规范

## 四、里程碑时间表 🎯

- **M1（+1 周）**：全局统一响应/异常/分页/权限规范落地，CI 打通，文档整理完成，Fundus爬虫集成完成
- **M2（+2 周）**：英语模块（复习 SM-2 + 新闻抓取）闭环、求职/代办最小可用 CRUD
- **M3（+3-4 周）**：AI 对话基础联动、搜索跨模块检索、E2E 测试通过

## 五、风险与待决策 ⚠️

- **外部数据源**：词典/新闻频率与版权限制，需限制速率与缓存，明确来源与 License 字段
- **数据规模**：增长的索引策略与归档，提前在 DDL 设计中体现
- **AI 接口**：成本与稳定性，需设置配额、降级与熔断策略
- **搜索引擎**：是否引入专门搜索引擎（ES/Meilisearch），M3 再评估

## 六、执行指引 🚀

### 本地开发启动
```bash
# 启动 Celery Worker/Beat（如需）
cd backend && celery -A alpha worker --loglevel=INFO
cd backend && celery -A alpha beat --loglevel=INFO

# 运行测试
cd backend && pytest -q
```

### 项目结构
```
backend/apps/
├── api/          # 核心 APIs (auth/users/articles/categories/links)
├── english/      # 英语学习模块
├── jobs/         # 求职模块 (skeleton)
├── todos/        # 代办/笔记模块 (skeleton)
├── ai/           # AI助手模块 (skeleton)
├── search/       # 搜索模块 (skeleton)
└── common/       # 共享基类/工具

tests/            # 统一测试目录
├── unit/         # 单元测试
├── integration/  # 集成测试
├── e2e/          # 端到端测试
└── fixtures/     # 测试数据

docs/             # 文档目录
├── GUIDE.md      # 统一指南
├── TODO.md       # 待办清单
└── spec/         # 规范文档
```

---

> 📝 **注意**：本文档会在每个阶段结束时更新，作为跨模块协作与自动化开发的主清单。所有模块采用统一的架构模式，确保扩展性与维护性。
