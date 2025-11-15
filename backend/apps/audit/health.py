"""
Health check endpoint for monitoring system status.
"""

import logging
from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def check_database():
    """
    Check database connectivity.
    Returns (is_healthy, details)
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return True, {"status": "healthy", "message": "Database connection successful"}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}", exc_info=True)
        return False, {"status": "unhealthy", "message": f"Database connection failed: {str(e)}"}


def check_redis():
    """
    Check Redis connectivity.
    Returns (is_healthy, details)
    """
    try:
        # Try to set and get a test value
        test_key = "health_check_test"
        test_value = "ok"
        cache.set(test_key, test_value, timeout=10)
        retrieved_value = cache.get(test_key)
        
        if retrieved_value == test_value:
            cache.delete(test_key)
            return True, {"status": "healthy", "message": "Redis connection successful"}
        else:
            return False, {"status": "unhealthy", "message": "Redis value mismatch"}
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}", exc_info=True)
        return False, {"status": "unhealthy", "message": f"Redis connection failed: {str(e)}"}


def check_postgis():
    """
    Check PostGIS extension availability.
    Returns (is_healthy, details)
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT PostGIS_Version()")
            version = cursor.fetchone()[0]
        return True, {"status": "healthy", "message": f"PostGIS available: {version}"}
    except Exception as e:
        logger.error(f"PostGIS health check failed: {str(e)}", exc_info=True)
        return False, {"status": "unhealthy", "message": f"PostGIS check failed: {str(e)}"}


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint that verifies system components.
    
    Returns:
        200 OK if all components are healthy
        503 Service Unavailable if any component is unhealthy
    
    Response format:
    {
        "status": "healthy" | "unhealthy",
        "components": {
            "database": {...},
            "redis": {...},
            "postgis": {...}
        }
    }
    """
    components = {}
    overall_healthy = True
    
    # Check database
    db_healthy, db_details = check_database()
    components["database"] = db_details
    if not db_healthy:
        overall_healthy = False
    
    # Check Redis
    redis_healthy, redis_details = check_redis()
    components["redis"] = redis_details
    if not redis_healthy:
        overall_healthy = False
    
    # Check PostGIS
    postgis_healthy, postgis_details = check_postgis()
    components["postgis"] = postgis_details
    if not postgis_healthy:
        overall_healthy = False
    
    response_data = {
        "status": "healthy" if overall_healthy else "unhealthy",
        "components": components
    }
    
    http_status = status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response(response_data, status=http_status)


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness check endpoint for Kubernetes/container orchestration.
    Checks if the application is ready to serve traffic.
    
    Returns:
        200 OK if ready
        503 Service Unavailable if not ready
    """
    # For readiness, we only check critical components
    db_healthy, _ = check_database()
    
    if db_healthy:
        return Response({"status": "ready"}, status=status.HTTP_200_OK)
    else:
        return Response({"status": "not_ready"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check(request):
    """
    Liveness check endpoint for Kubernetes/container orchestration.
    Checks if the application is alive and should not be restarted.
    
    Returns:
        200 OK always (if Django can respond, it's alive)
    """
    return Response({"status": "alive"}, status=status.HTTP_200_OK)
