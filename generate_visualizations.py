#!/usr/bin/env python3
"""
测试结构可视化图表生成脚本
生成树状结构图和依赖关系图
"""

import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict

class VisualizationGenerator:
    def __init__(self):
        self.project_root = Path('.')
        
    def generate_tree_structure(self, test_report):
        """生成树状结构图"""
        print("🌳 生成树状结构图...")
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(16, 12))
        
        # 构建树状结构数据
        tree_data = defaultdict(list)
        for dir_name, files in test_report['directory_structure'].items():
            parts = dir_name.split('/')
            current = tree_data
            for part in parts:
                if part not in current:
                    current[part] = {'files': [], 'subdirs': defaultdict(dict)}
                current = current[part]['subdirs']
            
            # 添加文件
            current = tree_data
            for part in parts:
                current = current[part]['subdirs']
            current['files'] = files
        
        # 绘制树状图
        self._draw_tree(tree_data, ax, x=0, y=0, level=0)
        
        ax.set_xlim(-1, 20)
        ax.set_ylim(-1, 15)
        ax.set_title('测试文件结构树状图', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        # 保存图片
        plt.tight_layout()
        plt.savefig('test_structure_tree.png', dpi=300, bbox_inches='tight')
        print("✅ 树状结构图已生成: test_structure_tree.png")
        
    def _draw_tree(self, node, ax, x, y, level, max_width=20):
        """递归绘制树状图"""
        if not node:
            return
            
        # 绘制当前节点
        if 'files' in node:
            # 这是叶子节点（包含文件）
            file_count = len(node['files'])
            ax.text(x, y, f'📁 {file_count} files', 
                   fontsize=10, ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue'))
        else:
            # 这是目录节点
            ax.text(x, y, '📂', fontsize=20, ha='center', va='center')
        
        # 绘制子节点
        if 'subdirs' in node:
            subdirs = list(node['subdirs'].keys())
            if subdirs:
                # 计算子节点位置
                total_width = len(subdirs) * 2
                start_x = x - total_width / 2
                
                for i, subdir in enumerate(subdirs):
                    child_x = start_x + i * 2
                    child_y = y - 1.5
                    
                    # 绘制连接线
                    ax.plot([x, child_x], [y-0.3, child_y+0.3], 'k-', alpha=0.5)
                    
                    # 递归绘制子节点
                    self._draw_tree(node['subdirs'][subdir], ax, child_x, child_y, level+1)
    
    def generate_dependency_graph(self, dependency_report):
        """生成依赖关系图"""
        print("🔗 生成依赖关系图...")
        
        # 创建有向图
        G = nx.DiGraph()
        
        # 添加节点和边
        for file_path, imports in dependency_report['dependencies'].items():
            G.add_node(file_path)
            for imp in imports:
                G.add_edge(file_path, imp)
        
        # 创建图形
        plt.figure(figsize=(20, 16))
        
        # 使用spring布局
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # 绘制节点
        nx.draw_networkx_nodes(G, pos, 
                              node_color='lightblue',
                              node_size=1000,
                              alpha=0.7)
        
        # 绘制边
        nx.draw_networkx_edges(G, pos, 
                              edge_color='gray',
                              arrows=True,
                              arrowsize=10,
                              alpha=0.5)
        
        # 绘制标签（只显示文件名，避免过长）
        labels = {node: Path(node).name for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        plt.title('测试文件依赖关系图', fontsize=16, fontweight='bold')
        plt.axis('off')
        
        # 保存图片
        plt.tight_layout()
        plt.savefig('test_dependency_graph.png', dpi=300, bbox_inches='tight')
        print("✅ 依赖关系图已生成: test_dependency_graph.png")
        
        # 生成统计信息
        self._generate_dependency_stats(G, dependency_report)
    
    def _generate_dependency_stats(self, G, dependency_report):
        """生成依赖关系统计信息"""
        print("📊 生成依赖关系统计...")
        
        stats = {
            'total_nodes': G.number_of_nodes(),
            'total_edges': G.number_of_edges(),
            'in_degree_centrality': nx.in_degree_centrality(G),
            'out_degree_centrality': nx.out_degree_centrality(G),
            'circular_dependencies': dependency_report['circular_dependencies']
        }
        
        # 找出最重要的节点（被依赖最多的）
        in_degrees = dict(G.in_degree())
        most_depended_on = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 找出依赖最多的节点
        out_degrees = dict(G.out_degree())
        most_dependent = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print(f"\n📈 依赖关系统计:")
        print(f"   - 总节点数: {stats['total_nodes']}")
        print(f"   - 总边数: {stats['total_edges']}")
        print(f"   - 循环依赖数: {len(stats['circular_dependencies'])}")
        
        print(f"\n🔝 被依赖最多的节点 (Top 5):")
        for node, degree in most_depended_on[:5]:
            print(f"   - {Path(node).name}: {degree} 个依赖")
        
        print(f"\n🔝 依赖最多的节点 (Top 5):")
        for node, degree in most_dependent[:5]:
            print(f"   - {Path(node).name}: {degree} 个依赖")
    
    def generate_framework_distribution(self, framework_report):
        """生成框架分布饼图"""
        print("🍰 生成框架分布图...")
        
        frameworks = framework_report['framework_statistics']
        
        # 创建饼图
        plt.figure(figsize=(10, 8))
        plt.pie(frameworks.values(), 
                labels=frameworks.keys(),
                autopct='%1.1f%%',
                startangle=90)
        plt.title('测试框架分布', fontsize=16, fontweight='bold')
        
        # 保存图片
        plt.tight_layout()
        plt.savefig('framework_distribution.png', dpi=300, bbox_inches='tight')
        print("✅ 框架分布图已生成: framework_distribution.png")
    
    def generate_comprehensive_report(self):
        """生成综合可视化报告"""
        print("📋 生成综合可视化报告...")
        
        # 加载各种报告
        try:
            with open('test_structure_report.json', 'r', encoding='utf-8') as f:
                test_report = json.load(f)
        except FileNotFoundError:
            print("❌ 找不到test_structure_report.json")
            return
            
        try:
            with open('framework_analysis_report.json', 'r', encoding='utf-8') as f:
                framework_report = json.load(f)
        except FileNotFoundError:
            print("❌ 找不到framework_analysis_report.json")
            return
            
        try:
            with open('dependency_analysis_report.json', 'r', encoding='utf-8') as f:
                dependency_report = json.load(f)
        except FileNotFoundError:
            print("❌ 找不到dependency_analysis_report.json")
            return
        
        # 生成各种图表
        self.generate_tree_structure(test_report)
        self.generate_dependency_graph(dependency_report)
        self.generate_framework_distribution(framework_report)
        
        # 生成HTML报告
        self._generate_html_report(test_report, framework_report, dependency_report)
        
        print("✅ 所有可视化图表生成完成！")
    
    def _generate_html_report(self, test_report, framework_report, dependency_report):
        """生成HTML综合报告"""
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试体系分析报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
        .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
        .chart {{ text-align: center; margin: 20px 0; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
        .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 测试体系分析报告</h1>
        <p>基于 {test_report['summary']['total_test_files']} 个测试文件的全面分析</p>
    </div>
    
    <div class="section">
        <h2>📊 总体统计</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{test_report['summary']['total_test_files']}</div>
                <div>测试文件总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{test_report['summary']['test_directories']}</div>
                <div>测试目录数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{framework_report['framework_statistics'].get('pytest', 0)}</div>
                <div>Pytest文件</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{framework_report['framework_statistics'].get('vitest', 0)}</div>
                <div>Vitest文件</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🌳 文件结构树</h2>
        <div class="chart">
            <img src="test_structure_tree.png" alt="测试结构树状图" style="max-width: 100%; height: auto;">
        </div>
    </div>
    
    <div class="section">
        <h2>🔗 依赖关系图</h2>
        <div class="chart">
            <img src="test_dependency_graph.png" alt="依赖关系图" style="max-width: 100%; height: auto;">
        </div>
    </div>
    
    <div class="section">
        <h2>🍰 框架分布</h2>
        <div class="chart">
            <img src="framework_distribution.png" alt="框架分布图" style="max-width: 100%; height: auto;">
        </div>
    </div>
    
    <div class="section">
        <h2>⚠️ 发现的问题</h2>
        <ul>
            <li>循环依赖: {len(dependency_report.get('circular_dependencies', []))} 个</li>
            <li>框架混用: 需要统一测试框架</li>
            <li>依赖复杂: 需要简化依赖关系</li>
        </ul>
    </div>
</body>
</html>
        """
        
        with open('test_analysis_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print("✅ HTML综合报告已生成: test_analysis_report.html")

def main():
    """主函数"""
    generator = VisualizationGenerator()
    generator.generate_comprehensive_report()

if __name__ == "__main__":
    main()


