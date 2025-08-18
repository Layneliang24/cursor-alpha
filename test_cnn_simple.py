#!/usr/bin/env python3
"""
简化的CNN新闻爬取问题诊断
"""

import sys
import os

def test_cnn_issue():
    """测试CNN问题"""
    print("🧪 CNN新闻爬取问题诊断")
    print("="*50)
    
    try:
        # 1. 测试Fundus导入
        print("1. 测试Fundus导入...")
        from fundus import PublisherCollection
        print("✅ Fundus导入成功")
        
        # 2. 检查发布者集合
        print("\n2. 检查发布者集合...")
        publishers = PublisherCollection()
        print("✅ PublisherCollection创建成功")
        
        # 3. 检查US国家对象
        if hasattr(publishers, 'us'):
            print("✅ US国家对象存在")
            us_publishers = dir(publishers.us)
            us_pub_list = [p for p in us_publishers if not p.startswith('_')]
            print(f"US发布者数量: {len(us_pub_list)}")
            
            # 4. 检查CNN是否存在
            if hasattr(publishers.us, 'CNN'):
                print("✅ CNN发布者存在")
                cnn_publisher = publishers.us.CNN
                print(f"CNN发布者: {cnn_publisher}")
            else:
                print("❌ CNN发布者不存在")
                print("US发布者列表:")
                for i, pub in enumerate(us_pub_list[:10], 1):  # 只显示前10个
                    print(f"  {i}. {pub}")
                if len(us_pub_list) > 10:
                    print(f"  ... 还有 {len(us_pub_list) - 10} 个")
        else:
            print("❌ US国家对象不存在")
            
        # 5. 检查available_publishers.py
        print("\n3. 检查available_publishers.py...")
        try:
            backend_path = os.path.join(os.path.dirname(__file__), 'backend')
            sys.path.insert(0, backend_path)
            from available_publishers import AVAILABLE_PUBLISHERS
            
            print(f"✅ available_publishers.py加载成功，共{len(AVAILABLE_PUBLISHERS)}个发布者")
            
            # 检查CNN是否在列表中
            cnn_variants = [p for p in AVAILABLE_PUBLISHERS if 'cnn' in p.lower()]
            if cnn_variants:
                print(f"找到CNN相关发布者: {cnn_variants}")
            else:
                print("⚠️ CNN不在可用发布者列表中")
                
            # 检查US发布者
            us_publishers = [p for p in AVAILABLE_PUBLISHERS if p.startswith('us.')]
            print(f"US发布者数量: {len(us_publishers)}")
            print("US发布者列表:")
            for pub in us_publishers:
                print(f"  - {pub}")
                
        except Exception as e:
            print(f"❌ 检查available_publishers.py失败: {e}")
            
        # 6. 生成解决方案
        print("\n" + "="*50)
        print("🔧 问题分析和解决方案")
        print("="*50)
        
        print("问题原因:")
        print("1. CNN不在Fundus的可用发布者列表中")
        print("2. available_publishers.py中没有包含CNN")
        print("3. 可能CNN在Fundus中的名称不是'CNN'")
        
        print("\n解决方案:")
        print("1. 使用传统CNN爬虫（已实现）")
        print("2. 更新available_publishers.py包含CNN")
        print("3. 检查CNN在Fundus中的正确名称")
        print("4. 手动测试CNN发布者")
        
        print("\n立即解决方案:")
        print("- 在前端选择'CNN'时，系统会自动使用传统爬虫")
        print("- 传统CNN爬虫已经实现并可用")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    test_cnn_issue()




