<template>
  <div class="expressions-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>地道表达</h1>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData" :loading="expressionsLoading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 筛选器 -->
    <el-card class="filter-card">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索表达..."
            @input="handleSearch"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="categoryFilter" placeholder="选择分类" @change="handleFilter" clearable>
            <el-option label="全部分类" value="" />
            <el-option label="日常对话" value="daily" />
            <el-option label="商务英语" value="business" />
            <el-option label="学术英语" value="academic" />
            <el-option label="旅行" value="travel" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="difficultyFilter" placeholder="难度等级" @change="handleFilter" clearable>
            <el-option label="全部难度" value="" />
            <el-option label="初级" value="beginner" />
            <el-option label="中级" value="intermediate" />
            <el-option label="高级" value="advanced" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="frequencyFilter" placeholder="使用频率" @change="handleFilter" clearable>
            <el-option label="全部频率" value="" />
            <el-option label="高频" value="high" />
            <el-option label="中频" value="medium" />
            <el-option label="低频" value="low" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <!-- 表达列表 -->
    <div class="expressions-list" v-loading="expressionsLoading">
      <div v-if="expressions.length === 0 && !expressionsLoading" class="empty-state">
        <el-empty description="暂无地道表达数据">
          <el-button type="primary" @click="refreshData">刷新数据</el-button>
        </el-empty>
      </div>
      
      <div v-else class="expressions-grid">
        <el-card 
          v-for="expression in expressions" 
          :key="expression.id" 
          class="expression-card"
          shadow="hover"
        >
          <div class="expression-header">
            <h3 class="expression-text">{{ expression.expression }}</h3>
            <div class="expression-tags">
              <el-tag 
                :type="getDifficultyType(expression.difficulty_level)" 
                size="small"
              >
                {{ getDifficultyLabel(expression.difficulty_level) }}
              </el-tag>
              <el-tag 
                :type="getFrequencyType(expression.usage_frequency)" 
                size="small"
              >
                {{ getFrequencyLabel(expression.usage_frequency) }}
              </el-tag>
            </div>
          </div>

          <div class="expression-content">
            <div class="meaning" v-if="expression.meaning">
              <h4>含义</h4>
              <p>{{ expression.meaning }}</p>
            </div>

            <div class="category-scenario" v-if="expression.category || expression.scenario">
              <el-row :gutter="10">
                <el-col :span="12" v-if="expression.category">
                  <div class="info-item">
                    <strong>分类:</strong> {{ getCategoryLabel(expression.category) }}
                  </div>
                </el-col>
                <el-col :span="12" v-if="expression.scenario">
                  <div class="info-item">
                    <strong>场景:</strong> {{ getScenarioLabel(expression.scenario) }}
                  </div>
                </el-col>
              </el-row>
            </div>

            <div class="usage-examples" v-if="expression.usage_examples">
              <h4>使用示例</h4>
              <p class="examples-text">{{ expression.usage_examples }}</p>
            </div>

            <div class="cultural-background" v-if="expression.cultural_background">
              <h4>文化背景</h4>
              <p class="background-text">{{ expression.cultural_background }}</p>
            </div>
          </div>

          <div class="expression-actions">
            <el-button size="small" @click="playAudio(expression)" :disabled="!expression.audio_url">
              <el-icon><VideoPlay /></el-icon>
              播放发音
            </el-button>
            <el-button size="small" type="primary" @click="addToCollection(expression)">
              <el-icon><Star /></el-icon>
              收藏
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-container" v-if="expressions.length > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 36, 48]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useEnglishStore } from '@/stores/english'
import { ElMessage } from 'element-plus'
import { Refresh, Search, VideoPlay, Star } from '@element-plus/icons-vue'

