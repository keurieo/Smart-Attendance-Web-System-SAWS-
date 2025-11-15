from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from django.db.models import Q
from datetime import datetime

from apps.accounts.permissions import IsTeacher
from apps.academics.models import Course
from apps.attendance.models import AttendanceRecord, AttendanceSession
from .renderers import CSVAttendanceRenderer


class AttendanceReportView(views.APIView):
    """
    API view for teachers to generate attendance reports.
    
    GET /api/reports/attendance?course_id=1&from_date=2025-11-01&to_date=2025-11-30
    
    Supports both JSON and CSV formats via Accept header or format query parameter.
    """
    permission_classes = [IsAuthenticated, IsTeacher]
    renderer_classes = [JSONRenderer, CSVAttendanceRenderer]
    
    def get(self, request):
        """
        Generate attendance report for a course within a date range.
        
        Query parameters:
        - course_id (required): ID of the course
        - from_date (optional): Start date in YYYY-MM-DD format
        - to_date (optional): End date in YYYY-MM-DD format
        """
        # Extract query parameters
        course_id = request.query_params.get('course_id')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        
        # Validate course_id is provided
        if not course_id:
            return Response(
                {
                    'error_code': 'VAL_001',
                    'message': 'Missing required parameter: course_id'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
                    'details': {
                        'course_id': course_id,
                        'course_code': course.code
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Build query filters
        filters = Q(session__course=course)
        
        # Parse and validate date filters
        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
                filters &= Q(session__start_at__gte=from_date_obj)
            except ValueError:
                return Response(
                    {
                        'error_code': 'VAL_002',
                        'message': 'Invalid from_date format. Use YYYY-MM-DD',
                        'details': {'from_date': from_date}
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
                # Include the entire day by adding 23:59:59
                from datetime import timedelta
                to_date_obj = to_date_obj + timedelta(days=1) - timedelta(seconds=1)
                filters &= Q(session__start_at__lte=to_date_obj)
            except ValueError:
                return Response(
                    {
                        'error_code': 'VAL_002',
                        'message': 'Invalid to_date format. Use YYYY-MM-DD',
                        'details': {'to_date': to_date}
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Query attendance records with student data
        attendance_records = AttendanceRecord.objects.filter(filters).select_related(
            'student',
            'session',
            'session__course'
        ).order_by('session__start_at', 'student__full_name')
        
        # Prepare data for CSV renderer
        report_data = []
        for record in attendance_records:
            report_data.append({
                'student_name': record.student.full_name,
                'email': record.student.email,
                'session_date': record.session.start_at.strftime('%Y-%m-%d'),
                'session_time': record.session.start_at.strftime('%H:%M:%S'),
                'status': record.status,
                'marked_at': record.marked_at.strftime('%Y-%m-%d %H:%M:%S') if record.marked_at else '',
                'distance_meters': f"{record.distance_meters:.2f}" if record.distance_meters is not None else '',
                'reason': record.reason or ''
            })
        
        # Return response with CSV renderer
        return Response(report_data, status=status.HTTP_200_OK)
