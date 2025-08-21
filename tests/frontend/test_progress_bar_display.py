#!/usr/bin/env python
"""
进度条显示问题测试脚本

测试问题：练习界面首次加载时进度条不显示，需要点击任意键开始后，
再切换到其他页面，再回到练习界面，进度条才显示。

可能原因：
1. 组件初始化时机问题
2. 状态同步问题
3. 路由切换问题
4. Vue 组件生命周期问题
"""

import requests
import json
import time
from typing import Dict, Any

class ProgressBarDisplayTester:
    """进度条显示问题测试器"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def test_api_endpoints(self):
        """测试相关 API 端点"""
        print("🔍 测试相关 API 端点...")
        
        # 测试词库列表
        try:
            response = self.session.get(f"{self.base_url}/api/v1/english/dictionaries/")
            if response.status_code == 200:
                dictionaries = response.json()
                print(f"✅ 词库列表 API 正常，共 {len(dictionaries)} 个词库")
                
                # 找到测试词典
                test_dict = None
                for dict_item in dictionaries:
                    if dict_item.get('name') == '测试词典':
                        test_dict = dict_item
                        break
                
                if test_dict:
                    print(f"✅ 找到测试词典: {test_dict}")
                    return test_dict
                else:
                    print("❌ 未找到测试词典")
                    return None
            else:
                print(f"❌ 词库列表 API 失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 测试词库列表 API 出错: {e}")
            return None
    
    def test_typing_words_api(self, dictionary_id: int, chapter: int = 1):
        """测试打字练习单词 API"""
        print(f"🔍 测试打字练习单词 API (词典ID: {dictionary_id}, 章节: {chapter})...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/english/typing-words/by_dictionary/",
                params={
                    'dictionary_id': dictionary_id,
                    'chapter': chapter
                }
            )
            
            if response.status_code == 200:
                words = response.json()
                print(f"✅ 获取单词成功，共 {len(words)} 个单词")
                
                if len(words) > 0:
                    print(f"✅ 第一个单词: {words[0]}")
                    return words
                else:
                    print("❌ 单词列表为空")
                    return []
            else:
                print(f"❌ 获取单词失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 测试打字练习单词 API 出错: {e}")
            return []
    
    def test_chapter_word_counts(self, dictionary_id: int):
        """测试章节单词数量 API"""
        print(f"🔍 测试章节单词数量 API (词典ID: {dictionary_id})...")
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/english/dictionaries/chapter_word_counts/",
                params={'dictionary_id': dictionary_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取章节单词数量成功")
                print(f"   词典名称: {data.get('dictionary_name')}")
                print(f"   总单词数: {data.get('total_words')}")
                print(f"   章节数: {data.get('chapter_count')}")
                
                chapters = data.get('chapters', [])
                for chapter in chapters:
                    print(f"   第{chapter['number']}章: {chapter['wordCount']} 个单词")
                
                return data
            else:
                print(f"❌ 获取章节单词数量失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 测试章节单词数量 API 出错: {e}")
            return None
    
    def simulate_frontend_flow(self, dictionary_id: int, chapter: int = 1):
        """模拟前端流程"""
        print(f"🔄 模拟前端流程 (词典ID: {dictionary_id}, 章节: {chapter})...")
        
        # 1. 获取词库信息
        dict_info = self.test_chapter_word_counts(dictionary_id)
        if not dict_info:
            print("❌ 无法获取词库信息，跳过流程模拟")
            return False
        
        # 2. 获取练习单词
        words = self.test_typing_words_api(dictionary_id, chapter)
        if not words:
            print("❌ 无法获取练习单词，跳过流程模拟")
            return False
        
        # 3. 模拟练习开始
        print("✅ 模拟练习开始...")
        print(f"   单词数量: {len(words)}")
        print(f"   当前单词索引: 0")
        print(f"   进度条应该显示: 1/{len(words)}")
        
        # 4. 检查进度条显示条件
        progress_conditions = {
            "words_exists": len(words) > 0,
            "words_length": len(words),
            "current_word_index": 0,
            "progress_percentage": round((1 / len(words)) * 100, 2),
            "progress_text": f"1/{len(words)}"
        }
        
        print("📊 进度条显示条件检查:")
        for key, value in progress_conditions.items():
            print(f"   {key}: {value}")
        
        # 5. 模拟状态变化
        print("🔄 模拟状态变化...")
        
        # 模拟输入第一个字母
        print("   模拟输入第一个字母...")
        first_word = words[0]
        first_letter = first_word['word'][0] if first_word['word'] else 'a'
        print(f"   第一个单词: {first_word['word']}")
        print(f"   第一个字母: {first_letter}")
        
        # 模拟完成第一个单词
        print("   模拟完成第一个单词...")
        progress_conditions["current_word_index"] = 1
        progress_conditions["progress_percentage"] = round((2 / len(words)) * 100, 2)
        progress_conditions["progress_text"] = f"2/{len(words)}"
        
        print("📊 完成第一个单词后的进度条状态:")
        for key, value in progress_conditions.items():
            print(f"   {key}: {value}")
        
        return True
    
    def analyze_problem(self):
        """分析问题"""
        print("\n🔍 问题分析...")
        
        print("""
