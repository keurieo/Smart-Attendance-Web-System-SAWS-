from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import Course, Enrollment, Schedule
from apps.accounts.models import User, Role


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model."""
    institution_id = serializers.IntegerField(write_only=True, required=False)
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    instructor_id = serializers.IntegerField(write_only=True, required=True)
    instructor_name = serializers.CharField(source='instructor.full_name', read_only=True)
    instructor_email = serializers.CharField(source='instructor.email', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'institution_id', 'institution_name', 'code', 'title', 
            'department_id', 'instructor_id', 'instructor_name', 'instructor_email',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_instructor_id(self, value):
        """Validate that the instructor exists and has teacher role."""
        try:
            user = User.objects.select_related('role').get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Instructor does not exist.")
        
        if user.role.name != Role.TEACHER:
            raise serializers.ValidationError("Instructor must have teacher role.")
        
        return value
    
    def validate(self, attrs):
        """Validate institution matches instructor's institution."""
        instructor_id = attrs.get('instructor_id')
        institution_id = attrs.get('institution_id')
        
        if instructor_id:
            try:
                instructor = User.objects.get(id=instructor_id)
                # If institution_id is not provided, use instructor's institution
                if not institution_id:
                    attrs['institution_id'] = instructor.institution.id
                # If provided, validate it matches instructor's institution
                elif institution_id != instructor.institution.id:
                    raise serializers.ValidationError({
                        "institution_id": "Institution must match instructor's institution."
                    })
            except User.DoesNotExist:
                pass  # Will be caught by validate_instructor_id
        
        return attrs
    
    def create(self, validated_data):
        """Create course with instructor and institution."""
        instructor_id = validated_data.pop('instructor_id')
        institution_id = validated_data.pop('institution_id')
        
        instructor = User.objects.get(id=instructor_id)
        
        course = Course.objects.create(
            instructor=instructor,
            institution_id=institution_id,
            **validated_data
        )
        
        return course
    
    def update(self, instance, validated_data):
        """Update course fields."""
        instructor_id = validated_data.pop('instructor_id', None)
        validated_data.pop('institution_id', None)  # Institution cannot be changed
        
        if instructor_id:
            instructor = User.objects.get(id=instructor_id)
            instance.instructor = instructor
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model."""
    student_id = serializers.IntegerField(write_only=True, required=True)
    course_id = serializers.IntegerField(write_only=True, required=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_email = serializers.CharField(source='student.email', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student_id', 'student_name', 'student_email',
            'course_id', 'course_code', 'course_title',
            'active', 'enrolled_at', 'updated_at'
        ]
        read_only_fields = ['id', 'enrolled_at', 'updated_at']
    
    def validate_student_id(self, value):
        """Validate that the student exists and has student role."""
        try:
            user = User.objects.select_related('role').get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Student does not exist.")
        
        if user.role.name != Role.STUDENT:
            raise serializers.ValidationError("User must have student role.")
        
        return value
    
    def validate_course_id(self, value):
        """Validate that the course exists."""
        try:
            Course.objects.get(id=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course does not exist.")
        
        return value
    
    def validate(self, attrs):
        """Validate unique constraint on (student_id, course_id)."""
        student_id = attrs.get('student_id')
        course_id = attrs.get('course_id')
        
        # Check for existing enrollment (only on create)
        if not self.instance:
            if Enrollment.objects.filter(student_id=student_id, course_id=course_id).exists():
                raise serializers.ValidationError({
                    "non_field_errors": ["Student is already enrolled in this course."]
                })
        
        return attrs
    
    def create(self, validated_data):
        """Create enrollment."""
        student_id = validated_data.pop('student_id')
        course_id = validated_data.pop('course_id')
        
        enrollment = Enrollment.objects.create(
            student_id=student_id,
            course_id=course_id,
            **validated_data
        )
        
        return enrollment


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Schedule model."""
    course_id = serializers.IntegerField(write_only=True, required=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    latitude = serializers.FloatField(write_only=True, required=True)
    longitude = serializers.FloatField(write_only=True, required=True)
    location_display = serializers.SerializerMethodField(read_only=True)
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'course_id', 'course_code', 'course_title',
            'weekday', 'weekday_display', 'start_time', 'duration_minutes',
            'latitude', 'longitude', 'location_display', 'room',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_location_display(self, obj):
        """Return location as lat/lon dictionary."""
        if obj.location:
            return {
                'latitude': obj.location.y,
                'longitude': obj.location.x
            }
        return None
    
    def validate_course_id(self, value):
        """Validate that the course exists."""
        try:
            Course.objects.get(id=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course does not exist.")
        
        return value
    
    def validate_weekday(self, value):
        """Validate weekday is in valid range."""
        if value < 0 or value > 6:
            raise serializers.ValidationError("Weekday must be between 0 (Monday) and 6 (Sunday).")
        
        return value
    
    def validate_duration_minutes(self, value):
        """Validate duration is positive."""
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0.")
        
        return value
    
    def validate(self, attrs):
        """Validate location coordinates."""
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')
        
        if latitude is not None and longitude is not None:
            # Validate latitude range
            if latitude < -90 or latitude > 90:
                raise serializers.ValidationError({
                    "latitude": "Latitude must be between -90 and 90."
                })
            
            # Validate longitude range
            if longitude < -180 or longitude > 180:
                raise serializers.ValidationError({
                    "longitude": "Longitude must be between -180 and 180."
                })
            
            # Check for invalid coordinates (0, 0)
            if latitude == 0.0 and longitude == 0.0:
                raise serializers.ValidationError({
                    "non_field_errors": ["Invalid location coordinates (0, 0)."]
                })
        
        return attrs
    
    def create(self, validated_data):
        """Create schedule with location point."""
        course_id = validated_data.pop('course_id')
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        
        # Create Point object (longitude, latitude order for PostGIS)
        location = Point(longitude, latitude, srid=4326)
        
        schedule = Schedule.objects.create(
            course_id=course_id,
            location=location,
            **validated_data
        )
        
        return schedule
    
    def update(self, instance, validated_data):
        """Update schedule fields."""
        validated_data.pop('course_id', None)  # Course cannot be changed
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        
        # Update location if coordinates provided
        if latitude is not None and longitude is not None:
            instance.location = Point(longitude, latitude, srid=4326)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
