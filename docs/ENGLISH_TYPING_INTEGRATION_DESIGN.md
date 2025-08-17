# 英语学习模块 - 智能打字练习功能集成设计

## 🎯 **项目目标**

将Qwerty Learner项目的单词拼写功能集成到alpha项目的英语学习模块中，创建"智能练习"功能，提供打字练习、数据统计等核心功能。

## 📊 **功能需求分析**

### 1. **核心功能**
- **单词拼写练习**: 实时拼写检查、错误提示、进度跟踪
- **数据统计**: WPM速度、准确率、学习进度、学习时长
- **词库管理**: 支持多种词库（CET4/6、TOEFL、GRE等）
- **个性化学习**: 根据用户水平推荐词库和练习内容

### 2. **技术特性**
- **实时反馈**: 输入时即时验证拼写正确性
- **进度保存**: 学习记录持久化存储
- **数据可视化**: 学习进度图表展示
- **响应式设计**: 支持桌面端和移动端

## 🏗 **系统架构设计**

### **数据模型设计**

```python
# 新增模型
class Word(models.Model):
    """单词模型"""
    word = models.CharField(max_length=100, unique=True)
    translation = models.CharField(max_length=200)
    phonetic = models.CharField(max_length=100, blank=True)
    difficulty = models.CharField(max_length=20, choices=[
        ('beginner', '初级'),
        ('intermediate', '中级'),
        ('advanced', '高级')
    ])
    category = models.CharField(max_length=50)  # CET4, TOEFL, GRE等
    frequency = models.IntegerField(default=0)  # 词频
    created_at = models.DateTimeField(auto_now_add=True)

class TypingSession(models.Model):
    """打字练习会话"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    is_correct = models.BooleanField()
    typing_speed = models.FloatField()  # WPM
    response_time = models.FloatField()  # 响应时间(秒)
    session_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

class UserTypingStats(models.Model):
    """用户打字统计"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_words_practiced = models.IntegerField(default=0)
    total_correct_words = models.IntegerField(default=0)
    average_wpm = models.FloatField(default=0.0)
    total_practice_time = models.IntegerField(default=0)  # 分钟
    last_practice_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### **API接口设计**

```python
# 新增API端点
class TypingPracticeViewSet(viewsets.ModelViewSet):
    """打字练习API"""
    
    @action(detail=False, methods=['get'])
    def get_word_list(self, request):
        """获取练习单词列表"""
        category = request.query_params.get('category', 'CET4')
        difficulty = request.query_params.get('difficulty', 'intermediate')
        limit = int(request.query_params.get('limit', 50))
        
        words = Word.objects.filter(
            category=category,
            difficulty=difficulty
        ).order_by('?')[:limit]
        
        return Response(WordSerializer(words, many=True).data)
    
    @action(detail=False, methods=['post'])
    def submit_result(self, request):
        """提交练习结果"""
        word_id = request.data.get('word_id')
        is_correct = request.data.get('is_correct')
        typing_speed = request.data.get('typing_speed', 0)
        response_time = request.data.get('response_time', 0)
        
        # 保存练习记录
        TypingSession.objects.create(
            user=request.user,
            word_id=word_id,
            is_correct=is_correct,
            typing_speed=typing_speed,
            response_time=response_time
        )
        
        # 更新用户统计
        self.update_user_stats(request.user, is_correct, typing_speed)
        
        return Response({'status': 'success'})
    
    @action(detail=False, methods=['get'])
    def get_statistics(self, request):
        """获取用户统计信息"""
        stats = UserTypingStats.objects.get_or_create(user=request.user)[0]
        return Response(UserTypingStatsSerializer(stats).data)
    
    @action(detail=False, methods=['get'])
    def get_daily_progress(self, request):
        """获取每日学习进度"""
        days = int(request.query_params.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        daily_stats = TypingSession.objects.filter(
            user=request.user,
            session_date__range=[start_date, end_date]
        ).values('session_date').annotate(
            total_words=Count('id'),
            correct_words=Count('id', filter=Q(is_correct=True)),
            avg_wpm=Avg('typing_speed')
        ).order_by('session_date')
        
        return Response(daily_stats)
```

## 🔄 **数据导入流程**

### **1. 词库导入脚本**

```python
# backend/apps/english/management/commands/import_qwerty_dicts.py
from django.core.management.base import BaseCommand
import json
import os
from apps.english.models import Word

class Command(BaseCommand):
    help = '从Qwerty Learner项目导入词库数据'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dicts-path',
            type=str,
            default='../qwerty-learner/public/dicts',
            help='Qwerty Learner词库文件路径'
        )
        parser.add_argument(
            '--categories',
            nargs='+',
            default=['CET4', 'CET6', 'TOEFL', 'GRE', 'IELTS'],
            help='要导入的词库类别'
        )
    
    def handle(self, *args, **options):
        dicts_path = options['dicts_path']
        categories = options['categories']
        
        for category in categories:
            dict_file = os.path.join(dicts_path, f'{category}.json')
            if os.path.exists(dict_file):
                self.import_dict_file(dict_file, category)
            else:
                self.stdout.write(
                    self.style.WARNING(f'词库文件不存在: {dict_file}')
                )
    
    def import_dict_file(self, file_path, category):
        """导入单个词库文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            words_data = json.load(f)
        
        imported_count = 0
        for word_data in words_data:
            word, created = Word.objects.get_or_create(
                word=word_data['word'],
                defaults={
                    'translation': word_data.get('trans', ''),
                    'phonetic': word_data.get('phonetic', ''),
                    'category': category,
                    'difficulty': self.determine_difficulty(word_data),
                    'frequency': word_data.get('frequency', 0)
                }
            )
            if created:
                imported_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'成功导入 {category} 词库: {imported_count} 个新单词'
            )
        )
    
    def determine_difficulty(self, word_data):
        """根据单词特征确定难度"""
        word = word_data['word']
        frequency = word_data.get('frequency', 0)
        
        if len(word) <= 4 or frequency > 1000:
            return 'beginner'
        elif len(word) <= 8 or frequency > 500:
            return 'intermediate'
        else:
            return 'advanced'
```

### **2. 前端组件设计**

```vue
<!-- frontend/src/views/english/TypingPractice.vue -->
<template>
  <div class="typing-practice">
    <!-- 顶部统计栏 -->
    <div class="stats-header">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ stats.totalWords }}</div>
              <div class="stat-label">总练习单词</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ stats.accuracy }}%</div>
              <div class="stat-label">准确率</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ stats.avgWpm }}</div>
              <div class="stat-label">平均WPM</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ stats.practiceTime }}分钟</div>
              <div class="stat-label">练习时长</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 练习区域 -->
    <div class="practice-area">
      <el-card>
        <div class="word-display">
          <h2 class="word-text">{{ currentWord.word }}</h2>
          <p class="word-phonetic">[{{ currentWord.phonetic }}]</p>
          <p class="word-translation">{{ currentWord.translation }}</p>
        </div>
        
        <div class="input-section">
          <el-input
            v-model="userInput"
            placeholder="请输入单词..."
            @input="handleInput"
            @keydown.enter="submitAnswer"
            :class="inputClass"
            size="large"
            ref="wordInput"
          />
        </div>
        
        <div class="feedback-section" v-if="showFeedback">
          <el-alert
            :title="feedbackMessage"
            :type="feedbackType"
            show-icon
          />
        </div>
      </el-card>
    </div>
    
    <!-- 控制面板 -->
    <div class="control-panel">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-select v-model="selectedCategory" placeholder="选择词库">
            <el-option label="CET4" value="CET4" />
            <el-option label="CET6" value="CET6" />
            <el-option label="TOEFL" value="TOEFL" />
            <el-option label="GRE" value="GRE" />
            <el-option label="IELTS" value="IELTS" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-select v-model="selectedDifficulty" placeholder="选择难度">
            <el-option label="初级" value="beginner" />
            <el-option label="中级" value="intermediate" />
            <el-option label="高级" value="advanced" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-button type="primary" @click="startPractice">开始练习</el-button>
          <el-button @click="pausePractice">暂停</el-button>
        </el-col>
      </el-row>
    </div>
    
    <!-- 进度图表 -->
    <div class="charts-section">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <div class="chart-title">每日学习进度</div>
            <div ref="dailyChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <div class="chart-title">WPM趋势</div>
            <div ref="wpmChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useTypingStore } from '@/stores/typing'
import * as echarts from 'echarts'

// 状态管理
const typingStore = useTypingStore()
const userInput = ref('')
const currentWord = ref({})
const showFeedback = ref(false)
const feedbackMessage = ref('')
const feedbackType = ref('info')
const selectedCategory = ref('CET4')
const selectedDifficulty = ref('intermediate')

// 计算属性
const inputClass = computed(() => {
  if (!showFeedback.value) return ''
  return feedbackType.value === 'success' ? 'correct-input' : 'incorrect-input'
})

const stats = computed(() => typingStore.userStats)

// 方法
const handleInput = () => {
  showFeedback.value = false
}

const submitAnswer = async () => {
  const isCorrect = userInput.value.toLowerCase() === currentWord.value.word.toLowerCase()
  const responseTime = typingStore.getResponseTime()
  
  // 更新反馈
  showFeedback.value = true
  feedbackType.value = isCorrect ? 'success' : 'error'
  feedbackMessage.value = isCorrect ? '拼写正确！' : `正确答案: ${currentWord.value.word}`
  
  // 提交结果
  await typingStore.submitResult({
    word_id: currentWord.value.id,
    is_correct: isCorrect,
    response_time: responseTime
  })
  
  // 清空输入
  userInput.value = ''
  
  // 延迟后进入下一题
  setTimeout(() => {
    nextWord()
  }, 1500)
}

const nextWord = async () => {
  showFeedback.value = false
  currentWord.value = await typingStore.getNextWord()
  typingStore.startTimer()
  // 聚焦输入框
  nextTick(() => {
    document.querySelector('.word-input').focus()
  })
}

const startPractice = async () => {
  await typingStore.startSession({
    category: selectedCategory.value,
    difficulty: selectedDifficulty.value
  })
  nextWord()
}

// 图表初始化
onMounted(() => {
  initCharts()
})

const initCharts = () => {
  // 初始化ECharts图表
  const dailyChart = echarts.init(document.querySelector('#dailyChart'))
  const wpmChart = echarts.init(document.querySelector('#wpmChart'))
  
  // 配置图表选项...
}
</script>

<style scoped>
.typing-practice {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.stats-header {
  margin-bottom: 30px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.practice-area {
  margin-bottom: 30px;
}

.word-display {
  text-align: center;
  margin-bottom: 30px;
}

.word-text {
  font-size: 48px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 10px;
}

.word-phonetic {
  font-size: 18px;
  color: #666;
  margin-bottom: 10px;
}

.word-translation {
  font-size: 16px;
  color: #999;
}

.input-section {
  margin-bottom: 20px;
}

.correct-input {
  border-color: #67c23a;
}

.incorrect-input {
  border-color: #f56c6c;
}

.control-panel {
  margin-bottom: 30px;
}

.charts-section {
  margin-top: 30px;
}

.chart-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 15px;
}
</style>
```

## 📊 **状态管理设计**

```javascript
// frontend/src/stores/typing.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/english'

export const useTypingStore = defineStore('typing', () => {
  // 状态
  const currentSession = ref(null)
  const wordList = ref([])
  const currentIndex = ref(0)
  const sessionStartTime = ref(null)
  const userStats = ref({
    totalWords: 0,
    correctWords: 0,
    accuracy: 0,
    avgWpm: 0,
    practiceTime: 0
  })
  
  // 计算属性
  const currentWord = computed(() => {
    return wordList.value[currentIndex.value] || {}
  })
  
  const progress = computed(() => {
    return wordList.value.length > 0 
      ? Math.round((currentIndex.value / wordList.value.length) * 100)
      : 0
  })
  
  // 方法
  const startSession = async (params) => {
    try {
      const response = await api.getTypingWordList(params)
      wordList.value = response.data
      currentIndex.value = 0
      sessionStartTime.value = Date.now()
      
      // 获取用户统计
      await loadUserStats()
    } catch (error) {
      console.error('启动练习会话失败:', error)
      throw error
    }
  }
  
  const getNextWord = async () => {
    if (currentIndex.value >= wordList.value.length - 1) {
      // 获取更多单词
      await loadMoreWords()
    }
    
    currentIndex.value++
    return currentWord.value
  }
  
  const submitResult = async (result) => {
    try {
      await api.submitTypingResult(result)
      
      // 更新本地统计
      userStats.value.totalWords++
      if (result.is_correct) {
        userStats.value.correctWords++
      }
      userStats.value.accuracy = Math.round(
        (userStats.value.correctWords / userStats.value.totalWords) * 100
      )
      
      // 更新用户统计
      await loadUserStats()
    } catch (error) {
      console.error('提交练习结果失败:', error)
      throw error
    }
  }
  
  const loadUserStats = async () => {
    try {
      const response = await api.getTypingStatistics()
      userStats.value = response.data
    } catch (error) {
      console.error('加载用户统计失败:', error)
    }
  }
  
  const loadMoreWords = async () => {
    // 实现加载更多单词的逻辑
  }
  
  const getResponseTime = () => {
    if (!sessionStartTime.value) return 0
    return (Date.now() - sessionStartTime.value) / 1000
  }
  
  const startTimer = () => {
    sessionStartTime.value = Date.now()
  }
  
  return {
    // 状态
    currentSession,
    wordList,
    currentIndex,
    userStats,
    
    // 计算属性
    currentWord,
    progress,
    
    // 方法
    startSession,
    getNextWord,
    submitResult,
    loadUserStats,
    getResponseTime,
    startTimer
  }
})
```

## 🔧 **API接口扩展**

```javascript
// frontend/src/api/english.js
// 在现有文件中添加打字练习相关API

// 获取打字练习单词列表
export const getTypingWordList = (params) => {
  return request.get('/api/v1/english/typing-practice/words/', { params })
}

// 提交打字练习结果
export const submitTypingResult = (data) => {
  return request.post('/api/v1/english/typing-practice/submit/', data)
}

// 获取用户打字统计
export const getTypingStatistics = () => {
  return request.get('/api/v1/english/typing-practice/statistics/')
}

// 获取每日学习进度
export const getDailyProgress = (params) => {
  return request.get('/api/v1/english/typing-practice/daily-progress/', { params })
}
```

## 📈 **数据可视化**

### **学习进度图表**
- **每日练习单词数**: 柱状图显示每日练习的单词数量
- **准确率趋势**: 折线图显示准确率变化趋势
- **WPM速度**: 折线图显示打字速度提升情况
- **学习时长**: 饼图显示不同词库的学习时间分布

### **成就系统**
- **连续练习天数**: 连续练习奖励
- **速度里程碑**: WPM达到特定值时的成就
- **词库完成度**: 完成特定词库的成就
- **准确率提升**: 准确率提升的成就

## 🎯 **集成优势**

1. **无缝集成**: 利用现有的用户系统和认证
2. **数据持久化**: 学习记录保存在数据库中
3. **个性化推荐**: 根据用户水平推荐合适的词库
4. **社交功能**: 可以添加排行榜和好友挑战
5. **移动端适配**: 响应式设计支持手机端练习
6. **不影响现有功能**: 独立模块，不影响新闻爬取等功能

## 📋 **实施计划**

### **第一阶段: 数据导入**
1. 创建数据模型
2. 编写词库导入脚本
3. 导入Qwerty Learner词库数据

### **第二阶段: 后端开发**
1. 实现API接口
2. 编写数据统计逻辑
3. 添加用户进度跟踪

### **第三阶段: 前端开发**
1. 创建打字练习组件
2. 实现状态管理
3. 添加数据可视化

### **第四阶段: 测试优化**
1. 功能测试
2. 性能优化
3. 用户体验优化

这个设计方案可以充分利用Qwerty Learner的优秀功能，同时保持alpha项目的独立性和完整性。




