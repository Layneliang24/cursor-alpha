#!/usr/bin/env python3
"""
测试问题识别和分类脚本
基于质量分析结果，识别测试体系中的关键问题并分类
"""

import json
import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

class TestIssueClassifier:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.issues = defaultdict(list)
        self.issue_categories = {
            "编码问题": [],
            "结构问题": [],
            "依赖缺失": [],
            "非测试代码": [],
            "框架混用": [],
            "重复测试": [],
            "质量缺陷": []
        }
        
    def load_quality_reports(self):
        """加载质量分析报告"""
        print("📊 加载质量分析报告...")
        
        reports = {}
        report_files = [
            "quality_analysis_report.json",
            "js_quality_analysis_report.json",
            "dependency_analysis_report.json"
        ]
        
        for report_file in report_files:
            if os.path.exists(report_file):
                try:
                    with open(report_file, 'r', encoding='utf-8') as f:
                        reports[report_file] = json.load(f)
                    print(f"✅ 加载: {report_file}")
                except Exception as e:
                    print(f"❌ 加载失败: {report_file} - {e}")
            else:
                print(f"⚠️ 文件不存在: {report_file}")
                
        return reports
    
    def classify_encoding_issues(self, reports):
        """分类编码问题"""
        print("🔍 识别编码问题...")
        
        encoding_issues = []
        
        # 检查Python文件编码问题
        if "quality_analysis_report.json" in reports:
            py_report = reports["quality_analysis_report.json"]
            for file_path, data in py_report.get("files", {}).items():
                if "encoding_issues" in data:
                    encoding_issues.append({
                        "file": file_path,
                        "type": "编码问题",
                        "severity": "high",
                        "priority": "high",
                        "description": "Unicode编码错误",
                        "details": data["encoding_issues"]
                    })
        
        # 检查JavaScript文件编码问题
        if "js_quality_analysis_report.json" in reports:
            js_report = reports["js_quality_analysis_report.json"]
            for file_path, data in js_report.get("files", {}).items():
                if "encoding_issues" in data:
                    encoding_issues.append({
                        "file": file_path,
                        "type": "编码问题",
                        "severity": "high",
                        "priority": "high",
                        "description": "Unicode编码错误",
                        "details": data["encoding_issues"]
                    })
        
        self.issue_categories["编码问题"] = encoding_issues
        print(f"✅ 识别到 {len(encoding_issues)} 个编码问题")
        
    def classify_structure_issues(self, reports):
        """分类结构问题"""
        print("🔍 识别结构问题...")
        
        structure_issues = []
        
        # 检查非标准格式
        if "quality_analysis_report.json" in reports:
            py_report = reports["quality_analysis_report.json"]
            for file_path, data in py_report.get("files", {}).items():
                if data.get("coding_standards", {}).get("score", 100) < 80:
                    structure_issues.append({
                        "file": file_path,
                        "type": "结构问题",
                        "severity": "medium",
                        "priority": "medium",
                        "description": "代码规范不符合标准",
                        "details": f"规范得分: {data['coding_standards']['score']}/100"
                    })
        
        # 检查JavaScript结构问题
        if "js_quality_analysis_report.json" in reports:
            js_report = reports["js_quality_analysis_report.json"]
            for file_path, data in js_report.get("files", {}).items():
                if data.get("codingStandards", {}).get("score", 100) < 80:
                    structure_issues.append({
                        "file": file_path,
                        "type": "结构问题",
                        "severity": "medium",
                        "priority": "medium",
                        "description": "代码规范不符合标准",
                        "details": f"规范得分: {data['codingStandards']['score']}/100"
                    })
        
        self.issue_categories["结构问题"] = structure_issues
        print(f"✅ 识别到 {len(structure_issues)} 个结构问题")
        
    def classify_dependency_issues(self, reports):
        """分类依赖缺失问题"""
        print("🔍 识别依赖缺失问题...")
        
        dependency_issues = []
        
        # 检查Python依赖问题
        if "quality_analysis_report.json" in reports:
            py_report = reports["quality_analysis_report.json"]
            for file_path, data in py_report.get("files", {}).items():
                if "missing_imports" in data:
                    dependency_issues.append({
                        "file": file_path,
                        "type": "依赖缺失",
                        "severity": "high",
                        "priority": "high",
                        "description": "缺少必要的导入",
                        "details": f"缺失导入: {', '.join(data['missing_imports'])}"
                    })
        
        # 检查JavaScript依赖问题
        if "js_quality_analysis_report.json" in reports:
            js_report = reports["js_quality_analysis_report.json"]
            for file_path, data in js_report.get("files", {}).items():
                if "missingImports" in data:
                    dependency_issues.append({
                        "file": file_path,
                        "type": "依赖缺失",
                        "severity": "high",
                        "priority": "high",
                        "description": "缺少必要的导入",
                        "details": f"缺失导入: {', '.join(data['missingImports'])}"
                    })
        
        self.issue_categories["依赖缺失"] = dependency_issues
        print(f"✅ 识别到 {len(dependency_issues)} 个依赖缺失问题")
        
    def classify_framework_mixing(self, reports):
        """分类框架混用问题"""
        print("🔍 识别框架混用问题...")
        
        framework_issues = []
        
        # 检查依赖分析报告中的框架混用
        if "dependency_analysis_report.json" in reports:
            dep_report = reports["dependency_analysis_report.json"]
            
            # 检查是否有文件同时依赖多个测试框架
            for file_path, deps in dep_report.get("dependencies", {}).items():
                frameworks = set()
                for dep in deps:
                    if "pytest" in dep.lower():
                        frameworks.add("pytest")
                    elif "unittest" in dep.lower():
                        frameworks.add("unittest")
                    elif "nose" in dep.lower():
                        frameworks.add("nose")
                    elif "vitest" in dep.lower():
                        frameworks.add("vitest")
                    elif "jest" in dep.lower():
                        frameworks.add("jest")
                    elif "mocha" in dep.lower():
                        frameworks.add("mocha")
                
                if len(frameworks) > 1:
                    framework_issues.append({
                        "file": file_path,
                        "type": "框架混用",
                        "severity": "medium",
                        "priority": "medium",
                        "description": "多个测试框架混用",
                        "details": f"混用框架: {', '.join(frameworks)}"
                    })
        
        self.issue_categories["框架混用"] = framework_issues
        print(f"✅ 识别到 {len(framework_issues)} 个框架混用问题")
        
    def classify_duplicate_tests(self, reports):
        """分类重复测试问题"""
        print("🔍 识别重复测试问题...")
        
        duplicate_issues = []
        
        # 检查是否有重复的测试函数名
        test_functions = defaultdict(list)
        
        if "quality_analysis_report.json" in reports:
            py_report = reports["quality_analysis_report.json"]
            for file_path, data in py_report.get("files", {}).items():
                if "test_functions" in data:
                    for func_name in data["test_functions"]:
                        test_functions[func_name].append(file_path)
        
        if "js_quality_analysis_report.json" in reports:
            js_report = reports["js_quality_analysis_report.json"]
            for file_path, data in js_report.get("files", {}).items():
                if "testFunctions" in data:
                    for func_name in data["testFunctions"]:
                        test_functions[func_name].append(file_path)
        
        # 找出重复的测试函数
        for func_name, files in test_functions.items():
            if len(files) > 1:
                duplicate_issues.append({
                    "file": ", ".join(files),
                    "type": "重复测试",
                    "severity": "low",
                    "priority": "low",
                    "description": "重复的测试函数名",
                    "details": f"函数名: {func_name}, 出现在: {', '.join(files)}"
                })
        
        self.issue_categories["重复测试"] = duplicate_issues
        print(f"✅ 识别到 {len(duplicate_issues)} 个重复测试问题")
        
    def classify_quality_defects(self, reports):
        """分类质量缺陷"""
        print("🔍 识别质量缺陷...")
        
        quality_issues = []
        
        # 检查Python质量缺陷
        if "quality_analysis_report.json" in reports:
            py_report = reports["quality_analysis_report.json"]
            for file_path, data in py_report.get("files", {}).items():
                if data.get("quality_score", 100) < 60:
                    quality_issues.append({
                        "file": file_path,
                        "type": "质量缺陷",
                        "severity": "high",
                        "priority": "high",
                        "description": "代码质量严重不足",
                        "details": f"质量得分: {data.get('quality_score', 0)}/100"
                    })
                elif data.get("complexity", 0) > 15:
                    quality_issues.append({
                        "file": file_path,
                        "type": "质量缺陷",
                        "severity": "medium",
                        "priority": "medium",
                        "description": "代码复杂度过高",
                        "details": f"复杂度: {data.get('complexity', 0)}"
                    })
        
        # 检查JavaScript质量缺陷
        if "js_quality_analysis_report.json" in reports:
            js_report = reports["js_quality_analysis_report.json"]
            for file_path, data in js_report.get("files", {}).items():
                if data.get("qualityScore", 100) < 60:
                    quality_issues.append({
                        "file": file_path,
                        "type": "质量缺陷",
                        "severity": "high",
                        "priority": "high",
                        "description": "代码质量严重不足",
                        "details": f"质量得分: {data.get('qualityScore', 0)}/100"
                    })
                elif data.get("complexity", 0) > 15:
                    quality_issues.append({
                        "file": file_path,
                        "type": "质量缺陷",
                        "severity": "medium",
                        "priority": "medium",
                        "description": "代码复杂度过高",
                        "details": f"复杂度: {data.get('complexity', 0)}"
                    })
        
        self.issue_categories["质量缺陷"] = quality_issues
        print(f"✅ 识别到 {len(quality_issues)} 个质量缺陷")
        
    def generate_priority_matrix(self):
        """生成优先级矩阵"""
        print("📊 生成优先级矩阵...")
        
        priority_matrix = {
            "high": [],
            "medium": [],
            "low": []
        }
        
        severity_matrix = {
            "high": [],
            "medium": [],
            "low": []
        }
        
        for category, issues in self.issue_categories.items():
            for issue in issues:
                priority_matrix[issue["priority"]].append(issue)
                severity_matrix[issue["severity"]].append(issue)
        
        return priority_matrix, severity_matrix
    
    def generate_report(self):
        """生成问题分类报告"""
        print("📝 生成问题分类报告...")
        
        # 统计信息
        total_issues = sum(len(issues) for issues in self.issue_categories.values())
        
        # 按优先级和严重性分类
        priority_matrix, severity_matrix = self.generate_priority_matrix()
        
        report = {
            "summary": {
                "total_issues": total_issues,
                "categories": {cat: len(issues) for cat, issues in self.issue_categories.items()},
                "priority_distribution": {pri: len(issues) for pri, issues in priority_matrix.items()},
                "severity_distribution": {sev: len(issues) for sev, issues in severity_matrix.items()}
            },
            "issues_by_category": self.issue_categories,
            "issues_by_priority": priority_matrix,
            "issues_by_severity": severity_matrix,
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self):
        """生成修复建议"""
        recommendations = []
        
        # 高优先级问题建议
        high_priority_count = len(self.issue_categories["编码问题"]) + len(self.issue_categories["依赖缺失"])
        if high_priority_count > 0:
            recommendations.append({
                "priority": "high",
                "action": "立即修复编码和依赖问题",
                "reason": f"发现 {high_priority_count} 个高优先级问题，可能影响测试执行",
                "estimated_effort": "2-4小时"
            })
        
        # 中优先级问题建议
        medium_priority_count = len(self.issue_categories["结构问题"]) + len(self.issue_categories["框架混用"])
        if medium_priority_count > 0:
            recommendations.append({
                "priority": "medium",
                "action": "逐步修复结构和框架问题",
                "reason": f"发现 {medium_priority_count} 个中优先级问题，影响代码质量",
                "estimated_effort": "4-8小时"
            })
        
        # 低优先级问题建议
        low_priority_count = len(self.issue_categories["重复测试"])
        if low_priority_count > 0:
            recommendations.append({
                "priority": "low",
                "action": "清理重复测试",
                "reason": f"发现 {low_priority_count} 个重复测试，影响维护性",
                "estimated_effort": "1-2小时"
            })
        
        return recommendations
    
    def run_analysis(self):
        """运行完整的问题分析"""
        print("🚀 开始测试问题识别和分类分析...")
        
        # 加载质量报告
        reports = self.load_quality_reports()
        
        if not reports:
            print("❌ 没有找到质量分析报告，无法进行分类")
            return None
        
        # 执行分类
        self.classify_encoding_issues(reports)
        self.classify_structure_issues(reports)
        self.classify_dependency_issues(reports)
        self.classify_framework_mixing(reports)
        self.classify_duplicate_tests(reports)
        self.classify_quality_defects(reports)
        
        # 生成报告
        report = self.generate_report()
        
        print("✅ 问题识别和分类分析完成！")
        return report

def main():
    classifier = TestIssueClassifier()
    report = classifier.run_analysis()
    
    if report:
        # 保存报告
        with open("issue_classification_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 打印摘要
        print("\n📊 问题分类摘要:")
        print(f"总问题数: {report['summary']['total_issues']}")
        print("\n按类别分布:")
        for category, count in report['summary']['categories'].items():
            print(f"  {category}: {count}")
        
        print("\n按优先级分布:")
        for priority, count in report['summary']['priority_distribution'].items():
            print(f"  {priority}: {count}")
        
        print("\n修复建议:")
        for rec in report['recommendations']:
            print(f"  [{rec['priority'].upper()}] {rec['action']} - {rec['reason']} (预计: {rec['estimated_effort']})")
        
        print(f"\n详细报告已保存到: issue_classification_report.json")

if __name__ == "__main__":
    main()


