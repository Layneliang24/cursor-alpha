# 需求文档：完善英语学习-地道表达模块

## 基本信息

**标题**: 完善英语学习-地道表达模块

**类型**: feature

**优先级**: high

**组件**: backend, frontend, api, database

**负责人**: developer

**预估工时**: 16

**创建时间**: 2025-01-17

## 需求描述

### 背景
当前英语学习模块已有基础的Expression模型，但地道表达功能不够完善，缺乏系统的学习流程、练习模式和数据分析功能。用户无法有效学习和掌握英语习语、俚语和地道表达方式。

### 目标
1. **完善地道表达学习系统**：提供完整的学习、练习、复习流程
2. **增强用户体验**：提供多种学习模式和交互方式
3. **集成数据分析**：将地道表达学习数据集成到仪表盘系统
4. **提升学习效果**：通过智能推荐和个性化学习提升用户掌握程度

### 功能范围
- 地道表达词库管理和分类
- 多种学习模式（浏览、记忆、测试、情景应用）
- 智能练习系统（选择题、填空题、情景对话）
- 学习进度跟踪和掌握程度评估
- 个性化推荐和学习计划
- 仪表盘数据集成和可视化

## 验收标准

### 功能验收
1. ✅ **词库管理功能**
   - 用户可以浏览完整的地道表达词库
   - 支持按分类（商务、日常、学术、情感等）筛选
   - 支持按难度等级（初级、中级、高级）筛选
   - 支持按使用频率（高频、中频、低频）筛选
   - 支持搜索功能（按表达内容、含义、场景）

2. ✅ **学习模式功能**
   - **浏览模式**：用户可以浏览表达列表，查看详细信息
   - **记忆模式**：提供记忆卡片，支持翻转查看含义和例句
   - **测试模式**：多种题型（选择题、填空题、情景应用）
   - **情景模式**：模拟真实对话场景，练习表达使用

3. ✅ **练习系统功能**
   - **选择题练习**：给出表达，选择正确含义
   - **填空题练习**：给出含义，填写正确表达
   - **情景对话练习**：在对话中正确使用表达
   - **造句练习**：使用表达造句，系统评估正确性

4. ✅ **进度跟踪功能**
   - 记录每个表达的学习次数和掌握程度
   - 提供学习进度可视化（热力图、趋势图）
   - 支持复习提醒和间隔重复算法
   - 生成个人学习报告和统计

5. ✅ **仪表盘集成功能**
   - 在英语学习仪表盘中显示地道表达学习统计
   - 提供表达学习热力图和趋势分析
   - 集成到总体学习进度和成就系统
   - 支持数据导出和分享

### 性能验收
- 表达列表加载时间 < 1秒
- 练习题生成时间 < 500ms
- 支持10000+地道表达数据
- 并发用户支持 > 1000

### 兼容性验收
- 支持桌面端和移动端响应式设计
- 兼容主流浏览器（Chrome、Firefox、Safari、Edge）
- 支持离线学习模式（PWA）

## 依赖关系

### 前置依赖
- 用户认证系统（已完成）
- 英语学习基础模块（已完成）
- 数据分析系统（已完成）
- Expression模型（已完成）

### 后置影响
- 需要更新英语学习仪表盘
- 需要更新学习统计系统
- 需要更新用户成就系统

## 技术要求

### 后端技术栈
- **框架**: Django 5.2 + Django REST Framework
- **数据库**: MySQL 8.0
- **缓存**: Redis 6.0
- **API文档**: drf-spectacular
- **任务队列**: Celery（用于数据统计）
- **数据爬取**: Scrapy + Selenium（用于数据采集）
- **AI处理**: OpenAI API / Claude API（用于数据增强）

### 数据来源方案
- **公开API**: 第三方词典API、翻译API
- **网络爬虫**: 权威网站数据采集
- **AI生成**: 使用大模型生成和验证数据
- **用户贡献**: 社区用户提交和审核
- **数据购买**: 商业数据源采购

### 前端技术栈
- **框架**: Vue 3 + Composition API
- **状态管理**: Pinia
- **UI组件**: Element Plus
- **路由**: Vue Router
- **图表**: ECharts
- **PWA**: Workbox

### 数据库设计

