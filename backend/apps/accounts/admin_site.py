"""
Custom Django Admin Site Configuration
Provides enhanced branding and customization for the admin interface.
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import path
from django.template.response import TemplateResponse


class SmartAttendanceAdminSite(AdminSite):
    """Custom admin site with branding for Smart Attendance System."""
    
    site_header = 'Smart Attendance System'
    site_title = 'Smart Attendance Admin'
    index_title = 'Dashboard'
    site_url = None  # Disable "View site" link
    enable_nav_sidebar = False  # Disable default sidebar (we have custom one)
    
    def each_context(self, request):
        """Add custom context to all admin pages."""
        context = super().each_context(request)
        context.update({
            'site_header': self.site_header,
            'site_title': self.site_title,
            'index_title': self.index_title,
            'has_permission': request.user.is_active and request.user.is_staff,
            'available_apps': self.get_app_list(request),
        })
        return context
    
    def index(self, request, extra_context=None):
        """
        Display the main admin index page with custom dashboard.
        """
        app_list = self.get_app_list(request)
        
        context = {
            **self.each_context(request),
            'title': self.index_title,
            'subtitle': None,
            'app_list': app_list,
            **(extra_context or {}),
        }
        
        request.current_app = self.name
        
        return TemplateResponse(request, 'admin/index.html', context)
    
    def get_urls(self):
        """Add custom URLs for dashboard API endpoints."""
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/metrics/', self.admin_view(self.dashboard_metrics_view), name='dashboard_metrics'),
            path('dashboard/chart-data/', self.admin_view(self.chart_data_view), name='chart_data'),
            path('dashboard/heatmap-data/', self.admin_view(self.heatmap_data_view), name='heatmap_data'),
        ]
        return custom_urls + urls
    
    def dashboard_metrics_view(self, request):
        """API endpoint for dashboard metrics."""
        from django.http import JsonResponse
        from apps.accounts.dashboard_views import DashboardMetrics
        
        metrics = DashboardMetrics()
        data = {
            'total_users': metrics.get_total_users(),
            'active_sessions': metrics.get_active_sessions(),
            'attendance_rate': metrics.get_attendance_rate(),
            'total_courses': metrics.get_total_courses(),
        }
        
        return JsonResponse(data)
    
    def chart_data_view(self, request):
        """API endpoint for attendance trend chart data."""
        from django.http import JsonResponse
        from apps.accounts.dashboard_views import DashboardMetrics
        
        days = int(request.GET.get('days', 30))
        metrics = DashboardMetrics()
        data = metrics.get_attendance_trend_data(days=days)
        
        return JsonResponse({'data': data})
    
    def heatmap_data_view(self, request):
        """API endpoint for activity heatmap data."""
        from django.http import JsonResponse
        from apps.accounts.dashboard_views import DashboardMetrics
        
        metrics = DashboardMetrics()
        data = metrics.get_activity_heatmap_data()
        
        return JsonResponse({'data': data})


# Create custom admin site instance
admin_site = SmartAttendanceAdminSite(name='smart_attendance_admin')
