from django.urls import path
from .views import AuditLogListView
from .health import health_check, readiness_check, liveness_check

urlpatterns = [
    # Audit log endpoint
    path('audit/', AuditLogListView.as_view(), name='audit-log-list'),
    # Health check endpoints
    path('health/', health_check, name='health-check'),
    path('health/ready/', readiness_check, name='readiness-check'),
    path('health/live/', liveness_check, name='liveness-check'),
]
