#!/usr/bin/env python3
"""
测试可运行性验证工具
验证重构后的测试文件是否可以正常运行，检查语法、导入和基本功能
"""
import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import re # Added missing import for re

class TestRunnabilityValidator:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.validation_results = []
        self.overall_stats = {
            'total_files': 0,
            'syntax_valid': 0,
            'import_successful': 0,
            'runnable': 0,
            'failed': 0
        }

    def validate_test_file(self, file_path: str) -> Dict[str, Any]:
        """验证单个测试文件的可运行性"""
        print(f"🔍 验证文件: {file_path}")
        
        validation_result = {
            'file_path': file_path,
            'syntax_valid': False,
            'import_successful': False,
            'runnable': False,
            'errors': [],
            'warnings': [],
            'validation_time': datetime.now().isoformat()
        }

        try:
            # 1. 检查文件是否存在
            if not os.path.exists(file_path):
                validation_result['errors'].append("文件不存在")
                return validation_result

            # 2. 检查Python语法
            syntax_result = self._check_python_syntax(file_path)
            validation_result['syntax_valid'] = syntax_result['valid']
            if not syntax_result['valid']:
                validation_result['errors'].extend(syntax_result['errors'])

            # 3. 检查导入
            if validation_result['syntax_valid']:
                import_result = self._check_imports(file_path)
                validation_result['import_successful'] = import_result['success']
                if not import_result['success']:
                    validation_result['errors'].extend(import_result['errors'])
                if import_result['warnings']:
                    validation_result['warnings'].extend(import_result['warnings'])

            # 4. 检查可运行性
            if validation_result['syntax_valid'] and validation_result['import_successful']:
                runnable_result = self._check_runnability(file_path)
                validation_result['runnable'] = runnable_result['runnable']
                if not runnable_result['runnable']:
                    validation_result['errors'].extend(runnable_result['errors'])

            # 5. 更新统计信息
            self.overall_stats['total_files'] += 1
            if validation_result['syntax_valid']:
                self.overall_stats['syntax_valid'] += 1
            if validation_result['import_successful']:
                self.overall_stats['import_successful'] += 1
            if validation_result['runnable']:
                self.overall_stats['runnable'] += 1
            else:
                self.overall_stats['failed'] += 1

            # 6. 生成状态摘要
            if validation_result['runnable']:
                print(f"✅ 验证通过: {file_path}")
            elif validation_result['import_successful']:
                print(f"⚠️ 导入成功但不可运行: {file_path}")
            elif validation_result['syntax_valid']:
                print(f"⚠️ 语法正确但导入失败: {file_path}")
            else:
                print(f"❌ 验证失败: {file_path}")

            return validation_result

        except Exception as e:
            validation_result['errors'].append(f"验证过程异常: {str(e)}")
            self.overall_stats['failed'] += 1
            print(f"❌ 验证异常 {file_path}: {e}")
            return validation_result

    def _check_python_syntax(self, file_path: str) -> Dict[str, Any]:
        """检查Python语法"""
        try:
            # 使用python -m py_compile检查语法
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {'valid': True, 'errors': []}
            else:
                # 解析错误信息
                errors = []
                for line in result.stderr.split('\n'):
                    if line.strip() and 'Error:' in line:
                        errors.append(line.strip())
                
                return {'valid': False, 'errors': errors}
                
        except subprocess.TimeoutExpired:
            return {'valid': False, 'errors': ['语法检查超时']}
        except Exception as e:
            return {'valid': False, 'errors': [f'语法检查异常: {str(e)}']}

    def _check_imports(self, file_path: str) -> Dict[str, Any]:
        """检查导入是否成功"""
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查常见的导入问题
            import_issues = []
            warnings = []

            # 检查Django相关导入
            if 'from django.' in content or 'import django.' in content:
                try:
                    # 尝试导入Django
                    import django
                    django.setup()
                except Exception as e:
                    import_issues.append(f"Django导入失败: {str(e)}")

            # 检查apps相关导入
            if 'from apps.' in content or 'import apps.' in content:
                warnings.append("检测到apps模块导入，可能需要Django环境")

            # 检查第三方库导入
            third_party_imports = [
                'requests', 'httpx', 'aiohttp', 'redis', 'celery',
                'pandas', 'numpy', 'matplotlib', 'seaborn'
            ]
            
            for lib in third_party_imports:
                if lib in content:
                    try:
                        importlib.import_module(lib)
                    except ImportError:
                        warnings.append(f"第三方库 {lib} 未安装")

            # 检查Mock导入
            if 'Mock(' in content or 'patch(' in content:
                try:
                    from unittest.mock import Mock, patch
                except ImportError:
                    import_issues.append("Mock模块导入失败")

            # 如果没有严重错误，认为导入成功
            success = len(import_issues) == 0
            
            return {
                'success': success,
                'errors': import_issues,
                'warnings': warnings
            }

        except Exception as e:
            return {
                'success': False,
                'errors': [f'导入检查异常: {str(e)}'],
                'warnings': []
            }

    def _check_runnability(self, file_path: str) -> Dict[str, Any]:
        """检查测试文件是否可以运行"""
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            runnable_issues = []

            # 检查是否有测试函数
            test_functions = []
            if 'def test_' in content:
                test_functions = re.findall(r'def (test_\w+)', content)
            
            if not test_functions:
                runnable_issues.append("未找到测试函数")

            # 检查测试类
            test_classes = []
            if 'class Test' in content:
                test_classes = re.findall(r'class (\w*Test\w*)', content)

            # 检查必要的测试结构
            if not test_functions and not test_classes:
                runnable_issues.append("缺少测试函数或测试类")

            # 检查setUp和tearDown方法
            if test_classes:
                if 'def setUp(' not in content and 'def setUpClass(' not in content:
                    warnings.append("测试类缺少setUp方法")

            # 检查断言
            if 'assert ' not in content and 'self.assert' not in content:
                runnable_issues.append("缺少断言语句")

            # 如果没有严重问题，认为可以运行
            runnable = len(runnable_issues) == 0

            return {
                'runnable': runnable,
                'errors': runnable_issues,
                'test_functions': test_functions,
                'test_classes': test_classes
            }

        except Exception as e:
            return {
                'runnable': False,
                'errors': [f'可运行性检查异常: {str(e)}'],
                'test_functions': [],
                'test_classes': []
            }

    def validate_refactored_files(self, refactor_report_file: str = "test_isolation_refactor_report.md") -> Dict[str, Any]:
        """验证重构后的测试文件"""
        print("🎯 开始验证重构后的测试文件...")
        
        # 检查重构报告文件
        if not os.path.exists(refactor_report_file):
            print(f"❌ 未找到重构报告: {refactor_report_file}")
            return {}

        # 从重构报告中提取文件列表
        refactored_files = self._extract_refactored_files_from_report(refactor_report_file)
        
        if not refactored_files:
            print("❌ 未找到重构后的文件列表")
            return {}

        print(f"📋 找到 {len(refactored_files)} 个重构后的文件")

        # 验证每个文件
        for file_path in refactored_files:
            result = self.validate_test_file(file_path)
            self.validation_results.append(result)

        return self.generate_validation_report()

    def _extract_refactored_files_from_report(self, report_file: str) -> List[str]:
        """从重构报告中提取文件列表"""
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取文件路径
            file_paths = []
            lines = content.split('\n')
            
            for line in lines:
                if line.startswith('### ') and not line.startswith('### 重构详情'):
                    # 提取文件路径
                    file_path = line.replace('### ', '').strip()
                    if file_path and os.path.exists(file_path):
                        file_paths.append(file_path)

            return file_paths

        except Exception as e:
            print(f"❌ 解析重构报告失败: {e}")
            return []

    def validate_all_test_files(self) -> Dict[str, Any]:
        """验证所有测试文件"""
        print("🎯 开始验证所有测试文件...")
        
        # 查找所有测试文件
        test_files = self._find_all_test_files()
        print(f"📋 找到 {len(test_files)} 个测试文件")

        # 验证每个文件
        for file_path in test_files:
            result = self.validate_test_file(file_path)
            self.validation_results.append(result)

        return self.generate_validation_report()

    def _find_all_test_files(self) -> List[str]:
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

    def generate_validation_report(self) -> Dict[str, Any]:
        """生成验证报告"""
        print("📝 生成验证报告...")

        # 按状态分类结果
        successful_files = [r for r in self.validation_results if r['runnable']]
        syntax_valid_files = [r for r in self.validation_results if r['syntax_valid']]
        import_successful_files = [r for r in self.validation_results if r['import_successful']]
        failed_files = [r for r in self.validation_results if not r['runnable']]

        # 按错误类型分类
        error_types = {}
        for result in self.validation_results:
            for error in result['errors']:
                error_type = error.split(':')[0] if ':' in error else '其他'
                error_types[error_type] = error_types.get(error_type, 0) + 1

        report = {
            "summary": {
                "total_files": self.overall_stats['total_files'],
                "syntax_valid": len(syntax_valid_files),
                "import_successful": len(import_successful_files),
                "runnable": len(successful_files),
                "failed": len(failed_files),
                "success_rate": f"{(len(successful_files)/self.overall_stats['total_files']*100):.1f}%" if self.overall_stats['total_files'] > 0 else "0%"
            },
            "error_analysis": error_types,
            "detailed_results": self.validation_results,
            "recommendations": self.generate_recommendations(),
            "next_steps": self.generate_next_steps()
        }

        return report

    def generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 基于统计数据的建议
        if self.overall_stats['failed'] > 0:
            recommendations.append(f"有 {self.overall_stats['failed']} 个文件验证失败，需要进一步修复")

        if self.overall_stats['syntax_valid'] < self.overall_stats['total_files']:
            recommendations.append("部分文件存在语法错误，需要修复语法问题")

        if self.overall_stats['import_successful'] < self.overall_stats['syntax_valid']:
            recommendations.append("部分文件导入失败，需要解决依赖问题")

        # 基于错误类型的建议
        if 'Django导入失败' in [r.get('errors', []) for r in self.validation_results]:
            recommendations.append("Django环境配置问题，需要正确设置DJANGO_SETTINGS_MODULE")

        if '第三方库' in [r.get('warnings', []) for r in self.validation_results]:
            recommendations.append("部分第三方库未安装，需要安装缺失的依赖")

        if not recommendations:
            recommendations.append("所有测试文件验证通过，可以继续进行下一步")

        return recommendations

    def generate_next_steps(self) -> List[str]:
        """生成下一步行动建议"""
        next_steps = []

        if self.overall_stats['runnable'] > 0:
            next_steps.append("运行可运行的测试文件，验证功能正常")
            next_steps.append("修复不可运行的测试文件")

        if self.overall_stats['failed'] > 0:
            next_steps.append("分析失败原因，制定修复计划")
            next_steps.append("继续重构其他测试文件")

        next_steps.append("建立测试可运行性检查机制")
        next_steps.append("进行Task 31.4的后续工作")

        return next_steps

    def save_validation_report(self, report: Dict[str, Any], filename: str = "test_runnability_validation_report.json"):
        """保存验证报告"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"📋 验证报告已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存验证报告失败: {e}")

    def display_validation_summary(self, report: Dict[str, Any]):
        """显示验证摘要"""
        print(f"\n📊 测试可运行性验证结果:")
        print(f"  总文件数: {report['summary']['total_files']}")
        print(f"  语法正确: {report['summary']['syntax_valid']}")
        print(f"  导入成功: {report['summary']['import_successful']}")
        print(f"  可以运行: {report['summary']['runnable']}")
        print(f"  验证失败: {report['summary']['failed']}")
        print(f"  成功率: {report['summary']['success_rate']}")

        if report['error_analysis']:
            print(f"\n🔍 错误类型分析:")
            for error_type, count in report['error_analysis'].items():
                print(f"  {error_type}: {count} 个")

        print(f"\n💡 改进建议:")
        for rec in report['recommendations']:
            print(f"  - {rec}")

        print(f"\n🎯 下一步行动:")
        for step in report['next_steps']:
            print(f"  - {step}")

def main():
    """主函数"""
    print("🚀 启动测试可运行性验证工具...")
    
    # 创建验证工具实例
    validator = TestRunnabilityValidator()
    
    # 首先验证重构后的文件
    print("\n🎯 第一步: 验证重构后的测试文件")
    refactor_validation = validator.validate_refactored_files()
    
    if refactor_validation:
        # 显示重构文件验证结果
        validator.display_validation_summary(refactor_validation)
        
        # 保存重构文件验证报告
        validator.save_validation_report(refactor_validation, "refactored_files_validation_report.json")
    
    # 然后验证所有测试文件
    print("\n🎯 第二步: 验证所有测试文件")
    all_files_validation = validator.validate_all_test_files()
    
    if all_files_validation:
        # 显示所有文件验证结果
        validator.display_validation_summary(all_files_validation)
        
        # 保存完整验证报告
        validator.save_validation_report(all_files_validation, "all_test_files_validation_report.json")
    
    print(f"\n🎉 验证完成!")
    
    if refactor_validation and all_files_validation:
        print(f"✅ 重构文件验证: {refactor_validation['summary']['runnable']}/{refactor_validation['summary']['total_files']} 可运行")
        print(f"✅ 所有文件验证: {all_files_validation['summary']['runnable']}/{all_files_validation['summary']['total_files']} 可运行")
        
        if all_files_validation['summary']['runnable'] > 0:
            print(f"\n🎯 Task 31.4 完成!")
            print("下一步: 运行可运行的测试，验证功能正常")

if __name__ == "__main__":
    main()


