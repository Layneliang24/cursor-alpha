# 测试用例库

## 📋 文档说明

本文档是项目的标准化测试用例库，按模块和功能分类归档，确保测试用例的统一性和可维护性。

## 🏗️ 用例库结构

```
tests/
├── regression/          # 回归测试用例
│   ├── english/        # 英语学习模块回归测试
│   ├── auth/           # 认证模块回归测试
│   └── common/         # 通用功能回归测试
├── new_features/        # 新功能测试用例
│   └── data_analysis/  # 数据分析功能测试
└── resources/           # 测试资源
    ├── fixtures/        # 测试数据文件
    └── mocks/          # 模拟数据
```

## 📝 测试用例标准格式

### 用例模板
```yaml
test_case:
  id: "TC_XXX"
  module: "模块名称"
  function: "功能名称"
  priority: "高/中/低"
  description: "测试描述"
  preconditions: ["前置条件"]
  test_steps: ["测试步骤"]
  expected_result: "预期结果"
  test_data: "测试数据文件"
  tags: ["标签列表"]
  test_type: "单元测试/集成测试/API测试"
  execution_time: "预计执行时间"
  dependencies: ["依赖的测试用例"]
```

### 优先级定义
- **高**：核心功能、安全相关、用户反馈问题
- **中**：重要功能、性能相关
- **低**：辅助功能、边缘情况

### 标签分类
- **功能标签**：发音、练习、新闻、认证等
- **测试类型**：单元、集成、API、前端等
- **业务标签**：核心功能、辅助功能、新功能等

## 🎓 英语学习模块测试用例

### 智能练习功能

#### TC_001: 单词发音功能测试
```yaml
test_case:
  id: "TC_001"
  module: "英语学习-智能练习"
  function: "单词发音功能"
  priority: "高"
  description: "验证单词自动发音功能正常工作"
  preconditions:
    - "用户已登录"
    - "练习页面已加载"
    - "音频文件可用"
  test_steps:
    - "切换到新单词"
    - "检查是否自动发音"
    - "验证发音质量"
  expected_result: "新单词自动播放发音，音频清晰无杂音"
  test_data: "test_words.json"
  tags: ["发音", "自动播放", "核心功能"]
  test_type: "单元测试"
  execution_time: "30秒"
  dependencies: []
```

#### TC_002: 练习进度跟踪测试
```yaml
test_case:
  id: "TC_002"
  module: "英语学习-智能练习"
  function: "练习进度跟踪"
  priority: "高"
  description: "验证练习进度正确记录和显示"
  preconditions:
    - "用户已开始练习"
    - "数据库连接正常"
  test_steps:
    - "完成一个单词练习"
    - "检查进度条更新"
    - "验证数据库记录"
  expected_result: "进度条正确更新，数据库记录准确"
  test_data: "test_progress_data.json"
  tags: ["进度跟踪", "数据记录", "核心功能"]
  test_type: "集成测试"
  execution_time: "1分钟"
  dependencies: ["TC_001"]
```

#### TC_003: 暂停/继续功能测试
```yaml
test_case:
  id: "TC_003"
  module: "英语学习-智能练习"
  function: "暂停/继续功能"
  priority: "中"
  description: "验证练习暂停和继续功能"
  preconditions:
    - "练习正在进行中"
    - "计时器正常运行"
  test_steps:
    - "点击暂停按钮"
    - "检查计时器停止"
    - "点击继续按钮"
    - "验证计时器恢复"
  expected_result: "暂停时计时器停止，继续时计时器恢复，时间计算准确"
  test_data: "test_timer_data.json"
  tags: ["暂停功能", "计时器", "用户体验"]
  test_type: "单元测试"
  execution_time: "45秒"
  dependencies: ["TC_002"]
```

### 新闻阅读功能

#### TC_004: 新闻爬取功能测试
```yaml
test_case:
  id: "TC_004"
  module: "英语学习-新闻阅读"
  function: "新闻爬取功能"
  priority: "高"
  description: "验证新闻爬取功能正常工作"
  preconditions:
    - "网络连接正常"
    - "目标网站可访问"
    - "数据库连接正常"
  test_steps:
    - "选择新闻源"
    - "执行爬取操作"
    - "检查爬取结果"
    - "验证数据保存"
  expected_result: "成功爬取新闻，数据正确保存到数据库"
  test_data: "test_news_sources.json"
  tags: ["新闻爬取", "数据获取", "核心功能"]
  test_type: "集成测试"
  execution_time: "2分钟"
  dependencies: []
```

