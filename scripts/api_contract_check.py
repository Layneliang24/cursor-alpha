#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API契约校验脚本
生成当前API的OpenAPI规范并与预期规范进行对比，阻断不兼容变更
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
from deepdiff import DeepDiff
from jsonschema import validate, ValidationError

# 添加Django项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'backend'))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')

try:
    import django
    django.setup()
except Exception as e:
    print(f"警告: Django初始化失败: {e}")


class APIContractChecker:
    """API契约检查器"""
    
    def __init__(self, project_root: str = None):
        if project_root:
            self.project_root = Path(project_root)
        else:
            # 自动检测项目根目录
            current_dir = Path(__file__).parent.parent
            self.project_root = current_dir
        
        self.spec_file = self.project_root / 'docs' / 'spec' / 'openapi.json'
        self.generated_spec_file = self.project_root / 'backend' / 'generated_openapi.json'
        
    def generate_openapi_spec(self) -> bool:
        """生成当前API的OpenAPI规范"""
        print("🔄 生成当前API的OpenAPI规范...")
        
        try:
            # 使用Django的管理命令生成OpenAPI规范
            cmd = [
                'python', 'manage.py', 'generate_openapi', 
                '--output', 'generated_openapi.json',
                '--format', 'json',
                '--pretty'
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root / 'backend',
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"❌ 生成OpenAPI规范失败:\n{result.stderr}")
                return False
            
            if not self.generated_spec_file.exists():
                print("❌ OpenAPI规范文件未生成")
                return False
            
            print("✅ OpenAPI规范生成成功")
            print(result.stdout)
            return True
            
        except subprocess.TimeoutExpired:
            print("❌ 生成OpenAPI规范超时")
            return False
        except Exception as e:
            print(f"❌ 生成OpenAPI规范时发生错误: {e}")
            return False
    
    def load_spec(self, file_path: Path) -> Dict[str, Any]:
        """加载OpenAPI规范文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 规范文件不存在: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ 规范文件格式错误: {e}")
            return {}
    
    def validate_openapi_spec(self, spec: Dict[str, Any]) -> bool:
        """验证OpenAPI规范格式"""
        print("🔍 验证OpenAPI规范格式...")
        
        # 基本结构检查
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in spec:
                print(f"❌ 缺少必需字段: {field}")
                return False
        
        # 版本检查
        if not spec['openapi'].startswith('3.'):
            print(f"❌ 不支持的OpenAPI版本: {spec['openapi']}")
            return False
        
        print("✅ OpenAPI规范格式验证通过")
        return True
    
    def compare_specs(self, expected_spec: Dict[str, Any], actual_spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """对比两个OpenAPI规范"""
        print("🔍 对比API规范...")
        
        issues = []
        
        # 使用DeepDiff进行深度对比
        diff = DeepDiff(
            expected_spec,
            actual_spec,
            ignore_order=True,
            exclude_paths=[
                "root['info']['version']",  # 忽略版本号变化
                "root['servers']",  # 忽略服务器配置
            ]
        )
        
        # 检查删除的路径（破坏性变更）
        if 'dictionary_item_removed' in diff:
            for removed_item in diff['dictionary_item_removed']:
                if 'paths' in str(removed_item):
                    issues.append(f"❌ 删除了API路径: {removed_item}")
        
        # 检查类型变更（破坏性变更）
        if 'type_changes' in diff:
            for type_change in diff['type_changes']:
                if 'paths' in str(type_change):
                    issues.append(f"❌ API类型发生变更: {type_change}")
        
        # 检查值变更
        if 'values_changed' in diff:
            for value_change in diff['values_changed']:
                path = str(value_change)
                if 'paths' in path and ('required' in path or 'type' in path):
                    old_val = diff['values_changed'][value_change]['old_value']
                    new_val = diff['values_changed'][value_change]['new_value']
                    issues.append(f"❌ API参数要求发生变更: {path} ({old_val} -> {new_val})")
        
        # 检查新增的路径（非破坏性变更，仅提示）
        if 'dictionary_item_added' in diff:
            for added_item in diff['dictionary_item_added']:
                if 'paths' in str(added_item):
                    print(f"ℹ️  新增API路径: {added_item}")
        
        return len(issues) == 0, issues
    
    def normalize_path(self, path: str, servers: List[dict] = None) -> str:
        """标准化路径，处理服务器前缀"""
        if servers:
            for server in servers:
                server_url = server.get('url', '')
                if server_url and path.startswith(server_url):
                    return path[len(server_url):]
        return path
    
    def find_matching_path(self, target_path: str, available_paths: dict, servers: List[dict] = None) -> str:
        """查找匹配的路径，考虑服务器前缀"""
        # 直接匹配
        if target_path in available_paths:
            return target_path
        
        # 如果有服务器配置，尝试添加前缀匹配
        if servers:
            for server in servers:
                server_url = server.get('url', '')
                if server_url:
                    full_path = server_url.rstrip('/') + target_path
                    if full_path in available_paths:
                        return full_path
        
        # 尝试移除前缀匹配
        for available_path in available_paths:
            if available_path.endswith(target_path):
                return available_path
        
        return None
    
    def check_backward_compatibility(self, expected_spec: Dict[str, Any], actual_spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """检查向后兼容性"""
        print("🔍 检查向后兼容性...")
        
        issues = []
        
        expected_paths = expected_spec.get('paths', {})
        actual_paths = actual_spec.get('paths', {})
        expected_servers = expected_spec.get('servers', [])
        actual_servers = actual_spec.get('servers', [])
        
        # 检查是否删除了现有的API路径
        for path, methods in expected_paths.items():
            # 查找匹配的当前路径
            matching_path = self.find_matching_path(path, actual_paths, actual_servers)
            
            if not matching_path:
                issues.append(f"❌ 删除了API路径: {path}")
                continue
            
            # 检查是否删除了现有的HTTP方法
            for method, spec in methods.items():
                if method not in actual_paths[matching_path]:
                    issues.append(f"❌ 删除了HTTP方法: {method.upper()} {path}")
                    continue
                
                # 检查请求参数的兼容性
                self._check_parameters_compatibility(
                    path, method, 
                    spec.get('parameters', []),
                    actual_paths[matching_path][method].get('parameters', []),
                    issues
                )
                
                # 检查请求体的兼容性
                self._check_request_body_compatibility(
                    path, method,
                    spec.get('requestBody'),
                    actual_paths[matching_path][method].get('requestBody'),
                    issues
                )
        
        return len(issues) == 0, issues
    
    def _check_parameters_compatibility(self, path: str, method: str, 
                                      expected_params: List[Dict], 
                                      actual_params: List[Dict], 
                                      issues: List[str]) -> None:
        """检查参数兼容性"""
        expected_param_names = {p['name'] for p in expected_params if p.get('required', False)}
        actual_param_names = {p['name'] for p in actual_params if p.get('required', False)}
        
        # 检查是否删除了必需参数
        removed_required_params = expected_param_names - actual_param_names
        for param in removed_required_params:
            issues.append(f"❌ 删除了必需参数: {method.upper()} {path} - {param}")
        
        # 检查参数类型是否发生变化
        expected_params_dict = {p['name']: p for p in expected_params}
        actual_params_dict = {p['name']: p for p in actual_params}
        
        for param_name in expected_param_names & actual_param_names:
            expected_param = expected_params_dict[param_name]
            actual_param = actual_params_dict[param_name]
            
            expected_type = expected_param.get('schema', {}).get('type')
            actual_type = actual_param.get('schema', {}).get('type')
            
            if expected_type != actual_type:
                issues.append(f"❌ 参数类型发生变化: {method.upper()} {path} - {param_name} ({expected_type} -> {actual_type})")
    
    def _check_request_body_compatibility(self, path: str, method: str,
                                        expected_body: Dict,
                                        actual_body: Dict,
                                        issues: List[str]) -> None:
        """检查请求体兼容性"""
        if not expected_body:
            return
        
        if not actual_body:
            issues.append(f"❌ 删除了请求体: {method.upper()} {path}")
            return
        
        # 检查Content-Type
        expected_content = expected_body.get('content', {})
        actual_content = actual_body.get('content', {})
        
        for content_type in expected_content:
            if content_type not in actual_content:
                issues.append(f"❌ 删除了Content-Type: {method.upper()} {path} - {content_type}")
    
    def generate_compatibility_report(self, issues: List[str]) -> str:
        """生成兼容性报告"""
        if not issues:
            return "✅ API契约检查通过，无兼容性问题"
        
        report = "❌ API契约检查失败，发现以下兼容性问题:\n\n"
        for i, issue in enumerate(issues, 1):
            report += f"{i}. {issue}\n"
        
        report += "\n💡 建议:\n"
        report += "- 不要删除现有的API路径或HTTP方法\n"
        report += "- 不要删除必需的请求参数\n"
        report += "- 不要更改参数的数据类型\n"
        report += "- 新增功能应该向后兼容\n"
        
        return report
    
    def run_check(self) -> bool:
        """运行完整的API契约检查"""
        print("🚀 开始API契约检查")
        print("=" * 50)
        
        # 生成当前API规范
        if not self.generate_openapi_spec():
            return False
        
        # 加载规范文件
        expected_spec = self.load_spec(self.spec_file)
        actual_spec = self.load_spec(self.generated_spec_file)
        
        if not expected_spec or not actual_spec:
            return False
        
        # 验证规范格式
        if not self.validate_openapi_spec(actual_spec):
            return False
        
        # 检查向后兼容性
        is_compatible, issues = self.check_backward_compatibility(expected_spec, actual_spec)
        
        # 生成报告
        report = self.generate_compatibility_report(issues)
        print("\n" + "=" * 50)
        print("📊 API契约检查报告")
        print("=" * 50)
        print(report)
        
        # 清理临时文件
        if self.generated_spec_file.exists():
            self.generated_spec_file.unlink()
        
        return is_compatible


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="API契约校验工具")
    parser.add_argument("--project-root", help="项目根目录路径")
    parser.add_argument("--fail-on-incompatible", action="store_true", 
                       help="发现不兼容变更时返回非零退出码")
    
    args = parser.parse_args()
    
    checker = APIContractChecker(args.project_root)
    
    try:
        is_compatible = checker.run_check()
        
        if not is_compatible and args.fail_on_incompatible:
            print("\n💥 API契约检查失败，存在不兼容变更")
            sys.exit(1)
        elif is_compatible:
            print("\n🎉 API契约检查通过")
            sys.exit(0)
        else:
            print("\n⚠️  发现API变更，请确认是否符合预期")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 API契约检查过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()