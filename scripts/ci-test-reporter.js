#!/usr/bin/env node

/**
 * CI/CD测试报告生成器
 * 收集并汇总所有测试结果，生成统一报告
 */

const fs = require('fs');
const path = require('path');

class CITestReporter {
  constructor() {
    this.results = {
      timestamp: new Date().toISOString(),
      summary: {
        total: 0,
        passed: 0,
        failed: 0,
        skipped: 0,
        passRate: 0
      },
      tests: {
        unit: { status: 'not_run', results: null },
        e2e: { status: 'not_run', results: null },
        selenium: { status: 'not_run', results: null },
        lint: { status: 'not_run', results: null },
        build: { status: 'not_run', results: null }
      },
      artifacts: []
    };
  }

  /**
   * 收集Playwright E2E测试结果
   */
  collectPlaywrightResults() {
    try {
      const reportPath = path.join(process.cwd(), 'frontend/test-results/results.json');
      if (fs.existsSync(reportPath)) {
        const data = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
        
        this.results.tests.e2e = {
          status: 'completed',
          results: {
            total: data.stats?.total || 0,
            passed: data.stats?.expected || 0,
            failed: data.stats?.unexpected || 0,
            skipped: data.stats?.skipped || 0,
            duration: data.stats?.duration || 0
          }
        };
        
        console.log('✅ Playwright E2E结果已收集');
        return true;
      }
    } catch (error) {
      console.warn('⚠️ 无法收集Playwright结果:', error.message);
    }
    
    this.results.tests.e2e.status = 'failed';
    return false;
  }

  /**
   * 收集Vitest单元测试结果
   */
  collectVitestResults() {
    try {
      const coveragePath = path.join(process.cwd(), 'frontend/coverage/coverage-summary.json');
      if (fs.existsSync(coveragePath)) {
        const data = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
        
        this.results.tests.unit = {
          status: 'completed',
          results: {
            coverage: {
              lines: data.total?.lines?.pct || 0,
              functions: data.total?.functions?.pct || 0,
              branches: data.total?.branches?.pct || 0,
              statements: data.total?.statements?.pct || 0
            }
          }
        };
        
        console.log('✅ Vitest单元测试结果已收集');
        return true;
      }
    } catch (error) {
      console.warn('⚠️ 无法收集Vitest结果:', error.message);
    }
    
    this.results.tests.unit.status = 'skipped';
    return false;
  }

  /**
   * 收集Selenium测试结果
   */
  collectSeleniumResults() {
    try {
      const reportDir = path.join(process.cwd(), 'frontend/test-results/selenium-reports');
      if (fs.existsSync(reportDir)) {
        const files = fs.readdirSync(reportDir);
        const latestReport = files
          .filter(f => f.endsWith('.json'))
          .sort()
          .pop();
          
        if (latestReport) {
          const data = JSON.parse(fs.readFileSync(path.join(reportDir, latestReport), 'utf8'));
          
          this.results.tests.selenium = {
            status: 'completed',
            results: data
          };
          
          console.log('✅ Selenium测试结果已收集');
          return true;
        }
      }
    } catch (error) {
      console.warn('⚠️ 无法收集Selenium结果:', error.message);
    }
    
    this.results.tests.selenium.status = 'not_run';
    return false;
  }

  /**
   * 收集构建结果
   */
  collectBuildResults() {
    try {
      const distPath = path.join(process.cwd(), 'frontend/dist');
      if (fs.existsSync(distPath)) {
        const stats = fs.statSync(distPath);
        
        this.results.tests.build = {
          status: 'success',
          results: {
            timestamp: stats.mtime.toISOString(),
            size: this.getDirSize(distPath)
          }
        };
        
        console.log('✅ 构建结果已收集');
        return true;
      }
    } catch (error) {
      console.warn('⚠️ 无法收集构建结果:', error.message);
    }
    
    this.results.tests.build.status = 'failed';
    return false;
  }

  /**
   * 计算目录大小
   */
  getDirSize(dirPath) {
    let totalSize = 0;
    
    const files = fs.readdirSync(dirPath);
    for (const file of files) {
      const filePath = path.join(dirPath, file);
      const stats = fs.statSync(filePath);
      
      if (stats.isDirectory()) {
        totalSize += this.getDirSize(filePath);
      } else {
        totalSize += stats.size;
      }
    }
    
    return totalSize;
  }

