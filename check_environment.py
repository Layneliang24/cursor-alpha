#!/usr/bin/env python3
"""
环境检查脚本
用于验证新机器的环境是否满足Alpha项目的要求
"""

import sys
import subprocess
import platform
import os
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
    print("           Alpha 项目环境检查工具")
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

def run_command(command, capture_output=True):
    """运行命令并返回结果"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        else:
            result = subprocess.run(command, shell=True, timeout=10)
            return result.returncode == 0, "", ""
    except subprocess.TimeoutExpired:
        return False, "", "命令执行超时"
    except Exception as e:
        return False, "", str(e)

def check_python():
    """检查Python环境"""
    print_section("Python 环境检查")
    
    # 检查Python版本
    success, output, error = run_command("python --version")
    if success:
        version = output.split()[1]
        print_success(f"Python版本: {version}")
        
        # 检查版本是否满足要求
        major, minor = map(int, version.split('.')[:2])
        if major >= 3 and minor >= 8:
            print_success("Python版本满足要求 (>= 3.8)")
        else:
            print_error(f"Python版本过低: {version} (需要 >= 3.8)")
            return False
    else:
        print_error("Python未安装或未配置PATH")
        return False
    
    # 检查pip
    success, output, error = run_command("pip --version")
    if success:
        print_success("pip可用")
    else:
        print_error("pip不可用")
        return False
    
    # 检查虚拟环境模块
    success, output, error = run_command("python -c 'import venv'")
    if success:
        print_success("venv模块可用")
    else:
        print_error("venv模块不可用")
        return False
    
    return True

def check_nodejs():
    """检查Node.js环境"""
    print_section("Node.js 环境检查")
    
    # 检查Node.js版本
    success, output, error = run_command("node --version")
    if success:
        version = output.strip()
        print_success(f"Node.js版本: {version}")
        
        # 检查版本是否满足要求
        major = int(version.strip('v').split('.')[0])
        if major >= 16:
            print_success("Node.js版本满足要求 (>= 16)")
        else:
            print_error(f"Node.js版本过低: {version} (需要 >= 16)")
            return False
    else:
        print_error("Node.js未安装或未配置PATH")
        return False
    
    # 检查npm
    success, output, error = run_command("npm --version")
    if success:
        print_success(f"npm版本: {output}")
    else:
        print_error("npm不可用")
        return False
    
    return True

def check_git():
    """检查Git环境"""
    print_section("Git 环境检查")
    
    success, output, error = run_command("git --version")
    if success:
        print_success(f"Git版本: {output}")
    else:
        print_warning("Git未安装，某些功能可能受限")
        return False
    
    return True

def check_system():
    """检查系统信息"""
    print_section("系统信息")
    
    system = platform.system()
    release = platform.release()
    machine = platform.machine()
    
    print_success(f"操作系统: {system} {release}")
    print_success(f"架构: {machine}")
    
    # 检查可用内存
    if system == "Windows":
        try:
            import psutil
            memory = psutil.virtual_memory()
            total_gb = memory.total / (1024**3)
            print_success(f"总内存: {total_gb:.1f} GB")
            if total_gb < 4:
                print_warning("内存可能不足，建议至少4GB")
        except ImportError:
            print_warning("无法获取内存信息 (需要安装psutil)")
    else:
        success, output, error = run_command("free -h | grep Mem")
        if success:
            print_success(f"内存信息: {output}")
    
    return True

def check_project_structure():
    """检查项目结构"""
    print_section("项目结构检查")
    
    required_dirs = ["backend", "frontend", "tests", "docs"]
    missing_dirs = []
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print_success(f"目录存在: {dir_name}")
        else:
            print_error(f"目录缺失: {dir_name}")
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print_warning(f"缺失目录: {', '.join(missing_dirs)}")
        return False
    
    # 检查关键文件
    required_files = [
        "backend/requirements.txt",
        "backend/manage.py",
        "frontend/package.json",
        "tests/conftest.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"文件存在: {file_path}")
        else:
            print_error(f"文件缺失: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print_warning(f"缺失文件: {', '.join(missing_files)}")
        return False
    
    return True

def check_network():
    """检查网络连接"""
    print_section("网络连接检查")
    
    # 检查pip镜像
    success, output, error = run_command("pip config list")
    if success and "tuna.tsinghua.edu.cn" in output:
        print_success("已配置国内pip镜像")
    else:
        print_warning("未配置国内pip镜像，建议配置以提高下载速度")
    
    # 检查npm镜像
    success, output, error = run_command("npm config get registry")
    if success and "registry.npmmirror.com" in output:
        print_success("已配置国内npm镜像")
    else:
        print_warning("未配置国内npm镜像，建议配置以提高下载速度")
    
    return True

def generate_report(results):
    """生成检查报告"""
    print_section("检查报告")
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    failed_checks = total_checks - passed_checks
    
    print(f"总检查项: {total_checks}")
    print(f"通过: {passed_checks}")
    print(f"失败: {failed_checks}")
    
    if failed_checks == 0:
        print_success("环境检查全部通过！可以开始部署项目。")
        return True
    else:
        print_error(f"有 {failed_checks} 项检查失败，请解决后重试。")
        return False

def main():
    """主函数"""
    print_header()
    
    results = {}
    
    # 执行各项检查
    results['python'] = check_python()
    results['nodejs'] = check_nodejs()
    results['git'] = check_git()
    results['system'] = check_system()
    results['project'] = check_project_structure()
    results['network'] = check_network()
    
    # 生成报告
    all_passed = generate_report(results)
    
    # 提供建议
    if not all_passed:
        print_section("解决建议")
        print("1. 安装缺失的软件包")
        print("2. 配置环境变量PATH")
        print("3. 检查项目文件完整性")
        print("4. 配置国内镜像源以提高下载速度")
        print("\n详细部署指南请参考: docs/DEPLOYMENT_GUIDE.md")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
