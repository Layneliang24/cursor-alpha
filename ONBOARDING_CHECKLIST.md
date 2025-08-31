# 🎯 Alpha项目新开发者入门检查清单

> **目标**：确保任何新开发者（包括AI助手）都能在30分钟内掌握并应用我们的开发方法论

## 📋 **必须完成的步骤**

### ✅ **第一步：环境配置（5分钟）**
```bash
# 执行自动化配置脚本
./scripts/setup-dev-environment.sh

# 验证配置成功
./scripts/validate-methodology.sh
```
- [ ] 脚本执行成功，无错误提示
- [ ] Task Master正常工作
- [ ] 前后端依赖安装完成
- [ ] Git钩子配置成功

### ✅ **第二步：理解项目规则（10分钟）**
**必读文档**（按顺序）：
- [ ] `.cursorrules` - 核心开发规则（361行）
- [ ] `docs/METHODOLOGY_ONBOARDING.md` - 入门指南
- [ ] `docs/TESTING_STANDARDS.md` - 测试规范
- [ ] `docs/DEVELOPMENT.md` - 开发规范

### ✅ **第三步：掌握Task Master流程（10分钟）**
```bash
# 查看当前任务状态
task-master list

# 了解下一个任务
task-master next

# 查看具体任务详情
task-master show <task-id>
```
- [ ] 理解Task Master的基本命令
- [ ] 知道如何查看和管理任务
- [ ] 理解PRD驱动开发流程

### ✅ **第四步：验证测试驱动开发（5分钟）**
```bash
# 运行前端测试
cd frontend && npm run test:fe -- --run

# 运行后端测试
python tests/run_tests.py --mode=quick

# 运行E2E测试
cd frontend && npx playwright test --project=chromium
```
- [ ] 理解TDD流程：先写测试，再写代码
- [ ] 知道如何运行各种类型的测试
- [ ] 理解测试覆盖率要求

## 🎓 **实践验证任务**

### **练习1：创建简单功能（15分钟）**
目标：通过实际操作验证是否掌握完整流程

```bash
# 1. 创建练习任务
task-master add-task --prompt="创建一个返回当前时间的API接口"

# 2. 查看生成的任务
task-master show <new-task-id>

# 3. 分解任务
task-master expand --id=<new-task-id>

# 4. 按TDD流程实现
# - 先写测试用例
# - 再写实现代码
# - 验证测试通过

# 5. 提交代码
git add .
git commit -m "feat(api): 添加获取当前时间接口"

# 6. 标记完成
task-master set-status --id=<new-task-id> --status=done
```

**验收标准**：
- [ ] 成功创建并分解任务
- [ ] 编写了对应的测试用例
- [ ] 实现了功能代码
- [ ] 所有测试通过
- [ ] 正确提交了代码
- [ ] 更新了任务状态

### **练习2：修复模拟Bug（10分钟）**
目标：验证调试和修复流程

```bash
# 1. 创建Bug修复任务
task-master add-task --prompt="修复用户登录时偶尔出现的超时问题"

# 2. 研究问题
task-master research --query="用户登录超时问题的常见原因和解决方案"

# 3. 更新任务详情
task-master update-task --id=<bug-task-id> --prompt="根据研究结果，问题可能是..."

# 4. 按标准流程修复
# 5. 记录到FAQ文档
# 6. 提交代码并标记完成
```

## 🔄 **日常工作流程检查**

### **每日开始工作前**
```bash
# 1. 检查合规性
./scripts/check-development-compliance.sh

# 2. 查看今日任务
task-master next

# 3. 确认测试环境正常
npm run test:fe -- --run --reporter=basic
```

### **每次提交代码前**
```bash
# 1. 运行完整测试
npm run test:fe
python tests/run_tests.py

# 2. 检查测试覆盖率
npm run test:fe -- --coverage

# 3. 验证提交信息规范
# 格式：type(scope): description
```

### **每周回顾**
```bash
# 1. 分析开发合规性
./scripts/check-development-compliance.sh

# 2. 回顾任务完成情况
task-master list --status=done

# 3. 更新文档和FAQ
# 根据本周遇到的问题更新docs/FAQ.md
```

## 🚨 **强制执行机制**

### **自动化检查点**
1. **Git Pre-commit**：提交前自动检查测试文件
2. **CI/CD Pipeline**：所有测试必须通过
3. **Task Master验证**：任务状态必须正确更新
4. **文档同步检查**：功能变更必须更新文档

### **违规处理**
- ❌ **无测试文件**：提交被拒绝
- ❌ **测试不通过**：无法合并到主分支
- ❌ **不使用Task Master**：代码review时要求补充
- ❌ **文档不同步**：功能被标记为未完成

## 🎯 **成功标准**

### **个人层面**
- [ ] 能在30分钟内在新环境搭建开发环境
- [ ] 严格遵循TDD流程
- [ ] 主动使用Task Master管理任务
- [ ] 及时更新文档和FAQ

### **团队层面**
- [ ] 合规性评分保持在90%以上
- [ ] 测试覆盖率达到项目要求
- [ ] Bug修复时间控制在2小时内
- [ ] 新功能开发周期可预测

### **项目层面**
- [ ] 代码质量持续提升
- [ ] 技术债务得到控制
- [ ] 开发效率稳定提高
- [ ] 团队知识有效沉淀

## 📞 **获取帮助**

### **遇到问题时**
1. **查看FAQ**：`docs/FAQ.md`
2. **搜索文档**：`grep -r "关键词" docs/`
3. **使用AI研究**：`task-master research --query="你的问题"`
4. **查看示例**：`docs/TESTING_STANDARDS.md`中的代码示例

### **需要支持时**
1. **技术问题**：查看`docs/technical/`目录
2. **流程问题**：查看`docs/DEVELOPMENT.md`
3. **测试问题**：查看`docs/TESTING_STANDARDS.md`
4. **部署问题**：查看`docs/DEPLOYMENT.md`

---

## 🎉 **完成入门后**

恭喜！您现在已经掌握了Alpha项目的完整开发方法论。

**记住核心原则**：
1. **PRD驱动**：所有功能都从需求文档开始
2. **测试优先**：先写测试，再写代码
3. **Task Master管理**：所有工作都通过任务管理
4. **文档同步**：代码变更必须更新文档
5. **自动化验证**：依靠工具保证质量

**下一步**：
- 选择一个真实任务开始开发
- 严格遵循学到的流程
- 在实践中不断改进和完善

**持续改进**：
- 定期运行合规性检查
- 及时更新文档和FAQ
- 分享经验和最佳实践
