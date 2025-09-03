#!/usr/bin/env python3
"""
测试文件依赖关系分析脚本
分析测试文件间的导入依赖关系，生成依赖图
"""

import os
import re
import json
from collections import defaultdict, deque
from pathlib import Path
import ast

class DependencyAnalyzer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.dependencies = defaultdict(set)
        self.reverse_dependencies = defaultdict(set)
        self.import_patterns = {
            'python': [
                r'^import\s+(\w+)',
                r'^from\s+(\w+)\s+import',
                r'^from\s+([\w.]+)\s+import'
            ],
            'javascript': [
                r'^import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
                r'^import\s+([\w{][\w\s{},]*)\s+from',
                r'^const\s+\w+\s*=\s*require\s*\(\s*[\'"]([^\'"]+)[\'"]'
            ]
        }
        
    def analyze_python_dependencies(self, file_path):
        """分析Python文件的依赖关系"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 使用AST解析Python文件
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        
            return imports
        except Exception as e:
            print(f"❌ 解析Python文件 {file_path} 失败: {e}")
            return []
    
    def analyze_javascript_dependencies(self, file_path):
        """分析JavaScript文件的依赖关系"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            imports = []
            for pattern in self.import_patterns['javascript']:
                matches = re.findall(pattern, content, re.MULTILINE)
                imports.extend(matches)
                
            return imports
        except Exception as e:
            print(f"❌ 解析JavaScript文件 {file_path} 失败: {e}")
            return []
    
    def build_dependency_graph(self, test_files):
        """构建依赖关系图"""
        print("🔗 构建依赖关系图...")
        
        for file_info in test_files:
            file_path = file_info['file']
            file_type = file_info['type']
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                continue
                
            if file_type == 'python':
                imports = self.analyze_python_dependencies(full_path)
            elif file_type == 'javascript':
                imports = self.analyze_javascript_dependencies(full_path)
            else:
                continue
                
            # 记录依赖关系
            for imp in imports:
                self.dependencies[str(file_path)].add(imp)
                self.reverse_dependencies[imp].add(str(file_path))
    
    def detect_circular_dependencies(self):
        """检测循环依赖"""
        print("🔄 检测循环依赖...")
        
        visited = set()
        rec_stack = set()
        circular_deps = []
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependencies.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    circular_deps.append((node, neighbor))
                    return True
                    
            rec_stack.remove(node)
            return False
        
        for node in self.dependencies:
            if node not in visited:
                dfs(node)
                
        return circular_deps
    
    def generate_dependency_report(self):
        """生成依赖关系报告"""
        print("📊 生成依赖关系报告...")
        
        report = {
            'summary': {
                'total_files': len(self.dependencies),
                'total_imports': sum(len(imports) for imports in self.dependencies.values()),
                'circular_dependencies': len(self.detect_circular_dependencies())
            },
            'dependencies': {k: list(v) for k, v in self.dependencies.items()},
            'reverse_dependencies': {k: list(v) for k, v in self.reverse_dependencies.items()},
            'circular_dependencies': self.detect_circular_dependencies()
        }
        
        # 保存报告
        with open('dependency_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print("✅ 依赖关系报告已生成: dependency_analysis_report.json")
        return report

def main():
    """主函数"""
    analyzer = DependencyAnalyzer()
    
    # 加载测试结构报告
    try:
        with open('test_structure_report.json', 'r', encoding='utf-8') as f:
            test_report = json.load(f)
    except FileNotFoundError:
        print("❌ 找不到test_structure_report.json，请先运行analyze_test_structure_fixed.py")
        return
    
    # 收集所有测试文件
    all_test_files = []
    for dir_name, files in test_report['directory_structure'].items():
        all_test_files.extend(files)
    
    # 分析依赖关系
    analyzer.build_dependency_graph(all_test_files)
    
    # 生成报告
    report = analyzer.generate_dependency_report()
    
    print(f"\n📈 依赖分析完成:")
    print(f"   - 分析文件数: {report['summary']['total_files']}")
    print(f"   - 总导入数: {report['summary']['total_imports']}")
    print(f"   - 循环依赖: {report['summary']['circular_dependencies']}")

if __name__ == "__main__":
    main()

