from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User
from apps.academics.models import Course, Schedule


class AttendanceSession(models.Model):
    """Model representing an attendance session."""
    ACTIVE = 'active'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (EXPIRED, 'Expired'),
        (CANCELLED, 'Cancelled'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_sessions')
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendance_sessions')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_sessions')
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    teacher_location = models.PointField(geography=True)
    radius_meters = models.IntegerField(
        validators=[MinValueValidator(10), MaxValueValidator(500)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_sessions'
        verbose_name = 'Attendance Session'
        verbose_name_plural = 'Attendance Sessions'
        indexes = [
            models.Index(fields=['course', 'start_at']),
            models.Index(fields=['created_by']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Session for {self.course.code} at {self.start_at}"


class QRToken(models.Model):
    """Model representing a QR token for attendance."""
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='qr_tokens')
    token = models.CharField(max_length=500, unique=True)
    code6 = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)

    class Meta:
        db_table = 'qr_tokens'
        verbose_name = 'QR Token'
        verbose_name_plural = 'QR Tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['session']),
            models.Index(fields=['code6']),
        ]

    def __str__(self):
        return f"Token for session {self.session.id} - {self.code6}"


class AttendanceRecord(models.Model):
    """Model representing an attendance record."""
    PRESENT = 'present'
    ABSENT = 'absent'
    REJECTED = 'rejected'
    PENDING = 'pending'
    
    STATUS_CHOICES = [
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (REJECTED, 'Rejected'),
        (PENDING, 'Pending'),
    ]
    
    QR_SCAN = 'qr_scan'
    MANUAL_CODE = 'manual_code'
    ADMIN_OVERRIDE = 'admin_override'
    
    METHOD_CHOICES = [
        (QR_SCAN, 'QR Scan'),
        (MANUAL_CODE, 'Manual Code'),
        (ADMIN_OVERRIDE, 'Admin Override'),
    ]
    
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    marked_at = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    token = models.ForeignKey(QRToken, on_delete=models.SET_NULL, null=True, blank=True, related_name='attendance_records')
    student_location = models.PointField(geography=True, null=True, blank=True)
    distance_meters = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reason = models.TextField(blank=True)
    flagged_for_review = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_records'
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
        unique_together = [['session', 'student']]
        indexes = [
            models.Index(fields=['session', 'student']),
            models.Index(fields=['student', 'marked_at']),
            models.Index(fields=['status']),
            models.Index(fields=['flagged_for_review']),
        ]

    def __str__(self):
        return f"{self.student.full_name} - {self.session.course.code} - {self.status}"
