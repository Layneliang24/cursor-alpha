#!/usr/bin/env python3
"""
需求→测试→实现流水线测试脚本

用于验证流水线的基本功能是否正常工作
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from req_to_test_pipeline import (
    RequirementParser,
    TestGenerator,
    CodeGenerator,
    PipelineManager
)


def test_requirement_parser():
    """测试需求解析器"""
    print("🧪 测试需求解析器...")
    
    parser = RequirementParser()
    
    # 测试文本解析
    text = """
标题: 测试功能
类型: feature
优先级: medium
组件: backend, frontend
描述: 这是一个测试功能的描述
验收标准:
- 功能可以正常工作
- 界面友好易用
预估工时: 8
负责人: developer
    """
    
    req = parser.parse_from_text(text, "test_feature")
    
    assert req.id == "test_feature"
    assert req.title == "测试功能"
    assert req.type == "feature"
    assert req.priority == "medium"
    assert "backend" in req.components
    assert "frontend" in req.components
    assert len(req.acceptance_criteria) == 2
    assert req.estimated_hours == 8
    assert req.assignee == "developer"
    
    print("✅ 需求解析器测试通过")
    return True


def test_test_generator():
    """测试测试生成器"""
    print("🧪 测试测试生成器...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        generator = TestGenerator(temp_dir)
        
        # 创建测试需求
        from req_to_test_pipeline import Requirement
        req = Requirement(
            id="test_feature",
            title="测试功能",
            description="测试功能描述",
            type="feature",
            priority="medium",
            components=["backend", "frontend"],
            acceptance_criteria=["功能正常工作", "界面友好"],
            dependencies=[],
            estimated_hours=8
        )
        
        # 生成单元测试
        unit_tests = generator.generate_unit_tests(req)
        assert len(unit_tests) == 2  # backend + frontend
        
        # 检查Django测试
        django_test = next(t for t in unit_tests if 'backend' in t.file_path)
        assert 'TestTestFeature' in django_test.content
        assert 'def test_test_feature_basic_functionality' in django_test.content
        
        # 检查Vue测试
        vue_test = next(t for t in unit_tests if 'frontend' in t.file_path)
        assert 'TestFeatureComponent' in vue_test.content
        assert 'should render correctly' in vue_test.content
        
        # 生成集成测试
        integration_tests = generator.generate_integration_tests(req)
        assert len(integration_tests) == 1
        
        # 生成E2E测试
        e2e_tests = generator.generate_e2e_tests(req)
        assert len(e2e_tests) == 1
        
    print("✅ 测试生成器测试通过")
    return True


def test_code_generator():
    """测试代码生成器"""
    print("🧪 测试代码生成器...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        generator = CodeGenerator(temp_dir)
        
        # 创建测试需求
        from req_to_test_pipeline import Requirement
        req = Requirement(
            id="test_feature",
            title="测试功能",
            description="测试功能描述",
            type="feature",
            priority="medium",
            components=["backend", "frontend"],
            acceptance_criteria=["功能正常工作"],
            dependencies=[],
            estimated_hours=8
        )
        
        # 生成代码模板
        templates = generator.generate_code_templates(req)
        assert len(templates) >= 4  # model, view, serializer, component, service
        
        # 检查Django模型
        model_template = next(t for t in templates if t.template_type == 'model')
        assert 'class TestFeature(models.Model)' in model_template.content
        assert 'created_at = models.DateTimeField' in model_template.content
        
        # 检查Django视图
        view_template = next(t for t in templates if t.template_type == 'view')
        assert 'class TestFeatureViewSet' in view_template.content
        assert 'permission_classes = [IsAuthenticated]' in view_template.content
        
        # 检查Vue组件
        component_template = next(t for t in templates if t.template_type == 'component')
        assert '<template>' in component_template.content
        assert 'TestFeatureComponent' in component_template.content
        
    print("✅ 代码生成器测试通过")
    return True


def test_pipeline_dry_run():
    """测试流水线预览模式"""
    print("🧪 测试流水线预览模式...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试需求文件
        req_file = Path(temp_dir) / "test_requirement.md"
        req_content = """
# 测试需求

## 基本信息

