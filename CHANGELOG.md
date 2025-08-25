# 📋 Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- markdownlint-disable MD024 -->

## [Unreleased]

### 🚀 Features

- 建立统一测试入口与覆盖率阈值
- 配置 GitHub Actions CI/CD 流水线
- 接入静态检查与类型检查工具
- 落地 API 契约校验机制
- 搭建 E2E 测试基线（Playwright）
- 引入特性开关机制
- 建立 flaky 测试复跑与隔离机制
- 接入语义化发布与自动 CHANGELOG

### 🐛 Bug Fixes

- 修复 Django 初始化问题
- 解决 API 契约校验路径问题
- 修复特性开关 API 请求方法不匹配问题

### ⚡ Performance Improvements

- 优化测试执行速度
- 改进构建流程效率

### 📚 Documentation

- 添加完整的项目文档
- 创建 E2E 测试指南
- 编写特性开关使用文档
- 完善 flaky 测试处理文档
- 添加语义化发布指南

### 🔧 Chores

- 配置项目依赖管理
- 设置代码质量检查工具
- 建立 pre-commit 钩子
- 配置 husky 和 commitlint

---

## 版本说明

### 版本格式

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范：

- **MAJOR**：不兼容的 API 修改
- **MINOR**：向下兼容的功能性新增
- **PATCH**：向下兼容的问题修正

### 变更类型

- 🚀 **Features**：新功能
- 🐛 **Bug Fixes**：错误修复
- ⚡ **Performance Improvements**：性能优化
- ⏪ **Reverts**：回滚变更
- 📚 **Documentation**：文档变更
- 💄 **Styles**：代码格式变更
- ♻️ **Code Refactoring**：代码重构
- ✅ **Tests**：测试相关
- 🏗️ **Build System**：构建系统变更
- 👷 **CI/CD**：持续集成变更
- 🔧 **Chores**：其他杂项变更

### 自动化发布

本项目使用 [semantic-release](https://semantic-release.gitbook.io/) 进行自动化版本管理：

1. 基于 [约定式提交](https://www.conventionalcommits.org/zh-hans/) 自动确定版本号
2. 自动生成 CHANGELOG
3. 自动创建 GitHub Release
4. 自动上传构建产物

### 提交规范

请使用以下格式提交代码：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

示例：
```
feat(auth): add OAuth2 login support

Implement OAuth2 authentication flow with Google and GitHub providers.
Includes user profile synchronization and token refresh mechanism.

Closes #123
```

使用 `make commit` 命令可以获得交互式提交信息创建体验。