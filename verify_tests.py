#!/usr/bin/env python3
"""
测试流程验证脚本
用于在新机器上快速验证测试流程是否正常工作
"""

import sys
import subprocess
import os
import time
from pathlib import Path

# 颜色定义
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header():
    """打印标题"""
    print(f"{Colors.BLUE}{Colors.BOLD}")
    print("=" * 60)
    print("           Alpha 项目测试流程验证")
    print("=" * 60)
    print(f"{Colors.RESET}")

def print_section(title):
    """打印章节标题"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{title}{Colors.RESET}")
    print("-" * len(title))

def print_success(message):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_warning(message):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def run_command(command, cwd=None, timeout=30):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            cwd=cwd
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", str(e)

def check_backend_environment():
    """检查后端环境"""
    print_section("后端环境检查")
    
    # 检查是否在backend目录
    if not Path("backend").exists():
        print_error("backend目录不存在")
        return False
    
    # 检查虚拟环境
    venv_path = Path("backend/venv")
    if not venv_path.exists():
        print_error("虚拟环境不存在，请先运行setup_project.bat")
        return False
    
    print_success("虚拟环境存在")
    
    # 检查Django
    success, output, error = run_command(
        "python -c 'import django; print(django.get_version())'",
        cwd="backend"
    )
    if success:
        print_success(f"Django版本: {output}")
    else:
        print_error("Django未安装")
        return False
    
    # 检查pytest
    success, output, error = run_command(
        "python -m pytest --version",
        cwd="backend"
    )
    if success:
        print_success(f"pytest可用: {output}")
    else:
        print_error("pytest未安装")
        return False
    
    return True

def run_basic_tests():
    """运行基础测试"""
    print_section("基础测试执行")
    
    # 运行基础测试
    success, output, error = run_command(
        "python -m pytest ../tests/unit/test_basic.py -v",
        cwd="backend",
        timeout=60
    )
    
    if success:
        print_success("基础测试通过")
        # 解析测试结果
        lines = output.split('\n')
        for line in lines:
            if 'PASSED' in line:
                print_success(f"  {line.strip()}")
        return True
    else:
        print_error("基础测试失败")
        print(f"错误信息: {error}")
        return False

def run_unit_tests():
    """运行单元测试"""
    print_section("单元测试执行")
    
    # 运行模型测试
    success, output, error = run_command(
        "python -m pytest ../tests/unit/test_models.py -v",
        cwd="backend",
        timeout=60
    )
    
    if success:
        print_success("模型测试通过")
        # 统计测试数量
        test_count = output.count('PASSED')
        print_success(f"  通过测试数: {test_count}")
    else:
        print_error("模型测试失败")
        print(f"错误信息: {error}")
        return False
    
    return True

def run_integration_tests():
    """运行集成测试"""
    print_section("集成测试执行")
    
    # 运行API测试
    success, output, error = run_command(
        "python -m pytest ../tests/integration/test_api.py -v",
        cwd="backend",
        timeout=120
    )
    
    if success:
        print_success("API集成测试通过")
        # 统计测试数量
        test_count = output.count('PASSED')
        print_success(f"  通过测试数: {test_count}")
    else:
        print_error("API集成测试失败")
        print(f"错误信息: {error}")
        return False
    
    return True

def generate_coverage_report():
    """生成覆盖率报告"""
    print_section("覆盖率报告生成")
    
    # 运行覆盖率测试
    success, output, error = run_command(
        "python -m pytest ../tests/ --cov=apps --cov-report=html --cov-report=term-missing",
        cwd="backend",
        timeout=180
    )
    
    if success:
        print_success("覆盖率报告生成成功")
        
        # 查找覆盖率信息
        lines = output.split('\n')
        for line in lines:
            if 'TOTAL' in line and '%' in line:
                print_success(f"  总体覆盖率: {line.strip()}")
            elif 'apps/' in line and '%' in line:
                print_success(f"  {line.strip()}")
        
        # 检查报告文件
        report_path = Path("tests/htmlcov/index.html")
        if report_path.exists():
            print_success(f"  详细报告: {report_path.absolute()}")
        else:
            print_warning("覆盖率报告文件未找到")
        
        return True
    else:
        print_error("覆盖率报告生成失败")
        print(f"错误信息: {error}")
        return False

def check_test_structure():
    """检查测试结构"""
    print_section("测试结构检查")
    
    # 检查测试目录结构
    test_dirs = ["tests", "tests/unit", "tests/integration", "tests/factories"]
    for dir_name in test_dirs:
        if Path(dir_name).exists():
            print_success(f"目录存在: {dir_name}")
        else:
            print_error(f"目录缺失: {dir_name}")
            return False
    
    # 检查关键测试文件
    test_files = [
        "tests/conftest.py",
        "tests/unit/test_basic.py",
        "tests/unit/test_models.py",
        "tests/integration/test_api.py",
        "tests/factories/user_factory.py",
        "tests/factories/article_factory.py",
        "tests/factories/category_factory.py"
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            print_success(f"文件存在: {file_path}")
        else:
            print_error(f"文件缺失: {file_path}")
            return False
    
    return True

def verify_database():
    """验证数据库连接"""
    print_section("数据库连接验证")
    
    # 检查数据库迁移
    success, output, error = run_command(
        "python manage.py showmigrations",
        cwd="backend"
    )
    
    if success:
        print_success("数据库迁移状态正常")
        # 检查是否有未应用的迁移
        if " [ ] " in output:
            print_warning("存在未应用的迁移")
            # 应用迁移
            success, output, error = run_command(
                "python manage.py migrate",
                cwd="backend"
            )
            if success:
                print_success("数据库迁移应用成功")
            else:
                print_error("数据库迁移应用失败")
                return False
        else:
            print_success("所有迁移已应用")
    else:
        print_error("数据库连接失败")
        return False
    
    return True

def main():
    """主函数"""
    print_header()
    
    results = {}
    
    # 执行各项验证
    print("开始验证测试流程...")
    
    # 1. 检查测试结构
    results['structure'] = check_test_structure()
    if not results['structure']:
        print_error("测试结构检查失败，请检查项目完整性")
        return 1
    
    # 2. 检查后端环境
    results['backend'] = check_backend_environment()
    if not results['backend']:
        print_error("后端环境检查失败，请先完成环境搭建")
        return 1
    
    # 3. 验证数据库
    results['database'] = verify_database()
    if not results['database']:
        print_error("数据库验证失败")
        return 1
    
    # 4. 运行基础测试
    results['basic'] = run_basic_tests()
    if not results['basic']:
        print_error("基础测试失败")
        return 1
    
    # 5. 运行单元测试
    results['unit'] = run_unit_tests()
    if not results['unit']:
        print_error("单元测试失败")
        return 1
    
    # 6. 运行集成测试
    results['integration'] = run_integration_tests()
    if not results['integration']:
        print_error("集成测试失败")
        return 1
    
    # 7. 生成覆盖率报告
    results['coverage'] = generate_coverage_report()
    if not results['coverage']:
        print_warning("覆盖率报告生成失败，但不影响测试功能")
    
    # 生成验证报告
    print_section("验证报告")
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    failed_checks = total_checks - passed_checks
    
    print(f"总验证项: {total_checks}")
    print(f"通过: {passed_checks}")
    print(f"失败: {failed_checks}")
    
    if failed_checks == 0:
        print_success("🎉 测试流程验证全部通过！")
        print_success("新机器上的测试环境已准备就绪。")
        return 0
    else:
        print_error(f"有 {failed_checks} 项验证失败，请检查并修复。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
