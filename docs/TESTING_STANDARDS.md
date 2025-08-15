# Alpha 项目测试规范

## 📋 目录
- [测试架构](#测试架构)
- [测试编写规范](#测试编写规范)
- [测试数据管理](#测试数据管理)
- [测试覆盖率要求](#测试覆盖率要求)
- [测试运行规范](#测试运行规范)

---

## 🏗️ 测试架构

### 测试金字塔
```
┌─────────────────────────────────────┐
│           E2E测试 (10%)              │  ← 用户流程测试
├─────────────────────────────────────┤
│        集成测试 (20%)                │  ← API和模块交互
├─────────────────────────────────────┤
│        单元测试 (70%)                │  ← 核心业务逻辑
└─────────────────────────────────────┘
```

### 目录结构
```
tests/
├── conftest.py              # 全局测试配置
├── factories/               # 测试数据工厂
│   ├── user_factory.py
│   ├── article_factory.py
│   └── category_factory.py
├── unit/                   # 单元测试
│   ├── test_models.py
│   ├── test_views.py
│   └── test_serializers.py
├── integration/            # 集成测试
│   ├── test_api.py
│   └── test_auth.py
├── e2e/                   # 端到端测试
│   └── test_user_flows.py
└── utils/                 # 测试工具
    ├── test_helpers.py
    └── mock_data.py
```

---

## 📝 测试编写规范

### 命名规范

#### 测试文件命名
- 单元测试: `test_<模块名>.py`
- 集成测试: `test_<功能>_integration.py`
- E2E测试: `test_<用户流程>_e2e.py`

#### 测试类命名
```python
class TestUserModel:          # 模型测试
class TestArticleAPI:         # API测试
class TestUserAuthentication: # 功能测试
```

#### 测试方法命名
```python
def test_create_user_success():           # 成功场景
def test_create_user_with_invalid_data(): # 失败场景
def test_user_login_with_valid_credentials(): # 具体功能
```

### 测试结构规范

#### 单元测试模板
```python
import pytest
from django.test import TestCase

@pytest.mark.django_db
class TestUserModel:
    """用户模型测试"""
    
    def test_create_user_success(self, user_factory):
        """测试成功创建用户"""
        # Arrange
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com'
        }
        
        # Act
        user = user_factory(**user_data)
        
        # Assert
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
    
    def test_user_str_representation(self, user_factory):
        """测试用户字符串表示"""
        user = user_factory(username='testuser')
        assert str(user) == 'testuser'
```

#### API测试模板
```python
import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestArticleAPI:
    """文章API测试"""
    
    def test_get_articles_list(self, api_client, article_factory):
        """测试获取文章列表"""
        # Arrange
        article_factory(status='published')
        article_factory(status='published')
        
        # Act
        url = reverse('api:articles-list')
        response = api_client.get(url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 2
```

### 测试数据规范

#### 使用工厂模式
```python
# 好的做法
def test_create_article(self, article_factory, user_factory):
    user = user_factory()
    article = article_factory(author=user)
    assert article.author == user

# 避免的做法
def test_create_article(self):
    user = User.objects.create(username='test', email='test@example.com')
    article = Article.objects.create(title='Test', author=user)
    assert article.author == user
```

#### 测试数据隔离
```python
@pytest.mark.django_db
class TestUserModel:
    def test_user_creation(self, user_factory):
        # 每个测试方法都有独立的数据
        user1 = user_factory()
        user2 = user_factory()
        assert user1.id != user2.id
```

---

## 🗄️ 测试数据管理

### 测试数据工厂

#### 用户工厂
```python
# tests/factories/user_factory.py
import factory
from django.contrib.auth import get_user_model

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
```

#### 文章工厂
```python
# tests/factories/article_factory.py
import factory
from apps.articles.models import Article

class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Article
    
    title = factory.Faker('sentence')
    content = factory.Faker('text', max_nb_chars=1000)
    summary = factory.Faker('text', max_nb_chars=200)
    author = factory.SubFactory('tests.factories.user_factory.UserFactory')
    category = factory.SubFactory('tests.factories.category_factory.CategoryFactory')
    status = 'published'
```

### 测试数据清理

#### 自动清理
```python
@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """自动启用数据库访问"""
    pass

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """自动清理测试数据"""
    yield
    # 测试后清理
    User.objects.all().delete()
    Article.objects.all().delete()
```

---

## 📊 测试覆盖率要求

### 覆盖率目标
- **总体覆盖率**: > 80%
- **核心业务逻辑**: > 90%
- **API接口**: > 85%
- **模型层**: > 95%

### 覆盖率检查
```bash
# 运行覆盖率测试
pytest --cov=apps --cov-report=html --cov-report=term-missing

# 检查覆盖率是否达标
pytest --cov=apps --cov-fail-under=80
```

### 覆盖率报告解读
```bash
# 生成详细报告
pytest --cov=apps --cov-report=html --cov-report=term-missing

# 查看报告
open htmlcov/index.html
```

---

## 🚀 测试运行规范

### 测试命令

#### 开发阶段
```bash
# 快速测试（只运行失败的测试）
pytest --lf

# 运行特定测试
pytest tests/unit/test_models.py::TestUserModel::test_create_user

# 运行标记的测试
pytest -m "unit"
pytest -m "integration"
pytest -m "slow"
```

#### CI/CD阶段
```bash
# 完整测试套件
pytest --cov=apps --cov-report=xml --cov-report=html

# 并行测试
pytest -n auto

# 生成测试报告
pytest --junitxml=test-results.xml
```

### 测试标记

#### 测试类型标记
```python
@pytest.mark.unit
def test_user_model():
    pass

@pytest.mark.integration
def test_api_integration():
    pass

@pytest.mark.e2e
def test_user_flow():
    pass
```

#### 性能标记
```python
@pytest.mark.slow
def test_performance():
    pass

@pytest.mark.fast
def test_quick():
    pass
```

### 测试环境配置

#### 测试设置
```python
# tests/conftest.py
import pytest
from django.conf import settings

@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """配置测试数据库"""
    with django_db_blocker.unblock():
        # 测试数据库配置
        settings.DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
```

#### 环境变量
```bash
# 测试环境变量
export DJANGO_SETTINGS_MODULE=alpha.test_settings
export TESTING=True
export COVERAGE=True
```

---

## 🔧 测试工具配置

### pytest配置
```ini
# tests/pytest.ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = alpha.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --verbose
    --tb=short
    --cov=apps
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
```

### 前端测试配置
```javascript
// frontend/vitest.config.js
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    }
  }
})
```

---

## 📋 测试检查清单

### 编写测试前
- [ ] 理解业务需求
- [ ] 确定测试边界
- [ ] 设计测试数据
- [ ] 选择测试类型

### 编写测试时
- [ ] 遵循命名规范
- [ ] 使用工厂模式
- [ ] 包含边界条件
- [ ] 测试异常情况

### 测试完成后
- [ ] 检查覆盖率
- [ ] 验证测试独立性
- [ ] 确保测试可重复
- [ ] 更新测试文档

---

## 🚨 常见问题

### 测试数据冲突
```python
# 问题：测试间数据相互影响
# 解决：使用事务回滚
@pytest.mark.django_db(transaction=True)
def test_with_transaction():
    # 测试结束后自动回滚
    pass
```

### 测试性能问题
```python
# 问题：测试运行缓慢
# 解决：使用数据库复用
pytest --reuse-db
```

### 测试环境问题
```python
# 问题：测试环境配置错误
# 解决：使用独立的测试设置
# settings/test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
```

---

*最后更新：2024年12月*
