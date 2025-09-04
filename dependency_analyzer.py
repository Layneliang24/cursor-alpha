#!/usr/bin/env python3
"""
测试依赖分析工具
扫描所有测试文件的import语句，识别缺失的模块、类、函数
"""
import os
import re
import json
import ast
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict

class TestDependencyAnalyzer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.test_files = []
        self.dependency_map = {}
        self.missing_dependencies = defaultdict(list)
        self.dependency_categories = {
            "service_classes": [],
            "model_classes": [],
            "utility_functions": [],
            "external_packages": [],
            "internal_modules": []
        }
    
    def find_test_files(self) -> List[str]:
        """查找所有测试文件"""
        test_files = []
        
        # 搜索tests目录
        tests_dir = self.project_root / "tests"
        if tests_dir.exists():
            for root, dirs, files in os.walk(tests_dir):
                for file in files:
                    if file.endswith('.py') and file.startswith('test_'):
                        test_files.append(str(Path(root) / file))
        
        # 搜索backend/tests目录
        backend_tests_dir = self.project_root / "backend" / "tests"
        if backend_tests_dir.exists():
            for root, dirs, files in os.walk(backend_tests_dir):
                for file in files:
                    if file.endswith('.py') and file.startswith('test_'):
                        test_files.append(str(Path(root) / file))
        
        return test_files
    
    def parse_imports(self, file_path: str) -> List[Dict[str, Any]]:
        """解析文件的import语句"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用AST解析import语句
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            'type': 'import',
                            'module': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append({
                            'type': 'from_import',
                            'module': module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        })
            
            return imports
            
        except Exception as e:
            print(f"❌ 解析文件失败 {file_path}: {e}")
            return []
    
    def check_dependency_exists(self, import_info: Dict[str, Any]) -> bool:
        """检查依赖是否存在"""
        try:
            if import_info['type'] == 'import':
                module_name = import_info['module']
                # 检查是否为标准库模块
                if module_name in ['os', 'sys', 'json', 're', 'datetime', 'time', 'random', 'string', 'typing']:
                    return True
                
                # 检查是否为第三方包
                try:
                    __import__(module_name)
                    return True
                except ImportError:
                    pass
                
                # 检查是否为内部模块
                module_path = self.project_root / f"{module_name.replace('.', '/')}.py"
                if module_path.exists():
                    return True
                
                # 检查是否为包目录
                package_path = self.project_root / f"{module_name.replace('.', '/')}"
                if package_path.exists() and package_path.is_dir():
                    init_file = package_path / "__init__.py"
                    if init_file.exists():
                        return True
                
                return False
                
            elif import_info['type'] == 'from_import':
                module_name = import_info['module']
                item_name = import_info['name']
                
                if not module_name:  # from . import xxx
                    return True
                
                # 检查模块是否存在
                try:
                    module = __import__(module_name, fromlist=[item_name])
                    if hasattr(module, item_name):
                        return True
                except ImportError:
                    pass
                
                # 检查内部模块
                if module_name.startswith('apps.'):
                    # 检查apps目录结构
                    app_parts = module_name.split('.')
                    if len(app_parts) >= 2:
                        app_path = self.project_root / "backend" / "apps" / app_parts[1]
                        if app_path.exists():
                            # 检查具体的文件
                            if len(app_parts) > 2:
                                file_path = app_path / f"{app_parts[2]}.py"
                                if file_path.exists():
                                    return True
                            else:
                                # 检查__init__.py
                                init_file = app_path / "__init__.py"
                                if init_file.exists():
                                    return True
                
                return False
            
            return False
            
        except Exception as e:
            print(f"❌ 检查依赖失败: {e}")
            return False
    
    def categorize_dependency(self, import_info: Dict[str, Any]) -> str:
        """分类依赖类型"""
        module_name = import_info.get('module', '')
        item_name = import_info.get('name', '')
        
        # 服务类
        if item_name and item_name.endswith('Service'):
            return "service_classes"
        
        # 模型类
        if item_name and (item_name.endswith('Model') or item_name.endswith('Config')):
            return "model_classes"
        
        # 工具函数
        if item_name and (item_name.endswith('Helper') or item_name.endswith('Utils')):
            return "utility_functions"
        
        # 外部包
        if module_name and not module_name.startswith('apps.') and not module_name.startswith('.'):
            return "external_packages"
        
        # 内部模块
        return "internal_modules"
    
    def analyze_dependencies(self) -> Dict[str, Any]:
        """分析所有测试文件的依赖"""
        print("🔍 开始分析测试文件依赖...")
        
        # 1. 查找测试文件
        self.test_files = self.find_test_files()
        print(f"📁 找到 {len(self.test_files)} 个测试文件")
        
        # 2. 分析每个文件的依赖
        for file_path in self.test_files:
            print(f"  📄 分析文件: {file_path}")
            imports = self.parse_imports(file_path)
            
            file_dependencies = {
                'file_path': file_path,
                'imports': imports,
                'missing': [],
                'existing': []
            }
            
            for import_info in imports:
                if self.check_dependency_exists(import_info):
                    file_dependencies['existing'].append(import_info)
                else:
                    file_dependencies['missing'].append(import_info)
                    # 分类缺失的依赖
                    category = self.categorize_dependency(import_info)
                    self.missing_dependencies[category].append({
                        'file': file_path,
                        'import_info': import_info
                    })
            
            self.dependency_map[file_path] = file_dependencies
        
        # 3. 生成分析报告
        return self.generate_analysis_report()
    
    def generate_analysis_report(self) -> Dict[str, Any]:
        """生成依赖分析报告"""
        print("📝 生成依赖分析报告...")
        
        # 统计信息
        total_files = len(self.test_files)
        total_imports = sum(len(dep['imports']) for dep in self.dependency_map.values())
        total_missing = sum(len(dep['missing']) for dep in self.dependency_map.values())
        total_existing = sum(len(dep['existing']) for dep in self.dependency_map.values())
        
        # 按类别统计缺失依赖
        missing_by_category = {}
        for category, deps in self.missing_dependencies.items():
            missing_by_category[category] = {
                'count': len(deps),
                'unique_items': list(set(
                    f"{dep['import_info'].get('module', '')}.{dep['import_info'].get('name', '')}"
                    for dep in deps
                ))
            }
        
        report = {
            "summary": {
                "total_test_files": total_files,
                "total_imports": total_imports,
                "existing_dependencies": total_existing,
                "missing_dependencies": total_missing,
                "dependency_success_rate": f"{((total_existing/total_imports)*100):.1f}%" if total_imports > 0 else "0%"
            },
            "missing_dependencies_by_category": missing_by_category,
            "detailed_analysis": self.dependency_map,
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """生成修复建议"""
        recommendations = []
        
        # 服务类缺失建议
        if self.missing_dependencies['service_classes']:
            service_count = len(self.missing_dependencies['service_classes'])
            recommendations.append(f"创建 {service_count} 个缺失的服务类")
        
        # 模型类缺失建议
        if self.missing_dependencies['model_classes']:
            model_count = len(self.missing_dependencies['model_classes'])
            recommendations.append(f"创建 {model_count} 个缺失的模型类")
        
        # 工具函数缺失建议
        if self.missing_dependencies['utility_functions']:
            util_count = len(self.missing_dependencies['utility_functions'])
            recommendations.append(f"创建 {util_count} 个缺失的工具函数")
        
        # 内部模块缺失建议
        if self.missing_dependencies['internal_modules']:
            module_count = len(self.missing_dependencies['internal_modules'])
            recommendations.append(f"检查 {module_count} 个内部模块的导入路径")
        
        if not recommendations:
            recommendations.append("所有依赖都已满足，无需额外操作")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], filename: str = "dependency_analysis_report.json"):
        """保存分析报告"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"📋 依赖分析报告已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")

