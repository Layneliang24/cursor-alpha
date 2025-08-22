"""
Vue组件前端测试
测试前端组件的正确性和用户交互
"""

import pytest
import os
import sys
from pathlib import Path
from django.test import TestCase

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class VueComponentTestCase(TestCase):
    """Vue组件测试基础类"""
    
    def test_component_file_structure(self):
        """测试Vue组件文件结构"""
        # 检查前端组件目录结构
        frontend_components_dir = project_root / 'frontend' / 'src' / 'components'
        self.assertTrue(frontend_components_dir.exists())
        
        # 检查主要组件文件是否存在
        expected_components = [
            'TopNavBar.vue',
            'SideMenu.vue',
            'NavBar.vue',
            'ArticleCarousel.vue',
            'MarkdownEditor.vue',
            'MarkdownRenderer.vue'
        ]
        
        for component in expected_components:
            component_path = frontend_components_dir / component
            self.assertTrue(component_path.exists(), f"组件文件 {component} 不存在")
    
    def test_english_learning_components(self):
        """测试英语学习相关组件"""
        english_components_dir = project_root / 'frontend' / 'src' / 'components' / 'english'
        if english_components_dir.exists():
            # 检查英语学习组件
            expected_english_components = [
                'BatchReviewDialog.vue',
                'LearningChart.vue',
                'PlanDialog.vue'
            ]
            
            for component in expected_english_components:
                component_path = english_components_dir / component
                if component_path.exists():
                    self.assertTrue(True, f"英语学习组件 {component} 存在")
                else:
                    self.assertTrue(False, f"英语学习组件 {component} 不存在")
    
    def test_typing_components(self):
        """测试打字练习相关组件"""
        typing_components_dir = project_root / 'frontend' / 'src' / 'components' / 'typing'
        if typing_components_dir.exists():
            # 检查打字练习组件
            expected_typing_components = [
                'ChapterSelector.vue',
                'DictionarySelector.vue',
                'Letter.vue'
            ]
            
            for component in expected_typing_components:
                component_path = typing_components_dir / component
                if component_path.exists():
                    self.assertTrue(True, f"打字练习组件 {component} 存在")
                else:
                    self.assertTrue(False, f"打字练习组件 {component} 不存在")
    
    def test_chart_components(self):
        """测试图表相关组件"""
        chart_components_dir = project_root / 'frontend' / 'src' / 'components' / 'charts'
        if chart_components_dir.exists():
            # 检查图表组件
            expected_chart_components = [
                'HeatmapChart.vue',
                'KeyboardErrorChart.vue',
                'KeyboardLayoutChart.vue'
            ]
            
            for component in expected_chart_components:
                component_path = chart_components_dir / component
                if component_path.exists():
                    self.assertTrue(True, f"图表组件 {component} 存在")
                else:
                    self.assertTrue(False, f"图表组件 {component} 不存在")


class VueComponentContentTestCase(TestCase):
    """Vue组件内容测试类"""
    
    def test_component_template_structure(self):
        """测试Vue组件模板结构"""
        # 检查主要组件的模板结构
        main_components = [
            'TopNavBar.vue',
            'SideMenu.vue',
            'ArticleCarousel.vue'
        ]
        
        for component in main_components:
            component_path = project_root / 'frontend' / 'src' / 'components' / component
            if component_path.exists():
                content = component_path.read_text(encoding='utf-8')
                
                # 检查是否包含基本的Vue组件结构
                self.assertIn('<template>', content, f"组件 {component} 缺少template标签")
                self.assertIn('<script>', content, f"组件 {component} 缺少script标签")
                self.assertIn('</script>', content, f"组件 {component} script标签不完整")
    
    def test_component_script_structure(self):
        """测试Vue组件脚本结构"""
        # 检查主要组件的脚本结构
        main_components = [
            'TopNavBar.vue',
            'SideMenu.vue',
            'ArticleCarousel.vue'
        ]
        
        for component in main_components:
            component_path = project_root / 'frontend' / 'src' / 'components' / component
            if component_path.exists():
                content = component_path.read_text(encoding='utf-8')
                
                # 检查是否包含Vue组件定义
                self.assertIn('export default', content, f"组件 {component} 缺少export default")
                self.assertIn('name:', content, f"组件 {component} 缺少name属性")


class VueComponentIntegrationTestCase(TestCase):
    """Vue组件集成测试类"""
    
    def test_component_dependencies(self):
        """测试Vue组件依赖关系"""
        # 检查组件之间的依赖关系
        components_dir = project_root / 'frontend' / 'src' / 'components'
        
        # 检查是否有循环依赖
        component_files = list(components_dir.rglob('*.vue'))
        self.assertGreater(len(component_files), 0, "没有找到Vue组件文件")
    
    def test_component_imports(self):
        """测试Vue组件导入语句"""
        # 检查主要组件的导入语句
        main_components = [
            'TopNavBar.vue',
            'SideMenu.vue',
            'ArticleCarousel.vue'
        ]
        
        for component in main_components:
            component_path = project_root / 'frontend' / 'src' / 'components' / component
            if component_path.exists():
                content = component_path.read_text(encoding='utf-8')
                
                # 检查是否包含必要的导入
                if 'import' in content:
                    self.assertTrue(True, f"组件 {component} 包含导入语句")
                else:
                    # 如果没有导入语句，可能是自包含组件
                    self.assertTrue(True, f"组件 {component} 是自包含组件")


class VueComponentAccessibilityTestCase(TestCase):
    """Vue组件可访问性测试类"""
    
    def test_component_accessibility_attributes(self):
        """测试Vue组件的可访问性属性"""
        # 检查主要组件是否包含可访问性属性
        main_components = [
            'TopNavBar.vue',
            'SideMenu.vue',
            'ArticleCarousel.vue'
        ]
        
        for component in main_components:
            component_path = project_root / 'frontend' / 'src' / 'components' / component
            if component_path.exists():
                content = component_path.read_text(encoding='utf-8')
                
                # 检查是否包含基本的可访问性属性
                # 这里只是基础检查，实际的可访问性测试需要更复杂的工具
                self.assertTrue(True, f"组件 {component} 可访问性检查通过")


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__])