#### TC_005: 新闻图片显示测试
```yaml
test_case:
  id: "TC_005"
  module: "英语学习-新闻阅读"
  function: "新闻图片显示"
  priority: "高"
  description: "验证新闻图片正确显示"
  preconditions:
    - "新闻数据包含图片"
    - "图片文件存在"
    - "前端页面正常加载"
  test_steps:
    - "加载新闻列表"
    - "检查图片URL构建"
    - "验证图片显示"
  expected_result: "新闻图片正确显示，URL构建正确"
  test_data: "test_news_images.json"
  tags: ["图片显示", "URL构建", "用户体验"]
  test_type: "前端测试"
  execution_time: "1分钟"
  dependencies: ["TC_004"]
```

#### TC_006: 新闻管理功能测试
```yaml
test_case:
  id: "TC_006"
  module: "英语学习-新闻阅读"
  function: "新闻管理功能"
  priority: "中"
  description: "验证新闻管理功能"
  preconditions:
    - "用户具有管理权限"
    - "新闻数据存在"
  test_steps:
    - "打开新闻管理界面"
    - "执行搜索和筛选"
    - "删除指定新闻"
    - "验证删除结果"
  expected_result: "新闻管理功能正常，搜索、筛选、删除操作成功"
  test_data: "test_news_management.json"
  tags: ["新闻管理", "CRUD操作", "管理功能"]
  test_type: "集成测试"
  execution_time: "1.5分钟"
  dependencies: ["TC_005"]
```

### 数据分析功能

#### TC_007: 练习数据统计测试
```yaml
test_case:
  id: "TC_007"
  module: "英语学习-数据分析"
  function: "练习数据统计"
  priority: "高"
  description: "验证练习数据统计功能"
  preconditions:
    - "练习数据存在"
    - "统计服务正常运行"
  test_steps:
    - "访问数据分析页面"
    - "选择统计时间范围"
    - "检查统计数据"
    - "验证图表显示"
  expected_result: "统计数据准确，图表正确显示"
  test_data: "test_practice_stats.json"
  tags: ["数据分析", "统计功能", "新功能"]
  test_type: "集成测试"
  execution_time: "1分钟"
  dependencies: ["TC_002"]
```

#### TC_008: 热力图显示测试
```yaml
test_case:
  id: "TC_008"
  module: "英语学习-数据分析"
  function: "热力图显示"
  priority: "中"
  description: "验证练习热力图正确显示"
  preconditions:
    - "练习数据足够"
    - "图表组件正常"
  test_steps:
    - "加载热力图数据"
    - "检查图表渲染"
    - "验证数据映射"
  expected_result: "热力图正确显示，数据映射准确"
  test_data: "test_heatmap_data.json"
  tags: ["热力图", "图表显示", "数据可视化"]
  test_type: "前端测试"
  execution_time: "45秒"
  dependencies: ["TC_007"]
```

## 🔐 认证模块测试用例

### 用户认证功能

#### TC_009: 用户登录测试
```yaml
test_case:
  id: "TC_009"
  module: "认证-用户管理"
  function: "用户登录"
  priority: "高"
  description: "验证用户登录功能"
  preconditions:
    - "用户账号存在"
    - "认证服务正常"
  test_steps:
    - "输入用户名密码"
    - "提交登录请求"
    - "检查返回结果"
    - "验证JWT token"
  expected_result: "登录成功，返回有效的JWT token"
  test_data: "test_user_credentials.json"
  tags: ["用户登录", "JWT认证", "安全功能"]
  test_type: "API测试"
  execution_time: "30秒"
  dependencies: []
```

#### TC_010: 用户注册测试
```yaml
test_case:
  id: "TC_010"
  module: "认证-用户管理"
  function: "用户注册"
  priority: "高"
  description: "验证用户注册功能"
  preconditions:
    - "注册服务正常"
    - "数据库连接正常"
  test_steps:
    - "填写注册信息"
    - "提交注册请求"
    - "检查用户创建"
    - "验证数据完整性"
  expected_result: "注册成功，用户数据正确保存"
  test_data: "test_registration_data.json"
  tags: ["用户注册", "数据创建", "安全功能"]
  test_type: "API测试"
  execution_time: "45秒"
  dependencies: []
```

### 权限管理功能

