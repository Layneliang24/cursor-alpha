# -*- coding: utf-8 -*-
"""
测试报告生成工具
用于生成和汇总测试报告
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tests_dir = project_root / 'tests'
        self.reports_dir = self.tests_dir / 'reports'
        self.html_dir = self.reports_dir / 'html'
        self.json_dir = self.reports_dir / 'json'
    
    def generate_summary_report(self):
        """生成测试总结报告"""
        summary_file = self.html_dir / 'test_summary.html'
        
        # 收集报告信息
        reports_info = self._collect_reports_info()
        
        # 生成HTML内容
        html_content = self._generate_summary_html(reports_info)
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ 测试总结报告生成完成: {summary_file}")
            return True
        except Exception as e:
            print(f"❌ 生成测试总结报告失败: {e}")
            return False
    
    def _collect_reports_info(self) -> Dict[str, Any]:
        """收集报告信息"""
        reports_info = {
            'generated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'reports': [],
            'coverage': None,
            'statistics': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0,
                'total_modules': 0,
                'test_coverage': 0.0
            }
        }
        
        # 收集HTML报告
        if self.html_dir.exists():
            for report_file in self.html_dir.glob('*.html'):
                if report_file.name != 'test_summary.html':
                    report_info = {
                        'name': report_file.stem.replace('_', ' ').title(),
                        'type': self._get_report_type(report_file.name),
                        'path': report_file.name,
                        'size': report_file.stat().st_size,
                        'modified': datetime.fromtimestamp(report_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    }
                    reports_info['reports'].append(report_info)
        
        # 收集JSON报告
        if self.json_dir.exists():
            for json_file in self.json_dir.glob('*.json'):
                json_info = self._parse_json_report(json_file)
                if json_info:
                    reports_info['statistics']['total_tests'] += json_info.get('total', 0)
                    reports_info['statistics']['passed_tests'] += json_info.get('passed', 0)
                    reports_info['statistics']['failed_tests'] += json_info.get('failed', 0)
                    reports_info['statistics']['skipped_tests'] += json_info.get('skipped', 0)
        
        # 收集覆盖率信息
        coverage_file = self.json_dir / 'coverage.json'
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r', encoding='utf-8') as f:
                    coverage_data = json.load(f)
                    reports_info['coverage'] = coverage_data
                    reports_info['statistics']['test_coverage'] = coverage_data.get('totals', {}).get('percent_covered', 0.0)
            except Exception as e:
                print(f"⚠️  解析覆盖率报告失败: {e}")
        
        # 统计模块数量
        regression_dir = self.tests_dir / 'regression'
        if regression_dir.exists():
            reports_info['statistics']['total_modules'] = len([
                item for item in regression_dir.iterdir() 
                if item.is_dir() and not item.name.startswith('.')
            ])
        
        return reports_info
    
    def _get_report_type(self, filename: str) -> str:
        """获取报告类型"""
        if 'unit' in filename:
            return '单元测试'
        elif 'api' in filename:
            return 'API测试'
        elif 'integration' in filename:
            return '集成测试'
        elif 'regression' in filename:
            return '回归测试'
        elif 'new_feature' in filename:
            return '新功能测试'
        elif 'full' in filename:
            return '完整测试套件'
        elif 'coverage' in filename:
            return '覆盖率报告'
        else:
            return '其他测试'
    
    def _parse_json_report(self, json_file: Path) -> Dict[str, Any]:
        """解析JSON报告文件"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'total': data.get('summary', {}).get('total', 0),
                    'passed': data.get('summary', {}).get('passed', 0),
                    'failed': data.get('summary', {}).get('failed', 0),
                    'skipped': data.get('summary', {}).get('skipped', 0),
                    'duration': data.get('summary', {}).get('duration', 0)
                }
        except Exception as e:
            print(f"⚠️  解析JSON报告失败 {json_file}: {e}")
            return None
    
    def _generate_summary_html(self, reports_info: Dict[str, Any]) -> str:
        """生成总结报告HTML内容"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alpha项目测试执行总结报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{ 
            font-size: 2.5rem; 
            margin-bottom: 10px; 
            font-weight: 700;
        }}
        .header p {{ 
            font-size: 1.1rem; 
            opacity: 0.9; 
        }}
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; 
            margin-bottom: 30px; 
        }}
        .stat-card {{ 
            background: white; 
            padding: 25px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .stat-value {{ 
            font-size: 2rem; 
            font-weight: 700; 
            color: #667eea; 
            margin-bottom: 5px; 
        }}
        .stat-label {{ 
            color: #666; 
            font-size: 0.9rem; 
            text-transform: uppercase; 
            letter-spacing: 0.5px; 
        }}
        .reports-section {{ 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px; 
        }}
        .reports-section h2 {{ 
            color: #333; 
            margin-bottom: 20px; 
            font-size: 1.5rem; 
        }}
        .report-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px; 
        }}
        .report-card {{ 
            border: 1px solid #e0e0e0; 
            border-radius: 8px; 
            padding: 20px; 
            transition: all 0.3s ease; 
        }}
        .report-card:hover {{ 
            border-color: #667eea; 
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2); 
        }}
        .report-name {{ 
            font-weight: 600; 
            color: #333; 
            margin-bottom: 8px; 
        }}
        .report-type {{ 
            color: #667eea; 
            font-size: 0.9rem; 
            margin-bottom: 8px; 
        }}
        .report-meta {{ 
            color: #666; 
            font-size: 0.8rem; 
        }}
        .report-link {{ 
            display: inline-block; 
            margin-top: 10px; 
            padding: 8px 16px; 
            background: #667eea; 
            color: white; 
            text-decoration: none; 
            border-radius: 5px; 
            font-size: 0.9rem; 
            transition: background 0.3s ease; 
        }}
        .report-link:hover {{ 
            background: #5a6fd8; 
        }}
        .coverage-section {{ 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px; 
        }}
        .coverage-bar {{ 
            background: #f0f0f0; 
            border-radius: 10px; 
            height: 20px; 
            overflow: hidden; 
            margin: 15px 0; 
        }}
        .coverage-fill {{ 
            background: linear-gradient(90deg, #667eea, #764ba2); 
            height: 100%; 
            border-radius: 10px; 
            transition: width 0.5s ease; 
        }}
        .footer {{ 
            text-align: center; 
            color: #666; 
            margin-top: 40px; 
            padding: 20px; 
            border-top: 1px solid #e0e0e0; 
        }}
        @media (max-width: 768px) {{
            .stats-grid {{ grid-template-columns: 1fr; }}
            .report-grid {{ grid-template-columns: 1fr; }}
            .header h1 {{ font-size: 2rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Alpha项目测试执行总结报告</h1>
            <p>生成时间: {reports_info['generated_time']}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{reports_info['statistics']['total_tests']}</div>
                <div class="stat-label">总测试数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{reports_info['statistics']['passed_tests']}</div>
                <div class="stat-label">通过测试</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{reports_info['statistics']['failed_tests']}</div>
                <div class="stat-label">失败测试</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{reports_info['statistics']['total_modules']}</div>
                <div class="stat-label">测试模块</div>
            </div>
        </div>
        
        <div class="coverage-section">
            <h2>📊 测试覆盖率</h2>
            <div class="coverage-bar">
                <div class="coverage-fill" style="width: {reports_info['statistics']['test_coverage']}%"></div>
            </div>
            <p>当前覆盖率: <strong>{reports_info['statistics']['test_coverage']:.1f}%</strong></p>
            <p>目标覆盖率: <strong>≥80%</strong></p>
        </div>
        
        <div class="reports-section">
            <h2>📋 详细测试报告</h2>
            <div class="report-grid">
                {self._generate_report_cards_html(reports_info['reports'])}
            </div>
        </div>
        
        <div class="footer">
            <p>本报告由Alpha项目测试系统自动生成</p>
            <p>如有问题，请联系开发团队</p>
        </div>
    </div>
    
    <script>
        // 添加一些交互效果
        document.addEventListener('DOMContentLoaded', function() {{
            // 为覆盖率条添加动画
            const coverageFill = document.querySelector('.coverage-fill');
            if (coverageFill) {{
                setTimeout(() => {{
                    coverageFill.style.width = '{reports_info['statistics']['test_coverage']}%';
                }}, 500);
            }}
            
            // 为统计卡片添加点击效果
            const statCards = document.querySelectorAll('.stat-card');
            statCards.forEach(card => {{
                card.addEventListener('click', function() {{
                    this.style.transform = 'scale(1.05)';
                    setTimeout(() => {{
                        this.style.transform = 'scale(1)';
                    }}, 200);
                }});
            }});
        }});
    </script>
</body>
</html>
        """
    
    def _generate_report_cards_html(self, reports: List[Dict[str, Any]]) -> str:
        """生成报告卡片HTML"""
        if not reports:
            return '<p>暂无测试报告</p>'
        
        cards_html = ''
        for report in reports:
            size_kb = report['size'] / 1024
            cards_html += f"""
                <div class="report-card">
                    <div class="report-name">{report['name']}</div>
                    <div class="report-type">{report['type']}</div>
                    <div class="report-meta">
                        大小: {size_kb:.1f} KB<br>
                        修改: {report['modified']}
                    </div>
                    <a href="{report['path']}" class="report-link" target="_blank">查看报告</a>
                </div>
            """
        
        return cards_html
    
    def generate_coverage_report(self):
        """生成覆盖率报告"""
        coverage_file = self.json_dir / 'coverage.json'
        if not coverage_file.exists():
            print("⚠️  覆盖率报告文件不存在")
            return False
        
        try:
            with open(coverage_file, 'r', encoding='utf-8') as f:
                coverage_data = json.load(f)
            
            # 生成覆盖率HTML报告
            coverage_html = self._generate_coverage_html(coverage_data)
            coverage_report_file = self.html_dir / 'coverage_report.html'
            
            with open(coverage_report_file, 'w', encoding='utf-8') as f:
                f.write(coverage_html)
            
            print(f"✅ 覆盖率报告生成完成: {coverage_report_file}")
            return True
            
        except Exception as e:
            print(f"❌ 生成覆盖率报告失败: {e}")
            return False
    
    def _generate_coverage_html(self, coverage_data: Dict[str, Any]) -> str:
        """生成覆盖率HTML报告"""
        totals = coverage_data.get('totals', {})
        files = coverage_data.get('files', {})
        
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alpha项目代码覆盖率报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .coverage-summary {{ margin: 20px 0; }}
        .file-list {{ margin: 20px 0; }}
        .file-item {{ padding: 10px; border-bottom: 1px solid #eee; }}
        .coverage-bar {{ background: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden; }}
        .coverage-fill {{ background: #4CAF50; height: 100%; transition: width 0.5s ease; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Alpha项目代码覆盖率报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="coverage-summary">
        <h2>总体覆盖率</h2>
        <div class="coverage-bar">
            <div class="coverage-fill" style="width: {totals.get('percent_covered', 0)}%"></div>
        </div>
        <p>覆盖率: {totals.get('percent_covered', 0):.1f}%</p>
        <p>总行数: {totals.get('num_statements', 0)}</p>
        <p>覆盖行数: {totals.get('covered_statements', 0)}</p>
        <p>缺失行数: {totals.get('missing_statements', 0)}</p>
    </div>
    
    <div class="file-list">
        <h2>文件覆盖率详情</h2>
        {self._generate_file_coverage_html(files)}
    </div>
</body>
</html>
        """
    
    def _generate_file_coverage_html(self, files: Dict[str, Any]) -> str:
        """生成文件覆盖率HTML"""
        if not files:
            return '<p>暂无文件覆盖率信息</p>'
        
        files_html = ''
        for file_path, file_data in files.items():
            percent_covered = file_data.get('summary', {}).get('percent_covered', 0)
            files_html += f"""
                <div class="file-item">
                    <strong>{file_path}</strong><br>
                    <div class="coverage-bar" style="width: 200px;">
                        <div class="coverage-fill" style="width: {percent_covered}%"></div>
                    </div>
                    覆盖率: {percent_covered:.1f}%
                </div>
            """
        
        return files_html


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    generator = TestReportGenerator(project_root)
    
    print("📊 开始生成测试报告...")
    
    # 生成总结报告
    success1 = generator.generate_summary_report()
    
    # 生成覆盖率报告
    success2 = generator.generate_coverage_report()
    
    if success1 and success2:
        print("✅ 所有测试报告生成完成！")
        return True
    else:
        print("⚠️  部分测试报告生成失败")
        return False


if __name__ == '__main__':
    main()
"""
测试报告生成工具
用于生成和汇总测试报告
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tests_dir = project_root / 'tests'
        self.reports_dir = self.tests_dir / 'reports'
        self.html_dir = self.reports_dir / 'html'
        self.json_dir = self.reports_dir / 'json'
    
    def generate_summary_report(self):
        """生成测试总结报告"""
        summary_file = self.html_dir / 'test_summary.html'
        
        # 收集报告信息
        reports_info = self._collect_reports_info()
        
        # 生成HTML内容
        html_content = self._generate_summary_html(reports_info)
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ 测试总结报告生成完成: {summary_file}")
            return True
        except Exception as e:
            print(f"❌ 生成测试总结报告失败: {e}")
            return False
    
    def _collect_reports_info(self) -> Dict[str, Any]:
        """收集报告信息"""
        reports_info = {
            'generated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'reports': [],
            'coverage': None,
            'statistics': {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'skipped_tests': 0,
                'total_modules': 0,
                'test_coverage': 0.0
            }
        }
        
        # 收集HTML报告
        if self.html_dir.exists():
            for report_file in self.html_dir.glob('*.html'):
                if report_file.name != 'test_summary.html':
                    report_info = {
                        'name': report_file.stem.replace('_', ' ').title(),
                        'type': self._get_report_type(report_file.name),
                        'path': report_file.name,
                        'size': report_file.stat().st_size,
                        'modified': datetime.fromtimestamp(report_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    }
                    reports_info['reports'].append(report_info)
        
        # 收集JSON报告
        if self.json_dir.exists():
            for json_file in self.json_dir.glob('*.json'):
                json_info = self._parse_json_report(json_file)
                if json_info:
                    reports_info['statistics']['total_tests'] += json_info.get('total', 0)
                    reports_info['statistics']['passed_tests'] += json_info.get('passed', 0)
                    reports_info['statistics']['failed_tests'] += json_info.get('failed', 0)
                    reports_info['statistics']['skipped_tests'] += json_info.get('skipped', 0)
        
        # 收集覆盖率信息
        coverage_file = self.json_dir / 'coverage.json'
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r', encoding='utf-8') as f:
                    coverage_data = json.load(f)
                    reports_info['coverage'] = coverage_data
                    reports_info['statistics']['test_coverage'] = coverage_data.get('totals', {}).get('percent_covered', 0.0)
            except Exception as e:
                print(f"⚠️  解析覆盖率报告失败: {e}")
        
        # 统计模块数量
        regression_dir = self.tests_dir / 'regression'
        if regression_dir.exists():
            reports_info['statistics']['total_modules'] = len([
                item for item in regression_dir.iterdir() 
                if item.is_dir() and not item.name.startswith('.')
            ])
        
        return reports_info
    
    def _get_report_type(self, filename: str) -> str:
        """获取报告类型"""
        if 'unit' in filename:
            return '单元测试'
        elif 'api' in filename:
            return 'API测试'
        elif 'integration' in filename:
            return '集成测试'
        elif 'regression' in filename:
            return '回归测试'
        elif 'new_feature' in filename:
            return '新功能测试'
        elif 'full' in filename:
            return '完整测试套件'
        elif 'coverage' in filename:
            return '覆盖率报告'
        else:
            return '其他测试'
    
    def _parse_json_report(self, json_file: Path) -> Dict[str, Any]:
        """解析JSON报告文件"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'total': data.get('summary', {}).get('total', 0),
                    'passed': data.get('summary', {}).get('passed', 0),
                    'failed': data.get('summary', {}).get('failed', 0),
                    'skipped': data.get('summary', {}).get('skipped', 0),
                    'duration': data.get('summary', {}).get('duration', 0)
                }
        except Exception as e:
            print(f"⚠️  解析JSON报告失败 {json_file}: {e}")
            return None
    
    def _generate_summary_html(self, reports_info: Dict[str, Any]) -> str:
        """生成总结报告HTML内容"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alpha项目测试执行总结报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{ 
            font-size: 2.5rem; 
            margin-bottom: 10px; 
            font-weight: 700;
        }}
        .header p {{ 
            font-size: 1.1rem; 
            opacity: 0.9; 
        }}
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px; 
            margin-bottom: 30px; 
        }}
        .stat-card {{ 
            background: white; 
            padding: 25px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        .stat-value {{ 
            font-size: 2rem; 
            font-weight: 700; 
            color: #667eea; 
            margin-bottom: 5px; 
        }}
        .stat-label {{ 
            color: #666; 
            font-size: 0.9rem; 
            text-transform: uppercase; 
            letter-spacing: 0.5px; 
        }}
        .reports-section {{ 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px; 
        }}
        .reports-section h2 {{ 
            color: #333; 
            margin-bottom: 20px; 
            font-size: 1.5rem; 
        }}
        .report-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px; 
        }}
        .report-card {{ 
            border: 1px solid #e0e0e0; 
            border-radius: 8px; 
            padding: 20px; 
            transition: all 0.3s ease; 
        }}
        .report-card:hover {{ 
            border-color: #667eea; 
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2); 
        }}
        .report-name {{ 
            font-weight: 600; 
            color: #333; 
            margin-bottom: 8px; 
        }}
        .report-type {{ 
            color: #667eea; 
            font-size: 0.9rem; 
            margin-bottom: 8px; 
        }}
        .report-meta {{ 
            color: #666; 
            font-size: 0.8rem; 
        }}
        .report-link {{ 
            display: inline-block; 
            margin-top: 10px; 
            padding: 8px 16px; 
            background: #667eea; 
            color: white; 
            text-decoration: none; 
            border-radius: 5px; 
            font-size: 0.9rem; 
            transition: background 0.3s ease; 
        }}
        .report-link:hover {{ 
            background: #5a6fd8; 
        }}
        .coverage-section {{ 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px; 
        }}
        .coverage-bar {{ 
            background: #f0f0f0; 
            border-radius: 10px; 
            height: 20px; 
            overflow: hidden; 
            margin: 15px 0; 
        }}
        .coverage-fill {{ 
            background: linear-gradient(90deg, #667eea, #764ba2); 
            height: 100%; 
            border-radius: 10px; 
            transition: width 0.5s ease; 
        }}
        .footer {{ 
            text-align: center; 
            color: #666; 
            margin-top: 40px; 
            padding: 20px; 
            border-top: 1px solid #e0e0e0; 
        }}
        @media (max-width: 768px) {{
            .stats-grid {{ grid-template-columns: 1fr; }}
            .report-grid {{ grid-template-columns: 1fr; }}
            .header h1 {{ font-size: 2rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Alpha项目测试执行总结报告</h1>
            <p>生成时间: {reports_info['generated_time']}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{reports_info['statistics']['total_tests']}</div>
                <div class="stat-label">总测试数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{reports_info['statistics']['passed_tests']}</div>
                <div class="stat-label">通过测试</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{reports_info['statistics']['failed_tests']}</div>
                <div class="stat-label">失败测试</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{reports_info['statistics']['total_modules']}</div>
                <div class="stat-label">测试模块</div>
            </div>
        </div>
        
        <div class="coverage-section">
            <h2>📊 测试覆盖率</h2>
            <div class="coverage-bar">
                <div class="coverage-fill" style="width: {reports_info['statistics']['test_coverage']}%"></div>
            </div>
            <p>当前覆盖率: <strong>{reports_info['statistics']['test_coverage']:.1f}%</strong></p>
            <p>目标覆盖率: <strong>≥80%</strong></p>
        </div>
        
        <div class="reports-section">
            <h2>📋 详细测试报告</h2>
            <div class="report-grid">
                {self._generate_report_cards_html(reports_info['reports'])}
            </div>
        </div>
        
        <div class="footer">
            <p>本报告由Alpha项目测试系统自动生成</p>
            <p>如有问题，请联系开发团队</p>
        </div>
    </div>
    
    <script>
        // 添加一些交互效果
        document.addEventListener('DOMContentLoaded', function() {{
            // 为覆盖率条添加动画
            const coverageFill = document.querySelector('.coverage-fill');
            if (coverageFill) {{
                setTimeout(() => {{
                    coverageFill.style.width = '{reports_info['statistics']['test_coverage']}%';
                }}, 500);
            }}
            
            // 为统计卡片添加点击效果
            const statCards = document.querySelectorAll('.stat-card');
            statCards.forEach(card => {{
                card.addEventListener('click', function() {{
                    this.style.transform = 'scale(1.05)';
                    setTimeout(() => {{
                        this.style.transform = 'scale(1)';
                    }}, 200);
                }});
            }});
        }});
    </script>
</body>
</html>
        """
    
    def _generate_report_cards_html(self, reports: List[Dict[str, Any]]) -> str:
        """生成报告卡片HTML"""
        if not reports:
            return '<p>暂无测试报告</p>'
        
        cards_html = ''
        for report in reports:
            size_kb = report['size'] / 1024
            cards_html += f"""
                <div class="report-card">
                    <div class="report-name">{report['name']}</div>
                    <div class="report-type">{report['type']}</div>
                    <div class="report-meta">
                        大小: {size_kb:.1f} KB<br>
                        修改: {report['modified']}
                    </div>
                    <a href="{report['path']}" class="report-link" target="_blank">查看报告</a>
                </div>
            """
        
        return cards_html
    
    def generate_coverage_report(self):
        """生成覆盖率报告"""
        coverage_file = self.json_dir / 'coverage.json'
        if not coverage_file.exists():
            print("⚠️  覆盖率报告文件不存在")
            return False
        
        try:
            with open(coverage_file, 'r', encoding='utf-8') as f:
                coverage_data = json.load(f)
            
            # 生成覆盖率HTML报告
            coverage_html = self._generate_coverage_html(coverage_data)
            coverage_report_file = self.html_dir / 'coverage_report.html'
            
            with open(coverage_report_file, 'w', encoding='utf-8') as f:
                f.write(coverage_html)
            
            print(f"✅ 覆盖率报告生成完成: {coverage_report_file}")
            return True
            
        except Exception as e:
            print(f"❌ 生成覆盖率报告失败: {e}")
            return False
    
    def _generate_coverage_html(self, coverage_data: Dict[str, Any]) -> str:
        """生成覆盖率HTML报告"""
        totals = coverage_data.get('totals', {})
        files = coverage_data.get('files', {})
        
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alpha项目代码覆盖率报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .coverage-summary {{ margin: 20px 0; }}
        .file-list {{ margin: 20px 0; }}
        .file-item {{ padding: 10px; border-bottom: 1px solid #eee; }}
        .coverage-bar {{ background: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden; }}
        .coverage-fill {{ background: #4CAF50; height: 100%; transition: width 0.5s ease; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Alpha项目代码覆盖率报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="coverage-summary">
        <h2>总体覆盖率</h2>
        <div class="coverage-bar">
            <div class="coverage-fill" style="width: {totals.get('percent_covered', 0)}%"></div>
        </div>
        <p>覆盖率: {totals.get('percent_covered', 0):.1f}%</p>
        <p>总行数: {totals.get('num_statements', 0)}</p>
        <p>覆盖行数: {totals.get('covered_statements', 0)}</p>
        <p>缺失行数: {totals.get('missing_statements', 0)}</p>
    </div>
    
    <div class="file-list">
        <h2>文件覆盖率详情</h2>
        {self._generate_file_coverage_html(files)}
    </div>
</body>
</html>
        """
    
    def _generate_file_coverage_html(self, files: Dict[str, Any]) -> str:
        """生成文件覆盖率HTML"""
        if not files:
            return '<p>暂无文件覆盖率信息</p>'
        
        files_html = ''
        for file_path, file_data in files.items():
            percent_covered = file_data.get('summary', {}).get('percent_covered', 0)
            files_html += f"""
                <div class="file-item">
                    <strong>{file_path}</strong><br>
                    <div class="coverage-bar" style="width: 200px;">
                        <div class="coverage-fill" style="width: {percent_covered}%"></div>
                    </div>
                    覆盖率: {percent_covered:.1f}%
                </div>
            """
        
        return files_html


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent.parent
    generator = TestReportGenerator(project_root)
    
    print("📊 开始生成测试报告...")
    
    # 生成总结报告
    success1 = generator.generate_summary_report()
    
    # 生成覆盖率报告
    success2 = generator.generate_coverage_report()
    
    if success1 and success2:
        print("✅ 所有测试报告生成完成！")
        return True
    else:
        print("⚠️  部分测试报告生成失败")
        return False


if __name__ == '__main__':
    main()
