# 测试规范文档

## 📋 概述

本文档规定了Alpha项目的测试规范和标准，确保代码质量和功能可靠性。

## 🎯 测试目标

- **覆盖率目标**：> 80%
- **测试类型**：单元测试、集成测试、端到端测试
- **自动化程度**：100%自动化
- **执行频率**：每次代码提交、每次功能开发

## 📁 测试结构

```
tests/
├── unit/                    # 单元测试
│   ├── test_basic.py       # 基础功能测试
│   ├── test_models.py      # 模型测试
│   ├── test_mysql_connection.py  # 数据库连接测试
│   └── test_simple.py      # 简化测试
├── integration/            # 集成测试
│   └── test_api.py         # API集成测试
├── e2e/                    # 端到端测试（待开发）
├── factories/              # 测试数据工厂
│   ├── user_factory.py
│   ├── article_factory.py
│   └── category_factory.py
├── fixtures/               # 测试数据
│   └── english_seed.json
├── conftest.py            # pytest配置
├── pytest.ini            # pytest设置
└── README.md             # 测试说明
```

## 🧪 测试类型

### 1. 单元测试 (Unit Tests)
- **位置**：`tests/unit/`
- **范围**：单个函数、方法、类
- **特点**：快速、独立、可重复
- **工具**：pytest + Django TestCase

**示例**：
```python
def test_user_creation(self):
    """测试用户创建"""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    self.assertEqual(user.username, 'testuser')
    self.assertEqual(user.email, 'test@example.com')
```

### 2. 集成测试 (Integration Tests)
- **位置**：`tests/integration/`
- **范围**：模块间交互、API端点
- **特点**：测试组件协作
- **工具**：pytest + DRF APIClient

**示例**：
```python
def test_article_api(self):
    """测试文章API"""
    url = reverse('article-list')
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
```

### 3. 端到端测试 (E2E Tests)
- **位置**：`tests/e2e/`
- **范围**：完整用户流程
- **特点**：真实浏览器环境
- **工具**：Selenium/Playwright（待实现）

## 🔧 测试工具

### 核心工具
- **pytest**: 测试框架
- **pytest-django**: Django集成
- **pytest-cov**: 覆盖率报告
- **factory-boy**: 测试数据生成

### 配置
```ini
# pytest.ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = alpha.settings
python_files = tests.py test_*.py *_tests.py
addopts = 
    --strict-markers
    --verbose
    --cov=apps
    --cov-report=html
    --cov-fail-under=80
```

## 📝 测试编写规范

### 1. 命名规范
- **文件命名**：`test_*.py`
- **类命名**：`Test*` 或 `*Test`
- **方法命名**：`test_*`
- **描述性命名**：清晰表达测试目的

### 2. 测试结构
```python
class TestFeature(TestCase):
    """功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        pass
    
    def test_specific_functionality(self):
        """测试特定功能"""
        # Arrange: 准备数据
        # Act: 执行操作
        # Assert: 验证结果
        pass
    
    def tearDown(self):
        """测试后清理"""
        pass
```

### 3. 断言使用
- 使用明确的断言
- 提供有意义的错误信息
- 测试边界条件

```python
# 好的断言
self.assertEqual(result, expected, "结果不匹配")
self.assertIn(item, collection, "项目不在集合中")

# 避免的断言
assert result == expected  # 错误信息不明确
```

### 4. 测试数据管理
- 使用工厂模式创建测试数据
- 避免硬编码测试数据
- 清理测试数据

```python
# 使用工厂
user = user_factory(username='testuser')

# 避免硬编码
user = User.objects.create_user(username='testuser', ...)
```

## 🚀 测试执行

### 运行命令
```bash
# 运行所有测试
python -m pytest ../tests/ -v

# 运行特定类型测试
python -m pytest ../tests/unit/ -v
python -m pytest ../tests/integration/ -v

# 运行标记测试
python -m pytest ../tests/ -m fast
python -m pytest ../tests/ -m slow

# 生成覆盖率报告
python -m pytest ../tests/ --cov=apps --cov-report=html
```

### 自动化脚本
```bash
# 完整测试（包含pytest）
# Windows
run_tests.bat

# PowerShell
.\run_tests.ps1

# 简化测试（避免Django设置问题）
# Windows
run_simple_tests.bat

# PowerShell
.\run_simple_tests.ps1

# 直接运行Django环境测试
python test_django_setup.py
```

### 测试类型说明
1. **简化测试**：`run_simple_tests.bat/.ps1`
   - 避免复杂的pytest配置问题
   - 验证Python环境和Django设置
   - 检查项目结构完整性
   - 适合快速验证环境

2. **完整测试**：`run_tests.bat/.ps1`
   - 使用pytest框架
   - 包含单元测试、集成测试
   - 生成覆盖率报告
   - 适合正式测试流程

3. **Django环境测试**：`test_django_setup.py`
   - 独立验证Django配置
   - 检查数据库连接
   - 验证模型导入
   - 适合环境诊断

## 📊 覆盖率要求

### 覆盖率目标
- **总体覆盖率**：> 80%
- **核心模块**：> 90%
- **新增功能**：100%

### 覆盖率报告
- HTML报告：`htmlcov/index.html`
- 命令行报告：显示未覆盖代码行
- CI/CD集成：自动检查覆盖率

## 🔄 测试流程

### 开发流程
1. **编写代码** → 2. **编写测试** → 3. **运行测试** → 4. **提交代码**

### 测试检查清单
- [ ] 新功能有对应测试
- [ ] 测试覆盖边界条件
- [ ] 测试通过率100%
- [ ] 覆盖率达标
- [ ] 测试文档更新

## ⚠️ 注意事项

### 禁止行为
- ❌ 跳过测试
- ❌ 硬编码测试数据
- ❌ 测试间相互依赖
- ❌ 不清理测试数据

### 推荐行为
- ✅ 每个功能都有测试
- ✅ 使用工厂创建测试数据
- ✅ 测试独立且可重复
- ✅ 及时更新测试文档

## 📈 持续改进

### 定期评估
- 每周检查测试覆盖率
- 每月评估测试质量
- 每季度优化测试策略

### 改进方向
- 增加端到端测试
- 优化测试执行速度
- 完善测试文档
- 集成CI/CD流程

---

*最后更新：2024年12月*
