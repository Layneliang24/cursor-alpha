#!/usr/bin/env python3
"""
测试文件结构树状图生成脚本
基于分析结果生成可视化的树状结构图
"""

import json
import os
from pathlib import Path

class TreeVisualizer:
    def __init__(self, structure_file='test_structure_report.json', framework_file='framework_analysis_report.json'):
        self.structure_file = structure_file
        self.framework_file = framework_file
        self.project_root = Path('.')
        
    def load_data(self):
        """加载分析数据"""
        try:
            with open(self.structure_file, 'r', encoding='utf-8') as f:
                structure_data = json.load(f)
            
            framework_data = None
            if os.path.exists(self.framework_file):
                with open(self.framework_file, 'r', encoding='utf-8') as f:
                    framework_data = json.load(f)
            
            return structure_data, framework_data
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            return None, None
    
    def generate_text_tree(self, structure_data, framework_data=None):
        """生成文本格式的树状图"""
        print("🌳 生成文本格式树状图...")
        
        tree_output = []
        tree_output.append("📁 项目测试文件结构树")
        tree_output.append("=" * 60)
        
        # 按目录组织
        for dir_name, files in structure_data['directory_structure'].items():
            tree_output.append(f"\n📂 {dir_name}/")
            
            # 按框架类型分组
            if framework_data:
                framework_groups = {}
                for file_info in files:
                    file_path = file_info['file']
                    framework = 'unknown'
                    
                    if file_path in framework_data.get('file_framework_mapping', {}):
                        framework = framework_data['file_framework_mapping'][file_path]['primary']
                    
                    if framework not in framework_groups:
                        framework_groups[framework] = []
                    framework_groups[framework].append(file_info)
                
                # 按框架类型显示
                for framework, group_files in framework_groups.items():
                    tree_output.append(f"  🔧 {framework} ({len(group_files)} 个文件):")
                    for file_info in group_files:
                        file_name = Path(file_info['file']).name
                        size_kb = file_info['size'] / 1024
                        tree_output.append(f"    📄 {file_name} ({size_kb:.1f} KB)")
            else:
                # 简单显示
                for file_info in files:
                    file_name = Path(file_info['file']).name
                    size_kb = file_info['size'] / 1024
                    tree_output.append(f"    📄 {file_name} ({size_kb:.1f} KB)")
        
        return "\n".join(tree_output)
    
    def generate_markdown_tree(self, structure_data, framework_data=None):
        """生成Markdown格式的树状图"""
        print("📝 生成Markdown格式树状图...")
        
        md_output = []
        md_output.append("# 项目测试文件结构树")
        md_output.append("")
        
        # 统计信息
        summary = structure_data['summary']
        md_output.append("## 📊 统计信息")
        md_output.append("")
        md_output.append(f"- **测试文件总数**: {summary['total_test_files']}")
        md_output.append(f"- **测试目录数量**: {summary['test_directories']}")
        md_output.append(f"- **框架类型分布**:")
        
        for framework, count in summary['framework_distribution'].items():
            md_output.append(f"  - {framework}: {count} 个文件")
        
        md_output.append("")
        md_output.append("## 📂 目录结构")
        md_output.append("")
        
        # 按目录组织
        for dir_name, files in structure_data['directory_structure'].items():
            md_output.append(f"### 📁 {dir_name}/")
            md_output.append("")
            
            if framework_data:
                # 按框架类型分组
                framework_groups = {}
                for file_info in files:
                    file_path = file_info['file']
                    framework = 'unknown'
                    
                    if file_path in framework_data.get('file_framework_mapping', {}):
                        framework = framework_data['file_framework_mapping'][file_path]['primary']
                    
                    if framework not in framework_groups:
                        framework_groups[framework] = []
                    framework_groups[framework].append(file_info)
                
                # 按框架类型显示
                for framework, group_files in framework_groups.items():
                    md_output.append(f"#### 🔧 {framework} ({len(group_files)} 个文件)")
                    md_output.append("")
                    
                    for file_info in group_files:
                        file_name = Path(file_info['file']).name
                        size_kb = file_info['size'] / 1024
                        md_output.append(f"- `{file_name}` ({size_kb:.1f} KB)")
                    
                    md_output.append("")
            else:
                # 简单显示
                for file_info in files:
                    file_name = Path(file_info['file']).name
                    size_kb = file_info['size'] / 1024
                    md_output.append(f"- `{file_name}` ({size_kb:.1f} KB)")
                
                md_output.append("")
        
        return "\n".join(md_output)
    
    def generate_html_tree(self, structure_data, framework_data=None):
        """生成HTML格式的树状图"""
        print("🌐 生成HTML格式树状图...")
        
        html_output = []
        html_output.append("<!DOCTYPE html>")
        html_output.append("<html lang='zh-CN'>")
        html_output.append("<head>")
        html_output.append("    <meta charset='UTF-8'>")
        html_output.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        html_output.append("    <title>项目测试文件结构树</title>")
        html_output.append("    <style>")
        html_output.append("        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }")
        html_output.append("        .container { max-width: 1200px; margin: 0 auto; }")
        html_output.append("        .stats { background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px; }")
        html_output.append("        .directory { margin: 20px 0; }")
        html_output.append("        .framework-group { margin: 15px 0; }")
        html_output.append("        .file-list { margin-left: 20px; }")
        html_output.append("        .file-item { padding: 5px 0; }")
        html_output.append("        .framework-badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin-left: 10px; }")
        html_output.append("        .pytest { background: #4CAF50; color: white; }")
        html_output.append("        .django_test { background: #2196F3; color: white; }")
        html_output.append("        .vitest { background: #FF9800; color: white; }")
        html_output.append("        .unknown { background: #9E9E9E; color: white; }")
        html_output.append("    </style>")
        html_output.append("</head>")
        html_output.append("<body>")
        html_output.append("    <div class='container'>")
        html_output.append("        <h1>🌳 项目测试文件结构树</h1>")
        
        # 统计信息
        summary = structure_data['summary']
        html_output.append("        <div class='stats'>")
        html_output.append("            <h2>📊 统计信息</h2>")
        html_output.append(f"            <p><strong>测试文件总数:</strong> {summary['total_test_files']}</p>")
        html_output.append(f"            <p><strong>测试目录数量:</strong> {summary['test_directories']}</p>")
        html_output.append("            <p><strong>框架类型分布:</strong></p>")
        html_output.append("            <ul>")
        
        for framework, count in summary['framework_distribution'].items():
            html_output.append(f"                <li>{framework}: {count} 个文件</li>")
        
        html_output.append("            </ul>")
        html_output.append("        </div>")
        
        # 目录结构
        html_output.append("        <h2>📂 目录结构</h2>")
        
        for dir_name, files in structure_data['directory_structure'].items():
            html_output.append(f"        <div class='directory'>")
            html_output.append(f"            <h3>📁 {dir_name}/</h3>")
            
            if framework_data:
                # 按框架类型分组
                framework_groups = {}
                for file_info in files:
                    file_path = file_info['file']
                    framework = 'unknown'
                    
                    if file_path in framework_data.get('file_framework_mapping', {}):
                        framework = framework_data['file_framework_mapping'][file_path]['primary']
                    
                    if framework not in framework_groups:
                        framework_groups[framework] = []
                    framework_groups[framework].append(file_info)
                
                # 按框架类型显示
                for framework, group_files in framework_groups.items():
                    html_output.append(f"            <div class='framework-group'>")
                    html_output.append(f"                <h4>🔧 {framework} ({len(group_files)} 个文件)</h4>")
                    html_output.append("                <div class='file-list'>")
                    
                    for file_info in group_files:
                        file_name = Path(file_info['file']).name
                        size_kb = file_info['size'] / 1024
                        framework_class = framework.replace('_', '-')
                        html_output.append(f"                    <div class='file-item'>")
                        html_output.append(f"                        📄 {file_name} ({size_kb:.1f} KB)")
                        html_output.append(f"                        <span class='framework-badge {framework_class}'>{framework}</span>")
                        html_output.append(f"                    </div>")
                    
                    html_output.append("                </div>")
                    html_output.append("            </div>")
            else:
                # 简单显示
                html_output.append("            <div class='file-list'>")
                for file_info in files:
                    file_name = Path(file_info['file']).name
                    size_kb = file_info['size'] / 1024
                    html_output.append(f"                <div class='file-item'>📄 {file_name} ({size_kb:.1f} KB)</div>")
                html_output.append("            </div>")
            
            html_output.append("        </div>")
        
        html_output.append("    </div>")
        html_output.append("</body>")
        html_output.append("</html>")
        
        return "\n".join(html_output)
    
    def save_outputs(self, text_tree, markdown_tree, html_tree):
        """保存所有输出格式"""
        try:
            # 保存文本格式
            with open('test_structure_tree.txt', 'w', encoding='utf-8') as f:
                f.write(text_tree)
            print("✅ 文本格式树状图已保存到: test_structure_tree.txt")
            
            # 保存Markdown格式
            with open('test_structure_tree.md', 'w', encoding='utf-8') as f:
                f.write(markdown_tree)
            print("✅ Markdown格式树状图已保存到: test_structure_tree.md")
            
            # 保存HTML格式
            with open('test_structure_tree.html', 'w', encoding='utf-8') as f:
                f.write(html_tree)
            print("✅ HTML格式树状图已保存到: test_structure_tree.html")
            
        except Exception as e:
            print(f"❌ 保存输出文件时出错: {e}")
    
    def print_summary(self, structure_data, framework_data):
        """打印生成摘要"""
        print("\n" + "="*60)
        print("🌳 树状结构图生成摘要")
        print("="*60)
        
        summary = structure_data['summary']
        print(f"📁 测试目录数量: {summary['test_directories']}")
        print(f"📄 测试文件总数: {summary['total_test_files']}")
        
        if framework_data:
            framework_stats = framework_data['framework_statistics']
            print(f"🔧 框架类型分布:")
            for framework, count in framework_stats.items():
                print(f"   {framework}: {count} 个文件")
        
        print(f"\n📊 输出文件:")
        print(f"   - test_structure_tree.txt (文本格式)")
        print(f"   - test_structure_tree.md (Markdown格式)")
        print(f"   - test_structure_tree.html (HTML格式)")

def main():
    """主函数"""
    print("🚀 开始生成测试文件结构树状图...")
    
    # 创建可视化器
    visualizer = TreeVisualizer()
    
    # 加载数据
    structure_data, framework_data = visualizer.load_data()
    if not structure_data:
        print("❌ 无法加载结构数据，退出")
        return
    
    # 生成各种格式的树状图
    text_tree = visualizer.generate_text_tree(structure_data, framework_data)
    markdown_tree = visualizer.generate_markdown_tree(structure_data, framework_data)
    html_tree = visualizer.generate_html_tree(structure_data, framework_data)
    
    # 保存输出
    visualizer.save_outputs(text_tree, markdown_tree, html_tree)
    
    # 打印摘要
    visualizer.print_summary(structure_data, framework_data)
    
    print("\n🎉 树状结构图生成完成！")

if __name__ == "__main__":
    main()
