from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import User, Role, Institution, TeacherProfile, StudentProfile


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer that includes user profile information."""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['full_name'] = user.full_name
        token['role'] = user.role.name
        token['institution_id'] = user.institution.id
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user profile information to response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'full_name': self.user.full_name,
            'role': self.user.role.name,
            'institution': {
                'id': self.user.institution.id,
                'name': self.user.institution.name,
            },
            'is_active': self.user.is_active,
        }
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(required=True)
    institution_id = serializers.IntegerField(required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'full_name', 'role', 'institution_id']
    
    def validate(self, attrs):
        """Validate password confirmation and role."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validate role exists
        role_name = attrs['role']
        if role_name not in [Role.ADMIN, Role.TEACHER, Role.STUDENT]:
            raise serializers.ValidationError({"role": f"Invalid role. Must be one of: {Role.ADMIN}, {Role.TEACHER}, {Role.STUDENT}"})
        
        # Validate institution exists
        try:
            Institution.objects.get(id=attrs['institution_id'])
        except Institution.DoesNotExist:
            raise serializers.ValidationError({"institution_id": "Institution does not exist."})
        
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password."""
        validated_data.pop('password_confirm')
        role_name = validated_data.pop('role')
        institution_id = validated_data.pop('institution_id')
        
        # Get role and institution objects
        role = Role.objects.get(name=role_name)
        institution = Institution.objects.get(id=institution_id)
        
        # Create user with hashed password (using bcrypt via set_password)
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            role=role,
            institution=institution
        )
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information."""
    role = serializers.CharField(source='role.name', read_only=True)
    institution = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'role', 'institution', 'is_active', 'profile', 'created_at', 'last_login']
        read_only_fields = ['id', 'email', 'created_at', 'last_login']
    
    def get_institution(self, obj):
        """Get institution details."""
        return {
            'id': obj.institution.id,
            'name': obj.institution.name,
            'timezone': obj.institution.timezone,
        }
    
    def get_profile(self, obj):
        """Get role-specific profile information."""
        if obj.role.name == Role.TEACHER:
            try:
                profile = obj.teacher_profile
                return {
                    'type': 'teacher',
                    'employee_id': profile.employee_id,
                    'department_id': profile.department_id,
                }
            except TeacherProfile.DoesNotExist:
                return None
        elif obj.role.name == Role.STUDENT:
            try:
                profile = obj.student_profile
                return {
                    'type': 'student',
                    'roll_number': profile.roll_number,
                    'enrollment_year': profile.enrollment_year,
                    'department_id': profile.department_id,
                }
            except StudentProfile.DoesNotExist:
                return None
        return None
