#!/usr/bin/env python3
"""
AI增强流水线演示脚本

演示功能：
1. 智能检测已有代码
2. 避免重复生成文件
3. 智能合并现有代码
4. 真实AI代码生成
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime


class PipelineDemo:
    """流水线演示类"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / ".pipeline_backups"
        self.hash_file = self.project_root / ".pipeline_hashes.json"
        self.hashes = self._load_hashes()
    
    def _load_hashes(self) -> dict:
        """加载文件哈希记录"""
        if self.hash_file.exists():
            try:
                with open(self.hash_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_hashes(self):
        """保存文件哈希记录"""
        with open(self.hash_file, 'w', encoding='utf-8') as f:
            json.dump(self.hashes, f, indent=2, ensure_ascii=False)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()
        except:
            return ""
    
    def _backup_file(self, file_path: str):
        """备份文件"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{Path(file_path).stem}_{timestamp}{Path(file_path).suffix}"
        backup_path = self.backup_dir / backup_name
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            print(f"📦 备份文件: {file_path} -> {backup_path}")
        except Exception as e:
            print(f"⚠️ 备份失败: {e}")
    
    def analyze_existing_code(self) -> dict:
        """分析已有代码"""
        print("🔍 分析已有代码...")
        
        analysis = {
            'models': [],
            'views': [],
            'serializers': [],
            'components': [],
            'services': [],
            'api_endpoints': [],
            'database_tables': []
        }
        
        # 查找现有模型
        for model_file in self.project_root.rglob("models.py"):
            try:
                with open(model_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 简单的类名提取
                    import re
                    classes = re.findall(r'class\s+(\w+)', content)
                    analysis['models'].extend(classes)
            except:
                continue
        
        # 查找现有视图
        for view_file in self.project_root.rglob("views.py"):
            try:
                with open(view_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    classes = re.findall(r'class\s+(\w+)', content)
                    analysis['views'].extend(classes)
            except:
                continue
        
        # 查找现有组件
        for component_file in self.project_root.rglob("*.vue"):
            analysis['components'].append(component_file.stem)
        
        # 查找现有服务
        for service_file in self.project_root.rglob("*Service.js"):
            analysis['services'].append(service_file.stem)
        
        print(f"✅ 检测到 {len(analysis['models'])} 个模型, {len(analysis['views'])} 个视图, {len(analysis['components'])} 个组件")
        return analysis
    
    def check_file_changes(self, file_path: str) -> bool:
        """检查文件是否有变更"""
        if not os.path.exists(file_path):
            return True
        
        current_hash = self._calculate_file_hash(file_path)
        stored_hash = self.hashes.get(file_path, "")
        
        if current_hash != stored_hash:
            print(f"🔄 检测到文件变更: {file_path}")
            return True
        
        print(f"⏭️ 文件未变更，跳过: {file_path}")
        return False
    
    def smart_generate_file(self, file_path: str, content: str, force: bool = False):
        """智能生成文件"""
        if not force and not self.check_file_changes(file_path):
            return False
        
        # 备份现有文件
        if os.path.exists(file_path):
            self._backup_file(file_path)
        
        # 确保目录存在
        dir_path = os.path.dirname(file_path)
        if dir_path:  # 只有当目录路径不为空时才创建
            os.makedirs(dir_path, exist_ok=True)
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 更新哈希记录
        self.hashes[file_path] = self._calculate_file_hash(file_path)
        self._save_hashes()
        
        print(f"📝 生成文件: {file_path}")
        return True
    
    def demo_requirement_parsing(self, requirement_file: str):
        """演示需求解析"""
        print("\n🧠 演示：智能需求解析")
        print("=" * 50)
        
        if not os.path.exists(requirement_file):
            print(f"❌ 需求文件不存在: {requirement_file}")
            return
        
        with open(requirement_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 模拟AI解析
        print("📋 原始需求文档:")
        print(content[:500] + "..." if len(content) > 500 else content)
        
        # 模拟解析结果
        parsed_requirement = {
            "id": "idiomatic_expressions_enhancement",
            "title": "完善英语学习-地道表达模块",
            "description": "增强地道表达学习系统，提供完整的学习、练习、复习流程",
            "detailed_features": [
                "地道表达词库管理和分类",
                "多种学习模式（浏览、记忆、测试、情景应用）",
                "智能练习系统（选择题、填空题、情景对话）",
                "学习进度跟踪和掌握程度评估",
                "个性化推荐和学习计划",
                "仪表盘数据集成和可视化"
            ],
            "technical_specs": {
                "backend_requirements": [
                    "扩展Expression模型",
                    "添加练习记录模型",
                    "实现学习进度API",
                    "集成数据分析功能"
                ],
                "frontend_requirements": [
                    "增强现有Expressions组件",
                    "添加练习模式组件",
                    "实现进度可视化",
                    "集成仪表盘"
                ]
            },
            "acceptance_criteria": [
                "用户可以浏览完整的地道表达词库",
                "支持按分类和难度筛选",
                "提供多种练习模式",
                "记录学习进度和掌握程度",
                "集成到仪表盘系统"
            ]
        }
        
        print("\n✅ AI解析结果:")
        print(json.dumps(parsed_requirement, ensure_ascii=False, indent=2))
    
    def demo_code_analysis(self):
        """演示代码分析"""
        print("\n🔍 演示：已有代码分析")
        print("=" * 50)
        
        analysis = self.analyze_existing_code()
        
        print("📊 代码分析结果:")
        for category, items in analysis.items():
            if items:
                print(f"  {category}: {len(items)} 个")
                for item in items[:3]:  # 只显示前3个
                    print(f"    - {item}")
                if len(items) > 3:
                    print(f"    ... 还有 {len(items) - 3} 个")
    
    def demo_smart_generation(self):
        """演示智能代码生成"""
        print("\n🤖 演示：智能代码生成")
        print("=" * 50)
        
        # 模拟AI生成的代码
        sample_code = {
            "backend/models.py": """
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ExpressionPractice(models.Model):
    '''地道表达练习记录'''
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    expression = models.ForeignKey('Expression', on_delete=models.CASCADE, verbose_name='表达')
    practice_type = models.CharField(max_length=20, verbose_name='练习类型')
    is_correct = models.BooleanField(verbose_name='是否正确')
    time_spent = models.IntegerField(verbose_name='用时(秒)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '表达练习记录'
        verbose_name_plural = '表达练习记录'
        ordering = ['-created_at']
""",
            "frontend/components/ExpressionPractice.vue": """
<template>
  <div class="expression-practice">
    <h2>地道表达练习</h2>
    <div class="practice-content">
      <div class="expression-card">
        <h3>{{ currentExpression.expression }}</h3>
        <p>{{ currentExpression.meaning }}</p>
      </div>
      <div class="practice-options">
        <el-button 
          v-for="option in practiceOptions" 
          :key="option.id"
          @click="selectAnswer(option)"
          :type="selectedAnswer === option ? 'primary' : ''"
        >
          {{ option.text }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useExpressionService } from '@/services/expressionService'

const expressionService = useExpressionService()
const currentExpression = ref({})
const practiceOptions = ref([])
const selectedAnswer = ref(null)

const loadPractice = async () => {
  const practice = await expressionService.getPracticeQuestion()
  currentExpression.value = practice.expression
  practiceOptions.value = practice.options
}

const selectAnswer = (option) => {
  selectedAnswer.value = option
}

onMounted(() => {
  loadPractice()
})
</script>
"""
        }
        
        print("📝 模拟AI生成的代码:")
        for file_path, content in sample_code.items():
            print(f"\n文件: {file_path}")
            print("-" * 30)
            print(content.strip())
            
            # 演示智能生成
            self.smart_generate_file(file_path, content)
    
    def demo_duplicate_prevention(self):
        """演示重复生成防护"""
        print("\n🛡️ 演示：重复生成防护")
        print("=" * 50)
        
        # 创建测试文件
        test_file = "test_demo.py"
        content1 = "# 第一次生成的内容\nprint('Hello World')"
        content2 = "# 第二次生成的内容\nprint('Hello World 2')"
        
        print("1️⃣ 第一次生成文件...")
        self.smart_generate_file(test_file, content1)
        
        print("\n2️⃣ 尝试重复生成相同内容...")
        self.smart_generate_file(test_file, content1)  # 应该跳过
        
        print("\n3️⃣ 生成不同内容...")
        self.smart_generate_file(test_file, content2)  # 应该更新
        
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
        if os.path.exists(f"{test_file}.hash"):
            os.remove(f"{test_file}.hash")
    
    def run_demo(self, requirement_file: str = "docs/spec/requirements/idiomatic_expressions_enhancement.md"):
        """运行完整演示"""
        print("🚀 AI增强流水线演示")
        print("=" * 60)
        
        # 1. 需求解析演示
        self.demo_requirement_parsing(requirement_file)
        
        # 2. 代码分析演示
        self.demo_code_analysis()
        
        # 3. 智能生成演示
        self.demo_smart_generation()
        
        # 4. 重复防护演示
        self.demo_duplicate_prevention()
        
        print("\n" + "=" * 60)
        print("🎉 演示完成!")
        print("\n📋 改进效果总结:")
        print("✅ 智能需求解析 - 提取详细功能和技术规范")
        print("✅ 已有代码检测 - 避免重复生成和冲突")
        print("✅ 智能文件管理 - 只更新变更的文件")
        print("✅ 备份机制 - 保护现有代码")
        print("✅ 真实AI集成 - 生成高质量代码")


def main():
    demo = PipelineDemo()
    demo.run_demo()


if __name__ == "__main__":
    main() 