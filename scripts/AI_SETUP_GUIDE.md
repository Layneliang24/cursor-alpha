# AI集成设置指南

## 概述

本项目已集成AI功能，支持多种AI提供商来自动生成测试代码、实现代码和代码审查。目前支持的AI提供商包括：

- **OpenAI** (GPT-4, GPT-3.5等)
- **Claude** (Anthropic)
- **Ollama** (本地模型)
- **Mock** (模拟模式，用于演示和测试)

## 快速开始

### 1. 使用模拟模式（无需配置）

```bash
# 测试AI接口
python scripts/ai_interface.py --test

# 列出所有提供商状态
python scripts/ai_interface.py --list

# 测试代码生成
python scripts/ai_interface.py --prompt "生成一个用户注册的API视图"
```

### 2. 配置真实AI提供商

编辑 `scripts/ai_config.json` 文件：

#### OpenAI配置
```json
{
  "providers": {
    "openai": {
      "api_key": "sk-your-actual-openai-api-key",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4",
      "max_tokens": 4000
    }
  },
  "default_provider": "openai"
}
```

#### Claude配置
```json
{
  "providers": {
    "claude": {
      "api_key": "your-claude-api-key",
      "base_url": "https://api.anthropic.com",
      "model": "claude-3-sonnet-20240229",
      "max_tokens": 4000
    }
  },
  "default_provider": "claude"
}
```

#### Ollama配置（本地模型）
```json
{
  "providers": {
    "ollama": {
      "base_url": "http://localhost:11434",
      "model": "codellama:13b",
      "max_tokens": 4000
    }
  },
  "default_provider": "ollama"
}
```

## 获取API密钥

### OpenAI API密钥
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. 注册/登录账户
3. 进入 API Keys 页面
4. 点击 "Create new secret key"
5. 复制生成的密钥（格式：sk-...）

### Claude API密钥
1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册/登录账户
3. 进入 API Keys 页面
4. 创建新的API密钥
5. 复制生成的密钥

### Ollama本地模型
1. 安装Ollama：访问 [Ollama官网](https://ollama.ai/)
2. 下载并安装适合你系统的版本
3. 启动Ollama服务：
   ```bash
   ollama serve
   ```
4. 下载代码模型：
   ```bash
   ollama pull codellama:13b
   # 或者其他模型
   ollama pull deepseek-coder:6.7b
   ```

## 使用方法

### 命令行使用

```bash
# 切换AI提供商
python scripts/ai_interface.py --provider openai

# 测试连接
python scripts/ai_interface.py --test

# 生成代码
python scripts/ai_interface.py --prompt "创建一个Django REST API用于用户管理"
```

### 在开发流程中使用

1. **创建需求文档**（按照现有模板）
2. **运行AI增强流水线**：
   ```bash
   make req-pipeline-ai REQ=path/to/requirement.md
   ```
3. **AI会自动**：
   - 生成测试代码
   - 实现功能代码
   - 进行代码审查
   - 创建Git分支和提交

### Python代码中使用

```python
from scripts.ai_interface import AIInterface

# 初始化AI接口
ai = AIInterface()

# 设置提供商
ai.set_provider('openai')

# 生成代码
code = ai.generate_code("创建一个用户认证的Django视图")
print(code)

# 测试连接
if ai.test_connection():
    print("AI连接正常")
```

## 成本考虑

### OpenAI定价（参考）
- GPT-4: ~$0.03/1K tokens (输入) + $0.06/1K tokens (输出)
- GPT-3.5-turbo: ~$0.001/1K tokens (输入) + $0.002/1K tokens (输出)

### Claude定价（参考）
- Claude-3-Sonnet: ~$0.003/1K tokens (输入) + $0.015/1K tokens (输出)

### 节省成本的建议
1. **使用模拟模式**进行开发和测试
2. **选择合适的模型**（GPT-3.5比GPT-4便宜很多）
3. **限制max_tokens**参数
4. **使用本地Ollama模型**（免费但需要本地计算资源）

## 故障排除

### 常见问题

1. **API密钥无效**
   ```
   错误：请在ai_config.json中配置有效的OpenAI API密钥
   解决：检查API密钥是否正确，是否有足够的配额
   ```

2. **Ollama连接失败**
   ```
   错误：无法连接到Ollama服务
   解决：确保Ollama服务正在运行（ollama serve）
   ```

3. **网络连接问题**
   ```
   解决：检查网络连接，考虑使用代理或VPN
   ```

### 调试模式

```bash
# 查看详细错误信息
python scripts/ai_interface.py --test --provider openai

# 检查配置文件
cat scripts/ai_config.json
```

## 安全注意事项

1. **保护API密钥**：
   - 不要将API密钥提交到Git仓库
   - 使用环境变量存储敏感信息
   - 定期轮换API密钥

2. **代码审查**：
   - AI生成的代码需要人工审查
   - 注意安全漏洞和最佳实践
   - 测试生成的代码

3. **数据隐私**：
   - 不要将敏感数据发送给AI服务
   - 了解AI提供商的数据使用政策

## 扩展和自定义

### 添加新的AI提供商

1. 在 `ai_interface.py` 中添加新的生成方法
2. 在 `ai_config.json` 中添加配置
3. 更新提供商列表

### 自定义提示模板

编辑 `ai_config.json` 中的 `prompts` 部分：

```json
{
  "prompts": {
    "custom_prompt": "你的自定义提示模板：{requirement}"
  }
}
```

## 支持和反馈

如果遇到问题或有改进建议，请：

1. 检查本文档的故障排除部分
2. 查看 `scripts/ai_interface.py` 的源代码
3. 提交Issue或Pull Request

---

**注意**：AI生成的代码仅供参考，请务必进行人工审查和测试后再用于生产环境。