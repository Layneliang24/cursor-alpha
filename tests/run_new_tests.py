#!/usr/bin/env python
"""
运行新创建的测试用例
验证用户认证、英语学习和文章管理功能的测试
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(backend_dir))

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.test_settings_mysql')
os.environ.setdefault('TESTING', 'true')

def run_tests(test_files):
    """运行指定的测试文件"""
    print("=" * 60)
    print("开始运行新创建的测试用例")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        print(f"\n📋 运行测试文件: {test_file}")
        print("-" * 40)
        
        try:
            # 运行测试
            result = subprocess.run([
                sys.executable, '-m', 'pytest', test_file,
                '-v', '--tb=short', '--no-header'
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            # 解析结果
            if result.returncode == 0:
                print("✅ 测试通过")
                # 统计通过的测试数量
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'PASSED' in line:
                        total_passed += 1
            else:
                print("❌ 测试失败")
                print("错误输出:")
                print(result.stderr)
                # 统计失败的测试数量
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'FAILED' in line:
                        total_failed += 1
            
            # 显示测试输出摘要
            output_lines = result.stdout.split('\n')
            for line in output_lines[-10:]:  # 显示最后10行
                if line.strip():
                    print(line)
                    
        except Exception as e:
            print(f"❌ 运行测试时出错: {e}")
            total_failed += 1
    
    # 显示总结
    print("\n" + "=" * 60)
    print("测试执行总结")
    print("=" * 60)
    print(f"✅ 通过的测试: {total_passed}")
    print(f"❌ 失败的测试: {total_failed}")
    print(f"📊 总计: {total_passed + total_failed}")
    
    if total_failed == 0:
        print("\n🎉 所有测试都通过了！")
        return True
    else:
        print(f"\n⚠️  有 {total_failed} 个测试失败，需要检查")
        return False

def main():
    """主函数"""
    # 新创建的测试文件列表
    test_files = [
        'tests/unit/test_user_auth.py',
        'tests/unit/test_english_learning.py', 
        'tests/unit/test_article_management.py'
    ]
    
    print("🧪 新创建测试用例验证脚本")
    print("=" * 60)
    print("测试文件:")
    for test_file in test_files:
        print(f"  - {test_file}")
    
    # 检查测试文件是否存在
    missing_files = []
    for test_file in test_files:
        if not Path(test_file).exists():
            missing_files.append(test_file)
    
    if missing_files:
        print(f"\n❌ 以下测试文件不存在:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    # 运行测试
    success = run_tests(test_files)
    
    if success:
        print("\n📝 测试用例创建完成，可以继续补充其他模块的测试")
    else:
        print("\n🔧 需要修复失败的测试用例")
    
    return success

if __name__ == '__main__':
    main() 