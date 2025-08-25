#!/usr/bin/env python3
"""
需求→测试→实现自动化流水线

功能：
1. 解析需求文档，提取关键信息
2. 生成对应的测试模板（单元测试、集成测试、E2E测试）
3. 创建工单和分支
4. 生成基础代码框架
5. 提交变更并触发CI
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
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import re


@dataclass
class Requirement:
    """需求数据结构"""
    id: str
    title: str
    description: str
    type: str  # feature, bugfix, enhancement, refactor
    priority: str  # high, medium, low
    components: List[str]  # frontend, backend, api, database
    acceptance_criteria: List[str]
    dependencies: List[str]
    estimated_hours: int
    assignee: Optional[str] = None
    labels: List[str] = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = []


@dataclass
class TestTemplate:
    """测试模板数据结构"""
    test_type: str  # unit, integration, e2e
    file_path: str
    content: str
    dependencies: List[str]


@dataclass
class CodeTemplate:
    """代码模板数据结构"""
    file_path: str
    content: str
    template_type: str  # model, view, component, service


class RequirementParser:
    """需求解析器"""
    
    def __init__(self):
        self.patterns = {
            'title': r'(?:标题|Title)[:：]\s*(.+)',
            'description': r'(?:描述|Description)[:：]\s*([\s\S]+?)(?=\n\n|\n(?:标题|Title|类型|Type|优先级|Priority|组件|Components))',
            'type': r'(?:类型|Type)[:：]\s*(feature|bugfix|enhancement|refactor)',
            'priority': r'(?:优先级|Priority)[:：]\s*(high|medium|low)',
            'components': r'(?:组件|Components)[:：]\s*([\w\s,，]+)',
            'acceptance_criteria': r'(?:验收标准|Acceptance Criteria)[:：]\s*([\s\S]+?)(?=\n\n|\n(?:标题|Title|依赖|Dependencies|预估|Estimated))',
            'dependencies': r'(?:依赖|Dependencies)[:：]\s*([\w\s,，#]+)',
            'estimated_hours': r'(?:预估工时|Estimated Hours)[:：]\s*(\d+)',
            'assignee': r'(?:负责人|Assignee)[:：]\s*([\w\s]+)',
        }
    
    def parse_from_text(self, text: str, req_id: str) -> Requirement:
        """从文本解析需求"""
        data = {'id': req_id}
        
        for field, pattern in self.patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                
                if field == 'components':
                    data[field] = [c.strip() for c in re.split(r'[,，]', value) if c.strip()]
                elif field == 'acceptance_criteria':
                    # 提取列表项
                    criteria = re.findall(r'[-*]\s*(.+)', value)
                    if not criteria:
                        criteria = [line.strip() for line in value.split('\n') if line.strip()]
                    data[field] = criteria
                elif field == 'dependencies':
                    deps = re.findall(r'#(\d+)|([\w-]+)', value)
                    data[field] = [d[0] or d[1] for d in deps if d[0] or d[1]]
                elif field == 'estimated_hours':
                    data[field] = int(value)
                else:
                    data[field] = value
        
        # 设置默认值
        data.setdefault('title', f'需求 {req_id}')
        data.setdefault('description', '暂无描述')
        data.setdefault('type', 'feature')
        data.setdefault('priority', 'medium')
        data.setdefault('components', ['frontend', 'backend'])
        data.setdefault('acceptance_criteria', [])
        data.setdefault('dependencies', [])
        data.setdefault('estimated_hours', 8)
        
        return Requirement(**data)
    
    def parse_from_file(self, file_path: str) -> Requirement:
        """从文件解析需求"""
        path = Path(file_path)
        req_id = path.stem
        
        if path.suffix.lower() == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data['id'] = req_id
                return Requirement(**data)
        elif path.suffix.lower() in ['.yml', '.yaml']:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                data['id'] = req_id
                return Requirement(**data)
        else:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
                return self.parse_from_text(text, req_id)


class TestGenerator:
    """测试生成器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.templates_dir = self.project_root / 'scripts' / 'templates'
        self.ensure_templates_dir()
    
    def ensure_templates_dir(self):
        """确保模板目录存在"""
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_unit_tests(self, req: Requirement) -> List[TestTemplate]:
        """生成单元测试"""
        tests = []
        
        if 'backend' in req.components:
            # Django 单元测试
            test_content = self._generate_django_unit_test(req)
            tests.append(TestTemplate(
                test_type='unit',
                file_path=f'backend/tests/test_{req.id}.py',
                content=test_content,
                dependencies=['pytest', 'django']
            ))
        
        if 'frontend' in req.components:
            # Vue 单元测试
            test_content = self._generate_vue_unit_test(req)
            tests.append(TestTemplate(
                test_type='unit',
                file_path=f'frontend/tests/unit/{req.id}.test.js',
                content=test_content,
                dependencies=['vitest', '@vue/test-utils']
            ))
        
        return tests
    
    def generate_integration_tests(self, req: Requirement) -> List[TestTemplate]:
        """生成集成测试"""
        tests = []
        
        if 'api' in req.components or 'backend' in req.components:
            test_content = self._generate_api_integration_test(req)
            tests.append(TestTemplate(
                test_type='integration',
                file_path=f'backend/tests/integration/test_{req.id}_api.py',
                content=test_content,
                dependencies=['pytest', 'requests', 'django']
            ))
        
        return tests
    
    def generate_e2e_tests(self, req: Requirement) -> List[TestTemplate]:
        """生成E2E测试"""
        tests = []
        
        if req.type == 'feature' and ('frontend' in req.components or 'ui' in req.components):
            test_content = self._generate_playwright_e2e_test(req)
            tests.append(TestTemplate(
                test_type='e2e',
                file_path=f'tests/e2e/{req.id}.spec.js',
                content=test_content,
                dependencies=['@playwright/test']
            ))
        
        return tests
    
    def _generate_django_unit_test(self, req: Requirement) -> str:
        """生成Django单元测试代码"""
        return f'''import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


User = get_user_model()


class Test{req.id.title().replace('_', '')}(APITestCase):
    """测试 {req.title}"""
    
    def setUp(self):
        """测试前置设置"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_{req.id}_basic_functionality(self):
        """测试基本功能"""
        # TODO: 实现基本功能测试
        # 基于需求描述: {req.description}
        pass
    
{self._generate_acceptance_criteria_tests(req, 'django')}
    
    def tearDown(self):
        """测试后清理"""
        User.objects.all().delete()
'''
    
    def _generate_vue_unit_test(self, req: Requirement) -> str:
        """生成Vue单元测试代码"""
        component_name = req.id.title().replace('_', '')
        return f'''import {{ describe, it, expect, beforeEach }} from 'vitest'
import {{ mount }} from '@vue/test-utils'
import {component_name}Component from '@/components/{component_name}Component.vue'

describe('{component_name}Component', () => {{
  let wrapper
  
  beforeEach(() => {{
    wrapper = mount({component_name}Component, {{
      props: {{
        // TODO: 添加必要的props
      }}
    }})
  }})
  
  it('should render correctly', () => {{
    expect(wrapper.exists()).toBe(true)
  }})
  
  it('should handle basic functionality', () => {{
    // TODO: 实现基本功能测试
    // 基于需求描述: {req.description}
  }})
  
{self._generate_acceptance_criteria_tests(req, 'vue')}
}})
'''
    
    def _generate_api_integration_test(self, req: Requirement) -> str:
        """生成API集成测试代码"""
        return f'''import pytest
import requests
from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status


User = get_user_model()


@pytest.mark.integration
class Test{req.id.title().replace('_', '')}Integration(TransactionTestCase):
    """集成测试 {req.title}"""
    
    def setUp(self):
        """测试前置设置"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_{req.id}_api_integration(self):
        """测试API集成"""
        # TODO: 实现API集成测试
        # 基于需求描述: {req.description}
        pass
    
{self._generate_acceptance_criteria_tests(req, 'api')}
'''
    
    def _generate_playwright_e2e_test(self, req: Requirement) -> str:
        """生成Playwright E2E测试代码"""
        return f'''import {{ test, expect }} from '@playwright/test'

test.describe('{req.title}', () => {{
  test.beforeEach(async ({{ page }}) => {{
    // 登录用户
    await page.goto('/login')
    await page.fill('[data-testid="username"]', 'testuser')
    await page.fill('[data-testid="password"]', 'testpass123')
    await page.click('[data-testid="login-button"]')
    await expect(page).toHaveURL('/dashboard')
  }})
  
  test('should complete user journey for {req.title}', async ({{ page }}) => {{
    // TODO: 实现用户旅程测试
    // 基于需求描述: {req.description}
  }})
  
{self._generate_acceptance_criteria_tests(req, 'e2e')}
}})
'''
    
    def _generate_acceptance_criteria_tests(self, req: Requirement, test_type: str) -> str:
        """生成验收标准测试"""
        if not req.acceptance_criteria:
            return ''
        
        tests = []
        for i, criteria in enumerate(req.acceptance_criteria, 1):
            test_name = f"test_{req.id}_acceptance_criteria_{i}"
            
            if test_type == 'django':
                tests.append(f'''    def {test_name}(self):
        """验收标准 {i}: {criteria}"""
        # TODO: 实现验收标准测试
        pass''')
            elif test_type == 'vue':
                tests.append(f'''  it('should meet acceptance criteria {i}: {criteria}', () => {{
    // TODO: 实现验收标准测试
  }})''')
            elif test_type == 'api':
                tests.append(f'''    def {test_name}(self):
        """验收标准 {i}: {criteria}"""
        # TODO: 实现验收标准测试
        pass''')
            elif test_type == 'e2e':
                tests.append(f'''  test('should meet acceptance criteria {i}: {criteria}', async ({{ page }}) => {{
    // TODO: 实现验收标准测试
  }})''')
        
        return '\n\n'.join(tests)


