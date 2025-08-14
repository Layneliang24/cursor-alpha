# 测试目录说明

## 📁 目录结构

```
tests/
├── unit/           # 单元测试
│   ├── test_api.py
│   ├── test_articles.py
│   ├── test_categories.py
│   ├── test_jobs.py
│   ├── test_todos.py
│   └── test_users.py
├── integration/    # 集成测试
├── e2e/           # 端到端测试
├── fixtures/      # 测试数据
│   └── english_seed.json
├── pytest.ini    # pytest配置
└── README.md     # 本文件
```

## 🧪 运行测试

### 运行所有测试
```bash
cd tests
pytest
```

### 运行特定类型测试
```bash
# 单元测试
pytest unit/

# 集成测试
pytest integration/

# 端到端测试
pytest e2e/
```

### 运行特定测试文件
```bash
pytest unit/test_api.py
```

### 生成覆盖率报告
```bash
pytest --cov=backend --cov-report=html
```

## 📝 测试规范

### 单元测试
- 测试单个函数或方法
- 使用 mock 隔离外部依赖
- 测试边界条件和异常情况

### 集成测试
- 测试模块间的交互
- 使用测试数据库
- 测试API端点的完整流程

### 端到端测试
- 测试完整的用户流程
- 使用真实的浏览器环境
- 测试前端和后端的集成

## 🔧 测试数据

测试数据存放在 `fixtures/` 目录下：
- `english_seed.json`: 英语学习模块的种子数据

## 📊 测试覆盖率

目标覆盖率：> 80%

查看覆盖率报告：
```bash
pytest --cov=backend --cov-report=html
open htmlcov/index.html
```
