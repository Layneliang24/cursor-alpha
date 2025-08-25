# 📋 语义化发布与自动 CHANGELOG

本项目采用语义化发布（Semantic Release）和约定式提交（Conventional Commits）来自动化版本管理和 CHANGELOG 生成。

## 🎯 功能特性

### 自动化版本管理
- **自动版本号生成**：基于提交信息自动确定版本号（major.minor.patch）
- **自动标签创建**：自动创建 Git 标签并推送到远程仓库
- **自动发布说明**：生成详细的 GitHub Release 说明
- **自动 CHANGELOG**：维护项目的变更日志文件

### 约定式提交规范
- **标准化提交格式**：强制使用约定式提交格式
- **交互式提交工具**：提供友好的提交信息创建界面
- **提交信息验证**：自动验证提交信息格式
- **多分支支持**：支持 main、develop、release/* 分支策略

## 🚀 使用方法

### 基本命令

```bash
# 交互式创建提交信息
make commit
# 或者
npm run commit

# 重试上次提交（如果失败）
make commit-retry

# 检查下一个版本号（不实际发布）
make version-check

# 生成 CHANGELOG
make changelog

# 语义化发布预演（查看将要发布的内容）
make release-dry-run

# 执行语义化发布
make release
```

### 提交信息格式

约定式提交格式：`<type>[optional scope]: <description>`

#### 支持的类型（Type）

| 类型 | 描述 | 版本影响 | 示例 |
|------|------|----------|------|
| `feat` | 新功能 | minor | `feat: add user authentication` |
| `fix` | 错误修复 | patch | `fix(api): resolve login endpoint error` |
| `perf` | 性能优化 | patch | `perf: improve database query performance` |
| `refactor` | 代码重构 | patch | `refactor: extract user service logic` |
| `docs` | 文档更新 | 无 | `docs: update README with setup instructions` |
| `style` | 代码格式 | 无 | `style: fix code formatting` |
| `test` | 测试相关 | 无 | `test: add unit tests for user service` |
| `build` | 构建系统 | 无 | `build: update webpack configuration` |
| `ci` | CI/CD 配置 | 无 | `ci: add semantic release workflow` |
| `chore` | 其他杂项 | 无 | `chore: update dependencies` |
| `revert` | 回滚提交 | patch | `revert: revert previous commit` |

#### 作用域（Scope）

可选的作用域标识，用于指明变更的影响范围：

- `frontend` - 前端相关
- `backend` - 后端相关
- `api` - API 相关
- `auth` - 认证相关
- `database` - 数据库相关
- `ui` - 用户界面
- `config` - 配置相关
- `deps` - 依赖更新
- `security` - 安全相关
- `performance` - 性能相关
- `tests` - 测试相关
- `docs` - 文档相关
- `ci` - CI/CD 相关

#### 破坏性变更（Breaking Changes）

对于包含破坏性变更的提交，需要在提交信息中明确标识：

```bash
# 方式1：在类型后添加 !
feat!: remove deprecated API endpoints

# 方式2：在提交体中添加 BREAKING CHANGE
feat: update user authentication

BREAKING CHANGE: remove support for legacy token format
```

### 提交示例

```bash
# 新功能
feat(auth): add OAuth2 login support

# 错误修复
fix(api): resolve user registration validation

# 性能优化
perf(database): optimize user query with indexing

# 文档更新
docs: add API documentation for user endpoints

# 测试添加
test(frontend): add unit tests for login component

# 破坏性变更
feat(api)!: redesign user authentication API

BREAKING CHANGE: The authentication API has been completely redesigned.
Old token format is no longer supported.
```

## 🔧 配置说明

### 分支策略

- **main**: 生产环境分支，触发正式版本发布
- **develop**: 开发分支，触发 beta 预发布版本
- **release/***: 发布分支，触发 rc 候选版本

### 版本规则

- **major**: 包含破坏性变更时触发
- **minor**: 包含新功能时触发
- **patch**: 包含错误修复、性能优化、重构时触发

### 发布资产

自动发布时会包含以下资产：
- 前端构建产物（`frontend/dist/`）
- 后端静态文件（`backend/staticfiles/`）
- 变更日志（`CHANGELOG.md`）

## 🔄 CI/CD 集成

### GitHub Actions 工作流

语义化发布集成在 `.github/workflows/test.yml` 中：

1. **触发条件**：推送到 main 分支
2. **前置条件**：所有测试必须通过
3. **发布流程**：
   - 构建前端和后端
   - 生成 CHANGELOG
   - 创建版本标签
   - 发布 GitHub Release
   - 上传构建产物

### 环境变量

需要在 GitHub 仓库设置中配置以下 secrets：

- `GITHUB_TOKEN`：GitHub 访问令牌（自动提供）
- `NPM_TOKEN`：NPM 发布令牌（如果需要发布到 NPM）

## 📊 CHANGELOG 格式

自动生成的 CHANGELOG 包含以下部分：

```markdown
# 📋 Changelog

## [1.2.0](https://github.com/your-org/alpha/compare/v1.1.0...v1.2.0) (2024-01-15)

### 🚀 Features

* **auth**: add OAuth2 login support ([abc1234](https://github.com/your-org/alpha/commit/abc1234))
* **api**: implement user profile endpoints ([def5678](https://github.com/your-org/alpha/commit/def5678))

### 🐛 Bug Fixes

* **frontend**: resolve login form validation ([ghi9012](https://github.com/your-org/alpha/commit/ghi9012))

### ⚡ Performance Improvements

* **database**: optimize user query performance ([jkl3456](https://github.com/your-org/alpha/commit/jkl3456))
```

## 🛠️ 故障排除

### 常见问题

#### 1. 提交信息格式错误

**错误信息**：
```
❌ Invalid commit message format!
```

**解决方案**：
- 使用 `make commit` 进行交互式提交
- 检查提交信息是否符合约定式提交格式
- 确保类型、作用域、描述格式正确

#### 2. 语义化发布失败

**错误信息**：
```
SemanticReleaseError: No release published
```

**可能原因**：
- 没有符合发布条件的提交
- 分支不是 main 分支
- 测试未通过

**解决方案**：
- 确保有 `feat`、`fix`、`perf` 等类型的提交
- 检查是否在正确的分支上
- 确保所有测试通过

#### 3. CHANGELOG 生成失败

**解决方案**：
- 检查 Git 历史记录
- 确保有符合约定式提交格式的提交
- 手动运行 `make changelog` 查看详细错误

### 调试模式

```bash
# 启用调试模式查看详细信息
make release-debug

# 预演模式查看将要发布的内容
make release-dry-run

# 检查下一个版本号
make version-check
```

## 📈 最佳实践

### 提交频率
- 保持小而频繁的提交
- 每个提交只包含一个逻辑变更
- 避免混合不同类型的变更

### 提交信息
- 使用现在时、祈使语气（"add" 而不是 "added"）
- 保持描述简洁明了（50字符以内）
- 必要时在提交体中提供详细说明

### 分支管理
- 在 feature 分支上开发新功能
- 通过 PR 合并到 develop 分支
- 定期从 develop 创建 release 分支
- 从 release 分支合并到 main 触发发布

### 版本策略
- 遵循语义化版本规范
- 谨慎处理破坏性变更
- 在 CHANGELOG 中详细说明变更内容

## 🔗 相关链接

- [语义化版本规范](https://semver.org/lang/zh-CN/)
- [约定式提交规范](https://www.conventionalcommits.org/zh-hans/)
- [Semantic Release 文档](https://semantic-release.gitbook.io/semantic-release/)
- [Commitizen 文档](https://commitizen-tools.github.io/commitizen/)