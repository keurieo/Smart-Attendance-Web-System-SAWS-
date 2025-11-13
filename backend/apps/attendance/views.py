from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import Point
from django.db import transaction, IntegrityError
from django.utils import timezone
import re

from .models import AttendanceSession, QRToken, AttendanceRecord
from .serializers import AttendanceSessionSerializer, AttendanceMarkingSerializer, AttendanceRecordSerializer
from .services import generate_qr_token, generate_6digit_code, verify_qr_token
from apps.accounts.permissions import IsTeacher, IsTeacherForCourse
from apps.accounts.models import Role
from apps.academics.models import Course, Schedule, Enrollment
from apps.audit.models import AuditLog, LocationSnapshot, Device
from apps.geo.utils import validate_location


class AttendanceSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing attendance sessions."""
    queryset = AttendanceSession.objects.all()
    serializer_class = AttendanceSessionSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    
    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action == 'create':
            return [IsAuthenticated(), IsTeacher()]
        return super().get_permissions()
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create a new attendance session.
        
        POST /api/teacher/sessions
        
        Request body:
        {
            "course_id": 1,
            "schedule_id": 1,  // optional
            "start_at": "2025-11-13T10:00:00Z",
            "end_at": "2025-11-13T11:00:00Z",
            "radius_meters": 50,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "notes": "Optional notes"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract validated data
        course_id = serializer.validated_data.pop('course_id')
        schedule_id = serializer.validated_data.pop('schedule_id', None)
        latitude = serializer.validated_data.pop('latitude')
        longitude = serializer.validated_data.pop('longitude')
        
        # Validate course exists
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response(
                {
                    'error_code': 'BIZ_001',
                    'message': 'Course not found',
                    'details': {'course_id': course_id}
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate teacher is assigned to the course
        if course.instructor != request.user:
            return Response(
                {
                    'error_code': 'BIZ_001',
                    'message': 'Teacher not assigned to course',
                    'details': {'course_id': course_id}
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate schedule if provided
        schedule = None
        if schedule_id:
            try:
                schedule = Schedule.objects.get(id=schedule_id, course=course)
            except Schedule.DoesNotExist:
                return Response(
                    {
                        'error_code': 'VAL_001',
                        'message': 'Schedule not found for this course',
                        'details': {'schedule_id': schedule_id}
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Create Point for teacher location
        teacher_location = Point(longitude, latitude, srid=4326)
        
        # Create the attendance session
        session = AttendanceSession.objects.create(
            course=course,
            schedule=schedule,
            created_by=request.user,
            teacher_location=teacher_location,
            **serializer.validated_data
        )
        
        # Generate QR token and 6-digit code
        token_string, nonce = generate_qr_token(
            session.id,
            serializer.validated_data['end_at']
        )
        code6 = generate_6digit_code()
        
        # Create QRToken record
        qr_token = QRToken.objects.create_token(
            session=session,
            token=token_string,
            code6=code6,
            expires_at=serializer.validated_data['end_at']
        )
        
        # Create location snapshot (subtask 6.3)
        LocationSnapshot.objects.create(
            user=request.user,
            location=teacher_location,
            source=LocationSnapshot.BROWSER_GEOLOCATION
        )
        
        # Create audit log entry (subtask 6.4)
        AuditLog.objects.create(
            performed_by=request.user,
            action='create_attendance_session',
            target_table='attendance_sessions',
            target_id=session.id,
            new_data={
                'course_id': course.id,
                'course_code': course.code,
                'schedule_id': schedule.id if schedule else None,
                'start_at': serializer.validated_data['start_at'].isoformat(),
                'end_at': serializer.validated_data['end_at'].isoformat(),
                'radius_meters': serializer.validated_data['radius_meters'],
                'teacher_location': {
                    'latitude': latitude,
                    'longitude': longitude
                }
            }
        )
        
        # Attach token data to session for serializer
        session._qr_token_data = {
            'token': token_string,
            'code6': code6
        }
        
        # Serialize and return response
        response_serializer = self.get_serializer(session)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
