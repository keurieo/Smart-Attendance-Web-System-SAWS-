from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.accounts.permissions import IsTeacher
from .models import Course, Schedule
from .serializers import CourseSerializer, ScheduleSerializer


class TeacherCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for teachers to view their assigned courses."""
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = CourseSerializer
    
    def get_queryset(self):
        """
        Get courses where the authenticated user is the instructor.
        """
        return Course.objects.filter(
            instructor=self.request.user,
            institution=self.request.user.institution
        ).select_related('institution', 'instructor').order_by('code')


class TeacherScheduleViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for teachers to view schedules for their courses."""
    permission_classes = [IsAuthenticated, IsTeacher]
    serializer_class = ScheduleSerializer
    
    def get_queryset(self):
        """
        Get schedules for courses where the authenticated user is the instructor.
        """
        queryset = Schedule.objects.filter(
            course__instructor=self.request.user,
            course__institution=self.request.user.institution
        ).select_related('course', 'course__instructor')
        
        # Filter by course if provided
        course_id = self.request.query_params.get('course_id', None)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        return queryset.order_by('weekday', 'start_time')
