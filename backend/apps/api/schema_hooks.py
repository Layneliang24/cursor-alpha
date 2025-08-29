# -*- coding: utf-8 -*-
"""
drf-spectacular schema hooks for API documentation enhancement
"""
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import extend_schema_view
from django.conf import settings


def preprocess_exclude_paths(result, generator, request, public):
    """
    预处理钩子：排除不需要在API文档中显示的路径
    """
    # 排除管理员接口和内部接口
    excluded_paths = [
        '/admin/',
        '/api/v1/internal/',
        '/api/v1/debug/',
    ]
    
    # 如果不是调试模式，排除调试相关接口
    if not settings.DEBUG:
        excluded_paths.extend([
            '/api/v1/test/',
            '/api/v1/mock/',
        ])
    
    # 过滤掉排除的路径
    filtered_paths = {}
    for path, path_info in result.get('paths', {}).items():
        if not any(excluded in path for excluded in excluded_paths):
            filtered_paths[path] = path_info
    
    result['paths'] = filtered_paths
    return result


def postprocess_schema_enhancements(result, generator, request, public):
    """
    后处理钩子：增强API文档的元数据和示例
    """
    # 添加API信息
    result['info'].update({
        'contact': {
            'name': 'API Support',
            'email': 'support@idiomaticexpressions.com',
            'url': 'https://github.com/your-repo/idiomatic-expressions'
        },
        'license': {
            'name': 'MIT',
            'url': 'https://opensource.org/licenses/MIT'
        },
        'termsOfService': 'https://idiomaticexpressions.com/terms/',
        'x-logo': {
            'url': '/static/images/api-logo.png',
            'altText': '地道表达学习平台'
        }
    })
    
    # 添加服务器信息
    if not result.get('servers'):
        result['servers'] = []
    
    if settings.DEBUG:
        result['servers'].append({
            'url': 'http://localhost:8000',
            'description': '开发环境'
        })
    else:
        result['servers'].extend([
            {
                'url': 'https://api.idiomaticexpressions.com',
                'description': '生产环境'
            },
            {
                'url': 'https://staging-api.idiomaticexpressions.com',
                'description': '测试环境'
            }
        ])
    
    # 添加安全方案
    result['components'] = result.get('components', {})
    result['components']['securitySchemes'] = {
        'BearerAuth': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'JWT认证令牌'
        },
        'ApiKeyAuth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key',
            'description': 'API密钥认证'
        },
        'SessionAuth': {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'sessionid',
            'description': 'Django会话认证'
        }
    }
    
    # 添加全局安全要求
    result['security'] = [
        {'BearerAuth': []},
        {'ApiKeyAuth': []},
        {'SessionAuth': []}
    ]
    
    # 为地道表达相关的接口添加示例
    expressions_examples = {
        'IdiomaticExpression': {
            'summary': '地道表达示例',
            'value': {
                'id': 1,
                'expression': 'break the ice',
                'meaning': '打破沉默，缓解尴尬气氛',
                'cultural_background': '这个表达来源于船只破冰前行的比喻',
                'difficulty_level': 'intermediate',
                'tags': ['社交', '商务'],
                'scenarios': [
                    {
                        'context': 'Business Meeting',
                        'example_sentence': 'Let me break the ice with a quick introduction.',
                        'situation_description': '商务会议开场'
                    }
                ],
                'created_at': '2024-01-15T10:30:00Z',
                'updated_at': '2024-01-15T10:30:00Z'
            }
        },
        'UserProgress': {
            'summary': '用户学习进度示例',
            'value': {
                'id': 1,
                'user': 1,
                'expression': 1,
                'mastery_level': 3,
                'learned_at': '2024-01-15T10:30:00Z',
                'last_reviewed': '2024-01-20T14:20:00Z',
                'review_count': 5,
                'correct_count': 4,
                'notes': '需要在商务场景中多练习'
            }
        }
    }
    
    # 将示例添加到components中
    if 'examples' not in result['components']:
        result['components']['examples'] = {}
    result['components']['examples'].update(expressions_examples)
    
    return result
