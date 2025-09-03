#!/usr/bin/env python3
"""
框架混用深度分析脚本
深入分析19个框架混用文件，识别具体混用模式和修复复杂度
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

class FrameworkMixingAnalyzer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.mixing_patterns = defaultdict(list)
        self.complexity_scores = {}
        self.risk_assessments = {}
        
    def load_issue_report(self):
        """加载问题分类报告"""
        print("📊 加载框架混用问题报告...")
        
        try:
            with open('issue_classification_report.json', 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            framework_issues = report['issues_by_category']['框架混用']
            print(f"✅ 加载了 {len(framework_issues)} 个框架混用问题")
            return framework_issues
            
        except Exception as e:
            print(f"❌ 加载报告失败: {e}")
            return []
    
    def analyze_mixing_patterns(self, framework_issues):
        """分析框架混用模式"""
        print("🔍 分析框架混用模式...")
        
        patterns = {
            "pytest_unittest": [],
            "pytest_nose": [],
            "unittest_nose": [],
            "vitest_jest": [],
            "jest_mocha": [],
            "other_combinations": []
        }
        
        for issue in framework_issues:
            file_path = issue['file']
            details = issue['details']
            
            # 提取混用的框架
            frameworks = re.findall(r'混用框架: (.+)', details)
            if frameworks:
                framework_list = frameworks[0].split(', ')
                
                # 分类混用模式
                if 'pytest' in framework_list and 'unittest' in framework_list:
                    patterns["pytest_unittest"].append(file_path)
                elif 'pytest' in framework_list and 'nose' in framework_list:
                    patterns["pytest_nose"].append(file_path)
                elif 'unittest' in framework_list and 'nose' in framework_list:
                    patterns["unittest_nose"].append(file_path)
                elif 'vitest' in framework_list and 'jest' in framework_list:
                    patterns["vitest_jest"].append(file_path)
                elif 'jest' in framework_list and 'mocha' in framework_list:
                    patterns["jest_mocha"].append(file_path)
                else:
                    patterns["other_combinations"].append(file_path)
        
        self.mixing_patterns = patterns
        
        # 打印模式统计
        print("📊 框架混用模式统计:")
        for pattern, files in patterns.items():
            if files:
                print(f"  {pattern}: {len(files)} 个文件")
        
        return patterns
    
    def analyze_file_complexity(self, file_path):
        """分析单个文件的修复复杂度"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            complexity_score = 0
            risk_factors = []
            
            # 1. 导入语句复杂度
            import_lines = re.findall(r'^import\s+(\w+)', content, re.MULTILINE)
            import_lines.extend(re.findall(r'^from\s+(\w+)', content, re.MULTILINE))
            
            test_framework_imports = [imp for imp in import_lines if any(fw in imp.lower() for fw in ['pytest', 'unittest', 'nose', 'vitest', 'jest', 'mocha'])]
            
            if len(test_framework_imports) > 1:
                complexity_score += 3
                risk_factors.append("多个测试框架导入")
            
            # 2. 测试类定义复杂度
            test_classes = re.findall(r'class\s+(\w+)\s*\(.*\):', content)
            unittest_classes = [cls for cls in test_classes if 'Test' in cls]
            pytest_classes = [cls for cls in test_classes if 'Test' in cls]
            
            if len(unittest_classes) > 0 and len(pytest_classes) > 0:
                complexity_score += 2
                risk_factors.append("混合测试类定义")
            
            # 3. 测试函数复杂度
            test_functions = re.findall(r'def\s+(test_\w+)', content)
            if len(test_functions) > 5:
                complexity_score += 1
                risk_factors.append("测试函数数量多")
            
            # 4. 装饰器复杂度
            decorators = re.findall(r'@(\w+)', content)
            test_decorators = [dec for dec in decorators if any(fw in dec.lower() for fw in ['pytest', 'unittest', 'nose'])]
            
            if len(test_decorators) > 2:
                complexity_score += 2
                risk_factors.append("多个测试装饰器")
            
            # 5. 文件大小复杂度
            lines = content.split('\n')
            if len(lines) > 100:
                complexity_score += 1
                risk_factors.append("文件行数多")
            
            # 6. 特殊语法复杂度
            if 'yield' in content:
                complexity_score += 1
                risk_factors.append("使用yield语法")
            
            if 'async' in content:
                complexity_score += 1
                risk_factors.append("使用异步语法")
            
            return {
                'score': complexity_score,
                'risk_factors': risk_factors,
                'imports': test_framework_imports,
                'test_classes': test_classes,
                'test_functions': test_functions,
                'decorators': test_decorators,
                'lines': len(lines)
            }
            
        except Exception as e:
            return {
                'score': 0,
                'risk_factors': [f"文件读取错误: {e}"],
                'imports': [],
                'test_classes': [],
                'test_functions': [],
                'decorators': [],
                'lines': 0
            }
    
    def assess_repair_risks(self, file_path, complexity_data):
        """评估修复风险"""
        risk_level = "low"
        risk_details = []
        
        if complexity_data['score'] >= 5:
            risk_level = "high"
        elif complexity_data['score'] >= 3:
            risk_level = "medium"
        
        # 具体风险分析
        if "多个测试框架导入" in complexity_data['risk_factors']:
            risk_details.append("需要重构导入语句，可能影响其他模块")
        
        if "混合测试类定义" in complexity_data['risk_factors']:
            risk_details.append("需要统一测试类继承结构")
        
        if "多个测试装饰器" in complexity_data['risk_factors']:
            risk_details.append("需要重新设计装饰器使用方式")
        
        if "文件行数多" in complexity_data['risk_factors']:
            risk_details.append("大文件修复风险较高，建议分批处理")
        
        return {
            'level': risk_level,
            'details': risk_details,
            'complexity_score': complexity_data['score']
        }
    
    def generate_repair_strategy(self, patterns, complexity_data):
        """生成修复策略建议"""
        print("💡 生成修复策略建议...")
        
        strategies = {
            "pytest_unittest": {
                "recommended_framework": "pytest",
                "migration_approach": "渐进式迁移",
                "steps": [
                    "1. 保留pytest装饰器和功能",
                    "2. 将unittest.TestCase继承改为pytest类",
                    "3. 替换unittest断言为pytest断言",
                    "4. 移除unittest特定导入"
                ],
                "estimated_effort": "2-4小时/文件"
            },
            "pytest_nose": {
                "recommended_framework": "pytest",
                "migration_approach": "直接替换",
                "steps": [
                    "1. 替换nose装饰器为pytest等价物",
                    "2. 更新测试发现机制",
                    "3. 调整测试运行参数"
                ],
                "estimated_effort": "1-3小时/文件"
            },
            "vitest_jest": {
                "recommended_framework": "vitest",
                "migration_approach": "功能映射",
                "steps": [
                    "1. 替换Jest API为Vitest等价物",
                    "2. 更新测试配置",
                    "3. 调整断言语法"
                ],
                "estimated_effort": "1-2小时/文件"
            }
        }
        
        return strategies
    
    def run_analysis(self):
        """运行完整的框架混用分析"""
        print("🚀 开始框架混用深度分析...")
        
        # 1. 加载问题报告
        framework_issues = self.load_issue_report()
        if not framework_issues:
            print("❌ 没有找到框架混用问题，分析终止")
            return None
        
        # 2. 分析混用模式
        patterns = self.analyze_mixing_patterns(framework_issues)
        
        # 3. 分析每个文件的复杂度
        print("🔍 分析文件修复复杂度...")
        for issue in framework_issues:
            file_path = issue['file']
            print(f"  分析: {file_path}")
            
            complexity_data = self.analyze_file_complexity(file_path)
            self.complexity_scores[file_path] = complexity_data
            
            risk_assessment = self.assess_repair_risks(file_path, complexity_data)
            self.risk_assessments[file_path] = risk_assessment
        
        # 4. 生成修复策略
        strategies = self.generate_repair_strategy(patterns, self.complexity_scores)
        
        # 5. 生成分析报告
        report = self.generate_analysis_report(patterns, strategies)
        
        print("✅ 框架混用深度分析完成！")
        return report
    
    def generate_analysis_report(self, patterns, strategies):
        """生成分析报告"""
        print("📝 生成分析报告...")
        
        # 统计信息
        total_files = sum(len(files) for files in patterns.values() if files)
        high_risk_files = len([f for f, risk in self.risk_assessments.items() if risk['level'] == 'high'])
        medium_risk_files = len([f for f, risk in self.risk_assessments.items() if risk['level'] == 'medium'])
        low_risk_files = len([f for f, risk in self.risk_assessments.items() if risk['level'] == 'low'])
        
        # 复杂度分布
        complexity_distribution = defaultdict(int)
        for complexity_data in self.complexity_scores.values():
            score = complexity_data['score']
            if score >= 5:
                complexity_distribution['high'] += 1
            elif score >= 3:
                complexity_distribution['medium'] += 1
            else:
                complexity_distribution['low'] += 1
        
        report = {
            "summary": {
                "total_files": total_files,
                "mixing_patterns": {k: len(v) for k, v in patterns.items() if v},
                "risk_distribution": {
                    "high": high_risk_files,
                    "medium": medium_risk_files,
                    "low": low_risk_files
                },
                "complexity_distribution": dict(complexity_distribution)
            },
            "detailed_analysis": {
                "patterns": patterns,
                "complexity_scores": self.complexity_scores,
                "risk_assessments": self.risk_assessments
            },
            "repair_strategies": strategies,
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self):
        """生成修复建议"""
        recommendations = []
        
        # 基于风险等级的建议
        high_risk_count = len([f for f, risk in self.risk_assessments.items() if risk['level'] == 'high'])
        if high_risk_count > 0:
            recommendations.append({
                "priority": "high",
                "action": "优先处理高风险文件",
                "reason": f"发现 {high_risk_count} 个高风险文件，需要谨慎处理",
                "approach": "分批修复，每次只处理1-2个文件"
            })
        
        # 基于复杂度的建议
        high_complexity_count = len([f for f, comp in self.complexity_scores.items() if comp['score'] >= 5])
        if high_complexity_count > 0:
            recommendations.append({
                "priority": "high",
                "action": "简化复杂文件结构",
                "reason": f"发现 {high_complexity_count} 个高复杂度文件",
                "approach": "先重构代码结构，再统一测试框架"
            })
        
        # 基于模式的建议
        pytest_unittest_count = len(self.mixing_patterns["pytest_unittest"])
        if pytest_unittest_count > 0:
            recommendations.append({
                "priority": "medium",
                "action": "统一为pytest框架",
                "reason": f"发现 {pytest_unittest_count} 个pytest+unittest混用文件",
                "approach": "pytest功能更强大，建议作为主导框架"
            })
        
        return recommendations

def main():
    analyzer = FrameworkMixingAnalyzer()
    report = analyzer.run_analysis()
    
    if report:
        # 保存报告
        with open("framework_mixing_analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 打印摘要
        print("\n📊 框架混用分析摘要:")
        summary = report['summary']
        print(f"总文件数: {summary['total_files']}")
        
        print("\n混用模式分布:")
        for pattern, count in summary['mixing_patterns'].items():
            print(f"  {pattern}: {count}")
        
        print("\n风险分布:")
        for risk_level, count in summary['risk_distribution'].items():
            print(f"  {risk_level}: {count}")
        
        print("\n复杂度分布:")
        for complexity_level, count in summary['complexity_distribution'].items():
            print(f"  {complexity_level}: {count}")
        
        print("\n修复建议:")
        for rec in report['recommendations']:
            print(f"  [{rec['priority'].upper()}] {rec['action']} - {rec['reason']}")
            print(f"      方法: {rec['approach']}")
        
        print(f"\n详细报告已保存到: framework_mixing_analysis_report.json")

if __name__ == "__main__":
    main()
