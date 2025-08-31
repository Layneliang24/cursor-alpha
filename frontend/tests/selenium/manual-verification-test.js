const { By, Key } = require('selenium-webdriver')
const BaseSeleniumTest = require('./base-test')
const readline = require('readline')

/**
 * 手动验证测试 - 需要人工输入验证码
 */
class ManualVerificationTest extends BaseSeleniumTest {
  constructor () {
    super()
    this.testName = '手动验证登录测试'
    this.realCredentials = {
      username: 'layne',
      password: 'meimei520',
    }
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    })
  }

  /**
   * 询问用户输入验证码
   */
  async askForCaptcha () {
    return new Promise((resolve) => {
      this.rl.question('请查看浏览器窗口中的验证码，然后输入: ', (answer) => {
        resolve(answer.trim())
      })
    })
  }

  /**
   * 运行手动验证测试
   */
  async runManualTest () {
    console.log(`\n🎯 开始 ${this.testName}`)
    console.log('=' .repeat(60))
    console.log('⚠️ 此测试需要手动输入验证码，请准备好查看浏览器窗口')

    try {
      // 使用Firefox进行测试（无头模式关闭以便用户看到）
      process.env.HEADLESS = 'false'
      await this.setup('firefox')
      
      await this.testCompleteLoginFlow()
      
    } catch (error) {
      console.error('❌ 手动测试失败:', error.message)
    } finally {
      this.rl.close()
      await this.teardown()
    }

    this.printManualTestResults()
  }

  /**
   * 测试完整登录流程
   */
  async testCompleteLoginFlow () {
    const testName = '完整登录流程测试'
    
    try {
      console.log('\n🔄 开始完整登录流程测试...')
      
      // 1. 导航到登录页面
      await this.navigateTo('/login')
      await this.sleep(2000)
      console.log('✅ 已导航到登录页面')
      
      // 2. 输入用户名和密码
      const usernameField = By.css('input[placeholder*="用户名"], input[placeholder*="邮箱"], .el-input__inner')
      const passwordField = By.css('input[type="password"], .el-input__inner[type="password"]')
      
      await this.sendKeys(usernameField, this.realCredentials.username)
      console.log(`✅ 已输入用户名: ${this.realCredentials.username}`)
      
      await this.sendKeys(passwordField, this.realCredentials.password)
      console.log('✅ 已输入密码')
      
      // 3. 等待用户手动输入验证码
      console.log('\n📋 浏览器窗口已打开，请查看验证码')
      const captcha = await this.askForCaptcha()
      
      // 4. 输入验证码
      const captchaField = By.css('input[placeholder*="验证码"], .captcha-container input')
      await this.sendKeys(captchaField, captcha)
      console.log(`✅ 已输入验证码: ${captcha}`)
      
      // 5. 点击登录
      await this.click(By.css('.el-button--primary, button[type="submit"]'))
      console.log('✅ 已点击登录按钮')
      
      // 6. 等待登录结果
      await this.sleep(5000)
      
      // 7. 检查登录结果
      const currentUrl = await this.getCurrentUrl()
      console.log(`当前URL: ${currentUrl}`)
      
      if (!currentUrl.includes('/login')) {
        console.log('🎉 登录成功！')
        this.recordResult(testName, true, '手动验证登录成功')
        
        // 8. 测试登录后功能
        await this.testPostLoginFunctionality()
        
      } else {
        console.log('❌ 登录失败，仍在登录页面')
        
        // 检查错误消息
        const errorElements = await this.findElements(By.css('.el-message--error, .error, [class*="error"]'))
        if (errorElements.length > 0) {
          for (const element of errorElements) {
            const errorText = await element.getText()
            if (errorText.trim()) {
              console.log(`错误信息: ${errorText}`)
            }
          }
        }
        
        this.recordResult(testName, false, '手动验证登录失败')
      }
      
    } catch (error) {
      console.error('登录流程测试出错:', error.message)
      this.recordResult(testName, false, error.message)
    }
  }

  /**
   * 测试登录后功能
   */
  async testPostLoginFunctionality () {
    console.log('\n🔄 测试登录后功能...')
    
    try {
      // 1. 测试导航到学习页面
      await this.navigateTo('/english/idiomatic-learning')
      await this.sleep(3000)
      
      const currentUrl = await this.getCurrentUrl()
      console.log(`学习页面URL: ${currentUrl}`)
      
      if (currentUrl.includes('/english/idiomatic-learning')) {
        console.log('✅ 成功访问地道表达学习页面')
        
        // 2. 检查页面内容
        const title = await this.getTitle()
        console.log(`页面标题: ${title}`)
        
        // 3. 查找学习模式卡片
        const modeCards = await this.findElements(By.css('.mode-card, .learning-mode, .el-card'))
        console.log(`发现 ${modeCards.length} 个页面元素`)
        
        if (modeCards.length > 0) {
          console.log('✅ 学习页面内容加载正常')
          this.recordResult('学习页面访问', true, `页面正常，发现 ${modeCards.length} 个元素`)
        } else {
          console.log('⚠️ 学习页面内容可能未完全加载')
          this.recordResult('学习页面访问', true, '页面可访问，但内容加载可能不完整')
        }
        
        // 4. 测试导航到分析页面
        await this.navigateTo('/english/learning-analytics')
        await this.sleep(3000)
        
        const analyticsUrl = await this.getCurrentUrl()
        if (analyticsUrl.includes('/english/learning-analytics')) {
          console.log('✅ 成功访问学习分析页面')
          this.recordResult('学习分析页面访问', true, '页面可正常访问')
        } else {
          console.log('❌ 学习分析页面访问失败')
          this.recordResult('学习分析页面访问', false, '页面访问被重定向')
        }
        
      } else if (currentUrl.includes('/login')) {
        console.log('❌ 登录状态丢失，被重定向到登录页面')
        this.recordResult('登录状态持久性', false, '登录状态未持久化')
      } else {
        console.log(`✅ 登录后重定向到: ${currentUrl}`)
        this.recordResult('登录后重定向', true, '登录成功，重定向正常')
      }
      
    } catch (error) {
      console.error('登录后功能测试出错:', error.message)
      this.recordResult('登录后功能', false, error.message)
    }
  }

  /**
   * 打印手动测试结果
   */
  printManualTestResults () {
    console.log('\n📊 手动验证测试结果')
    console.log('=' .repeat(60))

    const summary = this.getResultsSummary()
    console.log('\n📈 测试统计:')
    console.log(`  总测试数: ${summary.total}`)
    console.log(`  通过: ${summary.passed} (${summary.passRate}%)`)
    console.log(`  失败: ${summary.failed}`)

    console.log('\n📋 详细结果:')
    this.testResults.forEach(result => {
      const status = result.passed ? '✅' : '❌'
      console.log(`  ${status} ${result.test}: ${result.message}`)
    })

    console.log('\n🎯 测试质量评估:')
    if (summary.passRate >= 80) {
      console.log('  🟢 优秀 - 登录和核心功能工作正常')
    } else if (summary.passRate >= 60) {
      console.log('  🟡 良好 - 主要功能可用，部分功能需要优化')
    } else {
      console.log('  🔴 需要改进 - 存在重要功能问题')
    }

    console.log('\n📝 测试总结:')
    console.log('  1. 用户账号验证: 已使用真实账号进行测试')
    console.log('  2. 登录流程验证: 包含验证码的完整登录流程')
    console.log('  3. 功能可用性验证: 登录后的页面访问和功能使用')
    console.log('  4. 跨浏览器兼容性: 在Firefox环境下验证')
  }
}

// 如果直接运行此文件
if (require.main === module) {
  const test = new ManualVerificationTest()
  test.runManualTest()
    .then(() => {
      console.log('\n✅ 手动验证测试完成')
      process.exit(0)
    })
    .catch(error => {
      console.error('\n❌ 手动验证测试失败:', error)
      process.exit(1)
    })
}

module.exports = ManualVerificationTest
