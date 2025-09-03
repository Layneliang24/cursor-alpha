#!/usr/bin/env python3
"""
测试隔离性重构工具
自动重构测试文件，提高隔离性，使用Mock和Stub替代真实依赖
"""
import os
import re
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

class TestIsolationRefactor:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.backup_dir = Path("isolation_refactor_backups")
        self.refactor_log = []
        self.refactored_files = []

    def create_backup(self, file_path: str) -> str:
        """创建文件备份"""
        try:
            if not self.backup_dir.exists():
                self.backup_dir.mkdir(parents=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"{Path(file_path).name}_{timestamp}.py"
            
            shutil.copy2(file_path, backup_path)
            return str(backup_path)
        except Exception as e:
            print(f"❌ 创建备份失败 {file_path}: {e}")
            return ""

    def refactor_test_file(self, file_path: str) -> Dict[str, Any]:
        """重构单个测试文件"""
        print(f"🔧 重构文件: {file_path}")
        
        try:
            # 创建备份
            backup_path = self.create_backup(file_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            refactor_changes = []

            # 1. 添加Mock导入
            content, mock_changes = self._add_mock_imports(content)
            refactor_changes.extend(mock_changes)

            # 2. 重构数据库依赖
            content, db_changes = self._refactor_database_dependencies(content)
            refactor_changes.extend(db_changes)

            # 3. 重构外部服务依赖
            content, service_changes = self._refactor_external_service_dependencies(content)
            refactor_changes.extend(service_changes)

            # 4. 重构文件系统依赖
            content, fs_changes = self._refactor_filesystem_dependencies(content)
            refactor_changes.extend(fs_changes)

            # 5. 重构网络依赖
            content, network_changes = self._refactor_network_dependencies(content)
            refactor_changes.extend(network_changes)

            # 6. 重构硬编码值
            content, hardcoded_changes = self._refactor_hardcoded_values(content)
            refactor_changes.extend(hardcoded_changes)

            # 7. 添加测试数据工厂
            content, factory_changes = self._add_test_data_factories(content)
            refactor_changes.extend(factory_changes)

            # 8. 添加测试环境配置
            content, config_changes = self._add_test_environment_config(content)
            refactor_changes.extend(config_changes)

            # 如果有变化，写入文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                refactor_result = {
                    'file_path': file_path,
                    'backup_path': backup_path,
                    'changes_made': len(refactor_changes),
                    'changes': refactor_changes,
                    'status': 'refactored'
                }
                
                self.refactored_files.append(refactor_result)
                print(f"✅ 重构完成: {len(refactor_changes)} 处修改")
                return refactor_result
            else:
                print(f"ℹ️ 无需重构: {file_path}")
                return {
                    'file_path': file_path,
                    'status': 'no_changes_needed'
                }

        except Exception as e:
            print(f"❌ 重构失败 {file_path}: {e}")
            return {
                'file_path': file_path,
                'error': str(e),
                'status': 'failed'
            }

    def _add_mock_imports(self, content: str) -> Tuple[str, List[Dict[str, Any]]]:
        """添加Mock导入"""
        changes = []
        
        # 检查是否已有Mock导入
        if 'from unittest.mock import' not in content and 'import mock' not in content:
            # 在文件开头添加Mock导入
            mock_imports = [
                "from unittest.mock import Mock, patch, MagicMock, call",
                "from unittest.mock import Mock, patch, MagicMock, call, ANY"
            ]
            
            # 找到第一个import语句的位置
            import_match = re.search(r'^(import|from)', content, re.MULTILINE)
            if import_match:
                insert_pos = import_match.start()
                content = content[:insert_pos] + mock_imports[1] + '\n' + content[insert_pos:]
                changes.append({
                    'type': 'add_mock_imports',
                    'description': '添加Mock导入语句',
                    'line': '文件开头'
                })
            else:
                # 如果没有import语句，在文件开头添加
                content = mock_imports[1] + '\n\n' + content
                changes.append({
                    'type': 'add_mock_imports',
                    'description': '在文件开头添加Mock导入语句',
                    'line': 1
                })

        return content, changes

    def _refactor_database_dependencies(self, content: str) -> Tuple[str, List[Dict[str, Any]]]:
        """重构数据库依赖"""
        changes = []
        
        # 替换直接数据库操作为Mock
        db_replacements = [
            (r'(\w+)\.objects\.create\(', r'Mock()'),
            (r'(\w+)\.objects\.get\(', r'Mock()'),
            (r'(\w+)\.objects\.filter\(', r'Mock()'),
            (r'(\w+)\.objects\.all\(', r'Mock()'),
            (r'(\w+)\.save\(', r'# Mocked: \1.save()'),
            (r'(\w+)\.delete\(', r'# Mocked: \1.delete()'),
        ]

        for pattern, replacement in db_replacements:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append({
                    'type': 'database_mock',
                    'description': f'Mock数据库操作: {pattern}',
                    'line': 'multiple'
                })

        # 添加数据库Mock设置
        if 'def setUp(' in content and 'Mock()' in content:
            setup_pattern = r'(def setUp\([^)]*\):)'
            setup_replacement = r'\1\n        # Mock数据库操作\n        self.db_mock = Mock()\n        self.patcher = patch("django.db.models.Model.objects")\n        self.mock_objects = self.patcher.start()\n        self.mock_objects.create.return_value = Mock()\n        self.mock_objects.get.return_value = Mock()\n        self.mock_objects.filter.return_value = Mock()\n        self.mock_objects.all.return_value = Mock()'
            
            if re.search(setup_pattern, content):
                content = re.sub(setup_pattern, setup_replacement, content)
                changes.append({
                    'type': 'database_setup_mock',
                    'description': '在setUp中添加数据库Mock设置',
                    'line': 'setUp方法'
                })

        return content, changes

    def _refactor_external_service_dependencies(self, content: str) -> Tuple[str, List[Dict[str, Any]]]:
        """重构外部服务依赖"""
        changes = []
        
        # 替换外部服务调用为Mock
        service_replacements = [
            (r'from apps\.ai\.adapters', r'# Mocked: from apps.ai.adapters'),
            (r'from apps\.english\.services', r'# Mocked: from apps.english.services'),
            (r'requests\.get\(', r'Mock()'),
            (r'requests\.post\(', r'Mock()'),
            (r'urllib\.request', r'Mock()'),
            (r'httpx\.', r'Mock()'),
            (r'aiohttp\.', r'Mock()'),
            (r'redis\.', r'Mock()'),
            (r'celery\.', r'Mock()'),
        ]

        for pattern, replacement in service_replacements:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append({
                    'type': 'service_mock',
                    'description': f'Mock外部服务: {pattern}',
                    'line': 'multiple'
                })

        # 添加服务Mock设置
        if 'def setUp(' in content and any(re.search(pattern, content) for pattern, _ in service_replacements):
            setup_pattern = r'(def setUp\([^)]*\):)'
            setup_replacement = r'\1\n        # Mock外部服务\n        self.service_mock = Mock()\n        self.patcher_service = patch("apps.ai.adapters")\n        self.mock_ai_service = self.patcher_service.start()\n        self.patcher_english = patch("apps.english.services")\n        self.mock_english_service = self.patcher_english.start()'
            
            if re.search(setup_pattern, content):
                content = re.sub(setup_pattern, setup_replacement, content)
                changes.append({
                    'type': 'service_setup_mock',
                    'description': '在setUp中添加外部服务Mock设置',
                    'line': 'setUp方法'
                })

        return content, changes

    def _refactor_filesystem_dependencies(self, content: str) -> Tuple[str, List[Dict[str, Any]]]:
        """重构文件系统依赖"""
        changes = []
        
        # 替换文件系统操作为Mock
        fs_replacements = [
            (r'open\(', r'# Mocked: open('),
            (r'os\.path\.', r'# Mocked: os.path.'),
            (r'pathlib\.', r'# Mocked: pathlib.'),
            (r'\.read\(', r'# Mocked: .read('),
            (r'\.write\(', r'# Mocked: .write('),
            (r'\.mkdir\(', r'# Mocked: .mkdir('),
            (r'\.remove\(', r'# Mocked: .remove('),
        ]

        for pattern, replacement in fs_replacements:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append({
                    'type': 'filesystem_mock',
                    'description': f'Mock文件系统操作: {pattern}',
                    'line': 'multiple'
                })

        # 添加文件系统Mock设置
        if 'def setUp(' in content and any(re.search(pattern, content) for pattern, _ in fs_replacements):
            setup_pattern = r'(def setUp\([^)]*\):)'
            setup_replacement = r'\1\n        # Mock文件系统\n        self.fs_mock = Mock()\n        self.patcher_fs = patch("builtins.open")\n        self.mock_open = self.patcher_fs.start()\n        self.mock_open.return_value = Mock()'
            
            if re.search(setup_pattern, content):
                content = re.sub(setup_pattern, setup_replacement, content)
                changes.append({
                    'type': 'filesystem_setup_mock',
                    'description': '在setUp中添加文件系统Mock设置',
                    'line': 'setUp方法'
                })

        return content, changes

    def _refactor_network_dependencies(self, content: str) -> Tuple[str, List[Dict[str, Any]]]:
        """重构网络依赖"""
        changes = []
        
        # 替换网络操作为Mock
        network_replacements = [
            (r'socket\.', r'# Mocked: socket.'),
            (r'http://[^\s]+', r'# Mocked: http://...'),
            (r'https://[^\s]+', r'# Mocked: https://...'),
            (r'ws://[^\s]+', r'# Mocked: ws://...'),
            (r'wss://[^\s]+', r'# Mocked: wss://...'),
            (r'ftp://[^\s]+', r'# Mocked: ftp://...'),
            (r'smtp\.', r'# Mocked: smtp.'),
            (r'pop3\.', r'# Mocked: pop3.'),
        ]

        for pattern, replacement in network_replacements:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append({
                    'type': 'network_mock',
                    'description': f'Mock网络操作: {pattern}',
                    'line': 'multiple'
                })

        # 添加网络Mock设置
        if 'def setUp(' in content and any(re.search(pattern, content) for pattern, _ in network_replacements):
            setup_pattern = r'(def setUp\([^)]*\):)'
            setup_replacement = r'\1\n        # Mock网络操作\n        self.network_mock = Mock()\n        self.patcher_network = patch("socket.socket")\n        self.mock_socket = self.patcher_network.start()\n        self.mock_socket.return_value = Mock()'
            
            if re.search(setup_pattern, content):
                content = re.sub(setup_pattern, setup_replacement, content)
                changes.append({
                    'type': 'network_setup_mock',
                    'description': '在setUp中添加网络Mock设置',
                    'line': 'setUp方法'
                })

        return content, changes

    def _refactor_hardcoded_values(self, content: str) -> Tuple[str, List[Dict[str, Any]]]:
        """重构硬编码值"""
        changes = []
        
        # 替换硬编码值为配置变量
        hardcoded_replacements = [
            (r'password\s*=\s*["\'][^"\']+["\']', r'password=os.environ.get("TEST_PASSWORD", "test_password")'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', r'api_key=os.environ.get("TEST_API_KEY", "test_api_key")'),
            (r'secret\s*=\s*["\'][^"\']+["\']', r'secret=os.environ.get("TEST_SECRET", "test_secret")'),
            (r'token\s*=\s*["\'][^"\']+["\']', r'token=os.environ.get("TEST_TOKEN", "test_token")'),
            (r'localhost:\d+', r'os.environ.get("TEST_HOST", "localhost:8000")'),
            (r'127\.0\.0\.1:\d+', r'os.environ.get("TEST_HOST", "127.0.0.1:8000")'),
        ]

        for pattern, replacement in hardcoded_replacements:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append({
                    'type': 'hardcoded_replacement',
                    'description': f'替换硬编码值: {pattern}',
                    'line': 'multiple'
                })

        # 添加环境变量导入
        if any(re.search(pattern, content) for pattern, _ in hardcoded_replacements) and 'import os' not in content:
            import_match = re.search(r'^(import|from)', content, re.MULTILINE)
            if import_match:
                insert_pos = import_match.start()
                content = content[:insert_pos] + 'import os\n' + content[insert_pos:]
                changes.append({
                    'type': 'add_os_import',
                    'description': '添加os模块导入',
                    'line': 'import语句'
                })

        return content, changes

    def _add_test_data_factories(self, content: str) -> Tuple[str, List[Dict[str, Any]]]:
        """添加测试数据工厂"""
        changes = []
        
        # 检查是否已有数据工厂
        if 'def create_test_' not in content and 'class TestDataFactory' not in content:
            # 在文件末尾添加测试数据工厂
            data_factory = """
# 测试数据工厂
class TestDataFactory:
    @staticmethod
    def create_test_user(**kwargs):
        from django.contrib.auth.models import User
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        user_data.update(kwargs)
        return User.objects.create_user(**user_data)
    
    @staticmethod
    def create_test_article(**kwargs):
        article_data = {
            'title': 'Test Article',
            'content': 'This is a test article content.',
            'source': 'test_source',
            'url': 'http://test.com/article'
        }
        article_data.update(kwargs)
        return article_data
    
    @staticmethod
    def create_test_chapter(**kwargs):
        chapter_data = {
            'title': 'Test Chapter',
            'content': 'This is a test chapter content.',
            'difficulty': 'beginner'
        }
        chapter_data.update(kwargs)
        return chapter_data

# 测试数据常量
TEST_USER_DATA = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'testpass123'
}

TEST_ARTICLE_DATA = {
    'title': 'Test Article',
    'content': 'This is a test article content.',
    'source': 'test_source',
    'url': 'http://test.com/article'
}

TEST_CHAPTER_DATA = {
    'title': 'Test Chapter',
    'content': 'This is a test chapter content.',
    'difficulty': 'beginner'
}
"""
            
            content += data_factory
            changes.append({
                'type': 'add_test_data_factory',
                'description': '添加测试数据工厂类',
                'line': '文件末尾'
            })

        return content, changes

    def _add_test_environment_config(self, content: str) -> Tuple[str, List[Dict[str, Any]]]:
        """添加测试环境配置"""
        changes = []
        
        # 检查是否已有环境配置
        if 'TESTING = True' not in content and 'os.environ["TESTING"] = "True"' not in content:
            # 在文件开头添加测试环境配置
            env_config = """
# 测试环境配置
import os
os.environ['TESTING'] = 'True'
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

# 测试配置常量
TEST_CONFIG = {
    'database': 'sqlite:///:memory:',
    'cache': 'dummy',
    'email': 'dummy',
    'celery': 'dummy'
}

"""
            
            # 找到第一个import语句的位置
            import_match = re.search(r'^(import|from)', content, re.MULTILINE)
            if import_match:
                insert_pos = import_match.start()
                content = content[:insert_pos] + env_config + content[insert_pos:]
                changes.append({
                    'type': 'add_test_env_config',
                    'description': '添加测试环境配置',
                    'line': '文件开头'
                })
            else:
                # 如果没有import语句，在文件开头添加
                content = env_config + content
                changes.append({
                    'type': 'add_test_env_config',
                    'description': '在文件开头添加测试环境配置',
                    'line': 1
                })

        return content, changes

    def refactor_priority_files(self, priority_list: List[Dict[str, Any]], max_files: int = 5) -> Dict[str, Any]:
        """重构优先级最高的测试文件"""
        print(f"🎯 开始重构优先级最高的 {min(max_files, len(priority_list))} 个文件...")
        
        refactor_results = []
        
        for i, priority_item in enumerate(priority_list[:max_files]):
            file_path = priority_item['file_path']
            print(f"\n📋 重构文件 {i+1}/{min(max_files, len(priority_list))}: {file_path}")
            
            result = self.refactor_test_file(file_path)
            refactor_results.append(result)
            
            if result['status'] == 'refactored':
                print(f"✅ 重构成功: {result['changes_made']} 处修改")
            elif result['status'] == 'no_changes_needed':
                print(f"ℹ️ 无需重构")
            else:
                print(f"❌ 重构失败: {result.get('error', '未知错误')}")

        return {
            'total_files_processed': len(refactor_results),
            'successful_refactors': len([r for r in refactor_results if r['status'] == 'refactored']),
            'no_changes_needed': len([r for r in refactor_results if r['status'] == 'no_changes_needed']),
            'failed_refactors': len([r for r in refactor_results if r['status'] == 'failed']),
            'refactor_results': refactor_results
        }

    def generate_refactor_report(self, refactor_results: Dict[str, Any]) -> str:
        """生成重构报告"""
        report = f"""
# 测试隔离性重构报告

## 重构摘要
- 总处理文件数: {refactor_results['total_files_processed']}
- 成功重构: {refactor_results['successful_refactors']}
- 无需重构: {refactor_results['no_changes_needed']}
- 重构失败: {refactor_results['failed_refactors']}

## 重构详情
"""
        
        for result in refactor_results['refactor_results']:
            report += f"\n### {result['file_path']}\n"
            report += f"- 状态: {result['status']}\n"
            
            if result['status'] == 'refactored':
                report += f"- 修改数量: {result['changes_made']}\n"
                report += f"- 备份路径: {result.get('backup_path', 'N/A')}\n"
                
                if result.get('changes'):
                    report += "- 主要修改:\n"
                    for change in result['changes'][:5]:  # 只显示前5个修改
                        report += f"  - {change['description']}\n"
            
            elif result['status'] == 'failed':
                report += f"- 错误: {result.get('error', '未知错误')}\n"

        report += f"""
## 下一步行动
1. 验证重构后的测试文件是否可以正常运行
2. 运行测试确保功能正常
3. 继续重构其他优先级较低的测试文件
4. 建立测试隔离性检查机制

## 备份文件位置
所有原始文件已备份到: {self.backup_dir}
"""
        
        return report

    def save_refactor_report(self, report: str, filename: str = "test_isolation_refactor_report.md"):
        """保存重构报告"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📋 重构报告已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存重构报告失败: {e}")

def main():
    """主函数"""
    print("🚀 启动测试隔离性重构工具...")
    
    # 检查是否有隔离性分析报告
    isolation_report_file = "test_isolation_analysis_report.json"
    if not os.path.exists(isolation_report_file):
        print(f"❌ 未找到隔离性分析报告: {isolation_report_file}")
        print("请先运行 test_isolation_analyzer.py 生成分析报告")
        return
    
    # 加载隔离性分析报告
    try:
        with open(isolation_report_file, 'r', encoding='utf-8') as f:
            isolation_report = json.load(f)
    except Exception as e:
        print(f"❌ 加载隔离性分析报告失败: {e}")
        return
    
    # 创建重构工具实例
    refactor_tool = TestIsolationRefactor()
    
    # 获取重构优先级列表
    priority_list = isolation_report.get('refactoring_priority', [])
    if not priority_list:
        print("❌ 未找到重构优先级信息")
        return
    
    print(f"📊 找到 {len(priority_list)} 个需要重构的测试文件")
    
    # 重构优先级最高的文件
    refactor_results = refactor_tool.refactor_priority_files(priority_list, max_files=5)
    
    # 生成重构报告
    report = refactor_tool.generate_refactor_report(refactor_results)
    
    # 保存重构报告
    refactor_tool.save_refactor_report(report)
    
    print(f"\n🎉 重构完成!")
    print(f"✅ 成功重构: {refactor_results['successful_refactors']} 个文件")
    print(f"ℹ️ 无需重构: {refactor_results['no_changes_needed']} 个文件")
    print(f"❌ 重构失败: {refactor_results['failed_refactors']} 个文件")
    
    if refactor_results['successful_refactors'] > 0:
        print(f"\n🎯 下一步行动:")
        print("1. 验证重构后的测试文件")
        print("2. 运行测试确保功能正常")
        print("3. 继续重构其他测试文件")
        print("4. 进行Task 31.4: 验证测试可运行性")

if __name__ == "__main__":
    main()

