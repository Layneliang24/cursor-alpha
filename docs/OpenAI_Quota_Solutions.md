# OpenAI配额问题解决方案

## 🔍 问题诊断

根据测试结果，您的OpenAI账户遇到以下问题：

### ❌ 主要问题
1. **配额不足 (429错误)**: `insufficient_quota`
2. **模型访问权限 (404错误)**: `model_not_found`
3. **账户状态异常**: 无法获取使用情况

## 🛠️ 解决方案

### 方案1: 检查并修复账户状态

#### 1.1 检查账户余额
访问 [OpenAI Platform Billing](https://platform.openai.com/account/billing)
- 查看当前余额
- 检查是否有未付账单
- 确认账户状态

#### 1.2 设置支付方式
1. 访问 [OpenAI Platform Billing](https://platform.openai.com/account/billing)
2. 点击 "Add payment method"
3. 添加信用卡或借记卡
4. 设置支出限制（可选）

#### 1.3 重新生成API密钥
1. 访问 [OpenAI API Keys](https://platform.openai.com/api-keys)
2. 删除旧的API密钥
3. 创建新的API密钥
4. 更新环境变量

```bash
# 设置新的API密钥
export OPENAI_API_KEY="sk-your-new-api-key"
```

### 方案2: 使用免费替代方案

#### 2.1 申请新的免费账户
1. 使用不同的邮箱注册新的OpenAI账户
2. 获得新的5美元免费额度
3. 生成新的API密钥

#### 2.2 使用Claude API
1. 访问 [Anthropic Claude](https://console.anthropic.com/)
2. 注册账户获得免费额度
3. 生成API密钥

```bash
# 设置Claude API密钥
export ANTHROPIC_API_KEY="sk-ant-your-api-key"
```

#### 2.3 使用本地AI (推荐)
安装Ollama获得完全免费的AI体验：

```bash
# 1. 下载并安装Ollama
# 访问: https://ollama.ai/

# 2. 启动Ollama服务
ollama serve

# 3. 下载模型
ollama pull llama2
ollama pull codellama

# 4. 使用本地AI流水线
python scripts/local_ai_pipeline.py --input your_requirement.md
```

### 方案3: 优化API使用

#### 3.1 使用更便宜的模型
```python
# 使用gpt-3.5-turbo而不是gpt-4
response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # 更便宜
    messages=[{"role": "user", "content": prompt}],
    max_tokens=1000  # 限制token使用
)
```

#### 3.2 实现缓存机制
```python
import hashlib
import json
import os

def get_cached_response(prompt, cache_dir="cache"):
    """获取缓存的响应"""
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
    cache_file = os.path.join(cache_dir, f"{prompt_hash}.json")
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)['response']
    return None

def cache_response(prompt, response, cache_dir="cache"):
    """缓存响应"""
    os.makedirs(cache_dir, exist_ok=True)
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
    cache_file = os.path.join(cache_dir, f"{prompt_hash}.json")
    
    with open(cache_file, 'w') as f:
        json.dump({'prompt': prompt, 'response': response}, f)
```

## 🚀 推荐解决方案

### 立即解决方案
1. **使用本地AI流水线** (无需API密钥)
2. **检查账户状态** 并设置支付方式
3. **重新生成API密钥**

### 长期解决方案
1. **安装Ollama** 获得完全免费的AI体验
2. **实现缓存机制** 减少API调用
3. **使用更便宜的模型** 控制成本

## 📊 成本对比

| 方案 | 成本 | 可用性 | 推荐度 |
|------|------|--------|--------|
| 本地AI (Ollama) | 免费 | 高 | ⭐⭐⭐⭐⭐ |
| OpenAI GPT-3.5 | $0.002/1K tokens | 高 | ⭐⭐⭐⭐ |
| OpenAI GPT-4 | $0.03/1K tokens | 高 | ⭐⭐⭐ |
| Claude API | 免费额度 | 高 | ⭐⭐⭐⭐ |

## 🔧 快速修复步骤

### 步骤1: 立即使用本地AI
```bash
# 使用本地AI流水线（无需API密钥）
python scripts/local_ai_pipeline.py --input docs/spec/requirements/idiomatic_expressions_enhancement.md
```

### 步骤2: 检查账户
1. 访问 https://platform.openai.com/account/billing
2. 检查余额和支付方式
3. 如有问题，联系OpenAI支持

### 步骤3: 重新生成密钥
1. 访问 https://platform.openai.com/api-keys
2. 删除旧密钥
3. 创建新密钥
4. 更新环境变量

### 步骤4: 测试修复
```bash
python check_openai_account.py
```

## 📞 获取帮助

如果问题持续存在：
1. **OpenAI支持**: https://help.openai.com/
2. **社区论坛**: https://community.openai.com/
3. **GitHub Issues**: 在项目仓库提交问题

## 🎯 总结

**推荐优先级**:
1. 🥇 **本地AI流水线** - 立即可用，完全免费
2. 🥈 **检查账户状态** - 解决根本问题
3. 🥉 **重新生成API密钥** - 排除密钥问题

选择最适合您需求的方案，AI增强流水线将继续为您提供智能化的开发体验！ 