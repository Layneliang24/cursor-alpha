#!/usr/bin/env python3
"""
依赖验证脚本
测试新创建的服务和模型类是否可以正常导入
"""
import sys
import os
from pathlib import Path

def test_imports():
    """测试关键依赖的导入"""
    print("🔍 开始验证依赖导入...")
    
    # 添加项目根目录到Python路径
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    test_results = []
    
    # 测试1: AIModelConfig模型类
    print("\n📋 测试1: AIModelConfig模型类")
    try:
        from backend.apps.ai.adapters.base import AIModelConfig
        print("✅ AIModelConfig导入成功")
        test_results.append(("AIModelConfig", True, "导入成功"))
        
        # 测试类的基本属性
        print(f"  - 类名: {AIModelConfig.__name__}")
        print(f"  - 模块: {AIModelConfig.__module__}")
        print(f"  - 基类: {AIModelConfig.__bases__}")
        
    except ImportError as e:
        print(f"❌ AIModelConfig导入失败: {e}")
        test_results.append(("AIModelConfig", False, str(e)))
    except Exception as e:
        print(f"❌ AIModelConfig测试异常: {e}")
        test_results.append(("AIModelConfig", False, str(e)))
    
    # 测试2: DataAnalysisService服务类
    print("\n📋 测试2: DataAnalysisService服务类")
    try:
        from backend.apps.english.services import DataAnalysisService
        print("✅ DataAnalysisService导入成功")
        test_results.append(("DataAnalysisService", True, "导入成功"))
        
        # 测试类的基本属性
        print(f"  - 类名: {DataAnalysisService.__name__}")
        print(f"  - 模块: {DataAnalysisService.__module__}")
        print(f"  - 基类: {DataAnalysisService.__bases__}")
        
        # 测试实例化
        try:
            service = DataAnalysisService()
            print("✅ DataAnalysisService实例化成功")
            
            # 测试基本方法
            if hasattr(service, 'get_user_learning_summary'):
                print("✅ get_user_learning_summary方法存在")
            else:
                print("❌ get_user_learning_summary方法不存在")
                
        except Exception as e:
            print(f"❌ DataAnalysisService实例化失败: {e}")
            test_results.append(("DataAnalysisService实例化", False, str(e)))
        
    except ImportError as e:
        print(f"❌ DataAnalysisService导入失败: {e}")
        test_results.append(("DataAnalysisService", False, str(e)))
    except Exception as e:
        print(f"❌ DataAnalysisService测试异常: {e}")
        test_results.append(("DataAnalysisService", False, str(e)))
    
    # 测试3: 检查文件是否存在
    print("\n📋 测试3: 文件存在性检查")
    files_to_check = [
        "backend/apps/ai/adapters/base/__init__.py",
        "backend/apps/ai/adapters/base/ai_model_config.py",
        "backend/apps/english/services/__init__.py",
        "backend/apps/english/services/data_analysis_service.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ 文件存在: {file_path}")
            test_results.append((f"文件存在: {file_path}", True, "文件存在"))
        else:
            print(f"❌ 文件不存在: {file_path}")
            test_results.append((f"文件存在: {file_path}", False, "文件不存在"))
    
    # 测试4: 检查模块结构
    print("\n📋 测试4: 模块结构检查")
    try:
        # 检查AI适配器模块
        from backend.apps.ai.adapters import base
        print("✅ AI适配器基础模块导入成功")
        test_results.append(("AI适配器基础模块", True, "导入成功"))
        
        # 检查英语服务模块
        from backend.apps.english import services
        print("✅ 英语服务模块导入成功")
        test_results.append(("英语服务模块", True, "导入成功"))
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        test_results.append(("模块导入", False, str(e)))
    except Exception as e:
        print(f"❌ 模块测试异常: {e}")
        test_results.append(("模块测试", False, str(e)))
    
    # 生成测试报告
    print("\n📊 依赖验证报告")
    print("=" * 50)
    
    success_count = sum(1 for result in test_results if result[1])
    total_count = len(test_results)
    
    print(f"总测试项: {total_count}")
    print(f"成功项: {success_count}")
    print(f"失败项: {total_count - success_count}")
    print(f"成功率: {(success_count/total_count)*100:.1f}%")
    
    print("\n详细结果:")
    for test_name, success, message in test_results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {status} {test_name}: {message}")
    
    # 总结
    print("\n🎯 总结:")
    if success_count == total_count:
        print("🎉 所有依赖验证通过！缺失的服务和模型类已成功创建。")
        print("✅ Task 31.1 和 31.2 已完成")
        print("🚀 可以继续进行Task 31.3（重构测试隔离性）")
    else:
        print("⚠️ 部分依赖验证失败，需要进一步检查。")
        print("🔍 请检查失败项的具体原因")
    
    return success_count == total_count

def main():
    """主函数"""
    print("🚀 启动依赖验证脚本...")
    
    success = test_imports()
    
    if success:
        print("\n🎯 下一步行动:")
        print("1. 继续Task 31.3: 重构测试隔离性")
        print("2. 使用Mock和Stub替代真实依赖")
        print("3. 创建测试专用的数据工厂")
        print("4. 实现测试环境的配置隔离")
    else:
        print("\n🔧 需要修复的问题:")
        print("1. 检查文件路径和权限")
        print("2. 验证Python模块结构")
        print("3. 检查导入语句语法")
    
    return success

if __name__ == "__main__":
    main()


