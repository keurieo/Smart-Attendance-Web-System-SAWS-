from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import AttendanceSession, QRToken, AttendanceRecord
from apps.academics.models import Course, Schedule
import re


class AttendanceSessionSerializer(serializers.ModelSerializer):
    """Serializer for creating attendance sessions."""
    course_id = serializers.IntegerField(write_only=True)
    schedule_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    
    # Read-only fields for response
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    qr_token = serializers.SerializerMethodField()
    qr_url = serializers.SerializerMethodField()
    code6 = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceSession
        fields = [
            'id', 'course_id', 'schedule_id', 'start_at', 'end_at', 
            'radius_meters', 'latitude', 'longitude', 'notes', 'status',
            'course_code', 'course_title', 'qr_token', 'qr_url', 'code6',
            'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']
    
    def validate_radius_meters(self, value):
        """Validate radius_meters is between 10 and 500."""
        if value < 10 or value > 500:
            raise serializers.ValidationError(
                "Radius must be between 10 and 500 meters."
            )
        return value
    
    def validate(self, data):
        """Validate start_at is before end_at."""
        if data['start_at'] >= data['end_at']:
            raise serializers.ValidationError({
                'end_at': 'End time must be after start time.'
            })
        return data
    
    def get_qr_token(self, obj):
        """Get the QR token for this session."""
        if hasattr(obj, '_qr_token_data'):
            return obj._qr_token_data.get('token')
        return None
    
    def get_qr_url(self, obj):
        """Get the QR URL for this session."""
        if hasattr(obj, '_qr_token_data'):
            token = obj._qr_token_data.get('token')
            if token:
                # Generate a URL that the frontend can use
                return f"/attendance/scan?token={token}"
        return None
    
    def get_code6(self, obj):
        """Get the 6-digit code for this session."""
        if hasattr(obj, '_qr_token_data'):
            return obj._qr_token_data.get('code6')
        return None



class AttendanceMarkingSerializer(serializers.Serializer):
    """Serializer for marking attendance via QR scan or manual code entry."""
    token = serializers.CharField(required=True, max_length=500)
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    accuracy = serializers.FloatField(required=False, allow_null=True, default=None)
    device_info = serializers.JSONField(required=False, allow_null=True, default=None)
    device_timestamp = serializers.DateTimeField(required=False, allow_null=True, default=None)
    
    def validate_token(self, value):
        """Validate token format."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Token cannot be empty.")
        
        # Check if it's a 6-digit code
        if re.match(r'^\d{6}$', value):
            return value
        
        # Otherwise, assume it's a JWT token (basic validation)
        if len(value) < 10:
            raise serializers.ValidationError("Invalid token format.")
        
        return value
    
    def validate_latitude(self, value):
        """Validate latitude is within valid range."""
        if not (-90 <= value <= 90):
            raise serializers.ValidationError(
                f"Latitude must be between -90 and 90 degrees. Got: {value}"
            )
        return value
    
    def validate_longitude(self, value):
        """Validate longitude is within valid range."""
        if not (-180 <= value <= 180):
            raise serializers.ValidationError(
                f"Longitude must be between -180 and 180 degrees. Got: {value}"
            )
        return value
    
    def validate(self, data):
        """Validate student location coordinates."""
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        # Check for invalid (0,0) coordinates
        if latitude == 0.0 and longitude == 0.0:
            raise serializers.ValidationError({
                'student_location': 'Invalid location data: coordinates cannot be (0,0).'
            })
        
        return data


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for attendance record responses."""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    course_code = serializers.CharField(source='session.course.code', read_only=True)
    session_start = serializers.DateTimeField(source='session.start_at', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'session', 'student', 'student_name', 'student_email',
            'course_code', 'session_start', 'marked_at', 'method',
            'status', 'distance_meters', 'reason', 'flagged_for_review'
        ]
        read_only_fields = ['id', 'marked_at']


class AttendanceOverrideSerializer(serializers.Serializer):
    """Serializer for admin attendance record override."""
    status = serializers.ChoiceField(
        choices=[
            AttendanceRecord.PRESENT,
            AttendanceRecord.ABSENT,
            AttendanceRecord.REJECTED,
            AttendanceRecord.PENDING
        ],
        required=True
    )
    reason = serializers.CharField(
        required=True,
        allow_blank=False,
        trim_whitespace=True,
        max_length=1000
    )
    
    def validate_reason(self, value):
        """Validate reason is provided and non-empty."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError(
                "Reason must be provided and cannot be empty."
            )
        return value.strip()
    
    def validate_status(self, value):
        """Validate status is one of the allowed values."""
        allowed_statuses = [
            AttendanceRecord.PRESENT,
            AttendanceRecord.ABSENT,
            AttendanceRecord.REJECTED,
            AttendanceRecord.PENDING
        ]
        if value not in allowed_statuses:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(allowed_statuses)}"
            )
        return value
