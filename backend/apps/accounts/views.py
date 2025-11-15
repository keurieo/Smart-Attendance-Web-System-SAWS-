from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from apps.audit.models import AuditLog
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer
)
from .models import User, Role
from .permissions import IsAdmin


def create_audit_log(performed_by, action, target_table, target_id, old_data=None, new_data=None):
    """
    Utility function to create audit log entries.
    
    Args:
        performed_by: User who performed the action
        action: Description of the action
        target_table: Name of the table affected
        target_id: ID of the affected record
        old_data: Dictionary of old values (for updates/deletes)
        new_data: Dictionary of new values (for creates/updates)
    """
    AuditLog.objects.create(
        performed_by=performed_by,
        action=action,
        target_table=target_table,
        target_id=target_id,
        old_data=old_data,
        new_data=new_data
    )


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view that includes user profile in response."""
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    """View for user registration."""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role.name,
            },
            'message': 'User registered successfully. Please login to continue.'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveAPIView):
    """View for retrieving authenticated user profile."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Return the authenticated user."""
        return self.request.user


class UserPagination(PageNumberPagination):
    """Pagination class for user list."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminUserManagementViewSet(viewsets.ModelViewSet):
    """ViewSet for admin user management operations."""
    permission_classes = [IsAdmin]
    pagination_class = UserPagination
    
    def get_queryset(self):
        """
        Get users filtered by role and active status.
        Filter by institution to ensure data isolation.
        """
        queryset = User.objects.filter(institution=self.request.user.institution).select_related('role', 'institution')
        
        # Filter by role if provided
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role__name=role)
        
        # Filter by active status if provided
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_active=is_active_bool)
        
        # Search by email or full_name if provided
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) | Q(full_name__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new user."""
        # Add the admin's institution to the request data
        data = request.data.copy()
        if 'institution_id' not in data:
            data['institution_id'] = request.user.institution.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create audit log for user creation
        create_audit_log(
            performed_by=request.user,
            action='user_created',
            target_table='users',
            target_id=user.id,
            new_data={
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role.name,
                'institution_id': user.institution.id,
                'is_active': user.is_active
            }
        )
        
        # Return user data with UserSerializer
        response_serializer = UserSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update a user."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Store old data for audit log
        old_data = {
            'email': instance.email,
            'full_name': instance.full_name,
            'role': instance.role.name,
            'is_active': instance.is_active
        }
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Store new data for audit log
        new_data = {
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role.name,
            'is_active': user.is_active
        }
        
        # Create audit log for user update
        create_audit_log(
            performed_by=request.user,
            action='user_updated',
            target_table='users',
            target_id=user.id,
            old_data=old_data,
            new_data=new_data
        )
        
        # Return user data with UserSerializer
        response_serializer = UserSerializer(user)
        return Response(response_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete a user by setting is_active to False."""
        instance = self.get_object()
        
        # Store old data for audit log
        old_data = {
            'email': instance.email,
            'full_name': instance.full_name,
            'role': instance.role.name,
            'is_active': instance.is_active
        }
        
        instance.is_active = False
        instance.save()
        
        # Store new data for audit log
        new_data = {
            'email': instance.email,
            'full_name': instance.full_name,
            'role': instance.role.name,
            'is_active': instance.is_active
        }
        
        # Create audit log for user deactivation
        create_audit_log(
            performed_by=request.user,
            action='user_deactivated',
            target_table='users',
            target_id=instance.id,
            old_data=old_data,
            new_data=new_data
        )
        
        return Response(
            {'message': 'User deactivated successfully.'},
            status=status.HTTP_200_OK
        )
