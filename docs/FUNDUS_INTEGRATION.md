# Fundus爬虫集成说明

## 📋 概述

本项目已成功集成Fundus爬虫框架，用于提升英语新闻爬取的数据质量。Fundus是一个专门为新闻网站设计的Python爬虫框架，具有以下优势：

- **专门为新闻设计**：内置新闻文章解析器
- **高质量数据**：自动提取标题、正文、作者、发布时间
- **多语言支持**：支持多种英语新闻源
- **稳定性强**：内置错误处理和重试机制
- **扩展性好**：支持自定义解析规则

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
pip install fundus
```

### 2. 基本使用

```bash
# 使用Fundus爬虫抓取BBC新闻
python manage.py crawl_news --source bbc --crawler fundus

# 抓取所有支持的新闻源
python manage.py crawl_news --source all --crawler fundus

# 测试模式（不保存到数据库）
python manage.py crawl_news --source bbc --crawler fundus --dry-run --verbose
```

### 3. 支持的新闻源

#### Fundus爬虫支持的新闻源：
- **BBC** (`bbc`)
- **CNN** (`cnn`)
- **Reuters** (`reuters`)
- **TechCrunch** (`techcrunch`)
- **The Guardian** (`the_guardian`)
- **The New York Times** (`the_new_york_times`)
- **Wired** (`wired`)
- **Ars Technica** (`ars_technica`)
- **Hacker News** (`hacker_news`)
- **Stack Overflow Blog** (`stack_overflow`)

#### 传统爬虫支持的新闻源：
- **BBC** (`bbc`)
- **CNN** (`cnn`)
- **Reuters** (`reuters`)
- **TechCrunch** (`techcrunch`)
- **China Daily** (`local_test`)
- **新华社英语** (`xinhua`)

## 🔧 技术实现

### 1. 核心组件

#### FundusCrawlerService
```python
from apps.english.fundus_crawler import FundusCrawlerService

# 创建服务实例
service = FundusCrawlerService()

# 获取可用发布者
available = service.get_available_publishers()

# 爬取指定发布者
articles = service.crawl_publisher('bbc', max_articles=10)

# 爬取所有支持的发布者
all_articles = service.crawl_all_supported(max_articles_per_publisher=5)
```

#### FundusNewsItem
```python
from apps.english.fundus_crawler import FundusNewsItem

# 创建新闻项
item = FundusNewsItem(
    title="Article Title",
    content="Article content...",
    url="https://example.com/article",
    source="BBC",
    published_at=datetime.now(),
    summary="Article summary",
    difficulty_level="intermediate",
    tags=["news", "technology"],
    image_url="https://example.com/image.jpg",
    image_alt="Image description"
)
```

### 2. 数据质量保证

#### 内容过滤
- 自动过滤内容过短的文章（少于50个单词）
- 智能去重（基于URL）
- 内容质量评估

#### 难度分级
- **beginner**: 简单词汇，短句子，适合初学者
- **intermediate**: 中等难度，适合中级学习者
- **advanced**: 复杂词汇，长句子，适合高级学习者

#### 标签提取
自动从内容中提取相关标签：
- 技术类：technology, tech, ai, software
- 商业类：business, economy, finance
- 健康类：health, medical, healthcare
- 科学类：science, research, study
- 政治类：politics, government, policy
- 环境类：environment, climate, energy
- 国际类：world, international, global

### 3. 错误处理

- 网络连接异常处理
- 内容解析失败处理
- 发布者不可用时的降级处理
- 详细的日志记录

## 📊 性能优化

### 1. 延迟初始化
```python
# 避免在导入时初始化，提高启动速度
fundus_crawler_service = None

def get_fundus_service():
    global fundus_crawler_service
    if fundus_crawler_service is None:
        fundus_crawler_service = FundusCrawlerService()
    return fundus_crawler_service
```

### 2. 并发控制
- 控制每个发布者的爬取数量
- 避免对目标网站造成过大压力
- 支持自定义爬取间隔

### 3. 缓存机制
- 避免重复爬取相同URL
- 智能更新机制

## 🧪 测试

### 单元测试
```bash
# 运行Fundus相关测试
cd tests
pytest unit/test_fundus_crawler.py -v
```

### 集成测试
```bash
# 测试Fundus爬虫功能
python manage.py crawl_news --source bbc --crawler fundus --dry-run --verbose
```

## 🔄 与现有系统集成

### 1. 兼容性
Fundus爬虫完全兼容现有的新闻系统：
- 使用相同的数据库模型
- 支持相同的API接口
- 保持相同的数据格式

### 2. 混合模式
支持同时使用传统爬虫和Fundus爬虫：
```bash
# 使用两种爬虫
python manage.py crawl_news --source all --crawler both
```

### 3. 渐进式迁移
- 可以逐步从传统爬虫迁移到Fundus爬虫
- 支持并行运行两种爬虫
- 不影响现有功能

## 📈 监控和日志

### 1. 日志记录
```python
import logging
logger = logging.getLogger(__name__)

# 记录爬取进度
logger.info(f"开始爬取 {publisher_id} 的新闻...")
logger.info(f"{publisher_id} 爬取完成: {len(articles)} 条新闻")
```

### 2. 性能监控
- 爬取时间统计
- 成功率监控
- 数据质量评估

### 3. 错误告警
- 网络连接失败告警
- 内容解析失败告警
- 发布者不可用告警

## 🚀 未来规划

### 1. 功能扩展
- 支持更多新闻源
- 增加内容分类功能
- 支持多语言新闻

### 2. 性能优化
- 异步爬取支持
- 分布式爬取
- 智能调度算法

### 3. 质量提升
- 更精确的难度评估
- 更智能的标签提取
- 更好的内容去重

## 📞 支持

如有问题，请：
1. 查看本文档的相关章节
2. 检查日志文件
3. 运行测试用例
4. 联系开发团队

---

*最后更新：2024年12月*
