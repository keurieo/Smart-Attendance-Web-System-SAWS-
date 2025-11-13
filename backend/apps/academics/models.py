from django.contrib.gis.db import models
from apps.accounts.models import Institution, User


class Course(models.Model):
    """Model representing a course."""
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='courses')
    code = models.CharField(max_length=20)
    title = models.CharField(max_length=255)
    department_id = models.CharField(max_length=50)
    instructor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='taught_courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        unique_together = [['institution', 'code']]
        indexes = [
            models.Index(fields=['institution', 'code']),
            models.Index(fields=['instructor']),
        ]

    def __str__(self):
        return f"{self.code} - {self.title}"


class Enrollment(models.Model):
    """Model representing student enrollment in a course."""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    active = models.BooleanField(default=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'enrollments'
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
        unique_together = [['student', 'course']]
        indexes = [
            models.Index(fields=['student', 'course']),
            models.Index(fields=['course', 'active']),
        ]

    def __str__(self):
        return f"{self.student.full_name} enrolled in {self.course.code}"


class Schedule(models.Model):
    """Model representing a course schedule."""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
    
    WEEKDAY_CHOICES = [
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='schedules')
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    duration_minutes = models.IntegerField()
    location = models.PointField(geography=True)
    room = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'schedules'
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        indexes = [
            models.Index(fields=['course', 'weekday']),
        ]

    def __str__(self):
        return f"{self.course.code} - {self.get_weekday_display()} {self.start_time}"
