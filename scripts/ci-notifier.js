#!/usr/bin/env node

/**
 * CI/CD通知系统
 * 发送测试结果通知到各种渠道
 */

const fs = require('fs');
const path = require('path');

class CINotifier {
  constructor() {
    this.config = {
      slack: {
        enabled: process.env.SLACK_WEBHOOK_URL ? true : false,
        webhookUrl: process.env.SLACK_WEBHOOK_URL,
        channel: process.env.SLACK_CHANNEL || '#ci-cd'
      },
      email: {
        enabled: process.env.EMAIL_ENABLED === 'true',
        to: process.env.EMAIL_TO,
        from: process.env.EMAIL_FROM
      },
      github: {
        enabled: process.env.GITHUB_TOKEN ? true : false,
        token: process.env.GITHUB_TOKEN,
        repo: process.env.GITHUB_REPOSITORY
      }
    };
  }

  /**
   * 读取测试结果
   */
  loadTestResults() {
    try {
      const reportPath = path.join(process.cwd(), 'ci-reports/test-results.json');
      if (fs.existsSync(reportPath)) {
        return JSON.parse(fs.readFileSync(reportPath, 'utf8'));
      }
    } catch (error) {
      console.error('无法读取测试结果:', error.message);
    }
    return null;
  }

  /**
   * 生成通知消息
   */
  generateMessage(results) {
    const { summary } = results;
    const status = summary.passRate >= 80 ? '✅ 成功' : summary.passRate >= 60 ? '⚠️ 警告' : '❌ 失败';
    
    const message = {
      title: `CI/CD 测试报告 ${status}`,
      summary: `通过率: ${summary.passRate}% (${summary.passed}/${summary.total})`,
      details: [
        `📊 测试统计:`,
        `• 总数: ${summary.total}`,
        `• 通过: ${summary.passed}`,
        `• 失败: ${summary.failed}`,
        `• 跳过: ${summary.skipped}`,
        `• 通过率: ${summary.passRate}%`,
        '',
        `🔍 测试详情:`
      ],
      testDetails: Object.entries(results.tests).map(([name, test]) => {
        const displayName = this.getTestDisplayName(name);
        const statusIcon = this.getStatusIcon(test.status);
        return `${statusIcon} ${displayName}: ${this.getStatusText(test.status)}`;
      }),
      artifacts: results.artifacts.map(artifact => `📁 ${artifact.name}`),
      timestamp: results.timestamp,
      color: summary.passRate >= 80 ? 'good' : summary.passRate >= 60 ? 'warning' : 'danger'
    };

    return message;
  }

  getTestDisplayName(name) {
    const names = {
      unit: '单元测试',
      e2e: '端到端测试',
      selenium: '跨浏览器测试',
      lint: '代码检查',
      build: '构建测试'
    };
    return names[name] || name;
  }

