from django.contrib import admin
from .models import AttendanceSession, QRToken, AttendanceRecord


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['course', 'created_by', 'start_at', 'end_at', 'radius_meters', 'status', 'created_at']
    list_filter = ['status', 'course', 'created_at']
    search_fields = ['course__code', 'created_by__full_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(QRToken)
class QRTokenAdmin(admin.ModelAdmin):
    list_display = ['session', 'code6', 'created_at', 'expires_at', 'is_revoked']
    list_filter = ['is_revoked', 'created_at']
    search_fields = ['code6', 'token']
    readonly_fields = ['created_at']


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'status', 'method', 'distance_meters', 'marked_at', 'flagged_for_review']
    list_filter = ['status', 'method', 'flagged_for_review', 'marked_at']
    search_fields = ['student__full_name', 'student__email', 'session__course__code']
    readonly_fields = ['marked_at', 'updated_at']