#### 扩展现有Expression模型
```sql
-- 扩展现有的english_expressions表
ALTER TABLE english_expressions 
ADD COLUMN learning_difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
ADD COLUMN usage_examples JSON,
ADD COLUMN cultural_notes TEXT,
ADD COLUMN pronunciation_guide VARCHAR(200),
ADD COLUMN related_expressions JSON,
ADD COLUMN tags JSON,
ADD COLUMN popularity_score DECIMAL(3,2) DEFAULT 0.0;

-- 创建用户表达学习进度表
CREATE TABLE user_expression_progress (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    expression_id BIGINT NOT NULL,
    mastery_level ENUM('unknown', 'learning', 'familiar', 'mastered') DEFAULT 'unknown',
    correct_count INT DEFAULT 0,
    total_attempts INT DEFAULT 0,
    last_practiced_at TIMESTAMP NULL,
    next_review_date DATE NULL,
    learning_streak INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (expression_id) REFERENCES english_expressions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_expression (user_id, expression_id),
    INDEX idx_user_mastery (user_id, mastery_level),
    INDEX idx_next_review (user_id, next_review_date)
);

-- 创建表达练习记录表
CREATE TABLE expression_practice_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    expression_id BIGINT NOT NULL,
    practice_type ENUM('multiple_choice', 'fill_blank', 'sentence_building', 'dialogue') NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_spent_seconds INT DEFAULT 0,
    user_answer TEXT,
    correct_answer TEXT,
    practice_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (expression_id) REFERENCES english_expressions(id) ON DELETE CASCADE,
    INDEX idx_user_date (user_id, practice_date),
    INDEX idx_expression_date (expression_id, practice_date)
);

-- 创建表达分类表
CREATE TABLE expression_categories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) DEFAULT '#409EFF',
    icon VARCHAR(50),
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 创建表达标签表
CREATE TABLE expression_tags (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建表达-标签关联表
CREATE TABLE expression_tag_relations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    expression_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (expression_id) REFERENCES english_expressions(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES expression_tags(id) ON DELETE CASCADE,
    UNIQUE KEY unique_expression_tag (expression_id, tag_id)
);
```

### API设计

#### 地道表达管理API
```http
# 获取表达列表
GET /api/v1/english/expressions/
参数: category, difficulty, frequency, search, page, page_size

# 获取表达详情
GET /api/v1/english/expressions/{id}/

# 获取表达分类
GET /api/v1/english/expressions/categories/

# 获取表达标签
GET /api/v1/english/expressions/tags/

# 获取用户学习进度
GET /api/v1/english/expressions/progress/

# 更新学习进度
POST /api/v1/english/expressions/progress/update/
```

#### 练习系统API
```http
# 获取练习题
GET /api/v1/english/expressions/practice/
参数: type, difficulty, category, count

# 提交练习答案
POST /api/v1/english/expressions/practice/submit/

# 获取练习历史
GET /api/v1/english/expressions/practice/history/

# 获取推荐练习
GET /api/v1/english/expressions/practice/recommendations/
```

#### 仪表盘集成API
```http
# 获取表达学习统计
GET /api/v1/english/expressions/dashboard/stats/

# 获取表达学习热力图
GET /api/v1/english/expressions/dashboard/heatmap/

# 获取表达学习趋势
GET /api/v1/english/expressions/dashboard/trends/

# 获取表达掌握程度分布
GET /api/v1/english/expressions/dashboard/mastery-distribution/
```

### 前端页面设计

#### 主要页面
- `/english/expressions` - 地道表达主页
- `/english/expressions/browse` - 浏览表达
- `/english/expressions/learn` - 学习模式
- `/english/expressions/practice` - 练习模式
- `/english/expressions/progress` - 学习进度
- `/english/expressions/dashboard` - 表达学习仪表盘

#### 组件设计
- `ExpressionCard.vue` - 表达卡片组件
- `ExpressionList.vue` - 表达列表组件
- `ExpressionDetail.vue` - 表达详情组件
- `PracticeQuestion.vue` - 练习题组件
- `ProgressChart.vue` - 进度图表组件
- `MasteryHeatmap.vue` - 掌握程度热力图组件

## 仪表盘集成方案

