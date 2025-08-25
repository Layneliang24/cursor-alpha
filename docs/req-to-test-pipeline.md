# 需求→测试→实现自动化流水线

## 概述

需求→测试→实现自动化流水线是一个强大的开发工具，它可以根据需求文档自动生成测试模板、代码框架、GitHub Issue和Git分支，大大提高开发效率和代码质量。

## 功能特性

### 🔍 智能需求解析
- 支持多种格式：Markdown、YAML、JSON、纯文本
- 自动提取需求信息：标题、类型、优先级、组件、验收标准等
- 灵活的文本解析，支持中英文混合

### 🧪 自动测试生成
- **单元测试**：Django后端测试、Vue前端测试
- **集成测试**：API集成测试、数据库测试
- **E2E测试**：Playwright端到端测试
- 基于验收标准自动生成测试用例

### 💻 代码框架生成
- **后端代码**：Django模型、视图、序列化器
- **前端代码**：Vue组件、服务层、API调用
- 遵循项目代码规范和最佳实践

### 🔄 Git工作流集成
- 自动创建功能分支
- 规范化提交信息
- 推送到远程仓库

### 📝 工单管理
- 生成GitHub Issue模板
- 包含完整的任务清单
- 自动设置标签和负责人

## 使用方法

### 基本命令

```bash
# 从需求文件运行完整流水线
make req-pipeline REQ=path/to/requirement.md

# 预览模式（不创建实际文件）
make req-pipeline-dry REQ=path/to/requirement.md

# 从文本运行流水线
make req-pipeline-text TEXT="标题: 用户认证\n类型: feature\n描述: 实现用户登录功能"

# 运行示例需求
make req-example

# 查看需求模板
make req-template
```

## AI增强流水线

### 基本用法

```bash
# 使用AI增强流水线（默认使用所有AI任务）
make req-pipeline-ai INPUT=scripts/templates/example_requirement.md

# 指定AI提供商
make req-pipeline-ai INPUT=scripts/templates/example_requirement.md AI_PROVIDER=openai

# 只生成测试代码
make req-pipeline-ai INPUT=scripts/templates/example_requirement.md AI_TASKS=generate_tests

# 从文本输入运行
make req-pipeline-ai-text TEXT="实现用户登录功能" AI_PROVIDER=claude
```

### 文件集成策略

AI增强流水线会将生成的文件直接集成到项目现有的目录结构中：

**测试文件位置：**
- 后端单元测试：`backend/tests/test_{requirement_id}.py`
- 后端集成测试：`backend/tests/integration/test_{requirement_id}_api.py`
- 前端单元测试：`frontend/tests/unit/{requirement_id}.test.js`
- E2E测试：`e2e/tests/{requirement_id}.spec.js`
- 通用单元测试：`tests/unit/test_{requirement_id}.py`

**代码文件位置：**
- 后端应用：`backend/apps/{requirement_id}/`
  - `models.py` - 数据模型
  - `views.py` - 视图逻辑
  - `serializers.py` - 序列化器
  - `urls.py` - URL路由
  - `apps.py` - 应用配置
  - `__init__.py` - 包初始化
- 前端组件：`frontend/src/components/{RequirementId}Component.vue`
- 前端服务：`frontend/src/services/{requirement_id}Service.js`

**文档位置：**
- 代码审查报告：`docs/code_reviews/{requirement_id}_review.md`

这种集成策略确保AI生成的代码能够直接融入现有项目结构，便于后续开发和维护。

### 高级用法

```bash
# 使用Python脚本直接调用
python scripts/req_to_test_pipeline.py --input requirements/user_auth.md

# 只生成测试，不创建分支
python scripts/req_to_test_pipeline.py --input requirements/user_auth.md --no-branch --no-commit

# 从YAML文件解析需求
python scripts/req_to_test_pipeline.py --input requirements/feature.yml

# 输出详细报告
python scripts/req_to_test_pipeline.py --input requirements/feature.md --output report.md
```

## 需求文档格式

### Markdown格式（推荐）

```markdown
# 需求标题

## 基本信息

**标题**: 用户认证系统
**类型**: feature
**优先级**: high
**组件**: backend, frontend, api
**负责人**: developer
**预估工时**: 16

## 需求描述

详细的需求说明...

## 验收标准

- 用户可以成功注册账户
- 用户可以使用正确凭据登录
- 系统会验证密码强度

## 依赖关系

- #123 (用户模型设计)
- #124 (邮件服务配置)
```

### YAML格式

```yaml
id: user_auth
title: 用户认证系统
type: feature
priority: high
components:
  - backend
  - frontend
  - api
description: |
  实现完整的用户认证系统，包括注册、登录、登出功能。
acceptance_criteria:
  - 用户可以成功注册账户
  - 用户可以使用正确凭据登录
  - 系统会验证密码强度
dependencies:
  - "123"
  - "124"
estimated_hours: 16
assignee: developer
```

### JSON格式

```json
{
  "id": "user_auth",
  "title": "用户认证系统",
  "type": "feature",
  "priority": "high",
  "components": ["backend", "frontend", "api"],
  "description": "实现完整的用户认证系统",
  "acceptance_criteria": [
    "用户可以成功注册账户",
    "用户可以使用正确凭据登录"
  ],
  "dependencies": ["123", "124"],
  "estimated_hours": 16,
  "assignee": "developer"
}
```

## 生成的文件结构

### 测试文件

```
backend/tests/
├── test_{req_id}.py              # Django单元测试
└── integration/
    └── test_{req_id}_api.py       # API集成测试

frontend/tests/unit/
└── {req_id}.test.js               # Vue单元测试

tests/e2e/
└── {req_id}.spec.js               # Playwright E2E测试
```

