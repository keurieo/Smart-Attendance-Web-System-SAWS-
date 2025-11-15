from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from apps.accounts.permissions import IsAdmin
from apps.audit.models import AuditLog
from .models import Course, Enrollment, Schedule
from .serializers import CourseSerializer, EnrollmentSerializer, ScheduleSerializer


def create_audit_log(performed_by, action, target_table, target_id, old_data=None, new_data=None):
    """
    Utility function to create audit log entries.
    
    Args:
        performed_by: User who performed the action
        action: Description of the action
        target_table: Name of the table affected
        target_id: ID of the affected record
        old_data: Dictionary of old values (for updates/deletes)
        new_data: Dictionary of new values (for creates/updates)
    """
    AuditLog.objects.create(
        performed_by=performed_by,
        action=action,
        target_table=target_table,
        target_id=target_id,
        old_data=old_data,
        new_data=new_data
    )


class StandardPagination(PageNumberPagination):
    """Standard pagination class."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminCourseViewSet(viewsets.ModelViewSet):
    """ViewSet for admin course management operations."""
    permission_classes = [IsAdmin]
    serializer_class = CourseSerializer
    pagination_class = StandardPagination
    
    def get_queryset(self):
        """
        Get courses filtered by institution.
        Ensure data isolation by filtering to admin's institution.
        """
        queryset = Course.objects.filter(
            institution=self.request.user.institution
        ).select_related('institution', 'instructor', 'instructor__role')
        
        # Filter by instructor if provided
        instructor_id = self.request.query_params.get('instructor_id', None)
        if instructor_id:
            queryset = queryset.filter(instructor_id=instructor_id)
        
        # Filter by department if provided
        department_id = self.request.query_params.get('department_id', None)
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Create a new course."""
        # Add the admin's institution to the request data if not provided
        data = request.data.copy()
        if 'institution_id' not in data:
            data['institution_id'] = request.user.institution.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        
        # Create audit log for course creation
        create_audit_log(
            performed_by=request.user,
            action='course_created',
            target_table='courses',
            target_id=course.id,
            new_data={
                'code': course.code,
                'title': course.title,
                'department_id': course.department_id,
                'instructor_id': course.instructor.id,
                'institution_id': course.institution.id
            }
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update a course."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Store old data for audit log
        old_data = {
            'code': instance.code,
            'title': instance.title,
            'department_id': instance.department_id,
            'instructor_id': instance.instructor.id
        }
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        
        # Store new data for audit log
        new_data = {
            'code': course.code,
            'title': course.title,
            'department_id': course.department_id,
            'instructor_id': course.instructor.id
        }
        
        # Create audit log for course update
        create_audit_log(
            performed_by=request.user,
            action='course_updated',
            target_table='courses',
            target_id=course.id,
            old_data=old_data,
            new_data=new_data
        )
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a course."""
        instance = self.get_object()
        
        # Store data for audit log
        old_data = {
            'code': instance.code,
            'title': instance.title,
            'department_id': instance.department_id,
            'instructor_id': instance.instructor.id
        }
        
        course_id = instance.id
        instance.delete()
        
        # Create audit log for course deletion
        create_audit_log(
            performed_by=request.user,
            action='course_deleted',
            target_table='courses',
            target_id=course_id,
            old_data=old_data
        )
        
        return Response(
            {'message': 'Course deleted successfully.'},
            status=status.HTTP_200_OK
        )


class AdminEnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for admin enrollment management operations."""
    permission_classes = [IsAdmin]
    serializer_class = EnrollmentSerializer
    pagination_class = StandardPagination
    
    def get_queryset(self):
        """
        Get enrollments filtered by institution.
        Ensure data isolation by filtering to admin's institution.
        """
        queryset = Enrollment.objects.filter(
            course__institution=self.request.user.institution
        ).select_related('student', 'student__role', 'course')
        
        # Filter by course if provided
        course_id = self.request.query_params.get('course_id', None)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # Filter by student if provided
        student_id = self.request.query_params.get('student_id', None)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        
        # Filter by active status if provided
        active = self.request.query_params.get('active', None)
        if active is not None:
            active_bool = active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(active=active_bool)
        
        return queryset.order_by('-enrolled_at')
    
    def create(self, request, *args, **kwargs):
        """Create a new enrollment."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()
        
        # Create audit log for enrollment creation
        create_audit_log(
            performed_by=request.user,
            action='enrollment_created',
            target_table='enrollments',
            target_id=enrollment.id,
            new_data={
                'student_id': enrollment.student.id,
                'course_id': enrollment.course.id,
                'active': enrollment.active
            }
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update an enrollment."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Store old data for audit log
        old_data = {
            'student_id': instance.student.id,
            'course_id': instance.course.id,
            'active': instance.active
        }
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()
        
        # Store new data for audit log
        new_data = {
            'student_id': enrollment.student.id,
            'course_id': enrollment.course.id,
            'active': enrollment.active
        }
        
        # Create audit log for enrollment update
        create_audit_log(
            performed_by=request.user,
            action='enrollment_updated',
            target_table='enrollments',
            target_id=enrollment.id,
            old_data=old_data,
            new_data=new_data
        )
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete an enrollment."""
        instance = self.get_object()
        
        # Store data for audit log
        old_data = {
            'student_id': instance.student.id,
            'course_id': instance.course.id,
            'active': instance.active
        }
        
        enrollment_id = instance.id
        instance.delete()
        
        # Create audit log for enrollment deletion
        create_audit_log(
            performed_by=request.user,
            action='enrollment_deleted',
            target_table='enrollments',
            target_id=enrollment_id,
            old_data=old_data
        )
        
        return Response(
            {'message': 'Enrollment deleted successfully.'},
            status=status.HTTP_200_OK
        )


class AdminScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for admin schedule management operations."""
    permission_classes = [IsAdmin]
    serializer_class = ScheduleSerializer
    pagination_class = StandardPagination
    
    def get_queryset(self):
        """
        Get schedules filtered by institution.
        Ensure data isolation by filtering to admin's institution.
        """
        queryset = Schedule.objects.filter(
            course__institution=self.request.user.institution
        ).select_related('course', 'course__instructor')
        
        # Filter by course if provided
        course_id = self.request.query_params.get('course_id', None)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # Filter by weekday if provided
        weekday = self.request.query_params.get('weekday', None)
        if weekday is not None:
            queryset = queryset.filter(weekday=int(weekday))
        
        return queryset.order_by('weekday', 'start_time')
    
    def create(self, request, *args, **kwargs):
        """Create a new schedule."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        schedule = serializer.save()
        
        # Create audit log for schedule creation
        create_audit_log(
            performed_by=request.user,
            action='schedule_created',
            target_table='schedules',
            target_id=schedule.id,
            new_data={
                'course_id': schedule.course.id,
                'weekday': schedule.weekday,
                'start_time': str(schedule.start_time),
                'duration_minutes': schedule.duration_minutes,
                'room': schedule.room
            }
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update a schedule."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Store old data for audit log
        old_data = {
            'course_id': instance.course.id,
            'weekday': instance.weekday,
            'start_time': str(instance.start_time),
            'duration_minutes': instance.duration_minutes,
            'room': instance.room
        }
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        schedule = serializer.save()
        
        # Store new data for audit log
        new_data = {
            'course_id': schedule.course.id,
            'weekday': schedule.weekday,
            'start_time': str(schedule.start_time),
            'duration_minutes': schedule.duration_minutes,
            'room': schedule.room
        }
        
        # Create audit log for schedule update
        create_audit_log(
            performed_by=request.user,
            action='schedule_updated',
            target_table='schedules',
            target_id=schedule.id,
            old_data=old_data,
            new_data=new_data
        )
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a schedule."""
        instance = self.get_object()
        
        # Store data for audit log
        old_data = {
            'course_id': instance.course.id,
            'weekday': instance.weekday,
            'start_time': str(instance.start_time),
            'duration_minutes': instance.duration_minutes,
            'room': instance.room
        }
        
        schedule_id = instance.id
        instance.delete()
        
        # Create audit log for schedule deletion
        create_audit_log(
            performed_by=request.user,
            action='schedule_deleted',
            target_table='schedules',
            target_id=schedule_id,
            old_data=old_data
        )
        
        return Response(
            {'message': 'Schedule deleted successfully.'},
            status=status.HTTP_200_OK
        )
