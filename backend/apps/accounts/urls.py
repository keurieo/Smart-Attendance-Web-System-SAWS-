from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    UserRegistrationView,
    UserProfileView,
    AdminUserManagementViewSet
)

app_name = 'accounts'

# Router for admin user management
router = DefaultRouter()
router.register(r'users', AdminUserManagementViewSet, basename='admin-users')

urlpatterns = [
    # Authentication endpoints (JWT token endpoints)
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),  # Alias for token/
    path('register/', UserRegistrationView.as_view(), name='register'),
    
    # User profile endpoints
    path('users/me/', UserProfileView.as_view(), name='user-profile'),
    path('me/', UserProfileView.as_view(), name='user-profile-alias'),  # Alias
]

# Admin-specific URLs (will be mounted at /api/admin/)
admin_urlpatterns = [
    path('', include(router.urls)),
]
