# 英语学习模块 - 智能打字练习功能集成设计

## 🎯 **项目目标**

将Qwerty Learner项目的单词拼写功能集成到alpha项目的英语学习模块中，创建"智能练习"功能，提供打字练习、数据统计等核心功能。

## 📊 **功能需求分析**

### 1. **核心功能**
- **单词拼写练习**: 实时拼写检查、错误提示、进度跟踪
- **数据统计**: WPM速度、准确率、学习进度、学习时长
- **词库管理**: 支持多种词库（CET4/6、TOEFL、GRE等）
- **个性化学习**: 根据用户水平推荐词库和练习内容
- **数据分析**: 学习数据可视化分析，包括热力图、趋势图等

### 2. **技术特性**
- **实时反馈**: 输入时即时验证拼写正确性
- **进度保存**: 学习记录持久化存储
- **数据可视化**: 学习进度图表展示
- **响应式设计**: 支持桌面端和移动端
- **数据分析**: 基于历史数据的深度分析

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

# 新增数据分析相关模型
class TypingPracticeRecord(models.Model):
    """打字练习详细记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    is_correct = models.BooleanField()
    typing_speed = models.FloatField()  # WPM
    response_time = models.FloatField()  # 响应时间(秒)
    total_time = models.FloatField()  # 总用时(毫秒)
    wrong_count = models.IntegerField(default=0)  # 错误次数
    mistakes = models.JSONField(default=dict)  # 按键错误详情
    timing = models.JSONField(default=list)  # 每个字符的输入时间
    session_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'english_typing_practice_records'
        indexes = [
            models.Index(fields=['user', 'session_date']),
            models.Index(fields=['user', 'created_at']),
        ]

class DailyPracticeStats(models.Model):
    """每日练习统计"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    exercise_count = models.IntegerField(default=0)  # 练习次数
    word_count = models.IntegerField(default=0)  # 练习单词数
    total_time = models.FloatField(default=0)  # 总用时(毫秒)
    wrong_count = models.IntegerField(default=0)  # 总错误次数
    wrong_keys = models.JSONField(default=list)  # 错误按键列表
    avg_wpm = models.FloatField(default=0)  # 平均WPM
    accuracy_rate = models.FloatField(default=0)  # 正确率

    class Meta:
        db_table = 'english_daily_practice_stats'
        unique_together = [('user', 'date')]
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

