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

---

## 🆕 新功能上线测试流程（合并自 NEW_FEATURE_TESTING.md）

### 阶段与检查项（节选）
- 新功能专项：单元/集成/前端测试均通过，覆盖率≥90%
- 回归测试：既有回归用例100%通过；性能指标不降低
- 端到端：核心业务流程可用，用户场景验证通过

### 一键执行脚本（示例）
```bash
python -m pytest tests/new_features/ -v --html=reports/html/new_feature_report.html
python -m pytest tests/regression/ -v --html=reports/html/regression_report.html
python -m pytest tests/integration/ -v --html=reports/html/integration_report.html
```

---

## 🐞 问题修复测试流程（合并自 BUG_FIX_TESTING.md）

### 阶段与检查项（节选）
- 重现→修复验证→边界验证→相关回归→全量验证→性能/体验回归
- 通过标准：问题不再出现；相关功能正常；测试全部通过；性能稳定

### 常用命令（示例）
```bash
python -m pytest tests/regression/ -k "问题关键词" -v
python -m pytest tests/regression/ -k "修复功能" -v
python -m pytest tests/ -v --html=reports/html/full_test_report.html
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

*最后更新：2025-01-17*

## 附录：测试体系设计与建设总结（合并自 TESTING_SYSTEM.md / TESTING_SYSTEM_SUMMARY.md / TEST_FILE_REORGANIZATION.md）

### 测试体系主干
- 目录规范（标准化）：
  - `tests/regression/`、`tests/new_features/`、`tests/unit/`、`tests/integration/`
  - `tests/resources/{fixtures,mocks}/`、`tests/reports/{html,json}/`、`tests/utils/`
- 覆盖目标与类型：与正文一致，强调“关键路径≥90%，总体≥80%”。
- 一键执行：支持完整/回归/模块化执行与 HTML/JSON 报告产出。

### MySQL 测试数据库（示例）
```python
# tests/test_settings_mysql.py（要点）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test_alpha_db',
        'USER': 'root',
        'PASSWORD': '***',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# 可选：禁用迁移以加速测试
# MIGRATION_MODULES = DisableMigrations()
```

### 一键测试运行器（要点）
- 按模块运行：`python -m pytest tests/regression/{module}/ -v --html=tests/reports/html/{module}_report.html`
- 回归套件：`python -m pytest tests/regression/ -v --html=tests/reports/html/regression_report.html`
- 完整套件：见正文“测试执行”。

### 测试资产与覆盖分析（摘要）
- 统计维度：按模块/页面/功能四级、类型（单元/集成/API/前端）与优先级（高/中/低）。
- 输出物：HTML/JSON 报告与趋势统计，纳入 CI/CD 审查门槛。

### 测试文件重组（已完成要点）
- 根因：历史测试分散、命名不规范、路径引用错误。
- 调整：
  - 单元与集成测试归位 `tests/unit/`、`tests/integration/`；
  - 路径修复（如相对 `backend/` 的导入路径）；
  - 新增 `run_news_tests.*` 脚本统一运行新闻相关测试；
  - 目录与命名统一后，合并一次性记录文档。

> 注：本附录用于沉淀“方法与过程”，日常以本文件为唯一真实来源（SSOT）维护测试规范。

---

## 附录：测试计划（合并自 05-开发计划/测试计划.md）

### 目标与范围
- 功能正确性、性能稳定性、安全合规性、兼容性与可用性；覆盖全站模块与关键技术面。

### 策略与门禁
- 左移测试、自动化优先、数据隔离；准入（OpenAPI/环境就绪）、准出（覆盖/性能/回滚）。

### 环境与数据
- 本地/测试/预发/生产环境分层；Seed/fixtures/Mock 数据。

### 测试类型
- 功能/接口/E2E/性能/安全/兼容/可访问性；P95<500ms；核心路径全覆盖。

### CI/CD 集成
- Lint/TypeCheck → 单测 → 覆盖率门禁 → 构建/集成/E2E → 安全/依赖扫描 → 可回滚部署。
