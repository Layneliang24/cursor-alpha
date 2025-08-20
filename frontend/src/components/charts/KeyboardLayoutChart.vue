<template>
  <div class="keyboard-layout-chart">
    <div class="keyboard-container">
      <!-- 第一行数字键 -->
      <div class="keyboard-row">
        <div 
          v-for="key in numberKeys" 
          :key="key"
          class="keyboard-key number-key"
          :class="getKeyClass(key)"
          :title="getKeyTooltip(key)"
          @click="handleKeyClick(key)"
        >
          <span class="key-label">{{ key }}</span>
          <span v-if="getKeyErrorCount(key) > 0" class="error-count">{{ getKeyErrorCount(key) }}</span>
        </div>
      </div>
      
      <!-- 第二行QWERTY -->
      <div class="keyboard-row">
        <div 
          v-for="key in qwertyKeys" 
          :key="key"
          class="keyboard-key letter-key"
          :class="getKeyClass(key)"
          :title="getKeyTooltip(key)"
          @click="handleKeyClick(key)"
        >
          <span class="key-label">{{ key.toUpperCase() }}</span>
          <span v-if="getKeyErrorCount(key) > 0" class="error-count">{{ getKeyErrorCount(key) }}</span>
        </div>
      </div>
      
      <!-- 第三行ASDF -->
      <div class="keyboard-row">
        <div 
          v-for="key in asdfKeys" 
          :key="key"
          class="keyboard-key letter-key"
          :class="getKeyClass(key)"
          :title="getKeyTooltip(key)"
          @click="handleKeyClick(key)"
        >
          <span class="key-label">{{ key.toUpperCase() }}</span>
          <span v-if="getKeyErrorCount(key) > 0" class="error-count">{{ getKeyErrorCount(key) }}</span>
        </div>
      </div>
      
      <!-- 第四行ZXCV -->
      <div class="keyboard-row">
        <div 
          v-for="key in zxcvKeys" 
          :key="key"
          class="keyboard-key letter-key"
          :class="getKeyClass(key)"
          :title="getKeyTooltip(key)"
          @click="handleKeyClick(key)"
        >
          <span class="key-label">{{ key.toUpperCase() }}</span>
          <span v-if="getKeyErrorCount(key) > 0" class="error-count">{{ getKeyErrorCount(key) }}</span>
        </div>
      </div>
      
      <!-- 空格键 -->
      <div class="keyboard-row">
        <div 
          class="keyboard-key space-key"
          :class="getKeyClass(' ')"
          :title="getKeyTooltip(' ')"
          @click="handleKeyClick(' ')"
        >
          <span class="key-label">SPACE</span>
          <span v-if="getKeyErrorCount(' ') > 0" class="error-count">{{ getKeyErrorCount(' ') }}</span>
        </div>
      </div>
    </div>
    
    <!-- 图例 -->
    <div class="legend">
      <div class="legend-title">错误次数</div>
      <div class="legend-items">
        <div class="legend-item" v-for="(color, level) in legendColors" :key="level">
          <div class="legend-color" :style="{ backgroundColor: color }"></div>
          <span class="legend-label">{{ getLegendLabel(level) }}</span>
        </div>
      </div>
    </div>
    
    <!-- 统计信息 -->
    <div class="stats-info" v-if="errorStats.length > 0">
      <div class="stats-title">错误统计</div>
      <div class="stats-content">
        <div class="stat-item">
          <span class="stat-label">总错误次数:</span>
          <span class="stat-value">{{ totalErrors }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">错误最多的按键:</span>
          <span class="stat-value">{{ mostErrorKey }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">有错误的按键数:</span>
          <span class="stat-value">{{ errorKeyCount }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'KeyboardLayoutChart',
  props: {
    data: {
      type: Array,
      default: () => []
    }
  },
  emits: ['key-click'],
  setup(props, { emit }) {
    // 键盘布局定义
    const numberKeys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    const qwertyKeys = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p']
    const asdfKeys = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l']
    const zxcvKeys = ['z', 'x', 'c', 'v', 'b', 'n', 'm']
    
    // 图例颜色配置
    const legendColors = {
      0: '#f0f0f0', // 无错误
      1: '#ffeb3b', // 1-3次错误
      2: '#ff9800', // 4-10次错误
      3: '#f44336', // 11-20次错误
      4: '#9c27b0'  // 20次以上错误
    }
    
    // 处理错误数据
    const errorStats = computed(() => {
      return props.data || []
    })
    
    // 获取按键错误次数
    const getKeyErrorCount = (key) => {
      const keyData = errorStats.value.find(item => 
        item.name === key || item.name === key.toLowerCase() || item.name === key.toUpperCase()
      )
      return keyData ? keyData.value : 0
    }
    
    // 获取按键样式类
    const getKeyClass = (key) => {
      const errorCount = getKeyErrorCount(key)
      let level = 0
      
      if (errorCount > 20) level = 4
      else if (errorCount > 10) level = 3
      else if (errorCount > 3) level = 2
      else if (errorCount > 0) level = 1
      
      return `error-level-${level}`
    }
    
    // 获取按键提示信息
    const getKeyTooltip = (key) => {
      const errorCount = getKeyErrorCount(key)
      const keyName = key === ' ' ? '空格键' : key.toUpperCase()
      return `${keyName}: ${errorCount}次错误`
    }
    
    // 获取图例标签
    const getLegendLabel = (level) => {
      const labels = {
        0: '无错误',
        1: '1-3次',
        2: '4-10次',
        3: '11-20次',
        4: '20次以上'
      }
      return labels[level] || '无错误'
    }
    
    // 计算总错误次数
    const totalErrors = computed(() => {
      return errorStats.value.reduce((sum, item) => sum + item.value, 0)
    })
    
    // 计算错误最多的按键
    const mostErrorKey = computed(() => {
      if (errorStats.value.length === 0) return '无'
      const maxError = errorStats.value.reduce((max, item) => 
        item.value > max.value ? item : max
      )
      return `${maxError.name.toUpperCase()} (${maxError.value}次)`
    })
    
    // 计算有错误的按键数
    const errorKeyCount = computed(() => {
      return errorStats.value.filter(item => item.value > 0).length
    })
    
    // 处理按键点击
    const handleKeyClick = (key) => {
      const errorCount = getKeyErrorCount(key)
      emit('key-click', { key, errorCount })
    }
    
    return {
      numberKeys,
      qwertyKeys,
      asdfKeys,
      zxcvKeys,
      legendColors,
      errorStats,
      getKeyErrorCount,
      getKeyClass,
      getKeyTooltip,
      getLegendLabel,
      totalErrors,
      mostErrorKey,
      errorKeyCount,
      handleKeyClick
    }
  }
}
</script>

<style scoped>
.keyboard-layout-chart {
  width: 100%;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.keyboard-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-bottom: 30px;
}

.keyboard-row {
  display: flex;
  gap: 6px;
  justify-content: center;
}

.keyboard-key {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  height: 40px;
  background: #ffffff;
  border: 2px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  user-select: none;
}

.keyboard-key:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #409eff;
}

.keyboard-key.space-key {
  min-width: 200px;
  margin-top: 8px;
}

.key-label {
  font-size: 12px;
  font-weight: bold;
  color: #333;
}

.error-count {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ff4757;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: bold;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* 错误级别颜色 */
.keyboard-key.error-level-0 {
  background: #f0f0f0;
  border-color: #ddd;
}

.keyboard-key.error-level-1 {
  background: #fff3cd;
  border-color: #ffeaa7;
  color: #856404;
}

.keyboard-key.error-level-2 {
  background: #ffe0b2;
  border-color: #ffcc80;
  color: #e65100;
}

.keyboard-key.error-level-3 {
  background: #ffcdd2;
  border-color: #ef9a9a;
  color: #c62828;
}

.keyboard-key.error-level-4 {
  background: #e1bee7;
  border-color: #ce93d8;
  color: #4a148c;
}

.legend {
  margin-bottom: 20px;
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.legend-title {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 12px;
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
  gap: 6px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  border: 1px solid #ddd;
}

.legend-label {
  font-size: 12px;
  color: #666;
}

.stats-info {
  padding: 15px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stats-title {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 12px;
  text-align: center;
}

.stats-content {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 15px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 16px;
  font-weight: bold;
  color: #409eff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .keyboard-key {
    min-width: 32px;
    height: 32px;
  }
  
  .keyboard-key.space-key {
    min-width: 160px;
  }
  
  .key-label {
    font-size: 10px;
  }
  
  .error-count {
    width: 16px;
    height: 16px;
    font-size: 8px;
    top: -6px;
    right: -6px;
  }
  
  .legend-items {
    gap: 10px;
  }
  
  .stats-content {
    flex-direction: column;
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .keyboard-layout-chart {
    padding: 10px;
  }
  
  .keyboard-row {
    gap: 3px;
  }
  
  .keyboard-key {
    min-width: 28px;
    height: 28px;
  }
  
  .keyboard-key.space-key {
    min-width: 120px;
  }
}
</style>
