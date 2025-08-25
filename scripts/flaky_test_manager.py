#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flaky测试管理脚本

功能：
1. 统一管理前后端flaky测试
2. 生成综合报告
3. 自动隔离不稳定测试
4. 提供测试稳定性分析
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class FlakyTestManager:
    """Flaky测试管理器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.reports_dir = self.project_root / "tests" / "reports" / "flaky"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def run_backend_tests(self, isolate_flaky: bool = False) -> bool:
        """运行后端测试"""
        print("\n=== Running Backend Tests ===")
        
        cmd = ["python", "-m", "pytest"]
        if isolate_flaky:
            cmd.append("--flaky-isolate")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.backend_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            print(f"Backend tests exit code: {result.returncode}")
            if result.stdout:
                print("STDOUT:", result.stdout[-1000:])  # 只显示最后1000字符
            if result.stderr:
                print("STDERR:", result.stderr[-1000:])
            
            return result.returncode == 0
        
        except subprocess.TimeoutExpired:
            print("Backend tests timed out")
            return False
        except Exception as e:
            print(f"Error running backend tests: {e}")
            return False
    
    def run_frontend_tests(self, use_flaky_config: bool = False) -> bool:
        """运行前端测试"""
        print("\n=== Running Frontend Tests ===")
        
        config_file = "vitest.flaky.config.js" if use_flaky_config else "vitest.config.js"
        cmd = ["npm", "run", "test", "--", "--config", config_file]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            print(f"Frontend tests exit code: {result.returncode}")
            if result.stdout:
                print("STDOUT:", result.stdout[-1000:])
            if result.stderr:
                print("STDERR:", result.stderr[-1000:])
            
            return result.returncode == 0
        
        except subprocess.TimeoutExpired:
            print("Frontend tests timed out")
            return False
        except Exception as e:
            print(f"Error running frontend tests: {e}")
            return False
    
    def collect_flaky_reports(self) -> Dict:
        """收集flaky测试报告"""
        reports = {
            'backend': None,
            'frontend': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # 收集后端报告
        backend_report_dir = self.backend_dir / "tests" / "reports" / "flaky"
        if backend_report_dir.exists():
            history_file = backend_report_dir / "flaky_history.json"
            if history_file.exists():
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        reports['backend'] = json.load(f)
                except Exception as e:
                    print(f"Error reading backend flaky report: {e}")
        
        # 收集前端报告
        frontend_report_dir = self.frontend_dir / "tests" / "reports" / "flaky"
        if frontend_report_dir.exists():
            history_file = frontend_report_dir / "flaky_history.json"
            if history_file.exists():
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        reports['frontend'] = json.load(f)
                except Exception as e:
                    print(f"Error reading frontend flaky report: {e}")
        
        return reports
    
    def analyze_flaky_tests(self, reports: Dict) -> Dict:
        """分析flaky测试"""
        analysis = {
            'summary': {
                'total_backend_tests': 0,
                'total_frontend_tests': 0,
                'backend_flaky_tests': 0,
                'frontend_flaky_tests': 0,
                'most_unstable_tests': []
            },
            'backend_flaky': [],
            'frontend_flaky': [],
            'recommendations': []
        }
        
        # 分析后端
        if reports['backend'] and 'test_results' in reports['backend']:
            backend_results = reports['backend']['test_results']
            analysis['summary']['total_backend_tests'] = len(backend_results)
            
            for test_name, results in backend_results.items():
                if len(results) >= 5:
                    success_rate = results.count('passed') / len(results)
                    if success_rate < 0.8 and success_rate > 0:
                        analysis['backend_flaky'].append({
                            'name': test_name,
                            'success_rate': success_rate,
                            'total_runs': len(results),
                            'type': 'backend'
                        })
            
            analysis['summary']['backend_flaky_tests'] = len(analysis['backend_flaky'])
        
        # 分析前端
        if reports['frontend'] and 'testResults' in reports['frontend']:
            frontend_results = reports['frontend']['testResults']
            analysis['summary']['total_frontend_tests'] = len(frontend_results)
            
            for test_name, results in frontend_results.items():
                if len(results) >= 5:
                    passed_count = sum(1 for r in results if r.get('outcome') == 'passed')
                    success_rate = passed_count / len(results)
                    if success_rate < 0.8 and success_rate > 0:
                        analysis['frontend_flaky'].append({
                            'name': test_name,
                            'success_rate': success_rate,
                            'total_runs': len(results),
                            'type': 'frontend'
                        })
            
            analysis['summary']['frontend_flaky_tests'] = len(analysis['frontend_flaky'])
        
        # 找出最不稳定的测试
        all_flaky = analysis['backend_flaky'] + analysis['frontend_flaky']
        analysis['summary']['most_unstable_tests'] = sorted(
            all_flaky, key=lambda x: x['success_rate']
        )[:10]
        
        # 生成建议
        total_flaky = analysis['summary']['backend_flaky_tests'] + analysis['summary']['frontend_flaky_tests']
        if total_flaky == 0:
            analysis['recommendations'].append("🎉 No flaky tests detected! Your test suite is stable.")
        else:
            analysis['recommendations'].extend([
                f"⚠️  Found {total_flaky} flaky tests that need attention.",
                "🔧 Consider refactoring the most unstable tests.",
                "⏱️  Add proper wait conditions for timing-sensitive tests.",
                "🧪 Use test isolation to prevent test interference.",
                "📊 Monitor test stability over time."
            ])
            
            if total_flaky > 10:
                analysis['recommendations'].append(
                    "🚨 High number of flaky tests detected. Consider a comprehensive test review."
                )
        
        return analysis
    
    def generate_comprehensive_report(self, analysis: Dict):
        """生成综合报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON报告
        json_file = self.reports_dir / f"comprehensive_flaky_report_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        # HTML报告
        html_content = self._generate_html_report(analysis)
        html_file = self.reports_dir / "comprehensive_flaky_report.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n=== Comprehensive Flaky Test Report ===")
        print(f"Backend tests: {analysis['summary']['total_backend_tests']}")
        print(f"Frontend tests: {analysis['summary']['total_frontend_tests']}")
        print(f"Backend flaky: {analysis['summary']['backend_flaky_tests']}")
        print(f"Frontend flaky: {analysis['summary']['frontend_flaky_tests']}")
        print(f"Report saved to: {html_file}")
        
        # 显示建议
        print("\nRecommendations:")
        for rec in analysis['recommendations']:
            print(f"  {rec}")
        
        # 显示最不稳定的测试
        if analysis['summary']['most_unstable_tests']:
            print("\nMost unstable tests:")
            for test in analysis['summary']['most_unstable_tests'][:5]:
                print(f"  - [{test['type']}] {test['name']} (success rate: {test['success_rate']:.2%})")
    
    def _generate_html_report(self, analysis: Dict) -> str:
        """生成HTML报告"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        summary = analysis['summary']
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Comprehensive Flaky Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .metric {{ background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }}
        .metric.warning {{ border-left-color: #ffc107; }}
        .metric.danger {{ border-left-color: #dc3545; }}
        .test-section {{ margin: 20px 0; }}
        .test-item {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        .recommendations {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; }}
        .success-rate {{ font-weight: bold; }}
        .low {{ color: #dc3545; }}
        .medium {{ color: #fd7e14; }}
        .high {{ color: #28a745; }}
    </style>
</head>
<body>
    <h1>Comprehensive Flaky Test Report</h1>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Generated:</strong> {timestamp}</p>
        
        <div class="metrics">
            <div class="metric">
                <h3>Backend Tests</h3>
                <p>Total: {summary['total_backend_tests']}</p>
                <p>Flaky: {summary['backend_flaky_tests']}</p>
            </div>
            <div class="metric">
                <h3>Frontend Tests</h3>
                <p>Total: {summary['total_frontend_tests']}</p>
                <p>Flaky: {summary['frontend_flaky_tests']}</p>
            </div>
            <div class="metric {'warning' if summary['backend_flaky_tests'] + summary['frontend_flaky_tests'] > 0 else ''}">
                <h3>Total Flaky</h3>
                <p>{summary['backend_flaky_tests'] + summary['frontend_flaky_tests']}</p>
            </div>
        </div>
    </div>
    
    <div class="recommendations">
        <h2>Recommendations</h2>
        <ul>
"""
        
        for rec in analysis['recommendations']:
            html += f"<li>{rec}</li>"
        
        html += """
        </ul>
    </div>
    
    <div class="test-section">
        <h2>Most Unstable Tests</h2>
"""
        
        if not summary['most_unstable_tests']:
            html += "<p>No flaky tests detected! 🎉</p>"
        else:
            for test in summary['most_unstable_tests']:
                success_rate = test['success_rate']
                rate_class = 'low' if success_rate < 0.5 else 'medium' if success_rate < 0.8 else 'high'
                
                html += f"""
        <div class="test-item">
            <h3>[{test['type'].upper()}] {test['name']}</h3>
            <p>Success Rate: <span class="success-rate {rate_class}">{success_rate:.2%}</span></p>
            <p>Total Runs: {test['total_runs']}</p>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        return html
    
    def run_stability_check(self, iterations: int = 5) -> Dict:
        """运行稳定性检查"""
        print(f"\n=== Running Stability Check ({iterations} iterations) ===")
        
        results = {
            'backend': [],
            'frontend': [],
            'iterations': iterations,
            'timestamp': datetime.now().isoformat()
        }
        
        for i in range(iterations):
            print(f"\nIteration {i + 1}/{iterations}")
            
            # 运行后端测试
            backend_success = self.run_backend_tests()
            results['backend'].append(backend_success)
            
            # 运行前端测试
            frontend_success = self.run_frontend_tests(use_flaky_config=True)
            results['frontend'].append(frontend_success)
        
        # 计算稳定性
        backend_stability = sum(results['backend']) / len(results['backend'])
        frontend_stability = sum(results['frontend']) / len(results['frontend'])
        
        print(f"\n=== Stability Check Results ===")
        print(f"Backend stability: {backend_stability:.2%}")
        print(f"Frontend stability: {frontend_stability:.2%}")
        
        results['stability'] = {
            'backend': backend_stability,
            'frontend': frontend_stability,
            'overall': (backend_stability + frontend_stability) / 2
        }
        
        return results


def main():
    parser = argparse.ArgumentParser(description='Flaky Test Manager')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    parser.add_argument('--action', choices=['test', 'analyze', 'stability'], 
                       default='analyze', help='Action to perform')
    parser.add_argument('--isolate-flaky', action='store_true', 
                       help='Skip known flaky tests')
    parser.add_argument('--iterations', type=int, default=5, 
                       help='Number of iterations for stability check')
    
    args = parser.parse_args()
    
    manager = FlakyTestManager(args.project_root)
    
    if args.action == 'test':
        # 运行测试
        backend_success = manager.run_backend_tests(args.isolate_flaky)
        frontend_success = manager.run_frontend_tests(use_flaky_config=True)
        
        if backend_success and frontend_success:
            print("\n✅ All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    
    elif args.action == 'analyze':
        # 分析flaky测试
        reports = manager.collect_flaky_reports()
        analysis = manager.analyze_flaky_tests(reports)
        manager.generate_comprehensive_report(analysis)
    
    elif args.action == 'stability':
        # 稳定性检查
        results = manager.run_stability_check(args.iterations)
        
        # 保存结果
        stability_file = manager.reports_dir / f"stability_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stability_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nStability check results saved to: {stability_file}")
        
        # 根据稳定性决定退出码
        overall_stability = results['stability']['overall']
        if overall_stability >= 0.9:
            print("\n✅ Test suite is stable!")
            sys.exit(0)
        elif overall_stability >= 0.7:
            print("\n⚠️  Test suite has some instability.")
            sys.exit(1)
        else:
            print("\n❌ Test suite is highly unstable!")
            sys.exit(2)


if __name__ == '__main__':
    main()