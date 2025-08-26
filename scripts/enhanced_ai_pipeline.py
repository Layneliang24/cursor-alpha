#!/usr/bin/env python3
"""
AI增强流水线 - 支持多种AI提供商
"""

import os
import sys
import json
import hashlib
import shutil
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import ast
import re

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class CodeAnalysis:
    """代码分析结果"""
    existing_models: List[str]
    existing_views: List[str]
    existing_serializers: List[str]
    existing_components: List[str]
    file_hashes: Dict[str, str]

class CodeAnalyzer:
    """代码分析器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def analyze(self) -> CodeAnalysis:
        """分析现有代码"""
        print("🔍 分析已有代码...")
        
        existing_models = self._find_models()
        existing_views = self._find_views()
        existing_serializers = self._find_serializers()
        existing_components = self._find_components()
        file_hashes = self._calculate_file_hashes()
        
        print(f"📊 发现 {len(existing_models)} 个模型")
        print(f"📊 发现 {len(existing_views)} 个视图")
        print(f"📊 发现 {len(existing_serializers)} 个序列化器")
        print(f"📊 发现 {len(existing_components)} 个组件")
        
        return CodeAnalysis(
            existing_models=existing_models,
            existing_views=existing_views,
            existing_serializers=existing_serializers,
            existing_components=existing_components,
            file_hashes=file_hashes
        )
    
    def _find_models(self) -> List[str]:
        """查找现有模型"""
        models = []
        for model_file in self.project_root.rglob("models.py"):
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and 'Model' in [base.id for base in node.bases if hasattr(base, 'id')]:
                            models.append(f"{model_file.parent.name}.{node.name}")
            except Exception as e:
                print(f"⚠️ 解析模型文件失败 {model_file}: {e}")
        return models
    
    def _find_views(self) -> List[str]:
        """查找现有视图"""
        views = []
        for view_file in self.project_root.rglob("views.py"):
            try:
                with open(view_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and 'ViewSet' in [base.id for base in node.bases if hasattr(base, 'id')]:
                            views.append(f"{view_file.parent.name}.{node.name}")
            except Exception as e:
                print(f"⚠️ 解析视图文件失败 {view_file}: {e}")
        return views
    
    def _find_serializers(self) -> List[str]:
        """查找现有序列化器"""
        serializers = []
        for serializer_file in self.project_root.rglob("serializers.py"):
            try:
                with open(serializer_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and 'Serializer' in [base.id for base in node.bases if hasattr(base, 'id')]:
                            serializers.append(f"{serializer_file.parent.name}.{node.name}")
            except Exception as e:
                print(f"⚠️ 解析序列化器文件失败 {serializer_file}: {e}")
        return serializers
    
    def _find_components(self) -> List[str]:
        """查找现有组件"""
        components = []
        for component_file in self.project_root.rglob("*.vue"):
            components.append(str(component_file.relative_to(self.project_root)))
        return components
    
    def _calculate_file_hashes(self) -> Dict[str, str]:
        """计算文件哈希值"""
        hashes = {}
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.py', '.vue', '.js', '.json']:
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        hashes[str(file_path.relative_to(self.project_root))] = hashlib.md5(content).hexdigest()
                except Exception as e:
                    print(f"⚠️ 计算文件哈希失败 {file_path}: {e}")
        return hashes

class AIEnhancedPipeline:
    """AI增强流水线"""
    
    def __init__(self, config_file: str = "scripts/ai_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.analyzer = CodeAnalyzer(project_root)
        self.backup_dir = project_root / "backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"⚠️ 配置文件不存在: {self.config_file}")
            return {}
    
    def _call_ai(self, prompt: str, provider: str = "siliconflow") -> str:
        """调用AI服务"""
        try:
            provider_config = self.config.get("ai_providers", {}).get(provider, {})
            api_key = os.getenv(provider_config.get("api_key_env", "OPENAI_API_KEY"))
            
            if not api_key:
                print(f"❌ 未找到API密钥: {provider_config.get('api_key_env', 'OPENAI_API_KEY')}")
                return ""
            
            base_url = provider_config.get("base_url", "")
            model = provider_config.get("default_model", "deepseek-ai/DeepSeek-V3")
            
            # 限制prompt长度，避免413错误
            max_prompt_length = 4000  # 减少prompt长度限制
            if len(prompt) > max_prompt_length:
                prompt = prompt[:max_prompt_length] + "\n\n[内容已截断，请基于以上信息生成代码]"
            
            # 构建请求数据
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000  # 减少输出token
            }
            
            # 添加不同API的特殊参数
            if provider == "siliconflow":
                data.update({
                    "thinking_budget": 2048,  # 减少thinking_budget
                    "top_p": 0.7,
                    "temperature": 0.1
                })
            elif provider == "deepseek":
                data.update({
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "stream": False
                })
            
            # 发送请求，减少超时时间
            response = requests.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=data,
                timeout=60  # 减少超时时间到1分钟
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"❌ AI调用失败: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            print(f"❌ AI调用异常: {e}")
            return ""
    
    def _parse_requirement(self, content: str) -> Dict:
        """智能解析需求文档"""
        print("🧠 智能解析需求文档...")
        
        # 简化prompt，只取前2000字符
        content_preview = content[:2000] + "..." if len(content) > 2000 else content
        
        prompt = f"""
