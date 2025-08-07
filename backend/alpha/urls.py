"""
URL configuration for alpha project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
def api_root(request):
    """API根路径 - 显示可用的API端点"""
    api_endpoints = {
        'message': 'Alpha 技术共享平台 API',
        'version': '1.0.0',
        'endpoints': {
            'test': '/api/test/',
            'admin': '/admin/',
            'swagger': '/api/swagger/',
        },
        'status': 'running'
    }
    return Response(api_endpoints)


@api_view(['GET'])
def test_api(request):
    """测试API端点"""
    return Response({
        'message': 'API测试成功！',
        'timestamp': '2024-01-15',
        'status': 'ok'
    })


def home_view(request):
    """首页视图 - 提供HTML页面"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Alpha 技术共享平台</title>
        <style>
            body {
                font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 600px;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            .links {
                display: flex;
                flex-direction: column;
                gap: 15px;
                margin-top: 30px;
            }
            .link {
                display: inline-block;
                padding: 12px 24px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background 0.3s;
            }
            .link:hover {
                background: #5a6fd8;
            }
            .description {
                color: #666;
                line-height: 1.6;
                margin-bottom: 20px;
            }
            .status {
                background: #67C23A;
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                display: inline-block;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status">✅ 系统运行正常</div>
            <h1>🎉 Alpha 技术共享平台</h1>
            <p class="description">
                欢迎使用Alpha技术共享平台！这是一个前后端分离的技术文章分享网站，
                使用Django + Vue.js构建，提供文章分享、用户认证、分类管理等功能。
            </p>
            <div class="links">
                <a href="/api/" class="link">🔧 API接口</a>
                <a href="/api/test/" class="link">🧪 测试接口</a>
                <a href="/admin/" class="link">⚙️ 管理员后台</a>
                <a href="/api/swagger/" class="link">📚 API文档</a>
            </div>
        </div>
    </body>
    </html>
    """
    from django.http import HttpResponse
    return HttpResponse(html_content, content_type='text/html; charset=utf-8')


urlpatterns = [
    path('', home_view),  # 首页
    path('api/', api_root),  # API根路径
    path('api/test/', test_api),  # 测试API
    path('api/v1/', include('apps.api.urls')),  # API v1
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:  # 添加媒体文件url,生产环境下使用
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
