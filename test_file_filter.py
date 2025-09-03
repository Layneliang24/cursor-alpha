#!/usr/bin/env python3
"""
测试文件筛选器
识别真正的测试文件，过滤掉辅助工具文件
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any

class TestFileFilter:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.test_patterns = [
            r'^test_.*\.py$',           # 以test_开头的文件
            r'.*_test\.py$',            # 以_test结尾的文件
            r'.*Test.*\.py$',           # 包含Test的文件
        ]
        
        self.exclude_patterns = [
            r'.*helper.*\.py$',         # 包含helper的文件
            r'.*util.*\.py$',           # 包含util的文件
            r'.*factory.*\.py$',        # 包含factory的文件
            r'.*manager.*\.py$',        # 包含manager的文件
            r'.*generator.*\.py$',      # 包含generator的文件
        ]
    
    def is_test_file(self, file_path: str) -> bool:
        """判断文件是否为测试文件"""
        filename = Path(file_path).name
        
        # 检查是否匹配测试模式
        is_test = any(re.match(pattern, filename) for pattern in self.test_patterns)
        
        # 检查是否应该被排除
        should_exclude = any(re.search(pattern, filename, re.IGNORECASE) 
                           for pattern in self.exclude_patterns)
        
        # 检查文件内容是否包含测试函数
        has_test_functions = self.has_test_functions(file_path)
        
        return is_test and not should_exclude and has_test_functions
    
    def has_test_functions(self, file_path: str) -> bool:
        """检查文件是否包含测试函数"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否包含测试函数
            test_function_patterns = [
                r'def test_\w+',           # pytest风格
                r'def test\w+',            # 其他测试风格
                r'class.*Test.*:',         # 测试类
                r'self\.assert',           # unittest断言
                r'pytest\.',               # pytest相关
                r'@pytest\.',              # pytest装饰器
            ]
            
            return any(re.search(pattern, content) for pattern in test_function_patterns)
            
        except Exception:
            return False
    
    def filter_test_files(self, file_list: List[str]) -> List[str]:
        """过滤出真正的测试文件"""
        test_files = []
        
        for file_path in file_list:
            if self.is_test_file(file_path):
                test_files.append(file_path)
            else:
                print(f"⚠️ 跳过非测试文件: {file_path}")
        
        return test_files
    
    def analyze_file_list(self, file_list: List[str]) -> Dict[str, Any]:
        """分析文件列表，分类文件类型"""
        analysis = {
            "total_files": len(file_list),
            "test_files": [],
            "helper_files": [],
            "other_files": [],
            "recommendations": []
        }
        
        for file_path in file_list:
            filename = Path(file_path).name
            
            if self.is_test_file(file_path):
                analysis["test_files"].append(file_path)
            elif any(re.search(pattern, filename, re.IGNORECASE) 
                    for pattern in self.exclude_patterns):
                analysis["helper_files"].append(file_path)
                analysis["recommendations"].append(f"跳过 {file_path} - 辅助工具文件")
            else:
                analysis["other_files"].append(file_path)
                analysis["recommendations"].append(f"检查 {file_path} - 文件类型不明确")
        
        return analysis

def main():
    """主函数"""
    # 从策略报告加载文件列表
    try:
        import json
        with open("framework_unification_strategy_report.json", 'r', encoding='utf-8') as f:
            strategy = json.load(f)
        
        # 获取所有阶段的文件
        all_files = []
        for phase in ["phase_1", "phase_2", "phase_3"]:
            if phase in strategy.get("migration_strategy", {}).get("phases", {}):
                all_files.extend(strategy["migration_strategy"]["phases"][phase].get("files", []))
        
        print(f"📊 原始文件列表: {len(all_files)} 个文件")
        for file_path in all_files:
            print(f"  - {file_path}")
        
        # 创建筛选器
        filter_tool = TestFileFilter()
        
        # 筛选测试文件
        test_files = filter_tool.filter_test_files(all_files)
        
        print(f"\n✅ 筛选后的测试文件: {len(test_files)} 个文件")
        for file_path in test_files:
            print(f"  - {file_path}")
        
        # 分析结果
        analysis = filter_tool.analyze_file_list(all_files)
        
        print(f"\n📋 文件分析结果:")
        print(f"  总文件数: {analysis['total_files']}")
        print(f"  测试文件: {len(analysis['test_files'])}")
        print(f"  辅助文件: {len(analysis['helper_files'])}")
        print(f"  其他文件: {len(analysis['other_files'])}")
        
        if analysis['recommendations']:
            print(f"\n💡 建议:")
            for rec in analysis['recommendations']:
                print(f"  - {rec}")
        
        # 生成修正后的策略报告
        corrected_strategy = strategy.copy()
        for phase in ["phase_1", "phase_2", "phase_3"]:
            if phase in corrected_strategy.get("migration_strategy", {}).get("phases", {}):
                phase_files = corrected_strategy["migration_strategy"]["phases"][phase].get("files", [])
                corrected_files = filter_tool.filter_test_files(phase_files)
                corrected_strategy["migration_strategy"]["phases"][phase]["files"] = corrected_files
                corrected_strategy["migration_strategy"]["phases"][phase]["corrected_file_count"] = len(corrected_files)
        
        # 保存修正后的策略
        with open("corrected_framework_strategy.json", 'w', encoding='utf-8') as f:
            json.dump(corrected_strategy, f, indent=2, ensure_ascii=False)
        
        print(f"\n📝 修正后的策略已保存到: corrected_framework_strategy.json")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")

if __name__ == "__main__":
    main()