#### TC_011: 权限验证测试
```yaml
test_case:
  id: "TC_011"
  module: "认证-权限管理"
  function: "权限验证"
  priority: "高"
  description: "验证用户权限控制"
  preconditions:
    - "用户已登录"
    - "权限系统正常"
  test_steps:
    - "访问受限资源"
    - "检查权限验证"
    - "验证访问控制"
  expected_result: "权限验证正确，访问控制有效"
  test_data: "test_permission_data.json"
  tags: ["权限控制", "访问控制", "安全功能"]
  test_type: "集成测试"
  execution_time: "1分钟"
  dependencies: ["TC_009"]
```

## 🌐 通用功能模块测试用例

### 数据库功能

#### TC_012: 数据库连接测试
```yaml
test_case:
  id: "TC_012"
  module: "通用-数据库"
  function: "数据库连接"
  priority: "中"
  description: "验证数据库连接功能"
  preconditions:
    - "数据库服务运行"
    - "网络连接正常"
  test_steps:
    - "建立数据库连接"
    - "执行简单查询"
    - "检查连接状态"
  expected_result: "数据库连接成功，查询正常执行"
  test_data: "test_db_connection.json"
  tags: ["数据库", "连接管理", "基础设施"]
  test_type: "单元测试"
  execution_time: "30秒"
  dependencies: []
```

## 📊 测试用例统计

### 按模块统计
- **英语学习模块**：8个用例
- **认证模块**：3个用例
- **通用功能模块**：1个用例
- **总计**：12个用例

### 按优先级统计
- **高优先级**：9个用例
- **中优先级**：3个用例
- **低优先级**：0个用例

### 按测试类型统计
- **单元测试**：5个用例
- **集成测试**：4个用例
- **API测试**：2个用例
- **前端测试**：1个用例

## 🔄 用例维护

### 更新规则
1. **新功能上线**：必须补充对应的测试用例
2. **Bug修复**：必须更新相关测试用例
3. **功能变更**：必须同步更新测试用例
4. **定期审查**：每月审查一次测试用例有效性

### 版本控制
- 测试用例与代码版本同步
- 记录用例变更历史
- 维护用例依赖关系
- 支持用例回滚

---

**文档版本**：v1.0  
**创建时间**：2025-01-17  
**维护人员**：开发团队  
**审核状态**：待审核


## 📋 文档说明

本文档是项目的标准化测试用例库，按模块和功能分类归档，确保测试用例的统一性和可维护性。

## 🏗️ 用例库结构

```
tests/
├── regression/          # 回归测试用例
│   ├── english/        # 英语学习模块回归测试
│   ├── auth/           # 认证模块回归测试
│   └── common/         # 通用功能回归测试
├── new_features/        # 新功能测试用例
│   └── data_analysis/  # 数据分析功能测试
└── resources/           # 测试资源
    ├── fixtures/        # 测试数据文件
    └── mocks/          # 模拟数据
```

## 📝 测试用例标准格式

### 用例模板
```yaml
test_case:
  id: "TC_XXX"
  module: "模块名称"
  function: "功能名称"
  priority: "高/中/低"
  description: "测试描述"
  preconditions: ["前置条件"]
  test_steps: ["测试步骤"]
  expected_result: "预期结果"
  test_data: "测试数据文件"
  tags: ["标签列表"]
  test_type: "单元测试/集成测试/API测试"
  execution_time: "预计执行时间"
  dependencies: ["依赖的测试用例"]
```

### 优先级定义
- **高**：核心功能、安全相关、用户反馈问题
- **中**：重要功能、性能相关
- **低**：辅助功能、边缘情况

### 标签分类
- **功能标签**：发音、练习、新闻、认证等
- **测试类型**：单元、集成、API、前端等
- **业务标签**：核心功能、辅助功能、新功能等

## 🎓 英语学习模块测试用例

### 智能练习功能

#### TC_001: 单词发音功能测试
```yaml
test_case:
  id: "TC_001"
  module: "英语学习-智能练习"
  function: "单词发音功能"
  priority: "高"
  description: "验证单词自动发音功能正常工作"
  preconditions:
    - "用户已登录"
    - "练习页面已加载"
    - "音频文件可用"
  test_steps:
    - "切换到新单词"
    - "检查是否自动发音"
    - "验证发音质量"
  expected_result: "新单词自动播放发音，音频清晰无杂音"
  test_data: "test_words.json"
  tags: ["发音", "自动播放", "核心功能"]
  test_type: "单元测试"
  execution_time: "30秒"
  dependencies: []
```