### 数据集成
1. **学习统计集成**
   - 在英语学习仪表盘中添加"地道表达"统计卡片
   - 显示今日学习表达数、掌握表达数、学习时长
   - 集成到总体学习进度计算

2. **可视化集成**
   - 在数据分析页面添加表达学习热力图
   - 添加表达掌握程度趋势图
   - 添加表达学习分布饼图

3. **成就系统集成**
   - 添加表达学习相关成就
   - 支持表达学习里程碑
   - 集成到用户等级系统

### 数据流设计
```
用户学习行为 → 数据收集 → 统计分析 → 仪表盘展示
     ↓              ↓           ↓           ↓
练习记录表 → 进度更新 → 统计计算 → 图表渲染
```

## 数据来源与获取方案

### 数据来源优先级

#### 1. **免费公开数据源** ⭐⭐⭐⭐⭐
- **Urban Dictionary API**: 获取俚语和地道表达
- **Free Dictionary API**: 获取习语和成语
- **Merriam-Webster API**: 权威词典数据
- **Cambridge Dictionary**: 剑桥词典API
- **Oxford Learner's Dictionary**: 牛津学习者词典

#### 2. **网络爬虫采集** ⭐⭐⭐⭐
- **权威网站**:
  - `https://www.urbandictionary.com/` - 俚语词典
  - `https://www.merriam-webster.com/` - 韦氏词典
  - `https://dictionary.cambridge.org/` - 剑桥词典
  - `https://www.collinsdictionary.com/` - 柯林斯词典
  - `https://www.ldoceonline.com/` - 朗文词典

- **学习网站**:
  - `https://www.englishclub.com/` - 英语俱乐部
  - `https://www.bbc.co.uk/learningenglish/` - BBC英语学习
  - `https://www.voanews.com/` - 美国之音

#### 3. **AI生成与增强** ⭐⭐⭐
- **OpenAI GPT-4**: 生成地道表达和例句
- **Claude API**: 验证和优化表达内容
- **本地大模型**: 使用开源模型生成数据

#### 4. **用户贡献系统** ⭐⭐
- 社区用户提交地道表达
- 专家审核和验证
- 用户评分和反馈

#### 5. **商业数据源** ⭐
- 购买专业词典数据
- 订阅商业API服务

### 数据获取技术方案

#### 爬虫系统设计
```python
# 爬虫架构
class ExpressionSpider:
    """地道表达爬虫基类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def crawl_urban_dictionary(self):
        """爬取Urban Dictionary数据"""
        # 实现Urban Dictionary爬虫逻辑
        
    def crawl_merriam_webster(self):
        """爬取韦氏词典数据"""
        # 实现韦氏词典爬虫逻辑
        
    def crawl_cambridge(self):
        """爬取剑桥词典数据"""
        # 实现剑桥词典爬虫逻辑
```

#### AI数据生成系统
```python
# AI数据生成
class ExpressionGenerator:
    """AI地道表达生成器"""
    
    def __init__(self, api_key):
        self.openai_client = OpenAI(api_key=api_key)
    
    def generate_expressions(self, category, count=10):
        """生成指定类别的地道表达"""
        prompt = f"""
        生成{count}个{category}类别的英语地道表达，包含：
        1. 表达内容
        2. 中文含义
        3. 使用场景
        4. 例句（中英文）
        5. 难度等级
        6. 文化背景说明
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return self.parse_ai_response(response.choices[0].message.content)
    
    def validate_expression(self, expression):
        """验证表达的正确性和地道性"""
        # 使用AI验证表达质量
```

#### 数据质量控制系统
```python
# 数据质量控制
class DataQualityController:
    """数据质量控制器"""
    
    def validate_expression_data(self, expression_data):
        """验证表达数据质量"""
        checks = [
            self.check_expression_format,
            self.check_meaning_accuracy,
            self.check_example_quality,
            self.check_cultural_context
        ]
        
        score = 0
        for check in checks:
            score += check(expression_data)
        
        return score / len(checks)
    
    def deduplicate_expressions(self, expressions):
        """去重和合并表达数据"""
        # 实现去重逻辑
```

### 数据采集实施计划

