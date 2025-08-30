<template>
  <div class="report-generator">
    <el-card class="generator-card">
      <template #header>
        <div class="card-header">
          <h3>学习报告生成</h3>
          <el-button
            type="primary"
            @click="showGeneratorDialog = true"
            icon="el-icon-document"
          >
            生成报告
          </el-button>
        </div>
      </template>

      <!-- 最近报告列表 -->
      <div class="recent-reports" v-if="recentReports.length > 0">
        <h4>最近生成的报告</h4>
        <div class="reports-list">
          <div 
            v-for="report in recentReports" 
            :key="report.id"
            class="report-item"
          >
            <div class="report-info">
              <div class="report-title">{{ report.title }}</div>
              <div class="report-meta">
                <span class="report-period">{{ report.period }}</span>
                <span class="report-date">{{ formatDate(report.generated_at) }}</span>
              </div>
            </div>
            <div class="report-actions">
              <el-button 
                size="small" 
                type="text"
                @click="viewReport(report)"
              >
                查看
              </el-button>
              <el-button 
                size="small" 
                type="text"
                @click="downloadReport(report)"
              >
                下载
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 快速生成按钮 -->
      <div class="quick-generate" v-if="recentReports.length === 0">
        <el-empty description="暂无报告">
          <el-button 
            type="primary" 
            @click="quickGenerate('weekly')"
            :loading="generating"
          >
            生成本周报告
          </el-button>
        </el-empty>
      </div>
    </el-card>

    <!-- 报告生成对话框 -->
    <el-dialog
      v-model="showGeneratorDialog"
      title="生成学习报告"
      width="600px"
      :before-close="handleDialogClose"
    >
      <el-form :model="reportForm" label-width="100px" ref="reportFormRef">
        <el-form-item label="报告模板" required>
          <el-select 
            v-model="reportForm.template"
            placeholder="选择报告模板"
            @change="handleTemplateChange"
          >
            <el-option
              v-for="template in templates"
              :key="template.id"
              :label="template.name"
              :value="template.id"
            >
              <span>{{ template.name }}</span>
              <span style="float: right; color: #8492a6; font-size: 13px">
                {{ template.description }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="时间范围" required v-if="reportForm.template === 'custom'">
          <el-date-picker
            v-model="reportForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <el-form-item label="报告格式">
          <el-radio-group v-model="reportForm.format">
            <el-radio label="json">在线查看</el-radio>
            <el-radio label="pdf">PDF文件</el-radio>
            <el-radio label="excel">Excel表格</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="包含内容">
          <el-checkbox-group v-model="reportForm.sections">
            <el-checkbox label="summary">学习概览</el-checkbox>
            <el-checkbox label="progress">进度分析</el-checkbox>
            <el-checkbox label="efficiency">效率分析</el-checkbox>
            <el-checkbox label="weak_areas">薄弱环节</el-checkbox>
            <el-checkbox label="recommendations">学习建议</el-checkbox>
            <el-checkbox label="achievements">学习成就</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <el-form-item label="包含图表" v-if="reportForm.format === 'pdf'">
          <el-switch v-model="reportForm.includeCharts" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showGeneratorDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="generateReport"
          :loading="generating"
        >
          生成报告
        </el-button>
      </template>
    </el-dialog>

    <!-- 报告预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      title="报告预览"
      width="80%"
      :before-close="handlePreviewClose"
    >
      <div class="report-preview" v-if="previewData">
        <div class="preview-header">
          <h2>{{ previewData.report_info.username }} 的学习报告</h2>
          <p class="preview-period">
            {{ previewData.report_info.start_date }} 至 {{ previewData.report_info.end_date }}
          </p>
        </div>

        <div class="preview-summary">
          <h3>学习概览</h3>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-value">{{ previewData.summary.total_expressions }}</div>
                <div class="summary-label">学习表达总数</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-value">{{ formatPercentage(previewData.summary.mastery_rate) }}</div>
                <div class="summary-label">掌握率</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-value">{{ formatDuration(previewData.summary.total_study_time) }}</div>
                <div class="summary-label">总学习时长</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="summary-item">
                <div class="summary-value">{{ previewData.summary.learning_streak }}</div>
                <div class="summary-label">连续学习天数</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <div class="preview-sections">
          <!-- 薄弱环节 -->
          <div class="preview-section" v-if="previewData.weak_areas?.length > 0">
            <h3>薄弱环节</h3>
            <el-table :data="previewData.weak_areas.slice(0, 5)" size="small">
              <el-table-column prop="expression" label="表达" />
              <el-table-column prop="category" label="分类" />
              <el-table-column label="掌握度">
                <template #default="scope">
                  {{ formatPercentage(scope.row.mastery_level) }}
                </template>
              </el-table-column>
              <el-table-column label="准确率">
                <template #default="scope">
                  {{ formatPercentage(scope.row.accuracy_rate) }}
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 学习建议 -->
          <div class="preview-section" v-if="previewData.recommendations?.length > 0">
            <h3>学习建议</h3>
            <div class="recommendations-preview">
              <div 
                v-for="(rec, index) in previewData.recommendations"
                :key="index"
                class="recommendation-item"
              >
                <div class="rec-priority" :class="rec.priority">
                  {{ getPriorityText(rec.priority) }}
                </div>
                <div class="rec-content">
                  <div class="rec-title">{{ rec.title }}</div>
                  <div class="rec-description">{{ rec.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
        <el-button 
          type="primary" 
          @click="downloadPreviewReport"
          :loading="downloading"
        >
          下载此报告
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { dataAnalysisAPI } from '@/api/english'
import { ElMessage } from 'element-plus'

export default {
  name: 'ReportGenerator',
  data() {
    return {
      showGeneratorDialog: false,
      showPreviewDialog: false,
      generating: false,
      downloading: false,
      templates: [],
      recentReports: [],
      previewData: null,
      reportForm: {
        template: 'monthly',
        dateRange: [],
        format: 'json',
        sections: ['summary', 'progress', 'weak_areas', 'recommendations'],
        includeCharts: false
      }
    }
  },
  mounted() {
    this.loadTemplates()
    this.loadRecentReports()
  },
  methods: {
    async loadTemplates() {
      try {
        const response = await dataAnalysisAPI.getReportTemplates()
        this.templates = response.data.templates
      } catch (error) {
        console.error('加载报告模板失败:', error)
      }
    },
    
    async loadRecentReports() {
      // 模拟最近报告数据
      this.recentReports = [
        {
          id: 1,
          title: '月度学习报告',
          period: '2025-08-01 至 2025-08-30',
          format: 'pdf',
          generated_at: '2025-08-30T10:00:00Z'
        },
        {
          id: 2,
          title: '周度学习报告',
          period: '2025-08-23 至 2025-08-30',
          format: 'json',
          generated_at: '2025-08-30T15:30:00Z'
        }
      ]
    },
    
    handleTemplateChange() {
      const template = this.templates.find(t => t.id === this.reportForm.template)
      if (template && template.default_period) {
        const endDate = new Date()
        const startDate = new Date()
        startDate.setDate(endDate.getDate() - template.default_period)
        
        this.reportForm.dateRange = [
          startDate.toISOString().split('T')[0],
          endDate.toISOString().split('T')[0]
        ]
      }
    },
    
    async generateReport() {
      this.generating = true
      try {
        const params = this.buildReportParams()
        
        if (this.reportForm.format === 'json') {
          const response = await dataAnalysisAPI.generateReport(params)
          this.previewData = response.data
          this.showGeneratorDialog = false
          this.showPreviewDialog = true
        } else {
          // 下载文件格式
          const response = await dataAnalysisAPI.downloadReport(params)
          this.downloadFile(response.data, this.getFileName())
          this.showGeneratorDialog = false
          ElMessage.success('报告生成成功')
        }
        
        // 更新最近报告列表
        this.loadRecentReports()
        
      } catch (error) {
        console.error('生成报告失败:', error)
        ElMessage.error('生成报告失败，请稍后重试')
      } finally {
        this.generating = false
      }
    },
    
    async quickGenerate(templateId) {
      this.generating = true
      try {
        const template = this.templates.find(t => t.id === templateId)
        const params = {
          format: 'json'
        }
        
        if (template?.default_period) {
          const endDate = new Date()
          const startDate = new Date()
          startDate.setDate(endDate.getDate() - template.default_period)
          
          params.start_date = startDate.toISOString().split('T')[0]
          params.end_date = endDate.toISOString().split('T')[0]
        }
        
        const response = await dataAnalysisAPI.generateReport(params)
        this.previewData = response.data
        this.showPreviewDialog = true
        
        ElMessage.success('报告生成成功')
        
      } catch (error) {
        console.error('快速生成报告失败:', error)
        ElMessage.error('生成报告失败，请稍后重试')
      } finally {
        this.generating = false
      }
    },
    
    buildReportParams() {
      const params = {
        format: this.reportForm.format,
        include_charts: this.reportForm.includeCharts
      }
      
      if (this.reportForm.template === 'custom' && this.reportForm.dateRange.length === 2) {
        params.start_date = this.reportForm.dateRange[0]
        params.end_date = this.reportForm.dateRange[1]
      } else {
        const template = this.templates.find(t => t.id === this.reportForm.template)
        if (template?.default_period) {
          const endDate = new Date()
          const startDate = new Date()
          startDate.setDate(endDate.getDate() - template.default_period)
          
          params.start_date = startDate.toISOString().split('T')[0]
          params.end_date = endDate.toISOString().split('T')[0]
        }
      }
      
      return params
    },
    
    getFileName() {
      const template = this.templates.find(t => t.id === this.reportForm.template)
      const templateName = template?.name || '学习报告'
      const date = new Date().toISOString().split('T')[0]
      const extension = this.reportForm.format === 'pdf' ? 'pdf' : 'xlsx'
      
      return `${templateName}_${date}.${extension}`
    },
    
    downloadFile(data, filename) {
      const blob = new Blob([data])
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    },
    
    async downloadPreviewReport() {
      this.downloading = true
      try {
        const params = {
          ...this.buildReportParams(),
          format: 'pdf'
        }
        
        const response = await dataAnalysisAPI.downloadReport(params)
        this.downloadFile(response.data, this.getFileName())
        
        ElMessage.success('报告下载成功')
      } catch (error) {
        console.error('下载报告失败:', error)
        ElMessage.error('下载失败，请稍后重试')
      } finally {
        this.downloading = false
      }
    },
    
    viewReport(report) {
      // 查看历史报告
      ElMessage.info('查看历史报告功能开发中...')
    },
    
    downloadReport(report) {
      // 下载历史报告
      ElMessage.info('下载历史报告功能开发中...')
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    formatPercentage(value) {
      if (!value && value !== 0) return '0%'
      return `${(value * 100).toFixed(1)}%`
    },
    
    formatDuration(minutes) {
      if (!minutes) return '0分钟'
      
      const hours = Math.floor(minutes / 60)
      const mins = Math.round(minutes % 60)
      
      if (hours > 0) {
        return `${hours}小时${mins}分钟`
      }
      return `${mins}分钟`
    },
    
    getPriorityText(priority) {
      const map = {
        high: '高优先级',
        medium: '中优先级',
        low: '低优先级'
      }
      return map[priority] || priority
    },
    
    handleDialogClose() {
      this.showGeneratorDialog = false
      this.resetForm()
    },
    
    handlePreviewClose() {
      this.showPreviewDialog = false
      this.previewData = null
    },
    
    resetForm() {
      this.reportForm = {
        template: 'monthly',
        dateRange: [],
        format: 'json',
        sections: ['summary', 'progress', 'weak_areas', 'recommendations'],
        includeCharts: false
      }
    }
  }
}
</script>

<style scoped>
.report-generator {
  margin-bottom: 20px;
}

.generator-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  color: #303133;
  font-size: 18px;
  font-weight: 500;
}

.recent-reports h4 {
  margin: 0 0 15px 0;
  color: #606266;
  font-size: 16px;
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.report-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #fafafa;
}

.report-info {
  flex: 1;
}

.report-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.report-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #909399;
}

.report-actions {
  display: flex;
  gap: 5px;
}

.quick-generate {
  padding: 40px 0;
  text-align: center;
}

.report-preview {
  max-height: 70vh;
  overflow-y: auto;
}

.preview-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.preview-header h2 {
  margin: 0 0 10px 0;
  color: #303133;
}

.preview-period {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.preview-summary {
  margin-bottom: 30px;
}

.preview-summary h3 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
}

.summary-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: #409EFF;
  margin-bottom: 5px;
}

.summary-label {
  font-size: 12px;
  color: #606266;
}

.preview-section {
  margin-bottom: 25px;
}

.preview-section h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.recommendations-preview {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  padding: 15px;
  border-radius: 8px;
  background: #f8f9fa;
}

.rec-priority {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  margin-right: 12px;
  flex-shrink: 0;
}

.rec-priority.high {
  background: #fef0f0;
  color: #F56C6C;
}

.rec-priority.medium {
  background: #fdf6ec;
  color: #E6A23C;
}

.rec-priority.low {
  background: #f0f9ff;
  color: #409EFF;
}

.rec-content {
  flex: 1;
}

.rec-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.rec-description {
  font-size: 13px;
  color: #606266;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .card-header button {
    margin-top: 10px;
  }
  
  .report-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .report-actions {
    margin-top: 10px;
    align-self: flex-end;
  }
}
</style>
