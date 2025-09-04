#!/usr/bin/env python3
"""
测试隔离性分析工具
分析测试文件的隔离性状况，识别需要重构的测试文件
"""
import os
import re
import json
import ast
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict

class TestIsolationAnalyzer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.test_files = []
        self.isolation_issues = defaultdict(list)
        self.isolation_categories = {
            "database_dependencies": [],
            "external_service_dependencies": [],
            "file_system_dependencies": [],
            "network_dependencies": [],
            "global_state_dependencies": [],
            "hardcoded_values": [],
            "missing_mocks": []
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

    def analyze_test_isolation(self, file_path: str) -> Dict[str, Any]:
        """分析单个测试文件的隔离性"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 使用AST解析文件
            tree = ast.parse(content)
            
            isolation_analysis = {
                'file_path': file_path,
                'total_lines': len(content.split('\n')),
                'test_functions': 0,
                'issues_found': 0,
                'isolation_score': 100,  # 满分100分
                'issues': []
            }

            # 分析测试函数数量
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    isolation_analysis['test_functions'] += 1

            # 检查各种隔离性问题
            issues = []

            # 1. 检查数据库依赖
            db_issues = self._check_database_dependencies(content, file_path)
            issues.extend(db_issues)

            # 2. 检查外部服务依赖
            service_issues = self._check_external_service_dependencies(content, file_path)
            issues.extend(service_issues)

            # 3. 检查文件系统依赖
            fs_issues = self._check_filesystem_dependencies(content, file_path)
            issues.extend(fs_issues)

            # 4. 检查网络依赖
            network_issues = self._check_network_dependencies(content, file_path)
            issues.extend(network_issues)

            # 5. 检查全局状态依赖
            global_issues = self._check_global_state_dependencies(content, file_path)
            issues.extend(global_issues)

            # 6. 检查硬编码值
            hardcoded_issues = self._check_hardcoded_values(content, file_path)
            issues.extend(hardcoded_issues)

            # 7. 检查缺失的Mock
            mock_issues = self._check_missing_mocks(content, file_path)
            issues.extend(mock_issues)

            # 计算隔离性分数
            isolation_analysis['issues'] = issues
            isolation_analysis['issues_found'] = len(issues)
            
            # 根据问题数量扣分
            if issues:
                deduction = min(80, len(issues) * 10)  # 最多扣80分
                isolation_analysis['isolation_score'] = max(20, 100 - deduction)

            return isolation_analysis

        except Exception as e:
            print(f"❌ 分析文件失败 {file_path}: {e}")
            return {
                'file_path': file_path,
                'error': str(e),
                'isolation_score': 0
            }

    def _check_database_dependencies(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查数据库依赖问题"""
        issues = []
        
        # 检查直接数据库操作
        db_patterns = [
            r'\.objects\.create\(',
            r'\.objects\.get\(',
            r'\.objects\.filter\(',
            r'\.objects\.all\(',
            r'\.save\(',
            r'\.delete\(',
            r'@transaction\.atomic',
            r'from django\.db import transaction'
        ]

        for pattern in db_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'type': 'database_dependency',
                    'severity': 'high',
                    'line': line_num,
                    'description': f'直接数据库操作: {match.group()}',
                    'recommendation': '使用Mock或测试数据库'
                })

        return issues

    def _check_external_service_dependencies(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查外部服务依赖问题"""
        issues = []
        
        # 检查外部服务调用
        service_patterns = [
            r'requests\.get\(',
            r'requests\.post\(',
            r'urllib\.request',
            r'httpx\.',
            r'aiohttp\.',
            r'redis\.',
            r'celery\.',
            r'from apps\.ai\.adapters',
            r'from apps\.english\.services'
        ]

        for pattern in service_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'type': 'external_service_dependency',
                    'severity': 'high',
                    'line': line_num,
                    'description': f'外部服务依赖: {match.group()}',
                    'recommendation': '使用Mock替代真实服务'
                })

        return issues

    def _check_filesystem_dependencies(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查文件系统依赖问题"""
        issues = []
        
        # 检查文件操作
        fs_patterns = [
            r'open\(',
            r'os\.path\.',
            r'pathlib\.',
            r'with open\(',
            r'\.read\(',
            r'\.write\(',
            r'\.mkdir\(',
            r'\.remove\('
        ]

        for pattern in fs_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'type': 'filesystem_dependency',
                    'severity': 'medium',
                    'line': line_num,
                    'description': f'文件系统操作: {match.group()}',
                    'recommendation': '使用临时文件或Mock文件系统'
                })

        return issues

    def _check_network_dependencies(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查网络依赖问题"""
        issues = []
        
        # 检查网络相关操作
        network_patterns = [
            r'socket\.',
            r'http\.',
            r'https://',
            r'ws://',
            r'wss://',
            r'ftp://',
            r'smtp\.',
            r'pop3\.'
        ]

        for pattern in network_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'type': 'network_dependency',
                    'severity': 'high',
                    'line': line_num,
                    'description': f'网络依赖: {match.group()}',
                    'recommendation': '使用Mock网络响应'
                })

        return issues

    def _check_global_state_dependencies(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查全局状态依赖问题"""
        issues = []
        
        # 检查全局状态操作
        global_patterns = [
            r'global\s+\w+',
            r'os\.environ\[',
            r'os\.environ\.setdefault\(',
            r'os\.environ\.update\(',
            r'settings\.',
            r'config\.',
            r'@patch\(',
            r'@mock\.patch\('
        ]

        for pattern in global_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'type': 'global_state_dependency',
                    'severity': 'medium',
                    'line': line_num,
                    'description': f'全局状态操作: {match.group()}',
                    'recommendation': '使用测试环境配置或Mock'
                })

        return issues

    def _check_hardcoded_values(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查硬编码值问题"""
        issues = []
        
        # 检查硬编码值
        hardcoded_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'localhost:\d+',
            r'127\.0\.0\.1:\d+',
            r'http://[^\s]+',
            r'https://[^\s]+'
        ]

        for pattern in hardcoded_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                issues.append({
                    'type': 'hardcoded_value',
                    'severity': 'low',
                    'line': line_num,
                    'description': f'硬编码值: {match.group()}',
                    'recommendation': '使用环境变量或配置文件'
                })

        return issues

    def _check_missing_mocks(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """检查缺失的Mock"""
        issues = []
        
        # 检查是否使用了Mock
        mock_imports = re.findall(r'from unittest\.mock import|from unittest\.mock import|import mock|from mock import', content)
        
        if not mock_imports:
            # 检查是否有外部依赖但没有Mock
            external_deps = re.findall(r'from apps\.|import apps\.|from django\.|import django\.', content)
            if external_deps:
                issues.append({
                    'type': 'missing_mocks',
                    'severity': 'medium',
                    'line': 1,
                    'description': '缺少Mock导入，可能存在外部依赖',
                    'recommendation': '添加Mock导入并Mock外部依赖'
                })

        return issues

    def analyze_all_tests(self) -> Dict[str, Any]:
        """分析所有测试文件的隔离性"""
        print("🔍 开始分析测试文件隔离性...")

        # 1. 查找测试文件
        self.test_files = self.find_test_files()
        print(f"📁 找到 {len(self.test_files)} 个测试文件")

        # 2. 分析每个文件的隔离性
        all_analyses = []
        total_issues = 0
        total_score = 0

        for file_path in self.test_files:
            print(f"  📄 分析文件: {file_path}")
            analysis = self.analyze_test_isolation(file_path)
            all_analyses.append(analysis)
            
            if 'error' not in analysis:
                total_issues += analysis['issues_found']
                total_score += analysis['isolation_score']

        # 3. 生成分析报告
        return self.generate_isolation_report(all_analyses, total_issues, total_score)

    def generate_isolation_report(self, analyses: List[Dict[str, Any]], total_issues: int, total_score: int) -> Dict[str, Any]:
        """生成隔离性分析报告"""
        print("📝 生成隔离性分析报告...")

        # 统计信息
        total_files = len(analyses)
        valid_files = len([a for a in analyses if 'error' not in a])
        average_score = total_score / valid_files if valid_files > 0 else 0

        # 按问题类型分类
        issues_by_type = defaultdict(list)
        for analysis in analyses:
            if 'issues' in analysis:
                for issue in analysis['issues']:
                    issues_by_type[issue['type']].append(issue)

        # 按严重程度分类
        issues_by_severity = defaultdict(list)
        for analysis in analyses:
            if 'issues' in analysis:
                for issue in analysis['issues']:
                    issues_by_severity[issue['severity']].append(issue)

        # 生成建议
        recommendations = self.generate_isolation_recommendations(issues_by_type, issues_by_severity)

        report = {
            "summary": {
                "total_test_files": total_files,
                "valid_files": valid_files,
                "total_issues": total_issues,
                "average_isolation_score": round(average_score, 1),
                "overall_grade": self._calculate_grade(average_score)
            },
            "issues_by_type": {k: len(v) for k, v in issues_by_type.items()},
            "issues_by_severity": {k: len(v) for k, v in issues_by_severity.items()},
            "detailed_analyses": analyses,
            "recommendations": recommendations,
            "refactoring_priority": self.calculate_refactoring_priority(analyses)
        }

        return report

    def _calculate_grade(self, score: float) -> str:
        """根据分数计算等级"""
        if score >= 90:
            return "A (优秀)"
        elif score >= 80:
            return "B (良好)"
        elif score >= 70:
            return "C (一般)"
        elif score >= 60:
            return "D (较差)"
        else:
            return "F (很差)"

    def calculate_refactoring_priority(self, analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """计算重构优先级"""
        priority_list = []

        for analysis in analyses:
            if 'error' in analysis:
                continue

            # 计算优先级分数
            priority_score = 0
            
            # 根据隔离性分数
            if analysis['isolation_score'] < 60:
                priority_score += 30
            elif analysis['isolation_score'] < 80:
                priority_score += 20
            elif analysis['isolation_score'] < 90:
                priority_score += 10

            # 根据问题数量
            if analysis['issues_found'] > 10:
                priority_score += 25
            elif analysis['issues_found'] > 5:
                priority_score += 15
            elif analysis['issues_found'] > 0:
                priority_score += 5

            # 根据问题严重程度
            high_severity = len([i for i in analysis.get('issues', []) if i['severity'] == 'high'])
            priority_score += high_severity * 10

            priority_list.append({
                'file_path': analysis['file_path'],
                'priority_score': priority_score,
                'isolation_score': analysis['isolation_score'],
                'issues_count': analysis['issues_found'],
                'high_severity_issues': high_severity,
                'refactoring_effort': self._estimate_refactoring_effort(analysis)
            })

        # 按优先级排序
        priority_list.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priority_list

    def _estimate_refactoring_effort(self, analysis: Dict[str, Any]) -> str:
        """估算重构工作量"""
        issues_count = analysis['issues_found']
        high_severity = len([i for i in analysis.get('issues', []) if i['severity'] == 'high'])
        
        if high_severity > 5 or issues_count > 15:
            return "高 (4-6小时)"
        elif high_severity > 2 or issues_count > 8:
            return "中 (2-4小时)"
        elif issues_count > 0:
            return "低 (1-2小时)"
        else:
            return "无 (0小时)"

    def generate_isolation_recommendations(self, issues_by_type: Dict, issues_by_severity: Dict) -> List[str]:
        """生成隔离性改进建议"""
        recommendations = []

        # 基于问题类型的建议
        if issues_by_type.get('database_dependency'):
            count = len(issues_by_type['database_dependency'])
            recommendations.append(f"数据库依赖问题: {count}个 - 建议使用测试数据库或Mock ORM操作")

        if issues_by_type.get('external_service_dependency'):
            count = len(issues_by_type['external_service_dependency'])
            recommendations.append(f"外部服务依赖: {count}个 - 建议使用Mock替代真实服务调用")

        if issues_by_type.get('filesystem_dependency'):
            count = len(issues_by_type['filesystem_dependency'])
            recommendations.append(f"文件系统依赖: {count}个 - 建议使用临时文件或Mock文件系统")

        if issues_by_type.get('network_dependency'):
            count = len(issues_by_type['network_dependency'])
            recommendations.append(f"网络依赖: {count}个 - 建议使用Mock网络响应")

        # 基于严重程度的建议
        if issues_by_severity.get('high'):
            count = len(issues_by_severity['high'])
            recommendations.append(f"高严重性问题: {count}个 - 优先处理，可能影响测试稳定性")

        if issues_by_severity.get('medium'):
            count = len(issues_by_severity['medium'])
            recommendations.append(f"中严重性问题: {count}个 - 建议在下一轮重构中处理")

        # 通用建议
        if recommendations:
            recommendations.append("建议按优先级逐步重构，先解决高严重性问题")
            recommendations.append("使用Mock、Stub和测试数据工厂提高测试隔离性")
            recommendations.append("建立测试环境配置，避免硬编码和外部依赖")

        return recommendations

    def save_report(self, report: Dict[str, Any], filename: str = "test_isolation_analysis_report.json"):
        """保存分析报告"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"📋 隔离性分析报告已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存报告失败: {e}")

def main():
    """主函数"""
    print("🚀 启动测试隔离性分析工具...")

    # 创建分析器实例
    analyzer = TestIsolationAnalyzer()

    # 执行隔离性分析
    report = analyzer.analyze_all_tests()

    # 显示分析结果
    print(f"\n📊 隔离性分析结果:")
    print(f"  测试文件总数: {report['summary']['total_test_files']}")
    print(f"  有效文件数: {report['summary']['valid_files']}")
    print(f"  总问题数: {report['summary']['total_issues']}")
    print(f"  平均隔离性分数: {report['summary']['average_isolation_score']}")
    print(f"  整体等级: {report['summary']['overall_grade']}")

    print(f"\n🔍 问题类型分布:")
    for issue_type, count in report['issues_by_type'].items():
        if count > 0:
            print(f"  {issue_type}: {count} 个")

    print(f"\n⚠️ 问题严重程度分布:")
    for severity, count in report['issues_by_severity'].items():
        if count > 0:
            print(f"  {severity}: {count} 个")

    print(f"\n🎯 重构优先级 (前5名):")
    for i, item in enumerate(report['refactoring_priority'][:5], 1):
        print(f"  {i}. {item['file_path']}")
        print(f"     优先级分数: {item['priority_score']}")
        print(f"     隔离性分数: {item['isolation_score']}")
        print(f"     问题数量: {item['issues_count']}")
        print(f"     重构工作量: {item['refactoring_effort']}")

    print(f"\n💡 改进建议:")
    for rec in report['recommendations']:
        print(f"  - {rec}")

    # 保存报告
    analyzer.save_report(report)

if __name__ == "__main__":
    main()


