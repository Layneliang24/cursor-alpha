const CrossBrowserLoginTest = require('./cross-browser-login.test')
const CrossBrowserLearningTest = require('./cross-browser-learning.test')
const fs = require('fs')
const path = require('path')

/**
 * Selenium 测试套件运行器
 */
class SeleniumTestRunner {
  constructor () {
    this.allResults = []
    this.startTime = new Date()
  }

  /**
   * 运行所有Selenium测试
   */
  async runAllTests () {
    console.log('🚀 开始运行 Selenium 跨浏览器测试套件')
    console.log('=' .repeat(80))
    console.log(`开始时间: ${this.startTime.toLocaleString()}`)
    console.log('=' .repeat(80))

    try {
      // 运行登录功能测试
      console.log('\n📋 第一阶段: 登录功能测试')
      const loginTest = new CrossBrowserLoginTest()
      const loginResults = await loginTest.runAllBrowsers()
      this.allResults.push(...loginResults)

      // 运行学习功能测试
      console.log('\n📋 第二阶段: 学习功能测试')
      const learningTest = new CrossBrowserLearningTest()
      const learningResults = await learningTest.runAllBrowsers()
      this.allResults.push(...learningResults)

      // 生成综合报告
      await this.generateReport()

    } catch (error) {
      console.error('❌ 测试套件运行失败:', error)
      throw error
    }
  }

  /**
   * 生成测试报告
   */
  async generateReport () {
    const endTime = new Date()
    const duration = Math.round((endTime - this.startTime) / 1000)

    console.log('\n📊 生成综合测试报告')
    console.log('=' .repeat(80))

    // 统计数据
    const stats = this.calculateStats()
    
    // 控制台报告
    this.printConsoleSummary(stats, duration)
    
    // 生成JSON报告
    const jsonReport = this.generateJsonReport(stats, duration)
    await this.saveJsonReport(jsonReport)
    
    // 生成HTML报告
    const htmlReport = this.generateHtmlReport(stats, duration)
    await this.saveHtmlReport(htmlReport)

    console.log('\n🎯 所有测试完成!')
    console.log(`总耗时: ${duration} 秒`)
    console.log('报告已保存到: test-results/selenium-reports/')
  }

  /**
   * 计算统计数据
   */
  calculateStats () {
    const total = this.allResults.length
    const passed = this.allResults.filter(r => r.passed).length
    const failed = total - passed
    const passRate = total > 0 ? (passed / total * 100).toFixed(2) : 0

    // 按浏览器分组
    const browserStats = {}
    this.allResults.forEach(result => {
      if (!browserStats[result.browser]) {
        browserStats[result.browser] = { passed: 0, failed: 0, total: 0, tests: [] }
      }
      
      browserStats[result.browser].total++
      if (result.passed) {
        browserStats[result.browser].passed++
      } else {
        browserStats[result.browser].failed++
      }
      
      browserStats[result.browser].tests.push(result)
    })

    // 按测试类型分组
    const testTypeStats = {}
    this.allResults.forEach(result => {
      const testType = result.test.includes('登录') ? '登录功能' : '学习功能'
      if (!testTypeStats[testType]) {
        testTypeStats[testType] = { passed: 0, failed: 0, total: 0 }
      }
      
      testTypeStats[testType].total++
      if (result.passed) {
        testTypeStats[testType].passed++
      } else {
        testTypeStats[testType].failed++
      }
    })

    return {
      total,
      passed,
      failed,
      passRate,
      browserStats,
      testTypeStats,
      failedTests: this.allResults.filter(r => !r.passed),
    }
  }

  /**
   * 打印控制台摘要
   */
  printConsoleSummary (stats, duration) {
    console.log('\n📈 总体统计:')
    console.log(`  总测试数: ${stats.total}`)
    console.log(`  通过: ${stats.passed} (${stats.passRate}%)`)
    console.log(`  失败: ${stats.failed}`)
    console.log(`  耗时: ${duration} 秒`)

    console.log('\n🌐 浏览器兼容性:')
    Object.keys(stats.browserStats).forEach(browser => {
      const browserStat = stats.browserStats[browser]
      const rate = (browserStat.passed / browserStat.total * 100).toFixed(1)
      console.log(`  ${browser.toUpperCase()}: ${browserStat.passed}/${browserStat.total} (${rate}%)`)
    })

    console.log('\n🔧 功能模块:')
    Object.keys(stats.testTypeStats).forEach(testType => {
      const typeStat = stats.testTypeStats[testType]
      const rate = (typeStat.passed / typeStat.total * 100).toFixed(1)
      console.log(`  ${testType}: ${typeStat.passed}/${typeStat.total} (${rate}%)`)
    })

    if (stats.failedTests.length > 0) {
      console.log('\n❌ 失败的测试:')
      stats.failedTests.forEach(test => {
        console.log(`  [${test.browser}] ${test.test}: ${test.message}`)
      })
    }
  }

