"""
Logging middleware for request ID tracking and structured logging.
"""

import uuid
import logging
import threading

# Thread-local storage for request context
_thread_locals = threading.local()


def get_request_id():
    """Get the current request ID from thread-local storage."""
    return getattr(_thread_locals, 'request_id', None)


def set_request_id(request_id):
    """Set the request ID in thread-local storage."""
    _thread_locals.request_id = request_id


def clear_request_id():
    """Clear the request ID from thread-local storage."""
    if hasattr(_thread_locals, 'request_id'):
        delattr(_thread_locals, 'request_id')


class RequestIDMiddleware:
    """
    Middleware to generate and track request IDs for distributed tracing.
    Adds X-Request-ID header to all responses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Generate or extract request ID
        request_id = request.headers.get('X-Request-ID')
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Store in thread-local storage
        set_request_id(request_id)
        
        # Add to request object
        request.request_id = request_id
        
        # Process request
        response = self.get_response(request)
        
        # Add request ID to response headers
        response['X-Request-ID'] = request_id
        
        # Clear thread-local storage
        clear_request_id()
        
        return response


class RequestIDFilter(logging.Filter):
    """
    Logging filter that adds request_id to log records.
    """
    
    def filter(self, record):
        record.request_id = get_request_id() or 'no-request-id'
        return True
