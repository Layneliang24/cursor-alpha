# -*- coding: utf-8 -*-
"""
AI适配器单元测试
验证适配器接口和功能的正确性
"""
import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from apps.ai.adapters.base import (
    BaseAIAdapter, AIModelConfig, AIMessage, AIResponse, 
    HealthCheckResult, MessageRole, AIProviderType, MockAIAdapter
)
from apps.ai.adapters.openai_adapter import OpenAIAdapter
from apps.ai.adapters.claude_adapter import ClaudeAdapter
from apps.ai.adapters.google_adapter import GoogleAdapter
from apps.ai.adapters.factory import AIAdapterFactory
from apps.ai.adapters.exceptions import (
    AIServiceException, RateLimitException, AuthenticationException,
    ModelNotFoundException, QuotaExceededException
)


class TestAIModelConfig:
    """测试AI模型配置"""
    
    def test_config_creation(self):
        """测试配置创建"""
        config = AIModelConfig(
            provider=AIProviderType.OPENAI,
            model_name="gpt-4",
            api_key="sk-test123"
        )
        
        assert config.provider == AIProviderType.OPENAI
        assert config.model_name == "gpt-4"
        assert config.api_key == "sk-test123"
        assert config.max_tokens == 4000
        assert config.temperature == 0.7
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试无效temperature
        with pytest.raises(ValueError, match="temperature必须在0-2之间"):
            AIModelConfig(
                provider=AIProviderType.OPENAI,
                model_name="gpt-4",
                api_key="sk-test123",
                temperature=3.0
            )
        
        # 测试空API密钥
        with pytest.raises(ValueError, match="api_key不能为空"):
            AIModelConfig(
                provider=AIProviderType.OPENAI,
                model_name="gpt-4",
                api_key=""
            )
    
    def test_max_tokens_adjustment(self):
        """测试max_tokens自动调整"""
        config = AIModelConfig(
            provider=AIProviderType.OPENAI,
            model_name="gpt-4",
            api_key="sk-test123",
            max_tokens=10000,  # 超过context_window
            context_window=8192
        )
        
        assert config.max_tokens == 7192  # context_window - 1000


class TestAIMessage:
    """测试AI消息"""
    
    def test_message_creation(self):
        """测试消息创建"""
        message = AIMessage(
            role=MessageRole.USER,
            content="Hello, world!"
        )
        
        assert message.role == MessageRole.USER
        assert message.content == "Hello, world!"
        assert message.timestamp > 0
        assert message.metadata == {}
    
    def test_message_with_metadata(self):
        """测试带元数据的消息"""
        metadata = {"source": "test", "priority": "high"}
        message = AIMessage(
            role=MessageRole.ASSISTANT,
            content="Response",
            metadata=metadata
        )
        
        assert message.metadata == metadata


class TestAIResponse:
    """测试AI响应"""
    
    def test_response_creation(self):
        """测试响应创建"""
        response = AIResponse(
            content="Hello!",
            model="gpt-4",
            provider="openai",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        )
        
        assert response.content == "Hello!"
        assert response.model == "gpt-4"
        assert response.provider == "openai"
        assert response.usage["total_tokens"] == 15
    
    def test_cost_calculation(self):
        """测试成本计算"""
        config = AIModelConfig(
            provider=AIProviderType.OPENAI,
            model_name="gpt-4",
            api_key="sk-test123",
            cost_per_input_token=0.00003,
            cost_per_output_token=0.00006
        )
        
        response = AIResponse(
            content="Hello!",
            model="gpt-4",
            provider="openai",
            usage={"prompt_tokens": 1000, "completion_tokens": 500}
        )
        
        cost = response.calculate_cost(config)
        expected_cost = (1000 * 0.00003) + (500 * 0.00006)
        assert abs(cost - expected_cost) < 0.0001