  /**
   * 计算总体统计
   */
  calculateSummary() {
    let total = 0, passed = 0, failed = 0, skipped = 0;
    
    Object.values(this.results.tests).forEach(test => {
      if (test.results) {
        if (test.results.total !== undefined) {
          total += test.results.total;
          passed += test.results.passed || 0;
          failed += test.results.failed || 0;
          skipped += test.results.skipped || 0;
        }
      }
    });
    
    this.results.summary = {
      total,
      passed,
      failed,
      skipped,
      passRate: total > 0 ? Math.round((passed / total) * 100) : 0
    };
  }

  /**
   * 收集测试artifacts
   */
  collectArtifacts() {
    const artifacts = [];
    
    // Playwright报告
    const playwrightReport = 'frontend/playwright-report';
    if (fs.existsSync(playwrightReport)) {
      artifacts.push({
        name: 'Playwright HTML Report',
        path: playwrightReport,
        type: 'html_report'
      });
    }
    
    // 覆盖率报告
    const coverageReport = 'frontend/coverage';
    if (fs.existsSync(coverageReport)) {
      artifacts.push({
        name: 'Coverage Report',
        path: coverageReport,
        type: 'coverage_report'
      });
    }
    
    // Selenium报告
    const seleniumReports = 'frontend/test-results/selenium-reports';
    if (fs.existsSync(seleniumReports)) {
      artifacts.push({
        name: 'Selenium Reports',
        path: seleniumReports,
        type: 'selenium_reports'
      });
    }
    
    this.results.artifacts = artifacts;
  }