#### TC_002: 练习进度跟踪测试
```yaml
test_case:
  id: "TC_002"
  module: "英语学习-智能练习"
  function: "练习进度跟踪"
  priority: "高"
  description: "验证练习进度正确记录和显示"
  preconditions:
    - "用户已开始练习"
    - "数据库连接正常"
  test_steps:
    - "完成一个单词练习"
    - "检查进度条更新"
    - "验证数据库记录"
  expected_result: "进度条正确更新，数据库记录准确"
  test_data: "test_progress_data.json"
  tags: ["进度跟踪", "数据记录", "核心功能"]
  test_type: "集成测试"
  execution_time: "1分钟"
  dependencies: ["TC_001"]
```

#### TC_003: 暂停/继续功能测试
```yaml
test_case:
  id: "TC_003"
  module: "英语学习-智能练习"
  function: "暂停/继续功能"
  priority: "中"
  description: "验证练习暂停和继续功能"
  preconditions:
    - "练习正在进行中"
    - "计时器正常运行"
  test_steps:
    - "点击暂停按钮"
    - "检查计时器停止"
    - "点击继续按钮"
    - "验证计时器恢复"
  expected_result: "暂停时计时器停止，继续时计时器恢复，时间计算准确"
  test_data: "test_timer_data.json"
  tags: ["暂停功能", "计时器", "用户体验"]
  test_type: "单元测试"
  execution_time: "45秒"
  dependencies: ["TC_002"]
```

### 新闻阅读功能

#### TC_004: 新闻爬取功能测试
```yaml
test_case:
  id: "TC_004"
  module: "英语学习-新闻阅读"
  function: "新闻爬取功能"
  priority: "高"
  description: "验证新闻爬取功能正常工作"
  preconditions:
    - "网络连接正常"
    - "目标网站可访问"
    - "数据库连接正常"
  test_steps:
    - "选择新闻源"
    - "执行爬取操作"
    - "检查爬取结果"
    - "验证数据保存"
  expected_result: "成功爬取新闻，数据正确保存到数据库"
  test_data: "test_news_sources.json"
  tags: ["新闻爬取", "数据获取", "核心功能"]
  test_type: "集成测试"
  execution_time: "2分钟"
  dependencies: []
```

#### TC_005: 新闻图片显示测试
```yaml
test_case:
  id: "TC_005"
  module: "英语学习-新闻阅读"
  function: "新闻图片显示"
  priority: "高"
  description: "验证新闻图片正确显示"
  preconditions:
    - "新闻数据包含图片"
    - "图片文件存在"
    - "前端页面正常加载"
  test_steps:
    - "加载新闻列表"
    - "检查图片URL构建"
    - "验证图片显示"
  expected_result: "新闻图片正确显示，URL构建正确"
  test_data: "test_news_images.json"
  tags: ["图片显示", "URL构建", "用户体验"]
  test_type: "前端测试"
  execution_time: "1分钟"
  dependencies: ["TC_004"]
```

#### TC_006: 新闻管理功能测试
```yaml
test_case:
  id: "TC_006"
  module: "英语学习-新闻阅读"
  function: "新闻管理功能"
  priority: "中"
  description: "验证新闻管理功能"
  preconditions:
    - "用户具有管理权限"
    - "新闻数据存在"
  test_steps:
    - "打开新闻管理界面"
    - "执行搜索和筛选"
    - "删除指定新闻"
    - "验证删除结果"
  expected_result: "新闻管理功能正常，搜索、筛选、删除操作成功"
  test_data: "test_news_management.json"
  tags: ["新闻管理", "CRUD操作", "管理功能"]
  test_type: "集成测试"
  execution_time: "1.5分钟"
  dependencies: ["TC_005"]
```

### 数据分析功能

#### TC_007: 练习数据统计测试
```yaml
test_case:
  id: "TC_007"
  module: "英语学习-数据分析"
  function: "练习数据统计"
  priority: "高"
  description: "验证练习数据统计功能"
  preconditions:
    - "练习数据存在"
    - "统计服务正常运行"
  test_steps:
    - "访问数据分析页面"
    - "选择统计时间范围"
    - "检查统计数据"
    - "验证图表显示"
  expected_result: "统计数据准确，图表正确显示"
  test_data: "test_practice_stats.json"
  tags: ["数据分析", "统计功能", "新功能"]
  test_type: "集成测试"
  execution_time: "1分钟"
  dependencies: ["TC_002"]
```

