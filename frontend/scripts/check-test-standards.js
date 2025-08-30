#!/usr/bin/env node

/**
 * 测试规范检查脚本
 * 使用方法：node scripts/check-test-standards.js
 */

const fs = require('fs')
const path = require('path')
const glob = require('glob')

// 颜色输出
const colors = {
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
}

function log (message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`)
}

// 检查规则
const rules = {
  // 文件命名规范
  fileName: {
    pattern: /^[A-Z][a-zA-Z0-9]*\.spec\.ts$/,
    message: '测试文件应该使用 PascalCase 并以 .spec.ts 结尾',
  },
  
  // 测试套件命名规范
  describeName: {
    pattern: /^[A-Z][a-zA-Z0-9]*\.vue Component$|^[a-z][a-zA-Z0-9]*\.js API$|^[a-z][a-zA-Z0-9]* utility$/,
    message: '测试套件应该使用正确的命名格式：ComponentName.vue Component 或 apiName.js API',
  },
  
  // 测试用例命名规范
  testName: {
    pattern: /^应该.*$/,
    message: '测试用例应该使用中文描述，以"应该"开头',
  },
  
  // 必需的结构
  requiredStructure: [
    'import { describe, it, expect, beforeEach, vi, afterEach }',
    'beforeEach(() => {',
    'afterEach(() => {',
    'vi.clearAllMocks()',
    'wrapper.unmount()',
  ],
  
  // 必需的测试分组
  requiredGroups: [
    '基础渲染',
    '属性验证',
    '用户交互',
    '边界情况',
    '数据流测试',  // ⭐ 新增
    '集成测试',     // ⭐ 新增
  ],
}

// 检查单个文件
function checkTestFile (filePath) {
  const content = fs.readFileSync(filePath, 'utf-8')
  const fileName = path.basename(filePath)
  const issues = []
  
  log(`检查文件: ${fileName}`, 'blue')
  
  // 检查文件名
  if (!rules.fileName.pattern.test(fileName)) {
    issues.push(`文件名: ${rules.fileName.message}`)
  }
  
  // 检查测试套件命名
  const describeMatches = content.match(/describe\('([^']+)'/g)
  if (describeMatches) {
    describeMatches.forEach(match => {
      const name = match.match(/describe\('([^']+)'/)[1]
      if (!rules.describeName.pattern.test(name)) {
        issues.push(`测试套件命名: ${rules.describeName.message} (${name})`)
      }
    })
  }
  
  // 检查测试用例命名
  const itMatches = content.match(/it\('([^']+)'/g)
  if (itMatches) {
    itMatches.forEach(match => {
      const name = match.match(/it\('([^']+)'/)[1]
      if (!rules.testName.pattern.test(name)) {
        issues.push(`测试用例命名: ${rules.testName.message} (${name})`)
      }
    })
  }
  
  // 检查必需的结构
  rules.requiredStructure.forEach(structure => {
    if (!content.includes(structure)) {
      issues.push(`缺少必需结构: ${structure}`)
    }
  })
  
  // 检查测试分组
  const foundGroups = []
  rules.requiredGroups.forEach(group => {
    if (content.includes(`describe('${group}'`)) {
      foundGroups.push(group)
    }
  })
  
  if (foundGroups.length < 2) {
    issues.push(`缺少必需的测试分组，至少需要包含: ${rules.requiredGroups.slice(0, 2).join(', ')}`)
  }
  
  // 检查覆盖率要求
  if (content.includes('mount(') && !content.includes('--coverage')) {
    issues.push('真实组件测试应该检查覆盖率')
  }
  
  // 检查异步测试
  const asyncTests = content.match(/it\('.*', async \(\) => \{/g)
  if (asyncTests) {
    asyncTests.forEach(test => {
      const testName = test.match(/it\('([^']+)'/)[1]
      if (!content.includes('await nextTick()') && testName.includes('应该')) {
        issues.push(`异步测试应该使用 await nextTick(): ${testName}`)
      }
    })
  }
  
  return issues
}

// 主函数
function main () {
  log('🔍 开始检查测试规范...', 'green')
  
  // 查找所有测试文件
  const testFiles = glob.sync('src/**/*.spec.ts')
  
  if (testFiles.length === 0) {
    log('❌ 未找到测试文件', 'red')
    process.exit(1)
  }
  
  log(`📁 找到 ${testFiles.length} 个测试文件`, 'green')
  
  let totalIssues = 0
  let passedFiles = 0
  
  testFiles.forEach(file => {
    const issues = checkTestFile(file)
    
    if (issues.length === 0) {
      log(`✅ ${path.basename(file)} - 通过`, 'green')
      passedFiles++
    } else {
      log(`❌ ${path.basename(file)} - ${issues.length} 个问题`, 'red')
      issues.forEach(issue => {
        log(`   - ${issue}`, 'yellow')
      })
      totalIssues += issues.length
    }
  })
  
  // 输出总结
  log('\n📊 检查总结:', 'blue')
  log(`✅ 通过文件: ${passedFiles}/${testFiles.length}`, 'green')
  log(`❌ 问题总数: ${totalIssues}`, totalIssues > 0 ? 'red' : 'green')
  
  if (totalIssues === 0) {
    log('🎉 所有测试文件都符合规范！', 'green')
  } else {
    log('⚠️  请修复上述问题以确保测试质量', 'yellow')
    process.exit(1)
  }
}

// 运行检查
if (require.main === module) {
  main()
}

module.exports = { checkTestFile, rules } 