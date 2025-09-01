"""
测试数据工厂
使用Factory Boy创建测试数据
"""
import factory
from django.contrib.auth import get_user_model
from apps.ai.config_models import (
    AIProvider, APIKey, AIModel, ModelConfig, 
    TokenUsage, UsageQuota, FailoverStrategy
)

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """用户工厂"""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True


class AIProviderFactory(factory.django.DjangoModelFactory):
    """AI提供商工厂"""
    class Meta:
        model = AIProvider
    
    name = factory.Sequence(lambda n: f'provider_{n}')
    provider_type = factory.Iterator(['openai', 'anthropic', 'google', 'azure'])
    display_name = factory.LazyAttribute(lambda obj: f'{obj.provider_type.title()} Provider')
    base_url = factory.LazyAttribute(lambda obj: f'https://api.{obj.provider_type}.com')
    api_version = 'v1'
    is_active = True
    is_healthy = True
    created_by = factory.SubFactory(UserFactory)


class APIKeyFactory(factory.django.DjangoModelFactory):
    """API密钥工厂"""
    class Meta:
        model = APIKey
    
    provider = factory.SubFactory(AIProviderFactory)
    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f'key_{n}')
    encrypted_key = factory.Sequence(lambda n: f'encrypted_key_{n}')
    key_prefix = factory.LazyAttribute(lambda obj: obj.name[:8].upper())
    is_active = True
    is_default = False


class AIModelFactory(factory.django.DjangoModelFactory):
    """AI模型工厂"""
    class Meta:
        model = AIModel
    
    name = factory.Iterator(['GPT-4', 'GPT-3.5', 'Claude-3', 'Gemini Pro'])
    provider = factory.SubFactory(AIProviderFactory)
    model_id = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))
    max_tokens = factory.Iterator([4096, 8192, 16384, 32768])
    temperature = factory.Faker('pyfloat', min_value=0.0, max_value=2.0)
    created_by = factory.SubFactory(UserFactory)


class ModelConfigFactory(factory.django.DjangoModelFactory):
    """模型配置工厂"""
    class Meta:
        model = ModelConfig
    
    name = factory.Sequence(lambda n: f'config_{n}')
    model = factory.SubFactory(AIModelFactory)
    temperature = factory.Faker('pyfloat', min_value=0.0, max_value=2.0)
    max_tokens = factory.Iterator([1024, 2048, 4096, 8192])
    top_p = factory.Faker('pyfloat', min_value=0.0, max_value=1.0)
    frequency_penalty = factory.Faker('pyfloat', min_value=-2.0, max_value=2.0)
    presence_penalty = factory.Faker('pyfloat', min_value=-2.0, max_value=2.0)
    created_by = factory.SubFactory(UserFactory)


class TokenUsageFactory(factory.django.DjangoModelFactory):
    """Token使用量工厂"""
    class Meta:
        model = TokenUsage
    
    user = factory.SubFactory(UserFactory)
    provider = factory.SubFactory(AIProviderFactory)
    model_name = factory.Iterator(['gpt-4', 'claude-3', 'gemini-pro'])
    prompt_tokens = factory.Faker('random_int', min=10, max=1000)
    completion_tokens = factory.Faker('random_int', min=5, max=500)
    total_tokens = factory.LazyAttribute(lambda obj: obj.prompt_tokens + obj.completion_tokens)
    cost = factory.Faker('pyfloat', min_value=0.001, max_value=0.1)


class UsageQuotaFactory(factory.django.DjangoModelFactory):
    """使用配额工厂"""
    class Meta:
        model = UsageQuota
    
    user = factory.SubFactory(UserFactory)
    provider = factory.SubFactory(AIProviderFactory)
    quota_type = factory.Iterator(['daily', 'monthly', 'yearly'])
    limit = factory.Faker('random_int', min=100000, max=10000000)
    used = factory.Faker('random_int', min=0, max=1000000)
    reset_date = factory.Faker('date_this_month')


class FailoverStrategyFactory(factory.django.DjangoModelFactory):
    """故障转移策略工厂"""
    class Meta:
        model = FailoverStrategy
    
    name = factory.Sequence(lambda n: f'strategy_{n}')
    priority = factory.Sequence(lambda n: n + 1)
    providers = factory.LazyFunction(lambda: [])
    description = factory.Faker('text', max_nb_chars=200)
    created_by = factory.SubFactory(UserFactory)


