"""
流式响应处理

处理AI响应的流式传输和Server-Sent Events (SSE)
"""

import json
import asyncio
import logging
from typing import Dict, Any, AsyncGenerator, Optional, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from django.http import StreamingHttpResponse
from django.utils.html import escape

logger = logging.getLogger(__name__)


class StreamEventType(Enum):
    """流事件类型"""
    START = "start"
    CONTENT = "content"
    COMPLETE = "complete"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    METADATA = "metadata"


@dataclass
class StreamEvent:
    """流事件"""
    type: StreamEventType
    data: Dict[str, Any]
    timestamp: datetime
    event_id: Optional[str] = None
    retry: Optional[int] = None
    
    def to_sse_format(self) -> str:
        """转换为SSE格式"""
        lines = []
        
        # 事件ID
        if self.event_id:
            lines.append(f"id: {self.event_id}")
        
        # 事件类型
        lines.append(f"event: {self.type.value}")
        
        # 重试间隔
        if self.retry:
            lines.append(f"retry: {self.retry}")
        
        # 数据
        data_with_timestamp = {
            **self.data,
            'timestamp': self.timestamp.isoformat()
        }
        data_json = json.dumps(data_with_timestamp, ensure_ascii=False)
        lines.append(f"data: {data_json}")
        
        # SSE格式需要两个换行符结尾
        lines.append("")
        lines.append("")
        
        return "\n".join(lines)


class StreamBuffer:
    """流缓冲器"""
    
    def __init__(self, max_size: int = 1000):
        """初始化缓冲器"""
        self.max_size = max_size
        self.events: List[StreamEvent] = []
        self._lock = asyncio.Lock()
    
    async def add_event(self, event: StreamEvent):
        """添加事件"""
        async with self._lock:
            self.events.append(event)
            
            # 限制缓冲区大小
            if len(self.events) > self.max_size:
                self.events.pop(0)
    
    async def get_events_since(self, last_event_id: Optional[str] = None) -> List[StreamEvent]:
        """获取指定ID之后的事件"""
        async with self._lock:
            if not last_event_id:
                return self.events.copy()
            
            # 找到指定ID的位置
            start_index = 0
            for i, event in enumerate(self.events):
                if event.event_id == last_event_id:
                    start_index = i + 1
                    break
            
            return self.events[start_index:].copy()
    
    async def clear(self):
        """清空缓冲区"""
        async with self._lock:
            self.events.clear()


