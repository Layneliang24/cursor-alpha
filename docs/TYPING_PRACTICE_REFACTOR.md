# 智能打字练习重构文档

## 🎯 **重构目标**

参考 qwerty-learner 项目的设计风格和交互逻辑，重构本地项目的打字练习功能，实现：
- 按任意键开始练习
- 自动发音功能
- 实时拼写检查
- 自动跳转下一个单词
- 键盘声音反馈
- 词库切换功能

## 📋 **重构内容**

### 1. **前端界面重构**

#### 页面布局
- **头部区域**：显示标题、统计信息、控制按钮
- **设置区域**：练习数量、音标显示设置
- **练习区域**：单词显示、进度条、操作提示
- **完成区域**：练习结果统计

#### 交互逻辑
- **按任意键开始**：页面加载后，按任意键开始练习
- **实时状态切换**：未开始 → 练习中 → 完成
- **键盘快捷键**：
  - `Esc`：跳过当前单词
  - `Ctrl+J`：播放发音
  - 任意键：开始练习/继续打字

### 2. **发音系统重构**

#### 有道词典API集成
```javascript
// 发音URL生成
const PRONUNCIATION_API = 'https://dict.youdao.com/dictvoice?audio='
function generateWordSoundSrc(word, pronunciationType = 'us') {
  switch (pronunciationType) {
    case 'uk':
      return `${PRONUNCIATION_API}${encodeURIComponent(word)}&type=1`
    case 'us':
    default:
      return `${PRONUNCIATION_API}${encodeURIComponent(word)}&type=2`
  }
}
```

#### 自动发音功能
- 开始练习时自动播放第一个单词发音
- 切换单词时自动播放新单词发音
- 支持手动播放发音（Ctrl+J）

### 3. **声音系统重构**

#### 本地音频文件
- **按键音**：`/sounds/key-sound/key-default.wav`
- **正确音**：`/sounds/correct.wav`
- **错误音**：`/sounds/beep.wav`

#### 声音反馈
- 输入正确字母时播放按键音
- 完成单词时播放正确音
- 输入错误时播放错误音

### 4. **状态管理优化**

#### 练习状态
- `practiceStarted`：练习是否已开始
- `isTyping`：是否正在打字
- `practiceCompleted`：练习是否完成

#### 单词状态
- `wordState.displayWord`：显示单词
- `wordState.inputWord`：用户输入
- `wordState.letterStates`：字母状态（normal/correct/wrong）

### 5. **词库管理**

#### 支持的词库
- **CET4_T**：大学英语四级
- **CET6_T**：大学英语六级
- **TOEFL_3_T**：托福词汇
- **GRE_3_T**：GRE词汇

#### 难度设置
- **beginner**：初级
- **intermediate**：中级
- **advanced**：高级

## 🔧 **技术实现**

### 1. **发音Hook (`usePronunciation.js`)**
```javascript
export default function usePronunciation(word, pronunciationType = 'us') {
  const play = () => {
    // 使用有道词典API播放发音
  }
  
  const preload = () => {
    // 预加载音频文件
  }
  
  return { play, stop, isPlaying, preload }
}
```

### 2. **键盘声音Hook (`useKeySounds.js`)**
```javascript
export default function useKeySounds() {
  const playKeySound = () => {
    // 播放按键音
  }
  
  const playCorrectSound = () => {
    // 播放正确音
  }
  
  const playWrongSound = () => {
    // 播放错误音
  }
  
  return { playKeySound, playCorrectSound, playWrongSound }
}
```

### 3. **状态管理 (`typing.js`)**
```javascript
const handleKeyInput = (key) => {
  // 处理键盘输入
  // 更新字母状态
  // 播放相应声音
  // 检查完成状态
}
```

## 🎨 **界面设计**

### 设计风格
- **渐变背景**：蓝紫色渐变
- **卡片布局**：圆角卡片，半透明背景
- **响应式设计**：适配不同屏幕尺寸

### 交互反馈
- **字母状态**：正确变绿，错误变红
- **进度显示**：实时进度条
- **声音反馈**：按键音、正确音、错误音

## 📁 **文件结构**

```
frontend/src/
├── views/english/
│   └── TypingPractice.vue          # 主组件
├── stores/
│   └── typing.js                   # 状态管理
├── hooks/
│   ├── usePronunciation.js         # 发音Hook
│   └── useKeySounds.js             # 键盘声音Hook
├── components/typing/
│   └── Letter.vue                  # 字母组件
└── public/sounds/                  # 音频文件
    ├── key-sound/
    │   └── key-default.wav
    ├── correct.wav
    └── beep.wav
```

## 🚀 **使用方法**

### 1. **启动项目**
```bash
# 启动后端
cd backend && python manage.py runserver 8000

# 启动前端
cd frontend && npm run dev
```

### 2. **访问功能**
1. 访问英语学习模块
2. 点击"智能练习" → "智能打字练习"
3. 按任意键开始练习

### 3. **操作说明**
- **按任意键**：开始练习
- **输入字母**：实时拼写检查
- **Esc键**：跳过当前单词
- **Ctrl+J**：播放发音
- **切换词库**：随时更换词库和难度

## ✅ **功能特性**

### ✅ **已实现功能**
- [x] 按任意键开始练习
- [x] 自动发音功能
- [x] 实时拼写检查
- [x] 自动跳转下一个单词
- [x] 键盘声音反馈
- [x] 词库切换功能
- [x] 难度设置
- [x] 进度显示
- [x] 练习统计

### 🔄 **待优化功能**
- [ ] 更多词库支持
- [ ] 自定义声音设置
- [ ] 练习历史记录
- [ ] 成绩排行榜
- [ ] 移动端适配

## 📊 **性能优化**

### 1. **音频预加载**
- 预加载下一个单词的发音
- 减少播放延迟

### 2. **状态管理**
- 使用响应式状态管理
- 避免不必要的重新渲染

### 3. **错误处理**
- 音频播放失败时的降级处理
- 网络请求失败时的重试机制

## 🎯 **总结**

通过本次重构，智能打字练习功能已经实现了与 qwerty-learner 类似的核心功能：

1. **用户体验**：流畅的键盘交互，即时的视觉和声音反馈
2. **功能完整**：支持词库切换、难度设置、自动发音
3. **技术先进**：使用有道词典API、本地音频文件、响应式设计
4. **可扩展性**：模块化设计，易于添加新功能

重构后的打字练习功能为用户提供了专业、流畅的英语学习体验。