class CodeGenerator:
    """代码生成器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
    
    def generate_code_templates(self, req: Requirement) -> List[CodeTemplate]:
        """生成代码模板"""
        templates = []
        
        if 'backend' in req.components:
            if 'database' in req.components or req.type == 'feature':
                # 生成Django模型
                templates.append(self._generate_django_model(req))
                # 生成Django视图
                templates.append(self._generate_django_view(req))
                # 生成Django序列化器
                templates.append(self._generate_django_serializer(req))
        
        if 'frontend' in req.components:
            # 生成Vue组件
            templates.append(self._generate_vue_component(req))
            # 生成Vue服务
            templates.append(self._generate_vue_service(req))
        
        return templates
    
    def _generate_django_model(self, req: Requirement) -> CodeTemplate:
        """生成Django模型"""
        model_name = req.id.title().replace('_', '')
        content = f'''from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class {model_name}(models.Model):
    """模型: {req.title}"""
    
    # TODO: 根据需求添加字段
    # 需求描述: {req.description}
    
    name = models.CharField(max_length=255, verbose_name='名称')
    description = models.TextField(blank=True, verbose_name='描述')
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='{req.id}_created',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    class Meta:
        verbose_name = '{req.title}'
        verbose_name_plural = '{req.title}'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
'''
        
        return CodeTemplate(
            file_path=f'backend/apps/{req.id}/models.py',
            content=content,
            template_type='model'
        )
    
    def _generate_django_view(self, req: Requirement) -> CodeTemplate:
        """生成Django视图"""
        model_name = req.id.title().replace('_', '')
        content = f'''from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import {model_name}
from .serializers import {model_name}Serializer


class {model_name}ViewSet(viewsets.ModelViewSet):
    """视图集: {req.title}"""
    
    queryset = {model_name}.objects.all()
    serializer_class = {model_name}Serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'created_by']
    
    def get_queryset(self):
        """获取查询集"""
        queryset = super().get_queryset()
        # TODO: 根据需求添加过滤逻辑
        return queryset.filter(is_active=True)
    
    def perform_create(self, serializer):
        """创建时设置创建者"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换激活状态"""
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save()
        return Response({{
            'status': 'success',
            'is_active': instance.is_active
        }})
    
    # TODO: 根据需求添加自定义动作
