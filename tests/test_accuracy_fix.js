// 测试正确率计算修复
// 这个脚本模拟正确率计算的逻辑

function testAccuracyCalculation() {
  console.log('=== 测试正确率计算修复 ===')
  
  // 模拟数据
  const words = [
    { word: 'hello' },    // 5个字符
    { word: 'world' },    // 5个字符
    { word: 'test' }      // 4个字符
  ]
  
  // 总字符数
  const totalChars = words.reduce((sum, word) => sum + word.word.length, 0)
  console.log(`总字符数: ${totalChars}`)
  
  // 模拟按键错误记录
  const keyMistakes = {
    'h': ['h'],      // 1个错误
    'e': ['e', 'e'], // 2个错误
    'l': ['l']       // 1个错误
  }
  
  // 计算错误总数
  const totalErrors = Object.values(keyMistakes).reduce((sum, mistakes) => sum + mistakes.length, 0)
  console.log(`总错误数: ${totalErrors}`)
  
  // 计算正确率
  const correctChars = totalChars - totalErrors
  const accuracy = totalChars > 0 ? (correctChars / totalChars) * 100 : 0
  
  console.log(`正确字符数: ${correctChars}`)
  console.log(`计算出的正确率: ${accuracy.toFixed(2)}%`)
  
  // 验证结果
  const expectedAccuracy = ((14 - 4) / 14) * 100 // (14-4)/14 * 100 = 71.43%
  console.log(`期望的正确率: ${expectedAccuracy.toFixed(2)}%`)
  
  if (Math.abs(accuracy - expectedAccuracy) < 0.01) {
    console.log('✅ 正确率计算正确！')
  } else {
    console.log('❌ 正确率计算错误！')
  }
  
  // 显示每个单词的错误分布
  console.log('\n错误分布:')
  Object.entries(keyMistakes).forEach(([key, mistakes]) => {
    console.log(`  按键 '${key}': ${mistakes.length} 次错误`)
  })
}

// 运行测试
testAccuracyCalculation() 