请分析以下需求文档，提取关键信息：

{content_preview}

请返回JSON格式：
{{
    "title": "功能标题",
    "description": "功能描述",
    "features": ["功能1", "功能2"],
    "technical_specs": {{
        "backend": ["Django模型", "API接口"],
        "frontend": ["Vue组件"],
        "database": ["数据表设计"]
    }},
    "acceptance_criteria": ["验收标准1", "验收标准2"]
}}
"""
        
        # 尝试使用AI解析
        ai_response = self._call_ai(prompt, "siliconflow")
        if ai_response:
            try:
                # 尝试提取JSON
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except Exception as e:
                print(f"⚠️ AI解析JSON失败: {e}")
        
        # 备用解析方案
        print("⚠️ AI解析失败，使用备用解析")
        return self._parse_requirement_fallback(content)
    
    def _parse_requirement_fallback(self, content: str) -> Dict:
        """需求解析备用方案"""
        # 使用正则表达式提取信息
        title_match = re.search(r'标题[:：]\s*(.+)', content)
        description_match = re.search(r'描述[:：]\s*([\s\S]+?)(?=\n\n|\n#|$)', content)
        
        title = title_match.group(1).strip() if title_match else "未知功能"
        description = description_match.group(1).strip() if description_match else "暂无描述"
        
        return {
            "title": title,
            "description": description,
            "features": ["基础功能"],
            "technical_specs": {
                "backend": ["Django模型", "API接口"],
                "frontend": ["Vue组件"],
                "database": ["数据表"]
            },
            "acceptance_criteria": ["功能可用"]
        }
    
    def _generate_code(self, requirement: Dict, file_type: str, existing_code: str = "") -> str:
        """智能生成代码"""
        print(f"🤖 智能生成{file_type}代码...")
        
        # 构建更详细的提示词
        if "models.py" in file_type:
            prompt = self._build_model_prompt(requirement, existing_code)
        elif "views.py" in file_type:
            prompt = self._build_view_prompt(requirement, existing_code)
        elif "serializers.py" in file_type:
            prompt = self._build_serializer_prompt(requirement, existing_code)
        elif "Component.vue" in file_type:
            prompt = self._build_vue_prompt(requirement, existing_code)
        else:
            prompt = self._build_generic_prompt(requirement, file_type, existing_code)
        
        # 尝试使用AI生成 - 修正：使用siliconflow来调用DeepSeek模型
        ai_response = self._call_ai(prompt, "siliconflow")
        if ai_response:
            return ai_response
        
        # 备用生成方案
        print("⚠️ AI生成失败，使用备用生成")
        return self._generate_code_fallback(file_type, requirement)
    
    def _build_model_prompt(self, requirement: Dict, existing_code: str) -> str:
        """构建模型生成提示词"""
        return f"""
请为英语学习平台的地道表达模块设计Django模型。

功能：{requirement.get('title', '')}
描述：{requirement.get('description', '')[:500]}

请生成完整的Django模型代码，包含：
- 导入语句
- 模型类定义
- 字段注释
- Meta类
- __str__方法

确保代码可以直接运行。
"""
    
    def _build_view_prompt(self, requirement: Dict, existing_code: str) -> str:
        """构建视图生成提示词"""
        return f"""
你是一个资深的Django REST Framework开发专家。请为以下需求设计高质量的API视图：

## 需求背景
- 项目：英语学习平台
- 功能：{requirement.get('title', '')}
- 描述：{requirement.get('description', '')}

## 具体要求
1. 使用Django REST Framework的ViewSet和Serializer
2. 实现完整的CRUD操作
3. 包含适当的权限控制和认证
4. 添加自定义的业务逻辑方法
5. 实现数据过滤、排序和分页
6. 包含错误处理和响应格式化
7. 考虑API性能和缓存策略