**标题**: 测试功能
**类型**: feature
**优先级**: medium
**组件**: backend, frontend
**预估工时**: 8

## 需求描述

这是一个用于测试流水线的示例需求。

## 验收标准

- 功能可以正常工作
- 界面友好易用
- 性能满足要求
        """
        
        with open(req_file, 'w', encoding='utf-8') as f:
            f.write(req_content)
        
        # 运行流水线预览
        pipeline = PipelineManager(temp_dir)
        result = pipeline.run_pipeline(
            requirement_input=str(req_file),
            input_type='file',
            create_branch=False,  # 不创建分支
            generate_tests=True,
            generate_code=True,
            create_issue=True,
            commit_changes=False  # 不提交变更
        )
        
        assert result['success'] == True
        assert result['requirement'] is not None
        assert len(result['tests']) > 0
        assert len(result['code']) > 0
        assert result['issue'] is not None
        
        # 检查生成的文件
        req_data = result['requirement']
        assert req_data['title'] == '测试功能'
        assert req_data['type'] == 'feature'
        assert req_data['priority'] == 'medium'
        assert 'backend' in req_data['components']
        assert 'frontend' in req_data['components']
        
    print("✅ 流水线预览模式测试通过")
    return True


def test_text_input():
    """测试文本输入模式"""
    print("🧪 测试文本输入模式...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        pipeline = PipelineManager(temp_dir)
        
        text_input = """
标题: 用户登录
类型: feature
优先级: high
组件: backend, frontend, api
描述: 实现用户登录功能，支持邮箱和密码登录
验收标准:
- 用户可以输入邮箱和密码
- 系统验证用户凭据
- 登录成功后跳转到首页
- 登录失败显示错误信息
预估工时: 12
        """
        
        result = pipeline.run_pipeline(
            requirement_input=text_input,
            input_type='text',
            create_branch=False,
            generate_tests=True,
            generate_code=True,
            create_issue=False,
            commit_changes=False
        )
        
        assert result['success'] == True
        assert result['requirement']['title'] == '用户登录'
        assert result['requirement']['type'] == 'feature'
        assert result['requirement']['priority'] == 'high'
        assert len(result['requirement']['acceptance_criteria']) == 4
        
    print("✅ 文本输入模式测试通过")
    return True


def test_error_handling():
    """测试错误处理"""
    print("🧪 测试错误处理...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        pipeline = PipelineManager(temp_dir)
        
        # 测试无效输入
        result = pipeline.run_pipeline(
            requirement_input="无效的需求内容",
            input_type='text',
            create_branch=False,
            generate_tests=True,
            generate_code=True,
            create_issue=False,
            commit_changes=False
        )
        
        # 应该能处理无效输入并使用默认值
        assert result['success'] == True
        assert result['requirement'] is not None
        
        # 测试不存在的文件
        result = pipeline.run_pipeline(
            requirement_input="/path/to/nonexistent/file.md",
            input_type='file',
            create_branch=False,
            generate_tests=False,
            generate_code=False,
            create_issue=False,
            commit_changes=False
        )
        
        # 应该失败
        assert result['success'] == False
        assert len(result['errors']) > 0
        
    print("✅ 错误处理测试通过")
    return True


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行需求流水线测试套件...\n")
    
    tests = [
        test_requirement_parser,
        test_test_generator,
        test_code_generator,
        test_pipeline_dry_run,
        test_text_input,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_func.__name__} 测试失败")
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__} 测试异常: {e}")
        print()
    
    print("="*60)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！需求流水线功能正常")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return False


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
需求流水线测试脚本

用法:
  python scripts/test_pipeline.py              # 运行所有测试
  python scripts/test_pipeline.py --help       # 显示帮助信息

测试内容:
  - 需求解析器功能
  - 测试生成器功能
  - 代码生成器功能
  - 流水线预览模式
  - 文本输入模式
  - 错误处理机制
        """)
        return
    
    # 确保在正确的目录下运行
    script_dir = Path(__file__).parent
    os.chdir(script_dir.parent)
    
    # 添加脚本目录到Python路径
    sys.path.insert(0, str(script_dir))
    
    success = run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()