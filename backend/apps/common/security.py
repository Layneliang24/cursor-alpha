"""
安全工具类 - SQL注入防护和数据验证
基于2024年Django安全最佳实践
"""
import re
import logging
from typing import Any, Dict, List, Optional, Union
from django.db import connection
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.html import escape
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

class SQLSecurityUtils:
    """SQL安全工具类"""
    
    # 危险SQL关键词黑名单
    DANGEROUS_SQL_KEYWORDS = [
        'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE',
        'UNION', 'SELECT', 'EXEC', 'EXECUTE', 'SCRIPT', 'DECLARE', 'SHUTDOWN',
        '--', '/*', '*/', 'xp_', 'sp_', 'INFORMATION_SCHEMA'
    ]
    
    # 允许的表名白名单（用于动态查询）
    ALLOWED_TABLES = [
        'english_idiomaticexpression',
        'english_newsitem', 
        'english_expressionsource',
        'english_typingword',
        'english_word',
        'english_dictionary',
        'config_manager_aiprovider',
        'config_manager_apikey',
        'config_manager_modelconfig',
        'config_manager_tokenusage'
    ]
    
    # 允许的列名白名单
    ALLOWED_COLUMNS = [
        'id', 'name', 'title', 'content', 'category', 'status', 'created_at',
        'updated_at', 'frequency_score', 'difficulty_level', 'chapter',
        'provider_type', 'display_name', 'api_endpoint', 'is_active'
    ]
    
    @classmethod
    def validate_table_name(cls, table_name: str) -> str:
        """验证表名是否安全"""
        if not table_name or not isinstance(table_name, str):
            raise ValidationError("表名不能为空")
        
        # 移除空白字符
        table_name = table_name.strip()
        
        # 检查是否在白名单中
        if table_name not in cls.ALLOWED_TABLES:
            raise ValidationError(f"不允许访问的表: {table_name}")
        
        # 检查是否包含危险字符
        if not re.match(r'^[a-z_]+$', table_name):
            raise ValidationError("表名包含非法字符")
        
        return table_name
    
    @classmethod
    def validate_column_name(cls, column_name: str) -> str:
        """验证列名是否安全"""
        if not column_name or not isinstance(column_name, str):
            raise ValidationError("列名不能为空")
        
        # 移除空白字符
        column_name = column_name.strip()
        
        # 检查是否在白名单中
        if column_name not in cls.ALLOWED_COLUMNS:
            raise ValidationError(f"不允许访问的列: {column_name}")
        
        # 检查是否包含危险字符
        if not re.match(r'^[a-z_]+$', column_name):
            raise ValidationError("列名包含非法字符")
        
        return column_name
    
    @classmethod
    def validate_sql_input(cls, user_input: str) -> str:
        """验证用户输入是否包含SQL注入攻击向量"""
        if not user_input or not isinstance(user_input, str):
            return ""
        
        # 转换为大写进行检查
        upper_input = user_input.upper()
        
        # 检查危险关键词
        for keyword in cls.DANGEROUS_SQL_KEYWORDS:
            if keyword in upper_input:
                logger.warning(f"检测到潜在SQL注入攻击: {user_input}")
                raise ValidationError(f"输入包含不允许的内容: {keyword}")
        
        # 检查SQL注释符号
        if '--' in user_input or '/*' in user_input or '*/' in user_input:
            raise ValidationError("输入包含SQL注释符号")
        
        # 检查引号配对
        single_quotes = user_input.count("'")
        double_quotes = user_input.count('"')
        if single_quotes % 2 != 0 or double_quotes % 2 != 0:
            logger.warning(f"检测到不配对的引号: {user_input}")
        
        return user_input.strip()
    
    @classmethod
    def safe_execute_query(cls, query: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """安全执行原生SQL查询"""
        if not query or not isinstance(query, str):
            raise ValueError("查询语句不能为空")
        
        # 验证查询语句（仅允许SELECT）
        query_upper = query.strip().upper()
        if not query_upper.startswith('SELECT'):
            raise ValidationError("仅允许SELECT查询")
        
        # 检查危险关键词
        for keyword in ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']:
            if keyword in query_upper:
                raise ValidationError(f"查询包含危险操作: {keyword}")
        
        try:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                columns = [col[0] for col in cursor.description]
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return results
        except Exception as e:
            logger.error(f"SQL查询执行失败: {str(e)}")
            raise ValidationError(f"查询执行失败: {str(e)}")

class InputValidator:
    """输入验证工具类"""
    
    # 常用验证器
    ALPHANUMERIC_VALIDATOR = RegexValidator(
        regex=r'^[a-zA-Z0-9_]+$',
        message='只允许字母、数字和下划线'
    )
    
    SAFE_STRING_VALIDATOR = RegexValidator(
        regex=r'^[\w\s\u4e00-\u9fa5\-_.()]+$',
        message='包含不允许的特殊字符'
    )
    
    URL_VALIDATOR = RegexValidator(
        regex=r'^https?://[\w\-.]+(:\d+)?(/[\w\-./?%&=]*)?$',
        message='URL格式不正确'
    )
    
    @classmethod
    def validate_provider_type(cls, value: str) -> str:
        """验证AI提供商类型"""
        allowed_types = [
            'openai', 'anthropic', 'google', 'azure', 'local',
            'openrouter', 'siliconflow', 'chenmoai', 'custom'
        ]
        
        if not value or value not in allowed_types:
            raise ValidationError(f"无效的提供商类型: {value}")
        
        return value
    
    @classmethod
    def validate_model_name(cls, value: str) -> str:
        """验证AI模型名称"""
        if not value or not isinstance(value, str):
            raise ValidationError("模型名称不能为空")
        
        # 移除前后空白
        value = value.strip()
        
        # 长度检查
        if len(value) < 1 or len(value) > 100:
            raise ValidationError("模型名称长度必须在1-100字符之间")
        
        # 字符检查（允许字母、数字、连字符、点号）
        if not re.match(r'^[a-zA-Z0-9\-_.]+$', value):
            raise ValidationError("模型名称只能包含字母、数字、连字符、下划线和点号")
        
        return value
    
    @classmethod
    def validate_api_endpoint(cls, value: str) -> str:
        """验证API端点URL"""
        if not value or not isinstance(value, str):
            raise ValidationError("API端点不能为空")
        
        # 移除前后空白
        value = value.strip()
        
        # 自动添加协议前缀
        if not value.startswith(('http://', 'https://')):
            value = f"https://{value}"
        
        # URL格式验证
        try:
            from urllib.parse import urlparse
            parsed = urlparse(value)
            if not parsed.netloc:
                raise ValidationError("URL格式不正确")
            if parsed.scheme not in ['http', 'https']:
                raise ValidationError("仅支持HTTP和HTTPS协议")
        except Exception:
            raise ValidationError("URL格式验证失败")
        
        return value
    
    @classmethod
    def validate_json_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """验证JSON配置参数"""
        if not isinstance(config, dict):
            raise ValidationError("配置必须是JSON对象")
        
        # 允许的配置键白名单
        allowed_keys = {
            'temperature', 'max_tokens', 'top_p', 'frequency_penalty',
            'presence_penalty', 'organization_id', 'deployment_name',
            'resource_name', 'model_path', 'device', 'timeout',
            'retry_count', 'rate_limit'
        }
        
        # 检查配置键
        for key in config.keys():
            if key not in allowed_keys:
                raise ValidationError(f"不允许的配置参数: {key}")
        
        # 验证数值范围
        if 'temperature' in config:
            temp = config['temperature']
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                raise ValidationError("temperature必须在0-2之间")
        
        if 'max_tokens' in config:
            tokens = config['max_tokens']
            if not isinstance(tokens, int) or tokens < 1 or tokens > 100000:
                raise ValidationError("max_tokens必须在1-100000之间")
        
        return config
    
    @classmethod
    def sanitize_search_query(cls, query: str) -> str:
        """清理搜索查询字符串"""
        if not query or not isinstance(query, str):
            return ""
        
        # 移除前后空白
        query = query.strip()
        
        # 长度限制
        if len(query) > 100:
            query = query[:100]
        
        # 移除危险字符
        query = re.sub(r'[<>"\';\\]', '', query)
        
        # 转义特殊字符
        query = escape(query)
        
        return query

class DatabaseSecurityMixin:
    """数据库安全混入类，用于ViewSet"""
    
    def validate_query_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证查询参数"""
        validated_params = {}
        
        for key, value in params.items():
            # 验证参数名
            if not re.match(r'^[a-z_]+$', key):
                logger.warning(f"可疑的参数名: {key}")
                continue
            
            # 验证参数值
            if isinstance(value, str):
                try:
                    validated_value = SQLSecurityUtils.validate_sql_input(value)
                    validated_params[key] = validated_value
                except ValidationError as e:
                    logger.warning(f"参数验证失败 {key}: {str(e)}")
                    continue
            else:
                validated_params[key] = value
        
        return validated_params
    
    def get_safe_queryset(self):
        """获取安全的查询集"""
        # 验证查询参数
        safe_params = self.validate_query_params(
            dict(self.request.query_params.items())
        )
        
        # 应用安全过滤
        queryset = super().get_queryset()
        
        # 基于验证后的参数进行过滤
        for key, value in safe_params.items():
            if hasattr(self.queryset.model, key):
                queryset = queryset.filter(**{key: value})
        
        return queryset

# 安全装饰器
def require_safe_sql(func):
    """装饰器：要求函数使用安全的SQL查询"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 记录潜在的SQL注入尝试
            logger.error(f"SQL查询异常，可能的注入攻击: {str(e)}")
            raise ValidationError("查询执行失败")
    return wrapper

# 常用验证器实例
PROVIDER_NAME_VALIDATOR = RegexValidator(
    regex=r'^[a-zA-Z0-9_\-]+$',
    message='提供商名称只能包含字母、数字、下划线和连字符'
)

MODEL_NAME_VALIDATOR = RegexValidator(
    regex=r'^[a-zA-Z0-9\-_.]+$',
    message='模型名称只能包含字母、数字、连字符、下划线和点号'
)

API_KEY_VALIDATOR = RegexValidator(
    regex=r'^[a-zA-Z0-9\-_.]+$',
    message='API密钥格式不正确'
)

def validate_database_identifier(identifier: str, identifier_type: str = "标识符") -> str:
    """验证数据库标识符（表名、列名等）"""
    if not identifier or not isinstance(identifier, str):
        raise ValidationError(f"{identifier_type}不能为空")
    
    # 移除前后空白
    identifier = identifier.strip()
    
    # 长度检查
    if len(identifier) > 64:  # MySQL标识符最大长度
        raise ValidationError(f"{identifier_type}长度不能超过64字符")
    
    # 字符检查（仅允许字母、数字、下划线）
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', identifier):
        raise ValidationError(f"{identifier_type}格式不正确，只能以字母开头，包含字母、数字和下划线")
    
    return identifier

def validate_limit_offset(limit: Union[str, int], offset: Union[str, int] = 0) -> tuple[int, int]:
    """验证分页参数"""
    try:
        limit = int(limit) if limit else 50
        offset = int(offset) if offset else 0
    except (ValueError, TypeError):
        raise ValidationError("分页参数必须是整数")
    
    # 限制范围
    if limit < 1 or limit > 1000:
        raise ValidationError("limit必须在1-1000之间")
    
    if offset < 0:
        raise ValidationError("offset不能为负数")
    
    return limit, offset

def escape_like_pattern(pattern: str) -> str:
    """转义LIKE模式中的特殊字符"""
    if not pattern:
        return ""
    
    # 转义LIKE特殊字符
    pattern = pattern.replace('\\', '\\\\')  # 反斜杠
    pattern = pattern.replace('%', '\\%')    # 百分号
    pattern = pattern.replace('_', '\\_')    # 下划线
    
    return pattern

class SecureQueryBuilder:
    """安全查询构建器"""
    
    def __init__(self, model_class):
        self.model_class = model_class
        self.queryset = model_class.objects.all()
    
    def filter_by_safe_params(self, **params) -> 'SecureQueryBuilder':
        """使用安全参数进行过滤"""
        safe_params = {}
        
        for key, value in params.items():
            # 验证字段名
            if not hasattr(self.model_class, key.split('__')[0]):
                logger.warning(f"模型 {self.model_class.__name__} 不存在字段: {key}")
                continue
            
            # 验证字段值
            if isinstance(value, str):
                try:
                    value = SQLSecurityUtils.validate_sql_input(value)
                except ValidationError:
                    logger.warning(f"字段值验证失败: {key}={value}")
                    continue
            
            safe_params[key] = value
        
        self.queryset = self.queryset.filter(**safe_params)
        return self
    
    def search_safe(self, query: str, fields: List[str]) -> 'SecureQueryBuilder':
        """安全的搜索功能"""
        if not query or not fields:
            return self
        
        # 清理搜索查询
        safe_query = InputValidator.sanitize_search_query(query)
        if not safe_query:
            return self
        
        # 验证搜索字段
        safe_fields = []
        for field in fields:
            field_name = field.split('__')[0]
            if hasattr(self.model_class, field_name):
                safe_fields.append(field)
        
        if not safe_fields:
            return self
        
        # 构建安全的搜索条件
        from django.db.models import Q
        search_q = Q()
        for field in safe_fields:
            search_q |= Q(**{f"{field}__icontains": safe_query})
        
        self.queryset = self.queryset.filter(search_q)
        return self
    
    def order_by_safe(self, *fields) -> 'SecureQueryBuilder':
        """安全的排序功能"""
        safe_fields = []
        
        for field in fields:
            # 处理降序标记
            desc = field.startswith('-')
            field_name = field[1:] if desc else field
            
            # 验证字段名
            if hasattr(self.model_class, field_name):
                safe_fields.append(field)
            else:
                logger.warning(f"排序字段不存在: {field_name}")
        
        if safe_fields:
            self.queryset = self.queryset.order_by(*safe_fields)
        
        return self
    
    def get_queryset(self):
        """获取最终查询集"""
        return self.queryset

# 安全查询装饰器
def secure_database_operation(func):
    """装饰器：确保数据库操作安全"""
    def wrapper(self, *args, **kwargs):
        try:
            # 记录操作日志
            logger.info(f"执行数据库操作: {func.__name__}")
            result = func(self, *args, **kwargs)
            return result
        except ValidationError:
            # 重新抛出验证错误
            raise
        except Exception as e:
            # 记录其他异常
            logger.error(f"数据库操作异常: {func.__name__} - {str(e)}")
            raise ValidationError("操作执行失败")
    return wrapper
