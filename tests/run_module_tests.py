#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化测试执行脚本
用于执行特定模块的测试
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ['TESTING'] = 'true'
os.environ['DJANGO_SETTINGS_MODULE'] = 'alpha.settings'


class ModuleTestRunner:
    """模块测试运行器"""
    
    def __init__(self):
        self.project_root = project_root
        self.tests_dir = project_root / 'tests'
        self.available_modules = self._get_available_modules()
    
    def _get_available_modules(self):
        """获取可用的测试模块"""
        modules = []
        regression_dir = self.tests_dir / 'regression'
        
        if regression_dir.exists():
            for item in regression_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    modules.append(item.name)
        
        return sorted(modules)
    
    def show_available_modules(self):
        """显示可用的测试模块"""
        print("📦 可用的测试模块:")
        print("-" * 40)
        
        if not self.available_modules:
            print("❌ 没有找到可用的测试模块")
            print("请先创建 tests/regression/ 目录下的模块测试")
            return
        
        for i, module in enumerate(self.available_modules, 1):
            print(f"{i:2d}. {module}")
        
        print(f"\n总计: {len(self.available_modules)} 个模块")
    
    def run_module_test(self, module_name, test_type='all'):
        """运行指定模块的测试"""
        if module_name not in self.available_modules:
            print(f"❌ 模块 '{module_name}' 不存在")
            print(f"可用模块: {', '.join(self.available_modules)}")
            return False
        
        module_path = self.tests_dir / 'regression' / module_name
        
        print(f"🚀 开始执行 {module_name} 模块测试")
        print(f"模块路径: {module_path}")
        print("-" * 50)
        
        # 根据测试类型选择命令
        if test_type == 'unit':
            command = f"python -m pytest {module_path}/ -k 'unit' -v --html=tests/reports/html/{module_name}_unit_report.html"
        elif test_type == 'api':
            command = f"python -m pytest {module_path}/ -k 'api' -v --html=tests/reports/html/{module_name}_api_report.html"
        elif test_type == 'integration':
            command = f"python -m pytest {module_path}/ -k 'integration' -v --html=tests/reports/html/{module_name}_integration_report.html"
        else:
            command = f"python -m pytest {module_path}/ -v --html=tests/reports/html/{module_name}_report.html"
        
        print(f"执行命令: {command}")
        print()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print(f"✅ {module_name} 模块测试执行成功")
                return True
            else:
                print(f"❌ {module_name} 模块测试执行失败")
                return False
                
        except Exception as e:
            print(f"❌ 执行测试时出错: {e}")
            return False
    
    def run_multiple_modules(self, module_names, test_type='all'):
        """运行多个模块的测试"""
        if not module_names:
            print("❌ 未指定要测试的模块")
            return False
        
        success_count = 0
        total_count = len(module_names)
        
        print(f"🚀 开始执行 {total_count} 个模块的测试")
        print("=" * 60)
        
        for module_name in module_names:
            if module_name in self.available_modules:
                success = self.run_module_test(module_name, test_type)
                if success:
                    success_count += 1
                print()
            else:
                print(f"⚠️  跳过不存在的模块: {module_name}")
                print()
        
        print("=" * 60)
        print(f"📊 测试执行完成")
        print(f"成功: {success_count}/{total_count}")
        print(f"失败: {total_count - success_count}/{total_count}")
        
        return success_count == total_count
    
    def run_all_modules(self, test_type='all'):
        """运行所有模块的测试"""
        return self.run_multiple_modules(self.available_modules, test_type)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Alpha项目模块化测试执行器')
    parser.add_argument('modules', nargs='*', help='要测试的模块名称（不指定则显示可用模块）')
    parser.add_argument('--type', choices=['all', 'unit', 'api', 'integration'], 
                       default='all', help='测试类型')
    parser.add_argument('--all', action='store_true', help='运行所有模块的测试')
    parser.add_argument('--list', action='store_true', help='列出可用的测试模块')
    
    args = parser.parse_args()
    
    runner = ModuleTestRunner()
    
    try:
        # 显示可用模块
        if args.list or not args.modules and not args.all:
            runner.show_available_modules()
            return
        
        # 确定要测试的模块
        if args.all:
            modules_to_test = runner.available_modules
        else:
            modules_to_test = args.modules
        
        if not modules_to_test:
            print("❌ 没有可测试的模块")
            return
        
        # 执行测试
        if len(modules_to_test) == 1:
            success = runner.run_module_test(modules_to_test[0], args.type)
        else:
            success = runner.run_multiple_modules(modules_to_test, args.type)
        
        if success:
            print("\n🎉 所有模块测试执行完成！")
            sys.exit(0)
        else:
            print("\n💥 部分模块测试执行失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  测试执行被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试执行过程中出现未预期的错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
# -*- coding: utf-8 -*-
"""
模块化测试执行脚本
用于执行特定模块的测试
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ['TESTING'] = 'true'
os.environ['DJANGO_SETTINGS_MODULE'] = 'alpha.settings'


class ModuleTestRunner:
    """模块测试运行器"""
    
    def __init__(self):
        self.project_root = project_root
        self.tests_dir = project_root / 'tests'
        self.available_modules = self._get_available_modules()
    
    def _get_available_modules(self):
        """获取可用的测试模块"""
        modules = []
        regression_dir = self.tests_dir / 'regression'
        
        if regression_dir.exists():
            for item in regression_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    modules.append(item.name)
        
        return sorted(modules)
    
    def show_available_modules(self):
        """显示可用的测试模块"""
        print("📦 可用的测试模块:")
        print("-" * 40)
        
        if not self.available_modules:
            print("❌ 没有找到可用的测试模块")
            print("请先创建 tests/regression/ 目录下的模块测试")
            return
        
        for i, module in enumerate(self.available_modules, 1):
            print(f"{i:2d}. {module}")
        
        print(f"\n总计: {len(self.available_modules)} 个模块")
    
    def run_module_test(self, module_name, test_type='all'):
        """运行指定模块的测试"""
        if module_name not in self.available_modules:
            print(f"❌ 模块 '{module_name}' 不存在")
            print(f"可用模块: {', '.join(self.available_modules)}")
            return False
        
        module_path = self.tests_dir / 'regression' / module_name
        
        print(f"🚀 开始执行 {module_name} 模块测试")
        print(f"模块路径: {module_path}")
        print("-" * 50)
        
        # 根据测试类型选择命令
        if test_type == 'unit':
            command = f"python -m pytest {module_path}/ -k 'unit' -v --html=tests/reports/html/{module_name}_unit_report.html"
        elif test_type == 'api':
            command = f"python -m pytest {module_path}/ -k 'api' -v --html=tests/reports/html/{module_name}_api_report.html"
        elif test_type == 'integration':
            command = f"python -m pytest {module_path}/ -k 'integration' -v --html=tests/reports/html/{module_name}_integration_report.html"
        else:
            command = f"python -m pytest {module_path}/ -v --html=tests/reports/html/{module_name}_report.html"
        
        print(f"执行命令: {command}")
        print()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print(f"✅ {module_name} 模块测试执行成功")
                return True
            else:
                print(f"❌ {module_name} 模块测试执行失败")
                return False
                
        except Exception as e:
            print(f"❌ 执行测试时出错: {e}")
            return False
    
    def run_multiple_modules(self, module_names, test_type='all'):
        """运行多个模块的测试"""
        if not module_names:
            print("❌ 未指定要测试的模块")
            return False
        
        success_count = 0
        total_count = len(module_names)
        
        print(f"🚀 开始执行 {total_count} 个模块的测试")
        print("=" * 60)
        
        for module_name in module_names:
            if module_name in self.available_modules:
                success = self.run_module_test(module_name, test_type)
                if success:
                    success_count += 1
                print()
            else:
                print(f"⚠️  跳过不存在的模块: {module_name}")
                print()
        
        print("=" * 60)
        print(f"📊 测试执行完成")
        print(f"成功: {success_count}/{total_count}")
        print(f"失败: {total_count - success_count}/{total_count}")
        
        return success_count == total_count
    
    def run_all_modules(self, test_type='all'):
        """运行所有模块的测试"""
        return self.run_multiple_modules(self.available_modules, test_type)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Alpha项目模块化测试执行器')
    parser.add_argument('modules', nargs='*', help='要测试的模块名称（不指定则显示可用模块）')
    parser.add_argument('--type', choices=['all', 'unit', 'api', 'integration'], 
                       default='all', help='测试类型')
    parser.add_argument('--all', action='store_true', help='运行所有模块的测试')
    parser.add_argument('--list', action='store_true', help='列出可用的测试模块')
    
    args = parser.parse_args()
    
    runner = ModuleTestRunner()
    
    try:
        # 显示可用模块
        if args.list or not args.modules and not args.all:
            runner.show_available_modules()
            return
        
        # 确定要测试的模块
        if args.all:
            modules_to_test = runner.available_modules
        else:
            modules_to_test = args.modules
        
        if not modules_to_test:
            print("❌ 没有可测试的模块")
            return
        
        # 执行测试
        if len(modules_to_test) == 1:
            success = runner.run_module_test(modules_to_test[0], args.type)
        else:
            success = runner.run_multiple_modules(modules_to_test, args.type)
        
        if success:
            print("\n🎉 所有模块测试执行完成！")
            sys.exit(0)
        else:
            print("\n💥 部分模块测试执行失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  测试执行被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试执行过程中出现未预期的错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