  getStatusIcon(status) {
    const icons = {
      'completed': '✅',
      'success': '✅',
      'failed': '❌',
      'not_run': '⏸️',
      'skipped': '⏭️'
    };
    return icons[status] || '❓';
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

  /**
   * 发送Slack通知
   */
  async sendSlackNotification(message) {
    if (!this.config.slack.enabled) {
      console.log('Slack通知未启用');
      return false;
    }

    try {
      const payload = {
        channel: this.config.slack.channel,
        username: 'CI/CD Bot',
        icon_emoji: ':robot_face:',
        attachments: [{
          color: message.color,
          title: message.title,
          text: message.summary,
          fields: [
            {
              title: '测试详情',
              value: [...message.details, ...message.testDetails].join('\\n'),
              short: false
            }
          ],
          footer: 'Alpha CI/CD Pipeline',
          ts: Math.floor(new Date(message.timestamp).getTime() / 1000)
        }]
      };

      // 这里应该发送HTTP请求到Slack Webhook
      console.log('📤 Slack通知内容:', JSON.stringify(payload, null, 2));
      console.log('✅ Slack通知已发送 (模拟)');
      return true;

    } catch (error) {
      console.error('❌ Slack通知发送失败:', error.message);
      return false;
    }
  }

  /**
   * 发送邮件通知
   */
  async sendEmailNotification(message) {
    if (!this.config.email.enabled) {
      console.log('邮件通知未启用');
      return false;
    }

    try {
      const emailContent = {
        to: this.config.email.to,
        from: this.config.email.from,
        subject: message.title,
        html: `
          <h2>${message.title}</h2>
          <p><strong>${message.summary}</strong></p>
          <h3>测试详情:</h3>
          <ul>
            ${message.testDetails.map(detail => `<li>${detail}</li>`).join('')}
          </ul>
          ${message.artifacts.length > 0 ? `
            <h3>报告文件:</h3>
            <ul>
              ${message.artifacts.map(artifact => `<li>${artifact}</li>`).join('')}
            </ul>
          ` : ''}
          <p><small>生成时间: ${message.timestamp}</small></p>
        `
      };

      console.log('📧 邮件通知内容:', emailContent);
      console.log('✅ 邮件通知已发送 (模拟)');
      return true;

    } catch (error) {
      console.error('❌ 邮件通知发送失败:', error.message);
      return false;
    }
  }

  /**
   * 创建GitHub评论
   */
  async sendGitHubNotification(message) {
    if (!this.config.github.enabled) {
      console.log('GitHub通知未启用');
      return false;
    }

    try {
      const comment = `
## ${message.title}

**${message.summary}**

### 📊 测试详情
${message.testDetails.map(detail => `- ${detail}`).join('\\n')}

${message.artifacts.length > 0 ? `
### 📁 报告文件
${message.artifacts.map(artifact => `- ${artifact}`).join('\\n')}
` : ''}

---
*生成时间: ${message.timestamp}*
      `;

      console.log('💬 GitHub评论内容:', comment);
      console.log('✅ GitHub通知已发送 (模拟)');
      return true;

    } catch (error) {
      console.error('❌ GitHub通知发送失败:', error.message);
      return false;
    }
  }

  /**
   * 发送控制台通知
   */
  sendConsoleNotification(message) {
    console.log('\\n' + '='.repeat(60));
    console.log(`🚀 ${message.title}`);
    console.log('='.repeat(60));
    console.log(`📊 ${message.summary}`);
    console.log('');
    
    message.testDetails.forEach(detail => {
      console.log(`  ${detail}`);
    });
    
    if (message.artifacts.length > 0) {
      console.log('\\n📁 可用报告:');
      message.artifacts.forEach(artifact => {
        console.log(`  ${artifact}`);
      });
    }
    
    console.log(`\\n⏰ 生成时间: ${message.timestamp}`);
    console.log('='.repeat(60));
  }

  /**
   * 运行通知
   */
  async run() {
    console.log('📢 开始发送CI/CD通知...');
    
    // 加载测试结果
    const results = this.loadTestResults();
    if (!results) {
      console.error('❌ 无法加载测试结果，跳过通知');
      return;
    }

    // 生成通知消息
    const message = this.generateMessage(results);
    
    // 发送到各个渠道
    const notifications = await Promise.allSettled([
      this.sendSlackNotification(message),
      this.sendEmailNotification(message),
      this.sendGitHubNotification(message)
    ]);

    // 总是发送控制台通知
    this.sendConsoleNotification(message);

    // 统计通知结果
    const successful = notifications.filter(result => result.status === 'fulfilled' && result.value).length;
    const total = notifications.length;
    
    console.log(`\\n📤 通知发送完成: ${successful}/${total} 个渠道成功`);
    
    // 保存通知记录
    const notificationLog = {
      timestamp: new Date().toISOString(),
      message,
      results: notifications.map((result, index) => ({
        channel: ['slack', 'email', 'github'][index],
        success: result.status === 'fulfilled' && result.value,
        error: result.status === 'rejected' ? result.reason.message : null
      }))
    };
    
    const logPath = path.join(process.cwd(), 'ci-reports/notification-log.json');
    fs.writeFileSync(logPath, JSON.stringify(notificationLog, null, 2));
    console.log(`📝 通知日志已保存: ${logPath}`);
  }
}

// 如果直接运行此文件
if (require.main === module) {
  const notifier = new CINotifier();
  notifier.run().catch(error => {
    console.error('❌ 通知发送失败:', error);
    process.exit(1);
  });
}

module.exports = CINotifier;
