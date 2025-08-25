from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import FeatureFlag, FeatureFlagHistory, FeatureFlagUsage
from .services import feature_flag_service


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    """特性开关管理界面"""
    
    list_display = [
        'name', 'key', 'status_badge', 'target_type', 'rollout_percentage',
        'is_active_badge', 'created_by', 'updated_at', 'action_buttons'
    ]
    list_filter = [
        'status', 'target_type', 'created_at', 'updated_at', 'environments'
    ]
    search_fields = ['name', 'key', 'description']
    readonly_fields = [
        'created_by', 'updated_by', 'created_at', 'updated_at', 'version',
        'is_active_display', 'usage_stats_display'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'key', 'description')
        }),
        ('状态配置', {
            'fields': ('status', 'target_type', 'rollout_percentage')
        }),
        ('目标配置', {
            'fields': ('target_users', 'user_attributes', 'environments'),
            'classes': ('collapse',)
        }),
        ('特性值', {
            'fields': ('value',)
        }),
        ('时间控制', {
            'fields': ('start_time', 'end_time'),
            'classes': ('collapse',)
        }),
        ('元数据', {
            'fields': (
                'created_by', 'updated_by', 'created_at', 'updated_at', 
                'version', 'is_active_display', 'usage_stats_display'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = ['enable_flags', 'disable_flags', 'set_rollout_10', 'set_rollout_50', 'set_rollout_100']
    
    def status_badge(self, obj):
        """状态徽章"""
        colors = {
            'enabled': 'green',
            'disabled': 'red',
            'rollout': 'orange',
            'deprecated': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = '状态'
    
    def is_active_badge(self, obj):
        """活跃状态徽章"""
        is_active = obj.is_active()
        color = 'green' if is_active else 'red'
        text = '活跃' if is_active else '非活跃'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            text
        )
    is_active_badge.short_description = '活跃状态'
    
    def is_active_display(self, obj):
        """活跃状态显示"""
        return obj.is_active()
    is_active_display.short_description = '是否活跃'
    is_active_display.boolean = True
    
    def usage_stats_display(self, obj):
        """使用统计显示"""
        stats = feature_flag_service.get_usage_stats(obj.key, 7)
        if stats:
            return format_html(
                '7天内: {} 次请求, {} 次启用 ({:.1f}%), {} 个用户',
                stats['total_requests'],
                stats['enabled_requests'],
                stats['enabled_percentage'],
                stats['unique_users']
            )
        return '暂无数据'
    usage_stats_display.short_description = '使用统计'
    
    def action_buttons(self, obj):
        """操作按钮"""
        buttons = []
        
        # 切换状态按钮
        if obj.status == FeatureFlag.Status.DISABLED:
            buttons.append(
                f'<a href="#" onclick="toggleFlag(\'{obj.key}\', \'enable\')" '
                f'style="color: green; text-decoration: none;">启用</a>'
            )
        else:
            buttons.append(
                f'<a href="#" onclick="toggleFlag(\'{obj.key}\', \'disable\')" '
                f'style="color: red; text-decoration: none;">禁用</a>'
            )
        
        # 统计链接
        buttons.append(
            f'<a href="{reverse("admin:feature_flags_featureflagusage_changelist")}?feature_flag__key={obj.key}" '
            f'style="color: blue; text-decoration: none;">使用记录</a>'
        )
        
        # 历史链接
        buttons.append(
            f'<a href="{reverse("admin:feature_flags_featureflaghistory_changelist")}?feature_flag__key={obj.key}" '
            f'style="color: purple; text-decoration: none;">变更历史</a>'
        )
        
        return format_html(' | '.join(buttons))
    action_buttons.short_description = '操作'
    
    def save_model(self, request, obj, form, change):
        """保存模型时记录操作者"""
        if not change:  # 新建
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    # 批量操作
    def enable_flags(self, request, queryset):
        """批量启用特性开关"""
        count = 0
        for flag in queryset:
            success = feature_flag_service.update_flag(
                flag.key,
                {'status': FeatureFlag.Status.ENABLED},
                request.user,
                '管理员批量启用'
            )
            if success:
                count += 1
        
        self.message_user(request, f'成功启用 {count} 个特性开关')
    enable_flags.short_description = '启用选中的特性开关'
    
    def disable_flags(self, request, queryset):
        """批量禁用特性开关"""
        count = 0
        for flag in queryset:
            success = feature_flag_service.update_flag(
                flag.key,
                {'status': FeatureFlag.Status.DISABLED},
                request.user,
                '管理员批量禁用'
            )
            if success:
                count += 1
        
        self.message_user(request, f'成功禁用 {count} 个特性开关')
    disable_flags.short_description = '禁用选中的特性开关'
    
    def set_rollout_10(self, request, queryset):
        """设置10%灰度"""
        self._set_rollout(request, queryset, 10)
    set_rollout_10.short_description = '设置为10%灰度发布'
    
    def set_rollout_50(self, request, queryset):
        """设置50%灰度"""
        self._set_rollout(request, queryset, 50)
    set_rollout_50.short_description = '设置为50%灰度发布'
    
    def set_rollout_100(self, request, queryset):
        """设置100%灰度（全量发布）"""
        self._set_rollout(request, queryset, 100)
    set_rollout_100.short_description = '设置为100%灰度发布（全量）'
    
    def _set_rollout(self, request, queryset, percentage):
        """设置灰度百分比"""
        count = 0
        for flag in queryset:
            success = feature_flag_service.update_flag(
                flag.key,
                {
                    'status': FeatureFlag.Status.ROLLOUT,
                    'target_type': FeatureFlag.TargetType.PERCENTAGE,
                    'rollout_percentage': percentage
                },
                request.user,
                f'管理员批量设置{percentage}%灰度'
            )
            if success:
                count += 1
        
        self.message_user(request, f'成功设置 {count} 个特性开关为{percentage}%灰度发布')
    
    class Media:
        js = ('admin/js/feature_flags.js',)


@admin.register(FeatureFlagHistory)
class FeatureFlagHistoryAdmin(admin.ModelAdmin):
    """特性开关历史管理界面"""
    
    list_display = [
        'feature_flag_link', 'action', 'changed_by', 'changed_at', 
        'environment', 'reason_short'
    ]
    list_filter = [
        'action', 'changed_at', 'environment', 'feature_flag__status'
    ]
    search_fields = [
        'feature_flag__name', 'feature_flag__key', 'reason', 'changed_by__username'
    ]
    readonly_fields = [
        'feature_flag', 'action', 'old_value', 'new_value', 'reason',
        'changed_by', 'changed_at', 'environment', 'ip_address', 'user_agent'
    ]
    
    date_hierarchy = 'changed_at'
    ordering = ['-changed_at']
    
    def feature_flag_link(self, obj):
        """特性开关链接"""
        url = reverse('admin:feature_flags_featureflag_change', args=[obj.feature_flag.id])
        return format_html(
            '<a href="{}">{} ({})</a>',
            url,
            obj.feature_flag.name,
            obj.feature_flag.key
        )
    feature_flag_link.short_description = '特性开关'
    
    def reason_short(self, obj):
        """简短原因"""
        if len(obj.reason) > 50:
            return obj.reason[:50] + '...'
        return obj.reason
    reason_short.short_description = '变更原因'
    
    def has_add_permission(self, request):
        """禁止手动添加历史记录"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改历史记录"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """禁止删除历史记录"""
        return False


@admin.register(FeatureFlagUsage)
class FeatureFlagUsageAdmin(admin.ModelAdmin):
    """特性开关使用记录管理界面"""
    
    list_display = [
        'feature_flag_link', 'user_link', 'is_enabled_badge', 
        'accessed_at', 'environment', 'session_id_short'
    ]
    list_filter = [
        'is_enabled', 'accessed_at', 'environment', 'feature_flag__status'
    ]
    search_fields = [
        'feature_flag__name', 'feature_flag__key', 'user__username', 
        'session_id', 'ip_address'
    ]
    readonly_fields = [
        'feature_flag', 'user', 'session_id', 'is_enabled', 'value_returned',
        'context', 'environment', 'accessed_at', 'ip_address', 'user_agent'
    ]
    
    date_hierarchy = 'accessed_at'
    ordering = ['-accessed_at']
    
    def feature_flag_link(self, obj):
        """特性开关链接"""
        url = reverse('admin:feature_flags_featureflag_change', args=[obj.feature_flag.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.feature_flag.key
        )
    feature_flag_link.short_description = '特性开关'
    
    def user_link(self, obj):
        """用户链接"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.user.username
            )
        return '匿名用户'
    user_link.short_description = '用户'
    
    def is_enabled_badge(self, obj):
        """启用状态徽章"""
        color = 'green' if obj.is_enabled else 'red'
        text = '启用' if obj.is_enabled else '禁用'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            text
        )
    is_enabled_badge.short_description = '状态'
    
    def session_id_short(self, obj):
        """简短会话ID"""
        if obj.session_id and len(obj.session_id) > 10:
            return obj.session_id[:10] + '...'
        return obj.session_id or '-'
    session_id_short.short_description = '会话ID'
    
    def has_add_permission(self, request):
        """禁止手动添加使用记录"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """禁止修改使用记录"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """允许删除旧的使用记录"""
        return request.user.is_superuser


# 自定义管理站点标题
admin.site.site_header = 'Alpha 特性开关管理'
admin.site.site_title = 'Alpha 管理'
admin.site.index_title = '特性开关管理系统'