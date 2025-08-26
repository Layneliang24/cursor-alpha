#!/usr/bin/env python3
"""
本地AI增强流水线（无需API密钥）

功能：
1. 使用本地AI模型（Ollama）
2. 智能解析需求文档
3. 检测已有代码
4. 生成高质量代码
5. 避免重复生成
"""

import os
import sys
import json
import yaml
import argparse
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import re
import ast
import hashlib
import requests


@dataclass
class LocalAIRequirement:
    """本地AI需求数据结构"""
    id: str
    title: str
    description: str
    detailed_features: List[str]
    technical_specs: Dict[str, Any]
    acceptance_criteria: List[str]
    type: str
    priority: str
    components: List[str]
    dependencies: List[str]
    estimated_hours: int
    assignee: Optional[str] = None
    labels: List[str] = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = []


@dataclass
class CodeAnalysis:
    """代码分析结果"""
    existing_models: List[str]
    existing_views: List[str]
    existing_serializers: List[str]
    existing_components: List[str]
    existing_services: List[str]
    database_tables: List[str]
    api_endpoints: List[str]
    file_hashes: Dict[str, str]


class LocalAIPipeline:
    """本地AI增强流水线"""
    
    def __init__(self, project_root: str, ai_model: str = "codellama:7b"):
        self.project_root = Path(project_root)
        self.ai_model = ai_model
        self.code_analyzer = CodeAnalyzer(project_root)
        self.ollama_url = "http://localhost:11434"
        
    def check_ollama_available(self) -> bool:
        """检查Ollama是否可用"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def install_ollama_model(self):
        """安装Ollama模型"""
        print(f"📦 安装AI模型: {self.ai_model}")
        try:
            subprocess.run([
                "ollama", "pull", self.ai_model
            ], check=True, capture_output=True)
            print(f"✅ 模型安装成功: {self.ai_model}")
        except subprocess.CalledProcessError as e:
            print(f"❌ 模型安装失败: {e}")
            print("请确保已安装Ollama: https://ollama.ai/")
    
    def call_local_ai(self, prompt: str) -> str:
        """调用本地AI"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ai_model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return self._fallback_response(prompt)
        except Exception as e:
            print(f"⚠️ 本地AI调用失败: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """备用响应（基于规则）"""
        if "需求解析" in prompt:
            return self._parse_requirement_fallback(prompt)
        elif "代码生成" in prompt:
            return self._generate_code_fallback(prompt)
        else:
            return "# 本地AI响应\n# 这是基于规则的备用响应"
    
    def _parse_requirement_fallback(self, prompt: str) -> str:
        """需求解析备用方案"""
        # 简单的规则解析
        content = prompt.split("需求文档：")[-1] if "需求文档：" in prompt else prompt
        
        # 提取基本信息
        title_match = re.search(r'标题[:：]\s*(.+)', content)
        title = title_match.group(1).strip() if title_match else "未知需求"
        
        description_match = re.search(r'描述[:：]\s*([\s\S]+?)(?=\n\n|\n(?:目标|功能))', content)
        description = description_match.group(1).strip() if description_match else "无描述"
        
        # 提取功能列表
        features = []
        feature_matches = re.findall(r'[-*]\s*(.+)', content)
        for match in feature_matches:
            if any(keyword in match.lower() for keyword in ['功能', '系统', '模块', '管理', '处理']):
                features.append(match.strip())
        
        # 构建JSON响应
        result = {
            "id": "local_requirement",
            "title": title,
            "description": description,
            "detailed_features": features[:5],  # 最多5个功能
            "technical_specs": {
                "backend_requirements": ["数据模型", "API接口", "业务逻辑"],
                "frontend_requirements": ["用户界面", "交互功能", "数据展示"],
                "database_requirements": ["数据存储", "查询优化"],
                "api_requirements": ["RESTful API", "数据验证"]
            },
            "acceptance_criteria": [
                "功能正常运行",
                "用户界面友好",
                "数据准确无误",
                "性能满足要求"
            ],
            "type": "feature",
            "priority": "medium",
            "components": ["frontend", "backend", "database"],
            "dependencies": [],
            "estimated_hours": 8
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    def _generate_code_fallback(self, prompt: str) -> str:
        """代码生成备用方案"""
        if "models.py" in prompt:
            return self._generate_model_code()
        elif "views.py" in prompt:
            return self._generate_view_code()
        elif "serializers.py" in prompt:
            return self._generate_serializer_code()
        elif "Component.vue" in prompt:
            return self._generate_vue_component()
        else:
            return "# 代码生成\n# 请根据具体需求实现相应功能"
    
    def _generate_model_code(self) -> str:
        """生成模型代码"""
        return '''
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ExampleModel(models.Model):
    """示例模型"""
    name = models.CharField(max_length=100, verbose_name='名称')
    description = models.TextField(blank=True, verbose_name='描述')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    class Meta:
        verbose_name = '示例模型'
        verbose_name_plural = '示例模型'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
'''
    
    def _generate_view_code(self) -> str:
        """生成视图代码"""
        return '''
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import ExampleModel
from .serializers import ExampleModelSerializer

class ExampleModelViewSet(viewsets.ModelViewSet):
    """示例模型视图集"""
    queryset = ExampleModel.objects.all()
    serializer_class = ExampleModelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'created_by']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """激活模型"""
        instance = self.get_object()
        instance.is_active = True
        instance.save()
        return Response({'status': 'activated'})
'''
    
    def _generate_serializer_code(self) -> str:
        """生成序列化器代码"""
        return '''
from rest_framework import serializers
from .models import ExampleModel

class ExampleModelSerializer(serializers.ModelSerializer):
    """示例模型序列化器"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ExampleModel
        fields = [
            'id', 'name', 'description', 'created_by', 'created_by_username',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
'''
    
    def _generate_vue_component(self) -> str:
        """生成Vue组件代码"""
        return '''
<template>
  <div class="example-component">
    <h2>{{ title }}</h2>
    <div class="content">
      <el-form :model="form" label-width="120px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="请输入名称"></el-input>
        </el-form-item>
        <el-form-item label="描述">
          <el-input type="textarea" v-model="form.description" placeholder="请输入描述"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">提交</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const title = ref('示例组件')
const form = reactive({
  name: '',
  description: ''
})

const handleSubmit = () => {
  ElMessage.success('提交成功')
}

const handleReset = () => {
  form.name = ''
  form.description = ''
}
</script>

<style scoped>
.example-component {
  padding: 20px;
}
</style>
'''
    
    def analyze_existing_code(self) -> CodeAnalysis:
        """分析已有代码"""
        print("🔍 分析已有代码...")
        return self.code_analyzer.analyze()
    
    def parse_requirement_intelligently(self, requirement_file: str) -> LocalAIRequirement:
        """智能解析需求文档"""
        print("🧠 智能解析需求文档...")
        
        with open(requirement_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用本地AI解析需求
        prompt = f"""
请详细分析以下需求文档，提取所有关键信息：

{content}

请以JSON格式返回以下信息：
{{
    "id": "需求ID",
    "title": "需求标题",
    "description": "需求描述",
    "detailed_features": ["功能1", "功能2", ...],
    "technical_specs": {{
        "backend_requirements": ["后端要求1", "后端要求2"],
        "frontend_requirements": ["前端要求1", "前端要求2"],
        "database_requirements": ["数据库要求1", "数据库要求2"],
        "api_requirements": ["API要求1", "API要求2"]
    }},
    "acceptance_criteria": ["验收标准1", "验收标准2", ...],
    "type": "feature|bugfix|enhancement",
    "priority": "high|medium|low",
    "components": ["frontend", "backend", "api", "database"],
    "dependencies": ["依赖1", "依赖2"],
    "estimated_hours": 预估工时
}}
"""
        
        response = self.call_local_ai(prompt)
        try:
            data = json.loads(response)
            return LocalAIRequirement(**data)
        except Exception as e:
            print(f"AI解析失败，使用备用解析: {e}")
            return self._fallback_parse(content)
    
    def _fallback_parse(self, content: str) -> LocalAIRequirement:
        """备用解析方法"""
        lines = content.split('\n')
        data = {
            'id': 'local_requirement',
            'title': '本地需求',
            'description': content[:200],
            'detailed_features': [],
            'technical_specs': {},
            'acceptance_criteria': [],
            'type': 'feature',
            'priority': 'medium',
            'components': ['frontend', 'backend'],
            'dependencies': [],
            'estimated_hours': 8
        }
        return LocalAIRequirement(**data)
    
    def generate_smart_code(self, requirement: LocalAIRequirement, code_analysis: CodeAnalysis) -> Dict[str, str]:
        """智能生成代码"""
        print("🤖 本地AI智能生成代码...")
        
        context = {
            'requirement': requirement,
            'existing_code': code_analysis,
            'project_structure': self._get_project_structure()
        }
        
        generated_files = {}
        
        # 生成后端代码
        if 'backend' in requirement.components:
            backend_code = self._generate_backend_code(context)
            generated_files.update(backend_code)
        
        # 生成前端代码
        if 'frontend' in requirement.components:
            frontend_code = self._generate_frontend_code(context)
            generated_files.update(frontend_code)
        
        # 生成测试代码
        test_code = self._generate_test_code(context)
        generated_files.update(test_code)
        
        return generated_files
    
    def _generate_backend_code(self, context: Dict) -> Dict[str, str]:
        """生成后端代码"""
        prompt = f"""
基于以下需求和已有代码，生成高质量的后端代码：

需求：{json.dumps(asdict(context['requirement']), ensure_ascii=False, indent=2)}
已有代码：{json.dumps(asdict(context['existing_code']), ensure_ascii=False, indent=2)}

请生成以下文件：
1. models.py - 数据模型
2. views.py - 视图和API
3. serializers.py - 序列化器
4. urls.py - URL配置

要求：
- 遵循Django最佳实践
- 包含完整的CRUD操作
- 包含权限控制
- 包含数据验证
- 避免与已有代码冲突
- 生成高质量、可维护的代码

请以JSON格式返回：
{{
    "models.py": "模型代码",
    "views.py": "视图代码", 
    "serializers.py": "序列化器代码",
    "urls.py": "URL配置代码"
}}
"""
        
        response = self.call_local_ai(prompt)
        try:
            return json.loads(response)
        except:
            return {
                "models.py": self._generate_model_code(),
                "views.py": self._generate_view_code(),
                "serializers.py": self._generate_serializer_code(),
                "urls.py": "# URL配置\nfrom django.urls import path, include\nfrom rest_framework.routers import DefaultRouter\nfrom .views import ExampleModelViewSet\n\nrouter = DefaultRouter()\nrouter.register(r'example', ExampleModelViewSet)\n\nurlpatterns = [\n    path('', include(router.urls)),\n]"
            }
    
    def _generate_frontend_code(self, context: Dict) -> Dict[str, str]:
        """生成前端代码"""
        prompt = f"""
基于以下需求，生成高质量的Vue 3前端代码：

需求：{json.dumps(asdict(context['requirement']), ensure_ascii=False, indent=2)}

请生成以下文件：
1. Component.vue - 主组件
2. Service.js - 服务层
3. Store.js - 状态管理

要求：
- 使用Vue 3 Composition API
- 使用Element Plus UI组件
- 包含完整的CRUD操作
- 包含错误处理
- 包含加载状态
- 生成高质量、可维护的代码

请以JSON格式返回：
{{
    "Component.vue": "组件代码",
    "Service.js": "服务代码",
    "Store.js": "状态管理代码"
}}
"""
        
        response = self.call_local_ai(prompt)
        try:
            return json.loads(response)
        except:
            return {
                "Component.vue": self._generate_vue_component(),
                "Service.js": "// 服务层代码\nimport axios from 'axios'\n\nexport const exampleService = {\n  async getList() {\n    return await axios.get('/api/example/')\n  },\n  async create(data) {\n    return await axios.post('/api/example/', data)\n  }\n}",
                "Store.js": "// 状态管理代码\nimport { defineStore } from 'pinia'\n\nexport const useExampleStore = defineStore('example', {\n  state: () => ({\n    items: [],\n    loading: false\n  }),\n  actions: {\n    async fetchItems() {\n      this.loading = true\n      // 实现获取数据逻辑\n      this.loading = false\n    }\n  }\n})"
            }
    
    def _generate_test_code(self, context: Dict) -> Dict[str, str]:
        """生成测试代码"""
        return {
            "test_models.py": """
import pytest
from django.test import TestCase
from .models import ExampleModel

class TestExampleModel(TestCase):
    def test_model_creation(self):
        model = ExampleModel.objects.create(name="测试")
        self.assertEqual(model.name, "测试")
""",
            "test_views.py": """
import pytest
from rest_framework.test import APITestCase
from rest_framework import status

class TestExampleViewSet(APITestCase):
    def test_list_view(self):
        response = self.client.get('/api/example/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
""",
            "test_integration.py": """
import pytest
from django.test import TestCase

class TestIntegration(TestCase):
    def test_full_workflow(self):
        # 集成测试
        pass
""",
            "test_e2e.js": """
// E2E测试
describe('Example E2E', () => {
  it('should work', () => {
    // E2E测试逻辑
  })
})
"""
        }
    
    def _get_project_structure(self) -> Dict:
        """获取项目结构"""
        structure = {}
        for root, dirs, files in os.walk(self.project_root):
            rel_path = os.path.relpath(root, self.project_root)
            if rel_path == '.':
                continue
            structure[rel_path] = {
                'dirs': dirs,
                'files': [f for f in files if not f.startswith('.')]
            }
        return structure
    
    def check_file_changes(self, file_path: str) -> bool:
        """检查文件是否有变更"""
        if not os.path.exists(file_path):
            return True
        
        with open(file_path, 'rb') as f:
            content = f.read()
        current_hash = hashlib.md5(content).hexdigest()
        
        hash_file = f"{file_path}.hash"
        if os.path.exists(hash_file):
            with open(hash_file, 'r') as f:
                stored_hash = f.read().strip()
            return current_hash != stored_hash
        
        return True
    
    def save_file_with_hash(self, file_path: str, content: str):
        """保存文件并记录哈希"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_hash = hashlib.md5(content.encode()).hexdigest()
        with open(f"{file_path}.hash", 'w') as f:
            f.write(file_hash)
    
    def run(self, requirement_file: str, dry_run: bool = False):
        """运行本地AI增强流水线"""
        print("启动本地AI增强流水线...")
        
        # 检查Ollama可用性
        if not self.check_ollama_available():
            print("⚠️ Ollama未运行，将使用备用方案")
            print("💡 安装Ollama: https://ollama.ai/")
            print("💡 运行: ollama serve")
        else:
            print("✅ Ollama运行正常")
        
        # 1. 分析已有代码
        code_analysis = self.analyze_existing_code()
        
        # 2. 智能解析需求
        requirement = self.parse_requirement_intelligently(requirement_file)
        
        # 3. 生成智能代码
        generated_files = self.generate_smart_code(requirement, code_analysis)
        
        # 4. 检查文件变更并保存
        if not dry_run:
            for file_path, content in generated_files.items():
                full_path = self.project_root / file_path
                if self.check_file_changes(str(full_path)):
                    print(f"📝 生成文件: {file_path}")
                    self.save_file_with_hash(str(full_path), content)
                else:
                    print(f"⏭️ 跳过未变更文件: {file_path}")
        
        print("✅ 本地AI增强流水线执行完成!")
        return {
            'requirement': requirement,
            'code_analysis': code_analysis,
            'generated_files': list(generated_files.keys())
        }


class CodeAnalyzer:
    """代码分析器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
    
    def analyze(self) -> CodeAnalysis:
        """分析项目代码"""
        return CodeAnalysis(
            existing_models=self._find_models(),
            existing_views=self._find_views(),
            existing_serializers=self._find_serializers(),
            existing_components=self._find_components(),
            existing_services=self._find_services(),
            database_tables=self._find_database_tables(),
            api_endpoints=self._find_api_endpoints(),
            file_hashes=self._calculate_file_hashes()
        )
    
    def _find_models(self) -> List[str]:
        """查找现有模型"""
        models = []
        for model_file in self.project_root.rglob("models.py"):
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            models.append(node.name)
            except:
                continue
        return models
    
    def _find_views(self) -> List[str]:
        """查找现有视图"""
        views = []
        for view_file in self.project_root.rglob("views.py"):
            try:
                with open(view_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            views.append(node.name)
            except:
                continue
        return views
    
    def _find_serializers(self) -> List[str]:
        """查找现有序列化器"""
        serializers = []
        for serializer_file in self.project_root.rglob("serializers.py"):
            try:
                with open(serializer_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            serializers.append(node.name)
            except:
                continue
        return serializers
    
    def _find_components(self) -> List[str]:
        """查找现有Vue组件"""
        components = []
        for component_file in self.project_root.rglob("*.vue"):
            try:
                with open(component_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'export default' in content:
                        components.append(component_file.stem)
            except:
                continue
        return components
    
    def _find_services(self) -> List[str]:
        """查找现有服务"""
        services = []
        for service_file in self.project_root.rglob("*Service.js"):
            services.append(service_file.stem)
        return services
    
    def _find_database_tables(self) -> List[str]:
        """查找数据库表"""
        tables = []
        for migration_file in self.project_root.rglob("migrations/*.py"):
            try:
                with open(migration_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'CreateModel' in content:
                        tables.extend(re.findall(r"'(\w+)'", content))
            except:
                continue
        return list(set(tables))
    
    def _find_api_endpoints(self) -> List[str]:
        """查找API端点"""
        endpoints = []
        for url_file in self.project_root.rglob("urls.py"):
            try:
                with open(url_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    endpoints.extend(re.findall(r"path\(['\"]([^'\"]+)['\"]", content))
            except:
                continue
        return endpoints
    
    def _calculate_file_hashes(self) -> Dict[str, str]:
        """计算文件哈希值"""
        hashes = {}
        for file_path in self.project_root.rglob("*.py"):
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    hashes[str(file_path.relative_to(self.project_root))] = hashlib.md5(content).hexdigest()
            except:
                continue
        return hashes


def main():
    parser = argparse.ArgumentParser(description="本地AI增强的需求→测试→实现流水线")
    parser.add_argument("--input", required=True, help="需求文档路径")
    parser.add_argument("--ai-model", default="codellama:7b", help="本地AI模型")
    parser.add_argument("--dry-run", action="store_true", help="预览模式")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    
    args = parser.parse_args()
    
    pipeline = LocalAIPipeline(args.project_root, args.ai_model)
    result = pipeline.run(args.input, args.dry_run)
    
    print("\n" + "="*60)
    print("🎉 本地AI增强流水线执行完成!")
    print(f"📋 需求: {result['requirement'].title}")
    print(f"🔍 检测到 {len(result['code_analysis'].existing_models)} 个现有模型")
    print(f"📝 生成了 {len(result['generated_files'])} 个文件")
    print("="*60)


if __name__ == "__main__":
    main() 