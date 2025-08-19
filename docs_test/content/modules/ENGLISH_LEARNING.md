# 英语学习模块

## 📋 概述

英语学习模块是Alpha平台的核心功能之一，提供全面的英语学习解决方案，包括单词学习、新闻阅读、打字练习、学习统计等功能。

### 核心特性
- 🎯 **智能学习**：基于遗忘曲线的单词复习算法
- 📰 **新闻阅读**：实时爬取高质量英语新闻
- ⌨️ **打字练习**：集成Qwerty Learn的打字训练系统
- 📊 **数据分析**：学习进度可视化，学习效果分析
- 🎵 **多媒体支持**：音频发音、图片辅助、例句展示

---

## 🏗️ 系统架构

### 模块组成
```
英语学习模块
├── 单词学习系统
│   ├── 词典管理
│   ├── 学习算法
│   ├── 复习计划
│   └── 进度跟踪
├── 新闻阅读系统
│   ├── 爬虫引擎
│   ├── 内容管理
│   ├── 难度分级
│   └── 阅读统计
├── 打字练习系统
│   ├── 练习模式
│   ├── 错误分析
│   ├── 速度统计
│   └── 进度记录
└── 学习分析系统
    ├── 数据收集
    ├── 统计分析
    ├── 可视化展示
    └── 报告生成
```

### 技术架构
- **后端**: Django + Django REST Framework
- **数据库**: MySQL + Redis
- **前端**: Vue 3 + Element Plus + ECharts
- **爬虫**: Fundus + 传统爬虫
- **任务队列**: Celery + Redis

---

## 📚 单词学习系统

### 功能特性

#### 词典管理
- **多词典支持**
  - CET4/CET6：大学英语四六级
  - GRE/TOEFL：研究生入学考试
  - IELTS：雅思考试
  - 专业词典：计算机、医学、法律等

- **词典导入**
  - JSON格式词典文件
  - 批量导入功能
  - 词典版本管理
  - 自定义词典创建

#### 学习算法
- **间隔重复算法**
  - 基于遗忘曲线的复习计划
  - 动态调整复习间隔
  - 个性化学习路径
  - 智能难度调整

- **学习模式**
  - 新词学习：首次接触单词
  - 复习模式：巩固记忆
  - 测试模式：检验掌握程度
  - 挑战模式：高难度单词

#### 进度跟踪
- **学习统计**
  - 每日学习单词数
  - 复习单词数
  - 掌握单词数
  - 学习时长统计

- **进度可视化**
  - 学习热力图
  - 进度条显示
  - 里程碑标记
  - 成就系统

### 数据模型

