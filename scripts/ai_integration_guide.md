# AI集成指南：如何在开发流程中引入AI

## 概述

本指南展示如何在现有的`req_to_test_pipeline.py`流水线中集成AI功能，让AI自动完成测试文件生成、代码实现等任务。

## 当前系统架构

现有系统包含：
- `req_to_test_pipeline.py` - 需求到测试的自动化流水线
- `requirement_template.md` - 标准化需求模板
- `TestGenerator` - 测试代码生成器
- `CodeGenerator` - 基础代码框架生成器

## AI集成方案

### 1. AI配置管理

创建AI配置文件 `ai_config.json`：

```json
{
  "providers": {
    "openai": {
      "api_key": "your-openai-api-key",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4",
      "max_tokens": 4000
    },
    "claude": {
      "api_key": "your-claude-api-key",
      "base_url": "https://api.anthropic.com",
      "model": "claude-3-sonnet-20240229",
      "max_tokens": 4000
    },
    "ollama": {
      "base_url": "http://localhost:11434",
      "model": "codellama:13b",
      "max_tokens": 4000
    },
    "mock": {
      "enabled": true,
      "response_template": "# AI生成的代码\n# 这是模拟模式，实际使用时会调用真实AI"
    }
  },
  "default_provider": "mock",
  "prompts": {
    "test_generation": "基于以下需求生成完整的测试代码：\n{requirement}\n\n请生成包含单元测试、集成测试的完整代码。",
    "code_implementation": "基于以下需求和测试用例实现完整的功能代码：\n需求：{requirement}\n测试：{tests}\n\n请实现所有必要的模型、视图、序列化器等。",
    "code_review": "请审查以下代码并提供改进建议：\n{code}\n\n重点关注代码质量、安全性和性能。"
  }
}
```

### 2. AI接口管理器

创建 `ai_interface.py`：

```python
import json
import requests
from typing import Dict, Any, Optional
from pathlib import Path

class AIInterface:
    """AI接口管理器"""
    
    def __init__(self, config_path: str = "ai_config.json"):
        self.config = self._load_config(config_path)
        self.provider = self.config.get("default_provider", "mock")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载AI配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._create_default_config(config_path)
    
    def _create_default_config(self, config_path: str) -> Dict[str, Any]:
        """创建默认配置文件"""
        default_config = {
            "providers": {
                "mock": {"enabled": True}
            },
            "default_provider": "mock"
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        return default_config
    
    def generate_code(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """生成代码"""
        if self.provider == "mock":
            return self._mock_generate(prompt)
        elif self.provider == "openai":
            return self._openai_generate(prompt)
        elif self.provider == "claude":
            return self._claude_generate(prompt)
        elif self.provider == "ollama":
            return self._ollama_generate(prompt)
        else:
            raise ValueError(f"不支持的AI提供商: {self.provider}")
    
    def _mock_generate(self, prompt: str) -> str:
        """模拟AI生成（用于演示）"""
        return f"""# AI生成的代码（模拟模式）
# 提示词: {prompt[:100]}...

# 这是模拟生成的代码
# 实际使用时会调用真实的AI API

def generated_function():
    pass
"""
    
    def _openai_generate(self, prompt: str) -> str:
        """OpenAI API调用"""
        config = self.config["providers"]["openai"]
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": config["model"],
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": config["max_tokens"]
        }
        
        response = requests.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenAI API调用失败: {response.text}")
    
    def _claude_generate(self, prompt: str) -> str:
        """Claude API调用"""
        # 类似OpenAI的实现
        pass
    
    def _ollama_generate(self, prompt: str) -> str:
        """Ollama本地模型调用"""
        config = self.config["providers"]["ollama"]
        data = {
            "model": config["model"],
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(
            f"{config['base_url']}/api/generate",
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            raise Exception(f"Ollama API调用失败: {response.text}")
```

### 3. 增强的流水线管理器

修改 `req_to_test_pipeline.py`，添加AI增强功能：