'''
        
        return CodeTemplate(
            file_path=f'backend/apps/{req.id}/views.py',
            content=content,
            template_type='view'
        )
    
    def _generate_django_serializer(self, req: Requirement) -> CodeTemplate:
        """生成Django序列化器"""
        model_name = req.id.title().replace('_', '')
        content = f'''from rest_framework import serializers
from .models import {model_name}


class {model_name}Serializer(serializers.ModelSerializer):
    """序列化器: {req.title}"""
    
    created_by_name = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    
    class Meta:
        model = {model_name}
        fields = [
            'id', 'name', 'description', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """验证名称"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError('名称至少需要2个字符')
        return value.strip()
    
    # TODO: 根据需求添加自定义验证逻辑
'''
        
        return CodeTemplate(
            file_path=f'backend/apps/{req.id}/serializers.py',
            content=content,
            template_type='serializer'
        )
    
    def _generate_vue_component(self, req: Requirement) -> CodeTemplate:
        """生成Vue组件"""
        component_name = req.id.title().replace('_', '')
        content = f'''<template>
  <div class="{req.id.replace('_', '-')}-component">
    <div class="header">
      <h2>{{ title }}</h2>
      <p class="description">{{ description }}</p>
    </div>
    
    <!-- TODO: 根据需求实现组件内容 -->
    <!-- 需求描述: {req.description} -->
    
    <div class="content">
      <p>组件内容待实现</p>
    </div>
    
    <div class="actions">
      <button @click="handleAction" class="btn btn-primary">
        执行操作
      </button>
    </div>
  </div>
</template>

<script setup>
import {{ ref, onMounted }} from 'vue'
import {{ use{component_name}Service }} from '@/services/{req.id}Service'

// Props
const props = defineProps({{
  title: {{
    type: String,
    default: '{req.title}'
  }},
  description: {{
    type: String,
    default: '{req.description}'
  }}
}})

// Emits
const emit = defineEmits(['action-completed'])

// Composables
const {component_name.lower()}Service = use{component_name}Service()

// Reactive data
const loading = ref(false)
const data = ref([])

// Methods
const handleAction = async () => {{
  try {{
    loading.value = true
    // TODO: 实现操作逻辑
    emit('action-completed', {{ success: true }})
  }} catch (error) {{
    console.error('操作失败:', error)
    emit('action-completed', {{ success: false, error }})
  }} finally {{
    loading.value = false
  }}
}}

const loadData = async () => {{
  try {{
    loading.value = true
    data.value = await {component_name.lower()}Service.getList()
  }} catch (error) {{
    console.error('加载数据失败:', error)
  }} finally {{
    loading.value = false
  }}
}}

// Lifecycle
onMounted(() => {{
  loadData()
}})
</script>

<style scoped>
.{req.id.replace('_', '-')}-component {{
  padding: 1rem;
}}

.header {{
  margin-bottom: 1rem;
}}

.header h2 {{
  margin: 0 0 0.5rem 0;
  color: #333;
}}

.description {{
  color: #666;
  margin: 0;
}}

.content {{
  margin: 1rem 0;
}}

.actions {{
  margin-top: 1rem;
}}

.btn {{
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}}

.btn-primary {{
  background-color: #007bff;
  color: white;
}}

.btn-primary:hover {{
  background-color: #0056b3;
}}
</style>
'''
        
        return CodeTemplate(
            file_path=f'frontend/src/components/{component_name}Component.vue',
            content=content,
            template_type='component'
        )
    
    def _generate_vue_service(self, req: Requirement) -> CodeTemplate:
        """生成Vue服务"""
        service_name = req.id.title().replace('_', '')
        content = f'''import {{ ref }} from 'vue'
import api from '@/api'

/**
 * {req.title} 服务
 * {req.description}
 */
export function use{service_name}Service() {{
  const loading = ref(false)
  const error = ref(null)
  
  /**
   * 获取列表
   */
  const getList = async (params = {{}}) => {{
    try {{
      loading.value = true
      error.value = null
      const response = await api.get('/{req.id}/', {{ params }})
      return response.data
    }} catch (err) {{
      error.value = err.message
      throw err
    }} finally {{
      loading.value = false
    }}
  }}
  
  /**
   * 获取详情
   */
  const getDetail = async (id) => {{
    try {{
      loading.value = true
      error.value = null
      const response = await api.get(`/{req.id}/${{id}}/`)
      return response.data
    }} catch (err) {{
      error.value = err.message
      throw err
    }} finally {{
      loading.value = false
    }}
  }}
  
  /**
   * 创建
   */
  const create = async (data) => {{
    try {{
      loading.value = true
      error.value = null
      const response = await api.post('/{req.id}/', data)
      return response.data
    }} catch (err) {{
      error.value = err.message
      throw err
    }} finally {{
      loading.value = false
    }}
  }}
  
  /**
   * 更新
   */
  const update = async (id, data) => {{
    try {{
      loading.value = true
      error.value = null
      const response = await api.put(`/{req.id}/${{id}}/`, data)
      return response.data
    }} catch (err) {{
      error.value = err.message
      throw err
    }} finally {{
      loading.value = false
    }}
  }}
  
  /**
   * 删除
   */
  const remove = async (id) => {{
    try {{
      loading.value = true
      error.value = null
      await api.delete(`/{req.id}/${{id}}/`)
      return true
    }} catch (err) {{
      error.value = err.message
      throw err
    }} finally {{
      loading.value = false
    }}
  }}
  
  /**
   * 切换激活状态
   */
  const toggleActive = async (id) => {{
    try {{
      loading.value = true
      error.value = null
      const response = await api.post(`/{req.id}/${{id}}/toggle_active/`)
      return response.data
    }} catch (err) {{
      error.value = err.message
      throw err
    }} finally {{
      loading.value = false
    }}
  }}
  
  return {{
    loading,
    error,
    getList,
    getDetail,
    create,
    update,
    remove,
    toggleActive
  }}
}}

export default use{service_name}Service
'''
        
        return CodeTemplate(
            file_path=f'frontend/src/services/{req.id}Service.js',
            content=content,
            template_type='service'
        )


class GitManager:
    """Git管理器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
    
    def create_branch(self, req: Requirement) -> str:
        """创建分支"""
        branch_name = f"{req.type}/{req.id}-{req.title.lower().replace(' ', '-')}"
        
        try:
            # 切换到主分支
            subprocess.run(['git', 'checkout', 'main'], 
                         cwd=self.project_root, check=True)
            
            # 拉取最新代码
            subprocess.run(['git', 'pull', 'origin', 'main'], 
                         cwd=self.project_root, check=True)
            
            # 创建新分支
            subprocess.run(['git', 'checkout', '-b', branch_name], 
                         cwd=self.project_root, check=True)
            
            return branch_name
        except subprocess.CalledProcessError as e:
            raise Exception(f"创建分支失败: {e}")
    
    def commit_changes(self, req: Requirement, message: str = None) -> str:
        """提交变更"""
        if not message:
            message = f"feat({req.id}): add test templates and code scaffolding for {req.title}"
        
        try:
            # 添加所有变更
            subprocess.run(['git', 'add', '.'], 
                         cwd=self.project_root, check=True)
            
            # 提交变更
            subprocess.run(['git', 'commit', '-m', message], 
                         cwd=self.project_root, check=True)
            
            # 获取提交哈希
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  cwd=self.project_root, 
                                  capture_output=True, text=True, check=True)
            
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"提交变更失败: {e}")
    
    def push_branch(self, branch_name: str) -> bool:
        """推送分支"""
        try:
            subprocess.run(['git', 'push', '-u', 'origin', branch_name], 
                         cwd=self.project_root, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"推送分支失败: {e}")
            return False