export default {
  name: 'Expressions',
  components: {
    Refresh,
    Search,
    VideoPlay,
    Star
  },
  setup() {
    const englishStore = useEnglishStore()
    
    // 响应式数据
    const searchQuery = ref('')
    const categoryFilter = ref('')
    const difficultyFilter = ref('')
    const frequencyFilter = ref('')
    const currentPage = ref(1)
    const pageSize = ref(12)
    
    // 计算属性
    const expressions = computed(() => englishStore.expressions)
    const expressionsLoading = computed(() => englishStore.expressionsLoading)
    const total = computed(() => englishStore.expressionsPagination.total)
    
    // 方法
    const refreshData = async () => {
      try {
        await englishStore.fetchExpressions({
          page: currentPage.value,
          page_size: pageSize.value,
          search: searchQuery.value,
          category: categoryFilter.value,
          difficulty_level: difficultyFilter.value,
          usage_frequency: frequencyFilter.value
        })
      } catch (error) {
        ElMessage.error('获取表达数据失败')
        console.error(error)
      }
    }
    
    const handleSearch = () => {
      currentPage.value = 1
      refreshData()
    }
    
    const handleFilter = () => {
      currentPage.value = 1
      refreshData()
    }
    
    const handleSizeChange = (newSize) => {
      pageSize.value = newSize
      refreshData()
    }
    
    const handleCurrentChange = (newPage) => {
      currentPage.value = newPage
      refreshData()
    }
    
    const getDifficultyType = (difficulty) => {
      const typeMap = {
        'beginner': 'success',
        'intermediate': 'warning',
        'advanced': 'danger'
      }
      return typeMap[difficulty] || 'info'
    }
    
    const getDifficultyLabel = (difficulty) => {
      const labelMap = {
        'beginner': '初级',
        'intermediate': '中级',
        'advanced': '高级'
      }
      return labelMap[difficulty] || difficulty
    }
    
    const getFrequencyType = (frequency) => {
      const typeMap = {
        'high': 'danger',
        'medium': 'warning',
        'low': 'info'
      }
      return typeMap[frequency] || 'info'
    }
    
    const getFrequencyLabel = (frequency) => {
      const labelMap = {
        'high': '高频',
        'medium': '中频',
        'low': '低频'
      }
      return labelMap[frequency] || frequency
    }
    
    const getCategoryLabel = (category) => {
      const labelMap = {
        'daily': '日常对话',
        'business': '商务英语',
        'academic': '学术英语',
        'travel': '旅行'
      }
      return labelMap[category] || category
    }
    
    const getScenarioLabel = (scenario) => {
      const labelMap = {
        'meeting': '会议',
        'interview': '面试',
        'shopping': '购物',
        'restaurant': '餐厅',
        'airport': '机场'
      }
      return labelMap[scenario] || scenario
    }
    
    const playAudio = (expression) => {
      if (expression.audio_url) {
        const audio = new Audio(expression.audio_url)
        audio.play().catch(() => {
          ElMessage.warning('音频播放失败')
        })
      } else {
        ElMessage.info('暂无音频文件')
      }
    }
    
    const addToCollection = (expression) => {
      // 这里可以实现收藏功能
      ElMessage.success(`已收藏表达: ${expression.expression}`)
    }
    
    // 生命周期
    onMounted(() => {
      refreshData()
    })
    
    return {
      // 响应式数据
      searchQuery,
      categoryFilter,
      difficultyFilter,
      frequencyFilter,
      currentPage,
      pageSize,
      
      // 计算属性
      expressions,
      expressionsLoading,
      total,
      
      // 方法
      refreshData,
      handleSearch,
      handleFilter,
      handleSizeChange,
      handleCurrentChange,
      getDifficultyType,
      getDifficultyLabel,
      getFrequencyType,
      getFrequencyLabel,
      getCategoryLabel,
      getScenarioLabel,
      playAudio,
      addToCollection
    }
  }
}
</script>

<style scoped>
.expressions-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
  color: #303133;
  font-size: 28px;
  font-weight: 600;
}

.filter-card {
  margin-bottom: 24px;
}

.expressions-list {
  margin-bottom: 24px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.expressions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.expression-card {
  height: fit-content;
  transition: all 0.3s ease;
}

.expression-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.expression-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.expression-text {
  color: #303133;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  flex: 1;
  margin-right: 12px;
}

.expression-tags {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.expression-content {
  margin-bottom: 20px;
}

.expression-content h4 {
  color: #606266;
  font-size: 14px;
  margin: 0 0 8px 0;
  font-weight: 600;
}

.expression-content p {
  color: #303133;
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.category-scenario {
  margin-bottom: 16px;
}

.info-item {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.examples-text {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid #409EFF;
  font-style: italic;
}

.background-text {
  background-color: #fdf6ec;
  padding: 12px;
  border-radius: 6px;
  border-left: 4px solid #E6A23C;
  font-size: 14px;
}

.expression-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .expressions-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .expression-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .expression-tags {
    flex-direction: row;
    justify-content: flex-start;
  }
}
</style>