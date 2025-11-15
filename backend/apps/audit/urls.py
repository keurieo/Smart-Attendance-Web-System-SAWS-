from django.urls import path
from apps.attendance.views import AttendanceOverrideView
from .views import AuditLogListView

urlpatterns = [
    # Audit log endpoint
    path('audit/', AuditLogListView.as_view(), name='audit-log-list'),
    # Attendance override endpoint
    path('attendance/<int:record_id>/', AttendanceOverrideView.as_view(), name='attendance-override'),
]
