from rest_framework import viewsets, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.gis.geos import Point
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.shortcuts import get_object_or_404
import re

from .models import AttendanceSession, QRToken, AttendanceRecord
from .serializers import (
    AttendanceSessionSerializer, 
    AttendanceMarkingSerializer, 
    AttendanceRecordSerializer,
    AttendanceOverrideSerializer
)
from .services import generate_qr_token, generate_6digit_code, verify_qr_token
from .ratelimit import attendance_rate_limit
from .fraud_detection import check_fraud_indicators, flag_attendance_for_review
from apps.accounts.permissions import IsTeacher, IsTeacherForCourse, IsAdmin
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
        elif self.action == 'retrieve':
            return [IsAuthenticated(), IsTeacher()]
        return super().get_permissions()
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve session details with list of attendance records.
        
        GET /api/attendance/sessions/:id
        
        Returns session details including:
        - Session information (course, time, location, radius)
        - List of attendance records with student names and statuses
        """
        session = self.get_object()
        
        # Validate teacher is assigned to session's course
        if session.course.instructor != request.user:
            return Response(
                {
                    'error_code': 'BIZ_001',
                    'message': 'Teacher not assigned to this course',
                    'details': {
                        'session_id': session.id,
                        'course_code': session.course.code
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Serialize session
        serializer = self.get_serializer(session)
        session_data = serializer.data
        
        # Get attendance records for this session
        attendance_records = AttendanceRecord.objects.filter(
            session=session
        ).select_related('student').order_by('-marked_at')
        
        # Serialize attendance records
        attendance_serializer = AttendanceRecordSerializer(
            attendance_records, 
            many=True
        )
        
        # Add attendance records to response
        session_data['attendance_records'] = attendance_serializer.data
        session_data['total_attendance'] = attendance_records.count()
        session_data['present_count'] = attendance_records.filter(
            status=AttendanceRecord.PRESENT
        ).count()
        session_data['absent_count'] = attendance_records.filter(
            status=AttendanceRecord.ABSENT
        ).count()
        session_data['rejected_count'] = attendance_records.filter(
            status=AttendanceRecord.REJECTED
        ).count()
        
        return Response(session_data, status=status.HTTP_200_OK)
    
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



class AttendanceMarkingView(views.APIView):
    """
    API view for students to mark attendance via QR scan or manual code entry.
    
    POST /api/student/attendance/scan
    
    Rate limits:
    - 10 requests per minute per student user ID
    - 50 requests per minute per IP address
    """
    permission_classes = [IsAuthenticated]
    
    @attendance_rate_limit
    @transaction.atomic
    def post(self, request):
        """
        Mark attendance for a student.
        
        Request body:
        {
            "token": "jwt_token_or_6digit_code",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "accuracy": 15.5,  // optional
            "device_info": {...}  // optional
        }
        """
        # Validate user is a student
        if not hasattr(request.user, 'role') or request.user.role.name != Role.STUDENT:
            return Response(
                {
                    'error_code': 'AUTH_003',
                    'message': 'Only students can mark attendance',
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate request data
        serializer = AttendanceMarkingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'error_code': 'VAL_001',
                    'message': 'Invalid request data',
                    'details': serializer.errors,
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token_value = serializer.validated_data['token']
        student_lat = serializer.validated_data['latitude']
        student_lon = serializer.validated_data['longitude']
        student_accuracy = serializer.validated_data.get('accuracy')
        device_info = serializer.validated_data.get('device_info')
        
        # Determine if token is 6-digit code or JWT
        is_6digit = re.match(r'^\d{6}$', token_value)
        
        # Retrieve QR token from database
        if is_6digit:
            qr_token = QRToken.objects.get_by_code6(token_value)
            method = AttendanceRecord.MANUAL_CODE
        else:
            # Verify JWT token first
            is_valid, payload, error_msg = verify_qr_token(token_value)
            if not is_valid:
                return Response(
                    {
                        'error_code': 'ATT_003',
                        'message': error_msg,
                        'timestamp': timezone.now().isoformat()
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            qr_token = QRToken.objects.get_by_token(token_value)
            method = AttendanceRecord.QR_SCAN
        
        # Check if token exists
        if not qr_token:
            return Response(
                {
                    'error_code': 'ATT_003',
                    'message': 'Invalid or revoked token',
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if token is expired
        current_time = timezone.now()
        if current_time > qr_token.expires_at:
            return Response(
                {
                    'error_code': 'ATT_003',
                    'message': 'Token expired',
                    'details': {
                        'expired_at': qr_token.expires_at.isoformat()
                    },
                    'timestamp': current_time.isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Retrieve associated attendance session
        session = qr_token.session
        
        # Validate current server time is within session time window
        if current_time < session.start_at:
            return Response(
                {
                    'error_code': 'ATT_002',
                    'message': 'Outside session time window',
                    'details': {
                        'reason': 'Session has not started yet',
                        'session_start': session.start_at.isoformat(),
                        'current_time': current_time.isoformat()
                    },
                    'timestamp': current_time.isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if current_time > session.end_at:
            return Response(
                {
                    'error_code': 'ATT_002',
                    'message': 'Outside session time window',
                    'details': {
                        'reason': 'Session has ended',
                        'session_end': session.end_at.isoformat(),
                        'current_time': current_time.isoformat()
                    },
                    'timestamp': current_time.isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate student is enrolled in the course
        enrollment = Enrollment.objects.filter(
            student=request.user,
            course=session.course,
            active=True
        ).first()
        
        if not enrollment:
            return Response(
                {
                    'error_code': 'BIZ_002',
                    'message': 'Student not enrolled in course',
                    'details': {
                        'course_code': session.course.code,
                        'course_title': session.course.title
                    },
                    'timestamp': current_time.isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get teacher location from session
        teacher_location = session.teacher_location
        teacher_lat = teacher_location.y
        teacher_lon = teacher_location.x
        
        # Validate location using geo utilities
        validation_result = validate_location(
            student_lat=student_lat,
            student_lon=student_lon,
            student_accuracy=student_accuracy if student_accuracy else 0,
            class_lat=teacher_lat,
            class_lon=teacher_lon,
            allowed_radius=session.radius_meters
        )
        
        # Create student location Point
        student_location = Point(student_lon, student_lat, srid=4326)
        
        # Determine attendance status based on validation
        if validation_result['valid']:
            attendance_status = AttendanceRecord.PRESENT
            reason = None
        else:
            attendance_status = AttendanceRecord.REJECTED
            reason = validation_result['reason']
        
        distance_meters = validation_result.get('distance')
        
        # Try to create attendance record
        try:
            attendance_record = AttendanceRecord.objects.create(
                session=session,
                student=request.user,
                method=method,
                token=qr_token,
                student_location=student_location,
                distance_meters=distance_meters,
                status=attendance_status,
                reason=reason or ''
            )
        except IntegrityError:
            # Duplicate submission (unique constraint violation)
            return Response(
                {
                    'error_code': 'ATT_004',
                    'message': 'Duplicate submission',
                    'details': {
                        'reason': 'Attendance already marked for this session'
                    },
                    'timestamp': current_time.isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Run fraud detection checks (subtask 8.3)
        device_timestamp = serializer.validated_data.get('device_timestamp')
        fraud_result = check_fraud_indicators(
            session=session,
            student_location=student_location,
            device_timestamp=device_timestamp,
            server_timestamp=current_time
        )
        
        # Flag attendance record if fraud indicators detected
        if fraud_result['should_flag']:
            flag_attendance_for_review(
                attendance_record,
                fraud_result['reasons'],
                fraud_result['details']
            )
        
        # Create location snapshot (subtask 7.3)
        LocationSnapshot.objects.create(
            user=request.user,
            location=student_location,
            source=LocationSnapshot.BROWSER_GEOLOCATION,
            accuracy=student_accuracy
        )
        
        # Create or update device tracking (subtask 7.4)
        if device_info or request.META.get('HTTP_USER_AGENT'):
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Create device info dictionary
            device_data = device_info if device_info else {}
            if 'user_agent' not in device_data:
                device_data['user_agent'] = user_agent
            
            # Generate device_id from user_agent or use provided device_id
            device_id = device_data.get('device_id')
            if not device_id:
                # Create a simple hash-based device_id from user_agent
                import hashlib
                device_id = hashlib.md5(
                    f"{request.user.id}:{user_agent}".encode()
                ).hexdigest()
            
            # Create or update device record
            device, created = Device.objects.update_or_create(
                device_id=device_id,
                defaults={
                    'user': request.user,
                    'device_info': device_data
                }
            )
        
        # Prepare response
        response_data = {
            'success': attendance_status == AttendanceRecord.PRESENT,
            'status': attendance_status,
            'marked_at': attendance_record.marked_at.isoformat(),
            'distance_meters': distance_meters,
            'session': {
                'id': session.id,
                'course_code': session.course.code,
                'course_title': session.course.title,
                'start_at': session.start_at.isoformat(),
                'end_at': session.end_at.isoformat()
            },
            'timestamp': current_time.isoformat()
        }
        
        if reason:
            response_data['reason'] = reason
        
        # Include fraud detection information if flagged
        if fraud_result['should_flag']:
            response_data['flagged_for_review'] = True
            response_data['fraud_indicators'] = fraud_result['reasons']
        
        # Return appropriate status code
        if attendance_status == AttendanceRecord.PRESENT:
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)



class AttendanceOverrideView(views.APIView):
    """
    API view for admins to override attendance records.
    
    PATCH /api/admin/attendance/:record_id
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @transaction.atomic
    def patch(self, request, record_id):
        """
        Override an attendance record status with a mandatory reason.
        
        Request body:
        {
            "status": "present|absent|rejected|pending",
            "reason": "Reason for override"
        }
        """
        # Validate request data
        serializer = AttendanceOverrideSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    'error_code': 'VAL_001',
                    'message': 'Invalid request data',
                    'details': serializer.errors,
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Retrieve existing AttendanceRecord
        attendance_record = get_object_or_404(AttendanceRecord, id=record_id)
        
        # Store old status
        old_status = attendance_record.status
        old_reason = attendance_record.reason
        
        # Extract new values
        new_status = serializer.validated_data['status']
        new_reason = serializer.validated_data['reason']
        
        # Update status and reason fields
        attendance_record.status = new_status
        attendance_record.reason = new_reason
        attendance_record.save(update_fields=['status', 'reason', 'updated_at'])
        
        # Create audit log entry with old_data and new_data
        AuditLog.objects.create(
            performed_by=request.user,
            action='override_attendance_record',
            target_table='attendance_records',
            target_id=attendance_record.id,
            old_data={
                'status': old_status,
                'reason': old_reason,
                'student_id': attendance_record.student.id,
                'student_name': attendance_record.student.full_name,
                'session_id': attendance_record.session.id,
                'course_code': attendance_record.session.course.code
            },
            new_data={
                'status': new_status,
                'reason': new_reason,
                'student_id': attendance_record.student.id,
                'student_name': attendance_record.student.full_name,
                'session_id': attendance_record.session.id,
                'course_code': attendance_record.session.course.code
            }
        )
        
        # Prepare response
        response_serializer = AttendanceRecordSerializer(attendance_record)
        return Response(
            {
                'success': True,
                'message': 'Attendance record updated successfully',
                'data': response_serializer.data,
                'timestamp': timezone.now().isoformat()
            },
            status=status.HTTP_200_OK
        )