class TestMockAIAdapter:
    """测试Mock AI适配器"""
    
    @pytest.fixture
    def mock_config(self):
        return AIModelConfig(
            provider=AIProviderType.CUSTOM,
            model_name="mock-model",
            api_key="mock-key"
        )
    
    @pytest.fixture
    def mock_adapter(self, mock_config):
        return MockAIAdapter(mock_config)
    
    def test_adapter_creation(self, mock_adapter):
        """测试适配器创建"""
        assert mock_adapter.config.model_name == "mock-model"
        assert mock_adapter.provider_type == AIProviderType.CUSTOM
    
    @pytest.mark.asyncio
    async def test_generate_response(self, mock_adapter):
        """测试生成响应"""
        messages = [
            AIMessage(role=MessageRole.USER, content="Hello")
        ]
        
        response = await mock_adapter.generate_response(messages)
        
        assert isinstance(response, AIResponse)
        assert "Hello" in response.content
        assert response.model == "mock-model"
        assert response.provider == "custom"
        assert response.usage is not None
    
    @pytest.mark.asyncio
    async def test_stream_response(self, mock_adapter):
        """测试流式响应"""
        messages = [
            AIMessage(role=MessageRole.USER, content="Hello")
        ]
        
        chunks = []
        async for chunk in mock_adapter.stream_response(messages):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert "Hello" in full_response
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_adapter):
        """测试健康检查"""
        result = await mock_adapter.health_check()
        
        assert isinstance(result, HealthCheckResult)
        assert result.is_healthy == True
        assert result.model_available == True
        assert result.response_time > 0
    
    @pytest.mark.asyncio
    async def test_token_estimation(self, mock_adapter):
        """测试token估算"""
        text = "Hello, world! This is a test message."
        tokens = await mock_adapter.estimate_tokens(text)
        
        assert tokens > 0
        assert tokens < len(text)  # token数应该少于字符数
    
    @pytest.mark.asyncio
    async def test_context_validation(self, mock_adapter):
        """测试上下文长度验证"""
        # 短消息应该通过验证
        short_messages = [
            AIMessage(role=MessageRole.USER, content="Hello")
        ]
        assert await mock_adapter.validate_context_length(short_messages) == True
        
        # 长消息应该失败
        long_content = "x" * 50000  # 超长内容
        long_messages = [
            AIMessage(role=MessageRole.USER, content=long_content)
        ]
        assert await mock_adapter.validate_context_length(long_messages) == False
    
    def test_message_formatting(self, mock_adapter):
        """测试消息格式化"""
        messages = [
            AIMessage(role=MessageRole.SYSTEM, content="You are helpful"),
            AIMessage(role=MessageRole.USER, content="Hello"),
            AIMessage(role=MessageRole.ASSISTANT, content="Hi there!")
        ]
        
        formatted = mock_adapter.format_messages(messages)
        
        assert len(formatted) == 3
        assert formatted[0]["role"] == "system"
        assert formatted[1]["role"] == "user"
        assert formatted[2]["role"] == "assistant"
        assert formatted[0]["content"] == "You are helpful"


@pytest.mark.asyncio
class TestOpenAIAdapter:
    """测试OpenAI适配器"""
    
    @pytest.fixture
    def openai_config(self):
        return AIModelConfig(
            provider=AIProviderType.OPENAI,
            model_name="gpt-4",
            api_key="sk-test123",
            base_url="https://api.openai.com/v1"
        )
    
    @pytest.fixture
    def openai_adapter(self, openai_config):
        return OpenAIAdapter(openai_config)
    
    def test_adapter_initialization(self, openai_adapter):
        """测试适配器初始化"""
        assert openai_adapter.base_url == "https://api.openai.com/v1"
        assert "Bearer sk-test123" in openai_adapter.headers["Authorization"]
        assert openai_adapter.headers["Content-Type"] == "application/json"
    
    def test_config_validation(self, openai_adapter):
        """测试配置验证"""
        # 应该不抛出异常
        openai_adapter.validate_config()
        
        # 检查模型信息是否更新
        if openai_adapter.config.model_name in OpenAIAdapter.SUPPORTED_MODELS:
            model_info = OpenAIAdapter.SUPPORTED_MODELS[openai_adapter.config.model_name]
            assert openai_adapter.config.context_window == model_info['context_window']
    
    async def test_token_estimation(self, openai_adapter):
        """测试OpenAI token估算"""
        english_text = "Hello world"
        chinese_text = "你好世界"
        mixed_text = "Hello 世界"
        
        english_tokens = await openai_adapter.estimate_tokens(english_text)
        chinese_tokens = await openai_adapter.estimate_tokens(chinese_text)
        mixed_tokens = await openai_adapter.estimate_tokens(mixed_text)
        
        assert english_tokens > 0
        assert chinese_tokens > 0
        assert mixed_tokens > 0
        
        # 中文应该比英文估算更多token（相同字符数）
        assert chinese_tokens > english_tokens


