# Alpha技术共享平台 - 统一指南

## 📋 目录
- [系统概述](#系统概述)
- [功能模块](#功能模块)
- [快速启动](#快速启动)
- [使用指南](#使用指南)
- [故障排除](#故障排除)
- [测试指南](#测试指南)

---

## 🎯 系统概述

Alpha技术共享平台是一个集技术文章分享、英语学习、新闻阅读于一体的综合性平台。采用前后端分离架构，提供现代化的用户体验和强大的功能支持。

### 核心特性
- 🚀 **技术文章管理**：完整的文章发布、编辑、分类、标签系统
- 🎯 **英语学习系统**：智能单词学习、新闻阅读、打字练习
- 📰 **新闻爬取系统**：实时爬取高质量英语新闻，自动图片下载
- 👥 **用户管理系统**：用户认证、权限管理、个人资料
- 📊 **数据分析系统**：学习进度可视化，学习效果分析
- 🔧 **现代化技术栈**：Django + Vue 3 + MySQL + Redis

### 技术架构
- **后端**: Django 5.2 + Django REST Framework
- **前端**: Vue 3 + Vite + Element Plus
- **数据库**: MySQL 8.0 + Redis 6.0
- **部署**: Docker + Docker Compose
- **测试**: pytest + 完整测试框架

---

## 🏗️ 功能模块

### 1. 用户系统
- **用户认证**
  - 用户注册/登录
  - JWT Token认证
  - 密码重置
  - 邮箱验证

- **权限管理**
  - 角色基础权限控制
  - 细粒度权限管理
  - 用户组管理
  - 权限继承

- **个人资料**
  - 头像管理
  - 个人简介
  - 技能标签
  - 社交链接

### 2. 文章系统
- **文章管理**
  - 文章创建/编辑/删除
  - 草稿/发布/归档状态
  - 富文本编辑器
  - 版本控制

- **分类标签**
  - 层级分类管理
  - 标签系统
  - 分类统计
  - 标签云展示

- **互动功能**
  - 评论系统（多级评论）
  - 点赞/收藏
  - 浏览量统计
  - 阅读时间估算

### 3. 英语学习系统
- **单词学习**
  - 多词典支持（CET4、CET6、GRE、IELTS等）
  - 智能复习算法（间隔重复）
  - 学习进度跟踪
  - 掌握程度评估

- **新闻阅读**
  - 实时新闻爬取
  - 难度分级
  - 关键词提取
  - 阅读理解题

- **打字练习**
  - 多种练习模式
  - 实时反馈
  - 速度/准确率统计
  - 错误分析

- **学习分析**
  - 学习热力图
  - 进度趋势图
  - 学习统计报告
  - 个性化建议

### 4. 新闻爬取系统
- **爬虫引擎**
  - Fundus爬虫（高质量内容）
  - 传统爬虫（备选方案）
  - 自动图片下载
  - 内容去重

- **新闻源支持**
  - BBC News
  - CNN
  - Reuters
  - TechCrunch
  - The Guardian

- **内容管理**
  - 自动分类
  - 难度标记
  - 关键词提取
  - 批量操作

---

## 🚀 快速启动

### 环境要求
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Node.js**: 18+（可选，用于前端开发）
- **Python**: 3.9+（可选，用于后端开发）

### 一键启动（推荐）

#### Windows用户
```bash
# 使用批处理文件
./start-simple.bat

# 或使用PowerShell
./start-all.ps1
```

#### Linux/Mac用户
```bash
# 启动所有服务
docker-compose up -d

# 或分别启动
docker-compose up -d mysql redis
docker-compose up -d backend frontend
```

### 分别启动

#### 1. 启动数据库服务
```bash
# 启动MySQL和Redis
docker-compose up -d mysql redis

# 检查服务状态
docker-compose ps
```

#### 2. 启动后端服务
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

#### 3. 启动前端服务
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 访问地址
- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:8000/api/v1/
- **管理后台**: http://localhost:8000/admin/
- **API文档**: http://localhost:8000/api/swagger/

---

## 📖 使用指南

### 1. 用户注册和登录

#### 注册新用户
1. 访问 http://localhost:5173/register
2. 填写用户名、邮箱、密码
3. 点击注册按钮
4. 验证邮箱（如果启用）

#### 用户登录
1. 访问 http://localhost:5173/login
2. 输入用户名和密码
3. 点击登录按钮
4. 系统自动跳转到首页

### 2. 英语学习功能

#### 单词学习
1. 访问 http://localhost:5173/english/words
2. 选择词典（CET4、CET6、GRE等）
3. 开始学习新单词
4. 系统自动安排复习计划

#### 新闻阅读
1. 访问 http://localhost:5173/english/news-dashboard
2. 选择新闻源和数量
3. 点击"开始爬取"
4. 阅读爬取的新闻内容

#### 打字练习
1. 访问 http://localhost:5173/english/typing-practice
2. 选择词典和章节
3. 开始打字练习
4. 查看练习统计和进度

### 3. 文章管理功能

#### 发布文章
1. 访问 http://localhost:5173/articles/create
2. 填写文章标题和内容
3. 选择分类和标签
4. 设置发布状态
5. 点击发布按钮

#### 管理文章
1. 访问 http://localhost:5173/articles/manage
2. 查看所有文章列表
3. 编辑或删除文章
4. 管理评论和互动

### 4. 新闻爬取功能

#### 使用爬虫命令
```bash
# 使用Fundus爬虫（推荐）
python manage.py crawl_news --source bbc --crawler fundus --count 10

# 使用传统爬虫
python manage.py crawl_news --source bbc --crawler traditional --count 10

# 测试模式
python manage.py crawl_news --source bbc --crawler fundus --dry-run --verbose
```

#### 支持的新闻源
- **传统爬虫**: bbc, cnn, reuters, techcrunch, local_test, xinhua
- **Fundus爬虫**: bbc, cnn, reuters, techcrunch, the_guardian, the_new_york_times, wired, ars_technica, hacker_news, stack_overflow

---

## 🔧 故障排除

### 常见问题

#### 1. 启动脚本问题

**问题**: 启动脚本无法执行或显示乱码
**解决方案**:
- 使用 `start-simple.bat`（推荐）
- 或使用 `start-all.ps1`（PowerShell）
- 检查PowerShell执行策略

```powershell
# 查看执行策略
Get-ExecutionPolicy

# 临时允许脚本执行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 2. 端口冲突

**问题**: 服务启动失败，提示端口被占用
**解决方案**:
```bash
# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# 关闭占用进程
taskkill /PID <进程ID> /F

# 或修改docker-compose.yml中的端口映射
```

#### 3. 数据库连接失败

**问题**: 应用启动失败，数据库连接错误
**解决方案**:
```bash
# 检查MySQL服务状态
docker-compose ps mysql

# 查看MySQL日志
docker-compose logs mysql

# 重启MySQL服务
docker-compose restart mysql

# 测试数据库连接
python manage.py dbshell
```

#### 4. 前端构建失败

**问题**: 前端页面无法访问或显示错误
**解决方案**:
```bash
cd frontend

# 清理依赖
rm -rf node_modules package-lock.json

# 重新安装依赖
npm install

# 启动开发服务器
npm run dev
```

#### 5. 新闻爬取网络问题

**问题**: 爬虫无法访问外部新闻源
**解决方案**:
- 检查网络代理设置
- 使用本地测试源
- 配置网络防火墙规则

```bash
# 测试传统爬虫（推荐）
python manage.py crawl_news --source local_test --crawler traditional --dry-run

# 测试Fundus爬虫
python manage.py crawl_news --source bbc --crawler fundus --dry-run
```

### 日志查看

#### 查看服务日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mysql
```

#### 查看应用日志
```bash
# 查看Django日志
tail -f backend/logs/django.log

# 查看前端日志
cd frontend && npm run dev
```

---

## 🧪 测试指南

### 测试系统概述

#### 测试结构
```
tests/
├── unit/                    # 单元测试
├── integration/             # 集成测试
├── regression/              # 回归测试
├── new_features/            # 新功能测试
├── resources/               # 测试资源
├── reports/                 # 测试报告
├── run_tests.py            # 一键测试脚本
└── pytest.ini             # pytest配置
```

#### 测试覆盖情况
- **总功能数**: 89个
- **已有测试**: 16个 ✅
- **总体覆盖率**: 18.0%
- **高优先级功能覆盖率**: 50.0%

### 运行测试

#### 一键测试执行
```bash
# 运行所有测试
python tests/run_tests.py --mode=full

# 运行回归测试
python tests/run_tests.py --mode=regression

# 运行指定模块测试
python tests/run_tests.py --module=english
python tests/run_tests.py --module=auth
```

#### 使用pytest
```bash
cd tests

# 运行所有测试
pytest

# 运行特定测试
pytest unit/
pytest integration/
pytest regression/english/

# 生成覆盖率报告
pytest --cov=backend --cov-report=html
```

### 测试报告

#### 查看测试报告
```bash
# 测试报告位置
tests/reports/html/
├── full_report.html          # 完整测试报告
├── regression_report.html    # 回归测试报告
├── auth_report.html          # 认证模块报告
├── english_report.html       # 英语模块报告
└── test_summary.html         # 测试总结报告
```

#### 生成测试报告
```bash
# 生成HTML报告
python tests/run_tests.py --report=html

# 生成JSON报告
python tests/run_tests.py --report=json

# 生成覆盖率报告
python tests/run_tests.py --coverage
```

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

---

## 📚 相关文档

### 核心文档
- **[开发者指南](DEVELOPMENT.md)** - 开发环境搭建、代码规范、测试指南
- **[API文档](API.md)** - 完整的API接口文档
- **[部署指南](DEPLOYMENT.md)** - 部署运维、监控、故障处理
- **[常见问题](FAQ.md)** - 问题解答和故障排除
- **[更新日志](CHANGELOG.md)** - 版本更新历史

### 模块文档
- **[英语学习模块](modules/ENGLISH_LEARNING.md)** - 英语学习功能详解
- **[新闻系统模块](modules/NEWS_SYSTEM.md)** - 新闻爬取和管理
- **[文章系统模块](modules/ARTICLE_SYSTEM.md)** - 文章管理功能
- **[用户系统模块](modules/USER_SYSTEM.md)** - 用户认证和权限

### 技术文档
- **[系统架构](technical/ARCHITECTURE.md)** - 整体架构设计
- **[数据库设计](technical/DATABASE.md)** - 数据库模型和设计
- **[安全规范](technical/SECURITY.md)** - 安全策略和规范
- **[性能优化](technical/PERFORMANCE.md)** - 性能调优指南

### 运维文档
- **[监控方案](operations/MONITORING.md)** - 系统监控和告警
- **[备份策略](operations/BACKUP.md)** - 数据备份和恢复
- **[扩展方案](operations/SCALING.md)** - 系统扩展和优化

---

## 📞 支持

### 技术支持
- 查看 [常见问题](FAQ.md) 解决使用问题
- 参考 [开发者指南](DEVELOPMENT.md) 了解技术细节
- 查看 [部署指南](DEPLOYMENT.md) 解决部署问题

### 问题反馈
- 提交Issue：[GitHub Issues](https://github.com/your-repo/issues)
- 功能建议：[Feature Request](https://github.com/your-repo/issues/new?template=feature_request.md)
- Bug报告：[Bug Report](https://github.com/your-repo/issues/new?template=bug_report.md)

### 联系信息
- 项目维护者: maintainer@your-domain.com
- 技术支持: support@your-domain.com
- 紧急联系: +86-xxx-xxxx-xxxx

---

*最后更新：2025-01-17*
*更新内容：重构文档结构，整合现有内容，创建完整的用户指南*

---

## 附录：产品愿景（合并自 01-产品概述/产品愿景.md）

# Alpha 个人学习与工作管理平台 - 产品愿景

## 🎯 产品愿景

**打造一个集学习、工作、生活于一体的个人数字管理平台，让每个人都能高效地管理自己的知识、技能和职业发展。**

## 🌟 核心价值主张

### 1. 个人知识管理中心
- **知识积累**: 通过博客记录学习心得和技术分享
- **知识获取**: 智能爬虫自动收集最新技术资讯
- **知识应用**: AI助手辅助知识理解和应用

### 2. 技能提升平台
- **英语学习**: 系统化的英语学习路径和工具
- **技能跟踪**: 记录学习进度和能力提升
- **实践应用**: 将学习成果转化为实际项目

### 3. 职业发展助手
- **简历管理**: 专业的简历设计和维护工具
- **求职跟踪**: 完整的求职流程管理
- **能力评估**: 客观的能力评估和发展建议

### 4. 生活管理工具
- **任务管理**: 高效的待办事项和项目管理
- **笔记系统**: 结构化的知识记录和整理
- **时间管理**: 智能的时间规划和提醒

## 🎨 产品特色

### 1. 模块化设计
- **独立模块**: 每个功能模块可独立使用和升级
- **灵活组合**: 用户可根据需要选择启用模块
- **扩展性强**: 支持新模块的快速集成

### 2. 个人化体验
- **个性化配置**: 根据个人习惯定制界面和功能
- **智能推荐**: AI驱动的个性化内容推荐
- **隐私保护**: 个人数据完全自主控制

### 3. 智能化服务
- **AI助手**: 24/7智能问答和辅助服务
- **自动化**: 智能爬虫、提醒、备份等自动化功能
- **数据分析**: 个人学习和工作的数据洞察

### 4. 多平台支持
- **响应式设计**: 完美适配PC、平板、手机
- **离线支持**: 核心功能支持离线使用
- **数据同步**: 多设备间数据无缝同步

## 🚀 产品目标

### 短期目标 (3-6个月)
- [ ] 完成核心模块的基础功能开发
- [ ] 建立模块化架构和权限系统
- [ ] 实现基础的AI助手功能
- [ ] 完成响应式界面设计

### 中期目标 (6-12个月)
- [ ] 完善所有模块的高级功能
- [ ] 优化AI助手和智能推荐
- [ ] 建立完善的数据分析系统
- [ ] 实现多设备数据同步

### 长期目标 (1-2年)
- [ ] 建立个人知识图谱
- [ ] 实现跨平台生态集成
- [ ] 开发移动端原生应用
- [ ] 建立用户社区和分享机制

## 🎯 用户价值

### 对学习者的价值
- **系统化学习**: 提供结构化的学习路径和工具
- **知识管理**: 高效的知识收集、整理和应用
- **技能提升**: 持续的能力评估和提升建议

### 对求职者的价值
- **职业规划**: 清晰的职业发展路径规划
- **简历优化**: 专业的简历设计和维护
- **求职管理**: 完整的求职流程跟踪和管理

### 对工作者的价值
- **效率提升**: 智能的任务管理和时间规划
- **知识积累**: 持续的知识学习和技能提升
- **工作平衡**: 合理的工作和生活时间管理

## 🌍 社会价值

### 1. 促进终身学习
- 鼓励持续学习和技能提升
- 建立个人知识管理体系
- 推动知识分享和传播

### 2. 提升就业能力
- 帮助求职者提升竞争力
- 提供职业发展指导
- 促进人才市场匹配

### 3. 推动数字化转型
- 个人数字管理工具普及
- 智能化生活和工作方式
- 数据驱动的决策支持

## 📈 成功指标

### 用户指标
- **活跃用户**: 日活跃用户数和使用时长
- **用户留存**: 用户留存率和回访频率
- **用户满意度**: 用户反馈和评分

### 功能指标
- **模块使用率**: 各模块的使用情况
- **功能完成率**: 用户任务的完成情况
- **系统性能**: 响应时间和稳定性

### 业务指标
- **数据增长**: 用户数据和学习内容增长
- **功能迭代**: 新功能开发和优化速度
- **技术债务**: 代码质量和系统维护成本

## 🔮 未来展望

### 技术发展方向
- **AI增强**: 更智能的AI助手和推荐系统
- **区块链**: 去中心化的数据存储和验证
- **AR/VR**: 沉浸式的学习和工作体验

### 功能扩展方向
- **社交功能**: 用户间的知识分享和交流
- **企业版**: 面向团队和企业的协作功能
- **生态集成**: 与第三方平台的深度集成

### 商业模式探索
- **增值服务**: 高级功能和个性化服务
- **数据服务**: 匿名化的行业数据洞察
- **平台合作**: 与教育机构和企业的合作

---

愿景: 让每个人都能成为自己人生的CEO，高效管理知识、技能和职业发展，实现个人价值的最大化。

使命: 通过技术手段，为个人提供全方位的数字管理工具，让学习和工作更加高效、智能和愉悦。

---

## 附录：用户画像（合并自 01-产品概述/用户画像.md）

# Alpha 个人学习与工作管理平台 - 用户画像

## 👥 目标用户群体

### 主要用户画像

#### 1. 技术学习者 (Tech Learner)
...（以下内容为原文全文，已合并保存）

## 👥 目标用户群体

### 主要用户画像

#### 1. 技术学习者 (Tech Learner)
**基本信息**
- **年龄**: 22-35岁
- **职业**: 在校学生、初级开发者、转行人员
- **教育背景**: 本科及以上学历
- **技术背景**: 计算机相关专业或自学编程

**核心需求**
- 系统化的技术学习路径
- 最新技术资讯获取
- 学习笔记和知识整理
- 技能提升和认证

**使用场景**
- 日常技术学习
- 项目实践和总结
- 技术博客写作
- 求职准备

**痛点问题**
- 学习资料分散，难以系统管理
- 技术更新快，跟不上最新趋势
- 缺乏实践机会和反馈
- 学习进度难以跟踪

#### 2. 职场求职者 (Job Seeker)
**基本信息**
- **年龄**: 25-40岁
- **职业**: 在职员工、待业人员、跳槽者
- **工作经验**: 1-10年
- **求职目标**: 更好的工作机会或职业发展

**核心需求**
- 专业的简历设计和维护
- 求职流程管理
- 面试准备和记录
- 职业发展规划

**使用场景**
- 简历制作和优化
- 求职申请跟踪
- 面试准备和复盘
- 职业能力评估

**痛点问题**
- 简历制作困难，缺乏专业指导
- 求职信息管理混乱
- 面试经验难以积累
- 职业发展方向不明确

#### 3. 英语学习者 (English Learner)
**基本信息**
- **年龄**: 18-45岁
- **职业**: 学生、职场人士、自由职业者
- **英语水平**: 初级到中级
- **学习目标**: 提升英语能力，支持工作或学习

**核心需求**
- 系统化的英语学习计划
- 丰富的学习资源
- 发音和口语练习
- 学习进度跟踪

**使用场景**
- 日常英语学习
- 考试准备
- 工作英语提升
- 出国准备

**痛点问题**
- 学习资源质量参差不齐
- 缺乏系统化的学习计划
- 口语练习机会少
- 学习效果难以量化

#### 4. 知识工作者 (Knowledge Worker)
**基本信息**
- **年龄**: 28-45岁
- **职业**: 程序员、设计师、产品经理、研究人员
- **工作性质**: 需要持续学习和知识管理
- **工作环境**: 远程办公或混合办公

**核心需求**
- 高效的知识管理系统
- 智能的任务管理工具
- 团队协作和沟通
- 个人能力提升

**使用场景**
- 项目管理和跟踪
- 知识积累和分享
- 时间规划和优化
- 技能提升和认证

**痛点问题**
- 信息过载，难以筛选
- 任务管理效率低
- 知识难以有效利用
- 工作生活平衡困难

## 🎯 用户行为特征（节选）
- 设备偏好：主要PC，移动端补充；使用频率每周3-5次；注重隐私与效率

（完整“用户画像”内容已合并保存，详见上文原文段落）