#### 第一阶段：基础数据采集（4小时）
1. **Urban Dictionary爬虫开发**
   - 爬取热门俚语和地道表达
   - 提取表达、含义、例句、评分
   - 预计采集数据：5000+ 条

2. **Free Dictionary API集成**
   - 集成免费词典API
   - 获取习语和成语数据
   - 预计采集数据：3000+ 条

3. **数据清洗和格式化**
   - 统一数据格式
   - 去除重复和低质量数据
   - 添加分类和标签

#### 第二阶段：AI数据增强（3小时）
1. **AI生成系统开发**
   - 使用GPT-4生成地道表达
   - 按类别生成（商务、日常、学术等）
   - 预计生成数据：2000+ 条

2. **数据验证和优化**
   - AI验证生成数据的质量
   - 人工抽样检查
   - 优化生成提示词

#### 第三阶段：用户贡献系统（2小时）
1. **用户提交功能**
   - 用户提交地道表达
   - 社区投票和评分
   - 专家审核机制

2. **数据管理后台**
   - 数据审核界面
   - 质量评分系统
   - 数据统计报告

### 数据存储和更新策略

#### 数据存储结构
```sql
-- 数据来源记录表
CREATE TABLE expression_sources (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    expression_id BIGINT NOT NULL,
    source_type ENUM('crawler', 'api', 'ai_generated', 'user_submitted') NOT NULL,
    source_url VARCHAR(500),
    source_name VARCHAR(100),
    quality_score DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (expression_id) REFERENCES english_expressions(id)
);

-- 数据更新日志表
CREATE TABLE data_update_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    update_type ENUM('crawl', 'generate', 'import', 'clean') NOT NULL,
    records_count INT DEFAULT 0,
    success_count INT DEFAULT 0,
    error_count INT DEFAULT 0,
    execution_time INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 数据更新策略
- **每日更新**: 爬虫数据（Urban Dictionary热门内容）
- **每周更新**: AI生成数据（新类别和主题）
- **每月更新**: 用户贡献数据审核和入库
- **季度更新**: 数据质量评估和清理

## 实施计划

### 第一阶段：数据采集系统开发（4小时）
1. 爬虫系统开发和部署
2. API集成和数据获取
3. 数据清洗和格式化
4. 基础数据入库（目标：5000+条）

### 第二阶段：基础功能开发（8小时）
1. 数据库表结构设计和迁移
2. 基础API开发（CRUD操作）
3. 前端页面框架搭建
4. 基础学习功能实现

### 第三阶段：练习系统开发（4小时）

### 第二阶段：练习系统开发（4小时）
1. 练习题目生成算法
2. 多种练习模式实现
3. 答案评估系统
4. 练习记录管理

### 第三阶段：仪表盘集成（2小时）
1. 数据统计API开发
2. 仪表盘组件开发
3. 数据可视化实现
4. 集成测试

### 第四阶段：优化和测试（2小时）
1. 性能优化
2. 用户体验优化
3. 全面测试
4. 文档完善

## 风险评估

### 技术风险
- **数据量风险**：大量表达数据可能影响性能
  - 缓解措施：使用分页、缓存、索引优化
- **算法复杂度**：智能推荐算法可能复杂
  - 缓解措施：先实现简单算法，逐步优化

### 业务风险
- **用户接受度**：新功能可能不被用户接受
  - 缓解措施：用户调研、渐进式发布
- **数据质量**：表达数据质量可能不高
  - 缓解措施：数据验证、用户反馈机制

## 成功指标

### 功能指标
- 表达学习完成率 > 80%
- 练习正确率 > 70%
- 用户留存率提升 > 20%

### 性能指标
- 页面加载时间 < 2秒
- API响应时间 < 500ms
- 系统可用性 > 99.5%

### 用户指标
- 日活跃用户数增长 > 30%
- 用户满意度 > 4.0/5.0
- 功能使用频率 > 60%

## 后续规划

### 短期规划（1-2个月）
- 完善表达数据质量
- 优化推荐算法
- 增加更多练习模式

### 中期规划（3-6个月）
- 开发移动端应用
- 增加社交学习功能
- 集成AI辅助学习

### 长期规划（6-12个月）
- 开发国际化版本
- 增加更多语言支持
- 构建学习社区 