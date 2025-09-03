#!/usr/bin/env python3
"""
自动化框架迁移工具
自动将unittest+pytest混用的测试文件迁移到纯pytest框架
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

class AutomatedFrameworkMigration:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.backup_dir = Path("migration_backups")
        self.migration_log = []
        self.rollback_info = {}
        
    def load_strategy_report(self):
        """加载策略报告"""
        print("📊 加载框架统一策略报告...")
        
        try:
            # 优先使用修正后的策略报告
            strategy_file = 'corrected_framework_strategy.json'
            if not os.path.exists(strategy_file):
                # 回退到原始策略报告
                strategy_file = 'framework_unification_strategy_report.json'
                if not os.path.exists(strategy_file):
                    print("❌ 找不到策略报告文件")
                    return None
            
            with open(strategy_file, 'r', encoding='utf-8') as f:
                strategy = json.load(f)
            print(f"✅ 成功加载策略报告: {strategy_file}")
            return strategy
        except Exception as e:
            print(f"❌ 加载策略报告失败: {e}")
            return None
    
    def create_backup(self, file_path: str) -> bool:
        """创建文件备份"""
        try:
            # 创建备份目录
            self.backup_dir.mkdir(exist_ok=True)
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{Path(file_path).stem}_{timestamp}.py"
            backup_path = self.backup_dir / backup_name
            
            # 复制文件
            shutil.copy2(file_path, backup_path)
            
            # 记录备份信息
            self.rollback_info[file_path] = {
                'backup_path': str(backup_path),
                'timestamp': timestamp,
                'original_size': os.path.getsize(file_path)
            }
            
            print(f"✅ 已备份: {file_path} -> {backup_path}")
            return True
            
        except Exception as e:
            print(f"❌ 备份失败 {file_path}: {e}")
            return False
    
    def migrate_imports(self, content: str) -> str:
        """迁移导入语句"""
        print("  🔄 迁移导入语句...")
        
        # 移除unittest.TestCase继承
        content = re.sub(r'class\s+(\w+)\s*\(unittest\.TestCase\):', r'class \1:', content)
        
        # 保留pytest导入，移除unittest导入
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # 跳过unittest相关导入
            if re.match(r'^\s*import\s+unittest', line):
                continue
            if re.match(r'^\s*from\s+unittest', line):
                continue
            
            # 保留pytest和其他导入
            new_lines.append(line)
        
        # 确保pytest导入存在
        if not any('import pytest' in line for line in new_lines):
            new_lines.insert(0, 'import pytest')
        
        return '\n'.join(new_lines)
    
    def migrate_assertions(self, content: str) -> str:
        """迁移断言方法"""
        print("  🔄 迁移断言方法...")
        
        # 断言方法映射
        assertion_mapping = {
            r'self\.assertEqual\(([^,]+),\s*([^)]+)\)': r'assert \1 == \2',
            r'self\.assertNotEqual\(([^,]+),\s*([^)]+)\)': r'assert \1 != \2',
            r'self\.assertTrue\(([^)]+)\)': r'assert \1',
            r'self\.assertFalse\(([^)]+)\)': r'assert not \1',
            r'self\.assertIn\(([^,]+),\s*([^)]+)\)': r'assert \1 in \2',
            r'self\.assertNotIn\(([^,]+),\s*([^)]+)\)': r'assert \1 not in \2',
            r'self\.assertIs\(([^,]+),\s*([^)]+)\)': r'assert \1 is \2',
            r'self\.assertIsNot\(([^,]+),\s*([^)]+)\)': r'assert \1 is not \2',
            r'self\.assertIsInstance\(([^,]+),\s*([^)]+)\)': r'assert isinstance(\1, \2)',
            r'self\.assertGreater\(([^,]+),\s*([^)]+)\)': r'assert \1 > \2',
            r'self\.assertLess\(([^,]+),\s*([^)]+)\)': r'assert \1 < \2',
            r'self\.assertAlmostEqual\(([^,]+),\s*([^)]+)\)': r'assert \1 == pytest.approx(\2)'
        }
        
        for old_pattern, new_pattern in assertion_mapping.items():
            content = re.sub(old_pattern, new_pattern, content)
        
        return content
    
    def migrate_decorators(self, content: str) -> str:
        """迁移装饰器"""
        print("  🔄 迁移装饰器...")
        
        # 装饰器映射
        decorator_mapping = {
            r'@unittest\.skip\(([^)]+)\)': r'@pytest.mark.skip(reason=\1)',
            r'@unittest\.skipIf\(([^,]+),\s*([^)]+)\)': r'@pytest.mark.skipif(\1, reason=\2)',
            r'@unittest\.expectedFailure': r'@pytest.mark.xfail'
        }
        
        for old_pattern, new_pattern in decorator_mapping.items():
            content = re.sub(old_pattern, new_pattern, content)
        
        return content
    
    def migrate_setup_teardown(self, content: str) -> str:
        """迁移setup/teardown方法"""
        print("  🔄 迁移setup/teardown方法...")
        
        # 方法名映射
        method_mapping = {
            r'def\s+setUp\(self\):': 'def setup_method(self):',
            r'def\s+tearDown\(self\):': 'def teardown_method(self):',
            r'def\s+setUpClass\(cls\):': 'def setup_class(cls):',
            r'def\s+tearDownClass\(cls\):': 'def teardown_class(cls):'
        }
        
        for old_pattern, new_pattern in method_mapping.items():
            content = re.sub(old_pattern, new_pattern, content)
        
        return content
    
    def migrate_raises(self, content: str) -> str:
        """迁移异常测试"""
        print("  🔄 迁移异常测试...")
        
        # 查找self.assertRaises模式
        def replace_raises(match):
            exception_type = match.group(1)
            test_code = match.group(2)
            
            # 转换为pytest.raises格式
            return f'''with pytest.raises({exception_type}):
        {test_code}'''
        
        # 匹配self.assertRaises(Exception, function_call)模式
        content = re.sub(
            r'self\.assertRaises\(([^,]+),\s*([^)]+)\)',
            replace_raises,
            content
        )
        
        return content
    
    def validate_migration(self, file_path: str) -> bool:
        """验证迁移后的文件"""
        print(f"🔍 验证迁移结果: {file_path}")
        
        try:
            # 使用python -m py_compile进行语法检查
            result = subprocess.run(
                ['python', '-m', 'py_compile', file_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"✅ 语法验证通过: {file_path}")
                return True
            else:
                print(f"❌ 语法验证失败: {file_path}")
                print(f"错误: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ 验证超时: {file_path}")
            return False
        except Exception as e:
            print(f"❌ 验证执行错误: {file_path}: {e}")
            return False
    
    def migrate_file(self, file_path: str) -> bool:
        """迁移单个文件"""
        print(f"🚀 开始迁移文件: {file_path}")
        
        try:
            # 1. 创建备份
            if not self.create_backup(file_path):
                return False
            
            # 2. 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 3. 执行迁移步骤
            print("  🔄 迁移导入语句...")
            content = self.migrate_imports(content)
            print("  🔄 迁移断言方法...")
            content = self.migrate_assertions(content)
            print("  🔄 迁移装饰器...")
            content = self.migrate_decorators(content)
            print("  🔄 迁移setup/teardown方法...")
            content = self.migrate_setup_teardown(content)
            print("  🔄 迁移异常测试...")
            content = self.migrate_raises(content)
            
            # 4. 检查是否有变化
            if content == original_content:
                print(f"⚠️ 文件 {file_path} 无需迁移")
                return True
            
            # 5. 写入迁移后的内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 6. 验证迁移结果
            if not self.validate_migration(file_path):
                print(f"❌ 迁移验证失败: {file_path}")
                # 回滚文件
                self.rollback_file(file_path)
                return False
            
            # 7. 记录迁移日志
            self.migration_log.append({
                'file': file_path,
                'timestamp': datetime.now().isoformat(),
                'status': 'migrated',
                'changes_made': True
            })
            
            print(f"✅ 文件迁移完成: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 文件迁移失败 {file_path}: {e}")
            
            # 记录失败日志
            self.migration_log.append({
                'file': file_path,
                'timestamp': datetime.now().isoformat(),
                'status': 'failed',
                'error': str(e),
                'changes_made': False
            })
            
            return False
    
    def run_tests(self, file_path: str) -> bool:
        """运行测试验证"""
        print(f"🧪 运行测试验证: {file_path}")
        
        try:
            # 使用pytest运行测试
            result = subprocess.run(
                ['python', '-m', 'pytest', file_path, '-v'],
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                print(f"✅ 测试通过: {file_path}")
                return True
            else:
                print(f"❌ 测试失败: {file_path}")
                print(f"错误输出: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ 测试超时: {file_path}")
            return False
        except Exception as e:
            print(f"❌ 测试执行错误: {file_path}: {e}")
            return False
    
    def rollback_file(self, file_path: str) -> bool:
        """回滚文件到备份版本"""
        print(f"🔄 回滚文件: {file_path}")
        
        if file_path not in self.rollback_info:
            print(f"❌ 没有找到回滚信息: {file_path}")
            return False
        
        try:
            backup_path = self.rollback_info[file_path]['backup_path']
            
            # 恢复文件
            shutil.copy2(backup_path, file_path)
            
            print(f"✅ 文件已回滚: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 回滚失败: {file_path}: {e}")
            return False
    
    def rollback_all(self) -> bool:
        """回滚所有已迁移的文件"""
        print("🔄 开始回滚所有文件...")
        
        success_count = 0
        total_count = len(self.rollback_info)
        
        for file_path in self.rollback_info.keys():
            if self.rollback_file(file_path):
                success_count += 1
        
        print(f"✅ 回滚完成: {success_count}/{total_count} 个文件")
        return success_count == total_count
    
    def generate_migration_report(self) -> Dict:
        """生成迁移报告"""
        print("📝 生成迁移报告...")
        
        success_count = len([log for log in self.migration_log if log['status'] == 'success'])
        failed_count = len([log for log in self.migration_log if log['status'] == 'failed'])
        
        report = {
            "summary": {
                "total_files": len(self.migration_log),
                "successful": success_count,
                "failed": failed_count,
                "success_rate": f"{(success_count/len(self.migration_log)*100):.1f}%" if self.migration_log else "0%"
            },
            "migration_log": self.migration_log,
            "rollback_info": self.rollback_info,
            "timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def run_migration(self, file_list: List[str]) -> bool:
        """运行完整迁移流程"""
        print(f"🚀 开始自动化框架迁移，共 {len(file_list)} 个文件")
        
        success_count = 0
        
        for file_path in file_list:
            print(f"\n--- 处理文件 {file_path} ---")
            
            # 1. 迁移文件
            if self.migrate_file(file_path):
                # 2. 运行测试验证
                if self.run_tests(file_path):
                    success_count += 1
                    print(f"✅ 文件 {file_path} 迁移和验证成功")
                else:
                    print(f"❌ 文件 {file_path} 测试验证失败，准备回滚")
                    self.rollback_file(file_path)
            else:
                print(f"❌ 文件 {file_path} 迁移失败")
        
        # 生成迁移报告
        report = self.generate_migration_report()
        
        # 保存报告
        with open("migration_execution_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 迁移完成摘要:")
        print(f"  总文件数: {len(file_list)}")
        print(f"  成功数量: {success_count}")
        print(f"  失败数量: {len(file_list) - success_count}")
        print(f"  成功率: {report['summary']['success_rate']}")
        
        return success_count == len(file_list)

def main():
    """主函数"""
    print("🚀 启动自动化框架迁移工具...")
    
    # 创建迁移工具实例
    migrator = AutomatedFrameworkMigration()
    
    # 加载策略报告
    strategy = migrator.load_strategy_report()
    if not strategy:
        print("❌ 无法加载策略报告，迁移终止")
        return
    
    # 获取迁移文件列表（按风险等级排序）
    migration_strategy = strategy['migration_strategy']
    
    # 按阶段执行迁移
    for phase_name, phase_info in migration_strategy['phases'].items():
        print(f"\n🎯 开始执行 {phase_info['name']}")
        print(f"文件数量: {len(phase_info['files'])}")
        print(f"预计时间: {phase_info['duration']}")
        
        # 执行迁移
        success = migrator.run_migration(phase_info['files'])
        
        if success:
            print(f"✅ {phase_info['name']} 完成")
        else:
            print(f"❌ {phase_info['name']} 失败，停止后续迁移")
            break
    
    print(f"\n📋 迁移报告已保存到: migration_execution_report.json")
    print(f"📋 回滚信息已保存到迁移工具中")

if __name__ == "__main__":
    main()
