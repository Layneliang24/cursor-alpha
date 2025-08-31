# CI/CD 自动化流水线文档

## 📋 概述

本项目使用GitHub Actions实现完整的CI/CD自动化流水线，包括代码检查、单元测试、端到端测试、跨浏览器测试和自动部署。

## 🚀 流水线结构

### 1. 构建和基础检查 (Build)
- **触发条件**: 所有push和PR
- **执行内容**:
  - 代码检出和环境设置
  - 前端和后端依赖安装
  - ESLint代码检查
  - TypeScript类型检查
  - 前端构建验证
  - Django项目检查

### 2. 单元测试 (Unit Tests)
- **触发条件**: 构建成功后
- **执行内容**:
  - 前端Vitest单元测试
  - 后端Django单元测试
  - 测试覆盖率报告生成
  - 测试结果上传到Artifacts

### 3. 端到端测试 (E2E Tests)
- **触发条件**: 构建成功后
- **执行内容**:
  - MySQL和Redis服务启动
  - 数据库迁移
  - 前后端服务启动
  - Playwright E2E测试执行
  - 测试报告和截图上传

### 4. 跨浏览器测试 (Cross Browser Tests)
- **触发条件**: 仅在main/master分支push时执行
- **执行内容**:
  - Chrome、Firefox、Edge多浏览器测试
  - Selenium自动化测试
  - 跨浏览器兼容性验证

### 5. 部署到预发布环境 (Deploy Staging)
- **触发条件**: 测试通过且在main/master分支
- **执行内容**:
  - 自动部署到预发布环境
  - 部署后健康检查

### 6. 结果通知 (Notify)
- **触发条件**: 所有任务完成后
- **执行内容**:
  - 测试结果汇总
  - Slack通知（可选）
  - 邮件通知（可选）

## 🔧 环境配置

### 必需的环境变量

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=alpha_db_test
DB_USER=root
DB_PASSWORD=meimei520

# Redis配置
REDIS_URL=redis://localhost:6379

# Django配置
SECRET_KEY=test-secret-key-for-ci
DEBUG=False
```

### GitHub Secrets配置

在GitHub仓库设置中添加以下Secrets：

```
SLACK_WEBHOOK_URL          # Slack通知webhook
STAGING_DEPLOY_KEY         # 预发布环境部署密钥
PRODUCTION_DEPLOY_KEY      # 生产环境部署密钥
```

## 📊 测试覆盖率

### 前端测试覆盖率目标
- **语句覆盖率**: ≥ 80%
- **分支覆盖率**: ≥ 70%
- **函数覆盖率**: ≥ 80%
- **行覆盖率**: ≥ 80%

### 后端测试覆盖率目标
- **语句覆盖率**: ≥ 85%
- **分支覆盖率**: ≥ 75%
- **函数覆盖率**: ≥ 85%

## 🎯 测试策略

### 单元测试
- **前端**: Vitest + Vue Test Utils
- **后端**: Django TestCase
- **Mock策略**: API调用、外部服务、数据库操作

### 集成测试
- **API测试**: 完整的请求-响应流程
- **数据库测试**: 模型关系和查询优化
- **认证测试**: JWT token管理和权限验证

### 端到端测试
- **用户流程**: 完整的用户操作路径
- **跨页面导航**: 路由和状态管理
- **表单提交**: 数据验证和错误处理

### 跨浏览器测试
- **兼容性验证**: Chrome、Firefox、Edge
- **响应式设计**: 不同屏幕尺寸
- **JavaScript兼容性**: ES6+特性支持

## 🚨 故障排除

### 常见问题

#### 1. 数据库连接失败
```bash
# 检查MySQL服务状态
mysql --version
mysql -h localhost -u root -p -e "SELECT 1"
```

#### 2. 前端构建失败
```bash
# 清理缓存重新安装
npm ci
npm run build
```

#### 3. E2E测试超时
```bash
# 增加等待时间
PLAYWRIGHT_TIMEOUT=60000 npm run test:e2e
```

#### 4. 跨浏览器测试失败
```bash
# 检查浏览器驱动
npm run test:selenium -- --browser firefox
```

### 调试模式

#### 本地调试E2E测试
```bash
# 启动调试模式
npm run test:e2e:debug

# 查看测试报告
npm run test:e2e:report
```

#### 本地调试跨浏览器测试
```bash
# 设置无头模式为false
HEADLESS=false npm run test:cross-browser
```

## 📈 性能优化

### 流水线优化策略

1. **并行执行**: 单元测试和E2E测试并行运行
2. **缓存策略**: npm缓存、pip缓存、构建产物缓存
3. **条件执行**: 跨浏览器测试仅在主分支执行
4. **增量测试**: 仅测试变更相关的模块（未来优化）

### 执行时间基准

- **构建阶段**: < 3分钟
- **单元测试**: < 2分钟
- **E2E测试**: < 5分钟
- **跨浏览器测试**: < 8分钟
- **总执行时间**: < 15分钟

## 🔄 工作流触发条件

### 完整流水线触发
```
- push到main/master分支
- 对main/master的Pull Request
- 手动触发 (workflow_dispatch)
```

### 部分流水线触发
```
- push到feature分支: 仅执行构建和单元测试
- push到develop分支: 执行构建、单元测试、E2E测试
```

## 📋 检查清单

### PR合并前检查
- [ ] 所有测试通过
- [ ] 代码覆盖率达标
- [ ] ESLint检查通过
- [ ] TypeScript类型检查通过
- [ ] E2E测试通过
- [ ] 跨浏览器测试通过（如果在主分支）

### 发布前检查
- [ ] 预发布环境部署成功
- [ ] 健康检查通过
- [ ] 手动回归测试完成
- [ ] 性能测试通过
- [ ] 安全扫描通过

## 🔗 相关链接

- [GitHub Actions文档](https://docs.github.com/en/actions)
- [Playwright文档](https://playwright.dev/)
- [Vitest文档](https://vitest.dev/)
- [Django测试文档](https://docs.djangoproject.com/en/stable/topics/testing/)
- [项目测试规范](./TESTING_STANDARDS.md)

## 📞 支持

如有问题，请联系：
- 开发团队: dev@alpha.com
- CI/CD支持: devops@alpha.com
- 项目维护者: @layne
