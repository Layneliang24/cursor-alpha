from django.contrib import admin
from .models import ExternalLink


@admin.register(ExternalLink)
class ExternalLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'link_type', 'is_active', 'order', 'created_by', 'created_at')
    list_filter = ('link_type', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'url')
    list_editable = ('is_active', 'order')
    ordering = ('order', '-created_at')
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新建时设置创建者
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

