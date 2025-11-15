from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AttendanceSessionViewSet, 
    AttendanceMarkingView, 
    AttendanceOverrideView,
    StudentAttendanceHistoryView
)

router = DefaultRouter()

urlpatterns = [
    # Teacher endpoints for session management
    path('teacher/sessions/', AttendanceSessionViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='teacher-session-list'),
    path('teacher/sessions/<int:pk>/', AttendanceSessionViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='teacher-session-detail'),
    
    # Student endpoints for attendance marking and history
    path('student/attendance/scan/', AttendanceMarkingView.as_view(), name='student-attendance-scan'),
    path('student/attendance/', StudentAttendanceHistoryView.as_view(), name='student-attendance-history'),
    
    # Admin endpoints for attendance override
    path('admin/attendance/<int:record_id>/', AttendanceOverrideView.as_view(), name='admin-attendance-override'),
]
