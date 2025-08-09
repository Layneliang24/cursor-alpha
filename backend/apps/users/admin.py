from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile
from .forms import CustomUserCreationForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id', 'username', 'email', 'groups_list', 'permissions_brief',
        'is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'groups__name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    ordering = ('-date_joined',)
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name',
                       'is_active', 'is_staff', 'is_superuser', 'groups')
        }),
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'avatar', 'bio', 'website')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('groups', 'user_permissions')

    def groups_list(self, obj):
        names = list(obj.groups.values_list('name', flat=True))
        return ', '.join(names) if names else '-'
    groups_list.short_description = '所属组'

    def permissions_brief(self, obj):
        try:
            perms = sorted(list(obj.get_all_permissions()))
        except Exception:
            perms = []
        if not perms:
            return '-'
        if len(perms) <= 5:
            return ', '.join(perms)
        return f"{', '.join(perms[:5])} ...(+{len(perms)-5})"
    permissions_brief.short_description = '拥有权限'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'location', 'company', 'position', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone', 'company', 'position')
    autocomplete_fields = ('user',)
    ordering = ('-created_at',)