#### Word模型
```python
class Word(models.Model):
    """单词模型"""
    word = models.CharField(max_length=100, unique=True)
    phonetic = models.CharField(max_length=100, blank=True)
    part_of_speech = models.CharField(max_length=50, blank=True)
    definition = models.TextField()
    example = models.TextField(blank=True)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    frequency_rank = models.IntegerField(null=True, blank=True)
    audio_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

#### UserWordProgress模型
```python
class UserWordProgress(models.Model):
    """用户单词进度模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    review_count = models.IntegerField(default=0)
    last_review_date = models.DateTimeField(null=True, blank=True)
    next_review_date = models.DateTimeField(null=True, blank=True)
    mastery_level = models.FloatField(default=0.0)
    ease_factor = models.FloatField(default=2.5)
    interval_days = models.IntegerField(default=0)
    repetition_count = models.IntegerField(default=0)
```

### API接口

#### 获取单词列表
```http
GET /api/v1/english/words/
```

**查询参数**
- `difficulty_level`: 难度级别
- `category_hint`: 分类提示
- `search`: 搜索关键词
- `page`: 页码
- `page_size`: 每页数量

#### 获取单词详情
```http
GET /api/v1/english/words/{id}/
```

#### 更新学习进度
```http
POST /api/v1/english/words/{id}/progress/
```

**请求体**
```json
{
  "status": "learning",
  "mastery_level": 0.8,
  "review_count": 3
}
```

---

## 📰 新闻阅读系统

### 功能特性

#### 爬虫引擎
- **Fundus爬虫**
  - 高质量新闻内容
  - 自动图片下载
  - 智能内容提取
  - 多语言支持

- **传统爬虫**
  - 本地测试支持
  - 备选爬取方案
  - 自定义爬取规则
  - 错误重试机制

#### 新闻源支持
- **主流媒体**
  - BBC News
  - CNN
  - Reuters
  - TechCrunch
  - The Guardian

- **专业媒体**
  - Ars Technica
  - Hacker News
  - Stack Overflow
  - Wired

#### 内容管理
- **分类管理**
  - 技术新闻
  - 商业新闻
  - 科技新闻
  - 教育新闻

- **难度分级**
  - 初级：适合初学者
  - 中级：适合进阶学习者
  - 高级：适合高级学习者

### 数据模型

#### News模型
```python
class News(models.Model):
    """新闻模型"""
    title = models.CharField(max_length=500)
    summary = models.TextField()
    content = models.TextField()
    category = models.CharField(max_length=50)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    publish_date = models.DateTimeField()
    source = models.CharField(max_length=100)
    source_url = models.URLField()
    image_url = models.URLField(blank=True)
    image_alt = models.CharField(max_length=200, blank=True)
    word_count = models.IntegerField()
    reading_time_minutes = models.IntegerField()
    key_vocabulary = models.JSONField(default=list)
    comprehension_questions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### 爬虫命令

#### 爬取新闻
```bash
# 使用Fundus爬虫
python manage.py crawl_news --source bbc --crawler fundus --count 10

# 使用传统爬虫
python manage.py crawl_news --source bbc --crawler traditional --count 10

# 测试模式
python manage.py crawl_news --source bbc --crawler fundus --dry-run --verbose
```

#### 支持的新闻源
```bash
# 传统爬虫支持
bbc, cnn, reuters, techcrunch, local_test, xinhua

# Fundus爬虫支持
bbc, cnn, reuters, techcrunch, the_guardian, the_new_york_times, 
wired, ars_technica, hacker_news, stack_overflow
```

---

## ⌨️ 打字练习系统

### 功能特性

#### 练习模式
- **基础练习**
  - 单词练习
  - 句子练习
  - 段落练习
  - 自定义文本

- **专项练习**
  - 速度练习
  - 准确率练习
  - 耐力练习
  - 挑战模式

#### 词典支持
- **内置词典**
  - CET4/CET6词汇
  - GRE/TOEFL词汇
  - 专业领域词汇
  - 常用短语

- **自定义词典**
  - 个人词汇表
  - 学习计划词汇
  - 错词本
  - 收藏词汇

#### 实时反馈
- **输入反馈**
  - 实时显示输入内容
  - 错误字符高亮
  - 正确字符标记
  - 进度条显示

- **统计信息**
  - 当前速度（WPM）
  - 准确率统计
  - 错误类型分析
  - 练习时长

### 数据模型

#### TypingSession模型
```python
class TypingSession(models.Model):
    """打字练习会话模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dictionary = models.CharField(max_length=100)
    chapter = models.IntegerField(default=1)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_words = models.IntegerField(default=0)
    correct_words = models.IntegerField(default=0)
    total_time = models.FloatField(default=0.0)
    average_wpm = models.FloatField(default=0.0)
    accuracy_rate = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
