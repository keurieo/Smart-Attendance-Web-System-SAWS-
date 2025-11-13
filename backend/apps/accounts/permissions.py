from rest_framework import permissions
from .models import Role


class IsAdmin(permissions.BasePermission):
    """
    Permission class that allows only admin users.
    """
    message = "You must be an admin to perform this action."
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has admin role."""
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role.name == Role.ADMIN
        )


class IsTeacher(permissions.BasePermission):
    """
    Permission class that allows only teacher users.
    """
    message = "You must be a teacher to perform this action."
    
    def has_permission(self, request, view):
        """Check if user is authenticated and has teacher role."""
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role.name == Role.TEACHER
        )


class IsTeacherForCourse(permissions.BasePermission):
    """
    Permission class that validates teacher assignment to a specific course.
    This permission should be used with views that have a course_id parameter.
    """
    message = "You are not assigned to this course."
    
    def has_permission(self, request, view):
        """Check if user is a teacher."""
        if not (request.user and request.user.is_authenticated):
            return False
        
        if not (hasattr(request.user, 'role') and request.user.role.name == Role.TEACHER):
            return False
        
        # If no course_id in request, allow the permission check to pass
        # The actual course assignment validation will happen in has_object_permission
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if teacher is assigned to the course.
        The obj should be a Course object or have a 'course' attribute.
        """
        from apps.academics.models import Course
        
        # Determine the course object
        if isinstance(obj, Course):
            course = obj
        elif hasattr(obj, 'course'):
            course = obj.course
        else:
            return False
        
        # Check if the teacher is the instructor for this course
        return course.instructor == request.user


class IsStudentEnrolled(permissions.BasePermission):
    """
    Permission class that validates student enrollment in a specific course.
    This permission should be used with views that involve course-related operations.
    """
    message = "You are not enrolled in this course."
    
    def has_permission(self, request, view):
        """Check if user is a student."""
        if not (request.user and request.user.is_authenticated):
            return False
        
        if not (hasattr(request.user, 'role') and request.user.role.name == Role.STUDENT):
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if student is enrolled in the course.
        The obj should be a Course object or have a 'course' attribute.
        """
        from apps.academics.models import Course, Enrollment
        
        # Determine the course object
        if isinstance(obj, Course):
            course = obj
        elif hasattr(obj, 'course'):
            course = obj.course
        else:
            return False
        
        # Check if the student is enrolled in this course
        return Enrollment.objects.filter(
            student=request.user,
            course=course,
            active=True
        ).exists()