```python
# 在现有的PipelineManager类中添加AI功能

class AIEnhancedPipelineManager(PipelineManager):
    """AI增强的流水线管理器"""
    
    def __init__(self, project_root: str, ai_enabled: bool = False):
        super().__init__(project_root)
        self.ai_enabled = ai_enabled
        if ai_enabled:
            self.ai_interface = AIInterface()
    
    def run_ai_pipeline(self, requirement_input: str, 
                       input_type: str = 'file',
                       ai_tasks: List[str] = None) -> Dict:
        """运行AI增强的流水线"""
        
        if ai_tasks is None:
            ai_tasks = ['generate_tests', 'implement_code', 'review_code']
        
        # 先运行基础流水线
        result = self.run_pipeline(
            requirement_input, input_type,
            create_branch=True,
            generate_tests=False,  # AI会重新生成
            generate_code=False,   # AI会重新生成
            create_issue=True,
            commit_changes=False   # 最后统一提交
        )
        
        if not result['success']:
            return result
        
        req = result['requirement']
        ai_results = {}
        
        # AI生成测试
        if 'generate_tests' in ai_tasks:
            ai_results['tests'] = self._ai_generate_tests(req)
        
        # AI实现代码
        if 'implement_code' in ai_tasks:
            ai_results['code'] = self._ai_implement_code(req, ai_results.get('tests'))
        
        # AI代码审查
        if 'review_code' in ai_tasks:
            ai_results['review'] = self._ai_review_code(ai_results.get('code'))
        
        # 应用AI生成的内容
        self._apply_ai_results(req, ai_results)
        
        # 提交所有更改
        if ai_results:
            commit_msg = f"AI实现: {req.title}\n\n" + "\n".join([
                f"- {task}: 已完成" for task in ai_tasks
            ])
            self.git_manager.commit_changes(req, commit_msg)
        
        result['ai_results'] = ai_results
        return result
    
    def _ai_generate_tests(self, req: Requirement) -> Dict[str, str]:
        """AI生成测试代码"""
        prompt_template = self.ai_interface.config.get('prompts', {}).get(
            'test_generation', 
            '基于以下需求生成完整的测试代码：\n{requirement}'
        )
        
        prompt = prompt_template.format(
            requirement=f"标题: {req.title}\n描述: {req.description}\n验收标准: {req.acceptance_criteria}"
        )
        
        test_code = self.ai_interface.generate_code(prompt)
        
        # 保存测试文件
        test_files = {
            'unit_test': test_code,
            'integration_test': test_code,  # 可以分别生成
            'e2e_test': test_code
        }
        
        return test_files
    
    def _ai_implement_code(self, req: Requirement, tests: Dict[str, str] = None) -> Dict[str, str]:
        """AI实现功能代码"""
        prompt_template = self.ai_interface.config.get('prompts', {}).get(
            'code_implementation',
            '基于以下需求实现完整的功能代码：\n需求：{requirement}\n测试：{tests}'
        )
        
        tests_content = "\n\n".join(tests.values()) if tests else "无测试用例"
        
        prompt = prompt_template.format(
            requirement=f"标题: {req.title}\n描述: {req.description}",
            tests=tests_content
        )
        
        code = self.ai_interface.generate_code(prompt)
        
        # 根据组件类型分别生成代码
        code_files = {}
        for component in req.components:
            if component == 'backend':
                code_files['models'] = code
                code_files['views'] = code
                code_files['serializers'] = code
            elif component == 'frontend':
                code_files['components'] = code
                code_files['services'] = code
        
        return code_files
    
    def _ai_review_code(self, code: Dict[str, str]) -> str:
        """AI代码审查"""
        if not code:
            return "无代码需要审查"
        
        prompt_template = self.ai_interface.config.get('prompts', {}).get(
            'code_review',
            '请审查以下代码并提供改进建议：\n{code}'
        )
        
        all_code = "\n\n".join(code.values())
        prompt = prompt_template.format(code=all_code)
        
        return self.ai_interface.generate_code(prompt)
    
    def _apply_ai_results(self, req: Requirement, ai_results: Dict[str, Any]):
        """应用AI生成的结果到文件系统"""
        # 创建目录结构
        req_dir = self.project_root / 'ai_generated' / req.id
        req_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存测试文件
        if 'tests' in ai_results:
            tests_dir = req_dir / 'tests'
            tests_dir.mkdir(exist_ok=True)
            for test_type, content in ai_results['tests'].items():
                test_file = tests_dir / f"{test_type}.py"
                test_file.write_text(content, encoding='utf-8')
        
        # 保存代码文件
        if 'code' in ai_results:
            code_dir = req_dir / 'code'
            code_dir.mkdir(exist_ok=True)
            for code_type, content in ai_results['code'].items():
                code_file = code_dir / f"{code_type}.py"
                code_file.write_text(content, encoding='utf-8')
        
        # 保存审查报告
        if 'review' in ai_results:
            review_file = req_dir / 'code_review.md'
            review_file.write_text(ai_results['review'], encoding='utf-8')
```

