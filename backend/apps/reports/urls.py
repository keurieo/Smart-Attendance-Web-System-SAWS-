from django.urls import path
from .views import AttendanceReportView

urlpatterns = [
    # Teacher endpoints for reports
    path('teacher/reports/', AttendanceReportView.as_view(), name='teacher-attendance-report'),
]
