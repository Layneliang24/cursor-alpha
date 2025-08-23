#!/usr/bin/env python3
"""
前端测试运行器
集成到项目的整体测试体系中，支持不同级别的测试执行
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time
import shutil

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

class FrontendTestRunner:
    """前端测试运行器"""
    
    def __init__(self):
        self.frontend_dir = FRONTEND_DIR
        self.test_results = {}
        self.coverage_data = {}
        self.npm_cmd = self._get_npm_command()
        
    def _get_npm_command(self) -> str:
        """获取npm命令路径"""
        # 在Windows上，优先查找npm.cmd
        if os.name == 'nt':  # Windows
            npm_cmd = shutil.which('npm.cmd') or shutil.which('npm')
            if npm_cmd:
                return npm_cmd
            # 尝试常见的npm路径
            possible_paths = [
                r"C:\Program Files\nodejs\npm.cmd",
                r"C:\Program Files (x86)\nodejs\npm.cmd",
                r"C:\Users\%USERNAME%\AppData\Roaming\npm\npm.cmd"
            ]
            for path in possible_paths:
                expanded_path = os.path.expandvars(path)
                if os.path.exists(expanded_path):
                    return expanded_path
        else:
            npm_cmd = shutil.which('npm')
            if npm_cmd:
                return npm_cmd
        
        return 'npm'  # 回退到默认值
        
    def check_frontend_environment(self) -> bool:
        """检查前端测试环境"""
        print("🔍 检查前端测试环境...")
        
        # 检查前端目录是否存在
        if not self.frontend_dir.exists():
            print("❌ 前端目录不存在")
            return False
            
        # 检查package.json
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            print("❌ package.json不存在")
            return False
            
        # 检查node_modules
        node_modules = self.frontend_dir / "node_modules"
        if not node_modules.exists():
            print("❌ node_modules不存在，请先运行 npm install")
            return False
            
        # 检查vitest配置
        vitest_config = self.frontend_dir / "vitest.config.ts"
        if not vitest_config.exists():
            print("❌ vitest.config.ts不存在")
            return False
            
        print("✅ 前端测试环境检查通过")
        return True
        
    def install_dependencies(self) -> bool:
        """安装前端依赖"""
        print("📦 安装前端依赖...")
        
        try:
            result = subprocess.run(
                [self.npm_cmd, "install"],
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=300
            )
            
            if result.returncode == 0:
                print("✅ 前端依赖安装成功")
                return True
            else:
                print(f"❌ 前端依赖安装失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ 前端依赖安装超时")
            return False
        except Exception as e:
            print(f"❌ 前端依赖安装异常: {e}")
            return False
            
    def run_tests(self, level: str = "smoke", coverage: bool = True) -> Dict:
        """运行前端测试"""
        print(f"🚀 运行前端{level}测试...")
        
        # 构建测试命令
        cmd = [self.npm_cmd, "run", "test:fe"]
        
        # 添加覆盖率参数
        if coverage:
            cmd.extend(["--coverage"])
            
        # 添加测试级别标记
        if level == "smoke":
            cmd.extend(["--reporter=verbose", "--run"])
        elif level == "fast":
            cmd.extend(["--reporter=verbose", "--run", "--max-threads=2"])
        elif level == "full":
            cmd.extend(["--reporter=verbose", "--run", "--coverage"])
        elif level == "performance":
            cmd.extend(["--reporter=verbose", "--run", "--max-threads=1"])
            
        try:
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                cwd=self.frontend_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=600
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # 解析测试结果
            test_result = self._parse_test_result(result, duration)
            
            print(f"⏱️  测试耗时: {duration:.2f}秒")
            print(f"📊 测试结果: {test_result['summary']}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            print("❌ 测试执行超时")
            return {
                "success": False,
                "error": "测试执行超时",
                "duration": 600,
                "summary": "超时"
            }
        except Exception as e:
            print(f"❌ 测试执行异常: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration": 0,
                "summary": "异常"
            }
            
    def _parse_test_result(self, result: subprocess.CompletedProcess, duration: float) -> Dict:
        """解析测试结果"""
        if result.returncode == 0:
            # 成功
            return {
                "success": True,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration,
                "summary": "通过"
            }
        else:
            # 失败
            return {
                "success": False,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration": duration,
                "summary": "失败"
            }
            
    def generate_coverage_report(self) -> Dict:
        """生成覆盖率报告"""
        print("📈 生成覆盖率报告...")
        
        coverage_dir = self.frontend_dir / "coverage"
        if not coverage_dir.exists():
            print("❌ 覆盖率目录不存在")
            return {}
            
        # 读取覆盖率数据
        coverage_file = coverage_dir / "coverage-summary.json"
        if coverage_file.exists():
            try:
                with open(coverage_file, 'r', encoding='utf-8') as f:
                    coverage_data = json.load(f)
                print("✅ 覆盖率报告生成成功")
                return coverage_data
            except Exception as e:
                print(f"❌ 读取覆盖率数据失败: {e}")
                return {}
        else:
            print("❌ 覆盖率文件不存在")
            return {}
            
    def run_smoke_tests(self) -> Dict:
        """运行冒烟测试"""
        return self.run_tests("smoke", coverage=False)
        
    def run_fast_tests(self) -> Dict:
        """运行快速测试"""
        return self.run_tests("fast", coverage=True)
        
    def run_full_tests(self) -> Dict:
        """运行全量测试"""
        return self.run_tests("full", coverage=True)
        
    def run_performance_tests(self) -> Dict:
        """运行性能测试"""
        return self.run_tests("performance", coverage=False)
        
    def get_test_summary(self) -> Dict:
        """获取测试摘要"""
        return {
            "frontend_tests": self.test_results,
            "coverage": self.coverage_data,
            "total_tests": len(self.test_results),
            "passed_tests": sum(1 for r in self.test_results.values() if r.get("success")),
            "failed_tests": sum(1 for r in self.test_results.values() if not r.get("success"))
        }
        
    def cleanup(self):
        """清理测试环境"""
        print("🧹 清理测试环境...")
        
        # 清理覆盖率文件（可选）
        coverage_dir = self.frontend_dir / "coverage"
        if coverage_dir.exists():
            try:
                import shutil
                shutil.rmtree(coverage_dir)
                print("✅ 覆盖率文件清理完成")
            except Exception as e:
                print(f"⚠️  覆盖率文件清理失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="前端测试运行器")
    parser.add_argument(
        "--level", 
        choices=["smoke", "fast", "full", "performance"],
        default="smoke",
        help="测试级别"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="不生成覆盖率报告"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="测试完成后清理环境"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="自动安装依赖"
    )
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = FrontendTestRunner()
    
    try:
        # 检查环境
        if not runner.check_frontend_environment():
            print("❌ 前端测试环境检查失败")
            sys.exit(1)
            
        # 安装依赖（如果需要）
        if args.install_deps:
            if not runner.install_dependencies():
                print("❌ 依赖安装失败")
                sys.exit(1)
                
        # 运行测试
        print(f"🎯 开始执行前端{args.level}测试...")
        
        if args.level == "smoke":
            result = runner.run_smoke_tests()
        elif args.level == "fast":
            result = runner.run_fast_tests()
        elif args.level == "full":
            result = runner.run_full_tests()
        elif args.level == "performance":
            result = runner.run_performance_tests()
            
        # 保存测试结果
        runner.test_results[args.level] = result
        
        # 生成覆盖率报告
        if not args.no_coverage and result.get("success"):
            coverage_data = runner.generate_coverage_report()
            runner.coverage_data[args.level] = coverage_data
            
        # 输出测试摘要
        summary = runner.get_test_summary()
        print("\n" + "="*50)
        print("📋 测试摘要")
        print("="*50)
        print(f"测试级别: {args.level}")
        print(f"测试结果: {'✅ 通过' if result.get('success') else '❌ 失败'}")
        print(f"执行时间: {result.get('duration', 0):.2f}秒")
        print(f"总测试数: {summary['total_tests']}")
        print(f"通过测试: {summary['passed_tests']}")
        print(f"失败测试: {summary['failed_tests']}")
        
        # 清理环境
        if args.cleanup:
            runner.cleanup()
            
        # 返回状态码
        sys.exit(0 if result.get("success") else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"❌ 测试执行异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 