可能的问题原因：

1. **组件初始化时机问题**
   - 进度条组件在页面首次加载时没有正确初始化
   - Vue 组件的 mounted 生命周期中状态可能未同步

2. **状态同步问题**
   - useTypingStore 中的 words 和 currentWordIndex 状态
   - 在组件首次渲染时可能为空或未定义

3. **路由切换问题**
   - 从其他页面返回时触发了组件的重新挂载
   - 组件的 beforeRouteEnter 或 activated 钩子可能有问题

4. **Vue 响应式问题**
   - computed 属性可能没有正确响应状态变化
   - nextTick 或 watch 的使用可能有问题

5. **条件渲染问题**
   - v-if="words && words.length > 0" 条件判断
   - words 数组在初始化时可能为空
        """)
        
        print("""
建议的解决方案：

1. **检查组件生命周期**
   - 在 onMounted 中确保状态正确初始化
   - 使用 nextTick 等待 DOM 更新完成

2. **改进状态管理**
   - 在 store 中添加初始化状态检查
   - 使用 watch 监听状态变化

3. **优化条件渲染**
   - 添加加载状态检查
   - 使用 v-show 替代 v-if 避免重复渲染

4. **添加调试日志**
   - 在关键生命周期钩子中添加日志
   - 监控状态变化和组件渲染
        """)
    
    def run_tests(self):
        """运行所有测试"""
        print("🚀 开始进度条显示问题测试...")
        print("=" * 60)
        
        # 测试 API 端点
        test_dict = self.test_api_endpoints()
        if not test_dict:
            print("❌ 无法获取测试词典，测试终止")
            return
        
        print(f"\n✅ 使用测试词典: {test_dict['name']} (ID: {test_dict['id']})")
        
        # 测试打字练习单词 API
        words = self.test_typing_words_api(test_dict['id'], 1)
        if not words:
            print("❌ 无法获取练习单词，测试终止")
            return
        
        # 测试章节单词数量 API
        self.test_chapter_word_counts(test_dict['id'])
        
        # 模拟前端流程
        self.simulate_frontend_flow(test_dict['id'], 1)
        
        # 分析问题
        self.analyze_problem()
        
        print("\n" + "=" * 60)
        print("✅ 测试完成！")
        print("\n📝 下一步建议：")
        print("1. 检查前端组件的生命周期钩子")
        print("2. 验证 useTypingStore 的状态初始化")
        print("3. 添加调试日志监控状态变化")
        print("4. 测试路由切换时的组件行为")

def main():
    """主函数"""
    tester = ProgressBarDisplayTester()
    tester.run_tests()

if __name__ == "__main__":
    main()