class StudentAttendanceHistoryView(views.APIView):
    """
    API view for students to view their attendance history.
    
    GET /api/student/attendance/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get attendance history for the authenticated student.
        
        Query parameters:
        - course_id (optional): Filter by course ID
        - from_date (optional): Filter from date (YYYY-MM-DD)
        - to_date (optional): Filter to date (YYYY-MM-DD)
        - status (optional): Filter by status (present, absent, rejected, pending)
        """
        # Validate user is a student
        if not hasattr(request.user, 'role') or request.user.role.name != Role.STUDENT:
            return Response(
                {
                    'error_code': 'AUTH_003',
                    'message': 'Only students can view attendance history',
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Build query filters
        filters = {'student': request.user}
        
        # Filter by course
        course_id = request.query_params.get('course_id')
        if course_id:
            try:
                filters['session__course_id'] = int(course_id)
            except ValueError:
                return Response(
                    {
                        'error_code': 'VAL_001',
                        'message': 'Invalid course_id parameter',
                        'timestamp': timezone.now().isoformat()
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Filter by date range
        from_date = request.query_params.get('from_date')
        if from_date:
            try:
                from_date_obj = timezone.datetime.strptime(from_date, '%Y-%m-%d').date()
                filters['marked_at__date__gte'] = from_date_obj
            except ValueError:
                return Response(
                    {
                        'error_code': 'VAL_001',
                        'message': 'Invalid from_date format. Use YYYY-MM-DD',
                        'timestamp': timezone.now().isoformat()
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        to_date = request.query_params.get('to_date')
        if to_date:
            try:
                to_date_obj = timezone.datetime.strptime(to_date, '%Y-%m-%d').date()
                filters['marked_at__date__lte'] = to_date_obj
            except ValueError:
                return Response(
                    {
                        'error_code': 'VAL_001',
                        'message': 'Invalid to_date format. Use YYYY-MM-DD',
                        'timestamp': timezone.now().isoformat()
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Filter by status
        status_param = request.query_params.get('status')
        if status_param:
            if status_param not in [AttendanceRecord.PRESENT, AttendanceRecord.ABSENT, 
                                   AttendanceRecord.REJECTED, AttendanceRecord.PENDING]:
                return Response(
                    {
                        'error_code': 'VAL_001',
                        'message': f'Invalid status. Must be one of: present, absent, rejected, pending',
                        'timestamp': timezone.now().isoformat()
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            filters['status'] = status_param
        
        # Query attendance records
        attendance_records = AttendanceRecord.objects.filter(
            **filters
        ).select_related(
            'session__course',
            'session__schedule'
        ).order_by('-marked_at')
        
        # Serialize and return
        serializer = AttendanceRecordSerializer(attendance_records, many=True)
        
        return Response(
            {
                'count': attendance_records.count(),
                'results': serializer.data,
                'timestamp': timezone.now().isoformat()
            },
            status=status.HTTP_200_OK
        )
