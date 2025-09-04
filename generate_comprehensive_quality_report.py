#!/usr/bin/env python3
"""
综合质量报告生成器
整合Python和JavaScript的质量评估结果，生成综合质量报告
"""

import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
from collections import defaultdict

class ComprehensiveQualityReporter:
    def __init__(self):
        self.project_root = Path('.')
        
    def load_quality_reports(self):
        """加载质量分析报告"""
        reports = {}
        
        # 加载Python质量报告
        try:
            with open('quality_analysis_report.json', 'r', encoding='utf-8') as f:
                reports['python'] = json.load(f)
            print("✅ 加载Python质量报告成功")
        except FileNotFoundError:
            print("❌ 找不到Python质量报告")
            reports['python'] = None
            
        # 加载JavaScript质量报告
        try:
            with open('js_quality_analysis_report.json', 'r', encoding='utf-8') as f:
                reports['javascript'] = json.load(f)
            print("✅ 加载JavaScript质量报告成功")
        except FileNotFoundError:
            print("❌ 找不到JavaScript质量报告")
            reports['javascript'] = None
            
        return reports
    
    def generate_comprehensive_report(self, reports):
        """生成综合质量报告"""
        print("📊 生成综合质量报告...")
        
        if not reports['python'] and not reports['javascript']:
            print("❌ 没有可用的质量报告")
            return
            
        # 合并数据
        combined_data = self._combine_quality_data(reports)
        
        # 生成可视化图表
        self._generate_quality_charts(combined_data)
        
        # 生成HTML报告
        self._generate_html_report(combined_data, reports)
        
        # 保存JSON报告
        with open('comprehensive_quality_report.json', 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
            
        print("✅ 综合质量报告已生成: comprehensive_quality_report.json")
    
    def _combine_quality_data(self, reports):
        """合并质量数据"""
        combined = {
            'summary': {
                'total_files': 0,
                'python_files': 0,
                'javascript_files': 0,
                'overall_quality_score': 0.0,
                'overall_complexity': 0.0,
                'overall_test_coverage': 0.0
            },
            'quality_distribution': {
                'excellent': 0,
                'good': 0,
                'fair': 0,
                'poor': 0
            },
            'language_comparison': {},
            'top_issues': [],
            'recommendations': []
        }
        
        # 处理Python数据
        if reports['python']:
            python_data = reports['python']
            combined['summary']['python_files'] = python_data['summary']['total_files']
            combined['summary']['total_files'] += python_data['summary']['total_files']
            
            # 质量分布
            for quality, count in python_data['quality_distribution'].items():
                combined['quality_distribution'][quality] += count
                
            # 语言比较
            combined['language_comparison']['python'] = {
                'quality_score': python_data['summary']['average_quality_score'],
                'complexity': python_data['summary']['average_complexity'],
                'test_coverage': python_data['summary']['average_test_coverage']
            }
        
        # 处理JavaScript数据
        if reports['javascript']:
            js_data = reports['javascript']
            combined['summary']['javascript_files'] = js_data['summary']['total_files']
            combined['summary']['total_files'] += js_data['summary']['total_files']
            
            # 质量分布
            for quality, count in js_data['quality_distribution'].items():
                combined['quality_distribution'][quality] += count
                
            # 语言比较
            combined['language_comparison']['javascript'] = {
                'quality_score': js_data['summary']['average_quality_score'],
                'complexity': js_data['summary']['average_complexity'],
                'test_coverage': js_data['summary']['average_test_coverage']
            }
        
        # 计算总体指标
        if combined['summary']['total_files'] > 0:
            total_quality = 0
            total_complexity = 0
            total_coverage = 0
            file_count = 0
            
            for lang_data in combined['language_comparison'].values():
                if reports['python'] and reports['javascript']:
                    # 加权平均
                    weight = combined['summary']['python_files'] if 'python' in lang_data else combined['summary']['javascript_files']
                    total_quality += lang_data['quality_score'] * weight
                    total_complexity += lang_data['complexity'] * weight
                    total_coverage += lang_data['test_coverage'] * weight
                    file_count += weight
            
            combined['summary']['overall_quality_score'] = total_quality / file_count if file_count > 0 else 0
            combined['summary']['overall_complexity'] = total_complexity / file_count if file_count > 0 else 0
            combined['summary']['overall_test_coverage'] = total_coverage / file_count if file_count > 0 else 0
        
        # 生成建议
        combined['recommendations'] = self._generate_recommendations(combined)
        
        return combined
    
    def _generate_recommendations(self, combined_data):
        """生成改进建议"""
        recommendations = []
        
        # 基于质量评分的建议
        overall_score = combined_data['summary']['overall_quality_score']
        if overall_score < 50:
            recommendations.append("🚨 整体质量较差，需要立即进行代码重构和质量改进")
        elif overall_score < 70:
            recommendations.append("⚠️ 整体质量一般，建议逐步改进代码质量")
        elif overall_score < 85:
            recommendations.append("✅ 整体质量良好，可以进一步优化")
        else:
            recommendations.append("🎉 整体质量优秀，继续保持")
        
        # 基于复杂度的建议
        overall_complexity = combined_data['summary']['overall_complexity']
        if overall_complexity > 10:
            recommendations.append("🔧 代码复杂度较高，建议重构复杂函数，提取公共逻辑")
        elif overall_complexity > 7:
            recommendations.append("📝 代码复杂度适中，建议优化复杂函数")
        
        # 基于测试覆盖率的建议
        overall_coverage = combined_data['summary']['overall_test_coverage']
        if overall_coverage < 70:
            recommendations.append("🧪 测试覆盖率较低，建议增加测试用例")
        elif overall_coverage < 85:
            recommendations.append("📊 测试覆盖率一般，建议完善测试")
        
        # 基于质量分布的建议
        poor_count = combined_data['quality_distribution']['poor']
        if poor_count > 0:
            recommendations.append(f"🔍 发现 {poor_count} 个质量较差的文件，建议优先重构")
        
        # 语言特定建议
        if 'python' in combined_data['language_comparison']:
            python_score = combined_data['language_comparison']['python']['quality_score']
            if python_score < 70:
                recommendations.append("🐍 Python代码质量需要改进，建议使用pylint、black等工具")
        
        if 'javascript' in combined_data['language_comparison']:
            js_score = combined_data['language_comparison']['javascript']['quality_score']
            if js_score < 70:
                recommendations.append("🟨 JavaScript代码质量需要改进，建议使用ESLint、Prettier等工具")
        
        return recommendations
    
    def _generate_quality_charts(self, combined_data):
        """生成质量可视化图表"""
        print("📈 生成质量可视化图表...")
        
        # 1. 质量分布饼图
        self._generate_quality_distribution_chart(combined_data)
        
        # 2. 语言对比柱状图
        self._generate_language_comparison_chart(combined_data)
        
        # 3. 质量评分分布直方图
        self._generate_quality_score_histogram(combined_data)
        
        print("✅ 质量可视化图表生成完成")
    
    def _generate_quality_distribution_chart(self, combined_data):
        """生成质量分布饼图"""
        distribution = combined_data['quality_distribution']
        
        plt.figure(figsize=(10, 8))
        labels = ['优秀 (90+)', '良好 (80-89)', '一般 (70-79)', '较差 (<70)']
        sizes = [distribution['excellent'], distribution['good'], distribution['fair'], distribution['poor']]
        colors = ['#28a745', '#17a2b8', '#ffc107', '#dc3545']
        
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        plt.title('测试文件质量分布', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('quality_distribution.png', dpi=300, bbox_inches='tight')
        print("✅ 质量分布图已生成: quality_distribution.png")
    
    def _generate_language_comparison_chart(self, combined_data):
        """生成语言对比柱状图"""
        if not combined_data['language_comparison']:
            return
            
        languages = list(combined_data['language_comparison'].keys())
        quality_scores = [combined_data['language_comparison'][lang]['quality_score'] for lang in languages]
        complexities = [combined_data['language_comparison'][lang]['complexity'] for lang in languages]
        coverages = [combined_data['language_comparison'][lang]['test_coverage'] for lang in languages]
        
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
        
        # 质量评分对比
        bars1 = ax1.bar(languages, quality_scores, color=['#007bff', '#28a745'])
        ax1.set_title('质量评分对比', fontweight='bold')
        ax1.set_ylabel('质量评分')
        ax1.set_ylim(0, 100)
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}', ha='center', va='bottom')
        
        # 复杂度对比
        bars2 = ax2.bar(languages, complexities, color=['#ffc107', '#fd7e14'])
        ax2.set_title('代码复杂度对比', fontweight='bold')
        ax2.set_ylabel('平均复杂度')
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.1f}', ha='center', va='bottom')
        
        # 测试覆盖率对比
        bars3 = ax3.bar(languages, coverages, color=['#6f42c1', '#e83e8c'])
        ax3.set_title('测试覆盖率对比', fontweight='bold')
        ax3.set_ylabel('覆盖率 (%)')
        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('language_comparison.png', dpi=300, bbox_inches='tight')
        print("✅ 语言对比图已生成: language_comparison.png")
    
    def _generate_quality_score_histogram(self, combined_data):
        """生成质量评分分布直方图"""
        # 这里需要从详细数据中提取质量评分
        # 由于数据结构限制，我们创建一个简化的分布图
        plt.figure(figsize=(10, 6))
        
        # 创建质量区间
        quality_ranges = ['0-20', '21-40', '41-60', '61-80', '81-100']
        quality_counts = [
            combined_data['quality_distribution']['poor'] // 2,  # 简化处理
            combined_data['quality_distribution']['poor'] // 2,
            combined_data['quality_distribution']['fair'],
            combined_data['quality_distribution']['good'],
            combined_data['quality_distribution']['excellent']
        ]
        
        bars = plt.bar(quality_ranges, quality_counts, color=['#dc3545', '#fd7e14', '#ffc107', '#17a2b8', '#28a745'])
        plt.title('质量评分分布', fontsize=16, fontweight='bold')
        plt.xlabel('质量评分区间')
        plt.ylabel('文件数量')
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        str(int(height)), ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('quality_score_distribution.png', dpi=300, bbox_inches='tight')
        print("✅ 质量评分分布图已生成: quality_score_distribution.png")
    
    def _generate_html_report(self, combined_data, reports):
        """生成HTML综合质量报告"""
        print("🌐 生成HTML综合质量报告...")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试文件综合质量报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 15px; text-align: center; }}
        .section {{ background: white; margin: 20px 0; padding: 25px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 20px; border-radius: 10px; text-align: center; border-left: 4px solid #007bff; }}
        .stat-number {{ font-size: 2.5em; font-weight: bold; color: #007bff; margin-bottom: 10px; }}
        .chart {{ text-align: center; margin: 30px 0; }}
        .recommendations {{ background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; }}
        .recommendation {{ margin: 10px 0; padding: 10px; background: white; border-radius: 5px; border-left: 4px solid #ffc107; }}
        .quality-bad {{ color: #dc3545; }}
        .quality-good {{ color: #28a745; }}
        .quality-warning {{ color: #ffc107; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 测试文件综合质量报告</h1>
        <p>基于 {combined_data['summary']['total_files']} 个测试文件的全面质量分析</p>
    </div>
    
    <div class="section">
        <h2>📊 总体统计</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{combined_data['summary']['total_files']}</div>
                <div>测试文件总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{combined_data['summary']['python_files']}</div>
                <div>Python文件</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{combined_data['summary']['javascript_files']}</div>
                <div>JavaScript文件</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{combined_data['summary']['overall_quality_score']:.1f}</div>
                <div>整体质量评分</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🎯 质量指标</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number {self._get_quality_class(combined_data['summary']['overall_quality_score'])}">{combined_data['summary']['overall_quality_score']:.1f}/100</div>
                <div>整体质量评分</div>
            </div>
            <div class="stat-card">
                <div class="stat-number {self._get_complexity_class(combined_data['summary']['overall_complexity'])}">{combined_data['summary']['overall_complexity']:.1f}</div>
                <div>平均复杂度</div>
            </div>
            <div class="stat-card">
                <div class="stat-number {self._get_coverage_class(combined_data['summary']['overall_test_coverage'])}">{combined_data['summary']['overall_test_coverage']:.1f}%</div>
                <div>平均测试覆盖率</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🌳 质量分布</h2>
        <div class="chart">
            <img src="quality_distribution.png" alt="质量分布图" style="max-width: 100%; height: auto;">
        </div>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number quality-good">{combined_data['quality_distribution']['excellent']}</div>
                <div>优秀文件 (90+)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number quality-good">{combined_data['quality_distribution']['good']}</div>
                <div>良好文件 (80-89)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number quality-warning">{combined_data['quality_distribution']['fair']}</div>
                <div>一般文件 (70-79)</div>
            </div>
            <div class="stat-card">
                <div class="stat-number quality-bad">{combined_data['quality_distribution']['poor']}</div>
                <div>较差文件 (<70)</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🔍 语言对比</h2>
        <div class="chart">
            <img src="language_comparison.png" alt="语言对比图" style="max-width: 100%; height: auto;">
        </div>
    </div>
    
    <div class="section">
        <h2>📈 质量评分分布</h2>
        <div class="chart">
            <img src="quality_score_distribution.png" alt="质量评分分布图" style="max-width: 100%; height: auto;">
        </div>
    </div>
    
    <div class="section">
        <h2>💡 改进建议</h2>
        <div class="recommendations">
            {''.join([f'<div class="recommendation">{rec}</div>' for rec in combined_data['recommendations']])}
        </div>
    </div>
    
    <div class="section">
        <h2>📋 详细报告</h2>
        <ul>
            <li><a href="quality_analysis_report.json">Python质量分析报告 (JSON)</a></li>
            <li><a href="js_quality_analysis_report.json">JavaScript质量分析报告 (JSON)</a></li>
            <li><a href="comprehensive_quality_report.json">综合质量报告 (JSON)</a></li>
        </ul>
    </div>
</body>
</html>
        """
        
        with open('comprehensive_quality_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print("✅ HTML综合质量报告已生成: comprehensive_quality_report.html")
    
    def _get_quality_class(self, score):
        """获取质量评分的CSS类"""
        if score >= 80:
            return 'quality-good'
        elif score >= 60:
            return 'quality-warning'
        else:
            return 'quality-bad'
    
    def _get_complexity_class(self, complexity):
        """获取复杂度的CSS类"""
        if complexity <= 5:
            return 'quality-good'
        elif complexity <= 10:
            return 'quality-warning'
        else:
            return 'quality-bad'
    
    def _get_coverage_class(self, coverage):
        """获取覆盖率的CSS类"""
        if coverage >= 80:
            return 'quality-good'
        elif coverage >= 60:
            return 'quality-warning'
        else:
            return 'quality-bad'

def main():
    """主函数"""
    reporter = ComprehensiveQualityReporter()
    
    # 加载质量报告
    reports = reporter.load_quality_reports()
    
    # 生成综合报告
    reporter.generate_comprehensive_report(reports)
    
    print("✅ 综合质量报告生成完成！")

if __name__ == "__main__":
    main()


