from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AdminCourseViewSet, AdminEnrollmentViewSet, AdminScheduleViewSet
from .teacher_views import TeacherCourseViewSet, TeacherScheduleViewSet

# Create router for admin endpoints
router = DefaultRouter()

urlpatterns = [
    # Teacher endpoints
    path('teacher/courses/', TeacherCourseViewSet.as_view({
        'get': 'list'
    }), name='teacher-course-list'),
    path('teacher/courses/<int:pk>/', TeacherCourseViewSet.as_view({
        'get': 'retrieve'
    }), name='teacher-course-detail'),
    path('teacher/schedules/', TeacherScheduleViewSet.as_view({
        'get': 'list'
    }), name='teacher-schedule-list'),
    path('teacher/schedules/<int:pk>/', TeacherScheduleViewSet.as_view({
        'get': 'retrieve'
    }), name='teacher-schedule-detail'),
    
    # Admin course management endpoints
    path('admin/courses/', AdminCourseViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='admin-course-list'),
    path('admin/courses/<int:pk>/', AdminCourseViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='admin-course-detail'),
    
    # Admin enrollment management endpoints
    path('admin/enrollments/', AdminEnrollmentViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='admin-enrollment-list'),
    path('admin/enrollments/<int:pk>/', AdminEnrollmentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='admin-enrollment-detail'),
    
    # Admin schedule management endpoints
    path('admin/schedules/', AdminScheduleViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='admin-schedule-list'),
    path('admin/schedules/<int:pk>/', AdminScheduleViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='admin-schedule-detail'),
]