```

#### TypingPracticeRecord模型
```python
class TypingPracticeRecord(models.Model):
    """打字练习记录模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(TypingSession, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    user_input = models.CharField(max_length=100)
    is_correct = models.BooleanField()
    time_spent = models.FloatField()
    key_errors = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 练习流程

#### 1. 创建练习会话
```http
POST /api/v1/english/typing/session/
```

**请求体**
```json
{
  "dictionary": "CET4",
  "chapter": 1,
  "mode": "practice"
}
```

#### 2. 提交练习记录
```http
POST /api/v1/english/typing/record/
```

**请求体**
```json
{
  "session_id": 1,
  "word": "hello",
  "user_input": "hello",
  "is_correct": true,
  "time_spent": 1.5,
  "key_errors": []
}
```

#### 3. 完成练习会话
```http
PUT /api/v1/english/typing/session/{id}/complete/
```

---

## 📊 学习分析系统

### 功能特性

#### 数据收集
- **学习行为数据**
  - 学习时长
  - 学习频率
  - 学习内容
  - 学习效果

- **练习数据**
  - 打字速度
  - 准确率
  - 错误类型
  - 练习时长

#### 统计分析
- **学习统计**
  - 每日学习时长
  - 学习单词数量
  - 掌握程度
  - 学习效率

- **练习统计**
  - 平均打字速度
  - 准确率趋势
  - 错误分析
  - 进步情况

#### 可视化展示
- **图表类型**
  - 热力图：学习频率分布
  - 折线图：学习进度趋势
  - 柱状图：学习成果对比
  - 饼图：学习内容分布

- **交互功能**
  - 时间范围选择
  - 数据筛选
  - 图表缩放
  - 数据导出

### 数据模型

#### LearningStats模型
```python
class LearningStats(models.Model):
    """学习统计模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    words_learned = models.IntegerField(default=0)
    words_reviewed = models.IntegerField(default=0)
    expressions_learned = models.IntegerField(default=0)
    news_read = models.IntegerField(default=0)
    practice_count = models.IntegerField(default=0)
    study_time_minutes = models.IntegerField(default=0)
    accuracy_rate = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### DailyPracticeStats模型
```python
class DailyPracticeStats(models.Model):
    """每日练习统计模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    total_practice_time = models.FloatField(default=0.0)
    total_words_practiced = models.IntegerField(default=0)
    average_wpm = models.FloatField(default=0.0)
    average_accuracy = models.FloatField(default=0.0)
    total_sessions = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
```

### API接口

#### 获取学习统计
```http
GET /api/v1/english/stats/
```

**查询参数**
- `start_date`: 开始日期
- `end_date`: 结束日期
- `type`: 统计类型（daily, weekly, monthly）

#### 获取练习统计
```http
GET /api/v1/english/typing/stats/
```

#### 获取热力图数据
```http
GET /api/v1/english/stats/heatmap/
```

---

## 🎯 学习计划系统

### 功能特性

#### 计划管理
- **学习目标**
  - 每日单词目标
  - 每周学习时长
  - 月度掌握目标
  - 年度学习计划

- **计划类型**
  - 基础学习计划
  - 考试备考计划
  - 专业提升计划
  - 自定义计划

#### 进度跟踪
- **目标完成度**
  - 单词学习进度
  - 时间投入进度
  - 掌握程度进度
  - 整体完成度

- **提醒通知**
  - 学习提醒
  - 复习提醒
  - 目标提醒
  - 成就提醒

### 数据模型

#### LearningPlan模型
```python
class LearningPlan(models.Model):
    """学习计划模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    daily_word_target = models.IntegerField(default=20)
    daily_expression_target = models.IntegerField(default=5)
    review_frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

---

## 🔧 配置说明

### 环境配置

#### Django设置
```python
# settings.py
INSTALLED_APPS = [
    # ... 其他应用
    'apps.english',
]

# 英语学习模块配置
ENGLISH_LEARNING_CONFIG = {
    'DEFAULT_DICTIONARY': 'CET4',
    'DAILY_WORD_LIMIT': 50,
    'REVIEW_INTERVAL_DAYS': [1, 3, 7, 14, 30],
    'MASTERY_THRESHOLD': 0.8,
    'NEWS_CRAWL_INTERVAL': 3600,  # 1小时
    'MAX_NEWS_PER_SOURCE': 20,
}
```

#### Redis配置
```python
# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### 爬虫配置

#### Fundus配置
```python
# fundus_crawler.py
FUNDUS_CONFIG = {
    'API_KEY': 'your_fundus_api_key',
    'BASE_URL': 'https://api.fundus.ai',
    'TIMEOUT': 30,
    'MAX_RETRIES': 3,
    'RATE_LIMIT': 100,  # 每小时请求数
}
```