@pytest.mark.asyncio
class TestClaudeAdapter:
    """测试Claude适配器"""
    
    @pytest.fixture
    def claude_config(self):
        return AIModelConfig(
            provider=AIProviderType.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key="sk-ant-test123"
        )
    
    @pytest.fixture
    def claude_adapter(self, claude_config):
        return ClaudeAdapter(claude_config)
    
    def test_adapter_initialization(self, claude_adapter):
        """测试Claude适配器初始化"""
        assert claude_adapter.base_url == "https://api.anthropic.com/v1"
        assert claude_adapter.headers["x-api-key"] == "sk-ant-test123"
        assert claude_adapter.headers["anthropic-version"] == "2023-06-01"
    
    def test_message_formatting(self, claude_adapter):
        """测试Claude消息格式化"""
        messages = [
            AIMessage(role=MessageRole.SYSTEM, content="You are helpful"),
            AIMessage(role=MessageRole.USER, content="Hello"),
            AIMessage(role=MessageRole.ASSISTANT, content="Hi!")
        ]
        
        formatted = claude_adapter.format_messages(messages)
        
        assert formatted["system"] == "You are helpful"
        assert len(formatted["messages"]) == 2
        assert formatted["messages"][0]["role"] == "user"
        assert formatted["messages"][1]["role"] == "assistant"
    
    def test_config_validation(self, claude_adapter):
        """测试Claude配置验证"""
        claude_adapter.validate_config()
        
        # 检查模型信息是否更新
        if claude_adapter.config.model_name in ClaudeAdapter.SUPPORTED_MODELS:
            model_info = ClaudeAdapter.SUPPORTED_MODELS[claude_adapter.config.model_name]
            assert claude_adapter.config.context_window == model_info['context_window']


class TestAIExceptions:
    """测试AI异常"""
    
    def test_base_exception(self):
        """测试基础异常"""
        exc = AIServiceException(
            "测试错误",
            error_code="TEST_001",
            provider="test"
        )
        
        assert str(exc) == "测试错误"
        assert exc.error_code == "TEST_001"
        assert exc.provider == "test"
        
        error_dict = exc.to_dict()
        assert error_dict["error"] == "测试错误"
        assert error_dict["error_code"] == "TEST_001"
        assert error_dict["provider"] == "test"
        assert error_dict["type"] == "AIServiceException"
    
    def test_rate_limit_exception(self):
        """测试频率限制异常"""
        exc = RateLimitException(retry_after=60, provider="openai")
        
        assert exc.retry_after == 60
        assert exc.provider == "openai"
    
    def test_model_not_found_exception(self):
        """测试模型不存在异常"""
        exc = ModelNotFoundException("gpt-5", provider="openai")
        
        assert exc.model_name == "gpt-5"
        assert "gpt-5" in str(exc)


@pytest.mark.asyncio
class TestBaseAdapterFunctionality:
    """测试基础适配器功能"""
    
    @pytest.fixture
    def mock_config(self):
        return AIModelConfig(
            provider=AIProviderType.CUSTOM,
            model_name="test-model",
            api_key="test-key"
        )
    
    @pytest.fixture
    def mock_adapter(self, mock_config):
        return MockAIAdapter(mock_config)
    
    async def test_retry_mechanism(self, mock_adapter):
        """测试重试机制"""
        call_count = 0
        
        async def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RateLimitException("Rate limited")
            return "success"
        
        # 设置重试参数
        mock_adapter.config.max_retries = 3
        mock_adapter.config.retry_delay = 0.01  # 快速测试
        
        result = await mock_adapter.retry_on_failure(failing_function)
        assert result == "success"
        assert call_count == 3
    
    async def test_retry_exhausted(self, mock_adapter):
        """测试重试耗尽"""
        async def always_failing_function():
            raise RateLimitException("Always failing")
        
        mock_adapter.config.max_retries = 2
        mock_adapter.config.retry_delay = 0.01
        
        with pytest.raises(RateLimitException):
            await mock_adapter.retry_on_failure(always_failing_function)
    
    async def test_non_retryable_exception(self, mock_adapter):
        """测试不可重试异常"""
        async def auth_failing_function():
            raise AuthenticationException("Auth failed")
        
        # 认证异常不应该重试
        with pytest.raises(AuthenticationException):
            await mock_adapter.retry_on_failure(auth_failing_function)
    
    def test_message_creation_helpers(self, mock_adapter):
        """测试消息创建辅助方法"""
        system_msg = mock_adapter.create_system_message("System prompt")
        user_msg = mock_adapter.create_user_message("User input")
        assistant_msg = mock_adapter.create_assistant_message("Assistant response")
        
        assert system_msg.role == MessageRole.SYSTEM
        assert user_msg.role == MessageRole.USER
        assert assistant_msg.role == MessageRole.ASSISTANT
        
        assert system_msg.content == "System prompt"
        assert user_msg.content == "User input"
        assert assistant_msg.content == "Assistant response"
    
    def test_health_status_management(self, mock_adapter):
        """测试健康状态管理"""
        # 初始状态应该是不健康
        assert not mock_adapter.is_healthy()
        assert mock_adapter.get_health_status() is None
        
        # 设置健康状态
        health_result = HealthCheckResult(
            is_healthy=True,
            response_time=0.1,
            model_available=True
        )
        mock_adapter._last_health_check = health_result
        
        assert mock_adapter.is_healthy()
        assert mock_adapter.get_health_status() == health_result
    
    async def test_health_check_expiry(self, mock_adapter):
        """测试健康检查过期"""
        # 设置过期的健康检查
        old_time = time.time() - 400  # 6分钟前
        health_result = HealthCheckResult(
            is_healthy=True,
            response_time=0.1,
            last_check=old_time
        )
        mock_adapter._last_health_check = health_result
        
        # 应该被认为不健康（超过5分钟）
        assert not mock_adapter.is_healthy()


