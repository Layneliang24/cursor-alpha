#!/usr/bin/env python
"""
对话管理系统功能验证脚本

验证对话上下文管理、流式响应处理等核心功能
"""

import os
import sys
import asyncio
import django
from pathlib import Path

# 添加项目路径到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alpha.settings')
django.setup()

from apps.ai.conversation.manager import ConversationManager, ConversationSettings
from apps.ai.conversation.context import ConversationContext, ContextCompressor
from apps.ai.conversation.streaming import ResponseStreamer, StreamEvent, StreamEventType
from apps.ai.conversation.quality import QualityAssessor
from apps.ai.adapters.base import AIMessage, MessageRole


async def test_conversation_context():
    """测试对话上下文管理"""
    print("🧪 测试对话上下文管理...")
    
    try:
        # 创建对话上下文
        context = ConversationContext(
            conversation_id="test-001",
            title="测试对话",
            created_at=datetime.now()
        )
        
        # 添加消息
        context.add_message(AIMessage(role=MessageRole.USER, content="你好"))
        context.add_message(AIMessage(role=MessageRole.ASSISTANT, content="你好！有什么可以帮助你的吗？"))
        
        # 验证基本功能
        assert context.message_count == 2
        assert context.user_message_count == 1
        assert context.assistant_message_count == 1
        assert context.estimated_tokens > 0
        
        print(f"✅ 对话上下文创建成功，消息数: {context.message_count}, 估算token: {context.estimated_tokens}")
        return True
        
    except Exception as e:
        print(f"❌ 对话上下文测试失败: {e}")
        return False


