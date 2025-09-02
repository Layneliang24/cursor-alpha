#!/usr/bin/env python3
"""
测试框架类型和依赖关系分析脚本
扩展分析脚本，识别具体的测试框架类型并分析依赖关系
"""

import os
import re
import json
from collections import defaultdict
from pathlib import Path

class FrameworkAnalyzer:
    def __init__(self, report_file='test_structure_report.json'):
        self.report_file = report_file
        self.project_root = Path('.')
        self.framework_patterns = {
            'pytest': [
                r'import\s+pytest',
                r'from\s+pytest\s+import',
                r'@pytest\.',
                r'pytest\.',
                r'def\s+test_',
                r'class\s+\w+Test\w*:'
            ],
            'unittest': [
                r'import\s+unittest',
                r'from\s+unittest\s+import',
                r'class\s+\w+Test\w*\(unittest\.TestCase\):',
                r'self\.assert',
                r'unittest\.'
            ],
            'django_test': [
                r'from\s+django\.test\s+import',
                r'from\s+django\.contrib\.auth\s+import',
                r'class\s+\w+Test\w*\(TestCase\):',
                r'APIClient',
                r'@classmethod\s+def\s+setUpTestData'
            ],
            'vitest': [
                r'import\s+.*\s+from\s+[\'"]vitest[\'"]',
                r'describe\s*\(',
                r'it\s*\(',
                r'test\s*\(',
                r'expect\s*\(',
                r'vi\.'
            ],
            'playwright': [
                r'import\s+.*\s+from\s+[\'"]@playwright/test[\'"]',
                r'test\s*\(',
                r'page\.',
                r'locator\s*\(',
                r'expect\s*\('
            ],
            'jest': [
                r'import\s+.*\s+from\s+[\'"]jest[\'"]',
                r'describe\s*\(',
                r'it\s*\(',
                r'test\s*\(',
                r'expect\s*\(',
                r'jest\.'
            ]
        }
        
        self.framework_stats = defaultdict(int)
        self.file_framework_map = {}
        self.dependency_analysis = defaultdict(dict)
        
    def load_report(self):
        """加载测试结构报告"""
        try:
            with open(self.report_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 加载报告文件失败: {e}")
            return None
    
    def analyze_framework_types(self, report):
        """分析每个测试文件的框架类型"""
        print("🔍 分析测试文件框架类型...")
        
        for dir_name, files in report['directory_structure'].items():
            print(f"📁 分析目录: {dir_name}")
            
            for file_info in files:
                file_path = file_info['file']
                file_type = file_info['type']
                
                if file_type == 'python':
                    self._analyze_python_framework(file_path)
                elif file_type == 'javascript':
                    self._analyze_javascript_framework(file_path)
    
    def _analyze_python_framework(self, file_path):
        """分析Python测试文件的框架类型"""
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            detected_frameworks = []
            
            # 检查各种框架模式
            for framework, patterns in self.framework_patterns.items():
                if framework in ['pytest', 'unittest', 'django_test']:
                    for pattern in patterns:
                        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                            detected_frameworks.append(framework)
                            break
            
            # 如果没有检测到特定框架，标记为unknown
            if not detected_frameworks:
                detected_frameworks = ['unknown_python']
            
            # 记录结果
            primary_framework = detected_frameworks[0]
            self.framework_stats[primary_framework] += 1
            self.file_framework_map[file_path] = {
                'frameworks': detected_frameworks,
                'primary': primary_framework,
                'content_length': len(content)
            }
            
        except Exception as e:
            print(f"⚠️  分析Python文件 {file_path} 时出错: {e}")
    
    def _analyze_javascript_framework(self, file_path):
        """分析JavaScript测试文件的框架类型"""
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            detected_frameworks = []
            
            # 检查各种框架模式
            for framework, patterns in self.framework_patterns.items():
                if framework in ['vitest', 'playwright', 'jest']:
                    for pattern in patterns:
                        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                            detected_frameworks.append(framework)
                            break
            
            # 如果没有检测到特定框架，标记为unknown
            if not detected_frameworks:
                detected_frameworks = ['unknown_javascript']
            
            # 记录结果
            primary_framework = detected_frameworks[0]
            self.framework_stats[primary_framework] += 1
            self.file_framework_map[file_path] = {
                'frameworks': detected_frameworks,
                'primary': primary_framework,
                'content_length': len(content)
            }
            
        except Exception as e:
            print(f"⚠️  分析JavaScript文件 {file_path} 时出错: {e}")
    
    def analyze_dependencies(self, report):
        """分析依赖关系"""
        print("\n🔗 分析依赖关系...")
        
        dependencies = report.get('dependencies', {})
        
        for file_path, deps in dependencies.items():
            if file_path in self.file_framework_map:
                framework_info = self.file_framework_map[file_path]
                
                # 分析依赖类型
                dep_types = defaultdict(int)
                external_deps = []
                internal_deps = []
                
                for dep in deps:
                    if dep.startswith('.'):
                        internal_deps.append(dep)
                    else:
                        external_deps.append(dep)
                        dep_types[dep] += 1
                
                self.dependency_analysis[file_path] = {
                    'framework': framework_info['primary'],
                    'total_deps': len(deps),
                    'external_deps': external_deps,
                    'internal_deps': internal_deps,
                    'dep_types': dict(dep_types),
                    'content_length': framework_info['content_length']
                }
    
    def generate_framework_report(self):
        """生成框架分析报告"""
        print("\n📊 生成框架分析报告...")
        
        report = {
            'framework_statistics': dict(self.framework_stats),
            'file_framework_mapping': self.file_framework_map,
            'dependency_analysis': dict(self.dependency_analysis),
            'summary': {
                'total_files_analyzed': len(self.file_framework_map),
                'framework_distribution': dict(self.framework_stats),
                'avg_dependencies_per_file': sum(len(info.get('external_deps', [])) for info in self.dependency_analysis.values()) / max(len(self.dependency_analysis), 1)
            }
        }
        
        return report
    
    def save_framework_report(self, report, output_file='framework_analysis_report.json'):
        """保存框架分析报告"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"✅ 框架分析报告已保存到: {output_file}")
        except Exception as e:
            print(f"❌ 保存框架分析报告时出错: {e}")
    
    def print_framework_summary(self, report):
        """打印框架分析摘要"""
        print("\n" + "="*60)
        print("🔧 测试框架类型分析摘要")
        print("="*60)
        
        summary = report['summary']
        print(f"📄 分析的文件总数: {summary['total_files_analyzed']}")
        print(f"🔧 框架类型分布:")
        
        for framework, count in report['framework_statistics'].items():
            print(f"   {framework}: {count} 个文件")
        
        print(f"\n📊 平均外部依赖数: {summary['avg_dependencies_per_file']:.2f}")
        
        print("\n📂 各框架文件示例:")
        for framework in report['framework_statistics'].keys():
            example_files = [f for f, info in self.file_framework_map.items() 
                           if info['primary'] == framework][:3]
            if example_files:
                print(f"   {framework}:")
                for file in example_files:
                    print(f"     - {file}")

def main():
    """主函数"""
    print("🚀 开始分析测试框架类型和依赖关系...")
    
    # 创建分析器
    analyzer = FrameworkAnalyzer()
    
    # 加载测试结构报告
    report = analyzer.load_report()
    if not report:
        print("❌ 无法加载测试结构报告，退出")
        return
    
    # 分析框架类型
    analyzer.analyze_framework_types(report)
    
    # 分析依赖关系
    analyzer.analyze_dependencies(report)
    
    # 生成报告
    framework_report = analyzer.generate_framework_report()
    
    # 保存报告
    analyzer.save_framework_report(framework_report)
    
    # 打印摘要
    analyzer.print_framework_summary(framework_report)
    
    print("\n🎉 框架分析完成！")

if __name__ == "__main__":
    main()
