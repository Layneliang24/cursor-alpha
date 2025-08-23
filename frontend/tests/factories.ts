// 前端测试数据工厂
export interface User {
  id: number
  username: string
  email: string
  avatar?: string
  isAuthenticated: boolean
  isAdmin: boolean
  preferences: {
    theme: 'light' | 'dark'
    language: 'zh-CN' | 'en-US'
    soundEnabled: boolean
  }
}

export interface Article {
  id: number
  title: string
  content: string
  excerpt: string
  author: User
  category: string
  tags: string[]
  publishedAt: string
  readTime: number
  coverImage?: string
  isPublished: boolean
}

export interface Word {
  id: number
  word: string
  translation: string
  phonetic: string
  difficulty: 'easy' | 'medium' | 'hard'
  category: string
  examples: string[]
  reviewCount: number
  lastReviewed?: string
}

export interface TypingSession {
  id: number
  word: Word
  isCorrect: boolean
  typingSpeed: number
  responseTime: number
  timestamp: string
}

export interface UserStats {
  totalWordsPracticed: number
  totalCorrectWords: number
  averageWpm: number
  totalPracticeTime: number
  lastPracticeDate: string
  streakDays: number
}

export interface SearchResult {
  id: number
  type: 'article' | 'word' | 'user'
  title: string
  description: string
  url: string
  relevance: number
}

// 用户数据工厂
export class UserFactory {
  static create(overrides: Partial<User> = {}): User {
    return {
      id: Math.floor(Math.random() * 10000),
      username: `user_${Math.random().toString(36).substr(2, 9)}`,
      email: `user_${Math.random().toString(36).substr(2, 9)}@example.com`,
      avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${Math.random()}`,
      isAuthenticated: true,
      isAdmin: false,
      preferences: {
        theme: 'light',
        language: 'zh-CN',
        soundEnabled: true
      },
      ...overrides
    }
  }

  static createAdmin(overrides: Partial<User> = {}): User {
    return this.create({
      isAdmin: true,
      ...overrides
    })
  }

  static createGuest(): User {
    return this.create({
      isAuthenticated: false,
      isAdmin: false
    })
  }

  static createMultiple(count: number, overrides: Partial<User> = {}): User[] {
    return Array.from({ length: count }, (_, index) => 
      this.create({ id: index + 1, ...overrides })
    )
  }
}

// 文章数据工厂
export class ArticleFactory {
  static create(overrides: Partial<Article> = {}): Article {
    const author = overrides.author || UserFactory.create()
    
    return {
      id: Math.floor(Math.random() * 10000),
      title: `测试文章 ${Math.random().toString(36).substr(2, 9)}`,
      content: `这是测试文章的内容。${'测试内容 '.repeat(50)}`,
      excerpt: '这是测试文章的摘要，用于预览显示。',
      author,
      category: '技术',
      tags: ['测试', '前端', 'Vue'],
      publishedAt: new Date().toISOString(),
      readTime: Math.floor(Math.random() * 20) + 5,
      coverImage: `https://picsum.photos/800/400?random=${Math.random()}`,
      isPublished: true,
      ...overrides
    }
  }

  static createDraft(overrides: Partial<Article> = {}): Article {
    return this.create({
      isPublished: false,
      ...overrides
    })
  }

  static createMultiple(count: number, overrides: Partial<Article> = {}): Article[] {
    return Array.from({ length: count }, (_, index) => 
      this.create({ id: index + 1, ...overrides })
    )
  }

  static createByCategory(category: string, count: number = 5): Article[] {
    return this.createMultiple(count, { category })
  }
}

// 单词数据工厂
export class WordFactory {
  static create(overrides: Partial<Word> = {}): Word {
    return {
      id: Math.floor(Math.random() * 10000),
      word: `word_${Math.random().toString(36).substr(2, 6)}`,
      translation: `翻译_${Math.random().toString(36).substr(2, 6)}`,
      phonetic: `[wɜːd]`,
      difficulty: 'medium',
      category: '日常用语',
      examples: [
        `这是一个关于 ${overrides.word || 'word'} 的例句。`,
        `另一个 ${overrides.word || 'word'} 的使用场景。`
      ],
      reviewCount: Math.floor(Math.random() * 10),
      lastReviewed: Math.random() > 0.5 ? new Date().toISOString() : undefined,
      ...overrides
    }
  }

  static createEasy(overrides: Partial<Word> = {}): Word {
    return this.create({
      difficulty: 'easy',
      ...overrides
    })
  }

  static createHard(overrides: Partial<Word> = {}): Word {
    return this.create({
      difficulty: 'hard',
      ...overrides
    })
  }

  static createMultiple(count: number, overrides: Partial<Word> = {}): Word[] {
    return Array.from({ length: count }, (_, index) => 
      this.create({ id: index + 1, ...overrides })
    )
  }

  static createByDifficulty(difficulty: Word['difficulty'], count: number = 5): Word[] {
    return this.createMultiple(count, { difficulty })
  }
}

