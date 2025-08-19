# 开发者指南

## 📋 目录
- [开发环境](#开发环境)
- [项目结构](#项目结构)
- [开发规范](#开发规范)
- [测试指南](#测试指南)
- [部署流程](#部署流程)

---

## 🛠️ 开发环境

### 环境要求
- **Python**: 3.9+
- **Node.js**: 18+
- **MySQL**: 8.0+
- **Redis**: 6.0+
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### 环境搭建

#### 1. 克隆项目
```bash
git clone <repository-url>
cd cursor-alpha
```

#### 2. 启动数据库服务
```bash
# 使用Docker启动MySQL和Redis
docker-compose up -d mysql redis

# 或分别启动
docker-compose up -d mysql
docker-compose up -d redis
```

#### 3. 安装后端依赖
```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 4. 安装前端依赖
```bash
cd frontend
npm install
```

#### 5. 数据库迁移
```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

#### 6. 启动开发服务器
```bash
# 方式1：一键启动（推荐）
./start-simple.bat

# 方式2：分别启动
# 后端
cd backend
python manage.py runserver

# 前端
cd frontend
npm run dev
```

---

## 🏗️ 项目结构

### 后端结构
```
backend/
├── alpha/                     # Django项目配置
│   ├── settings.py           # 主配置文件
│   ├── urls.py               # 主URL配置
│   └── wsgi.py               # WSGI配置
├── apps/                      # 应用模块
│   ├── api/                  # API接口层
│   │   ├── views.py         # API视图
│   │   ├── serializers.py   # 数据序列化
│   │   ├── urls.py          # API路由
│   │   └── permissions.py   # 权限控制
│   ├── articles/             # 文章管理
│   │   ├── models.py        # 文章模型
│   │   ├── views.py         # 文章视图
│   │   └── admin.py         # 管理后台
│   ├── english/              # 英语学习
│   │   ├── models.py        # 英语学习模型
│   │   ├── views.py         # 英语学习视图
│   │   ├── services.py      # 业务逻辑
│   │   └── tasks.py         # 异步任务
│   ├── users/                # 用户管理
│   │   ├── models.py        # 用户模型
│   │   └── views.py         # 用户视图
│   └── categories/           # 分类管理
│       ├── models.py        # 分类模型
│       └── views.py         # 分类视图
├── tests/                    # 测试文件
│   ├── unit/                # 单元测试
│   ├── integration/         # 集成测试
│   ├── regression/          # 回归测试
│   └── reports/             # 测试报告
├── manage.py                 # Django管理脚本
└── requirements.txt          # Python依赖
```

### 前端结构
```
frontend/
├── src/
│   ├── components/           # 通用组件
│   │   ├── NavBar.vue       # 导航栏
│   │   ├── SideMenu.vue     # 侧边菜单
│   │   └── charts/          # 图表组件
│   ├── views/               # 页面组件
│   │   ├── Home.vue         # 首页
│   │   ├── english/         # 英语学习页面
│   │   ├── articles/        # 文章管理页面
│   │   └── user/            # 用户页面
│   ├── stores/              # 状态管理
│   │   ├── auth.js          # 认证状态
│   │   ├── english.js       # 英语学习状态
│   │   └── articles.js      # 文章状态
│   ├── api/                 # API调用
│   │   ├── request.js       # 请求封装
│   │   ├── auth.js          # 认证API
│   │   └── english.js       # 英语学习API
│   ├── router/              # 路由配置
│   │   └── index.js         # 路由定义
│   ├── utils/               # 工具函数
│   └── main.js              # 应用入口
├── public/                  # 静态资源
│   ├── dicts/              # 词典文件
│   └── sounds/             # 音频文件
├── package.json             # 依赖配置
└── vite.config.js           # Vite配置
```

---

## 📝 开发规范

### 代码规范

#### Python代码规范
- 遵循 **PEP 8** 规范
- 使用 **Black** 进行代码格式化
- 函数和类必须有 **docstring**
- 变量和函数使用 **snake_case** 命名

```python
def get_user_articles(user_id: int, limit: int = 10) -> List[Article]:
    """
    获取用户文章列表
    
    Args:
        user_id: 用户ID
        limit: 返回数量限制
        
    Returns:
        文章列表
    """
    return Article.objects.filter(author_id=user_id)[:limit]
```

#### JavaScript/Vue代码规范
- 使用 **ESLint + Prettier** 进行代码检查
- 遵循 **Vue 3 Composition API** 规范
- 组件名使用 **PascalCase**
- 变量和函数使用 **camelCase**

```javascript
// 组件命名
export default {
  name: 'UserProfile',
  setup() {
    const user = ref(null)
    const loading = ref(false)
    
    const fetchUser = async () => {
      loading.value = true
      try {
        user.value = await userApi.getProfile()
      } finally {
        loading.value = false
      }
    }
    
    return {
      user,
      loading,
      fetchUser
    }
  }
}
```

### 提交规范

#### Git提交信息格式
```bash
# 格式：type(scope): description
feat(english): 添加打字练习功能
fix(api): 修复用户认证bug
docs(readme): 更新项目说明
style(ui): 优化按钮样式
refactor(auth): 重构认证逻辑
test(english): 添加英语学习测试
chore(deps): 更新依赖版本
```

#### 分支管理
- `main`: 主分支，稳定版本
- `develop`: 开发分支
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复分支
- `release/*`: 发布分支

```bash
# 创建功能分支
git checkout -b feature/typing-practice

# 开发完成后合并
git checkout develop
git merge feature/typing-practice
git branch -d feature/typing-practice
```

### 数据库规范

#### 模型设计
- 使用 **Django ORM** 进行数据库操作
- 模型名使用 **PascalCase**
- 字段名使用 **snake_case**
- 必须包含 **created_at** 和 **updated_at** 字段

```python
class Article(models.Model):
    """文章模型"""
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-created_at']
```

---

## 🧪 测试指南

### 测试结构

#### 测试目录组织
```
tests/
├── unit/                    # 单元测试
│   ├── test_models.py      # 模型测试
│   ├── test_views.py       # 视图测试
│   └── test_services.py    # 服务测试
├── integration/             # 集成测试
│   ├── test_api.py         # API集成测试
│   └── test_database.py    # 数据库集成测试
├── regression/              # 回归测试
│   ├── english/            # 英语学习回归测试
│   └── auth/               # 认证回归测试
├── new_features/            # 新功能测试
├── resources/               # 测试资源
│   ├── fixtures/           # 测试数据
│   └── mocks/              # 模拟数据
├── reports/                 # 测试报告
│   ├── html/               # HTML报告
│   └── json/               # JSON报告
├── run_tests.py            # 一键测试脚本
├── pytest.ini             # pytest配置
└── conftest.py            # pytest配置
```

### 测试运行

#### 运行所有测试
```bash
# 使用测试脚本
python tests/run_tests.py --mode=full

# 使用pytest
cd tests
pytest

# 生成覆盖率报告
pytest --cov=backend --cov-report=html
```

#### 运行特定测试
```bash
# 运行特定模块
python tests/run_tests.py --module=english

# 运行特定测试文件
pytest tests/unit/test_models.py

# 运行特定测试方法
pytest tests/unit/test_models.py::TestArticleModel::test_article_creation
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

---

## 🚀 部署流程

### 开发环境部署

#### 本地开发
```bash
# 1. 启动数据库
docker-compose up -d mysql redis

# 2. 启动后端
cd backend
python manage.py runserver

# 3. 启动前端
cd frontend
npm run dev
```

#### 测试环境部署
```bash
# 1. 构建测试镜像
docker-compose -f docker-compose.test.yml build

# 2. 启动测试服务
docker-compose -f docker-compose.test.yml up -d

# 3. 运行测试
docker-compose -f docker-compose.test.yml exec backend python tests/run_tests.py
```

### 生产环境部署

#### Docker部署
```bash
# 1. 构建生产镜像
docker-compose -f docker-compose.prod.yml build

# 2. 启动生产服务
docker-compose -f docker-compose.prod.yml up -d

# 3. 数据库迁移
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 4. 收集静态文件
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic
```

#### Kubernetes部署
```bash
# 1. 应用配置
kubectl apply -f k8s/

# 2. 检查状态
kubectl get pods
kubectl get services

# 3. 查看日志
kubectl logs -f deployment/alpha-backend
```

---

---

## 附录：开发计划与技术实现（合并自 05-开发计划/开发阶段.md、技术实现.md）

### 开发阶段（节选）
- 第一阶段：基础架构与认证权限、CI/CD、监控与日志
- 第二阶段：博客/英语/待办模块与爬虫系统
- 第三阶段：求职管理、AI助手、性能优化
- 第四阶段：完善与优化、测试与培训、上线准备

### 技术实现要点（节选）
- 后端分层：表现层/应用层/领域层/基础设施/数据层；Celery 队列；统一响应与异常
- 前端结构：API 封装、路由守卫、Pinia 状态、主题与断点、错误处理
- DevOps：多阶段镜像、Compose 部署、反向代理、日志与监控、门禁流水线

## 🔧 开发工具

### 推荐工具

#### 代码编辑器
- **VS Code**: 轻量级，插件丰富
- **PyCharm**: Python开发专业IDE
- **WebStorm**: JavaScript/前端开发

#### 数据库工具
- **MySQL Workbench**: MySQL管理
- **Redis Desktop Manager**: Redis管理
- **DBeaver**: 通用数据库工具

#### API测试
- **Postman**: API接口测试
- **Insomnia**: 轻量级API客户端
- **curl**: 命令行API测试

### 开发插件

#### VS Code插件
- Python
- Vue Language Features
- ESLint
- Prettier
- GitLens
- Docker

#### PyCharm插件
- Django
- Vue.js
- Docker
- Git Integration

---

## 📚 学习资源

### 官方文档
- [Django官方文档](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue.js官方文档](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)

### 最佳实践
- [Django最佳实践](https://docs.djangoproject.com/en/stable/misc/)
- [Vue.js风格指南](https://vuejs.org/style-guide/)
- [REST API设计原则](https://restfulapi.net/)

---

## 📞 支持

### 开发支持
- 查看 [API文档](../API.md) 了解接口规范
- 参考 [模块文档](../modules/) 理解功能实现
- 查看 [常见问题](../FAQ.md) 解决开发问题

### 团队协作
- 使用Git进行版本控制
- 遵循代码审查流程
- 及时更新文档和注释

---

---

*最后更新：2025-01-17*
*更新内容：整合现有开发文档，创建完整的开发者指南*
