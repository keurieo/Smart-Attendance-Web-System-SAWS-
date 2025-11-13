from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceSessionViewSet, AttendanceMarkingView

router = DefaultRouter()
router.register(r'sessions', AttendanceSessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
    path('scan/', AttendanceMarkingView.as_view(), name='attendance-scan'),
]
