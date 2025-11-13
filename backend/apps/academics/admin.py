from django.contrib import admin
from .models import Course, Enrollment, Schedule


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'institution', 'instructor', 'department_id', 'created_at']
    list_filter = ['institution', 'department_id']
    search_fields = ['code', 'title', 'instructor__full_name']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'active', 'enrolled_at']
    list_filter = ['active', 'course']
    search_fields = ['student__full_name', 'student__email', 'course__code']


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['course', 'weekday', 'start_time', 'duration_minutes', 'room', 'created_at']
    list_filter = ['weekday', 'course']
    search_fields = ['course__code', 'room']