class KeyErrorStats(models.Model):
    """按键错误统计"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=10)  # 按键
    error_count = models.IntegerField(default=0)  # 错误次数
    last_error_date = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'english_key_error_stats'
        unique_together = [('user', 'key')]
        indexes = [
            models.Index(fields=['user', 'error_count']),
        ]
```

### **数据分析功能设计**

#### 1. 数据分析页面结构
```
数据分析页面
├── 页面头部
│   ├── 返回按钮
│   ├── 页面标题
│   └── 时间范围选择
├── 数据概览
│   ├── 总练习次数
│   ├── 总练习单词数
│   ├── 平均WPM
│   └── 平均正确率
└── 图表区域
    ├── 练习次数热力图
    ├── 练习单词数热力图
    ├── WPM趋势图
    ├── 正确率趋势图
    └── 按键错误分析图
```

#### 2. 数据可视化组件
- **热力图组件**：使用react-activity-calendar
- **趋势图组件**：使用ECharts或Chart.js
- **键盘错误图组件**：自定义键盘布局组件

#### 3. 数据聚合逻辑
```python
# 数据聚合服务
class DataAnalysisService:
    def get_exercise_heatmap(self, user_id, start_date, end_date):
        """获取练习次数热力图数据"""
        pass
    
    def get_word_heatmap(self, user_id, start_date, end_date):
        """获取练习单词数热力图数据"""
        pass
    
    def get_wpm_trend(self, user_id, start_date, end_date):
        """获取WPM趋势数据"""
        pass
    
    def get_accuracy_trend(self, user_id, start_date, end_date):
        """获取正确率趋势数据"""
        pass
    
    def get_key_error_stats(self, user_id):
        """获取按键错误统计"""
        pass
```

### **API接口设计**

```python
# 新增API端点
class DataAnalysisViewSet(viewsets.ModelViewSet):
    """数据分析API"""
    
    @action(detail=False, methods=['get'])
    def exercise_heatmap(self, request):
        """获取练习次数热力图数据"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        data = DataAnalysisService().get_exercise_heatmap(
            request.user.id, start_date, end_date
        )
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def word_heatmap(self, request):
        """获取练习单词数热力图数据"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        data = DataAnalysisService().get_word_heatmap(
            request.user.id, start_date, end_date
        )
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def wpm_trend(self, request):
        """获取WPM趋势数据"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        data = DataAnalysisService().get_wpm_trend(
            request.user.id, start_date, end_date
        )
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def accuracy_trend(self, request):
        """获取正确率趋势数据"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        data = DataAnalysisService().get_accuracy_trend(
            request.user.id, start_date, end_date
        )
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def key_error_stats(self, request):
        """获取按键错误统计"""
        data = DataAnalysisService().get_key_error_stats(request.user.id)
        return Response(data)
```

### **前端组件设计**

```vue
<!-- frontend/src/views/english/DataAnalysis.vue -->
<template>
  <div class="data-analysis">
    <!-- 页面头部 -->
    <div class="page-header">
      <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
      <h1>数据分析</h1>
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        @change="handleDateChange"
      />
    </div>
    
    <!-- 数据概览 -->
    <div class="data-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ overview.totalExercises }}</div>
              <div class="stat-label">总练习次数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ overview.totalWords }}</div>
              <div class="stat-label">总练习单词数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ overview.avgWpm }}</div>
              <div class="stat-label">平均WPM</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-value">{{ overview.avgAccuracy }}%</div>
              <div class="stat-label">平均正确率</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-container">
      <!-- 练习次数热力图 -->
      <el-card class="chart-card">
        <template #header>
          <span>过去一年练习次数热力图</span>
        </template>
        <HeatmapChart :data="exerciseHeatmap" />
      </el-card>
      
      <!-- 练习单词数热力图 -->
      <el-card class="chart-card">
        <template #header>
          <span>过去一年练习单词数热力图</span>
        </template>
        <HeatmapChart :data="wordHeatmap" />
      </el-card>
      
      <!-- WPM趋势图 -->
      <el-card class="chart-card">
        <template #header>
          <span>过去一年WPM趋势图</span>
        </template>
        <LineChart :data="wpmTrend" title="WPM" />
      </el-card>
      
      <!-- 正确率趋势图 -->
      <el-card class="chart-card">
        <template #header>
          <span>过去一年正确率趋势图</span>
        </template>
        <LineChart :data="accuracyTrend" title="正确率(%)" suffix="%" />
      </el-card>
      
      <!-- 按键错误分析 -->
      <el-card class="chart-card">
        <template #header>
          <span>按键错误次数排行</span>
        </template>
        <KeyboardErrorChart :data="keyErrorStats" />
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import HeatmapChart from '@/components/charts/HeatmapChart.vue'
import LineChart from '@/components/charts/LineChart.vue'
import KeyboardErrorChart from '@/components/charts/KeyboardErrorChart.vue'
import { dataAnalysisAPI } from '@/api/english'

export default {
  name: 'DataAnalysis',
  components: {
    HeatmapChart,
    LineChart,
    KeyboardErrorChart
  },
  setup() {
    const router = useRouter()
    const dateRange = ref([])
    const overview = ref({})
    const exerciseHeatmap = ref([])
    const wordHeatmap = ref([])
    const wpmTrend = ref([])
    const accuracyTrend = ref([])
    const keyErrorStats = ref([])
    
    const goBack = () => {
      router.push('/english/typing-practice')
    }
    
    const loadData = async () => {
      try {
        const [startDate, endDate] = dateRange.value || [
          new Date(Date.now() - 365 * 24 * 60 * 60 * 1000),
          new Date()
        ]
        
        const [
          exerciseData,
          wordData,
          wpmData,
          accuracyData,
          keyErrorData
        ] = await Promise.all([
          dataAnalysisAPI.getExerciseHeatmap(startDate, endDate),
          dataAnalysisAPI.getWordHeatmap(startDate, endDate),
          dataAnalysisAPI.getWpmTrend(startDate, endDate),
          dataAnalysisAPI.getAccuracyTrend(startDate, endDate),
          dataAnalysisAPI.getKeyErrorStats()
        ])
        
        exerciseHeatmap.value = exerciseData
        wordHeatmap.value = wordData
        wpmTrend.value = wpmData
        accuracyTrend.value = accuracyData
        keyErrorStats.value = keyErrorData
      } catch (error) {
        console.error('加载数据失败:', error)
      }
    }
    
    const handleDateChange = () => {
      loadData()
    }
    
    onMounted(() => {
      loadData()
    })
    
    return {
      dateRange,
      overview,
      exerciseHeatmap,
      wordHeatmap,
      wpmTrend,
      accuracyTrend,
      keyErrorStats,
      goBack,
      handleDateChange
    }
  }
}
</script>
```

## 🔧 **技术实现方案**

### 1. **数据收集策略**
- **实时记录**：每次练习时记录详细数据
- **批量聚合**：每日定时聚合统计数据
- **增量更新**：支持增量数据更新

### 2. **性能优化**
- **数据缓存**：缓存常用统计数据
- **分页加载**：大数据量时分页加载
- **异步处理**：数据聚合异步处理

### 3. **用户体验**
- **响应式设计**：适配不同屏幕尺寸
- **交互友好**：图表支持缩放、筛选等交互
- **加载状态**：显示数据加载进度

## 📈 **数据指标定义**

### 1. **练习次数**
- 定义：每日完成的练习会话数
- 计算：按session_date分组统计

### 2. **练习单词数**
- 定义：每日练习的单词总数（去重）
- 计算：按session_date分组，统计unique words

### 3. **WPM (Words Per Minute)**
- 定义：每分钟正确输入的单词数
- 计算：正确单词数 / (总用时 / 60)

### 4. **正确率**
- 定义：正确输入的字符数占总字符数的比例
- 计算：(总字符数 - 错误字符数) / 总字符数 * 100%

### 5. **按键错误**
- 定义：每个按键的错误次数统计
- 计算：按按键分组统计错误次数

## 🚀 **开发计划**

### 第一阶段：数据模型和API
1. 创建数据模型
2. 实现数据收集逻辑
3. 开发API接口

### 第二阶段：前端组件
1. 创建图表组件
2. 实现数据分析页面
3. 添加数据入口

### 第三阶段：优化和测试
1. 性能优化
2. 用户体验优化
3. 功能测试

---

*最后更新：2025-01-17*
*维护者：开发团队*