## 现有代码结构
{existing_code}

## 输出要求
请生成完整的视图代码，包含：
- 所有必要的导入语句
- ViewSet类定义
- 自定义方法实现
- 权限控制配置
- 错误处理机制
- API文档注释

请确保代码符合DRF最佳实践，具有良好的可维护性和扩展性。
"""
    
    def _build_serializer_prompt(self, requirement: Dict, existing_code: str) -> str:
        """构建序列化器生成提示词"""
        return f"""
你是一个资深的Django REST Framework开发专家。请为以下需求设计高质量的序列化器：

## 需求背景
- 项目：英语学习平台
- 功能：{requirement.get('title', '')}
- 描述：{requirement.get('description', '')}

## 具体要求
1. 创建完整的ModelSerializer
2. 包含字段验证和自定义验证器
3. 实现嵌套序列化（如需要）
4. 添加自定义字段和方法
5. 处理复杂的数据关系
6. 包含适当的字段过滤和权限控制
7. 实现数据转换和格式化

## 现有代码结构
{existing_code}

## 输出要求
请生成完整的序列化器代码，包含：
- 所有必要的导入语句
- Serializer类定义
- 字段配置和验证
- 自定义方法实现
- 嵌套序列化器（如需要）
- 错误处理机制

请确保代码符合DRF最佳实践，具有良好的数据验证和转换能力。
"""
    
    def _build_vue_prompt(self, requirement: Dict, existing_code: str) -> str:
        """构建Vue组件生成提示词"""
        return f"""
你是一个资深的Vue 3前端开发专家。请为以下需求设计高质量的Vue组件：

## 需求背景
- 项目：英语学习平台
- 功能：{requirement.get('title', '')}
- 描述：{requirement.get('description', '')}

## 具体要求
1. 使用Vue 3 Composition API
2. 实现响应式数据管理
3. 包含完整的用户交互功能
4. 使用Element Plus UI组件库
5. 实现数据获取和状态管理
6. 包含错误处理和加载状态
7. 实现适当的表单验证
8. 考虑用户体验和可访问性

## 现有代码结构
{existing_code}

## 输出要求
请生成完整的Vue组件代码，包含：
- 完整的template模板
- Composition API的script setup
- 响应式数据定义
- 方法实现
- 生命周期钩子
- 错误处理机制
- 样式定义

请确保代码符合Vue 3最佳实践，具有良好的用户体验和可维护性。
"""
    
    def _build_generic_prompt(self, requirement: Dict, file_type: str, existing_code: str) -> str:
        """构建通用代码生成提示词"""
        return f"""
你是一个资深的全栈开发专家。请为以下需求生成高质量的代码：

## 需求背景
- 项目：英语学习平台
- 功能：{requirement.get('title', '')}
- 描述：{requirement.get('description', '')}
- 文件类型：{file_type}

## 具体要求
1. 遵循最佳实践和设计模式
2. 包含完整的错误处理
3. 实现适当的注释和文档
4. 考虑性能和安全性
5. 确保代码的可维护性和可扩展性

## 现有代码结构
{existing_code}

## 输出要求
请生成完整的代码，确保：
- 代码结构清晰
- 功能完整
- 注释详细
- 符合项目规范

