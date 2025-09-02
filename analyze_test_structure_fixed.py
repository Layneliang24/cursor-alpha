#!/usr/bin/env python3
"""
测试文件结构分析脚本
分析项目中的所有测试文件，生成结构图和依赖关系
"""

import os
import re
from collections import defaultdict
from pathlib import Path
import json

class TestStructureAnalyzer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.test_dirs = [
            'tests',
            'backend/tests', 
            'backend/apps/ai/tests',
            'frontend/tests',
            'e2e/tests',
            'ai_pipeline/tests'
        ]
        
        # 测试文件模式
        self.test_patterns = {
            'python': [
                r'test_.*\.py$',
                r'.*_test\.py$',
                r'.*Test\.py$'
            ],
            'javascript': [
                r'.*\.test\.js$',
                r'.*\.test\.ts$',
                r'.*\.spec\.js$',
                r'.*\.spec\.ts$'
            ]
        }
        
        # 存储分析结果
        self.file_structure = defaultdict(list)
        self.framework_stats = defaultdict(int)
        self.file_count = 0
        
    def is_test_file(self, filename, filepath):
        """判断是否为测试文件"""
        for lang, patterns in self.test_patterns.items():
            for pattern in patterns:
                if re.match(pattern, filename):
                    return lang
        return None
    
    def analyze_structure(self):
        """分析测试文件结构"""
        print("🔍 开始分析测试文件结构...")
        
        for test_dir in self.test_dirs:
            dir_path = self.project_root / test_dir
            if not dir_path.exists():
                print(f"⚠️  目录不存在: {test_dir}")
                continue
                
            print(f"📁 分析目录: {test_dir}")
            self._walk_directory(dir_path, test_dir)
    
    def _walk_directory(self, dir_path, relative_dir):
        """遍历目录"""
        try:
            for root, dirs, files in os.walk(dir_path):
                # 跳过虚拟环境和缓存目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__', 'node_modules']]
                
                for file in files:
                    file_path = Path(root) / file
                    relative_path = file_path.relative_to(self.project_root)
                    
                    # 检查是否为测试文件
                    test_type = self.is_test_file(file, str(file_path))
                    if test_type:
                        self.file_structure[relative_dir].append({
                            'file': str(relative_path),
                            'type': test_type,
                            'size': file_path.stat().st_size if file_path.exists() else 0
                        })
                        self.framework_stats[test_type] += 1
                        self.file_count += 1
                        
        except Exception as e:
            print(f"❌ 遍历目录 {dir_path} 时出错: {e}")
    
    def generate_tree_structure(self):
        """生成树状结构"""
        print("\n🌳 生成树状结构...")
        
        tree = {}
        for dir_name, files in self.file_structure.items():
            current = tree
            parts = dir_name.split('/')
            
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current['__files__'] = files
        
        return tree
    
    def generate_dependency_analysis(self):
        """生成依赖关系分析"""
        print("🔗 分析依赖关系...")
        
        dependencies = defaultdict(set)
        
        for dir_name, files in self.file_structure.items():
            for file_info in files:
                file_path = file_info['file']
                file_type = file_info['type']
                
                # 分析Python文件的导入
                if file_type == 'python':
                    self._analyze_python_imports(file_path, dependencies)
                # 分析JavaScript文件的导入
                elif file_type == 'javascript':
                    self._analyze_javascript_imports(file_path, dependencies)
        
        return dependencies
    
    def _analyze_python_imports(self, file_path, dependencies):
        """分析Python文件的导入"""
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 查找import语句
            import_patterns = [
                r'^import\s+(\w+)',
                r'^from\s+(\w+)',
                r'^from\s+([\w.]+)\s+import'
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    if match and not match.startswith('.'):
                        dependencies[file_path].add(match)
                        
        except Exception as e:
            print(f"⚠️  分析Python文件 {file_path} 时出错: {e}")
    
    def _analyze_javascript_imports(self, file_path, dependencies):
        """分析JavaScript文件的导入"""
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                return
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 查找import语句
            import_patterns = [
                r'^import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
                r'^import\s+[\'"]([^\'"]+)[\'"]',
                r'^const\s+\w+\s*=\s*require\s*\(\s*[\'"]([^\'"]+)[\'"]'
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    if match and not match.startswith('.'):
                        dependencies[file_path].add(match)
                        
        except Exception as e:
            print(f"⚠️  分析JavaScript文件 {file_path} 时出错: {e}")
    
    def generate_report(self):
        """生成分析报告"""
        print("\n📊 生成分析报告...")
        
        # 修复JSON序列化问题：将set转换为list
        dependencies = self.generate_dependency_analysis()
        dependencies_serializable = {k: list(v) for k, v in dependencies.items()}
        
        # 基础统计
        report = {
            'summary': {
                'total_test_files': self.file_count,
                'test_directories': len(self.file_structure),
                'framework_distribution': dict(self.framework_stats)
            },
            'directory_structure': dict(self.file_structure),
            'tree_structure': self.generate_tree_structure(),
            'dependencies': dependencies_serializable
        }
        
        return report
    
    def save_report(self, report, output_file='test_structure_report.json'):
        """保存报告到文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"✅ 报告已保存到: {output_file}")
        except Exception as e:
            print(f"❌ 保存报告时出错: {e}")
    
    def print_summary(self, report):
        """打印摘要信息"""
        print("\n" + "="*60)
        print("📋 测试文件结构分析摘要")
        print("="*60)
        
        summary = report['summary']
        print(f"📁 测试目录数量: {summary['test_directories']}")
        print(f"📄 测试文件总数: {summary['total_test_files']}")
        print(f"🔧 框架类型分布:")
        
        for framework, count in summary['framework_distribution'].items():
            print(f"   {framework}: {count} 个文件")
        
        print("\n📂 各目录文件数量:")
        for dir_name, files in report['directory_structure'].items():
            print(f"   {dir_name}: {len(files)} 个文件")
        
        print("\n🔗 依赖关系统计:")
        total_deps = sum(len(deps) for deps in report['dependencies'].values())
        print(f"   总依赖关系: {total_deps}")
        print(f"   有依赖的文件: {len(report['dependencies'])}")

def main():
    """主函数"""
    print("🚀 开始分析项目测试文件结构...")
    
    # 创建分析器
    analyzer = TestStructureAnalyzer()
    
    # 执行分析
    analyzer.analyze_structure()
    
    # 生成报告
    report = analyzer.generate_report()
    
    # 保存报告
    analyzer.save_report(report)
    
    # 打印摘要
    analyzer.print_summary(report)
    
    print("\n🎉 分析完成！")

if __name__ == "__main__":
    main()
