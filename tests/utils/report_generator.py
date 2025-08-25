"""
测试报告生成器

生成详细的测试报告，包括：
1. HTML格式的测试报告
2. 覆盖率报告
3. 性能分析报告
4. 测试趋势分析
5. 失败分析报告
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import xml.etree.ElementTree as ET
from jinja2 import Template
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


@dataclass
class TestResult:
    """测试结果数据结构"""
    name: str
    status: str  # passed, failed, skipped, error
    duration: float
    file_path: str
    line_number: int = 0
    error_message: str = ""
    error_traceback: str = ""
    tags: List[str] = None


@dataclass
class TestSuite:
    """测试套件结果"""
    name: str
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    tests: List[TestResult]


@dataclass
class TestSession:
    """测试会话结果"""
    timestamp: datetime
    duration: float
    total_tests: int
    passed: int
    failed: int
    skipped: int
    errors: int
    pass_rate: float
    suites: List[TestSuite]
    environment: Dict[str, str]
    coverage: Optional[Dict[str, Any]] = None


class TestReportGenerator:
    """测试报告生成器"""
    
    def __init__(self, output_dir: str = "tests/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置样式
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def parse_junit_xml(self, xml_path: str) -> TestSession:
        """解析JUnit XML报告"""
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # 解析测试套件
        suites = []
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_errors = 0
        total_duration = 0.0
        
        for testsuite in root.findall('.//testsuite'):
            suite_name = testsuite.get('name', 'Unknown')
            suite_tests = int(testsuite.get('tests', 0))
            suite_failures = int(testsuite.get('failures', 0))
            suite_errors = int(testsuite.get('errors', 0))
            suite_skipped = int(testsuite.get('skipped', 0))
            suite_time = float(testsuite.get('time', 0))
            
            suite_passed = suite_tests - suite_failures - suite_errors - suite_skipped
            
            # 解析测试用例
            tests = []
            for testcase in testsuite.findall('.//testcase'):
                test_name = testcase.get('name', 'Unknown')
                test_file = testcase.get('file', '')
                test_line = int(testcase.get('line', 0))
                test_time = float(testcase.get('time', 0))
                
                # 确定测试状态
                if testcase.find('failure') is not None:
                    status = 'failed'
                    failure = testcase.find('failure')
                    error_msg = failure.get('message', '')
                    error_trace = failure.text or ''
                elif testcase.find('error') is not None:
                    status = 'error'
                    error = testcase.find('error')
                    error_msg = error.get('message', '')
                    error_trace = error.text or ''
                elif testcase.find('skipped') is not None:
                    status = 'skipped'
                    error_msg = ''
                    error_trace = ''
                else:
                    status = 'passed'
                    error_msg = ''
                    error_trace = ''
                
                test_result = TestResult(
                    name=test_name,
                    status=status,
                    duration=test_time,
                    file_path=test_file,
                    line_number=test_line,
                    error_message=error_msg,
                    error_traceback=error_trace
                )
                tests.append(test_result)
            
            suite = TestSuite(
                name=suite_name,
                total_tests=suite_tests,
                passed=suite_passed,
                failed=suite_failures,
                skipped=suite_skipped,
                errors=suite_errors,
                duration=suite_time,
                tests=tests
            )
            suites.append(suite)
            
            # 累计统计
            total_tests += suite_tests
            total_passed += suite_passed
            total_failed += suite_failures
            total_skipped += suite_skipped
            total_errors += suite_errors
            total_duration += suite_time
        
        # 创建测试会话
        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        session = TestSession(
            timestamp=datetime.now(),
            duration=total_duration,
            total_tests=total_tests,
            passed=total_passed,
            failed=total_failed,
            skipped=total_skipped,
            errors=total_errors,
            pass_rate=pass_rate,
            suites=suites,
            environment=self._get_environment_info()
        )
        
        return session
    
    def _get_environment_info(self) -> Dict[str, str]:
        """获取环境信息"""
        import platform
        import sys
        import django
        
        return {
            'python_version': sys.version,
            'platform': platform.platform(),
            'django_version': django.get_version(),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_html_report(self, session: TestSession, 
                           template_name: str = "test_report.html") -> str:
        """生成HTML测试报告"""
        
        # HTML模板
        html_template = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>测试报告 - {{ session.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</title>
            <style>
                body { font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #eee; }
                .header h1 { color: #333; margin: 0; }
                .header .subtitle { color: #666; font-size: 14px; margin-top: 5px; }
                
                .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
                .metric { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
                .metric.passed { background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); }
                .metric.failed { background: linear-gradient(135deg, #f44336 0%, #da190b 100%); }
                .metric.skipped { background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); }
                .metric h3 { margin: 0 0 10px 0; font-size: 24px; }
                .metric p { margin: 0; font-size: 14px; opacity: 0.9; }
                
                .progress-bar { background: #e0e0e0; border-radius: 10px; overflow: hidden; height: 20px; margin: 20px 0; }
                .progress-fill { height: 100%; background: linear-gradient(90deg, #4CAF50, #45a049); transition: width 0.3s ease; }
                
                .suites { margin-top: 30px; }
                .suite { margin-bottom: 25px; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; }
                .suite-header { background: #f8f9fa; padding: 15px; border-bottom: 1px solid #ddd; cursor: pointer; }
                .suite-header:hover { background: #e9ecef; }
                .suite-header h3 { margin: 0; color: #333; }
                .suite-stats { font-size: 14px; color: #666; margin-top: 5px; }
                
                .tests { display: none; }
                .tests.expanded { display: block; }
                .test { padding: 10px 15px; border-bottom: 1px solid #eee; }
                .test:last-child { border-bottom: none; }
                .test.passed { border-left: 4px solid #4CAF50; }
                .test.failed { border-left: 4px solid #f44336; background: #fff5f5; }
                .test.skipped { border-left: 4px solid #ff9800; }
                .test.error { border-left: 4px solid #9c27b0; background: #fdf4ff; }
                
                .test-name { font-weight: 600; color: #333; }
                .test-info { font-size: 12px; color: #666; margin-top: 5px; }
                .test-error { background: #f8f8f8; padding: 10px; margin-top: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; overflow-x: auto; }
                
                .charts { margin-top: 30px; display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
                .chart { text-align: center; }
                .chart img { max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
                
                .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 12px; }
                
                @media (max-width: 768px) {
                    .container { padding: 15px; }
                    .summary { grid-template-columns: 1fr 1fr; }
                    .charts { grid-template-columns: 1fr; }
                }
            </style>
            <script>
                function toggleSuite(suiteId) {
                    const tests = document.getElementById('tests-' + suiteId);
                    tests.classList.toggle('expanded');
                }
            </script>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧪 测试报告</h1>
                    <div class="subtitle">{{ session.timestamp.strftime('%Y年%m月%d日 %H:%M:%S') }} | 执行时间: {{ "%.2f"|format(session.duration) }}秒</div>
                </div>
                
                <div class="summary">
                    <div class="metric">
                        <h3>{{ session.total_tests }}</h3>
                        <p>总测试数</p>
                    </div>
                    <div class="metric passed">
                        <h3>{{ session.passed }}</h3>
                        <p>通过</p>
                    </div>
                    <div class="metric failed">
                        <h3>{{ session.failed + session.errors }}</h3>
                        <p>失败</p>
                    </div>
                    <div class="metric skipped">
                        <h3>{{ session.skipped }}</h3>
                        <p>跳过</p>
                    </div>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ session.pass_rate }}%"></div>
                </div>
                <div style="text-align: center; margin-top: 10px; font-weight: 600; color: #333;">
                    通过率: {{ "%.1f"|format(session.pass_rate) }}%
                </div>
                
                <div class="suites">
                    <h2>📋 测试套件详情</h2>
                    {% for suite in session.suites %}
                    <div class="suite">
                        <div class="suite-header" onclick="toggleSuite({{ loop.index }})">
                            <h3>{{ suite.name }}</h3>
                            <div class="suite-stats">
                                {{ suite.total_tests }}个测试 | 
                                ✅ {{ suite.passed }}个通过 | 
                                ❌ {{ suite.failed + suite.errors }}个失败 | 
                                ⏭️ {{ suite.skipped }}个跳过 | 
                                ⏱️ {{ "%.2f"|format(suite.duration) }}秒
                            </div>
                        </div>
                        <div id="tests-{{ loop.index }}" class="tests">
                            {% for test in suite.tests %}
                            <div class="test {{ test.status }}">
                                <div class="test-name">{{ test.name }}</div>
                                <div class="test-info">
                                    📁 {{ test.file_path }} | ⏱️ {{ "%.3f"|format(test.duration) }}秒
                                    {% if test.line_number > 0 %} | 📍 第{{ test.line_number }}行{% endif %}
                                </div>
                                {% if test.error_message %}
                                <div class="test-error">
                                    <strong>错误信息:</strong><br>
                                    {{ test.error_message }}<br>
                                    {% if test.error_traceback %}
                                    <br><strong>错误堆栈:</strong><br>
                                    <pre>{{ test.error_traceback }}</pre>
                                    {% endif %}
                                </div>
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
                
                <div class="footer">
                    <p>🐍 Python {{ session.environment.python_version.split()[0] }} | 🌐 {{ session.environment.platform }} | 🎯 Django {{ session.environment.django_version }}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 渲染模板
        template = Template(html_template)
        html_content = template.render(session=session)
        
        # 保存文件
        timestamp = session.timestamp.strftime('%Y%m%d_%H%M%S')
        filename = f"test_report_{timestamp}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def generate_charts(self, session: TestSession) -> Dict[str, str]:
        """生成测试图表"""
        charts = {}
        
        # 1. 测试结果饼图
        fig, ax = plt.subplots(figsize=(8, 6))
        labels = ['通过', '失败', '跳过', '错误']
        sizes = [session.passed, session.failed, session.skipped, session.errors]
        colors = ['#4CAF50', '#f44336', '#ff9800', '#9c27b0']
        
        # 只显示非零的部分
        non_zero = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
        if non_zero:
            labels, sizes, colors = zip(*non_zero)
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.set_title('测试结果分布', fontsize=16, fontweight='bold', pad=20)
            
            # 美化文本
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        
        plt.tight_layout()
        pie_chart_path = self.output_dir / f"test_results_pie_{int(time.time())}.png"
        plt.savefig(pie_chart_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        charts['pie_chart'] = str(pie_chart_path)
        
        # 2. 测试套件性能条形图
        if len(session.suites) > 1:
            fig, ax = plt.subplots(figsize=(10, 6))
            suite_names = [suite.name[:30] + '...' if len(suite.name) > 30 else suite.name for suite in session.suites]
            durations = [suite.duration for suite in session.suites]
            
            bars = ax.barh(suite_names, durations, color='skyblue', alpha=0.7)
            ax.set_xlabel('执行时间 (秒)', fontsize=12)
            ax.set_title('测试套件执行时间', fontsize=16, fontweight='bold', pad=20)
            
            # 添加数值标签
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                       f'{width:.2f}s', ha='left', va='center', fontsize=10)
            
            plt.tight_layout()
            bar_chart_path = self.output_dir / f"suite_performance_{int(time.time())}.png"
            plt.savefig(bar_chart_path, dpi=300, bbox_inches='tight', facecolor='white')
            plt.close()
            charts['bar_chart'] = str(bar_chart_path)
        
        return charts
    
    def generate_coverage_report(self, coverage_data: Dict[str, Any]) -> str:
        """生成覆盖率报告"""
        if not coverage_data:
            return ""
        
        # 生成覆盖率图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 总体覆盖率
        total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
        ax1.pie([total_coverage, 100-total_coverage], 
                labels=['已覆盖', '未覆盖'],
                colors=['#4CAF50', '#f44336'],
                autopct='%1.1f%%',
                startangle=90)
        ax1.set_title(f'总体覆盖率: {total_coverage:.1f}%', fontsize=14, fontweight='bold')
        
        # 文件覆盖率分布
        files = coverage_data.get('files', {})
        if files:
            file_coverages = [file_data.get('summary', {}).get('percent_covered', 0) 
                            for file_data in files.values()]
            ax2.hist(file_coverages, bins=20, color='skyblue', alpha=0.7, edgecolor='black')
            ax2.set_xlabel('覆盖率 (%)')
            ax2.set_ylabel('文件数量')
            ax2.set_title('文件覆盖率分布', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        coverage_chart_path = self.output_dir / f"coverage_report_{int(time.time())}.png"
        plt.savefig(coverage_chart_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(coverage_chart_path)
    
    def generate_trend_analysis(self, history_file: str = "test_history.json") -> str:
        """生成测试趋势分析"""
        history_path = self.output_dir / history_file
        
        if not history_path.exists():
            return ""
        
        # 读取历史数据
        with open(history_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if len(history) < 2:
            return ""
        
        # 创建趋势图
        df = pd.DataFrame(history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 通过率趋势
        ax1.plot(df['timestamp'], df['pass_rate'], marker='o', linewidth=2, markersize=6, color='#4CAF50')
        ax1.set_title('通过率趋势', fontsize=14, fontweight='bold')
        ax1.set_ylabel('通过率 (%)')
        ax1.grid(True, alpha=0.3)
        
        # 测试数量趋势
        ax2.plot(df['timestamp'], df['total_tests'], marker='s', linewidth=2, markersize=6, color='#2196F3')
        ax2.set_title('测试数量趋势', fontsize=14, fontweight='bold')
        ax2.set_ylabel('测试数量')
        ax2.grid(True, alpha=0.3)
        
        # 执行时间趋势
        ax3.plot(df['timestamp'], df['duration'], marker='^', linewidth=2, markersize=6, color='#ff9800')
        ax3.set_title('执行时间趋势', fontsize=14, fontweight='bold')
        ax3.set_ylabel('执行时间 (秒)')
        ax3.grid(True, alpha=0.3)
        
        # 失败测试趋势
        ax4.plot(df['timestamp'], df['failed'], marker='d', linewidth=2, markersize=6, color='#f44336')
        ax4.set_title('失败测试趋势', fontsize=14, fontweight='bold')
        ax4.set_ylabel('失败数量')
        ax4.grid(True, alpha=0.3)
        
        # 旋转x轴标签
        for ax in [ax1, ax2, ax3, ax4]:
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        trend_chart_path = self.output_dir / f"test_trends_{int(time.time())}.png"
        plt.savefig(trend_chart_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(trend_chart_path)
    
    def save_test_history(self, session: TestSession, history_file: str = "test_history.json"):
        """保存测试历史数据"""
        history_path = self.output_dir / history_file
        
        # 读取现有历史
        history = []
        if history_path.exists():
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        # 添加新记录
        record = {
            'timestamp': session.timestamp.isoformat(),
            'total_tests': session.total_tests,
            'passed': session.passed,
            'failed': session.failed,
            'skipped': session.skipped,
            'errors': session.errors,
            'pass_rate': session.pass_rate,
            'duration': session.duration
        }
        history.append(record)
        
        # 保留最近100条记录
        history = history[-100:]
        
        # 保存历史
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def generate_complete_report(self, xml_path: str, coverage_data: Optional[Dict] = None) -> str:
        """生成完整的测试报告"""
        # 解析测试结果
        session = self.parse_junit_xml(xml_path)
        
        # 添加覆盖率数据
        if coverage_data:
            session.coverage = coverage_data
        
        # 生成图表
        charts = self.generate_charts(session)
        
        # 生成覆盖率图表
        if coverage_data:
            coverage_chart = self.generate_coverage_report(coverage_data)
            if coverage_chart:
                charts['coverage_chart'] = coverage_chart
        
        # 生成趋势分析
        trend_chart = self.generate_trend_analysis()
        if trend_chart:
            charts['trend_chart'] = trend_chart
        
        # 生成HTML报告
        html_report = self.generate_html_report(session)
        
        # 保存测试历史
        self.save_test_history(session)
        
        print(f"✅ 测试报告生成完成: {html_report}")
        return html_report


# 便捷函数
def generate_test_report(xml_path: str, output_dir: str = "tests/reports", 
                        coverage_data: Optional[Dict] = None) -> str:
    """便捷函数：生成测试报告"""
    generator = TestReportGenerator(output_dir)
    return generator.generate_complete_report(xml_path, coverage_data)


print("✅ 测试报告生成器创建完成")