  /**
   * 生成JSON报告
   */
  generateJsonReport (stats, duration) {
    return {
      summary: {
        total: stats.total,
        passed: stats.passed,
        failed: stats.failed,
        passRate: parseFloat(stats.passRate),
        duration,
        timestamp: new Date().toISOString(),
      },
      browserStats: stats.browserStats,
      testTypeStats: stats.testTypeStats,
      results: this.allResults,
      failedTests: stats.failedTests,
    }
  }

  /**
   * 生成HTML报告
   */
  generateHtmlReport (stats, duration) {
    const browserRows = Object.keys(stats.browserStats).map(browser => {
      const stat = stats.browserStats[browser]
      const rate = (stat.passed / stat.total * 100).toFixed(1)
      const status = rate >= 90 ? 'success' : rate >= 70 ? 'warning' : 'danger'
      
      return `
        <tr class="${status}">
          <td>${browser.toUpperCase()}</td>
          <td>${stat.total}</td>
          <td>${stat.passed}</td>
          <td>${stat.failed}</td>
          <td>${rate}%</td>
        </tr>
      `
    }).join('')

    const failedTestRows = stats.failedTests.map(test => `
      <tr>
        <td>${test.browser}</td>
        <td>${test.test}</td>
        <td>${test.message}</td>
        <td>${new Date(test.timestamp).toLocaleString()}</td>
      </tr>
    `).join('')

    return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Selenium 跨浏览器测试报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .summary { display: flex; justify-content: space-around; margin-bottom: 30px; }
        .stat-card { background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; margin-bottom: 5px; }
        .stat-label { color: #666; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .success { background-color: #d4edda; }
        .warning { background-color: #fff3cd; }
        .danger { background-color: #f8d7da; }
        .pass { color: #28a745; }
        .fail { color: #dc3545; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 Selenium 跨浏览器测试报告</h1>
        <p>生成时间: ${new Date().toLocaleString()}</p>
        <p>测试耗时: ${duration} 秒</p>
    </div>

    <div class="summary">
        <div class="stat-card">
            <div class="stat-number">${stats.total}</div>
            <div class="stat-label">总测试数</div>
        </div>
        <div class="stat-card">
            <div class="stat-number pass">${stats.passed}</div>
            <div class="stat-label">通过</div>
        </div>
        <div class="stat-card">
            <div class="stat-number fail">${stats.failed}</div>
            <div class="stat-label">失败</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${stats.passRate}%</div>
            <div class="stat-label">通过率</div>
        </div>
    </div>

    <h2>🌐 浏览器兼容性报告</h2>
    <table>
        <thead>
            <tr>
                <th>浏览器</th>
                <th>总测试数</th>
                <th>通过</th>
                <th>失败</th>
                <th>通过率</th>
            </tr>
        </thead>
        <tbody>
            ${browserRows}
        </tbody>
    </table>

    ${stats.failedTests.length > 0 ? `
    <h2>❌ 失败的测试</h2>
    <table>
        <thead>
            <tr>
                <th>浏览器</th>
                <th>测试名称</th>
                <th>失败原因</th>
                <th>时间</th>
            </tr>
        </thead>
        <tbody>
            ${failedTestRows}
        </tbody>
    </table>
    ` : '<h2>🎉 所有测试都通过了!</h2>'}

    <h2>📋 详细结果</h2>
    <details>
        <summary>查看所有测试结果 JSON</summary>
        <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;">
${JSON.stringify(this.allResults, null, 2)}
        </pre>
    </details>
</body>
</html>
    `
  }

  /**
   * 保存JSON报告
   */
  async saveJsonReport (report) {
    const reportDir = path.join(__dirname, '../../test-results/selenium-reports')
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true })
    }

    const filename = `selenium-test-report-${new Date().toISOString().replace(/[:.]/g, '-')}.json`
    const filepath = path.join(reportDir, filename)
    
    fs.writeFileSync(filepath, JSON.stringify(report, null, 2))
    console.log(`📄 JSON报告已保存: ${filepath}`)
  }

  /**
   * 保存HTML报告
   */
  async saveHtmlReport (htmlContent) {
    const reportDir = path.join(__dirname, '../../test-results/selenium-reports')
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true })
    }

    const filename = `selenium-test-report-${new Date().toISOString().replace(/[:.]/g, '-')}.html`
    const filepath = path.join(reportDir, filename)
    
    fs.writeFileSync(filepath, htmlContent)
    console.log(`📄 HTML报告已保存: ${filepath}`)
  }
}

// 如果直接运行此文件
if (require.main === module) {
  const runner = new SeleniumTestRunner()
  runner.runAllTests()
    .then(() => {
      console.log('\n✅ 所有 Selenium 测试完成')
      process.exit(0)
    })
    .catch(error => {
      console.error('\n❌ Selenium 测试套件运行失败:', error)
      process.exit(1)
    })
}

module.exports = SeleniumTestRunner
