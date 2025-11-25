from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import AttendanceSession, QRToken, AttendanceRecord


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['get_course_link', 'created_by', 'start_at', 'end_at', 'radius_meters', 'get_status_badge', 'attendance_count', 'created_at']
    list_filter = ['status', 'course__institution', 'created_at']
    search_fields = ['course__code', 'course__title', 'created_by__full_name']
    readonly_fields = ['created_at', 'updated_at', 'get_qr_code_display']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Session Info', {
            'fields': ('course', 'created_by', 'start_at', 'end_at', 'status')
        }),
        ('Location Settings', {
            'fields': ('teacher_location', 'radius_meters')
        }),
        ('QR Code', {
            'fields': ('get_qr_code_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_course_link(self, obj):
        """Display course as a clickable link."""
        return format_html(
            '<strong>{}</strong><br><small style="color: #6b7280;">{}</small>',
            obj.course.code,
            obj.course.title
        )
    get_course_link.short_description = 'Course'
    
    def get_status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'active': '#16a34a',  # green
            'expired': '#dc2626',  # red
            'cancelled': '#6b7280',  # gray
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            color,
            obj.status
        )
    get_status_badge.short_description = 'Status'
    
    def attendance_count(self, obj):
        """Display count of attendance records."""
        count = obj.attendance_records.count()
        url = reverse('admin:attendance_attendancerecord_changelist') + f'?session__id__exact={obj.id}'
        return format_html('<a href="{}">{} records</a>', url, count)
    attendance_count.short_description = 'Attendance'
    
    def get_qr_code_display(self, obj):
        """Display QR code information."""
        try:
            token = obj.qr_tokens.latest('created_at')
            return format_html(
                '<div style="padding: 10px; background: #f3f4f6; border-radius: 5px;">'
                '<strong>6-Digit Code:</strong> <code style="font-size: 18px; color: #2563eb;">{}</code><br>'
                '<strong>Expires:</strong> {}<br>'
                '<strong>Revoked:</strong> {}'
                '</div>',
                token.code6,
                token.expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                '✓ Yes' if token.is_revoked else '✗ No'
            )
        except QRToken.DoesNotExist:
            return format_html('<em style="color: #6b7280;">No QR token generated</em>')
    get_qr_code_display.short_description = 'QR Code Info'


@admin.register(QRToken)
class QRTokenAdmin(admin.ModelAdmin):
    list_display = ['get_session_link', 'code6', 'created_at', 'expires_at', 'get_revoked_status']
    list_filter = ['is_revoked', 'created_at', 'expires_at']
    search_fields = ['code6', 'session__course__code']
    readonly_fields = ['created_at', 'token', 'code6']
    list_per_page = 50
    date_hierarchy = 'created_at'
    
    def get_session_link(self, obj):
        """Display session as a clickable link."""
        url = reverse('admin:attendance_attendancesession_change', args=[obj.session.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            f"{obj.session.course.code} - {obj.session.start_at.strftime('%Y-%m-%d %H:%M')}"
        )
    get_session_link.short_description = 'Session'
    
    def get_revoked_status(self, obj):
        """Display revoked status with color."""
        if obj.is_revoked:
            return format_html('<span style="color: #dc2626; font-weight: bold;">✓ Revoked</span>')
        return format_html('<span style="color: #16a34a; font-weight: bold;">✓ Active</span>')
    get_revoked_status.short_description = 'Status'


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['get_student_link', 'get_session_link', 'get_status_badge', 'method', 'distance_meters', 'get_flagged', 'marked_at']
    list_filter = ['status', 'method', 'flagged_for_review', 'marked_at']
    search_fields = ['student__full_name', 'student__email', 'session__course__code']
    readonly_fields = ['marked_at', 'updated_at']
    list_per_page = 50
    date_hierarchy = 'marked_at'
    actions = ['flag_for_review', 'unflag_records']
    
    fieldsets = (
        ('Attendance Info', {
            'fields': ('student', 'session', 'status', 'method')
        }),
        ('Location Data', {
            'fields': ('distance_meters', 'flagged_for_review'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('marked_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_student_link(self, obj):
        """Display student as a clickable link."""
        url = reverse('admin:accounts_user_change', args=[obj.student.id])
        return format_html('<a href="{}">{}</a>', url, obj.student.full_name)
    get_student_link.short_description = 'Student'
    
    def get_session_link(self, obj):
        """Display session as a clickable link."""
        url = reverse('admin:attendance_attendancesession_change', args=[obj.session.id])
        return format_html(
            '<a href="{}">{}</a><br><small style="color: #6b7280;">{}</small>',
            url,
            obj.session.course.code,
            obj.session.start_at.strftime('%Y-%m-%d %H:%M')
        )
    get_session_link.short_description = 'Session'
    
    def get_status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            'present': '#16a34a',  # green
            'absent': '#dc2626',  # red
            'late': '#f59e0b',  # amber
            'excused': '#2563eb',  # blue
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold; text-transform: uppercase;">{}</span>',
            color,
            obj.status
        )
    get_status_badge.short_description = 'Status'
    
    def get_flagged(self, obj):
        """Display flagged status."""
        if obj.flagged_for_review:
            return format_html('<span style="color: #dc2626; font-weight: bold;">⚠ Flagged</span>')
        return format_html('<span style="color: #6b7280;">—</span>')
    get_flagged.short_description = 'Review'
    
    def flag_for_review(self, request, queryset):
        """Bulk action to flag records for review."""
        updated = queryset.update(flagged_for_review=True)
        self.message_user(request, f'{updated} record(s) flagged for review.')
    flag_for_review.short_description = 'Flag selected records for review'
    
    def unflag_records(self, request, queryset):
        """Bulk action to unflag records."""
        updated = queryset.update(flagged_for_review=False)
        self.message_user(request, f'{updated} record(s) unflagged.')
    unflag_records.short_description = 'Remove review flag from selected records'
