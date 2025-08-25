import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import fs from 'fs'
import path from 'path'

/**
 * Vitest配置：支持flaky测试处理
 * 
 * 功能：
 * 1. 自动重试失败的测试
 * 2. 生成flaky测试报告
 * 3. 统计测试稳定性
 */

// Flaky测试追踪器
class FlakyTestTracker {
  constructor() {
    this.testResults = new Map()
    this.retryCount = new Map()
    this.maxRetries = 3
    this.flakyThreshold = 0.8
    this.reportDir = 'tests/reports/flaky'
    this.historyFile = path.join(this.reportDir, 'flaky_history.json')
    
    // 确保报告目录存在
    if (!fs.existsSync(this.reportDir)) {
      fs.mkdirSync(this.reportDir, { recursive: true })
    }
    
    this.loadHistory()
  }
  
  loadHistory() {
    try {
      if (fs.existsSync(this.historyFile)) {
        const data = JSON.parse(fs.readFileSync(this.historyFile, 'utf-8'))
        this.testResults = new Map(Object.entries(data.testResults || {}))
      }
    } catch (error) {
      console.warn('Failed to load flaky test history:', error.message)
    }
  }
  
  saveHistory() {
    try {
      const data = {
        testResults: Object.fromEntries(this.testResults),
        lastUpdated: new Date().toISOString()
      }
      fs.writeFileSync(this.historyFile, JSON.stringify(data, null, 2))
    } catch (error) {
      console.warn('Failed to save flaky test history:', error.message)
    }
  }
  
  recordResult(testName, outcome, duration) {
    if (!this.testResults.has(testName)) {
      this.testResults.set(testName, [])
    }
    
    const results = this.testResults.get(testName)
    results.push({ outcome, duration, timestamp: Date.now() })
    
    // 只保留最近50次结果
    if (results.length > 50) {
      results.splice(0, results.length - 50)
    }
  }
  
  isFlaky(testName) {
    const results = this.testResults.get(testName) || []
    if (results.length < 5) return false
    
    const passCount = results.filter(r => r.outcome === 'passed').length
    const successRate = passCount / results.length
    return successRate < this.flakyThreshold && successRate > 0
  }
  
  getFlakyTests() {
    const flakyTests = []
    
    for (const [testName, results] of this.testResults) {
      if (this.isFlaky(testName)) {
        const passCount = results.filter(r => r.outcome === 'passed').length
        const successRate = passCount / results.length
        const avgDuration = results.reduce((sum, r) => sum + r.duration, 0) / results.length
        
        flakyTests.push({
          testName,
          successRate,
          totalRuns: results.length,
          avgDuration,
          recentResults: results.slice(-10).map(r => r.outcome)
        })
      }
    }
    
    return flakyTests.sort((a, b) => a.successRate - b.successRate)
  }
  
  generateReport() {
    const flakyTests = this.getFlakyTests()
    
    // JSON报告
    const jsonReport = {
      timestamp: new Date().toISOString(),
      summary: {
        totalFlakyTests: flakyTests.length,
        threshold: this.flakyThreshold,
        maxRetries: this.maxRetries
      },
      flakyTests
    }
    
    const jsonFile = path.join(this.reportDir, `flaky_report_${new Date().toISOString().replace(/[:.]/g, '-')}.json`)
    fs.writeFileSync(jsonFile, JSON.stringify(jsonReport, null, 2))
    
    // HTML报告
    const htmlContent = this.generateHtmlReport(flakyTests)
    const htmlFile = path.join(this.reportDir, 'flaky_report.html')
    fs.writeFileSync(htmlFile, htmlContent)
    
    console.log('\n=== Flaky Test Report ===')
    console.log(`Total flaky tests: ${flakyTests.length}`)
    console.log(`Report saved to: ${htmlFile}`)
    
    if (flakyTests.length > 0) {
      console.log('\nTop 5 most unstable tests:')
      flakyTests.slice(0, 5).forEach(test => {
        console.log(`  - ${test.testName} (success rate: ${(test.successRate * 100).toFixed(1)}%)`)
      })
    }
  }
  
  generateHtmlReport(flakyTests) {
    const timestamp = new Date().toLocaleString()
    
    let html = `
<!DOCTYPE html>
<html>
<head>
    <title>Flaky Test Report - Frontend</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .test-item { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .flaky { background: #fff3cd; border-color: #ffeaa7; }
        .success-rate { font-weight: bold; }
        .low { color: #dc3545; }
        .medium { color: #fd7e14; }
        .high { color: #28a745; }
    </style>
</head>
<body>
    <h1>Flaky Test Report - Frontend</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Generated: ${timestamp}</p>
        <p>Total flaky tests: ${flakyTests.length}</p>
        <p>Flaky threshold: ${(this.flakyThreshold * 100).toFixed(0)}%</p>
        <p>Max retries: ${this.maxRetries}</p>
    </div>
    
    <h2>Flaky Tests</h2>
`
    
    if (flakyTests.length === 0) {
      html += '<p>No flaky tests detected! 🎉</p>'
    } else {
      flakyTests.forEach(test => {
        const successRate = test.successRate
        const rateClass = successRate < 0.5 ? 'low' : successRate < 0.8 ? 'medium' : 'high'
        
        html += `
    <div class="test-item flaky">
        <h3>${test.testName}</h3>
        <p>Success Rate: <span class="success-rate ${rateClass}">${(successRate * 100).toFixed(1)}%</span></p>
        <p>Total Runs: ${test.totalRuns}</p>
        <p>Average Duration: ${test.avgDuration.toFixed(2)}ms</p>
        <p>Recent Results: ${test.recentResults.join(' ')}</p>
    </div>
`
      })
    }
    
    html += `
</body>
</html>
`
    return html
  }
}

// 全局tracker实例
const flakyTracker = new FlakyTestTracker()

// 自定义reporter
class FlakyReporter {
  onInit() {
    console.log('Flaky test tracking enabled')
  }
  
  onTestFinished(test) {
    const testName = test.name || test.id
    const outcome = test.result?.state || 'unknown'
    const duration = test.result?.duration || 0
    
    flakyTracker.recordResult(testName, outcome, duration)
  }
  
  onFinished() {
    flakyTracker.saveHistory()
    flakyTracker.generateReport()
  }
}

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.js'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      reportsDirectory: './tests/reports/coverage',
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    },
    // 启用重试机制
    retry: 3,
    // 自定义reporter
    reporters: ['default', new FlakyReporter()],
    // 测试超时
    testTimeout: 10000,
    // 并发控制
    pool: 'threads',
    poolOptions: {
      threads: {
        maxThreads: 4,
        minThreads: 1
      }
    }
  },
})