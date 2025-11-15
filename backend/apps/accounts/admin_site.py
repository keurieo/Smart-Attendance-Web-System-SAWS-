"""
Custom Django Admin Site Configuration
Provides enhanced branding and customization for the admin interface.
"""
from django.contrib import admin
from django.contrib.admin import AdminSite


class SmartAttendanceAdminSite(AdminSite):
    """Custom admin site with branding for Smart Attendance System."""
    
    site_header = 'Smart Attendance System Administration'
    site_title = 'Smart Attendance Admin'
    index_title = 'Dashboard'
    site_url = '/admin/'
    enable_nav_sidebar = True
    
    def each_context(self, request):
        """Add custom context to all admin pages."""
        context = super().each_context(request)
        context.update({
            'site_header': self.site_header,
            'site_title': self.site_title,
            'index_title': self.index_title,
            'has_permission': request.user.is_active and request.user.is_staff,
        })
        return context


# Create custom admin site instance
admin_site = SmartAttendanceAdminSite(name='smart_attendance_admin')