// 打字会话数据工厂
export class TypingSessionFactory {
  static create(overrides: Partial<TypingSession> = {}): TypingSession {
    const word = overrides.word || WordFactory.create()
    
    return {
      id: Math.floor(Math.random() * 10000),
      word,
      isCorrect: Math.random() > 0.3,
      typingSpeed: Math.floor(Math.random() * 100) + 20,
      responseTime: Math.floor(Math.random() * 5000) + 500,
      timestamp: new Date().toISOString(),
      ...overrides
    }
  }

  static createCorrect(overrides: Partial<TypingSession> = {}): TypingSession {
    return this.create({
      isCorrect: true,
      ...overrides
    })
  }

  static createIncorrect(overrides: Partial<TypingSession> = {}): TypingSession {
    return this.create({
      isCorrect: false,
      ...overrides
    })
  }

  static createMultiple(count: number, overrides: Partial<TypingSession> = {}): TypingSession[] {
    return Array.from({ length: count }, (_, index) => 
      this.create({ id: index + 1, ...overrides })
    )
  }
}

// 用户统计数据工厂
export class UserStatsFactory {
  static create(overrides: Partial<UserStats> = {}): UserStats {
    return {
      totalWordsPracticed: Math.floor(Math.random() * 1000) + 100,
      totalCorrectWords: Math.floor(Math.random() * 800) + 80,
      averageWpm: Math.floor(Math.random() * 50) + 30,
      totalPracticeTime: Math.floor(Math.random() * 3600) + 600,
      lastPracticeDate: new Date().toISOString(),
      streakDays: Math.floor(Math.random() * 30) + 1,
      ...overrides
    }
  }

  static createBeginner(overrides: Partial<UserStats> = {}): UserStats {
    return this.create({
      totalWordsPracticed: Math.floor(Math.random() * 100) + 10,
      totalCorrectWords: Math.floor(Math.random() * 80) + 8,
      averageWpm: Math.floor(Math.random() * 20) + 15,
      totalPracticeTime: Math.floor(Math.random() * 1800) + 300,
      streakDays: Math.floor(Math.random() * 7) + 1,
      ...overrides
    })
  }

  static createAdvanced(overrides: Partial<UserStats> = {}): UserStats {
    return this.create({
      totalWordsPracticed: Math.floor(Math.random() * 2000) + 1000,
      totalCorrectWords: Math.floor(Math.random() * 1800) + 900,
      averageWpm: Math.floor(Math.random() * 30) + 70,
      totalPracticeTime: Math.floor(Math.random() * 7200) + 3600,
      streakDays: Math.floor(Math.random() * 60) + 30,
      ...overrides
    })
  }
}

// 搜索结果数据工厂
export class SearchResultFactory {
  static create(overrides: Partial<SearchResult> = {}): SearchResult {
    return {
      id: Math.floor(Math.random() * 10000),
      type: 'article',
      title: `搜索结果 ${Math.random().toString(36).substr(2, 9)}`,
      description: '这是搜索结果的描述信息。',
      url: `/search/result/${Math.random().toString(36).substr(2, 9)}`,
      relevance: Math.random(),
      ...overrides
    }
  }

  static createArticle(overrides: Partial<SearchResult> = {}): SearchResult {
    return this.create({
      type: 'article',
      ...overrides
    })
  }

  static createWord(overrides: Partial<SearchResult> = {}): SearchResult {
    return this.create({
      type: 'word',
      ...overrides
    })
  }

  static createUser(overrides: Partial<SearchResult> = {}): SearchResult {
    return this.create({
      type: 'user',
      ...overrides
    })
  }

  static createMultiple(count: number, overrides: Partial<SearchResult> = {}): SearchResult[] {
    return Array.from({ length: count }, (_, index) => 
      this.create({ id: index + 1, ...overrides })
    )
  }
}

// 测试数据集工厂
export class TestDataSetFactory {
  static createCompleteDataset() {
    const users = UserFactory.createMultiple(3)
    const articles = ArticleFactory.createMultiple(5, { author: users[0] })
    const words = WordFactory.createMultiple(10)
    const typingSessions = TypingSessionFactory.createMultiple(20, { word: words[0] })
    const userStats = UserStatsFactory.create()
    const searchResults = SearchResultFactory.createMultiple(8)

    return {
      users,
      articles,
      words,
      typingSessions,
      userStats,
      searchResults
    }
  }

  static createEnglishLearningDataset() {
    const words = [
      ...WordFactory.createByDifficulty('easy', 5),
      ...WordFactory.createByDifficulty('medium', 8),
      ...WordFactory.createByDifficulty('hard', 3)
    ]
    
    const typingSessions = words.flatMap(word => 
      TypingSessionFactory.createMultiple(3, { word })
    )
    
    const userStats = UserStatsFactory.createAdvanced()
    
    return {
      words,
      typingSessions,
      userStats
    }
  }

  static createBlogDataset() {
    const users = UserFactory.createMultiple(2)
    const articles = [
      ...ArticleFactory.createByCategory('技术', 3),
      ...ArticleFactory.createByCategory('生活', 2),
      ...ArticleFactory.createByCategory('学习', 2)
    ]
    
    return {
      users,
      articles
    }
  }
}

// 导出所有工厂
export default {
  UserFactory,
  ArticleFactory,
  WordFactory,
  TypingSessionFactory,
  UserStatsFactory,
  SearchResultFactory,
  TestDataSetFactory
} 