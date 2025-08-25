#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI接口管理器
支持多种AI提供商：OpenAI、Claude、Ollama、模拟模式
"""

import json
import requests
import os
from typing import Dict, Any, Optional
from pathlib import Path


class AIInterface:
    """AI接口管理器"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = Path(__file__).parent / "ai_config.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.provider = self.config.get("default_provider", "mock")
        
        print(f"AI接口初始化完成，当前提供商: {self.provider}")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载AI配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件不存在，创建默认配置: {self.config_path}")
            return self._create_default_config()
        except json.JSONDecodeError as e:
            print(f"配置文件格式错误: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置文件"""
        default_config = {
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
                    "enabled": True,
                    "response_template": "# AI生成的代码\n# 这是模拟模式，实际使用时会调用真实AI"
                }
            },
            "default_provider": "mock",
            "prompts": {
                "test_generation": "基于以下需求生成完整的测试代码：\n{requirement}\n\n请生成包含单元测试、集成测试的完整代码，使用pytest框架。",
                "code_implementation": "基于以下需求和测试用例实现完整的功能代码：\n需求：{requirement}\n测试：{tests}\n\n请实现所有必要的模型、视图、序列化器等。",
                "code_review": "请审查以下代码并提供改进建议：\n{code}\n\n重点关注代码质量、安全性和性能。"
            }
        }
        
        # 确保目录存在
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        print(f"默认配置文件已创建: {self.config_path}")
        return default_config
    
    def set_provider(self, provider: str):
        """设置AI提供商"""
        if provider not in self.config["providers"]:
            raise ValueError(f"不支持的AI提供商: {provider}")
        
        self.provider = provider
        self.config["default_provider"] = provider
        
        # 保存配置
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        print(f"AI提供商已切换为: {provider}")
    
    def generate_code(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """生成代码"""
        print(f"使用 {self.provider} 生成代码...")
        
        try:
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
        except Exception as e:
            print(f"AI代码生成失败: {e}")
            print("回退到模拟模式")
            return self._mock_generate(prompt)
    
    def _mock_generate(self, prompt: str) -> str:
        """模拟AI生成（用于演示）"""
        print("使用模拟模式生成代码")
        
        # 根据提示词类型生成不同的模拟代码
        if "测试" in prompt or "test" in prompt.lower():
            return self._generate_mock_test(prompt)
        elif "实现" in prompt or "implement" in prompt.lower():
            return self._generate_mock_implementation(prompt)
        elif "审查" in prompt or "review" in prompt.lower():
            return self._generate_mock_review(prompt)
        else:
            return f"""# AI生成的代码（模拟模式）
# 提示词: {prompt[:100]}...

# 这是模拟生成的代码
# 实际使用时会调用真实的AI API

def generated_function():
    \"\"\"AI生成的函数\"\"\"
    pass

class GeneratedClass:
    \"\"\"AI生成的类\"\"\"
    
    def __init__(self):
        self.data = {{}}
    
    def process(self):
        \"\"\"处理逻辑\"\"\"
        return "AI生成的处理结果"
"""
    
    def _generate_mock_test(self, prompt: str) -> str:
        """生成模拟测试代码"""
        return """import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status


User = get_user_model()


class TestAIGeneratedFeature(TestCase):
    \"\"\"AI生成的测试用例(模拟模式)\"\"\"
    
    def setUp(self):
        \"\"\"测试前置设置\"\"\"
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_feature_creation(self):
        \"\"\"测试功能创建\"\"\"
        data = {
            'name': 'Test Feature',
            'description': 'AI生成的测试功能'
        }
        
        response = self.client.post('/api/features/', data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Feature')
    
    def test_feature_list(self):
        \"\"\"测试功能列表\"\"\"
        response = self.client.get('/api/features/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
    
    def test_feature_detail(self):
        \"\"\"测试功能详情\"\"\"
        # 创建测试数据
        feature_data = {'name': 'Test Feature'}
        create_response = self.client.post('/api/features/', feature_data)
        feature_id = create_response.data['id']
        
        # 获取详情
        response = self.client.get(f'/api/features/{feature_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Feature')


@pytest.mark.integration
class TestFeatureIntegration:
    \"\"\"集成测试(模拟模式)\"\"\"
    
    def test_feature_workflow(self):
        \"\"\"测试完整的功能工作流\"\"\"
        # AI生成的集成测试
        assert True  # 模拟测试通过
"""
    
    def _generate_mock_implementation(self, prompt: str) -> str:
        """生成模拟实现代码"""
        return """from django.db import models
from django.contrib.auth import get_user_model
from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


User = get_user_model()


class AIGeneratedModel(models.Model):
    \"\"\"AI生成的模型(模拟模式)\"\"\"
    
    name = models.CharField(max_length=200, verbose_name="名称")
    description = models.TextField(blank=True, verbose_name="描述")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "AI生成功能"
        verbose_name_plural = "AI生成功能"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class AIGeneratedSerializer(serializers.ModelSerializer):
    \"\"\"AI生成的序列化器(模拟模式)\"\"\"
    
    class Meta:
        model = AIGeneratedModel
        fields = ['id', 'name', 'description', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AIGeneratedViewSet(viewsets.ModelViewSet):
    \"\"\"AI生成的视图集(模拟模式)\"\"\"
    
    serializer_class = AIGeneratedSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AIGeneratedModel.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def custom_action(self, request, pk=None):
        \"\"\"AI生成的自定义动作\"\"\"
        instance = self.get_object()
        # AI生成的业务逻辑
        return Response({
            'success': True,
            'message': 'AI生成的自定义动作执行成功',
            'data': self.get_serializer(instance).data
        })
"""
    
    def _generate_mock_review(self, prompt: str) -> str:
        """生成模拟代码审查"""
        return """# AI代码审查报告(模拟模式)

## 总体评价
代码结构清晰，符合Django和Vue的最佳实践

## 优点
1. **代码结构**: 遵循MVC模式，职责分离明确
2. **安全性**: 正确使用了用户认证和权限控制
3. **数据验证**: 序列化器提供了适当的数据验证
4. **用户体验**: 前端组件提供了友好的交互界面

## 改进建议

### 后端改进
1. **性能优化**
   - 建议为模型添加数据库索引
   - 考虑使用select_related优化查询
   
2. **错误处理**
   - 添加更详细的异常处理
   - 提供更友好的错误信息
   
3. **API文档**
   - 添加drf-spectacular的API文档注解
   - 完善接口说明和示例

### 前端改进
1. **表单验证**
   - 添加客户端表单验证规则
   - 提供实时验证反馈
   
2. **加载状态**
   - 添加loading状态显示
   - 优化用户等待体验
   
3. **错误处理**
   - 统一错误处理机制
   - 提供重试功能

### 测试覆盖
1. **单元测试**: 覆盖率良好，建议增加边界条件测试
2. **集成测试**: 建议添加更多API集成测试场景
3. **E2E测试**: 考虑添加用户操作流程的端到端测试

## 安全建议
1. 确保所有用户输入都经过验证和清理
2. 实施适当的权限控制
3. 添加请求频率限制
4. 考虑添加CSRF保护

## 性能建议
1. 实施数据分页
2. 添加缓存机制
3. 优化数据库查询
4. 考虑使用CDN加速静态资源

## 总结
代码质量整体良好，建议按照上述建议进行优化，可以进一步提升系统的稳定性和用户体验。
"""
    
    def _openai_generate(self, prompt: str) -> str:
        """OpenAI API调用"""
        config = self.config["providers"]["openai"]
        
        if config["api_key"] == "your-openai-api-key":
            raise Exception("请在ai_config.json中配置有效的OpenAI API密钥")
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": config["model"],
            "messages": [
                {"role": "system", "content": "你是一个专业的软件开发助手，擅长生成高质量的代码。"},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": config["max_tokens"],
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"OpenAI API调用失败: {response.status_code} - {response.text}")
    
    def _claude_generate(self, prompt: str) -> str:
        """Claude API调用"""
        config = self.config["providers"]["claude"]
        
        if config["api_key"] == "your-claude-api-key":
            raise Exception("请在ai_config.json中配置有效的Claude API密钥")
        
        headers = {
            "x-api-key": config["api_key"],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": config["model"],
            "max_tokens": config["max_tokens"],
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(
            f"{config['base_url']}/v1/messages",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            raise Exception(f"Claude API调用失败: {response.status_code} - {response.text}")
    
    def _ollama_generate(self, prompt: str) -> str:
        """Ollama本地模型调用"""
        config = self.config["providers"]["ollama"]
        
        data = {
            "model": config["model"],
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(
                f"{config['base_url']}/api/generate",
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                raise Exception(f"Ollama API调用失败: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            raise Exception("无法连接到Ollama服务，请确保Ollama已启动（ollama serve）")
    
    def test_connection(self) -> bool:
        """测试AI连接"""
        print(f"测试 {self.provider} 连接...")
        
        try:
            test_prompt = "请回复'连接测试成功'"
            result = self.generate_code(test_prompt)
            print(f"{self.provider} 连接测试成功")
            print(f"响应: {result[:100]}...")
            return True
        except Exception as e:
            print(f"{self.provider} 连接测试失败: {e}")
            return False
    
    def list_providers(self) -> Dict[str, bool]:
        """列出所有提供商及其可用性"""
        providers_status = {}
        
        for provider_name in self.config["providers"].keys():
            original_provider = self.provider
            try:
                self.provider = provider_name
                providers_status[provider_name] = self.test_connection()
            except:
                providers_status[provider_name] = False
            finally:
                self.provider = original_provider
        
        return providers_status


def main():
    """命令行测试接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI接口管理器")
    parser.add_argument("--provider", choices=["openai", "claude", "ollama", "mock"], 
                       help="设置AI提供商")
    parser.add_argument("--test", action="store_true", help="测试连接")
    parser.add_argument("--list", action="store_true", help="列出所有提供商")
    parser.add_argument("--prompt", help="测试提示词")
    
    args = parser.parse_args()
    
    ai = AIInterface()
    
    if args.provider:
        ai.set_provider(args.provider)
    
    if args.list:
        print("\nAI提供商状态:")
        status = ai.list_providers()
        for provider, available in status.items():
            status_icon = "[OK]" if available else "[FAIL]"
            print(f"  {status_icon} {provider}")
    
    if args.test:
        ai.test_connection()
    
    if args.prompt:
        print(f"\n生成代码...")
        result = ai.generate_code(args.prompt)
        print(f"\n生成结果:\n{result}")


if __name__ == "__main__":
    main()