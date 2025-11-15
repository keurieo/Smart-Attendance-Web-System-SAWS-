from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Institution, Role, User, TeacherProfile, StudentProfile


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ['name', 'timezone', 'user_count', 'created_at']
    search_fields = ['name']
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    def user_count(self, obj):
        """Display count of users in this institution."""
        count = obj.users.count()
        url = reverse('admin:accounts_user_changelist') + f'?institution__id__exact={obj.id}'
        return format_html('<a href="{}">{} users</a>', url, count)
    user_count.short_description = 'Users'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_display_name', 'user_count', 'created_at']
    list_per_page = 25
    
    def get_display_name(self, obj):
        """Display formatted role name."""
        return obj.get_name_display()
    get_display_name.short_description = 'Display Name'
    
    def user_count(self, obj):
        """Display count of users with this role."""
        count = obj.users.count()
        url = reverse('admin:accounts_user_changelist') + f'?role__id__exact={obj.id}'
        return format_html('<a href="{}">{} users</a>', url, count)
    user_count.short_description = 'Users'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'full_name', 'get_role_badge', 'institution', 'get_status', 'last_login', 'created_at']
    list_filter = ['role', 'institution', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'full_name']
    ordering = ['-created_at']
    list_per_page = 50
    date_hierarchy = 'created_at'
    actions = ['activate_users', 'deactivate_users']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'role', 'institution')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'role', 'institution', 'password1', 'password2', 'is_active'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    
    def get_role_badge(self, obj):
        """Display role as a colored badge."""
        colors = {
            'admin': '#dc2626',  # red
            'teacher': '#2563eb',  # blue
            'student': '#16a34a',  # green
        }
        color = colors.get(obj.role.name, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.role.get_name_display()
        )
    get_role_badge.short_description = 'Role'
    
    def get_status(self, obj):
        """Display active status as a colored indicator."""
        if obj.is_active:
            return format_html(
                '<span style="color: #16a34a; font-weight: bold;">● Active</span>'
            )
        return format_html(
            '<span style="color: #dc2626; font-weight: bold;">● Inactive</span>'
        )
    get_status.short_description = 'Status'
    
    def activate_users(self, request, queryset):
        """Bulk action to activate users."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated successfully.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Bulk action to deactivate users."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated successfully.')
    deactivate_users.short_description = 'Deactivate selected users'


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['get_user_link', 'employee_id', 'department_id', 'get_email', 'created_at']
    search_fields = ['employee_id', 'user__full_name', 'user__email']
    list_filter = ['department_id', 'created_at']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    def get_user_link(self, obj):
        """Display user as a clickable link."""
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.full_name)
    get_user_link.short_description = 'Teacher'
    
    def get_email(self, obj):
        """Display user email."""
        return obj.user.email
    get_email.short_description = 'Email'


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['get_user_link', 'roll_number', 'enrollment_year', 'department_id', 'get_email', 'created_at']
    search_fields = ['roll_number', 'user__full_name', 'user__email']
    list_filter = ['enrollment_year', 'department_id', 'created_at']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    def get_user_link(self, obj):
        """Display user as a clickable link."""
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.full_name)
    get_user_link.short_description = 'Student'
    
    def get_email(self, obj):
        """Display user email."""
        return obj.user.email
    get_email.short_description = 'Email'