# 集成测试标记
@pytest.mark.integration
@pytest.mark.asyncio
class TestAdapterIntegration:
    """适配器集成测试（需要真实API密钥）"""
    
    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration"),
        reason="需要 --run-integration 标志运行集成测试"
    )
    async def test_openai_real_api(self):
        """测试真实OpenAI API调用"""
        import os
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("需要OPENAI_API_KEY环境变量")
        
        config = AIModelConfig(
            provider=AIProviderType.OPENAI,
            model_name="gpt-3.5-turbo",
            api_key=api_key,
            max_tokens=50
        )
        
        adapter = OpenAIAdapter(config)
        
        messages = [
            adapter.create_system_message("You are a helpful assistant."),
            adapter.create_user_message("Say hello in one word.")
        ]
        
        response = await adapter.generate_response(messages)
        
        assert isinstance(response, AIResponse)
        assert len(response.content) > 0
        assert response.provider == "openai"
        assert response.usage is not None
    
    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration"),
        reason="需要 --run-integration 标志运行集成测试"
    )
    async def test_claude_real_api(self):
        """测试真实Claude API调用"""
        import os
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            pytest.skip("需要ANTHROPIC_API_KEY环境变量")
        
        config = AIModelConfig(
            provider=AIProviderType.ANTHROPIC,
            model_name="claude-3-haiku-20240307",
            api_key=api_key,
            max_tokens=50
        )
        
        adapter = ClaudeAdapter(config)
        
        messages = [
            adapter.create_user_message("Say hello in one word.")
        ]
        
        response = await adapter.generate_response(messages)
        
        assert isinstance(response, AIResponse)
        assert len(response.content) > 0
        assert response.provider == "anthropic"
        assert response.usage is not None


@pytest.mark.asyncio
class TestGoogleAdapter:
    """测试Google Gemini适配器"""
    
    @pytest.fixture
    def google_config(self):
        return AIModelConfig(
            provider=AIProviderType.GOOGLE,
            model_name="gemini-1.5-pro",
            api_key="test-google-key-123"
        )
    
    @pytest.fixture
    def google_adapter(self, google_config):
        return GoogleAdapter(google_config)
    
    def test_adapter_initialization(self, google_adapter):
        """测试Google适配器初始化"""
        assert google_adapter.base_url == "https://generativelanguage.googleapis.com/v1beta"
        assert "key=test-google-key-123" in google_adapter.api_key_param
    
    def test_message_formatting(self, google_adapter):
        """测试Google消息格式化"""
        messages = [
            AIMessage(role=MessageRole.SYSTEM, content="You are helpful"),
            AIMessage(role=MessageRole.USER, content="Hello"),
            AIMessage(role=MessageRole.ASSISTANT, content="Hi!")
        ]
        
        formatted = google_adapter.format_messages(messages)
        
        assert "contents" in formatted
        contents = formatted["contents"]
        assert len(contents) == 3
        
        # 系统消息应该转换为用户消息
        assert contents[0]["role"] == "user"
        assert "[System]" in contents[0]["parts"][0]["text"]
        
        # 助手角色应该转换为model
        assert contents[2]["role"] == "model"
    
    async def test_token_estimation(self, google_adapter):
        """测试Google token估算"""
        text = "Hello 世界 test"
        tokens = await google_adapter.estimate_tokens(text)
        assert tokens > 0


