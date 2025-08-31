# Alpha项目开发方法论入门指南

## 🎯 **核心理念**

本项目采用**Task Master驱动的测试优先开发方法论**，确保高质量、可维护的代码交付。

## 📋 **新开发者入门清单**

### 第一步：环境配置（5分钟）
```bash
# 1. 执行自动化配置脚本
./scripts/setup-dev-environment.sh

# 2. 验证环境
task-master list
npm run test:fe -- --run
python tests/run_tests.py --mode=quick
```

### 第二步：理解项目结构（10分钟）
**必读文档顺序**：
1. `docs/README.md` - 项目概览
2. `docs/DEVELOPMENT.md` - 开发规范
3. `docs/TESTING_STANDARDS.md` - 测试规范
4. `.cursorrules` - 核心开发规则
5. `docs/FAQ.md` - 常见问题解决方案

### 第三步：掌握开发流程（15分钟）
**标准开发循环**：
```bash
# 1. 查看当前任务
task-master list

# 2. 选择下一个任务
task-master next

# 3. 分解复杂任务
task-master expand --id=<task-id> --research

# 4. 开始开发（测试驱动）
# - 先写测试用例
# - 再写实现代码
# - 验证测试通过

# 5. 提交代码
git add .
git commit -m "feat(module): 功能描述"

# 6. 标记任务完成
task-master set-status --id=<task-id> --status=done
```

## 🔄 **开发方法论核心流程**

### 1. **PRD驱动开发**
```bash
# 新功能开发必须先创建PRD
# 1. 创建PRD文档
vim .taskmaster/docs/feature-name-prd.txt

# 2. 解析PRD生成任务
task-master parse-prd .taskmaster/docs/feature-name-prd.txt

# 3. 分析任务复杂度
task-master analyze-complexity --research

# 4. 分解复杂任务
task-master expand --all --research
```

### 2. **测试驱动开发**
```bash
# 前端组件开发
# 1. 创建测试文件
touch src/components/__tests__/NewComponent.spec.ts

# 2. 编写测试用例（定义期望行为）
# 3. 运行测试（确认失败）
npm run test:fe -- --run src/components/__tests__/NewComponent.spec.ts

# 4. 编写最小实现代码
# 5. 运行测试（确认通过）
# 6. 重构优化代码

# 后端API开发
# 1. 创建测试文件
touch tests/unit/test_new_api.py

# 2. 编写API测试用例
# 3. 运行测试（确认失败）
cd tests && python -m pytest unit/test_new_api.py -v

# 4. 编写API实现
# 5. 运行测试（确认通过）
```

### 3. **质量保障流程**
```bash
# 开发完成后的质量检查
# 1. 运行所有测试
npm run test:fe
python tests/run_tests.py --mode=full

# 2. 检查测试覆盖率
npm run test:fe -- --coverage
pytest --cov=backend --cov-report=html

# 3. 代码质量检查
npm run lint
flake8 backend/

# 4. 提交代码
git add .
git commit -m "feat(module): 功能描述"
```

## 🛡️ **方法论强制执行机制**

### 自动化检查点
1. **Git Pre-commit钩子**：自动检查测试文件存在性
2. **CI/CD流水线**：所有测试必须通过才能合并
3. **Task Master配置**：强制使用标准化任务管理
4. **文档更新检查**：确保相关文档同步更新

### 强制规范
- ❌ **禁止直接提交代码**：必须先有对应测试
- ❌ **禁止跳过测试**：所有测试必须通过
- ❌ **禁止不更新文档**：功能变更必须同步文档
- ❌ **禁止忽视Task Master**：所有开发必须通过任务管理

## 📚 **快速参考卡片**

### 常用Task Master命令
```bash
task-master list                    # 查看任务列表
task-master next                    # 查看下一个任务
task-master show <id>              # 查看任务详情
task-master expand --id=<id>       # 分解任务
task-master set-status --id=<id> --status=done  # 标记完成
task-master update-subtask --id=<id> --prompt="进度更新"  # 更新进度
```

### 测试命令
```bash
# 前端测试
npm run test:fe                    # 运行所有前端测试
npm run test:fe:watch             # 监听模式
npm run test:fe -- --coverage     # 覆盖率检查

# 后端测试
python tests/run_tests.py         # 一键测试
pytest tests/unit/               # 单元测试
pytest tests/integration/        # 集成测试

# E2E测试
npx playwright test               # 所有E2E测试
npx playwright test --ui          # 可视化测试
```

### 开发命令
```bash
# 启动开发服务器
./start-simple.bat               # 一键启动前后端

# 单独启动
cd backend && python manage.py runserver
cd frontend && npm run dev

# 数据库操作
python manage.py migrate          # 数据库迁移
python manage.py createsuperuser  # 创建管理员
```

## 🔒 **跨环境一致性保障**

### 1. **配置文件标准化**
- `.taskmaster/config.json` - Task Master配置
- `.cursorrules` - 开发规则
- `package.json` - 前端依赖和脚本
- `requirements.txt` - 后端依赖
- `pytest.ini` - 测试配置

### 2. **文档驱动开发**
- 所有规范都有文档记录
- 文档版本控制，确保同步
- 新人onboarding清单

### 3. **自动化验证**
- Git钩子强制检查
- CI/CD流水线验证
- 测试覆盖率门禁

## 🎓 **新开发者培训流程**

### 30分钟快速入门
1. **5分钟**：执行环境配置脚本
2. **10分钟**：阅读核心文档
3. **15分钟**：完成第一个练习任务

### 练习任务模板
```bash
# 练习：添加一个简单的API接口
# 1. 创建任务
task-master add-task --prompt="添加获取用户统计信息的API接口"

# 2. 分解任务
task-master expand --id=<new-task-id>

# 3. 按TDD流程开发
# 4. 验证完整流程
```

## 🔒 **跨环境方法论保障机制**

### **四层保障体系**
1. **🔧 环境自动化** - `./scripts/setup-dev-environment.sh`
2. **📋 合规性验证** - `./scripts/validate-methodology.sh`
3. **📊 持续监控** - `./scripts/check-development-compliance.sh`
4. **📚 培训体系** - `.taskmaster/templates/new-developer-training-prd.txt`

### **使用方法**
```bash
# 新环境配置（首次使用）
./scripts/setup-dev-environment.sh

# 验证环境合规性
./scripts/validate-methodology.sh

# 日常合规性检查
./scripts/check-development-compliance.sh

# 新人培训
task-master parse-prd .taskmaster/templates/new-developer-training-prd.txt --tag=training
```

### **自动化强制机制**
- ✅ **Git Pre-commit钩子**：自动检查测试文件
- ✅ **CI/CD门禁**：测试不通过无法合并
- ✅ **Task Master强制**：所有开发必须通过任务管理
- ✅ **文档同步检查**：功能变更必须更新文档

## 🎯 **确保持续应用的关键措施**

### **1. 制度化保障**
- 📋 **入职必修**：新开发者必须完成培训任务
- 🔄 **定期review**：每月检查方法论执行情况
- 📊 **量化考核**：通过合规性评分监控执行质量

### **2. 技术化保障**
- 🤖 **自动化检查**：每次提交自动验证合规性
- 🛡️ **强制门禁**：不符合规范的代码无法合并
- 📈 **持续监控**：实时跟踪开发流程执行情况

### **3. 文化化保障**
- 📚 **知识沉淀**：所有经验都记录到文档中
- 🎓 **培训体系**：标准化的学习路径
- 🤝 **团队共识**：所有开发者都认同并遵循

## 🚀 **立即验证机制**

让我们立即验证当前环境的方法论合规性：
