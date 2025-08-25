from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeatureFlagViewSet, FeatureFlagPublicViewSet

# 创建路由器
router = DefaultRouter()
router.register(r'flags', FeatureFlagViewSet, basename='featureflag')
router.register(r'public', FeatureFlagPublicViewSet, basename='featureflag-public')

app_name = 'feature_flags'

urlpatterns = [
    # API路由
    path('', include(router.urls)),
    
    # 额外的便捷端点
    path('check/<str:key>/', 
         FeatureFlagPublicViewSet.as_view({'get': 'enabled'}), 
         name='check-flag'),
    
    path('batch-check/', 
         FeatureFlagPublicViewSet.as_view({'post': 'batch_check'}), 
         name='batch-check'),
    
    # 用户特性开关端点
    path('user-flags/', 
         FeatureFlagPublicViewSet.as_view({'get': 'list'}), 
         name='user-flags'),
]

# URL模式说明：
# 
# 管理API (需要管理员权限):
# - GET    /api/flags/                    # 获取特性开关列表
# - POST   /api/flags/                    # 创建特性开关
# - GET    /api/flags/{key}/              # 获取特定特性开关详情
# - PUT    /api/flags/{key}/              # 更新特性开关
# - PATCH  /api/flags/{key}/              # 部分更新特性开关
# - DELETE /api/flags/{key}/              # 删除特性开关
# - GET    /api/flags/{key}/check/        # 检查特性开关状态
# - POST   /api/flags/{key}/check/        # 检查特性开关状态（带上下文）
# - GET    /api/flags/check_all/          # 获取所有特性开关状态
# - POST   /api/flags/check_all/          # 获取所有特性开关状态（带上下文）
# - POST   /api/flags/{key}/toggle/       # 快速启用/禁用特性开关
# - POST   /api/flags/{key}/rollout/      # 灰度发布控制
# - GET    /api/flags/{key}/stats/        # 获取使用统计
# - GET    /api/flags/{key}/history/      # 获取变更历史
# - GET    /api/flags/{key}/usage/        # 获取使用记录
#
# 公共API (只读，普通用户权限):
# - GET    /api/public/                   # 获取活跃特性开关列表
# - GET    /api/public/{key}/             # 获取特定特性开关详情
# - GET    /api/public/{key}/enabled/     # 检查特性开关是否启用
# - POST   /api/public/batch_check/       # 批量检查特性开关
#
# 便捷端点:
# - GET    /api/check/{key}/              # 快速检查特性开关
# - POST   /api/batch-check/              # 批量检查特性开关