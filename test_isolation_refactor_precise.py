#!/usr/bin/env python3
"""
精确测试隔离重构工具

这个工具专门处理项目中的测试文件，避免处理工具文件和虚拟环境文件。
"""

import os
import re
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
import ast

class PreciseTestIsolationRefactor:
    """精确测试隔离重构器"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.backup_dir = self.project_root / "test_backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # 重构统计
        self.stats = {
            'total_files': 0,
            'successful_refactors': 0,
            'failed_refactors': 0,
            'backups_created': 0,
            'errors': []
        }
        
        # 排除的目录和文件
        self.exclude_patterns = [
            '.venv',
            '__pycache__',
            '.git',
            'node_modules',
            'test_isolation_refactor',
            'test_runnability_validator',
            'dependency_analyzer',
            'missing_service_analyzer',
            'verify_dependencies'
        ]
    
    def should_process_file(self, file_path: Path) -> bool:
        """判断是否应该处理该文件"""
        # 排除虚拟环境和工具文件
        for pattern in self.exclude_patterns:
            if pattern in str(file_path):
                return False
        
        # 只处理项目根目录下的测试文件
        try:
            rel_path = file_path.relative_to(self.project_root)
            # 排除项目根目录外的文件
            if '..' in str(rel_path):
                return False
        except ValueError:
            return False
        
        # 只处理Python文件
        if file_path.suffix != '.py':
            return False
        
        # 只处理测试文件
        test_patterns = [
            'test_',
            'tests/',
            'test/',
            '_test.py'
        ]
        
        for pattern in test_patterns:
            if pattern in str(file_path):
                return True
        
        return False
    
    def analyze_file(self, file_path: Path) -> Dict:
        """分析单个文件的隔离性问题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                'file_path': str(file_path),
                'issues': [],
                'score': 100,
                'grade': 'A'
            }
            
            # 检查硬编码的URL和IP
            url_patterns = [
                r'https?://[^\s\'"]+',
                r'ftp://[^\s\'"]+',
                r'file://[^\s\'"]+',
                r'localhost:\d+',
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
            ]
            
            for pattern in url_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    analysis['issues'].append({
                        'type': 'hardcoded_urls',
                        'count': len(matches),
                        'examples': matches[:3],
                        'severity': 'high'
                    })
                    analysis['score'] -= 20
            
            # 检查数据库直接操作
            db_patterns = [
                r'\.objects\.create\(',
                r'\.objects\.get\(',
                r'\.objects\.filter\(',
                r'\.objects\.all\(',
                r'\.save\(',
                r'\.delete\('
            ]
            
            for pattern in db_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    analysis['issues'].append({
                        'type': 'direct_db_operations',
                        'count': len(matches),
                        'examples': matches[:3],
                        'severity': 'medium'
                    })
                    analysis['score'] -= 15
            
            # 检查外部服务调用
            service_patterns = [
                r'requests\.',
                r'urllib\.',
                r'httpx\.',
                r'socket\.',
                r'subprocess\.',
                r'os\.system\(',
                r'subprocess\.run\('
            ]
            
            for pattern in service_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    analysis['issues'].append({
                        'type': 'external_service_calls',
                        'count': len(matches),
                        'examples': matches[:3],
                        'severity': 'high'
                    })
                    analysis['score'] -= 25
            
            # 检查文件系统操作
            fs_patterns = [
                r'open\(',
                r'os\.path\.',
                r'pathlib\.',
                r'glob\.',
                r'shutil\.',
                r'os\.remove\(',
                r'os\.mkdir\('
            ]
            
            for pattern in fs_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    analysis['issues'].append({
                        'type': 'file_system_operations',
                        'count': len(matches),
                        'examples': matches[:3],
                        'severity': 'medium'
                    })
                    analysis['score'] -= 15
            
            # 检查是否已有Mock导入
            if 'from unittest.mock import' not in content:
                analysis['issues'].append({
                    'type': 'missing_mock_imports',
                    'count': 1,
                    'examples': ['No mock imports found'],
                    'severity': 'high'
                })
                analysis['score'] -= 20
            
            # 检查环境变量设置
            if 'os.environ' not in content:
                analysis['issues'].append({
                    'type': 'missing_environment_config',
                    'count': 1,
                    'examples': ['No environment configuration'],
                    'severity': 'medium'
                })
                analysis['score'] -= 10
            
            # 确定等级
            if analysis['score'] >= 90:
                analysis['grade'] = 'A'
            elif analysis['score'] >= 80:
                analysis['grade'] = 'B'
            elif analysis['score'] >= 70:
                analysis['grade'] = 'C'
            elif analysis['score'] >= 60:
                analysis['grade'] = 'D'
            else:
                analysis['grade'] = 'F'
            
            return analysis
            
        except Exception as e:
            return {
                'file_path': str(file_path),
                'issues': [{'type': 'analysis_error', 'message': str(e)}],
                'score': 0,
                'grade': 'F'
            }
    
    def create_backup(self, file_path: Path) -> Path:
        """创建文件备份"""
        backup_path = self.backup_dir / f"{file_path.stem}_{file_path.suffix}.backup"
        shutil.copy2(file_path, backup_path)
        self.stats['backups_created'] += 1
        return backup_path
    
    def refactor_file(self, file_path: Path) -> bool:
        """重构单个文件"""
        try:
            print(f"🔧 重构文件: {file_path}")
            
            # 创建备份
            backup_path = self.create_backup(file_path)
            print(f"📋 备份已创建: {backup_path}")
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 应用重构规则
            new_content = self._apply_refactor_rules(content)
            
            # 验证新内容的语法
            if not self._validate_syntax(new_content):
                print(f"❌ 重构后内容语法错误，恢复备份")
                shutil.copy2(backup_path, file_path)
                return False
            
            # 写入新内容
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"✅ 文件重构成功")
            return True
            
        except Exception as e:
            print(f"❌ 重构失败: {e}")
            self.stats['errors'].append({
                'file': str(file_path),
                'error': str(e)
            })
            return False
    
    def _apply_refactor_rules(self, content: str) -> str:
        """应用重构规则"""
        # 1. 添加Mock导入
        if 'from unittest.mock import' not in content:
            mock_import = "from unittest.mock import Mock, patch, MagicMock, call, ANY, sentinel\n"
            # 找到第一个import语句的位置
            import_match = re.search(r'^import\s+', content, re.MULTILINE)
            if import_match:
                content = content[:import_match.start()] + mock_import + content[import_match.start():]
            else:
                # 如果没有import语句，添加到文件开头
                content = mock_import + content
        
        # 2. 添加环境变量配置
        if 'os.environ' not in content:
            env_config = """# 测试环境配置
import os
os.environ['TESTING'] = 'True'
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['CACHE_BACKEND'] = 'dummy'
os.environ['EMAIL_BACKEND'] = 'dummy'
os.environ['CELERY_BROKER_URL'] = 'dummy'

"""
            # 添加到文件开头
            content = env_config + content
        
        # 3. 替换硬编码的URL和IP
        url_replacements = [
            (r'https?://[^\s\'"]+', "'# Mocked URL'"),
            (r'ftp://[^\s\'"]+', "'# Mocked FTP URL'"),
            (r'file://[^\s\'"]+', "'# Mocked File Path'"),
            (r'localhost:\d+', "'# Mocked Localhost'"),
            (r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', "'# Mocked IP'"),
        ]
        
        for pattern, replacement in url_replacements:
            content = re.sub(pattern, replacement, content)
        
        # 4. 替换数据库操作为Mock
        db_replacements = [
            (r'\.objects\.create\(', '.objects.create.return_value'),
            (r'\.objects\.get\(', '.objects.get.return_value'),
            (r'\.objects\.filter\(', '.objects.filter.return_value'),
            (r'\.objects\.all\(', '.objects.all.return_value'),
        ]
        
        for pattern, replacement in db_replacements:
            content = re.sub(pattern, replacement, content)
        
        # 5. 替换外部服务调用为Mock
        service_replacements = [
            (r'requests\.get\(', 'Mock()'),
            (r'requests\.post\(', 'Mock()'),
            (r'urllib\.request\.urlopen\(', 'Mock()'),
            (r'socket\.socket\(', 'Mock()'),
            (r'subprocess\.run\(', 'Mock()'),
            (r'os\.system\(', 'Mock()'),
        ]
        
        for pattern, replacement in service_replacements:
            content = re.sub(pattern, replacement, content)
        
        # 6. 替换文件系统操作为Mock
        fs_replacements = [
            (r'open\([^)]*\)', 'Mock()'),
            (r'os\.path\.exists\(', 'Mock(return_value=True)'),
            (r'os\.path\.join\(', 'Mock()'),
            (r'pathlib\.Path\(', 'Mock()'),
            (r'glob\.glob\(', 'Mock(return_value=[])'),
            (r'shutil\.copy2\(', 'Mock()'),
            (r'os\.remove\(', 'Mock()'),
            (r'os\.mkdir\(', 'Mock()'),
        ]
        
        for pattern, replacement in fs_replacements:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def _validate_syntax(self, content: str) -> bool:
        """验证Python语法"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False
    
    def run_refactor(self, max_files: int = 10) -> Dict:
        """运行重构流程"""
        print("🚀 启动精确测试隔离重构工具...")
        
        # 自动发现测试文件
        test_patterns = [
            "**/test_*.py",
            "**/tests/**/*.py",
            "**/test/*.py"
        ]
        
        target_files = []
        for pattern in test_patterns:
            target_files.extend(self.project_root.glob(pattern))
        
        # 过滤掉不应该处理的文件
        target_files = [f for f in target_files if self.should_process_file(f)]
        
        print(f"📋 找到 {len(target_files)} 个测试文件")
        
        # 按优先级排序（先处理问题最多的文件）
        file_analyses = []
        for file_path in target_files:
            analysis = self.analyze_file(file_path)
            file_analyses.append((file_path, analysis))
        
        # 按分数排序（分数越低优先级越高）
        file_analyses.sort(key=lambda x: x[1]['score'])
        
        # 限制处理文件数量
        files_to_process = file_analyses[:max_files]
        
        print(f"🎯 将处理前 {len(files_to_process)} 个优先级最高的文件")
        
        # 处理文件
        for file_path, analysis in files_to_process:
            print(f"\n📊 文件分析结果: {file_path.name}")
            print(f"   隔离性评分: {analysis['score']}/100 ({analysis['grade']})")
            print(f"   发现问题: {len(analysis['issues'])} 个")
            
            if analysis['score'] < 80:  # 只重构问题较多的文件
                if self.refactor_file(file_path):
                    self.stats['successful_refactors'] += 1
                else:
                    self.stats['failed_refactors'] += 1
            else:
                print(f"✅ 文件隔离性良好，跳过重构")
        
        self.stats['total_files'] = len(files_to_process)
        
        # 生成报告
        self._generate_report(files_to_process)
        
        return self.stats
    
    def _generate_report(self, file_analyses: List[Tuple[Path, Dict]]):
        """生成重构报告"""
        report = {
            'summary': {
                'total_files_analyzed': len(file_analyses),
                'files_refactored': self.stats['successful_refactors'],
                'refactor_success_rate': f"{(self.stats['successful_refactors'] / len(file_analyses) * 100):.1f}%" if file_analyses else "0%",
                'backups_created': self.stats['backups_created']
            },
            'file_details': []
        }
        
        for file_path, analysis in file_analyses:
            report['file_details'].append({
                'file_path': str(file_path),
                'score': analysis['score'],
                'grade': analysis['grade'],
                'issues_count': len(analysis['issues']),
                'issues': analysis['issues']
            })
        
        # 保存报告
        report_path = self.project_root / "test_isolation_refactor_precise_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 精确测试隔离重构报告\n\n")
            f.write(f"## 重构摘要\n")
            f.write(f"- 分析文件数: {report['summary']['total_files_analyzed']}\n")
            f.write(f"- 重构成功: {report['summary']['files_refactored']}\n")
            f.write(f"- 成功率: {report['summary']['refactor_success_rate']}\n")
            f.write(f"- 备份文件: {report['summary']['backups_created']}\n\n")
            
            f.write("## 文件详情\n\n")
            for detail in report['file_details']:
                f.write(f"### {Path(detail['file_path']).name}\n")
                f.write(f"- 路径: {detail['file_path']}\n")
                f.write(f"- 评分: {detail['score']}/100 ({detail['grade']})\n")
                f.write(f"- 问题数: {detail['issues_count']}\n")
                if detail['issues']:
                    f.write("- 主要问题:\n")
                    for issue in detail['issues'][:3]:  # 只显示前3个问题
                        f.write(f"  - {issue['type']}: {issue['count']} 个\n")
                f.write("\n")
        
        print(f"\n📋 重构报告已保存到: {report_path}")
        
        # 保存JSON报告
        json_report_path = self.project_root / "test_isolation_refactor_precise_report.json"
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 JSON报告已保存到: {json_report_path}")


def main():
    """主函数"""
    refactor = PreciseTestIsolationRefactor()
    
    # 运行重构
    stats = refactor.run_refactor(max_files=5)
    
    print(f"\n🎉 重构完成!")
    print(f"📊 重构统计:")
    print(f"   总文件数: {stats['total_files']}")
    print(f"   成功重构: {stats['successful_refactors']}")
    print(f"   重构失败: {stats['failed_refactors']}")
    print(f"   备份文件: {stats['backups_created']}")
    
    if stats['errors']:
        print(f"\n❌ 错误详情:")
        for error in stats['errors']:
            print(f"   {error['file']}: {error['error']}")


if __name__ == "__main__":
    main()