#### TC_008: 热力图显示测试
```yaml
test_case:
  id: "TC_008"
  module: "英语学习-数据分析"
  function: "热力图显示"
  priority: "中"
  description: "验证练习热力图正确显示"
  preconditions:
    - "练习数据足够"
    - "图表组件正常"
  test_steps:
    - "加载热力图数据"
    - "检查图表渲染"
    - "验证数据映射"
  expected_result: "热力图正确显示，数据映射准确"
  test_data: "test_heatmap_data.json"
  tags: ["热力图", "图表显示", "数据可视化"]
  test_type: "前端测试"
  execution_time: "45秒"
  dependencies: ["TC_007"]
```

## 🔐 认证模块测试用例

### 用户认证功能

#### TC_009: 用户登录测试
```yaml
test_case:
  id: "TC_009"
  module: "认证-用户管理"
  function: "用户登录"
  priority: "高"
  description: "验证用户登录功能"
  preconditions:
    - "用户账号存在"
    - "认证服务正常"
  test_steps:
    - "输入用户名密码"
    - "提交登录请求"
    - "检查返回结果"
    - "验证JWT token"
  expected_result: "登录成功，返回有效的JWT token"
  test_data: "test_user_credentials.json"
  tags: ["用户登录", "JWT认证", "安全功能"]
  test_type: "API测试"
  execution_time: "30秒"
  dependencies: []
```

#### TC_010: 用户注册测试
```yaml
test_case:
  id: "TC_010"
  module: "认证-用户管理"
  function: "用户注册"
  priority: "高"
  description: "验证用户注册功能"
  preconditions:
    - "注册服务正常"
    - "数据库连接正常"
  test_steps:
    - "填写注册信息"
    - "提交注册请求"
    - "检查用户创建"
    - "验证数据完整性"
  expected_result: "注册成功，用户数据正确保存"
  test_data: "test_registration_data.json"
  tags: ["用户注册", "数据创建", "安全功能"]
  test_type: "API测试"
  execution_time: "45秒"
  dependencies: []
```

### 权限管理功能

#### TC_011: 权限验证测试
```yaml
test_case:
  id: "TC_011"
  module: "认证-权限管理"
  function: "权限验证"
  priority: "高"
  description: "验证用户权限控制"
  preconditions:
    - "用户已登录"
    - "权限系统正常"
  test_steps:
    - "访问受限资源"
    - "检查权限验证"
    - "验证访问控制"
  expected_result: "权限验证正确，访问控制有效"
  test_data: "test_permission_data.json"
  tags: ["权限控制", "访问控制", "安全功能"]
  test_type: "集成测试"
  execution_time: "1分钟"
  dependencies: ["TC_009"]
```

## 🌐 通用功能模块测试用例

### 数据库功能

#### TC_012: 数据库连接测试
```yaml
test_case:
  id: "TC_012"
  module: "通用-数据库"
  function: "数据库连接"
  priority: "中"
  description: "验证数据库连接功能"
  preconditions:
    - "数据库服务运行"
    - "网络连接正常"
  test_steps:
    - "建立数据库连接"
    - "执行简单查询"
    - "检查连接状态"
  expected_result: "数据库连接成功，查询正常执行"
  test_data: "test_db_connection.json"
  tags: ["数据库", "连接管理", "基础设施"]
  test_type: "单元测试"
  execution_time: "30秒"
  dependencies: []
```

## 📊 测试用例统计

### 按模块统计
- **英语学习模块**：8个用例
- **认证模块**：3个用例
- **通用功能模块**：1个用例
- **总计**：12个用例

### 按优先级统计
- **高优先级**：9个用例
- **中优先级**：3个用例
- **低优先级**：0个用例

### 按测试类型统计
- **单元测试**：5个用例
- **集成测试**：4个用例
- **API测试**：2个用例
- **前端测试**：1个用例

## 🔄 用例维护

### 更新规则
1. **新功能上线**：必须补充对应的测试用例
2. **Bug修复**：必须更新相关测试用例
3. **功能变更**：必须同步更新测试用例
4. **定期审查**：每月审查一次测试用例有效性

### 版本控制
- 测试用例与代码版本同步
- 记录用例变更历史
- 维护用例依赖关系
- 支持用例回滚

---

**文档版本**：v1.0  
**创建时间**：2025-01-17  
**维护人员**：开发团队  
**审核状态**：待审核