class IssueManager:
    """工单管理器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.issues_dir = self.project_root / '.github' / 'ISSUE_TEMPLATE'
        self.issues_dir.mkdir(parents=True, exist_ok=True)
    
    def create_issue_template(self, req: Requirement) -> str:
        """创建GitHub Issue模板"""
        template_content = f'''---
name: {req.title}
about: {req.description}
title: '[{req.type.upper()}] {req.title}'
labels: {', '.join(req.labels + [req.type, req.priority])}
assignees: {req.assignee or ''}
---

## 📋 需求描述

{req.description}

## 🎯 验收标准

{chr(10).join(f'- [ ] {criteria}' for criteria in req.acceptance_criteria)}

## 🔗 依赖关系

{chr(10).join(f'- #{dep}' for dep in req.dependencies) if req.dependencies else '无'}

## ⏱️ 预估工时

{req.estimated_hours} 小时

## 🏗️ 涉及组件

{chr(10).join(f'- {comp}' for comp in req.components)}

## 📝 实现清单

### 后端任务
- [ ] 创建数据模型
- [ ] 实现API接口
- [ ] 编写单元测试
- [ ] 编写集成测试

### 前端任务
- [ ] 创建Vue组件
- [ ] 实现服务层
- [ ] 编写单元测试
- [ ] 更新路由配置

### 测试任务
- [ ] 编写E2E测试
- [ ] 执行手动测试
- [ ] 验证验收标准

### 文档任务
- [ ] 更新API文档
- [ ] 更新用户文档
- [ ] 更新CHANGELOG

## 🚀 部署清单

- [ ] 数据库迁移
- [ ] 静态文件收集
- [ ] 环境变量配置
- [ ] 功能开关配置
'''
        
        template_file = self.issues_dir / f'{req.id}_template.md'
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        return str(template_file)
    
    def generate_issue_json(self, req: Requirement) -> str:
        """生成Issue JSON数据"""
        issue_data = {
            'title': f'[{req.type.upper()}] {req.title}',
            'body': self._generate_issue_body(req),
            'labels': req.labels + [req.type, req.priority] + req.components,
            'assignees': [req.assignee] if req.assignee else [],
            'milestone': None,
            'projects': []
        }
        
        issue_file = self.project_root / 'issues' / f'{req.id}.json'
        issue_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(issue_file, 'w', encoding='utf-8') as f:
            json.dump(issue_data, f, ensure_ascii=False, indent=2)
        
        return str(issue_file)
    
    def _generate_issue_body(self, req: Requirement) -> str:
        """生成Issue正文"""
        return f'''## 📋 需求描述

{req.description}

## 🎯 验收标准

{chr(10).join(f'- [ ] {criteria}' for criteria in req.acceptance_criteria)}

## 🔗 依赖关系

{chr(10).join(f'- #{dep}' for dep in req.dependencies) if req.dependencies else '无'}

## ⏱️ 预估工时

{req.estimated_hours} 小时

## 🏗️ 涉及组件

{chr(10).join(f'- {comp}' for comp in req.components)}
'''


class PipelineManager:
    """流水线管理器"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.parser = RequirementParser()
        self.test_generator = TestGenerator(project_root)
        self.code_generator = CodeGenerator(project_root)
        self.git_manager = GitManager(project_root)
        self.issue_manager = IssueManager(project_root)
    
    def run_pipeline(self, requirement_input: str, 
                    input_type: str = 'file',
                    create_branch: bool = True,
                    generate_tests: bool = True,
                    generate_code: bool = True,
                    create_issue: bool = True,
                    commit_changes: bool = True) -> Dict:
        """运行完整流水线"""
        
        result = {
            'success': False,
            'requirement': None,
            'branch': None,
            'tests': [],
            'code': [],
            'issue': None,
            'commit': None,
            'errors': []
        }
        
        try:
            # 1. 解析需求
            print("📋 解析需求...")
            if input_type == 'file':
                req = self.parser.parse_from_file(requirement_input)
            else:
                req_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                req = self.parser.parse_from_text(requirement_input, req_id)
            
            result['requirement'] = asdict(req)
            print(f"✅ 需求解析完成: {req.title}")
            
            # 2. 创建分支
            if create_branch:
                print("🌿 创建分支...")
                branch_name = self.git_manager.create_branch(req)
                result['branch'] = branch_name
                print(f"✅ 分支创建完成: {branch_name}")
            
            # 3. 生成测试
            if generate_tests:
                print("🧪 生成测试模板...")
                
                # 生成单元测试
                unit_tests = self.test_generator.generate_unit_tests(req)
                result['tests'].extend([asdict(t) for t in unit_tests])
                
                # 生成集成测试
                integration_tests = self.test_generator.generate_integration_tests(req)
                result['tests'].extend([asdict(t) for t in integration_tests])
                
                # 生成E2E测试
                e2e_tests = self.test_generator.generate_e2e_tests(req)
                result['tests'].extend([asdict(t) for t in e2e_tests])
                
                # 写入测试文件
                for test in unit_tests + integration_tests + e2e_tests:
                    test_file = Path(self.project_root) / test.file_path
                    test_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(test_file, 'w', encoding='utf-8') as f:
                        f.write(test.content)
                
                print(f"✅ 测试模板生成完成: {len(result['tests'])} 个文件")
            
            # 4. 生成代码
            if generate_code:
                print("💻 生成代码模板...")
                code_templates = self.code_generator.generate_code_templates(req)
                result['code'] = [asdict(t) for t in code_templates]
                
                # 写入代码文件
                for template in code_templates:
                    code_file = Path(self.project_root) / template.file_path
                    code_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(code_file, 'w', encoding='utf-8') as f:
                        f.write(template.content)
                
                print(f"✅ 代码模板生成完成: {len(code_templates)} 个文件")
            
            # 5. 创建工单
            if create_issue:
                print("📝 创建工单...")
                issue_template = self.issue_manager.create_issue_template(req)
                issue_json = self.issue_manager.generate_issue_json(req)
                result['issue'] = {
                    'template': issue_template,
                    'json': issue_json
                }
                print(f"✅ 工单创建完成: {issue_template}")
            
            # 6. 提交变更
            if commit_changes:
                print("📦 提交变更...")
                commit_hash = self.git_manager.commit_changes(req)
                result['commit'] = commit_hash
                print(f"✅ 变更提交完成: {commit_hash[:8]}")
                
                # 推送分支
                if create_branch and result['branch']:
                    print("🚀 推送分支...")
                    if self.git_manager.push_branch(result['branch']):
                        print("✅ 分支推送完成")
                    else:
                        print("⚠️ 分支推送失败")
            
            result['success'] = True
            print("\n🎉 流水线执行完成!")
            
        except Exception as e:
            error_msg = str(e)
            result['errors'].append(error_msg)
            print(f"❌ 流水线执行失败: {error_msg}")
        
        return result
    
    def generate_summary_report(self, result: Dict) -> str:
        """生成总结报告"""
        if not result['success']:
            return f"❌ 流水线执行失败:\n{chr(10).join(result['errors'])}"
        
        req = result['requirement']
        report = f'''🎉 需求→测试→实现流水线执行完成!

📋 需求信息:
- ID: {req['id']}
- 标题: {req['title']}
- 类型: {req['type']}
- 优先级: {req['priority']}
- 组件: {', '.join(req['components'])}
- 预估工时: {req['estimated_hours']} 小时

🌿 分支信息:
- 分支名称: {result['branch'] or '未创建'}

🧪 测试文件:
{chr(10).join(f"- {t['file_path']} ({t['test_type']})" for t in result['tests'])}

💻 代码文件:
{chr(10).join(f"- {c['file_path']} ({c['template_type']})" for c in result['code'])}

📝 工单文件:
- 模板: {result['issue']['template'] if result['issue'] else '未创建'}
- JSON: {result['issue']['json'] if result['issue'] else '未创建'}

📦 提交信息:
- 提交哈希: {result['commit'][:8] if result['commit'] else '未提交'}

🚀 下一步:
1. 查看生成的测试和代码文件
2. 根据需求完善实现逻辑
3. 运行测试确保功能正确
4. 创建Pull Request进行代码审查
5. 部署到测试环境进行验证
'''
        
        return report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='需求→测试→实现自动化流水线',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  # 从文件解析需求并运行完整流水线
  python req_to_test_pipeline.py --input requirements/user_auth.md
  
  # 从文本解析需求
  python req_to_test_pipeline.py --input "标题: 用户认证\n类型: feature\n描述: 实现用户登录功能" --input-type text
  
  # 只生成测试，不创建分支和提交
  python req_to_test_pipeline.py --input requirements/user_auth.md --no-branch --no-commit
  
  # 预览模式，不实际创建文件
  python req_to_test_pipeline.py --input requirements/user_auth.md --dry-run
