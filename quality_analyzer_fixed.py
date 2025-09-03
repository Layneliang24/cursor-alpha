#!/usr/bin/env python3
"""
修复版测试文件质量评估脚本
使用pylint、coverage、radon等工具评估Python测试文件质量
"""

import os
import json
import subprocess
import ast
from pathlib import Path
from collections import defaultdict

class FixedQualityAnalyzer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.quality_scores = {}
        self.issues = defaultdict(list)
        
    def check_tools_availability(self):
        """检查质量评估工具的可用性"""
        print("🔍 检查质量评估工具...")
        
        tools = {
            'pylint': r'C:\Users\layne.liang\AppData\Roaming\Python\Python313\Scripts\pylint.exe --version',
            'coverage': 'python -m coverage --version',
            'radon': 'python -m radon --version'
        }
        
        available_tools = {}
        for tool_name, command in tools.items():
            try:
                result = subprocess.run(command.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    available_tools[tool_name] = True
                    print(f"✅ {tool_name}: 可用")
                else:
                    available_tools[tool_name] = False
                    print(f"❌ {tool_name}: 不可用")
            except FileNotFoundError:
                available_tools[tool_name] = False
                print(f"❌ {tool_name}: 未安装")
                
        return available_tools
    
    def run_pylint_analysis(self, file_path):
        """运行pylint分析"""
        try:
            result = subprocess.run([
                r'C:\Users\layne.liang\AppData\Roaming\Python\Python313\Scripts\pylint.exe',
                '--output-format=json', '--disable=C0114,C0115,C0116', 
                str(file_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return {'score': 10.0, 'issues': []}
            else:
                try:
                    pylint_output = json.loads(result.stdout)
                    score = pylint_output.get('score', 0.0)
                    issues = [msg['message'] for msg in pylint_output.get('messages', [])]
                    return {'score': score, 'issues': issues}
                except json.JSONDecodeError:
                    return {'score': 0.0, 'issues': ['pylint输出解析失败']}
        except Exception as e:
            return {'score': 0.0, 'issues': [f'pylint执行失败: {e}']}
    
    def run_coverage_analysis(self, file_path):
        """运行coverage分析"""
        try:
            # 使用python -m coverage方式
            result = subprocess.run([
                'python', '-m', 'coverage', 'run', '--source', str(file_path.parent), str(file_path)
            ], capture_output=True, text=True)
            
            # 获取覆盖率报告
            report_result = subprocess.run([
                'python', '-m', 'coverage', 'report', '--format=json'
            ], capture_output=True, text=True)
            
            if report_result.returncode == 0:
                try:
                    coverage_data = json.loads(report_result.stdout)
                    return coverage_data
                except json.JSONDecodeError:
                    return {'coverage': 0.0}
            else:
                return {'coverage': 0.0}
        except Exception as e:
            return {'coverage': 0.0, 'error': str(e)}
    
    def analyze_file_quality(self, file_path, available_tools):
        """分析单个文件的质量"""
        print(f"🔍 分析文件: {file_path}")
        
        file_quality = {
            'file_path': str(file_path),
            'complexity': self.analyze_code_complexity(file_path),
            'test_coverage': self.analyze_test_coverage_static(file_path),
            'coding_standards': self.analyze_coding_standards(file_path),
            'pylint_score': 0.0,
            'coverage_data': {}
        }
        
        # 运行pylint分析
        if available_tools.get('pylint'):
            pylint_result = self.run_pylint_analysis(file_path)
            file_quality['pylint_score'] = pylint_result['score']
            if pylint_result['issues']:
                self.issues[str(file_path)].extend(pylint_result['issues'])
        
        # 运行coverage分析
        if available_tools.get('coverage'):
            coverage_result = self.run_coverage_analysis(file_path)
            file_quality['coverage_data'] = coverage_result
        
        # 计算综合质量评分
        quality_score = self._calculate_quality_score(file_quality)
        file_quality['quality_score'] = quality_score
        
        return file_quality
    
    def analyze_code_complexity(self, file_path):
        """分析代码复杂度（圈复杂度）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            complexity = 1  # 基础复杂度
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1
                elif isinstance(node, ast.ExceptHandler):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
                    
            return complexity
        except Exception as e:
            print(f"❌ 分析复杂度失败 {file_path}: {e}")
            return 1
    
    def analyze_test_coverage_static(self, file_path):
        """静态分析测试覆盖率"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            test_functions = 0
            total_functions = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_functions += 1
                    if node.name.startswith('test_'):
                        test_functions += 1
                        
            coverage = (test_functions / total_functions * 100) if total_functions > 0 else 0
            return {
                'test_functions': test_functions,
                'total_functions': total_functions,
                'coverage_percentage': coverage
            }
        except Exception as e:
            return {'test_functions': 0, 'total_functions': 0, 'coverage_percentage': 0}
    
    def analyze_coding_standards(self, file_path):
        """分析编码规范遵守情况"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            issues = []
            lines = content.split('\n')
            
            # 检查行长度
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 120]
            if long_lines:
                issues.append(f"超长行: {len(long_lines)}行")
                
            # 检查空行使用
            consecutive_empty = 0
            for line in lines:
                if line.strip() == '':
                    consecutive_empty += 1
                else:
                    consecutive_empty = 0
                if consecutive_empty > 2:
                    issues.append("连续空行过多")
                    break
                    
            return issues
        except Exception as e:
            return ["分析失败"]
    
    def _calculate_quality_score(self, file_quality):
        """计算综合质量评分"""
        score = 100
        
        # 复杂度扣分
        complexity = file_quality['complexity']
        if complexity > 10:
            score -= (complexity - 10) * 2
        elif complexity > 5:
            score -= (complexity - 5)
            
        # 测试覆盖率扣分
        coverage = file_quality['test_coverage']['coverage_percentage']
        if coverage < 80:
            score -= (80 - coverage) * 0.5
            
        # pylint评分影响
        pylint_score = file_quality['pylint_score']
        if pylint_score < 8.0:
            score -= (8.0 - pylint_score) * 2
            
        # 编码规范问题扣分
        standards_issues = len(file_quality['coding_standards'])
        score -= standards_issues * 2
        
        return max(0, score)
    
    def analyze_all_test_files(self):
        """分析所有测试文件"""
        print("🚀 开始修复版质量分析...")
        
        # 检查工具可用性
        available_tools = self.check_tools_availability()
        
        # 加载测试结构报告
        try:
            with open('test_structure_report.json', 'r', encoding='utf-8') as f:
                test_report = json.load(f)
        except FileNotFoundError:
            print("❌ 找不到test_structure_report.json")
            return
        
        # 收集Python测试文件
        python_test_files = []
        for dir_name, files in test_report['directory_structure'].items():
            for file_info in files:
                if file_info['type'] == 'python':
                    file_path = Path(file_info['file'])
                    if file_path.exists():
                        python_test_files.append(file_path)
        
        print(f"📁 找到 {len(python_test_files)} 个Python测试文件")
        
        # 分析每个文件
        for file_path in python_test_files:
            try:
                file_quality = self.analyze_file_quality(file_path, available_tools)
                self.quality_scores[str(file_path)] = file_quality
            except Exception as e:
                print(f"❌ 分析文件失败 {file_path}: {e}")
        
        # 生成质量报告
        self._generate_quality_report(available_tools)
        
        print("✅ 修复版质量分析完成！")
    
    def _generate_quality_report(self, available_tools):
        """生成质量分析报告"""
        print("📊 生成质量分析报告...")
        
        total_files = len(self.quality_scores)
        if total_files == 0:
            print("❌ 没有可分析的文件")
            return
            
        avg_quality_score = sum(f['quality_score'] for f in self.quality_scores.values()) / total_files
        avg_complexity = sum(f['complexity'] for f in self.quality_scores.values()) / total_files
        avg_coverage = sum(f['test_coverage']['coverage_percentage'] for f in self.quality_scores.values()) / total_files
        
        # 质量分布
        quality_distribution = {
            'excellent': len([f for f in self.quality_scores.values() if f['quality_score'] >= 90]),
            'good': len([f for f in self.quality_scores.values() if 80 <= f['quality_score'] < 90]),
            'fair': len([f for f in self.quality_scores.values() if 70 <= f['quality_score'] < 80]),
            'poor': len([f for f in self.quality_scores.values() if f['quality_score'] < 70])
        }
        
        # 生成报告
        report = {
            'summary': {
                'total_files': total_files,
                'average_quality_score': round(avg_quality_score, 2),
                'average_complexity': round(avg_complexity, 2),
                'average_test_coverage': round(avg_coverage, 2),
                'available_tools': available_tools
            },
            'quality_distribution': quality_distribution,
            'file_quality_details': self.quality_scores,
            'issues_summary': dict(self.issues)
        }
        
        # 保存报告
        with open('fixed_quality_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print("✅ 修复版质量分析报告已生成: fixed_quality_analysis_report.json")
        
        # 打印摘要
        print(f"\n📈 修复版质量分析摘要:")
        print(f"   - 分析文件数: {total_files}")
        print(f"   - 平均质量评分: {avg_quality_score:.2f}/100")
        print(f"   - 平均复杂度: {avg_complexity:.2f}")
        print(f"   - 平均测试覆盖率: {avg_coverage:.2f}%")
        print(f"   - 优秀文件: {quality_distribution['excellent']}")
        print(f"   - 良好文件: {quality_distribution['good']}")
        print(f"   - 一般文件: {quality_distribution['fair']}")
        print(f"   - 较差文件: {quality_distribution['poor']}")

def main():
    """主函数"""
    analyzer = FixedQualityAnalyzer()
    analyzer.analyze_all_test_files()

if __name__ == "__main__":
    main()

