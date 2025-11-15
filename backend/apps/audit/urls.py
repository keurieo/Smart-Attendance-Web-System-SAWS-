from django.urls import path
from apps.attendance.views import AttendanceOverrideView
from .views import AuditLogListView
from .health import health_check, readiness_check, liveness_check

urlpatterns = [
    # Audit log endpoint
    path('audit/', AuditLogListView.as_view(), name='audit-log-list'),
    # Attendance override endpoint
    path('attendance/<int:record_id>/', AttendanceOverrideView.as_view(), name='attendance-override'),
    # Health check endpoints
    path('health/', health_check, name='health-check'),
    path('health/ready/', readiness_check, name='readiness-check'),
    path('health/live/', liveness_check, name='liveness-check'),
]
