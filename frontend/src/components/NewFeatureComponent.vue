

```vue
<template>
  <div class="practice-container">
    <h2>{{ currentWord.word }}</h2>
    <div class="input-area">
      <input
        v-model="userInput"
        @keyup.enter="submitAnswer"
        placeholder="输入单词的正确拼写"
        class="practice-input"
      />
      <button @click="submitAnswer" class="submit-btn">提交</button>
    </div>
    <div v-if="showFeedback" class="feedback">
      <p v-if="isCorrect" class="correct">正确！{{ currentWord.word }} 的拼写正确。</p>
      <p v-else class="incorrect">错误！正确拼写是：{{ currentWord.word }}</p>
    </div>
    <button @click="nextWord" class="next-btn">下一题</button>
  </div>
</template>

<script>
export default {
  name: "WordSpellingPractice",
  data() {
    return {
      wordsList: [
        { word: "accommodation" },
        { word: "occurrence" },
        { word: "necessary" },
        { word: "separate" },
        { word: "library" },
      ],
      currentWordIndex: 0,
      userInput: "",
      showFeedback: false,
      isCorrect: false,
    };
  },
  computed: {
    currentWord() {
      return this.wordsList[this.currentWordIndex] || { word: "" };
    },
  },
  methods: {
    submitAnswer() {
      if (this.userInput.trim().toLowerCase() === this.currentWord.word.toLowerCase()) {
        this.isCorrect = true;
      } else {
        this.isCorrect = false;
      }
      this.showFeedback = true;
    },
    nextWord() {
      this.currentWordIndex++;
      this.userInput = "";
      this.showFeedback = false;
      this.isCorrect = false;
    },
  },
};
</script>

<style scoped>
.practice-container {
  max-width: 600px;
  margin: 2rem auto;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.input-area {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.practice-input {
  flex: 1;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.submit-btn {
  padding: 10px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-btn:hover {
  background-color: #45a049;
}

.feedback {
  margin: 15px 0;
  padding: 10px;
  border-radius: 4px;
}

.correct {
  color: #155724;
  background-color: #d4edda;
}

.incorrect {
  color: #721c24;
  background-color: #f8d7da;
}

.next-btn {
  display: block;
  margin: 20px auto;
  padding: 10px 30px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.next-btn:hover {
  background-color: #218838;
}
</style>
```

### 代码说明：

1. **组件结构**：
   - 包含单词展示区域、输入框、提交按钮和反馈提示
   - 使用 flex 布局实现输入框和按钮的水平排列
   - 提供"下一题"按钮切换题目

2. **核心功能**：
   - 自动加载预设的易错单词列表
   - 实时输入监听和提交验证
   - 及时反馈机制（正确/错误提示）
   - 题目切换功能

3. **样式设计**：
   - 采用 Material Design 风格的按钮样式
   - 正确/错误反馈使用不同颜色方案
   - 完整的阴影和圆角设计提升视觉层次

4. **数据管理**：
   - 使用计算属性获取当前题目
   - 维护题目索引、用户输入和反馈状态
   - 提供 nextWord 方法处理题目切换逻辑

5. **交互优化**：
   - 回车键触发提交
   - 状态重置机制确保题目间独立性
   - 清晰的视觉反馈帮助用户理解进度

这个组件可以作为单词拼写练习的基础实现，可以根据具体需求：
- 添加更多单词到 wordsList
- 增加计分系统
- 添加定时器
- 集成 API 获取动态题目
- 增加发音提示功能
- 实现更复杂的数据跟踪等