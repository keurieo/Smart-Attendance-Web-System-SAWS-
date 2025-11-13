from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    UserRegistrationView,
    UserProfileView
)

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    
    # User profile endpoint
    path('me/', UserProfileView.as_view(), name='user-profile'),
]
