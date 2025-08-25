# 需求文档：完善英语学习-地道表达功能

## 基本信息
- **需求标题**: 完善英语学习-地道表达功能
- **需求类型**: feature
- **优先级**: medium
- **组件**: english
- **负责人**: developer
- **预估工时**: 8小时
- **创建时间**: 2024-01-15

## 需求描述

### 背景
当前英语学习模块缺少地道表达（Idiomatic Expressions）功能，用户无法学习和练习英语习语、俚语和地道表达方式。

### 目标
1. 提供地道表达词库管理功能
2. 实现地道表达的学习和练习模式
3. 支持表达的分类和难度等级
4. 提供使用场景和例句展示
5. 实现学习进度跟踪和统计

### 功能范围
- 地道表达词库的增删改查
- 按分类和难度筛选表达
- 学习模式：浏览、记忆、测试
- 练习模式：选择题、填空题、情景应用
- 学习进度和统计数据

## 验收标准

### 功能验收
1. ✅ 用户可以浏览地道表达词库
2. ✅ 用户可以按分类（商务、日常、学术等）筛选表达
3. ✅ 用户可以按难度等级筛选表达
4. ✅ 用户可以查看表达的详细信息（含义、例句、使用场景）
5. ✅ 用户可以进行地道表达练习（多种题型）
6. ✅ 系统记录用户学习进度和正确率
7. ✅ 用户可以查看学习统计和进度报告

### 性能验收
- 表达列表加载时间 < 2秒
- 练习题生成时间 < 1秒
- 支持1000+地道表达数据

### 兼容性验收
- 支持桌面端和移动端响应式设计
- 兼容主流浏览器

## 依赖关系

### 前置依赖
- 用户认证系统
- 英语学习基础模块
- 数据库表结构

### 后置影响
- 可能影响学习统计模块
- 需要更新导航菜单

## 技术要求

### 后端技术栈
- **框架**: Django REST Framework
- **数据库**: MySQL
- **缓存**: Redis（可选）
- **API文档**: drf-spectacular

### 前端技术栈
- **框架**: Vue 3 + Composition API
- **状态管理**: Pinia
- **UI组件**: Element Plus
- **路由**: Vue Router

### 数据库设计
```sql
-- 地道表达表
CREATE TABLE idiomatic_expressions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    expression VARCHAR(200) NOT NULL,
    meaning TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    difficulty_level ENUM('beginner', 'intermediate', 'advanced') NOT NULL,
    usage_context TEXT,
    example_sentences JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 用户学习记录表
CREATE TABLE user_expression_progress (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    expression_id INT NOT NULL,
    mastery_level ENUM('unknown', 'learning', 'familiar', 'mastered') DEFAULT 'unknown',
    correct_count INT DEFAULT 0,
    total_attempts INT DEFAULT 0,
    last_practiced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id),
    FOREIGN KEY (expression_id) REFERENCES idiomatic_expressions(id)
);
```

## 接口设计

### API端点

#### 地道表达管理
- `GET /api/english/expressions/` - 获取表达列表
- `GET /api/english/expressions/{id}/` - 获取表达详情
- `POST /api/english/expressions/` - 创建表达（管理员）
- `PUT /api/english/expressions/{id}/` - 更新表达（管理员）
- `DELETE /api/english/expressions/{id}/` - 删除表达（管理员）

#### 学习功能
- `GET /api/english/expressions/categories/` - 获取分类列表
- `GET /api/english/expressions/practice/` - 获取练习题
- `POST /api/english/expressions/practice/submit/` - 提交练习答案
- `GET /api/english/expressions/progress/` - 获取学习进度
- `POST /api/english/expressions/progress/update/` - 更新学习进度

### 前端页面
- `/english/expressions` - 地道表达主页
- `/english/expressions/browse` - 浏览表达
- `/english/expressions/practice` - 练习模式
- `/english/expressions/progress` - 学习进度

## 安全考虑
- 用户认证和授权
- 输入数据验证和清理
- SQL注入防护
- XSS攻击防护
- CSRF保护

## 测试要求

### 单元测试
- 模型测试：地道表达模型、用户进度模型
- 视图测试：API端点功能测试
- 服务测试：业务逻辑测试
- 前端组件测试：Vue组件单元测试

### 集成测试
- API集成测试
- 数据库操作测试
- 前后端集成测试

### E2E测试
- 用户浏览表达流程
- 用户练习表达流程
- 学习进度查看流程

## 性能要求
- 表达列表分页加载，每页20条
- 练习题缓存机制
- 数据库查询优化
- 前端懒加载和虚拟滚动

## 监控和日志
- 用户学习行为日志
- API调用监控
- 错误日志记录
- 性能指标监控

## 部署要求
- 数据库迁移脚本
- 静态文件更新
- 缓存清理
- 功能开关配置

---

**模板说明**：
- 本文档遵循项目需求文档标准格式
- 包含完整的技术实现细节
- 支持自动化测试生成
- 适用于"需求→测试→实现"流水线