#### 传统爬虫配置
```python
# news_crawler.py
CRAWLER_CONFIG = {
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'REQUEST_DELAY': 1,  # 请求间隔（秒）
    'MAX_RETRIES': 3,
    'TIMEOUT': 10,
}
```

---

## 📱 前端组件

### 主要组件

#### 单词学习组件
- `WordCard.vue`: 单词卡片组件
- `WordList.vue`: 单词列表组件
- `LearningProgress.vue`: 学习进度组件
- `ReviewScheduler.vue`: 复习计划组件

#### 新闻阅读组件
- `NewsList.vue`: 新闻列表组件
- `NewsDetail.vue`: 新闻详情组件
- `NewsDashboard.vue`: 新闻仪表板组件
- `NewsFilter.vue`: 新闻筛选组件

#### 打字练习组件
- `TypingPractice.vue`: 打字练习主组件
- `WordDisplay.vue`: 单词显示组件
- `InputField.vue`: 输入框组件
- `ProgressBar.vue`: 进度条组件

#### 学习分析组件
- `LearningChart.vue`: 学习图表组件
- `HeatmapChart.vue`: 热力图组件
- `LineChart.vue`: 折线图组件
- `StatisticsPanel.vue`: 统计面板组件

### 状态管理

#### Pinia Store
```javascript
// stores/english.js
export const useEnglishStore = defineStore('english', () => {
  // 状态
  const words = ref([])
  const news = ref([])
  const learningProgress = ref({})
  const practiceStats = ref({})
  
  // 操作
  const fetchWords = async (params) => {
    // 获取单词列表
  }
  
  const updateProgress = async (wordId, progress) => {
    // 更新学习进度
  }
  
  const fetchNews = async (params) => {
    // 获取新闻列表
  }
  
  return {
    words,
    news,
    learningProgress,
    practiceStats,
    fetchWords,
    updateProgress,
    fetchNews
  }
})
```

---

## 🧪 测试指南

### 测试覆盖

#### 单元测试
- **模型测试**
  - 单词模型测试
  - 用户进度测试
  - 新闻模型测试
  - 练习记录测试

- **服务测试**
  - 学习算法测试
  - 爬虫服务测试
  - 统计计算测试
  - 数据导入测试

#### 集成测试
- **API测试**
  - 单词学习API
  - 新闻管理API
  - 打字练习API
  - 学习统计API

- **数据库测试**
  - 数据完整性测试
  - 查询性能测试
  - 事务处理测试
  - 并发访问测试

### 测试运行

#### 运行特定测试
```bash
# 运行英语学习模块测试
python -m pytest tests/unit/test_english_models.py -v

# 运行爬虫测试
python -m pytest tests/integration/test_news_crawler.py -v

# 运行打字练习测试
python -m pytest tests/unit/test_typing_practice.py -v
```

#### 生成测试报告
```bash
# 生成覆盖率报告
pytest --cov=apps.english --cov-report=html

# 生成测试报告
python tests/run_tests.py --module=english --report=html
```

---

## 🚀 性能优化

### 数据库优化

#### 索引优化
```sql
-- 单词表索引
CREATE INDEX idx_word_difficulty ON english_word(difficulty_level);
CREATE INDEX idx_word_frequency ON english_word(frequency_rank);
CREATE INDEX idx_word_created ON english_word(created_at);

-- 用户进度表索引
CREATE INDEX idx_progress_user_word ON english_userwordprogress(user_id, word_id);
CREATE INDEX idx_progress_next_review ON english_userwordprogress(next_review_date);
CREATE INDEX idx_progress_status ON english_userwordprogress(status);

-- 新闻表索引
CREATE INDEX idx_news_category ON english_news(category);
CREATE INDEX idx_news_difficulty ON english_news(difficulty_level);
CREATE INDEX idx_news_publish_date ON english_news(publish_date);
```

#### 查询优化
```python
# 使用select_related减少查询
words = Word.objects.select_related('category').filter(
    difficulty_level='beginner'
)[:20]

# 使用prefetch_related预加载关联数据
user_progress = UserWordProgress.objects.select_related('word').filter(
    user=user
).prefetch_related('word__examples')
```

