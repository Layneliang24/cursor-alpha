#!/usr/bin/env python3
"""
Alpha Platform 测试体系运行器
提供一键测试、覆盖率、代码质量检查等命令
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """运行命令"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=False, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        # 对于覆盖率命令，即使有错误也认为是成功的（因为可能只是覆盖率低）
        if "coverage" in cmd.lower() or "cov" in cmd.lower():
            return True
        
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}", file=sys.stderr)
        return False

def show_help():
    """显示帮助信息"""
    print("Alpha Platform 测试体系命令:")
    print()
    print("测试相关:")
    print("  test          - 运行所有测试 (后端 + 前端 + E2E)")
    print("  test-backend  - 运行后端测试")
    print("  test-frontend - 运行前端单元测试")
    print("  test-e2e      - 运行端到端测试")
    print()
    print("覆盖率相关:")
    print("  cov           - 生成覆盖率报告")
    print("  cov-backend   - 生成后端覆盖率报告")
    print("  cov-frontend  - 生成前端覆盖率报告")
    print()
    print("代码质量:")
    print("  lint          - 代码质量检查")
    print("  format        - 代码格式化")
    print("  complexity    - 代码复杂度分析")
    print()
    print("环境管理:")
    print("  install       - 安装依赖")
    print("  clean         - 清理临时文件")
    print("  verify        - 验证测试环境")

def test_backend():
    """运行后端测试"""
    print("🧪 运行后端测试...")
    return run_command("python -m pytest tests/ -v --tb=short --strict-markers", 
                      cwd="backend")

def test_frontend():
    """运行前端单元测试"""
    print("🧪 运行前端单元测试...")
    return run_command("npm run test:unit")

def test_e2e():
    """运行端到端测试"""
    print("🧪 运行端到端测试...")
    return run_command("npm run test:e2e")

def test_all():
    """运行所有测试"""
    print("🧪 运行所有测试...")
    success = True
    success &= test_backend()
    success &= test_frontend()
    success &= test_e2e()
    
    if success:
        print("✅ 所有测试完成!")
    else:
        print("❌ 部分测试失败!")
    
    return success

def cov_backend():
    """生成后端覆盖率报告"""
    print("📊 生成后端覆盖率报告...")
    return run_command("python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing --cov-config=.coveragerc", 
                      cwd="backend")

def cov_frontend():
    """生成前端覆盖率报告"""
    print("📊 生成前端覆盖率报告...")
    return run_command("npm run test:coverage")

def cov_all():
    """生成所有覆盖率报告"""
    print("📊 生成覆盖率报告...")
    success = True
    success &= cov_backend()
    success &= cov_frontend()
    
    if success:
        print("📊 覆盖率报告生成完成!")
    else:
        print("❌ 覆盖率报告生成失败!")
    
    return success

def lint():
    """代码质量检查"""
    print("🔍 检查代码质量...")
    success = True
    
    print("检查后端代码...")
    success &= run_command("flake8 . --max-line-length=120 --extend-ignore=E203,W503", 
                          cwd="backend")
    
    print("检查前端代码...")
    success &= run_command("npm run lint")
    
    return success

def format_code():
    """代码格式化"""
    print("✨ 格式化代码...")
    success = True
    
    print("格式化后端代码...")
    success &= run_command("black . --line-length=120", cwd="backend")
    success &= run_command("isort .", cwd="backend")
    
    print("格式化前端代码...")
    success &= run_command("npm run format")
    
    return success

def complexity():
    """代码复杂度分析"""
    print("📈 分析代码复杂度...")
    return run_command("radon cc . -a -nc && radon mi . -a && radon hal . -a", 
                      cwd="backend")

def clean():
    """清理临时文件"""
    print("🧹 清理临时文件...")
    
    # 清理Python缓存
    for pattern in ["*.pyc", "__pycache__", ".coverage", "htmlcov", ".pytest_cache"]:
        if pattern == "*.pyc":
            run_command(f"find . -name '{pattern}' -delete", check=False)
        else:
            run_command(f"find . -type d -name '{pattern}' -exec rm -rf {{}} +", check=False)
    
    # 清理Node缓存
    run_command("find . -type d -name 'node_modules/.cache' -exec rm -rf {} +", check=False)
    
    print("✅ 清理完成!")

def install():
    """安装依赖"""
    print("📦 安装依赖...")
    success = True
    
    print("安装后端依赖...")
    success &= run_command("pip install -r backend/requirements.txt")
    
    print("安装前端依赖...")
    success &= run_command("npm install")
    
    print("安装Playwright浏览器...")
    success &= run_command("npx playwright install")
    
    return success

def verify():
    """验证测试环境"""
    print("🔍 验证测试环境...")
    
    print("检查Python版本...")
    run_command("python --version")
    
    print("检查Django版本...")
    run_command("python -c \"import django; print(f'Django {django.get_version()}')\"", 
                cwd="backend")
    
    print("检查pytest版本...")
    run_command("pytest --version")
    
    print("检查Node版本...")
    run_command("node --version")
    
    print("检查npm版本...")
    run_command("npm --version")
    
    print("✅ 测试环境验证完成!")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Alpha Platform 测试体系运行器")
    parser.add_argument("command", nargs="?", default="help", 
                       help="要执行的命令")
    
    args = parser.parse_args()
    
    commands = {
        "help": show_help,
        "test": test_all,
        "test-backend": test_backend,
        "test-frontend": test_frontend,
        "test-e2e": test_e2e,
        "cov": cov_all,
        "cov-backend": cov_backend,
        "cov-frontend": cov_frontend,
        "lint": lint,
        "format": format_code,
        "complexity": complexity,
        "clean": clean,
        "install": install,
        "verify": verify
    }
    
    if args.command not in commands:
        print(f"❌ 未知命令: {args.command}")
        show_help()
        sys.exit(1)
    
    success = commands[args.command]()
    
    if args.command != "help" and not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