请根据文件类型生成相应的代码。
"""
    
    def _generate_code_fallback(self, file_type: str, requirement: Dict) -> str:
        """代码生成备用方案"""
        if "models.py" in file_type:
            return self._generate_model_code(requirement)
        elif "views.py" in file_type:
            return self._generate_view_code(requirement)
        elif "serializers.py" in file_type:
            return self._generate_serializer_code(requirement)
        elif "Component.vue" in file_type:
            return self._generate_vue_component(requirement)
        else:
            return f"# {file_type} 代码\n# 请根据需求手动实现"
    
    def _generate_model_code(self, requirement: Dict) -> str:
        """生成模型代码"""
        model_name = requirement.get('title', 'UnknownModel').replace(' ', '').replace('-', '')
        return f'''
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class {model_name}(models.Model):
    """模型: {requirement.get('title', '')}"""
    
    name = models.CharField(max_length=255, verbose_name='名称')
    description = models.TextField(blank=True, verbose_name='描述')
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='{model_name.lower()}_created',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    class Meta:
        verbose_name = '{requirement.get("title", "")}'
        verbose_name_plural = '{requirement.get("title", "")}'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
'''
    
    def _generate_view_code(self, requirement: Dict) -> str:
        """生成视图代码"""
        model_name = requirement.get('title', 'UnknownModel').replace(' ', '').replace('-', '')
        return f'''
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import {model_name}
from .serializers import {model_name}Serializer

class {model_name}ViewSet(viewsets.ModelViewSet):
    """视图集: {requirement.get('title', '')}"""
    
    queryset = {model_name}.objects.all()
    serializer_class = {model_name}Serializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
'''
    
    def _generate_serializer_code(self, requirement: Dict) -> str:
        """生成序列化器代码"""
        model_name = requirement.get('title', 'UnknownModel').replace(' ', '').replace('-', '')
        return f'''
from rest_framework import serializers
from .models import {model_name}

class {model_name}Serializer(serializers.ModelSerializer):
    """序列化器: {requirement.get('title', '')}"""
    
    class Meta:
        model = {model_name}
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']
'''
    
    def _generate_vue_component(self, requirement: Dict) -> str:
        """生成Vue组件代码"""
        component_name = requirement.get('title', 'UnknownComponent').replace(' ', '').replace('-', '')
        return f'''
<template>
  <div class="{component_name.lower()}-component">
    <h2>{{ requirement.get('title', '') }}</h2>
    <p>{{ requirement.get('description', '') }}</p>
  </div>
</template>

<script setup>
import {{ ref }} from 'vue'

// 组件逻辑
</script>

<style scoped>
.{component_name.lower()}-component {{
  padding: 20px;
}}
</style>
'''
    
    def _backup_file(self, file_path: Path) -> None:
        """备份文件"""
        if not self.config.get("smart_features", {}).get("backup_before_modify", True):
            return
        
        if file_path.exists():
            backup_path = self.backup_dir / f"{file_path.name}.backup"
            shutil.copy2(file_path, backup_path)
            print(f"💾 已备份: {file_path} -> {backup_path}")
    
    def _check_duplicate(self, file_path: Path, content: str) -> bool:
        """检查是否重复"""
        if not self.config.get("smart_features", {}).get("duplicate_prevention", True):
            return False
        
        if file_path.exists():
            with open(file_path, 'rb') as f:
                existing_hash = hashlib.md5(f.read()).hexdigest()
            new_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            if existing_hash == new_hash:
                print(f"⏭️ 跳过重复文件: {file_path}")
                return True
        
        return False
    
    def run(self, requirement_file: str, dry_run: bool = False) -> None:
        """运行流水线"""
        print("🚀 启动AI增强流水线...")
        
        # 分析现有代码
        analysis = self.analyzer.analyze()
        
        # 读取需求文档
        req_file = Path(requirement_file)
        if not req_file.exists():
            print(f"❌ 需求文件不存在: {requirement_file}")
            return
        
        with open(req_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析需求
        requirement = self._parse_requirement(content)
        print(f"📋 需求: {requirement.get('title', '未知')}")
        
        # 生成文件列表
        files_to_generate = [
            ("backend/apps/new_feature/models.py", "models.py"),
            ("backend/apps/new_feature/views.py", "views.py"),
            ("backend/apps/new_feature/serializers.py", "serializers.py"),
            ("frontend/src/components/NewFeatureComponent.vue", "Component.vue"),
            ("backend/tests/test_new_feature.py", "test.py"),
            ("frontend/tests/unit/new_feature.test.js", "test.js")
        ]
        
        generated_files = []
        
        for file_path, file_type in files_to_generate:
            full_path = project_root / file_path
            
            # 创建目录
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 生成代码
            code = self._generate_code(requirement, file_type, str(analysis))
            
            # 检查重复
            if self._check_duplicate(full_path, code):
                continue
            
            # 备份文件
            self._backup_file(full_path)
            
            # 写入文件
            if not dry_run:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                print(f"✅ 生成: {file_path}")
            else:
                print(f"📝 预览: {file_path}")
            
            generated_files.append(file_path)
        
        print(f"\n🎉 AI增强流水线执行完成!")
        print(f"📝 生成了 {len(generated_files)} 个文件")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI增强流水线")
    parser.add_argument("--input", required=True, help="需求文档路径")
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    parser.add_argument("--ai-provider", default="deepseek", choices=["openai", "siliconflow", "deepseek", "anthropic"], help="AI提供商")
    
    args = parser.parse_args()
    
    pipeline = AIEnhancedPipeline()
    pipeline.run(args.input, args.dry_run)

if __name__ == "__main__":
    main() 