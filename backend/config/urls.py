"""
URL configuration for Smart Attendance System.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JWT Authentication
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # App URLs
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/academics/', include('apps.academics.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/admin/', include('apps.audit.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