async def test_context_compression():
    """测试上下文压缩"""
    print("\n🧪 测试上下文压缩...")
    
    try:
        compressor = ContextCompressor()
        
        # 创建测试消息
        messages = [
            AIMessage(role=MessageRole.SYSTEM, content="你是一个有用的AI助手"),
            AIMessage(role=MessageRole.USER, content="什么是人工智能？"),
            AIMessage(role=MessageRole.ASSISTANT, content="人工智能是计算机科学的一个分支..."),
            AIMessage(role=MessageRole.USER, content="请详细解释机器学习"),
            AIMessage(role=MessageRole.ASSISTANT, content="机器学习是人工智能的一个子领域..."),
            AIMessage(role=MessageRole.USER, content="深度学习和机器学习有什么区别？"),
            AIMessage(role=MessageRole.ASSISTANT, content="深度学习是机器学习的一个分支...")
        ]
        
        # 计算原始token数
        original_tokens = compressor._estimate_tokens(messages)
        print(f"   原始消息tokens: {original_tokens}")
        
        # 压缩测试 - 设置更小的目标token数强制压缩
        compressed = await compressor.compress(
            messages=messages,
            target_length=10,  # 极小的目标，强制压缩
            preserve_system=True,
            preserve_recent=2
        )
        
        # 验证压缩结果
        assert len(compressed) < len(messages)
        assert any(msg.role == MessageRole.SYSTEM for msg in compressed)  # 保留系统消息
        
        # 获取压缩统计
        stats = compressor.get_compression_stats(messages, compressed)
        
        print(f"✅ 上下文压缩成功: {len(messages)} -> {len(compressed)} 条消息")
        print(f"   压缩比: {stats['message_reduction_ratio']:.2%}")
        print(f"   Token压缩比: {stats['token_reduction_ratio']:.2%}")
        
        return True
        
    except Exception as e:
        import traceback
        print(f"❌ 上下文压缩测试失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False


async def test_response_streaming():
    """测试流式响应"""
    print("\n🧪 测试流式响应...")
    
    try:
        streamer = ResponseStreamer()
        stream_id = "test-stream-001"
        
        # 创建流
        buffer = await streamer.create_stream(stream_id)
        
        # 添加内容
        await streamer.add_content(stream_id, "这是", {"chunk_id": 1})
        await streamer.add_content(stream_id, "一个", {"chunk_id": 2})
        await streamer.add_content(stream_id, "测试", {"chunk_id": 3})
        
        # 完成流
        await streamer.complete_stream(stream_id, {"final": True})
        
        # 验证事件
        events = await buffer.get_events_since()
        assert len(events) >= 5  # start + 3个content + complete
        
        # 检查事件类型
        event_types = [event.type for event in events]
        assert StreamEventType.START in event_types
        assert StreamEventType.CONTENT in event_types
        assert StreamEventType.COMPLETE in event_types
        
        print(f"✅ 流式响应测试成功，生成 {len(events)} 个事件")
        
        # 获取统计
        stats = streamer.get_stream_stats()
        print(f"   活跃流数: {stats['active_streams']}")
        print(f"   总事件数: {stats['total_events']}")
        
        # 清理
        await streamer.close_stream(stream_id)
        
        return True
        
    except Exception as e:
        print(f"❌ 流式响应测试失败: {e}")
        return False


async def test_quality_assessment():
    """测试质量评估"""
    print("\n🧪 测试质量评估...")
    
    try:
        assessor = QualityAssessor()
        
        # 测试响应质量评估
        user_message = "什么是机器学习？"
        ai_response = """机器学习是人工智能的一个重要分支，它是一种让计算机通过数据学习规律的技术。

具体来说，机器学习包括以下几个核心概念：
1. 监督学习：使用标记数据训练模型
2. 无监督学习：从未标记数据中发现模式
3. 强化学习：通过奖励机制学习最优策略

机器学习广泛应用于图像识别、自然语言处理、推荐系统等领域。"""
        
        score = await assessor.assess_response(user_message, ai_response)
        
        assert 0.0 <= score <= 1.0
        
        print(f"✅ 质量评估测试成功，评分: {score:.3f}")
        
        # 测试对话质量评估
        context = ConversationContext(
            conversation_id="test-quality",
            title="质量测试对话",
            created_at=datetime.now()
        )
        
        context.add_message(AIMessage(role=MessageRole.USER, content=user_message))
        context.add_message(AIMessage(role=MessageRole.ASSISTANT, content=ai_response))
        
        conversation_report = await assessor.assess_conversation(context)
        
        assert 'overall_score' in conversation_report
        assert 'message_scores' in conversation_report
        
        print(f"   对话整体评分: {conversation_report['overall_score']:.3f}")
        print(f"   消息评分数: {len(conversation_report['message_scores'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ 质量评估测试失败: {e}")
        return False


async def test_conversation_manager():
    """测试对话管理器"""
    print("\n🧪 测试对话管理器...")
    
    try:
        # 使用测试配置
        settings = ConversationSettings(
            max_context_length=1000,
            cache_ttl=60,
            enable_streaming=True,
            enable_quality_assessment=True
        )
        
        manager = ConversationManager(settings)
        
        # 创建对话
        conversation_id = await manager.create_conversation(
            title="测试管理器对话",
            system_prompt="你是一个测试助手"
        )
        
        assert conversation_id is not None
        print(f"✅ 创建对话成功: {conversation_id}")
        
        # 获取对话
        context = await manager.get_conversation(conversation_id)
        assert context is not None
        assert context.title == "测试管理器对话"
        
        # 添加消息
        success = await manager.add_message(
            conversation_id,
            AIMessage(role=MessageRole.USER, content="测试消息")
        )
        assert success
        
        print("✅ 对话管理器基本功能测试通过")
        
        # 获取统计信息
        stats = await manager.get_conversation_stats(conversation_id)
        assert 'conversation_id' in stats
        assert 'message_count' in stats
        
        print(f"   统计信息: 消息数={stats['message_count']}, token={stats['estimated_tokens']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 对话管理器测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始对话管理系统功能验证")
    print("=" * 50)
    
    tests = [
        test_conversation_context,
        test_context_compression,
        test_response_streaming,
        test_quality_assessment,
        test_conversation_manager
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if await test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！对话管理系统功能正常")
        return True
    else:
        print("⚠️  部分测试失败，请检查系统配置")
        return False


if __name__ == '__main__':
    from datetime import datetime
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