def main():
    """主函数"""
    print("🚀 启动测试依赖分析工具...")
    
    # 创建分析器实例
    analyzer = TestDependencyAnalyzer()
    
    # 执行依赖分析
    report = analyzer.analyze_dependencies()
    
    # 显示分析结果
    print(f"\n📊 依赖分析结果:")
    print(f"  测试文件总数: {report['summary']['total_test_files']}")
    print(f"  总导入数: {report['summary']['total_imports']}")
    print(f"  现有依赖: {report['summary']['existing_dependencies']}")
    print(f"  缺失依赖: {report['summary']['missing_dependencies']}")
    print(f"  依赖成功率: {report['summary']['dependency_success_rate']}")
    
    print(f"\n🔍 缺失依赖分类:")
    for category, info in report['missing_dependencies_by_category'].items():
        if info['count'] > 0:
            print(f"  {category}: {info['count']} 个")
            print(f"    唯一项目: {', '.join(info['unique_items'][:5])}")
            if len(info['unique_items']) > 5:
                print(f"    ... 还有 {len(info['unique_items']) - 5} 个")
    
    print(f"\n💡 修复建议:")
    for rec in report['recommendations']:
        print(f"  - {rec}")
    
    # 保存报告
    analyzer.save_report(report)

if __name__ == "__main__":
    main()