'''
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='需求输入（文件路径或文本内容）'
    )
    
    parser.add_argument(
        '--input-type', '-t',
        choices=['file', 'text'],
        default='file',
        help='输入类型（默认: file）'
    )
    
    parser.add_argument(
        '--project-root', '-p',
        default='.',
        help='项目根目录（默认: 当前目录）'
    )
    
    parser.add_argument(
        '--no-branch',
        action='store_true',
        help='不创建Git分支'
    )
    
    parser.add_argument(
        '--no-tests',
        action='store_true',
        help='不生成测试文件'
    )
    
    parser.add_argument(
        '--no-code',
        action='store_true',
        help='不生成代码文件'
    )
    
    parser.add_argument(
        '--no-issue',
        action='store_true',
        help='不创建工单'
    )
    
    parser.add_argument(
        '--no-commit',
        action='store_true',
        help='不提交变更'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预览模式，不实际创建文件'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='输出报告文件路径'
    )
    
    args = parser.parse_args()
    
    # 创建流水线管理器
    pipeline = PipelineManager(args.project_root)
    
    if args.dry_run:
        print("🔍 预览模式，不会实际创建文件")
    
    # 运行流水线
    result = pipeline.run_pipeline(
        requirement_input=args.input,
        input_type=args.input_type,
        create_branch=not args.no_branch and not args.dry_run,
        generate_tests=not args.no_tests,
        generate_code=not args.no_code,
        create_issue=not args.no_issue,
        commit_changes=not args.no_commit and not args.dry_run
    )
    
    # 生成报告
    report = pipeline.generate_summary_report(result)
    print("\n" + "="*60)
    print(report)
    
    # 保存报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 报告已保存到: {args.output}")
    
    # 返回退出码
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()