### 代码文件

```
backend/apps/{req_id}/
├── models.py                      # Django模型
├── views.py                       # Django视图
└── serializers.py                 # DRF序列化器

frontend/src/
├── components/
│   └── {ComponentName}Component.vue  # Vue组件
└── services/
    └── {req_id}Service.js         # API服务
```

### 工单文件

```
.github/ISSUE_TEMPLATE/
└── {req_id}_template.md           # GitHub Issue模板

issues/
└── {req_id}.json                  # Issue JSON数据
```

## 配置选项

### 需求类型

- `feature`: 新功能开发
- `bugfix`: Bug修复
- `enhancement`: 功能增强
- `refactor`: 代码重构

### 优先级

- `high`: 高优先级
- `medium`: 中优先级
- `low`: 低优先级

### 组件类型

- `backend`: 后端Django应用
- `frontend`: 前端Vue应用
- `api`: API接口
- `database`: 数据库相关
- `ui`: 用户界面

## 工作流集成

### Git分支命名规范

```
{type}/{req_id}-{title-kebab-case}

示例：
feature/user-auth-implement-user-authentication-system
bugfix/login-fix-password-validation-issue
```

### 提交信息规范

```
feat({req_id}): add test templates and code scaffolding for {title}

示例：
feat(user-auth): add test templates and code scaffolding for User Authentication System
```

### GitHub Actions集成

流水线会自动触发CI/CD流程：

1. 代码质量检查（ESLint、Flake8、MyPy）
2. 单元测试和覆盖率检查
3. 集成测试
4. E2E测试
5. 构建和部署

## 最佳实践

### 1. 需求文档编写

- **明确具体**：避免模糊的描述，使用具体的动词和名词
- **验收标准**：每个标准都应该是可测试和可验证的
- **组件划分**：准确标识涉及的技术组件
- **依赖关系**：明确列出前置条件和相关需求

### 2. 流水线使用

- **预览模式**：首次使用时建议先运行预览模式
- **增量开发**：将大需求拆分为多个小需求
- **代码审查**：生成的代码仅为框架，需要完善实现逻辑
- **测试驱动**：先完善测试用例，再实现功能代码

### 3. 团队协作

- **统一模板**：团队使用统一的需求文档模板
- **代码规范**：遵循生成代码的风格和结构
- **分支管理**：及时合并完成的功能分支
- **文档更新**：及时更新API文档和用户文档

## 故障排除

### 常见问题

#### 1. 需求解析失败

**问题**：无法正确解析需求文档

**解决方案**：
- 检查文档格式是否正确
- 确保必填字段都已提供
- 使用预览模式检查解析结果

#### 2. Git操作失败

**问题**：无法创建分支或提交代码

**解决方案**：
- 确保Git仓库状态干净
- 检查是否有未提交的变更
- 确保有足够的权限

#### 3. 文件创建失败

**问题**：无法创建测试或代码文件

**解决方案**：
- 检查目录权限
- 确保目标目录存在
- 检查文件名是否合法

### 调试模式

```bash
# 启用详细日志
python scripts/req_to_test_pipeline.py --input requirement.md --verbose

# 只解析需求，不生成文件
python scripts/req_to_test_pipeline.py --input requirement.md --parse-only

# 生成调试报告
python scripts/req_to_test_pipeline.py --input requirement.md --debug --output debug.log
```

## 扩展功能

### 自定义模板

可以在 `scripts/templates/` 目录下创建自定义模板：

```
scripts/templates/
├── requirement_template.md        # 需求文档模板
├── test_templates/
│   ├── django_test.py.template    # Django测试模板
│   ├── vue_test.js.template       # Vue测试模板
│   └── e2e_test.js.template       # E2E测试模板
└── code_templates/
    ├── django_model.py.template   # Django模型模板
    ├── django_view.py.template    # Django视图模板
    └── vue_component.vue.template # Vue组件模板
```

### 插件系统

可以通过插件扩展流水线功能：

```python
# 自定义解析器插件
class CustomRequirementParser(RequirementParser):
    def parse_custom_format(self, content):
        # 实现自定义解析逻辑
        pass

# 自定义生成器插件
class CustomCodeGenerator(CodeGenerator):
    def generate_custom_template(self, req):
        # 实现自定义代码生成
        pass
```

## 性能优化

### 并行处理

对于大型需求，可以启用并行处理：

```bash
python scripts/req_to_test_pipeline.py --input requirement.md --parallel
```

### 缓存机制

启用模板缓存以提高性能：

```bash
python scripts/req_to_test_pipeline.py --input requirement.md --cache
```

## 监控和指标

### 流水线指标

- 需求处理时间
- 生成文件数量
- 测试覆盖率
- 代码质量分数

### 监控命令

```bash
# 查看流水线统计
python scripts/req_to_test_pipeline.py --stats

# 生成性能报告
python scripts/req_to_test_pipeline.py --performance-report
```

## 相关链接

- [需求模板示例](scripts/templates/requirement_template.md)
- [示例需求文档](scripts/templates/example_requirement.md)
- [测试框架文档](docs/testing.md)
- [代码规范文档](docs/coding-standards.md)
- [Git工作流文档](docs/git-workflow.md)

## 更新日志

### v1.0.0 (2024-01-15)

- ✨ 初始版本发布
- 🧪 支持自动测试生成
- 💻 支持代码框架生成
- 🔄 集成Git工作流
- 📝 支持GitHub Issue创建

### 计划功能

- [ ] 支持更多测试框架
- [ ] 集成AI代码生成
- [ ] 支持微服务架构
- [ ] 添加性能测试模板
- [ ] 集成代码审查工具