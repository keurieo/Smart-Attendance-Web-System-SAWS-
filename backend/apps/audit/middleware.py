"""
Audit logging middleware for tracking user actions.
"""
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests for audit purposes.
    
    Note: This is a placeholder implementation. Full audit logging
    will be implemented when the audit log endpoint task is executed.
    For now, it just passes through without logging to avoid errors.
    """
    
    def process_response(self, request, response):
        """
        Process response - currently a pass-through.
        """
        # TODO: Implement full audit logging in future task
        # This middleware is registered but doesn't log yet
        return response
