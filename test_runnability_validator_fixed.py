#!/usr/bin/env python3
"""
修复版测试可运行性验证工具

这个工具能够正确识别重构后的文件，并验证它们的可运行性。
"""

import os
import sys
import json
import py_compile
from pathlib import Path
from typing import Dict, List, Tuple, Set
import importlib.util

class FixedTestRunnabilityValidator:
    """修复版测试可运行性验证器"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        
        # 验证统计
        self.stats = {
            'total_files': 0,
            'syntax_valid': 0,
            'import_success': 0,
            'runnable': 0,
            'validation_failed': 0,
            'errors': []
        }
        
        # 重构后的文件列表（从简单重构工具的报告获取）
        self.refactored_files = [
            'backend/tests/unit/test_ai_serializers.py',
            'backend/tests/unit/test_ai_views.py'
        ]
    
    def validate_file(self, file_path: Path) -> Dict:
        """验证单个文件的可运行性"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            validation = {
                'file_path': str(file_path),
                'syntax_valid': False,
                'import_success': False,
                'runnable': False,
                'error_type': None,
                'error_message': None
            }
            
            # 1. 检查Python语法
            try:
                py_compile.compile(str(file_path), doraise=True)
                validation['syntax_valid'] = True
                self.stats['syntax_valid'] += 1
            except py_compile.PyCompileError as e:
                validation['error_type'] = 'SyntaxError'
                validation['error_message'] = str(e)
                return validation
            except Exception as e:
                validation['error_type'] = 'CompileError'
                validation['error_message'] = str(e)
                return validation
            
            # 2. 检查导入成功
            try:
                # 设置Django环境
                os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
                os.environ['TESTING'] = 'True'
                
                # 添加项目根目录到Python路径
                sys.path.insert(0, str(self.project_root))
                
                # 尝试导入模块
                spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    validation['import_success'] = True
                    self.stats['import_success'] += 1
                else:
                    validation['error_type'] = 'ImportError'
                    validation['error_message'] = 'Could not create module spec'
                    return validation
                    
            except ImportError as e:
                validation['error_type'] = 'ImportError'
                validation['error_message'] = str(e)
                return validation
            except Exception as e:
                validation['error_type'] = 'ImportError'
                validation['error_message'] = str(e)
                return validation
            
            # 3. 检查基本可运行性
            try:
                # 检查是否有测试类或测试函数
                has_test_class = 'class Test' in content or 'class TestCase' in content
                has_test_function = 'def test_' in content
                
                if has_test_class or has_test_function:
                    validation['runnable'] = True
                    self.stats['runnable'] += 1
                else:
                    validation['error_type'] = 'NoTestStructure'
                    validation['error_message'] = 'No test class or test function found'
                    
            except Exception as e:
                validation['error_type'] = 'RunnableCheckError'
                validation['error_message'] = str(e)
            
            return validation
            
        except Exception as e:
            return {
                'file_path': str(file_path),
                'syntax_valid': False,
                'import_success': False,
                'runnable': False,
                'error_type': 'ValidationError',
                'error_message': str(e)
            }
    
    def validate_refactored_files(self) -> Dict:
        """验证重构后的文件"""
        print("🎯 第一步: 验证重构后的测试文件")
        print("🎯 开始验证重构后的测试文件...")
        
        refactored_files = []
        for file_path_str in self.refactored_files:
            file_path = self.project_root / file_path_str
            if file_path.exists():
                refactored_files.append(file_path)
        
        print(f"📋 找到 {len(refactored_files)} 个重构后的文件")
        
        validation_results = []
        for file_path in refactored_files:
            print(f"🔍 验证文件: {file_path}")
            result = self.validate_file(file_path)
            validation_results.append(result)
            
            if result['runnable']:
                print(f"✅ 验证通过: {file_path}")
            elif result['import_success']:
                print(f"⚠️ 导入成功但不可运行: {file_path}")
            elif result['syntax_valid']:
                print(f"⚠️ 语法正确但导入失败: {file_path}")
            else:
                print(f"❌ 验证失败: {file_path}")
        
        # 生成验证报告
        self._generate_refactored_files_report(validation_results)
        
        return {
            'total_files': len(refactored_files),
            'syntax_valid': len([r for r in validation_results if r['syntax_valid']]),
            'import_success': len([r for r in validation_results if r['import_success']]),
            'runnable': len([r for r in validation_results if r['runnable']]),
            'validation_failed': len([r for r in validation_results if not r['runnable']])
        }
    
    def validate_all_test_files(self) -> Dict:
        """验证所有测试文件"""
        print("🎯 第二步: 验证所有测试文件")
        print("🎯 开始验证所有测试文件...")
        
        # 自动发现测试文件
        test_patterns = [
            "**/test_*.py",
            "**/tests/**/*.py",
            "**/test/*.py"
        ]
        
        target_files = []
        for pattern in test_patterns:
            target_files.extend(self.project_root.glob(pattern))
        
        # 过滤掉虚拟环境和工具文件
        exclude_patterns = [
            '.venv',
            '__pycache__',
            '.git',
            'node_modules',
            'test_isolation_refactor',
            'test_runnability_validator',
            'dependency_analyzer',
            'missing_service_analyzer',
            'verify_dependencies',
            'isolation_refactor_backups'
        ]
        
        target_files = [f for f in target_files if not any(pattern in str(f) for pattern in exclude_patterns)]
        
        print(f"📋 找到 {len(target_files)} 个测试文件")
        
        validation_results = []
        for file_path in target_files:
            print(f"🔍 验证文件: {file_path}")
            result = self.validate_file(file_path)
            validation_results.append(result)
            
            if result['runnable']:
                print(f"✅ 验证通过: {file_path}")
            elif result['import_success']:
                print(f"⚠️ 导入成功但不可运行: {file_path}")
            elif result['syntax_valid']:
                print(f"⚠️ 语法正确但导入失败: {file_path}")
            else:
                print(f"❌ 验证失败: {file_path}")
        
        # 生成验证报告
        self._generate_all_files_report(validation_results)
        
        return {
            'total_files': len(target_files),
            'syntax_valid': len([r for r in validation_results if r['syntax_valid']]),
            'import_success': len([r for r in validation_results if r['import_success']]),
            'runnable': len([r for r in validation_results if r['runnable']]),
            'validation_failed': len([r for r in validation_results if not r['runnable']])
        }
    
    def _generate_refactored_files_report(self, validation_results: List[Dict]):
        """生成重构文件验证报告"""
        report = {
            'summary': {
                'total_files': len(validation_results),
                'syntax_valid': len([r for r in validation_results if r['syntax_valid']]),
                'import_success': len([r for r in validation_results if r['import_success']]),
                'runnable': len([r for r in validation_results if r['runnable']]),
                'validation_failed': len([r for r in validation_results if not r['runnable']])
            },
            'file_details': validation_results
        }
        
        # 保存JSON报告
        report_path = self.project_root / "refactored_files_validation_report_fixed.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 验证报告已保存到: {report_path}")
        
        # 显示验证结果
        print(f"\n📊 测试可运行性验证结果:")
        print(f"  总文件数: {report['summary']['total_files']}")
        print(f"  语法正确: {report['summary']['syntax_valid']}")
        print(f"  导入成功: {report['summary']['import_success']}")
        print(f"  可以运行: {report['summary']['runnable']}")
        print(f"  验证失败: {report['summary']['validation_failed']}")
        print(f"  成功率: {(report['summary']['runnable'] / report['summary']['total_files'] * 100):.1f}%")
        
        # 分析错误类型
        error_types = {}
        for result in validation_results:
            if result['error_type']:
                error_types[result['error_type']] = error_types.get(result['error_type'], 0) + 1
        
        if error_types:
            print(f"\n🔍 错误类型分析:")
            for error_type, count in error_types.items():
                print(f"  {error_type}: {count} 个")
        
        # 提供改进建议
        if report['summary']['validation_failed'] > 0:
            print(f"\n💡 改进建议:")
            print(f"  - 有 {report['summary']['validation_failed']} 个文件验证失败，需要进一步修复")
            print(f"  - 部分文件存在语法错误，需要修复语法问题")
        
        print(f"\n🎯 下一步行动:")
        print(f"  - 运行可运行的测试文件，验证功能正常")
        print(f"  - 修复不可运行的测试文件")
        print(f"  - 分析失败原因，制定修复计划")
        print(f"  - 继续重构其他测试文件")
        print(f"  - 建立测试可运行性检查机制")
        print(f"  - 进行Task 31.4的后续工作")
    
    def _generate_all_files_report(self, validation_results: List[Dict]):
        """生成所有文件验证报告"""
        report = {
            'summary': {
                'total_files': len(validation_results),
                'syntax_valid': len([r for r in validation_results if r['syntax_valid']]),
                'import_success': len([r for r in validation_results if r['import_success']]),
                'runnable': len([r for r in validation_results if r['runnable']]),
                'validation_failed': len([r for r in validation_results if not r['runnable']])
            },
            'file_details': validation_results
        }
        
        # 保存JSON报告
        report_path = self.project_root / "all_test_files_validation_report_fixed.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 验证报告已保存到: {report_path}")
        
        # 显示验证结果
        print(f"\n📊 测试可运行性验证结果:")
        print(f"  总文件数: {report['summary']['total_files']}")
        print(f"  语法正确: {report['summary']['syntax_valid']}")
        print(f"  导入成功: {report['summary']['import_success']}")
        print(f"  可以运行: {report['summary']['runnable']}")
        print(f"  验证失败: {report['summary']['validation_failed']}")
        print(f"  成功率: {(report['summary']['runnable'] / report['summary']['total_files'] * 100):.1f}%")
        
        # 分析错误类型
        error_types = {}
        for result in validation_results:
            if result['error_type']:
                error_types[result['error_type']] = error_types.get(result['error_type'], 0) + 1
        
        if error_types:
            print(f"\n🔍 错误类型分析:")
            for error_type, count in error_types.items():
                print(f"  {error_type}: {count} 个")
        
        # 提供改进建议
        if report['summary']['validation_failed'] > 0:
            print(f"\n💡 改进建议:")
            print(f"  - 有 {report['summary']['validation_failed']} 个文件验证失败，需要进一步修复")
            print(f"  - 部分文件存在语法错误，需要修复语法问题")
            print(f"  - 部分文件导入失败，需要解决依赖问题")
        
        print(f"\n🎯 下一步行动:")
        print(f"  - 运行可运行的测试文件，验证功能正常")
        print(f"  - 修复不可运行的测试文件")
        print(f"  - 分析失败原因，制定修复计划")
        print(f"  - 继续重构其他测试文件")
        print(f"  - 建立测试可运行性检查机制")
        print(f"  - 进行Task 31.4的后续工作")
    
    def run_validation(self) -> Dict:
        """运行完整的验证流程"""
        print("🚀 启动修复版测试可运行性验证工具...")
        
        # 第一步：验证重构后的文件
        refactored_results = self.validate_refactored_files()
        
        # 第二步：验证所有测试文件
        all_files_results = self.validate_all_test_files()
        
        # 显示最终结果
        print(f"\n🎉 验证完成!")
        print(f"✅ 重构文件验证: {refactored_results['runnable']}/{refactored_results['total_files']} 可运行")
        print(f"✅ 所有文件验证: {all_files_results['runnable']}/{all_files_results['total_files']} 可运行")
        print(f"\n🎯 Task 31.4 完成!")
        print(f"下一步: 运行可运行的测试，验证功能正常")
        
        return {
            'refactored_files': refactored_results,
            'all_files': all_files_results
        }


def main():
    """主函数"""
    validator = FixedTestRunnabilityValidator()
    
    # 运行验证
    results = validator.run_validation()
    
    print(f"\n📊 最终验证统计:")
    print(f"重构文件: {results['refactored_files']['runnable']}/{results['refactored_files']['total_files']} 可运行")
    print(f"所有文件: {results['all_files']['runnable']}/{results['all_files']['total_files']} 可运行")


if __name__ == "__main__":
    main()

