"""
测试质量监控器

监控和分析测试质量指标：
1. 测试覆盖率监控
2. 测试执行时间分析
3. 测试稳定性分析
4. 测试质量评分
5. 质量趋势报告
"""

import os
import json
import time
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import subprocess
import xml.etree.ElementTree as ET


@dataclass
class QualityMetrics:
    """质量指标数据结构"""
    timestamp: datetime
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    pass_rate: float
    execution_time: float
    coverage_percentage: float
    avg_test_time: float
    flaky_tests: int
    new_tests: int
    removed_tests: int
    quality_score: float


@dataclass
class TestStability:
    """测试稳定性数据"""
    test_name: str
    success_rate: float
    avg_duration: float
    failure_count: int
    last_failure: Optional[datetime]
    is_flaky: bool


class TestQualityMonitor:
    """测试质量监控器"""
    
    def __init__(self, db_path: str = "tests/reports/quality.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_tests INTEGER NOT NULL,
                    passed_tests INTEGER NOT NULL,
                    failed_tests INTEGER NOT NULL,
                    skipped_tests INTEGER NOT NULL,
                    pass_rate REAL NOT NULL,
                    execution_time REAL NOT NULL,
                    coverage_percentage REAL,
                    avg_test_time REAL NOT NULL,
                    flaky_tests INTEGER DEFAULT 0,
                    new_tests INTEGER DEFAULT 0,
                    removed_tests INTEGER DEFAULT 0,
                    quality_score REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_stability (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    duration REAL NOT NULL,
                    status TEXT NOT NULL,
                    error_message TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON quality_metrics(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_name ON test_stability(test_name)
            """)
    
    def record_test_run(self, junit_xml_path: str, coverage_data: Optional[Dict] = None) -> QualityMetrics:
        """记录测试运行结果"""
        # 解析测试结果
        metrics = self._parse_test_results(junit_xml_path, coverage_data)
        
        # 分析测试稳定性
        self._analyze_test_stability(junit_xml_path)
        
        # 计算质量评分
        metrics.quality_score = self._calculate_quality_score(metrics)
        
        # 保存到数据库
        self._save_metrics(metrics)
        
        return metrics
    
    def _parse_test_results(self, junit_xml_path: str, coverage_data: Optional[Dict]) -> QualityMetrics:
        """解析测试结果"""
        tree = ET.parse(junit_xml_path)
        root = tree.getroot()
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        total_time = 0.0
        
        # 解析测试套件
        for testsuite in root.findall('.//testsuite'):
            suite_tests = int(testsuite.get('tests', 0))
            suite_failures = int(testsuite.get('failures', 0))
            suite_errors = int(testsuite.get('errors', 0))
            suite_skipped = int(testsuite.get('skipped', 0))
            suite_time = float(testsuite.get('time', 0))
            
            total_tests += suite_tests
            failed_tests += suite_failures + suite_errors
            skipped_tests += suite_skipped
            total_time += suite_time
        
        passed_tests = total_tests - failed_tests - skipped_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        avg_test_time = (total_time / total_tests) if total_tests > 0 else 0
        
        # 获取覆盖率
        coverage_percentage = 0.0
        if coverage_data:
            coverage_percentage = coverage_data.get('totals', {}).get('percent_covered', 0.0)
        
        return QualityMetrics(
            timestamp=datetime.now(),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            pass_rate=pass_rate,
            execution_time=total_time,
            coverage_percentage=coverage_percentage,
            avg_test_time=avg_test_time,
            flaky_tests=0,  # 稍后计算
            new_tests=0,    # 稍后计算
            removed_tests=0, # 稍后计算
            quality_score=0.0  # 稍后计算
        )
    
    def _analyze_test_stability(self, junit_xml_path: str):
        """分析测试稳定性"""
        tree = ET.parse(junit_xml_path)
        root = tree.getroot()
        
        with sqlite3.connect(self.db_path) as conn:
            for testsuite in root.findall('.//testsuite'):
                for testcase in testsuite.findall('.//testcase'):
                    test_name = f"{testsuite.get('name', '')}.{testcase.get('name', '')}"
                    duration = float(testcase.get('time', 0))
                    
                    # 确定测试状态
                    if testcase.find('failure') is not None:
                        status = 'failed'
                        error_msg = testcase.find('failure').get('message', '')
                    elif testcase.find('error') is not None:
                        status = 'error'
                        error_msg = testcase.find('error').get('message', '')
                    elif testcase.find('skipped') is not None:
                        status = 'skipped'
                        error_msg = ''
                    else:
                        status = 'passed'
                        error_msg = ''
                    
                    # 记录测试执行
                    conn.execute("""
                        INSERT INTO test_stability 
                        (test_name, timestamp, duration, status, error_message)
                        VALUES (?, ?, ?, ?, ?)
                    """, (test_name, datetime.now().isoformat(), duration, status, error_msg))
    
    def _calculate_quality_score(self, metrics: QualityMetrics) -> float:
        """计算质量评分 (0-100)"""
        # 权重配置
        weights = {
            'pass_rate': 0.4,      # 通过率权重40%
            'coverage': 0.3,       # 覆盖率权重30%
            'stability': 0.2,      # 稳定性权重20%
            'performance': 0.1     # 性能权重10%
        }
        
        # 通过率评分
        pass_rate_score = metrics.pass_rate
        
        # 覆盖率评分
        coverage_score = min(metrics.coverage_percentage, 100)
        
        # 稳定性评分 (基于flaky测试数量)
        stability_score = max(0, 100 - (metrics.flaky_tests * 10))
        
        # 性能评分 (基于平均测试时间)
        # 假设理想的测试时间是0.1秒，超过1秒开始扣分
        if metrics.avg_test_time <= 0.1:
            performance_score = 100
        elif metrics.avg_test_time <= 1.0:
            performance_score = 100 - (metrics.avg_test_time - 0.1) * 50
        else:
            performance_score = max(0, 50 - (metrics.avg_test_time - 1.0) * 10)
        
        # 计算综合评分
        quality_score = (
            pass_rate_score * weights['pass_rate'] +
            coverage_score * weights['coverage'] +
            stability_score * weights['stability'] +
            performance_score * weights['performance']
        )
        
        return round(quality_score, 2)
    
    def _save_metrics(self, metrics: QualityMetrics):
        """保存指标到数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO quality_metrics 
                (timestamp, total_tests, passed_tests, failed_tests, skipped_tests,
                 pass_rate, execution_time, coverage_percentage, avg_test_time,
                 flaky_tests, new_tests, removed_tests, quality_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.timestamp.isoformat(),
                metrics.total_tests,
                metrics.passed_tests,
                metrics.failed_tests,
                metrics.skipped_tests,
                metrics.pass_rate,
                metrics.execution_time,
                metrics.coverage_percentage,
                metrics.avg_test_time,
                metrics.flaky_tests,
                metrics.new_tests,
                metrics.removed_tests,
                metrics.quality_score
            ))
    
    def get_flaky_tests(self, days: int = 7, min_runs: int = 5) -> List[TestStability]:
        """获取不稳定的测试"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT test_name,
                       COUNT(*) as total_runs,
                       SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed_runs,
                       AVG(duration) as avg_duration,
                       SUM(CASE WHEN status != 'passed' THEN 1 ELSE 0 END) as failure_count,
                       MAX(CASE WHEN status != 'passed' THEN timestamp ELSE NULL END) as last_failure
                FROM test_stability
                WHERE timestamp > datetime('now', '-{} days')
                GROUP BY test_name
                HAVING total_runs >= ?
            """.format(days), (min_runs,))
            
            flaky_tests = []
            for row in cursor:
                test_name, total_runs, passed_runs, avg_duration, failure_count, last_failure = row
                success_rate = (passed_runs / total_runs * 100) if total_runs > 0 else 0
                
                # 认为成功率低于90%的测试为不稳定
                is_flaky = success_rate < 90.0
                
                if is_flaky:
                    flaky_tests.append(TestStability(
                        test_name=test_name,
                        success_rate=success_rate,
                        avg_duration=avg_duration,
                        failure_count=failure_count,
                        last_failure=datetime.fromisoformat(last_failure) if last_failure else None,
                        is_flaky=is_flaky
                    ))
            
            return sorted(flaky_tests, key=lambda x: x.success_rate)
    
    def get_quality_trend(self, days: int = 30) -> List[QualityMetrics]:
        """获取质量趋势"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM quality_metrics
                WHERE timestamp > datetime('now', '-{} days')
                ORDER BY timestamp DESC
            """.format(days))
            
            trends = []
            for row in cursor:
                _, timestamp, total_tests, passed_tests, failed_tests, skipped_tests, \
                pass_rate, execution_time, coverage_percentage, avg_test_time, \
                flaky_tests, new_tests, removed_tests, quality_score = row
                
                trends.append(QualityMetrics(
                    timestamp=datetime.fromisoformat(timestamp),
                    total_tests=total_tests,
                    passed_tests=passed_tests,
                    failed_tests=failed_tests,
                    skipped_tests=skipped_tests,
                    pass_rate=pass_rate,
                    execution_time=execution_time,
                    coverage_percentage=coverage_percentage,
                    avg_test_time=avg_test_time,
                    flaky_tests=flaky_tests,
                    new_tests=new_tests,
                    removed_tests=removed_tests,
                    quality_score=quality_score
                ))
            
            return trends
    
    def generate_quality_report(self, output_path: str = "tests/reports/quality_report.json"):
        """生成质量报告"""
        # 获取最新指标
        latest_metrics = self.get_quality_trend(days=1)
        current_metrics = latest_metrics[0] if latest_metrics else None
        
        # 获取历史趋势
        trend_metrics = self.get_quality_trend(days=30)
        
        # 获取不稳定测试
        flaky_tests = self.get_flaky_tests(days=7)
        
        # 计算趋势分析
        trend_analysis = self._analyze_trends(trend_metrics)
        
        # 生成报告
        report = {
            'generated_at': datetime.now().isoformat(),
            'current_metrics': asdict(current_metrics) if current_metrics else None,
            'trend_analysis': trend_analysis,
            'flaky_tests': [asdict(test) for test in flaky_tests[:10]],  # 前10个最不稳定的测试
            'recommendations': self._generate_recommendations(current_metrics, flaky_tests)
        }
        
        # 保存报告
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        return report
    
    def _analyze_trends(self, metrics: List[QualityMetrics]) -> Dict[str, Any]:
        """分析趋势"""
        if len(metrics) < 2:
            return {'status': 'insufficient_data'}
        
        # 计算变化趋势
        recent = metrics[0]
        older = metrics[-1]
        
        pass_rate_change = recent.pass_rate - older.pass_rate
        coverage_change = recent.coverage_percentage - older.coverage_percentage
        quality_change = recent.quality_score - older.quality_score
        
        return {
            'period_days': (recent.timestamp - older.timestamp).days,
            'pass_rate_change': round(pass_rate_change, 2),
            'coverage_change': round(coverage_change, 2),
            'quality_change': round(quality_change, 2),
            'trend_direction': 'improving' if quality_change > 0 else 'declining' if quality_change < 0 else 'stable'
        }
    
    def _generate_recommendations(self, current_metrics: Optional[QualityMetrics], 
                                flaky_tests: List[TestStability]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if not current_metrics:
            return ['需要更多测试数据来生成建议']
        
        # 通过率建议
        if current_metrics.pass_rate < 95:
            recommendations.append(f"通过率为{current_metrics.pass_rate:.1f}%，建议修复失败的测试用例")
        
        # 覆盖率建议
        if current_metrics.coverage_percentage < 80:
            recommendations.append(f"代码覆盖率为{current_metrics.coverage_percentage:.1f}%，建议增加测试用例")
        
        # 性能建议
        if current_metrics.avg_test_time > 1.0:
            recommendations.append(f"平均测试时间为{current_metrics.avg_test_time:.2f}秒，建议优化测试性能")
        
        # 稳定性建议
        if len(flaky_tests) > 0:
            recommendations.append(f"发现{len(flaky_tests)}个不稳定测试，建议修复以提高测试可靠性")
        
        # 质量评分建议
        if current_metrics.quality_score < 80:
            recommendations.append("整体质量评分偏低，建议重点关注通过率和覆盖率")
        
        return recommendations
    
    def check_quality_gates(self, metrics: QualityMetrics) -> Tuple[bool, List[str]]:
        """检查质量门禁"""
        failures = []
        
        # 质量门禁规则
        gates = {
            'min_pass_rate': 90.0,
            'min_coverage': 70.0,
            'max_avg_test_time': 2.0,
            'max_flaky_tests': 5,
            'min_quality_score': 75.0
        }
        
        if metrics.pass_rate < gates['min_pass_rate']:
            failures.append(f"通过率{metrics.pass_rate:.1f}%低于要求的{gates['min_pass_rate']}%")
        
        if metrics.coverage_percentage < gates['min_coverage']:
            failures.append(f"覆盖率{metrics.coverage_percentage:.1f}%低于要求的{gates['min_coverage']}%")
        
        if metrics.avg_test_time > gates['max_avg_test_time']:
            failures.append(f"平均测试时间{metrics.avg_test_time:.2f}秒超过限制的{gates['max_avg_test_time']}秒")
        
        if metrics.flaky_tests > gates['max_flaky_tests']:
            failures.append(f"不稳定测试数量{metrics.flaky_tests}超过限制的{gates['max_flaky_tests']}个")
        
        if metrics.quality_score < gates['min_quality_score']:
            failures.append(f"质量评分{metrics.quality_score:.1f}低于要求的{gates['min_quality_score']}")
        
        return len(failures) == 0, failures


# 命令行工具
def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="测试质量监控器")
    parser.add_argument('--junit-xml', required=True, help='JUnit XML报告路径')
    parser.add_argument('--coverage-json', help='覆盖率JSON报告路径')
    parser.add_argument('--output', default='tests/reports/quality_report.json', help='输出报告路径')
    parser.add_argument('--check-gates', action='store_true', help='检查质量门禁')
    
    args = parser.parse_args()
    
    # 创建监控器
    monitor = TestQualityMonitor()
    
    # 读取覆盖率数据
    coverage_data = None
    if args.coverage_json and os.path.exists(args.coverage_json):
        with open(args.coverage_json, 'r') as f:
            coverage_data = json.load(f)
    
    # 记录测试运行
    metrics = monitor.record_test_run(args.junit_xml, coverage_data)
    
    # 生成报告
    report = monitor.generate_quality_report(args.output)
    
    # 检查质量门禁
    if args.check_gates:
        passed, failures = monitor.check_quality_gates(metrics)
        
        print(f"质量门禁检查: {'✅ 通过' if passed else '❌ 失败'}")
        if failures:
            print("失败原因:")
            for failure in failures:
                print(f"  - {failure}")
        
        return 0 if passed else 1
    
    print(f"✅ 质量报告已生成: {args.output}")
    print(f"📊 质量评分: {metrics.quality_score:.1f}/100")
    return 0


if __name__ == '__main__':
    exit(main())


print("✅ 测试质量监控器创建完成")