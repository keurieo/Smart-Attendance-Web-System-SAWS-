"""
Rate limiting utilities for attendance marking.

This module provides custom rate limiting decorators and functions
for the attendance marking endpoint to prevent abuse and fraud.
"""

from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
import hashlib


def get_client_ip(request):
    """
    Extract client IP address from request.
    
    Handles X-Forwarded-For header for proxied requests.
    
    Args:
        request: Django request object
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def rate_limit_key(prefix, identifier):
    """
    Generate a cache key for rate limiting.
    
    Args:
        prefix: Key prefix (e.g., 'ratelimit:user' or 'ratelimit:ip')
        identifier: Unique identifier (user_id or IP address)
        
    Returns:
        str: Cache key
    """
    # Hash the identifier for privacy
    hashed = hashlib.sha256(str(identifier).encode()).hexdigest()[:16]
    return f"{prefix}:{hashed}"


def check_rate_limit(cache_key, limit, window_seconds):
    """
    Check if rate limit has been exceeded using sliding window algorithm.
    
    Args:
        cache_key: Redis cache key
        limit: Maximum number of requests allowed
        window_seconds: Time window in seconds
        
    Returns:
        tuple: (is_allowed, current_count, retry_after)
    """
    current_time = timezone.now().timestamp()
    
    # Get current request timestamps from cache
    request_times = cache.get(cache_key, [])
    
    # Remove timestamps outside the current window
    cutoff_time = current_time - window_seconds
    request_times = [t for t in request_times if t > cutoff_time]
    
    # Check if limit exceeded
    if len(request_times) >= limit:
        # Calculate retry_after (seconds until oldest request expires)
        oldest_request = min(request_times)
        retry_after = int(window_seconds - (current_time - oldest_request)) + 1
        return False, len(request_times), retry_after
    
    # Add current request timestamp
    request_times.append(current_time)
    
    # Store updated timestamps in cache
    cache.set(cache_key, request_times, window_seconds + 60)
    
    return True, len(request_times), 0


def attendance_rate_limit(view_func):
    """
    Decorator to apply rate limiting to attendance marking endpoint.
    
    Applies two rate limits:
    - 10 requests per minute per student user ID
    - 50 requests per minute per IP address
    
    Returns HTTP 429 when rate limit is exceeded.
    """
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        # Skip rate limiting if disabled in settings
        from django.conf import settings
        if not getattr(settings, 'RATELIMIT_ENABLE', True):
            return view_func(self, request, *args, **kwargs)
        
        # Check user-based rate limit (10 requests per minute)
        if request.user and request.user.is_authenticated:
            user_key = rate_limit_key('attendance:user', request.user.id)
            user_allowed, user_count, user_retry = check_rate_limit(
                user_key, 
                limit=10, 
                window_seconds=60
            )
            
            if not user_allowed:
                return JsonResponse(
                    {
                        'error_code': 'RATE_001',
                        'message': 'Rate limit exceeded',
                        'details': {
                            'limit_type': 'user',
                            'limit': 10,
                            'window': '1 minute',
                            'current_count': user_count,
                            'retry_after': user_retry
                        },
                        'timestamp': timezone.now().isoformat()
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
        
        # Check IP-based rate limit (50 requests per minute)
        client_ip = get_client_ip(request)
        ip_key = rate_limit_key('attendance:ip', client_ip)
        ip_allowed, ip_count, ip_retry = check_rate_limit(
            ip_key,
            limit=50,
            window_seconds=60
        )
        
        if not ip_allowed:
            return JsonResponse(
                {
                    'error_code': 'RATE_002',
                    'message': 'Rate limit exceeded',
                    'details': {
                        'limit_type': 'ip',
                        'limit': 50,
                        'window': '1 minute',
                        'current_count': ip_count,
                        'retry_after': ip_retry
                    },
                    'timestamp': timezone.now().isoformat()
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Rate limits passed, proceed with request
        return view_func(self, request, *args, **kwargs)
    
    return wrapper
