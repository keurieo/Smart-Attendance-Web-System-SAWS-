from django.urls import path
from .views import AttendanceReportView

urlpatterns = [
    path('attendance/', AttendanceReportView.as_view(), name='attendance-report'),
]