### 缓存优化

#### Redis缓存
```python
# 缓存热门单词
@cache_page(60 * 15)  # 缓存15分钟
def get_popular_words(request):
    words = Word.objects.filter(
        frequency_rank__lte=1000
    ).order_by('frequency_rank')[:50]
    return JsonResponse({'words': list(words.values())})

# 缓存用户进度
def get_user_progress(user_id):
    cache_key = f'user_progress_{user_id}'
    progress = cache.get(cache_key)
    if not progress:
        progress = UserWordProgress.objects.filter(user_id=user_id)
        cache.set(cache_key, progress, 60 * 5)  # 缓存5分钟
    return progress
```

### 前端优化

#### 代码分割
```javascript
// 路由懒加载
const EnglishLearning = () => import('@/views/english/EnglishLearning.vue')
const TypingPractice = () => import('@/views/english/TypingPractice.vue')

// 组件懒加载
const WordCard = defineAsyncComponent(() => import('@/components/WordCard.vue'))
```

#### 数据缓存
```javascript
// 本地存储缓存
const cacheKey = `english_words_${dictionary}_${page}`
const cachedData = localStorage.getItem(cacheKey)

if (cachedData) {
  return JSON.parse(cachedData)
}

// 内存缓存
const wordCache = new Map()
const getWord = async (id) => {
  if (wordCache.has(id)) {
    return wordCache.get(id)
  }
  const word = await fetchWord(id)
  wordCache.set(id, word)
  return word
}
```

---

## 📚 相关文档

### 技术文档
- [API接口文档](../API.md)
- [数据库设计文档](../technical/DATABASE.md)
- [系统架构文档](../technical/ARCHITECTURE.md)

### 用户文档
- [用户指南](../GUIDE.md)
- [常见问题](../FAQ.md)
- [部署指南](../DEPLOYMENT.md)

### 开发文档
- [开发者指南](../DEVELOPMENT.md)
- [测试规范](../TESTING_STANDARDS.md)
- [代码规范](../DOCUMENTATION_STANDARDS.md)

---

## 📞 支持

### 开发支持
- 查看 [API文档](../API.md) 了解接口规范
- 参考 [开发者指南](../DEVELOPMENT.md) 搭建开发环境
- 查看 [测试指南](../TESTING_STANDARDS.md) 运行测试

### 问题反馈
- 提交Issue：[GitHub Issues](https://github.com/your-repo/issues)
- 功能建议：[Feature Request](https://github.com/your-repo/issues/new?template=feature_request.md)
- Bug报告：[Bug Report](https://github.com/your-repo/issues/new?template=bug_report.md)

---

*最后更新：2025-01-17*
*更新内容：整合现有英语学习相关文档，创建完整的模块文档*

---

## 🧯 常见问题与修复（合并自 FAQ）

### 问题1：自动发音功能失效（智能练习页面）
- 现象：切换单词后不自动发音，ref 丢失
- 根因：动态组件 + key 更新导致 ref 不稳定
- 解决：引入 getCurrentInstance，多重 ref 获取；延迟获取；统一封装 getComponentRef

### 问题2：发音重叠与重复播放
- 现象：多次触发叠加播放
- 解决：全局发音实例互斥管理（停止其它实例）、发音防抖、组件卸载时清理资源

### 问题3：练习界面暂停按钮不起作用
- 现象：暂停后计时器/输入仍工作
- 解决：在 store 中增加 isPaused/pauseElapsedTime，并在计时器与输入路径检查暂停状态；继续时从暂停时间恢复

### 问题4：API 参数映射错误导致 404（打字练习）
- 现象：缺少 category，报“词库不存在”
- 根因：将 dictionary_id 误映射为 category
- 解决：参数改为 category，后端将 difficulty 设为可选并提供默认值

> 详细代码片段与步骤已收敛自 `docs/FAQ.md`，此处提供结论与改法摘要，便于模块内检索与维护。
