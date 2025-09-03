#!/usr/bin/env python3
"""
缺失服务分析工具
专门分析缺失的服务类和模型类，生成详细的创建计划
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any

class MissingServiceAnalyzer:
    def __init__(self, dependency_report_file: str = "dependency_analysis_report.json"):
        self.dependency_report_file = dependency_report_file
        self.dependency_report = None
        self.missing_services = []
        self.missing_models = []
        self.creation_plan = {}
    
    def load_dependency_report(self) -> bool:
        """加载依赖分析报告"""
        try:
            with open(self.dependency_report_file, 'r', encoding='utf-8') as f:
                self.dependency_report = json.load(f)
            print(f"✅ 成功加载依赖分析报告: {self.dependency_report_file}")
            return True
        except Exception as e:
            print(f"❌ 加载依赖分析报告失败: {e}")
            return False
    
    def analyze_missing_services(self) -> Dict[str, Any]:
        """分析缺失的服务类"""
        print("🔍 分析缺失的服务类...")
        
        if not self.dependency_report:
            print("❌ 依赖分析报告未加载")
            return {}
        
        missing_services = self.dependency_report.get('missing_dependencies_by_category', {}).get('service_classes', {})
        
        analysis_result = {
            'total_count': missing_services.get('count', 0),
            'unique_services': missing_services.get('unique_items', []),
            'service_details': [],
            'creation_priority': []
        }
        
        for service_path in missing_services.get('unique_items', []):
            service_info = self.analyze_service_path(service_path)
            analysis_result['service_details'].append(service_info)
            
            # 确定创建优先级
            priority = self.determine_service_priority(service_info)
            analysis_result['creation_priority'].append({
                'service_path': service_path,
                'priority': priority,
                'estimated_effort': self.estimate_service_effort(service_info),
                'dependencies': service_info.get('dependencies', [])
            })
        
        # 按优先级排序
        analysis_result['creation_priority'].sort(key=lambda x: x['priority'])
        
        return analysis_result
    
    def analyze_missing_models(self) -> Dict[str, Any]:
        """分析缺失的模型类"""
        print("🔍 分析缺失的模型类...")
        
        if not self.dependency_report:
            print("❌ 依赖分析报告未加载")
            return {}
        
        missing_models = self.dependency_report.get('missing_dependencies_by_category', {}).get('model_classes', {})
        
        analysis_result = {
            'total_count': missing_models.get('count', 0),
            'unique_models': missing_models.get('unique_items', []),
            'model_details': [],
            'creation_priority': []
        }
        
        for model_path in missing_models.get('unique_items', []):
            model_info = self.analyze_model_path(model_path)
            analysis_result['model_details'].append(model_info)
            
            # 确定创建优先级
            priority = self.determine_model_priority(model_info)
            analysis_result['creation_priority'].append({
                'model_path': model_path,
                'priority': priority,
                'estimated_effort': self.estimate_model_effort(model_info),
                'dependencies': model_info.get('dependencies', [])
            })
        
        # 按优先级排序
        analysis_result['creation_priority'].sort(key=lambda x: x['priority'])
        
        return analysis_result
    
    def analyze_service_path(self, service_path: str) -> Dict[str, Any]:
        """分析服务类路径，推断其功能和依赖"""
        service_info = {
            'full_path': service_path,
            'module_path': '',
            'class_name': '',
            'category': '',
            'estimated_functionality': '',
            'dependencies': [],
            'estimated_complexity': 'medium'
        }
        
        # 解析路径
        if '.' in service_path:
            parts = service_path.split('.')
            service_info['module_path'] = '.'.join(parts[:-1])
            service_info['class_name'] = parts[-1]
        
        # 推断功能类别
        class_name = service_info['class_name']
        if 'DataAnalysis' in class_name:
            service_info['category'] = 'data_processing'
            service_info['estimated_functionality'] = '数据分析服务，处理用户学习数据统计和分析'
            service_info['dependencies'] = ['pandas', 'numpy', 'matplotlib', 'seaborn']
            service_info['estimated_complexity'] = 'high'
        elif 'Service' in class_name:
            service_info['category'] = 'business_logic'
            service_info['estimated_functionality'] = '业务逻辑服务，处理核心业务功能'
            service_info['estimated_complexity'] = 'medium'
        else:
            service_info['category'] = 'utility'
            service_info['estimated_functionality'] = '工具服务，提供辅助功能'
            service_info['estimated_complexity'] = 'low'
        
        return service_info
    
    def analyze_model_path(self, model_path: str) -> Dict[str, Any]:
        """分析模型类路径，推断其功能和依赖"""
        model_info = {
            'full_path': model_path,
            'module_path': '',
            'class_name': '',
            'category': '',
            'estimated_functionality': '',
            'dependencies': [],
            'estimated_complexity': 'medium'
        }
        
        # 解析路径
        if '.' in model_path:
            parts = model_path.split('.')
            model_info['module_path'] = '.'.join(parts[:-1])
            model_info['class_name'] = parts[-1]
        
        # 推断功能类别
        class_name = model_info['class_name']
        if 'AIModelConfig' in class_name:
            model_info['category'] = 'ai_configuration'
            model_info['estimated_functionality'] = 'AI模型配置类，存储模型参数和配置信息'
            model_info['dependencies'] = ['django.db.models', 'django.core.validators']
            model_info['estimated_complexity'] = 'low'
        elif 'Config' in class_name:
            model_info['category'] = 'configuration'
            model_info['estimated_functionality'] = '配置类，存储应用配置信息'
            model_info['estimated_complexity'] = 'low'
        else:
            model_info['category'] = 'data_model'
            model_info['estimated_functionality'] = '数据模型类，定义数据结构'
            model_info['estimated_complexity'] = 'medium'
        
        return model_info
    
    def determine_service_priority(self, service_info: Dict[str, Any]) -> int:
        """确定服务类创建优先级（1=最高，5=最低）"""
        priority = 3  # 默认中等优先级
        
        # 根据类别调整优先级
        if service_info['category'] == 'data_processing':
            priority = 1  # 数据分析服务优先级最高
        elif service_info['category'] == 'business_logic':
            priority = 2  # 业务逻辑服务次之
        elif service_info['category'] == 'utility':
            priority = 4  # 工具服务优先级较低
        
        # 根据复杂度调整优先级
        if service_info['estimated_complexity'] == 'high':
            priority = max(1, priority - 1)  # 高复杂度提高优先级
        elif service_info['estimated_complexity'] == 'low':
            priority = min(5, priority + 1)  # 低复杂度降低优先级
        
        return priority
    
    def determine_model_priority(self, model_info: Dict[str, Any]) -> int:
        """确定模型类创建优先级（1=最高，5=最低）"""
        priority = 3  # 默认中等优先级
        
        # 根据类别调整优先级
        if model_info['category'] == 'ai_configuration':
            priority = 1  # AI配置模型优先级最高
        elif model_info['category'] == 'data_model':
            priority = 2  # 数据模型次之
        elif model_info['category'] == 'configuration':
            priority = 4  # 配置模型优先级较低
        
        # 根据复杂度调整优先级
        if model_info['estimated_complexity'] == 'high':
            priority = max(1, priority - 1)
        elif model_info['estimated_complexity'] == 'low':
            priority = min(5, priority + 1)
        
        return priority
    
    def estimate_service_effort(self, service_info: Dict[str, Any]) -> str:
        """估算服务类创建工作量"""
        complexity = service_info['estimated_complexity']
        
        if complexity == 'high':
            return '4-6小时'
        elif complexity == 'medium':
            return '2-4小时'
        else:
            return '1-2小时'
    
    def estimate_model_effort(self, model_info: Dict[str, Any]) -> str:
        """估算模型类创建工作量"""
        complexity = model_info['estimated_complexity']
        
        if complexity == 'high':
            return '2-3小时'
        elif complexity == 'medium':
            return '1-2小时'
        else:
            return '0.5-1小时'
    
    def generate_creation_plan(self) -> Dict[str, Any]:
        """生成完整的创建计划"""
        print("📝 生成创建计划...")
        
        # 分析缺失的服务和模型
        services_analysis = self.analyze_missing_services()
        models_analysis = self.analyze_missing_models()
        
        # 生成创建计划
        creation_plan = {
            "summary": {
                "total_missing_services": services_analysis['total_count'],
                "total_missing_models": models_analysis['total_count'],
                "total_estimated_effort": "6-10小时",
                "priority_breakdown": {
                    "priority_1": len([s for s in services_analysis['creation_priority'] if s['priority'] == 1]),
                    "priority_2": len([s for s in services_analysis['creation_priority'] if s['priority'] == 2]),
                    "priority_3": len([s for s in services_analysis['creation_priority'] if s['priority'] == 3]),
                    "priority_4": len([s for s in services_analysis['creation_priority'] if s['priority'] == 4]),
                    "priority_5": len([s for s in services_analysis['creation_priority'] if s['priority'] == 5])
                }
            },
            "services_creation_plan": {
                "analysis": services_analysis,
                "step_by_step_plan": self.generate_service_creation_steps(services_analysis),
                "dependencies_resolution": self.analyze_service_dependencies(services_analysis)
            },
            "models_creation_plan": {
                "analysis": models_analysis,
                "step_by_step_plan": self.generate_model_creation_steps(models_analysis),
                "dependencies_resolution": self.analyze_model_dependencies(models_analysis)
            },
            "implementation_order": self.determine_implementation_order(services_analysis, models_analysis),
            "risk_assessment": self.assess_implementation_risks(services_analysis, models_analysis)
        }
        
        return creation_plan
    
    def generate_service_creation_steps(self, services_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成服务类创建步骤"""
        steps = []
        
        for service_item in services_analysis['creation_priority']:
            service_path = service_item['service_path']
            priority = service_item['priority']
            
            step = {
                'step_number': len(steps) + 1,
                'service_path': service_path,
                'priority': priority,
                'estimated_effort': service_item['estimated_effort'],
                'actions': [
                    f"创建文件: {service_path.replace('.', '/')}.py",
                    "定义服务类结构",
                    "实现核心方法",
                    "添加错误处理",
                    "编写单元测试",
                    "验证导入功能"
                ],
                'dependencies': service_item['dependencies'],
                'success_criteria': [
                    "服务类可以正常导入",
                    "基本方法可以调用",
                    "单元测试通过",
                    "无语法错误"
                ]
            }
            steps.append(step)
        
        return steps
    
    def generate_model_creation_steps(self, models_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成模型类创建步骤"""
        steps = []
        
        for model_item in models_analysis['creation_priority']:
            model_path = model_item['model_path']
            priority = model_item['priority']
            
            step = {
                'step_number': len(steps) + 1,
                'model_path': model_path,
                'priority': priority,
                'estimated_effort': model_item['estimated_effort'],
                'actions': [
                    f"创建文件: {model_path.replace('.', '/')}.py",
                    "定义模型类结构",
                    "添加必要的字段",
                    "实现验证逻辑",
                    "添加序列化器",
                    "编写单元测试"
                ],
                'dependencies': model_item['dependencies'],
                'success_criteria': [
                    "模型类可以正常导入",
                    "字段定义正确",
                    "验证逻辑有效",
                    "单元测试通过"
                ]
            }
            steps.append(step)
        
        return steps
    
    def analyze_service_dependencies(self, services_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析服务类依赖关系"""
        dependencies = {
            'external_packages': set(),
            'internal_modules': set(),
            'database_models': set(),
            'configuration_files': set()
        }
        
        for service_item in services_analysis['creation_priority']:
            service_path = service_item['service_path']
            
            # 根据服务类型推断依赖
            if 'DataAnalysis' in service_path:
                dependencies['external_packages'].update(['pandas', 'numpy', 'matplotlib', 'seaborn'])
                dependencies['internal_modules'].update(['apps.english.models', 'apps.users.models'])
                dependencies['database_models'].update(['User', 'UserProfile', 'TypingSession'])
                dependencies['configuration_files'].update(['settings.py', 'requirements.txt'])
        
        # 转换为列表
        return {k: list(v) for k, v in dependencies.items()}
    
    def analyze_model_dependencies(self, models_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析模型类依赖关系"""
        dependencies = {
            'django_modules': set(),
            'internal_modules': set(),
            'validation_modules': set(),
            'configuration_files': set()
        }
        
        for model_item in models_analysis['creation_priority']:
            model_path = model_item['model_path']
            
            if 'AIModelConfig' in model_path:
                dependencies['django_modules'].update(['django.db.models', 'django.core.validators'])
                dependencies['internal_modules'].update(['apps.ai.adapters.base'])
                dependencies['validation_modules'].update(['django.core.validators'])
                dependencies['configuration_files'].update(['models.py', 'admin.py'])
        
        # 转换为列表
        return {k: list(v) for k, v in dependencies.items()}
    
    def determine_implementation_order(self, services_analysis: Dict[str, Any], models_analysis: Dict[str, Any]) -> List[str]:
        """确定实现顺序"""
        implementation_order = []
        
        # 1. 先创建模型类（因为服务类可能依赖它们）
        for model_item in models_analysis['creation_priority']:
            implementation_order.append(f"创建模型: {model_item['model_path']}")
        
        # 2. 再创建服务类
        for service_item in services_analysis['creation_priority']:
            implementation_order.append(f"创建服务: {service_item['service_path']}")
        
        return implementation_order
    
    def assess_implementation_risks(self, services_analysis: Dict[str, Any], models_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """评估实现风险"""
        risks = {
            'high_risk': [],
            'medium_risk': [],
            'low_risk': []
        }
        
        # 评估服务类风险
        for service_item in services_analysis['creation_priority']:
            if service_item['estimated_effort'] == '4-6小时':
                risks['high_risk'].append(f"服务类 {service_item['service_path']} - 复杂度高，需要充分测试")
            elif service_item['estimated_effort'] == '2-4小时':
                risks['medium_risk'].append(f"服务类 {service_item['service_path']} - 中等复杂度，需要基本测试")
            else:
                risks['low_risk'].append(f"服务类 {service_item['service_path']} - 低复杂度，风险较小")
        
        # 评估模型类风险
        for model_item in models_analysis['creation_priority']:
            if model_item['estimated_effort'] == '2-3小时':
                risks['medium_risk'].append(f"模型类 {model_item['model_path']} - 中等复杂度，需要验证字段定义")
            else:
                risks['low_risk'].append(f"模型类 {model_item['model_path']} - 低复杂度，风险较小")
        
        return risks
    
    def save_creation_plan(self, creation_plan: Dict[str, Any], filename: str = "missing_services_creation_plan.json"):
        """保存创建计划"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(creation_plan, f, indent=2, ensure_ascii=False)
            print(f"📋 创建计划已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存创建计划失败: {e}")

def main():
    """主函数"""
    print("🚀 启动缺失服务分析工具...")
    
    # 创建分析器实例
    analyzer = MissingServiceAnalyzer()
    
    # 加载依赖分析报告
    if not analyzer.load_dependency_report():
        print("❌ 无法加载依赖分析报告，分析终止")
        return
    
    # 生成创建计划
    creation_plan = analyzer.generate_creation_plan()
    
    # 显示创建计划摘要
    print(f"\n📊 创建计划摘要:")
    print(f"  缺失服务类: {creation_plan['summary']['total_missing_services']} 个")
    print(f"  缺失模型类: {creation_plan['summary']['total_missing_models']} 个")
    print(f"  总预计工作量: {creation_plan['summary']['total_estimated_effort']}")
    
    print(f"\n🎯 优先级分布:")
    for priority, count in creation_plan['summary']['priority_breakdown'].items():
        if count > 0:
            print(f"  {priority}: {count} 个")
    
    print(f"\n📋 实现顺序:")
    for i, step in enumerate(creation_plan['implementation_order'], 1):
        print(f"  {i}. {step}")
    
    print(f"\n⚠️ 风险评估:")
    for risk_level, risks in creation_plan['risk_assessment'].items():
        if risks:
            print(f"  {risk_level}:")
            for risk in risks:
                print(f"    - {risk}")
    
    # 保存创建计划
    analyzer.save_creation_plan(creation_plan)

if __name__ == "__main__":
    main()