# 预定义的测试数据
class TestData:
    """预定义测试数据"""
    
    @staticmethod
    def create_basic_test_data():
        """创建基础测试数据"""
        # 创建测试用户
        user = UserFactory()
        
        # 创建提供商
        openai_provider = AIProviderFactory(
            name='openai',
            provider_type='openai',
            display_name='OpenAI',
            base_url='https://api.openai.com'
        )
        
        anthropic_provider = AIProviderFactory(
            name='anthropic',
            provider_type='anthropic',
            display_name='Anthropic',
            base_url='https://api.anthropic.com'
        )
        
        # 创建API密钥
        openai_key = APIKeyFactory(
            provider=openai_provider,
            user=user,
            name='OpenAI Key',
            encrypted_key='sk-test-openai-key'
        )
        
        anthropic_key = APIKeyFactory(
            provider=anthropic_provider,
            user=user,
            name='Anthropic Key',
            encrypted_key='sk-test-anthropic-key'
        )
        
        # 创建模型
        gpt4_model = AIModelFactory(
            name='GPT-4',
            provider=openai_provider,
            model_id='gpt-4',
            max_tokens=4096
        )
        
        claude_model = AIModelFactory(
            name='Claude-3',
            provider=anthropic_provider,
            model_id='claude-3',
            max_tokens=8192
        )
        
        # 创建配置
        default_config = ModelConfigFactory(
            name='Default Config',
            model=gpt4_model,
            temperature=0.7,
            max_tokens=2048
        )
        
        # 创建使用量记录
        usage1 = TokenUsageFactory(
            user=user,
            provider=openai_provider,
            model_name='gpt-4',
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            cost=0.003
        )
        
        usage2 = TokenUsageFactory(
            user=user,
            provider=anthropic_provider,
            model_name='claude-3',
            prompt_tokens=200,
            completion_tokens=100,
            total_tokens=300,
            cost=0.006
        )
        
        # 创建配额
        daily_quota = UsageQuotaFactory(
            user=user,
            provider=openai_provider,
            quota_type='daily',
            limit=1000000,
            used=500000
        )
        
        # 创建故障转移策略
        strategy = FailoverStrategyFactory(
            name='Primary Strategy',
            priority=1,
            providers=[openai_provider.id, anthropic_provider.id]
        )
        
        return {
            'user': user,
            'providers': [openai_provider, anthropic_provider],
            'api_keys': [openai_key, anthropic_key],
            'models': [gpt4_model, claude_model],
            'configs': [default_config],
            'usage_records': [usage1, usage2],
            'quotas': [daily_quota],
            'strategies': [strategy]
        }
    
    @staticmethod
    def create_mock_api_responses():
        """创建Mock API响应数据"""
        return {
            'openai_models': {
                'data': [
                    {
                        'id': 'gpt-4',
                        'object': 'model',
                        'created': 1677610602,
                        'owned_by': 'openai',
                        'permission': [],
                        'root': 'gpt-4',
                        'parent': None
                    },
                    {
                        'id': 'gpt-3.5-turbo',
                        'object': 'model',
                        'created': 1677610602,
                        'owned_by': 'openai',
                        'permission': [],
                        'root': 'gpt-3.5-turbo',
                        'parent': None
                    }
                ],
                'object': 'list'
            },
            'anthropic_models': {
                'data': [
                    {
                        'id': 'claude-3-opus-20240229',
                        'name': 'claude-3-opus-20240229',
                        'max_input_tokens': 200000,
                        'max_output_tokens': 4096
                    },
                    {
                        'id': 'claude-3-sonnet-20240229',
                        'name': 'claude-3-sonnet-20240229',
                        'max_input_tokens': 200000,
                        'max_output_tokens': 4096
                    }
                ]
            },
            'google_models': {
                'models': [
                    {
                        'name': 'models/gemini-pro',
                        'version': '001',
                        'displayName': 'Gemini Pro',
                        'description': 'Best model for scaling across a wide range of tasks',
                        'inputTokenLimit': 30720,
                        'outputTokenLimit': 2048
                    },
                    {
                        'name': 'models/gemini-pro-vision',
                        'version': '001',
                        'displayName': 'Gemini Pro Vision',
                        'description': 'Best model for image and text tasks',
                        'inputTokenLimit': 30720,
                        'outputTokenLimit': 2048
                    }
                ]
            }
        }
    
    @staticmethod
    def create_test_configs():
        """创建测试配置数据"""
        return {
            'provider_configs': {
                'openai': {
                    'base_url': 'https://api.openai.com',
                    'api_version': 'v1',
                    'models': ['gpt-4', 'gpt-3.5-turbo'],
                    'rate_limits': {
                        'requests_per_minute': 60,
                        'tokens_per_minute': 90000
                    }
                },
                'anthropic': {
                    'base_url': 'https://api.anthropic.com',
                    'api_version': 'v1',
                    'models': ['claude-3-opus', 'claude-3-sonnet'],
                    'rate_limits': {
                        'requests_per_minute': 50,
                        'tokens_per_minute': 80000
                    }
                },
                'google': {
                    'base_url': 'https://generativelanguage.googleapis.com',
                    'api_version': 'v1',
                    'models': ['gemini-pro', 'gemini-pro-vision'],
                    'rate_limits': {
                        'requests_per_minute': 60,
                        'tokens_per_minute': 100000
                    }
                }
            },
            'model_configs': {
                'gpt-4': {
                    'temperature': 0.7,
                    'max_tokens': 4096,
                    'top_p': 0.9,
                    'frequency_penalty': 0.0,
                    'presence_penalty': 0.0
                },
                'claude-3-opus': {
                    'temperature': 0.5,
                    'max_tokens': 8192,
                    'top_p': 0.8,
                    'frequency_penalty': 0.0,
                    'presence_penalty': 0.0
                },
                'gemini-pro': {
                    'temperature': 0.6,
                    'max_tokens': 2048,
                    'top_p': 0.85,
                    'frequency_penalty': 0.0,
                    'presence_penalty': 0.0
                }
            }
        }