class TestAIAdapterFactory:
    """测试AI适配器工厂"""
    
    def test_create_openai_adapter(self):
        """测试创建OpenAI适配器"""
        config = AIModelConfig(
            provider=AIProviderType.OPENAI,
            model_name="gpt-4",
            api_key="sk-test123"
        )
        
        adapter = AIAdapterFactory.create_adapter(config)
        assert isinstance(adapter, OpenAIAdapter)
        assert adapter.config.model_name == "gpt-4"
    
    def test_create_claude_adapter(self):
        """测试创建Claude适配器"""
        config = AIModelConfig(
            provider=AIProviderType.ANTHROPIC,
            model_name="claude-3-5-sonnet-20241022",
            api_key="sk-ant-test123"
        )
        
        adapter = AIAdapterFactory.create_adapter(config)
        assert isinstance(adapter, ClaudeAdapter)
    
    def test_create_google_adapter(self):
        """测试创建Google适配器"""
        config = AIModelConfig(
            provider=AIProviderType.GOOGLE,
            model_name="gemini-1.5-pro",
            api_key="google-key-123"
        )
        
        adapter = AIAdapterFactory.create_adapter(config)
        assert isinstance(adapter, GoogleAdapter)
    
    def test_infer_provider_from_model(self):
        """测试从模型名称推断提供商"""
        # 测试自动推断
        config = AIModelConfig(
            provider=AIProviderType.CUSTOM,  # 使用CUSTOM触发推断
            model_name="gpt-4",
            api_key="sk-test123"
        )
        
        adapter = AIAdapterFactory.create_adapter(config)
        assert isinstance(adapter, OpenAIAdapter)
    
    def test_unsupported_provider(self):
        """测试不支持的提供商"""
        config = AIModelConfig(
            provider=AIProviderType.LOCAL,  # 暂不支持
            model_name="local-model",
            api_key="local-key"
        )
        
        with pytest.raises(ModelNotFoundException):
            AIAdapterFactory.create_adapter(config)
    
    def test_get_supported_models(self):
        """测试获取支持的模型列表"""
        supported = AIAdapterFactory.get_supported_models()
        
        assert AIProviderType.OPENAI in supported
        assert AIProviderType.ANTHROPIC in supported
        assert AIProviderType.GOOGLE in supported
        
        assert 'gpt-4' in supported[AIProviderType.OPENAI]
        assert 'claude-3-5-sonnet-20241022' in supported[AIProviderType.ANTHROPIC]
        assert 'gemini-1.5-pro' in supported[AIProviderType.GOOGLE]
    
    def test_is_model_supported(self):
        """测试模型支持检查"""
        # 测试支持的模型
        assert AIAdapterFactory.is_model_supported("gpt-4", AIProviderType.OPENAI)
        assert AIAdapterFactory.is_model_supported("claude-3-5-sonnet-20241022", AIProviderType.ANTHROPIC)
        assert AIAdapterFactory.is_model_supported("gemini-1.5-pro", AIProviderType.GOOGLE)
        
        # 测试不支持的模型
        assert not AIAdapterFactory.is_model_supported("nonexistent-model", AIProviderType.OPENAI)
        
        # 测试无提供商的检查
        assert AIAdapterFactory.is_model_supported("gpt-4")  # 应该在所有提供商中找到
        assert not AIAdapterFactory.is_model_supported("nonexistent-model")
    
    def test_get_model_info(self):
        """测试获取模型信息"""
        # 测试指定提供商
        info = AIAdapterFactory.get_model_info("gpt-4", AIProviderType.OPENAI)
        assert info is not None
        assert 'context_window' in info
        assert 'supports_streaming' in info
        
        # 测试自动查找
        info = AIAdapterFactory.get_model_info("claude-3-5-sonnet-20241022")
        assert info is not None
        assert 'provider' in info
        assert info['provider'] == AIProviderType.ANTHROPIC
        
        # 测试不存在的模型
        info = AIAdapterFactory.get_model_info("nonexistent-model")
        assert info is None
    
    def test_register_custom_adapter(self):
        """测试注册自定义适配器"""
        class CustomAdapter(BaseAIAdapter):
            def validate_config(self):
                pass
            
            async def generate_response(self, messages, **kwargs):
                return AIResponse("test", "custom", "custom")
            
            async def stream_response(self, messages, **kwargs):
                yield "test"
            
            async def health_check(self):
                return HealthCheckResult(True, 0.1)
        
        # 注册自定义适配器
        AIAdapterFactory.register_adapter(AIProviderType.CUSTOM, CustomAdapter)
        
        config = AIModelConfig(
            provider=AIProviderType.CUSTOM,
            model_name="custom-model",
            api_key="custom-key"
        )
        
        adapter = AIAdapterFactory.create_adapter(config)
        assert isinstance(adapter, CustomAdapter)


# pytest配置
def pytest_addoption(parser):
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="运行集成测试（需要真实API密钥）"
    )
