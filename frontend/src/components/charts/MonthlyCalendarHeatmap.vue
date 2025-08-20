<template>
  <div class="monthly-calendar-heatmap">
    <div class="calendar-header">
      <el-button @click="previousMonth" icon="ArrowLeft" size="small" :disabled="isCurrentMonth"></el-button>
      <span class="month-title">{{ currentMonthTitle }}</span>
      <el-button @click="nextMonth" icon="ArrowRight" size="small"></el-button>
    </div>
    
    <div class="calendar-container">
      <!-- 星期标题 -->
      <div class="weekdays">
        <div class="weekday" v-for="weekday in weekdays" :key="weekday">{{ weekday }}</div>
      </div>
      
      <!-- 日历网格 -->
      <div class="calendar-grid">
        <div 
          v-for="day in calendarData" 
          :key="day.date"
          class="calendar-day"
          :class="{
            'current-month': day.is_current_month,
            'other-month': !day.is_current_month,
            'has-data': day.has_data,
            [`level-${day.exercise_level}`]: day.is_current_month && day.has_data
          }"
          @click="handleDayClick(day)"
          :title="getDayTooltip(day)"
        >
          <span class="day-number">{{ day.day }}</span>
          <div v-if="day.is_current_month && day.has_data" class="day-stats">
            <div class="exercise-count">{{ day.exercise_count }}</div>
            <div class="word-count">{{ day.word_count }}</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 图例 -->
    <div class="legend">
      <div class="legend-title">练习强度</div>
      <div class="legend-items">
        <div class="legend-item" v-for="(color, level) in legendColors" :key="level">
          <div class="legend-color" :style="{ backgroundColor: color }"></div>
          <span class="legend-label">{{ getLegendLabel(level) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'MonthlyCalendarHeatmap',
  props: {
    data: {
      type: Object,
      default: () => ({})
    },
    initialYear: {
      type: Number,
      default: () => new Date().getFullYear()
    },
    initialMonth: {
      type: Number,
      default: () => new Date().getMonth() + 1
    }
  },
  emits: ['month-change', 'day-click'],
  setup(props, { emit }) {
    const currentYear = ref(props.initialYear)
    const currentMonth = ref(props.initialMonth)
    
    const weekdays = ['日', '一', '二', '三', '四', '五', '六']
    
    // 图例颜色配置
    const legendColors = {
      0: '#ebedf0', // 无数据
      1: '#c6e48b', // 低强度
      2: '#7bc96f', // 中强度
      3: '#239a3b', // 高强度
      4: '#196127'  // 极高强度
    }
    
    // 计算当前月份标题
    const currentMonthTitle = computed(() => {
      return `${currentYear.value}年${currentMonth.value}月`
    })
    
    // 判断是否为当前月份
    const isCurrentMonth = computed(() => {
      const now = new Date()
      return currentYear.value === now.getFullYear() && currentMonth.value === now.getMonth() + 1
    })
    
    // 处理日历数据
    const calendarData = computed(() => {
      if (!props.data.weeks_data) return []
      
      const data = []
      props.data.weeks_data.forEach(week => {
        week.forEach(day => {
          data.push(day)
        })
      })
      return data
    })
    
    // 获取图例标签
    const getLegendLabel = (level) => {
      const labels = {
        0: '无练习',
        1: '1-2次',
        2: '3-5次', 
        3: '6-10次',
        4: '10次以上'
      }
      return labels[level] || '无练习'
    }
    
    // 获取日期提示信息
    const getDayTooltip = (day) => {
      if (!day.is_current_month) return ''
      
      if (day.has_data) {
        return `${day.date}\n练习次数: ${day.exercise_count}\n练习单词: ${day.word_count}`
      } else {
        return `${day.date}\n无练习记录`
      }
    }
    
    // 处理月份切换
    const previousMonth = () => {
      if (currentMonth.value === 1) {
        currentMonth.value = 12
        currentYear.value--
      } else {
        currentMonth.value--
      }
      emit('month-change', { year: currentYear.value, month: currentMonth.value })
    }
    
    const nextMonth = () => {
      if (currentMonth.value === 12) {
        currentMonth.value = 1
        currentYear.value++
      } else {
        currentMonth.value++
      }
      emit('month-change', { year: currentYear.value, month: currentMonth.value })
    }
    
    // 处理日期点击
    const handleDayClick = (day) => {
      if (day.is_current_month) {
        emit('day-click', day)
      }
    }
    
    // 监听数据变化，更新当前年月
    watch(() => props.data, (newData) => {
      if (newData.year && newData.month) {
        currentYear.value = newData.year
        currentMonth.value = newData.month
      }
    }, { immediate: true })
    
    return {
      currentYear,
      currentMonth,
      weekdays,
      legendColors,
      currentMonthTitle,
      isCurrentMonth,
      calendarData,
      getLegendLabel,
      getDayTooltip,
      previousMonth,
      nextMonth,
      handleDayClick
    }
  }
}
</script>

<style scoped>
.monthly-calendar-heatmap {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  background: #fafafa;
  border-radius: 12px;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 25px;
  margin-bottom: 25px;
  padding: 15px 25px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.month-title {
  font-size: 20px;
  font-weight: 600;
  color: #ffffff;
  min-width: 140px;
  text-align: center;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.calendar-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  border: 1px solid #e8eaed;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 2px solid #dee2e6;
}

.weekday {
  padding: 15px 8px;
  text-align: center;
  font-weight: 600;
  color: #495057;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 1px;
  background: #e4e7ed;
}

.calendar-day {
  aspect-ratio: 1;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
  min-height: 60px;
}

.calendar-day:hover {
  background: #e3f2fd;
  transform: scale(1.08);
  z-index: 2;
  box-shadow: 0 8px 25px rgba(33, 150, 243, 0.3);
  border-radius: 8px;
}

.calendar-day.other-month {
  background: #fafafa;
  color: #c0c4cc;
  cursor: default;
}

.calendar-day.other-month:hover {
  background: #fafafa;
  transform: none;
  box-shadow: none;
}

.calendar-day.has-data {
  font-weight: bold;
}

.day-number {
  font-size: 14px;
  margin-bottom: 2px;
}

.day-stats {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 10px;
  line-height: 1.2;
}

.exercise-count {
  color: #409eff;
  font-weight: bold;
}

.word-count {
  color: #67c23a;
}

/* 热力图颜色级别 - 更美观的渐变色 */
.calendar-day.level-0 {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
}

.calendar-day.level-1 {
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
  border: 1px solid #b8dacc;
  color: #155724;
}

.calendar-day.level-2 {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  border: 1px solid #1e7e34;
  color: #fff;
}

.calendar-day.level-3 {
  background: linear-gradient(135deg, #007bff 0%, #6610f2 100%);
  border: 1px solid #004085;
  color: #fff;
}

.calendar-day.level-4 {
  background: linear-gradient(135deg, #6f42c1 0%, #e83e8c 100%);
  border: 1px solid #59359a;
  color: #fff;
}

.calendar-day.level-1,
.calendar-day.level-2,
.calendar-day.level-3,
.calendar-day.level-4 {
  color: #fff;
}

.calendar-day.level-1 .exercise-count,
.calendar-day.level-1 .word-count,
.calendar-day.level-2 .exercise-count,
.calendar-day.level-2 .word-count,
.calendar-day.level-3 .exercise-count,
.calendar-day.level-3 .word-count,
.calendar-day.level-4 .exercise-count,
.calendar-day.level-4 .word-count {
  color: #fff;
}

.legend {
  margin-top: 25px;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid #e8eaed;
}

.legend-title {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
  text-align: center;
}

.legend-items {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 2px;
  border: 1px solid #dcdfe6;
}

.legend-label {
  font-size: 12px;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .monthly-calendar-heatmap {
    max-width: 100%;
  }
  
  .calendar-day {
    min-height: 50px;
  }
  
  .day-number {
    font-size: 12px;
  }
  
  .day-stats {
    font-size: 8px;
  }
  
  .legend-items {
    gap: 10px;
  }
  
  .legend-item {
    font-size: 10px;
  }
}
</style>