class ResponseStreamer:
    """
    响应流处理器
    
    处理AI响应的流式传输，支持SSE和WebSocket
    """
    
    def __init__(self):
        """初始化流处理器"""
        self._active_streams: Dict[str, StreamBuffer] = {}
        self._event_id_counter = 0
    
    def _generate_event_id(self) -> str:
        """生成事件ID"""
        self._event_id_counter += 1
        return f"event_{self._event_id_counter}_{int(datetime.now().timestamp())}"
    
    async def create_stream(self, stream_id: str) -> StreamBuffer:
        """创建新的流"""
        buffer = StreamBuffer()
        self._active_streams[stream_id] = buffer
        
        # 发送开始事件
        start_event = StreamEvent(
            type=StreamEventType.START,
            data={'stream_id': stream_id, 'message': '流开始'},
            timestamp=datetime.now(),
            event_id=self._generate_event_id()
        )
        await buffer.add_event(start_event)
        
        logger.info(f"创建流: {stream_id}")
        return buffer
    
    async def add_content(
        self,
        stream_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """添加内容到流"""
        buffer = self._active_streams.get(stream_id)
        if not buffer:
            logger.warning(f"流 {stream_id} 不存在")
            return
        
        event = StreamEvent(
            type=StreamEventType.CONTENT,
            data={
                'content': content,
                'metadata': metadata or {}
            },
            timestamp=datetime.now(),
            event_id=self._generate_event_id()
        )
        
        await buffer.add_event(event)
    
    async def add_metadata(
        self,
        stream_id: str,
        metadata: Dict[str, Any]
    ):
        """添加元数据到流"""
        buffer = self._active_streams.get(stream_id)
        if not buffer:
            logger.warning(f"流 {stream_id} 不存在")
            return
        
        event = StreamEvent(
            type=StreamEventType.METADATA,
            data=metadata,
            timestamp=datetime.now(),
            event_id=self._generate_event_id()
        )
        
        await buffer.add_event(event)
    
    async def complete_stream(
        self,
        stream_id: str,
        final_data: Optional[Dict[str, Any]] = None
    ):
        """完成流"""
        buffer = self._active_streams.get(stream_id)
        if not buffer:
            logger.warning(f"流 {stream_id} 不存在")
            return
        
        event = StreamEvent(
            type=StreamEventType.COMPLETE,
            data=final_data or {'message': '流完成'},
            timestamp=datetime.now(),
            event_id=self._generate_event_id()
        )
        
        await buffer.add_event(event)
        logger.info(f"完成流: {stream_id}")
    
    async def error_stream(
        self,
        stream_id: str,
        error_message: str,
        error_code: Optional[str] = None
    ):
        """流发生错误"""
        buffer = self._active_streams.get(stream_id)
        if not buffer:
            logger.warning(f"流 {stream_id} 不存在")
            return
        
        event = StreamEvent(
            type=StreamEventType.ERROR,
            data={
                'error': error_message,
                'error_code': error_code
            },
            timestamp=datetime.now(),
            event_id=self._generate_event_id()
        )
        
        await buffer.add_event(event)
        logger.error(f"流 {stream_id} 错误: {error_message}")
    
    async def close_stream(self, stream_id: str):
        """关闭流"""
        if stream_id in self._active_streams:
            del self._active_streams[stream_id]
            logger.info(f"关闭流: {stream_id}")
    
    async def get_sse_generator(
        self,
        stream_id: str,
        last_event_id: Optional[str] = None,
        heartbeat_interval: int = 30
    ) -> AsyncGenerator[str, None]:
        """
        获取SSE生成器
        
        Args:
            stream_id: 流ID
            last_event_id: 最后接收的事件ID
            heartbeat_interval: 心跳间隔（秒）
            
        Yields:
            SSE格式的字符串
        """
        buffer = self._active_streams.get(stream_id)
        if not buffer:
            # 流不存在，发送错误
            error_event = StreamEvent(
                type=StreamEventType.ERROR,
                data={'error': f'流 {stream_id} 不存在'},
                timestamp=datetime.now(),
                event_id=self._generate_event_id()
            )
            yield error_event.to_sse_format()
            return
        
        # 发送历史事件
        if last_event_id:
            historical_events = await buffer.get_events_since(last_event_id)
            for event in historical_events:
                yield event.to_sse_format()
        
        # 实时发送新事件
        last_heartbeat = datetime.now()
        processed_event_ids = set()
        
        while stream_id in self._active_streams:
            try:
                # 获取新事件
                events = await buffer.get_events_since(last_event_id)
                
                for event in events:
                    if event.event_id not in processed_event_ids:
                        yield event.to_sse_format()
                        processed_event_ids.add(event.event_id)
                        last_event_id = event.event_id
                        last_heartbeat = datetime.now()
                        
                        # 如果是完成或错误事件，结束流
                        if event.type in [StreamEventType.COMPLETE, StreamEventType.ERROR]:
                            return
                
                # 发送心跳
                now = datetime.now()
                if (now - last_heartbeat).seconds >= heartbeat_interval:
                    heartbeat_event = StreamEvent(
                        type=StreamEventType.HEARTBEAT,
                        data={'message': 'heartbeat'},
                        timestamp=now,
                        event_id=self._generate_event_id()
                    )
                    yield heartbeat_event.to_sse_format()
                    last_heartbeat = now
                
                # 短暂等待
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"SSE生成器异常: {e}")
                error_event = StreamEvent(
                    type=StreamEventType.ERROR,
                    data={'error': str(e)},
                    timestamp=datetime.now(),
                    event_id=self._generate_event_id()
                )
                yield error_event.to_sse_format()
                break
    
    def create_sse_response(
        self,
        stream_id: str,
        last_event_id: Optional[str] = None
    ) -> StreamingHttpResponse:
        """
        创建SSE响应
        
        Args:
            stream_id: 流ID
            last_event_id: 最后接收的事件ID
            
        Returns:
            流式HTTP响应
        """
        async def sse_generator():
            async for data in self.get_sse_generator(stream_id, last_event_id):
                yield data
        
        response = StreamingHttpResponse(
            sse_generator(),
            content_type='text/event-stream'
        )
        
        # 设置SSE相关头部
        response['Cache-Control'] = 'no-cache'
        response['Connection'] = 'keep-alive'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Cache-Control'
        
        return response
    
    async def process_ai_stream(
        self,
        stream_id: str,
        ai_response_generator: AsyncGenerator[Dict[str, Any], None]
    ):
        """
        处理AI流式响应
        
        Args:
            stream_id: 流ID
            ai_response_generator: AI响应生成器
        """
        try:
            async for chunk in ai_response_generator:
                chunk_type = chunk.get('type', 'content')
                
                if chunk_type == 'start':
                    await self.add_metadata(stream_id, chunk.get('data', {}))
                    
                elif chunk_type == 'content':
                    content = chunk.get('data', {}).get('content', '')
                    metadata = chunk.get('data', {})
                    metadata.pop('content', None)  # 避免重复
                    
                    await self.add_content(stream_id, content, metadata)
                    
                elif chunk_type == 'complete':
                    await self.complete_stream(stream_id, chunk.get('data', {}))
                    break
                    
                elif chunk_type == 'error':
                    error_message = chunk.get('data', {}).get('message', '未知错误')
                    await self.error_stream(stream_id, error_message)
                    break
                    
                else:
                    # 其他类型作为元数据处理
                    await self.add_metadata(stream_id, chunk.get('data', {}))
        
        except Exception as e:
            logger.error(f"处理AI流式响应异常: {e}")
            await self.error_stream(stream_id, str(e))
        
        finally:
            # 确保流被关闭
            await asyncio.sleep(1)  # 给客户端一点时间接收最后的事件
            await self.close_stream(stream_id)
    
    def get_stream_stats(self) -> Dict[str, Any]:
        """获取流统计信息"""
        return {
            'active_streams': len(self._active_streams),
            'stream_ids': list(self._active_streams.keys()),
            'total_events': sum(len(buffer.events) for buffer in self._active_streams.values()),
            'event_id_counter': self._event_id_counter
        }
    
    async def cleanup_inactive_streams(self, max_age_minutes: int = 30):
        """清理不活跃的流"""
        current_time = datetime.now()
        inactive_streams = []
        
        for stream_id, buffer in self._active_streams.items():
            if buffer.events:
                last_event_time = buffer.events[-1].timestamp
                age_minutes = (current_time - last_event_time).total_seconds() / 60
                
                if age_minutes > max_age_minutes:
                    inactive_streams.append(stream_id)
        
        for stream_id in inactive_streams:
            await self.close_stream(stream_id)
            logger.info(f"清理不活跃流: {stream_id}")
        
        return len(inactive_streams)


class StreamingResponse:
    """流式响应包装器"""
    
    def __init__(self, streamer: ResponseStreamer, stream_id: str):
        """初始化"""
        self.streamer = streamer
        self.stream_id = stream_id
    
    async def write_content(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        """写入内容"""
        await self.streamer.add_content(self.stream_id, content, metadata)
    
    async def write_metadata(self, metadata: Dict[str, Any]):
        """写入元数据"""
        await self.streamer.add_metadata(self.stream_id, metadata)
    
    async def complete(self, final_data: Optional[Dict[str, Any]] = None):
        """完成响应"""
        await self.streamer.complete_stream(self.stream_id, final_data)
    
    async def error(self, error_message: str, error_code: Optional[str] = None):
        """响应错误"""
        await self.streamer.error_stream(self.stream_id, error_message, error_code)
    
    async def close(self):
        """关闭响应"""
        await self.streamer.close_stream(self.stream_id)

