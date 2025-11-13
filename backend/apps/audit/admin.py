from django.contrib import admin
from .models import AuditLog, LocationSnapshot, Device


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['performed_by', 'action', 'target_table', 'target_id', 'performed_at']
    list_filter = ['action', 'target_table', 'performed_at']
    search_fields = ['performed_by__full_name', 'action', 'target_table']
    readonly_fields = ['performed_by', 'action', 'target_table', 'target_id', 'old_data', 'new_data', 'performed_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(LocationSnapshot)
class LocationSnapshotAdmin(admin.ModelAdmin):
    list_display = ['user', 'recorded_at', 'source', 'accuracy']
    list_filter = ['source', 'recorded_at']
    search_fields = ['user__full_name', 'user__email']
    readonly_fields = ['user', 'recorded_at', 'location', 'source', 'accuracy']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_id', 'last_seen', 'created_at']
    list_filter = ['last_seen', 'created_at']
    search_fields = ['user__full_name', 'device_id']
    readonly_fields = ['created_at', 'last_seen']
