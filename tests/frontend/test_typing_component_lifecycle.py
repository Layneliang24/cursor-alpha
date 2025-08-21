#!/usr/bin/env python
"""
打字练习组件生命周期测试脚本

测试问题：进度条在组件首次加载时不显示，需要路由切换后才显示
"""

import requests
import json
import time
from typing import Dict, Any

class TypingComponentLifecycleTester:
    """打字练习组件生命周期测试器"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_component_initialization(self):
        """测试组件初始化"""
        print("🔍 测试组件初始化...")
        
        # 模拟前端页面加载流程
        test_steps = [
            {
                "step": "1. 页面首次加载",
                "description": "TypingPractice 组件挂载",
                "expected_state": {
                    "words": "[] (空数组)",
                    "practiceStarted": "false",
                    "practiceCompleted": "false",
                    "currentWordIndex": "0",
                    "progressBarVisible": "false (因为 practiceStarted=false)"
                }
            },
            {
                "step": "2. 选择词库和章节",
                "description": "用户选择测试词典第1章",
                "expected_state": {
                    "words": "[] (仍然为空，因为还没开始练习)",
                    "practiceStarted": "false",
                    "practiceCompleted": "false",
                    "currentWordIndex": "0",
                    "progressBarVisible": "false (因为 practiceStarted=false)"
                }
            },
            {
                "step": "3. 按任意键开始练习",
                "description": "调用 startPracticeWithDictionary",
                "expected_state": {
                    "words": "[5个单词] (从API获取)",
                    "practiceStarted": "true",
                    "practiceCompleted": "false",
                    "currentWordIndex": "0",
                    "progressBarVisible": "true (因为所有条件都满足)"
                }
            },
            {
                "step": "4. 路由切换到其他页面",
                "description": "用户导航到其他页面",
                "expected_state": {
                    "words": "[5个单词] (保持状态)",
                    "practiceStarted": "true",
                    "practiceCompleted": "false",
                    "currentWordIndex": "0",
                    "progressBarVisible": "true (状态保持)"
                }
            },
            {
                "step": "5. 返回练习页面",
                "description": "用户返回 TypingPractice 页面",
                "expected_state": {
                    "words": "[5个单词] (从store恢复)",
                    "practiceStarted": "true",
                    "practiceCompleted": "false",
                    "currentWordIndex": "0",
                    "progressBarVisible": "true (应该立即显示)"
                }
            }
        ]
        
        print("📋 测试步骤分析:")
        for step in test_steps:
            print(f"\n{step['step']}: {step['description']}")
            print("   预期状态:")
            for key, value in step['expected_state'].items():
                print(f"     {key}: {value}")
        
        return test_steps
    
    def analyze_vue_lifecycle(self):
        """分析 Vue 组件生命周期"""
        print("\n🔍 Vue 组件生命周期分析...")
        
        print("""
Vue 3 Composition API 生命周期钩子：

1. **setup()** - 组件初始化时执行
   - 创建响应式状态
   - 定义计算属性和方法
   - 设置 watch 和 computed

2. **onMounted()** - DOM 挂载完成后执行
   - 可以访问 DOM 元素
   - 适合进行异步操作
   - 当前问题可能在这里

3. **onUnmounted()** - 组件卸载时执行
   - 清理定时器、事件监听器等

4. **onActivated()** - 被 keep-alive 缓存的组件激活时执行
   - 路由切换返回时触发
   - 这可能是进度条显示的原因

5. **onDeactivated()** - 被 keep-alive 缓存的组件停用时执行
        """)
        
        print("""
问题分析：

**根本原因**：进度条在组件首次加载时不显示，但在路由切换后显示

**可能原因**：
1. **组件挂载时机问题**
   - onMounted 中状态可能未正确初始化
   - 异步数据获取时机不对

2. **状态同步问题**
   - useTypingStore 的状态在组件首次渲染时可能为空
   - computed 属性没有正确响应初始状态

3. **路由切换触发重新挂载**
   - 从其他页面返回时，组件可能被重新挂载
   - 此时 store 状态已经存在，所以进度条显示正常

4. **条件渲染逻辑问题**
   - v-if 条件在首次渲染时可能为 false
   - 状态更新后没有触发重新渲染
        """)
    
    def suggest_solutions(self):
        """建议解决方案"""
        print("\n💡 建议解决方案...")
        
        print("""
**解决方案 1：改进组件初始化**

在 onMounted 中添加状态检查和初始化：

```javascript
onMounted(async () => {
  // 现有代码...
  
  // 检查并恢复练习状态
  if (typingStore.practiceStarted && !typingStore.practiceCompleted && typingStore.words.length > 0) {
    console.log('检测到未完成的练习，恢复状态...')
    // 强制触发响应式更新
    await nextTick()
  }
  
  // 添加状态监听
  watch(() => [typingStore.words, typingStore.practiceStarted], ([words, started]) => {
    if (words && words.length > 0 && started) {
      console.log('练习状态已就绪，进度条应该显示')
    }
  }, { immediate: true })
})
```

**解决方案 2：优化进度条显示逻辑**

使用 v-show 替代 v-if，并添加加载状态：