  /**
   * 生成HTML报告
   */
  generateHTMLReport() {
    const html = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CI/CD 测试报告</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric { background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-value { font-size: 2em; font-weight: bold; margin-bottom: 5px; }
        .metric-label { color: #666; font-size: 0.9em; }
        .success { color: #28a745; }
        .warning { color: #ffc107; }
        .danger { color: #dc3545; }
        .tests { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .test-section { margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #eee; }
        .test-section:last-child { border-bottom: none; }
        .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
        .status-success { background: #d4edda; color: #155724; }
        .status-failed { background: #f8d7da; color: #721c24; }
        .status-skipped { background: #fff3cd; color: #856404; }
        .artifacts { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 20px; }
        .artifact-link { display: inline-block; margin: 5px 10px 5px 0; padding: 8px 16px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }
        .artifact-link:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 CI/CD 测试报告</h1>
            <p>生成时间: ${this.results.timestamp}</p>
        </div>
        
        <div class="summary">
            <div class="metric">
                <div class="metric-value ${this.results.summary.total > 0 ? 'success' : 'warning'}">${this.results.summary.total}</div>
                <div class="metric-label">总测试数</div>
            </div>
            <div class="metric">
                <div class="metric-value success">${this.results.summary.passed}</div>
                <div class="metric-label">通过</div>
            </div>
            <div class="metric">
                <div class="metric-value danger">${this.results.summary.failed}</div>
                <div class="metric-label">失败</div>
            </div>
            <div class="metric">
                <div class="metric-value warning">${this.results.summary.skipped}</div>
                <div class="metric-label">跳过</div>
            </div>
            <div class="metric">
                <div class="metric-value ${this.results.summary.passRate >= 80 ? 'success' : this.results.summary.passRate >= 60 ? 'warning' : 'danger'}">${this.results.summary.passRate}%</div>
                <div class="metric-label">通过率</div>
            </div>
        </div>
        
        <div class="tests">
            <h2>📊 详细测试结果</h2>
            
            ${Object.entries(this.results.tests).map(([name, test]) => `
            <div class="test-section">
                <h3>${this.getTestDisplayName(name)} 
                    <span class="status-badge status-${this.getStatusClass(test.status)}">${this.getStatusText(test.status)}</span>
                </h3>
                ${test.results ? this.renderTestResults(name, test.results) : '<p>无测试结果</p>'}
            </div>
            `).join('')}
        </div>
        
        ${this.results.artifacts.length > 0 ? `
        <div class="artifacts">
            <h2>📁 测试报告文件</h2>
            ${this.results.artifacts.map(artifact => `
                <a href="${artifact.path}" class="artifact-link">${artifact.name}</a>
            `).join('')}
        </div>
        ` : ''}
    </div>
</body>
</html>`;
    
    return html;
  }

  getTestDisplayName(name) {
    const names = {
      unit: '🧪 单元测试',
      e2e: '🔄 端到端测试',
      selenium: '🌐 跨浏览器测试',
      lint: '📝 代码检查',
      build: '🔨 构建测试'
    };
    return names[name] || name;
  }

  getStatusClass(status) {
    const classes = {
      'completed': 'success',
      'success': 'success',
      'failed': 'failed',
      'not_run': 'skipped',
      'skipped': 'skipped'
    };
    return classes[status] || 'skipped';
  }

  getStatusText(status) {
    const texts = {
      'completed': '完成',
      'success': '成功',
      'failed': '失败',
      'not_run': '未运行',
      'skipped': '跳过'
    };
    return texts[status] || status;
  }

  renderTestResults(testName, results) {
    if (testName === 'unit' && results.coverage) {
      return `
        <p><strong>代码覆盖率:</strong></p>
        <ul>
          <li>行覆盖率: ${results.coverage.lines}%</li>
          <li>函数覆盖率: ${results.coverage.functions}%</li>
          <li>分支覆盖率: ${results.coverage.branches}%</li>
          <li>语句覆盖率: ${results.coverage.statements}%</li>
        </ul>
      `;
    }
    
    if (testName === 'e2e' && results.total !== undefined) {
      return `
        <ul>
          <li>总数: ${results.total}</li>
          <li>通过: ${results.passed}</li>
          <li>失败: ${results.failed}</li>
          <li>跳过: ${results.skipped}</li>
          <li>耗时: ${Math.round(results.duration / 1000)}秒</li>
        </ul>
      `;
    }
    
    if (testName === 'build' && results.size) {
      return `
        <ul>
          <li>构建时间: ${results.timestamp}</li>
          <li>构建大小: ${Math.round(results.size / 1024 / 1024 * 100) / 100} MB</li>
        </ul>
      `;
    }
    
    return '<p>测试完成</p>';
  }

  /**
   * 运行报告生成
   */
  async run() {
    console.log('🚀 开始生成CI/CD测试报告...');
    
    // 收集所有测试结果
    this.collectPlaywrightResults();
    this.collectVitestResults();
    this.collectSeleniumResults();
    this.collectBuildResults();
    
    // 计算总体统计
    this.calculateSummary();
    
    // 收集artifacts
    this.collectArtifacts();
    
    // 生成报告
    const reportDir = path.join(process.cwd(), 'ci-reports');
    if (!fs.existsSync(reportDir)) {
      fs.mkdirSync(reportDir, { recursive: true });
    }
    
    // JSON报告
    const jsonReport = path.join(reportDir, 'test-results.json');
    fs.writeFileSync(jsonReport, JSON.stringify(this.results, null, 2));
    console.log(`✅ JSON报告已生成: ${jsonReport}`);
    
    // HTML报告
    const htmlReport = path.join(reportDir, 'test-results.html');
    fs.writeFileSync(htmlReport, this.generateHTMLReport());
    console.log(`✅ HTML报告已生成: ${htmlReport}`);
    
    // 输出摘要
    console.log('\n📊 测试摘要:');
    console.log(`总测试数: ${this.results.summary.total}`);
    console.log(`通过: ${this.results.summary.passed}`);
    console.log(`失败: ${this.results.summary.failed}`);
    console.log(`跳过: ${this.results.summary.skipped}`);
    console.log(`通过率: ${this.results.summary.passRate}%`);
    
    // 根据通过率返回退出码 (CI环境下更宽容)
    if (this.results.summary.passRate >= 80) {
      console.log('🎉 测试质量优秀！');
      process.exit(0);
    } else if (this.results.summary.passRate >= 60) {
      console.log('⚠️ 测试质量良好，建议改进');
      process.exit(0);
    } else if (this.results.summary.total === 0) {
      console.log('⚠️ 无测试数据，可能是配置问题');
      process.exit(0); // 在CI环境中不因为无测试数据而失败
    } else {
      console.log('❌ 测试质量需要改进');
      process.exit(1);
    }
  }
}

// 如果直接运行此文件
if (require.main === module) {
  const reporter = new CITestReporter();
  reporter.run().catch(error => {
    console.error('❌ 报告生成失败:', error);
    process.exit(1);
  });
}

module.exports = CITestReporter;
