import { Page, Locator } from '@playwright/test';
import { TestHelpers } from '../utils/test-helpers';

/**
 * 词典练习页面对象模型
 */
export class DictionaryPage {
  private helpers: TestHelpers;

  // 页面元素定位器
  readonly dictionaryList: Locator;
  readonly createDictionaryButton: Locator;
  readonly searchInput: Locator;
  readonly practiceButton: Locator;
  readonly wordCard: Locator;
  readonly nextWordButton: Locator;
  readonly previousWordButton: Locator;
  readonly showAnswerButton: Locator;
  readonly knownButton: Locator;
  readonly unknownButton: Locator;
  readonly progressBar: Locator;
  readonly scoreDisplay: Locator;
  readonly practiceSettings: Locator;
  readonly difficultySelector: Locator;
  readonly practiceTypeSelector: Locator;

  constructor(private page: Page) {
    this.helpers = new TestHelpers(page);
    
    // 初始化元素定位器
    this.dictionaryList = page.locator('.dictionary-list, [data-testid="dictionary-list"]');
    this.createDictionaryButton = page.locator('button:has-text("创建词典"), button:has-text("Create Dictionary"), [data-testid="create-dictionary"]');
    this.searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="Search"], [data-testid="search-input"]');
    this.practiceButton = page.locator('button:has-text("开始练习"), button:has-text("Start Practice"), [data-testid="practice-button"]');
    this.wordCard = page.locator('.word-card, [data-testid="word-card"]');
    this.nextWordButton = page.locator('button:has-text("下一个"), button:has-text("Next"), [data-testid="next-word"]');
    this.previousWordButton = page.locator('button:has-text("上一个"), button:has-text("Previous"), [data-testid="previous-word"]');
    this.showAnswerButton = page.locator('button:has-text("显示答案"), button:has-text("Show Answer"), [data-testid="show-answer"]');
    this.knownButton = page.locator('button:has-text("认识"), button:has-text("Known"), [data-testid="known-button"]');
    this.unknownButton = page.locator('button:has-text("不认识"), button:has-text("Unknown"), [data-testid="unknown-button"]');
    this.progressBar = page.locator('.progress-bar, [data-testid="progress-bar"]');
    this.scoreDisplay = page.locator('.score-display, [data-testid="score-display"]');
    this.practiceSettings = page.locator('.practice-settings, [data-testid="practice-settings"]');
    this.difficultySelector = page.locator('select[name="difficulty"], [data-testid="difficulty-selector"]');
    this.practiceTypeSelector = page.locator('select[name="practiceType"], [data-testid="practice-type-selector"]');
  }

  /**
   * 导航到词典页面
   */
  async goto() {
    await this.page.goto('/dictionaries');
    await this.helpers.waitForPageLoad();
  }

  /**
   * 搜索词典
   */
  async searchDictionary(searchTerm: string) {
    await this.searchInput.fill(searchTerm);
    await this.page.keyboard.press('Enter');
    await this.helpers.waitForPageLoad();
  }

  /**
   * 选择词典并开始练习
   */
  async startPractice(dictionaryName?: string) {
    if (dictionaryName) {
      // 点击指定词典
      const dictionaryItem = this.page.locator(`[data-testid="dictionary-item"]:has-text("${dictionaryName}")`);
      await dictionaryItem.click();
    } else {
      // 点击第一个词典
      await this.dictionaryList.locator('.dictionary-item, [data-testid="dictionary-item"]').first().click();
    }
    
    await this.practiceButton.click();
    await this.helpers.waitForPageLoad();
  }

  /**
   * 配置练习设置
   */
  async configurePracticeSettings(options: {
    difficulty?: string;
    practiceType?: string;
    wordCount?: number;
  }) {
    if (options.difficulty) {
      await this.difficultySelector.selectOption(options.difficulty);
    }
    
    if (options.practiceType) {
      await this.practiceTypeSelector.selectOption(options.practiceType);
    }
    
    if (options.wordCount) {
      const wordCountInput = this.page.locator('input[name="wordCount"], [data-testid="word-count-input"]');
      await wordCountInput.fill(options.wordCount.toString());
    }
  }

  /**
   * 练习单词 - 标记为认识
   */
  async markWordAsKnown() {
    await this.knownButton.click();
    await this.helpers.waitForPageLoad();
  }

  /**
   * 练习单词 - 标记为不认识
   */
  async markWordAsUnknown() {
    await this.unknownButton.click();
    await this.helpers.waitForPageLoad();
  }

  /**
   * 显示答案
   */
  async showAnswer() {
    await this.showAnswerButton.click();
    await this.page.waitForTimeout(500); // 等待答案显示动画
  }

  /**
   * 下一个单词
   */
  async nextWord() {
    await this.nextWordButton.click();
    await this.helpers.waitForPageLoad();
  }

  /**
   * 上一个单词
   */
  async previousWord() {
    await this.previousWordButton.click();
    await this.helpers.waitForPageLoad();
  }

  /**
   * 完成一轮练习
   */
  async completePracticeRound(wordCount: number = 5) {
    for (let i = 0; i < wordCount; i++) {
      // 随机选择认识或不认识
      const isKnown = Math.random() > 0.5;
      
      if (isKnown) {
        await this.markWordAsKnown();
      } else {
        await this.showAnswer();
        await this.markWordAsUnknown();
      }
      
      // 如果不是最后一个单词，点击下一个
      if (i < wordCount - 1) {
        await this.nextWord();
      }
    }
  }

  /**
   * 验证练习页面元素
   */
  async verifyPracticePageElements() {
    await this.helpers.verifyElementVisible(this.wordCard);
    await this.helpers.verifyElementVisible(this.showAnswerButton);
    await this.helpers.verifyElementVisible(this.knownButton);
    await this.helpers.verifyElementVisible(this.unknownButton);
    await this.helpers.verifyElementVisible(this.progressBar);
  }

  /**
   * 获取当前练习进度
   */
  async getPracticeProgress() {
    const progressText = await this.progressBar.textContent();
    const scoreText = await this.scoreDisplay.textContent();
    
    return {
      progress: progressText,
      score: scoreText
    };
  }

  /**
   * 验证练习完成
   */
  async verifyPracticeCompletion() {
    // 验证练习结果页面或完成提示
    const completionMessage = this.page.locator('.practice-complete, [data-testid="practice-complete"]');
    await this.helpers.verifyElementVisible(completionMessage);
    
    // 验证最终分数显示
    const finalScore = this.page.locator('.final-score, [data-testid="final-score"]');
    await this.helpers.verifyElementVisible(finalScore);
  }

  /**
   * 创建新词典
   */
  async createDictionary(dictionaryData: {
    name: string;
    description?: string;
    language?: string;
  }) {
    await this.createDictionaryButton.click();
    
    // 填写词典信息
    await this.page.fill('input[name="name"], [data-testid="dictionary-name"]', dictionaryData.name);
    
    if (dictionaryData.description) {
      await this.page.fill('textarea[name="description"], [data-testid="dictionary-description"]', dictionaryData.description);
    }
    
    if (dictionaryData.language) {
      await this.page.selectOption('select[name="language"], [data-testid="language-selector"]', dictionaryData.language);
    }
    
    // 提交表单
    const submitButton = this.page.locator('button[type="submit"], button:has-text("创建"), button:has-text("Create")');
    await submitButton.click();
    
    await this.helpers.waitForPageLoad();
  }

  /**
   * 验证词典列表
   */
  async verifyDictionaryList() {
    await this.helpers.verifyElementVisible(this.dictionaryList);
    
    // 验证至少有一个词典项
    const dictionaryItems = this.dictionaryList.locator('.dictionary-item, [data-testid="dictionary-item"]');
    await this.helpers.verifyElementVisible(dictionaryItems.first());
  }
}