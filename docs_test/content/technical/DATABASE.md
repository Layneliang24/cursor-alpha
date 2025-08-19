# 数据库设计文档

## 📋 概述

本文档描述了Alpha技术共享平台的数据库设计，包括数据模型、表结构、关系设计和性能优化方案。

## 🏗️ 数据库架构

### 技术选型
- **主数据库**: MySQL 8.0+
- **缓存数据库**: Redis 6.0+
- **搜索引擎**: Elasticsearch 7.0+
- **任务队列**: Redis + Celery

## 📊 核心数据模型

### 1. 用户系统 (User System)

#### 1.1 用户表 (users)
```sql
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    phone VARCHAR(20),
    avatar_url VARCHAR(500),
    bio TEXT,
    birth_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    email_verified_at TIMESTAMP NULL,
    phone_verified_at TIMESTAMP NULL,
    last_login TIMESTAMP NULL,
    last_login_ip INET,
    password_changed_at TIMESTAMP NULL,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMP NULL,
    timezone VARCHAR(50) DEFAULT 'Asia/Shanghai',
    language VARCHAR(10) DEFAULT 'zh-hans',
    theme VARCHAR(20) DEFAULT 'light',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_phone (phone),
    INDEX idx_is_active (is_active),
    INDEX idx_created_at (created_at)
);
```

#### 1.2 用户配置表 (user_profiles)
```sql
CREATE TABLE user_profiles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    real_name VARCHAR(100),
    company VARCHAR(200),
    position VARCHAR(100),
    website VARCHAR(500),
    location VARCHAR(100),
    github_username VARCHAR(100),
    linkedin_url VARCHAR(500),
    twitter_username VARCHAR(100),
    learning_goals JSON,
    skill_tags JSON,
    interests JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_company (company),
    INDEX idx_location (location)
);
```

### 2. 内容系统 (Content System)

#### 2.1 文章表 (articles)
```sql
CREATE TABLE articles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    content LONGTEXT NOT NULL,
    summary TEXT,
    author_id BIGINT NOT NULL,
    category_id BIGINT,
    status ENUM('draft', 'pending', 'published', 'archived', 'deleted') DEFAULT 'draft',
    featured BOOLEAN DEFAULT FALSE,
    allow_comments BOOLEAN DEFAULT TRUE,
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    comment_count INT DEFAULT 0,
    published_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_author_id (author_id),
    INDEX idx_category_id (category_id),
    INDEX idx_status (status),
    INDEX idx_published_at (published_at),
    INDEX idx_created_at (created_at),
    INDEX idx_slug (slug),
    FULLTEXT idx_title_content (title, content)
);
```

#### 2.2 分类表 (categories)
```sql
CREATE TABLE categories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    parent_id BIGINT NULL,
    icon VARCHAR(100),
    color VARCHAR(7) DEFAULT '#409EFF',
    order_index INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE,
    INDEX idx_parent_id (parent_id),
    INDEX idx_slug (slug),
    INDEX idx_order_index (order_index),
    INDEX idx_is_active (is_active)
);
```

### 3. 英语学习系统 (English Learning System)

#### 3.1 单词表 (words)
```sql
CREATE TABLE words (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) UNIQUE NOT NULL,
    phonetic VARCHAR(100),
    part_of_speech VARCHAR(50),
    definition TEXT NOT NULL,
    example TEXT,
    difficulty_level ENUM('beginner', 'intermediate', 'advanced') DEFAULT 'beginner',
    audio_url VARCHAR(500),
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_word (word),
    INDEX idx_difficulty_level (difficulty_level),
    INDEX idx_part_of_speech (part_of_speech)
);
```

#### 3.2 新闻表 (news)
```sql
CREATE TABLE news (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    content LONGTEXT,
    url VARCHAR(1000) UNIQUE NOT NULL,
    source VARCHAR(100) NOT NULL,
    publisher VARCHAR(100),
    author VARCHAR(100),
    published_at TIMESTAMP NULL,
    difficulty_level ENUM('beginner', 'intermediate', 'advanced'),
    tags JSON,
    image_url VARCHAR(500),
    image_alt VARCHAR(200),
    crawler_type ENUM('traditional', 'fundus', 'ai') DEFAULT 'traditional',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_source (source),
    INDEX idx_publisher (publisher),
    INDEX idx_difficulty_level (difficulty_level),
    INDEX idx_published_at (published_at),
    INDEX idx_created_at (created_at),
    FULLTEXT idx_title_summary (title, summary)
);
```

## 🔗 数据关系设计

### 1. 实体关系图 (ERD)
```
用户 (users)
├── 1:1 用户配置 (user_profiles)
├── 1:N 文章 (articles)
├── 1:N 用户学习进度 (user_word_progress)
└── N:M 权限 (permissions)

分类 (categories)
├── 1:N 文章 (articles)
└── 1:N 子分类 (categories)

文章 (articles)
├── N:1 作者 (users)
├── N:1 分类 (categories)
└── N:M 标签 (tags)

单词 (words)
└── 1:N 用户学习进度 (user_word_progress)

新闻 (news)
└── 独立实体，无直接关联
```

## 📈 索引策略

### 1. 主键索引
- 所有表使用自增主键
- 主键自动创建聚集索引

### 2. 唯一索引
- 用户名、邮箱、手机号等唯一字段
- 文章slug、分类slug等URL友好字段

### 3. 普通索引
- 外键字段：author_id, category_id等
- 查询频繁字段：status, created_at等
- 排序字段：order_index, published_at等

### 4. 全文索引
- 文章标题和内容：title + content
- 新闻标题和摘要：title + summary

## 🚀 性能优化

### 1. 查询优化
- **索引优化**: 为常用查询创建合适的索引
- **查询重写**: 优化复杂查询语句
- **分页优化**: 使用游标分页代替偏移分页

### 2. 缓存策略
- **Redis缓存**: 热点数据缓存
- **查询缓存**: 复杂查询结果缓存
- **对象缓存**: 用户会话和权限缓存

### 3. 读写分离
- **主从复制**: 主库写，从库读
- **读写分离**: 应用层读写分离
- **负载均衡**: 多个从库负载均衡

## 🔒 安全设计

### 1. 数据加密
- **敏感字段**: 密码、手机号等敏感信息加密
- **传输加密**: 使用TLS/SSL加密传输
- **存储加密**: 数据库文件加密

### 2. 访问控制
- **用户认证**: JWT Token认证
- **权限控制**: 基于角色的访问控制
- **数据隔离**: 用户数据隔离

## 📁 相关文件

### 数据库配置
- `backend/alpha/settings.py` - 数据库连接配置
- `mysql/conf.d/mysql.cnf` - MySQL配置文件
- `mysql/init.sql` - 数据库初始化脚本

### 数据模型
- `backend/apps/users/models.py` - 用户数据模型
- `backend/apps/articles/models.py` - 文章数据模型
- `backend/apps/english/models.py` - 英语学习数据模型

---

*最后更新：2025-01-17*
*更新内容：整合技术架构目录下的数据库设计内容，创建完整的数据库设计文档*
