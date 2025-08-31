#!/usr/bin/env node

/**
 * CI/CD性能监控器
 * 监控构建时间、测试执行时间、资源使用情况
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class PerformanceMonitor {
  constructor() {
    this.metrics = {
      timestamp: new Date().toISOString(),
      build: {},
      tests: {},
      resources: {},
      recommendations: []
    };
    this.startTime = Date.now();
  }

  /**
   * 监控构建性能
   */
  monitorBuildPerformance() {
    try {
      const distPath = path.join(process.cwd(), 'frontend/dist');
      const nodeModulesPath = path.join(process.cwd(), 'frontend/node_modules');
      
      if (fs.existsSync(distPath)) {
        this.metrics.build = {
          distSize: this.getDirSize(distPath),
          distSizeMB: Math.round(this.getDirSize(distPath) / 1024 / 1024 * 100) / 100,
          nodeModulesSize: fs.existsSync(nodeModulesPath) ? this.getDirSize(nodeModulesPath) : 0,
          files: this.countFiles(distPath),
          largestFiles: this.getLargestFiles(distPath)
        };

        // 性能建议
        if (this.metrics.build.distSizeMB > 10) {
          this.metrics.recommendations.push({
            type: 'build',
            severity: 'warning',
            message: `构建产物过大 (${this.metrics.build.distSizeMB}MB)，建议优化代码分割和资源压缩`
          });
        }

        console.log(`✅ 构建性能监控完成 - 构建大小: ${this.metrics.build.distSizeMB}MB`);
      }
    } catch (error) {
      console.warn('⚠️ 构建性能监控失败:', error.message);
    }
  }

  /**
   * 监控测试性能
   */
  monitorTestPerformance() {
    try {
      const testResults = [];
      
      // 检查Playwright测试结果
      const playwrightReport = path.join(process.cwd(), 'frontend/test-results/results.json');
      if (fs.existsSync(playwrightReport)) {
        const data = JSON.parse(fs.readFileSync(playwrightReport, 'utf8'));
        testResults.push({
          name: 'E2E Tests',
          duration: data.stats?.duration || 0,
          durationSec: Math.round((data.stats?.duration || 0) / 1000),
          tests: data.stats?.total || 0
        });
      }

      // 检查Selenium测试结果
      const seleniumReportsDir = path.join(process.cwd(), 'frontend/test-results/selenium-reports');
      if (fs.existsSync(seleniumReportsDir)) {
        const files = fs.readdirSync(seleniumReportsDir);
        const latestReport = files.filter(f => f.endsWith('.json')).sort().pop();
        
        if (latestReport) {
          const data = JSON.parse(fs.readFileSync(path.join(seleniumReportsDir, latestReport), 'utf8'));
          testResults.push({
            name: 'Selenium Tests',
            duration: data.totalDuration || 0,
            durationSec: Math.round((data.totalDuration || 0) / 1000),
            tests: data.totalTests || 0
          });
        }
      }

      this.metrics.tests = {
        results: testResults,
        totalDuration: testResults.reduce((sum, test) => sum + test.duration, 0),
        totalDurationSec: testResults.reduce((sum, test) => sum + test.durationSec, 0),
        totalTests: testResults.reduce((sum, test) => sum + test.tests, 0)
      };

      // 性能建议
      if (this.metrics.tests.totalDurationSec > 300) { // 5分钟
        this.metrics.recommendations.push({
          type: 'tests',
          severity: 'warning',
          message: `测试执行时间过长 (${this.metrics.tests.totalDurationSec}秒)，建议优化测试并行度或减少测试数量`
        });
      }

      console.log(`✅ 测试性能监控完成 - 总耗时: ${this.metrics.tests.totalDurationSec}秒`);
    } catch (error) {
      console.warn('⚠️ 测试性能监控失败:', error.message);
    }
  }

  /**
   * 监控资源使用情况
   */
  monitorResourceUsage() {
    try {
      // 获取系统信息
      const totalTime = Date.now() - this.startTime;
      
      this.metrics.resources = {
        totalExecutionTime: totalTime,
        totalExecutionTimeSec: Math.round(totalTime / 1000),
        memoryUsage: process.memoryUsage(),
        cpuUsage: process.cpuUsage(),
        platform: process.platform,
        nodeVersion: process.version
      };

      // 性能建议
      if (this.metrics.resources.totalExecutionTimeSec > 600) { // 10分钟
        this.metrics.recommendations.push({
          type: 'resources',
          severity: 'error',
          message: `CI/CD流水线执行时间过长 (${this.metrics.resources.totalExecutionTimeSec}秒)，建议优化构建和测试流程`
        });
      }

      console.log(`✅ 资源监控完成 - 总执行时间: ${this.metrics.resources.totalExecutionTimeSec}秒`);
    } catch (error) {
      console.warn('⚠️ 资源监控失败:', error.message);
    }
  }

  /**
   * 计算目录大小
   */
  getDirSize(dirPath) {
    let totalSize = 0;
    
    try {
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
    } catch (error) {
      // 忽略权限错误等
    }
    
    return totalSize;
  }

  /**
   * 统计文件数量
   */
  countFiles(dirPath) {
    let fileCount = 0;
    
    try {
      const files = fs.readdirSync(dirPath);
      for (const file of files) {
        const filePath = path.join(dirPath, file);
        const stats = fs.statSync(filePath);
        
        if (stats.isDirectory()) {
          fileCount += this.countFiles(filePath);
        } else {
          fileCount++;
        }
      }
    } catch (error) {
      // 忽略错误
    }
    
    return fileCount;
  }

  /**
   * 获取最大的文件
   */
  getLargestFiles(dirPath, maxFiles = 5) {
    const files = [];
    
    try {
      const dirFiles = fs.readdirSync(dirPath);
      for (const file of dirFiles) {
        const filePath = path.join(dirPath, file);
        const stats = fs.statSync(filePath);
        
        if (stats.isFile()) {
          files.push({
            name: path.relative(process.cwd(), filePath),
            size: stats.size,
            sizeMB: Math.round(stats.size / 1024 / 1024 * 100) / 100
          });
        } else if (stats.isDirectory()) {
          files.push(...this.getLargestFiles(filePath, maxFiles));
        }
      }
    } catch (error) {
      // 忽略错误
    }
    
    return files
      .sort((a, b) => b.size - a.size)
      .slice(0, maxFiles);
  }

  /**
   * 生成性能报告
   */
  generateReport() {
    const report = {
      ...this.metrics,
      summary: {
        buildSizeMB: this.metrics.build.distSizeMB || 0,
        testDurationSec: this.metrics.tests.totalDurationSec || 0,
        totalExecutionTimeSec: this.metrics.resources.totalExecutionTimeSec || 0,
        recommendationsCount: this.metrics.recommendations.length,
        overallScore: this.calculateOverallScore()
      }
    };

    return report;
  }

  /**
   * 计算总体性能评分
   */
  calculateOverallScore() {
    let score = 100;
    
    // 构建大小扣分
    if (this.metrics.build.distSizeMB > 20) score -= 30;
    else if (this.metrics.build.distSizeMB > 10) score -= 15;
    else if (this.metrics.build.distSizeMB > 5) score -= 5;
    
    // 测试时间扣分
    if (this.metrics.tests.totalDurationSec > 600) score -= 30;
    else if (this.metrics.tests.totalDurationSec > 300) score -= 15;
    else if (this.metrics.tests.totalDurationSec > 120) score -= 5;
    
    // 总执行时间扣分
    if (this.metrics.resources.totalExecutionTimeSec > 900) score -= 25;
    else if (this.metrics.resources.totalExecutionTimeSec > 600) score -= 10;
    
    return Math.max(0, score);
  }

  /**
   * 输出性能摘要
   */
  printSummary() {
    const summary = this.generateReport().summary;
    
    console.log('\n' + '='.repeat(60));
    console.log('🚀 CI/CD 性能报告');
    console.log('='.repeat(60));
    console.log(`📦 构建大小: ${summary.buildSizeMB}MB`);
    console.log(`⏱️ 测试耗时: ${summary.testDurationSec}秒`);
    console.log(`🕒 总执行时间: ${summary.totalExecutionTimeSec}秒`);
    console.log(`📊 性能评分: ${summary.overallScore}/100`);
    
    if (this.metrics.recommendations.length > 0) {
      console.log('\n💡 性能建议:');
      this.metrics.recommendations.forEach((rec, index) => {
        const icon = rec.severity === 'error' ? '🔴' : rec.severity === 'warning' ? '🟡' : '🔵';
        console.log(`${index + 1}. ${icon} ${rec.message}`);
      });
    } else {
      console.log('\n✅ 性能表现良好，无需优化建议');
    }
    
    console.log('='.repeat(60));
  }

  /**
   * 运行性能监控
   */
  async run() {
    console.log('🔍 开始CI/CD性能监控...');
    
    this.monitorBuildPerformance();
    this.monitorTestPerformance();
    this.monitorResourceUsage();
    
    // 生成报告
    const report = this.generateReport();
    
    // 保存报告
    const reportsDir = path.join(process.cwd(), 'ci-reports');
    if (!fs.existsSync(reportsDir)) {
      fs.mkdirSync(reportsDir, { recursive: true });
    }
    
    const reportPath = path.join(reportsDir, 'performance-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`📄 性能报告已保存: ${reportPath}`);
    
    // 输出摘要
    this.printSummary();
    
    // 根据性能评分决定退出码
    const score = report.summary.overallScore;
    if (score >= 80) {
      console.log('\n🎉 性能表现优秀！');
      process.exit(0);
    } else if (score >= 60) {
      console.log('\n⚠️ 性能表现良好，建议优化');
      process.exit(0);
    } else {
      console.log('\n❌ 性能需要改进');
      process.exit(1);
    }
  }
}

// 如果直接运行此文件
if (require.main === module) {
  const monitor = new PerformanceMonitor();
  monitor.run().catch(error => {
    console.error('❌ 性能监控失败:', error);
    process.exit(1);
  });
}

module.exports = PerformanceMonitor;