```vue
<!-- 进度条 -->
<div class="progress-section" v-show="shouldShowProgressBar">
  <div class="progress-bar">
    <div class="progress-fill" :style="{ width: progressBarWidth + '%' }"></div>
  </div>
  <div class="progress-text">{{ progressBarText }}</div>
</div>

<script>
// 计算属性
const shouldShowProgressBar = computed(() => {
  const hasWords = typingStore.words && typingStore.words.length > 0
  const isPracticeActive = typingStore.practiceStarted && !typingStore.practiceCompleted
  return hasWords && isPracticeActive
})
</script>
```

**解决方案 3：添加状态持久化**

在 store 中添加状态恢复逻辑：

```javascript
// 在 useTypingStore 中
const restorePracticeState = () => {
  // 从 localStorage 或其他地方恢复状态
  const savedState = localStorage.getItem('typingPracticeState')
  if (savedState) {
    const state = JSON.parse(savedState)
    words.value = state.words || []
    practiceStarted.value = state.practiceStarted || false
    currentWordIndex.value = state.currentWordIndex || 0
    // ... 其他状态
  }
}

// 在组件挂载时调用
onMounted(() => {
  restorePracticeState()
})
```

**解决方案 4：使用 onActivated 钩子**

如果使用了 keep-alive，在 onActivated 中处理状态恢复：

```javascript
onActivated(() => {
  console.log('组件被激活，检查练习状态...')
  if (typingStore.practiceStarted && !typingStore.practiceCompleted) {
    console.log('恢复练习状态...')
    // 强制更新进度条
    nextTick(() => {
      // 触发响应式更新
    })
  }
})
```
        """)
    
    def create_debug_script(self):
        """创建调试脚本"""
        print("\n🐛 创建调试脚本...")
        
        debug_script = """
// 在 TypingPractice.vue 中添加的调试代码

// 1. 在 setup 函数开始处添加
console.log('=== TypingPractice 组件 setup 开始 ===')
console.log('初始 store 状态:', {
  words: typingStore.words,
  practiceStarted: typingStore.practiceStarted,
  practiceCompleted: typingStore.practiceCompleted,
  currentWordIndex: typingStore.currentWordIndex
})

// 2. 在 onMounted 中添加
onMounted(async () => {
  console.log('=== TypingPractice 组件 onMounted ===')
  console.log('挂载时 store 状态:', {
    words: typingStore.words,
    practiceStarted: typingStore.practiceStarted,
    practiceCompleted: typingStore.practiceCompleted,
    currentWordIndex: typingStore.currentWordIndex
  })
  
  // 延迟检查
  setTimeout(() => {
    console.log('延迟检查 store 状态:', {
      words: typingStore.words,
      practiceStarted: typingStore.practiceStarted,
      practiceCompleted: typingStore.practiceCompleted,
      currentWordIndex: typingStore.currentWordIndex
    })
  }, 1000)
})

// 3. 添加状态变化监听
watch(() => [typingStore.words, typingStore.practiceStarted, typingStore.practiceCompleted], 
  ([words, started, completed]) => {
    console.log('=== Store 状态变化 ===', {
      words: words,
      wordsLength: words?.length,
      practiceStarted: started,
      practiceCompleted: completed,
      shouldShowProgressBar: words && words.length > 0 && started && !completed
    })
  }, 
  { immediate: true, deep: true }
)

// 4. 在进度条计算属性中添加日志
const shouldShowProgressBar = computed(() => {
  const hasWords = typingStore.words && typingStore.words.length > 0
  const isPracticeActive = typingStore.practiceStarted && !typingStore.practiceCompleted
  const result = hasWords && isPracticeActive
  
  console.log('进度条显示条件计算:', {
    hasWords,
    isPracticeActive,
    result,
    words: typingStore.words,
    wordsLength: typingStore.words?.length,
    practiceStarted: typingStore.practiceStarted,
    practiceCompleted: typingStore.practiceCompleted
  })
  
  return result
})
"""
        
        print("📝 调试脚本内容:")
        print(debug_script)
        
        # 保存到文件
        with open('debug_typing_component.js', 'w', encoding='utf-8') as f:
            f.write(debug_script)
        
        print("✅ 调试脚本已保存到 debug_typing_component.js")
    
    def run_tests(self):
        """运行所有测试"""
        print("🚀 开始打字练习组件生命周期测试...")
        print("=" * 70)
        
        # 测试组件初始化
        test_steps = self.test_component_initialization()
        
        # 分析 Vue 生命周期
        self.analyze_vue_lifecycle()
        
        # 建议解决方案
        self.suggest_solutions()
        
        # 创建调试脚本
        self.create_debug_script()
        
        print("\n" + "=" * 70)
        print("✅ 测试完成！")
        print("\n📝 下一步建议：")
        print("1. 在前端组件中添加调试代码")
        print("2. 检查组件生命周期钩子中的状态")
        print("3. 验证 useTypingStore 的状态同步")
        print("4. 测试路由切换时的组件行为")
        print("5. 使用浏览器开发者工具监控状态变化")

def main():
    """主函数"""
    tester = TypingComponentLifecycleTester()
    tester.run_tests()

if __name__ == "__main__":
    main()
