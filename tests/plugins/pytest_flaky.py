#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest插件：处理flaky测试的复跑与隔离机制

功能：
1. 自动重试失败的测试用例
2. 统计测试稳定性
3. 隔离不稳定的测试用例
4. 生成flaky测试报告
"""

import json
import os
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pytest
from _pytest.config import Config
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.runner import CallInfo


class FlakyTestTracker:
    """Flaky测试追踪器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.test_results: Dict[str, List[str]] = defaultdict(list)
        self.test_times: Dict[str, List[float]] = defaultdict(list)
        self.retry_counts: Dict[str, int] = defaultdict(int)
        self.max_retries = config.getoption("--flaky-max-retries", default=3)
        self.flaky_threshold = config.getoption("--flaky-threshold", default=0.8)
        self.report_dir = Path(config.getoption("--flaky-report-dir", default="tests/reports/flaky"))
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载历史数据
        self.history_file = self.report_dir / "flaky_history.json"
        self.load_history()
    
    def load_history(self):
        """加载历史flaky测试数据"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.test_results.update(data.get('test_results', {}))
                    self.test_times.update(data.get('test_times', {}))
            except Exception as e:
                print(f"Warning: Failed to load flaky test history: {e}")
    
    def save_history(self):
        """保存历史数据"""
        try:
            data = {
                'test_results': dict(self.test_results),
                'test_times': dict(self.test_times),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save flaky test history: {e}")
    
    def should_retry(self, nodeid: str) -> bool:
        """判断是否应该重试"""
        return self.retry_counts[nodeid] < self.max_retries
    
    def record_result(self, nodeid: str, outcome: str, duration: float):
        """记录测试结果"""
        self.test_results[nodeid].append(outcome)
        self.test_times[nodeid].append(duration)
        
        # 只保留最近50次结果
        if len(self.test_results[nodeid]) > 50:
            self.test_results[nodeid] = self.test_results[nodeid][-50:]
            self.test_times[nodeid] = self.test_times[nodeid][-50:]
    
    def is_flaky(self, nodeid: str) -> bool:
        """判断测试是否为flaky"""
        results = self.test_results.get(nodeid, [])
        if len(results) < 5:  # 至少需要5次运行记录
            return False
        
        success_rate = results.count('passed') / len(results)
        return success_rate < self.flaky_threshold and success_rate > 0
    
    def get_flaky_tests(self) -> List[Dict]:
        """获取所有flaky测试"""
        flaky_tests = []
        for nodeid in self.test_results:
            if self.is_flaky(nodeid):
                results = self.test_results[nodeid]
                times = self.test_times[nodeid]
                success_rate = results.count('passed') / len(results)
                avg_time = sum(times) / len(times) if times else 0
                
                flaky_tests.append({
                    'nodeid': nodeid,
                    'success_rate': success_rate,
                    'total_runs': len(results),
                    'avg_duration': avg_time,
                    'recent_results': results[-10:],
                    'last_run': datetime.now().isoformat()
                })
        
        return sorted(flaky_tests, key=lambda x: x['success_rate'])
    
    def generate_report(self):
        """生成flaky测试报告"""
        flaky_tests = self.get_flaky_tests()
        
        # JSON报告
        json_report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_flaky_tests': len(flaky_tests),
                'threshold': self.flaky_threshold,
                'max_retries': self.max_retries
            },
            'flaky_tests': flaky_tests
        }
        
        json_file = self.report_dir / f"flaky_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2, ensure_ascii=False)
        
        # HTML报告
        html_content = self._generate_html_report(flaky_tests)
        html_file = self.report_dir / "flaky_report.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n=== Flaky Test Report ===")
        print(f"Total flaky tests: {len(flaky_tests)}")
        print(f"Report saved to: {html_file}")
        
        if flaky_tests:
            print("\nTop 5 most unstable tests:")
            for test in flaky_tests[:5]:
                print(f"  - {test['nodeid']} (success rate: {test['success_rate']:.2%})")
    
    def _generate_html_report(self, flaky_tests: List[Dict]) -> str:
        """生成HTML报告"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Flaky Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .test-item {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .flaky {{ background: #fff3cd; border-color: #ffeaa7; }}
        .stable {{ background: #d4edda; border-color: #c3e6cb; }}
        .success-rate {{ font-weight: bold; }}
        .low {{ color: #dc3545; }}
        .medium {{ color: #fd7e14; }}
        .high {{ color: #28a745; }}
    </style>
</head>
<body>
    <h1>Flaky Test Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total flaky tests: {len(flaky_tests)}</p>
        <p>Flaky threshold: {self.flaky_threshold:.0%}</p>
        <p>Max retries: {self.max_retries}</p>
    </div>
    
    <h2>Flaky Tests</h2>
"""
        
        if not flaky_tests:
            html += "<p>No flaky tests detected! 🎉</p>"
        else:
            for test in flaky_tests:
                success_rate = test['success_rate']
                rate_class = 'low' if success_rate < 0.5 else 'medium' if success_rate < 0.8 else 'high'
                
                html += f"""
    <div class="test-item flaky">
        <h3>{test['nodeid']}</h3>
        <p>Success Rate: <span class="success-rate {rate_class}">{success_rate:.2%}</span></p>
        <p>Total Runs: {test['total_runs']}</p>
        <p>Average Duration: {test['avg_duration']:.2f}s</p>
        <p>Recent Results: {' '.join(test['recent_results'])}</p>
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html


# 全局tracker实例
tracker: Optional[FlakyTestTracker] = None


def pytest_addoption(parser):
    """添加命令行选项"""
    group = parser.getgroup("flaky", "Flaky test handling")
    group.addoption(
        "--flaky-max-retries",
        type=int,
        default=3,
        help="Maximum number of retries for failed tests (default: 3)"
    )
    group.addoption(
        "--flaky-threshold",
        type=float,
        default=0.8,
        help="Success rate threshold below which a test is considered flaky (default: 0.8)"
    )
    group.addoption(
        "--flaky-report-dir",
        type=str,
        default="tests/reports/flaky",
        help="Directory to save flaky test reports (default: tests/reports/flaky)"
    )
    group.addoption(
        "--flaky-isolate",
        action="store_true",
        help="Skip known flaky tests"
    )


def pytest_configure(config):
    """配置插件"""
    global tracker
    tracker = FlakyTestTracker(config)
    
    # 注册标记
    config.addinivalue_line(
        "markers", "flaky: mark test as potentially flaky"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    if config.getoption("--flaky-isolate"):
        # 跳过已知的flaky测试
        remaining_items = []
        for item in items:
            if not tracker.is_flaky(item.nodeid):
                remaining_items.append(item)
            else:
                print(f"Skipping flaky test: {item.nodeid}")
        items[:] = remaining_items


def pytest_runtest_protocol(item: Item, nextitem: Optional[Item]):
    """测试运行协议"""
    nodeid = item.nodeid
    
    # 检查是否需要重试
    for attempt in range(tracker.max_retries + 1):
        start_time = time.time()
        
        # 运行测试
        rep = pytest_runtest_makereport(item, "call")
        
        duration = time.time() - start_time
        outcome = rep.outcome
        
        # 记录结果
        tracker.record_result(nodeid, outcome, duration)
        
        if outcome == "passed" or attempt == tracker.max_retries:
            break
        
        # 重试
        tracker.retry_counts[nodeid] += 1
        print(f"\nRetrying {nodeid} (attempt {attempt + 2}/{tracker.max_retries + 1})")
    
    return True


def pytest_runtest_makereport(item: Item, call):
    """生成测试报告"""
    # 这里简化处理，实际应该调用原始的makereport
    try:
        # 执行测试
        item.runtest()
        outcome = "passed"
        longrepr = None
    except Exception as e:
        outcome = "failed"
        longrepr = str(e)
    
    # 创建报告对象
    rep = TestReport(
        nodeid=item.nodeid,
        location=item.location,
        keywords=item.keywords,
        outcome=outcome,
        longrepr=longrepr,
        when=call
    )
    
    return rep


def pytest_sessionfinish(session, exitstatus):
    """会话结束时的处理"""
    if tracker:
        tracker.save_history()
        tracker.generate_report()


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """终端摘要"""
    if tracker:
        flaky_tests = tracker.get_flaky_tests()
        if flaky_tests:
            terminalreporter.write_sep("=", "FLAKY TEST SUMMARY")
            terminalreporter.write_line(f"Found {len(flaky_tests)} flaky tests:")
            for test in flaky_tests[:10]:  # 只显示前10个
                rate = test['success_rate']
                terminalreporter.write_line(
                    f"  {test['nodeid']} - Success rate: {rate:.2%}"
                )
            
            if len(flaky_tests) > 10:
                terminalreporter.write_line(f"  ... and {len(flaky_tests) - 10} more")
            
            terminalreporter.write_line("\nSee full report at: tests/reports/flaky/flaky_report.html")