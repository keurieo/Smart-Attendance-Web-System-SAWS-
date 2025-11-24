"""
URL configuration for Smart Attendance System.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from apps.accounts.urls import admin_urlpatterns as accounts_admin_urls

# Customize admin site
admin.site.site_header = getattr(settings, 'ADMIN_SITE_HEADER', 'Smart Attendance System')
admin.site.site_title = getattr(settings, 'ADMIN_SITE_TITLE', 'Smart Attendance Admin')
admin.site.index_title = getattr(settings, 'ADMIN_INDEX_TITLE', 'Administration Dashboard')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JWT Authentication - token refresh endpoint
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # App URLs
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/', include('apps.academics.urls')),  # Includes teacher/ and admin/ prefixes
    path('api/', include('apps.attendance.urls')),  # Includes teacher/, student/, admin/ prefixes
    path('api/', include('apps.reports.urls')),  # Includes teacher/ prefix
    path('api/admin/', include(accounts_admin_urls)),  # Admin user management
    path('api/admin/', include('apps.audit.urls')),  # Admin audit logs
]

if settings.DEBUG:
    from django.conf.urls.static import static
    
    # Serve static files in development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar (if installed)
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        # Debug toolbar not installed (e.g., in Docker with production requirements)
        pass