### 4. 更新Makefile

在现有Makefile中添加AI增强选项：

```makefile
# AI增强的需求流水线
req-ai-pipeline:
	@echo "🤖 运行AI增强的需求流水线..."
	python scripts/req_to_test_pipeline.py --input $(REQ) --ai-enabled --ai-tasks generate_tests,implement_code,review_code

req-ai-pipeline-dry:
	@echo "🤖 预览AI增强的需求流水线..."
	python scripts/req_to_test_pipeline.py --input $(REQ) --ai-enabled --dry-run

req-ai-tests:
	@echo "🤖 AI生成测试代码..."
	python scripts/req_to_test_pipeline.py --input $(REQ) --ai-enabled --ai-tasks generate_tests

req-ai-code:
	@echo "🤖 AI实现功能代码..."
	python scripts/req_to_test_pipeline.py --input $(REQ) --ai-enabled --ai-tasks implement_code

req-ai-review:
	@echo "🤖 AI代码审查..."
	python scripts/req_to_test_pipeline.py --input $(REQ) --ai-enabled --ai-tasks review_code
```

## 使用方法

### 1. 配置AI提供商

选择以下任一方式：

**方式1：使用模拟模式（无需API密钥）**
```bash
# 直接使用，默认为模拟模式
make req-ai-pipeline REQ=requirements/user_avatar.md
```

**方式2：配置OpenAI**
```bash
# 编辑ai_config.json
{
  "providers": {
    "openai": {
      "api_key": "sk-your-openai-key",
      "base_url": "https://api.openai.com/v1",
      "model": "gpt-4"
    }
  },
  "default_provider": "openai"
}
```

**方式3：使用本地Ollama**
```bash
# 1. 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. 下载代码模型
ollama pull codellama:13b

# 3. 启动服务
ollama serve

# 4. 配置ai_config.json
{
  "providers": {
    "ollama": {
      "base_url": "http://localhost:11434",
      "model": "codellama:13b"
    }
  },
  "default_provider": "ollama"
}
```

### 2. 运行AI增强流水线

```bash
# 完整的AI增强流水线
make req-ai-pipeline REQ=requirements/idiomatic_expressions.md

# 只生成测试
make req-ai-tests REQ=requirements/user_avatar.md

# 只实现代码
make req-ai-code REQ=requirements/user_avatar.md

# 只进行代码审查
make req-ai-review REQ=requirements/user_avatar.md

# 预览模式（不实际执行）
make req-ai-pipeline-dry REQ=requirements/user_avatar.md
```

### 3. 查看AI生成的结果

```bash
# AI生成的文件会保存在
ai_generated/
├── user_avatar/
│   ├── tests/
│   │   ├── unit_test.py
│   │   ├── integration_test.py
│   │   └── e2e_test.py
│   ├── code/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── components.py
│   └── code_review.md
```

## 优势对比

| 特性 | 传统流水线 | AI增强流水线 |
|------|------------|-------------|
| 测试生成 | 基础模板 | 智能生成，覆盖具体业务逻辑 |
| 代码实现 | 空框架 | 完整功能实现 |
| 代码质量 | 需要手动编写 | AI审查和优化建议 |
| 开发效率 | 中等 | 显著提升 |
| 学习成本 | 低 | 中等 |
| 成本 | 免费 | 需要API费用（或本地部署） |

## 总结

通过这个AI集成方案，你可以：

1. **无缝集成**：在现有流水线基础上添加AI功能
2. **灵活配置**：支持多种AI提供商（OpenAI、Claude、Ollama、模拟模式）
3. **渐进式采用**：可以选择性启用AI功能
4. **成本可控**：提供免费的模拟模式和本地部署选项
5. **质量保证**：AI生成的代码会经过审查和优化

这样你就可以在不提供API密钥的情况下，通过模拟模式体验完整的AI增强开发流程，或者配置自己的AI服务来获得真实的AI辅助开发体验。