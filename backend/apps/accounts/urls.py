from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView,
    UserRegistrationView,
    UserProfileView,
    AdminUserManagementViewSet
)

app_name = 'accounts'

# Router for admin user management
router = DefaultRouter()
router.register(r'admin/users', AdminUserManagementViewSet, basename='admin-users')

urlpatterns = [
    # Authentication endpoints
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    
    # User profile endpoint
    path('me/', UserProfileView.as_view(), name='user-profile'),
    
    # Include router URLs
    path('', include(router.urls)),
]
