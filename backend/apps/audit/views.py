from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as django_filters
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import datetime, time
from apps.accounts.permissions import IsAdmin
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogPagination(PageNumberPagination):
    """Custom pagination for audit logs with 50 records per page."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class AuditLogFilter(django_filters.FilterSet):
    """Filter class for audit log queries."""
    user_id = django_filters.NumberFilter(field_name='performed_by__id')
    date_from = django_filters.CharFilter(method='filter_date_from')
    date_to = django_filters.CharFilter(method='filter_date_to')
    action = django_filters.CharFilter(field_name='action', lookup_expr='icontains')
    target_table = django_filters.CharFilter(field_name='target_table', lookup_expr='iexact')

    class Meta:
        model = AuditLog
        fields = ['user_id', 'date_from', 'date_to', 'action', 'target_table']
    
    def filter_date_from(self, queryset, name, value):
        """
        Filter audit logs from the specified date (inclusive, start of day).
        
        This method filters audit log records starting from 00:00:00 of the specified date.
        The filter is inclusive, meaning records with performed_at exactly at midnight
        of the specified date will be included in the results.
        
        Date Format:
            Expected format is YYYY-MM-DD (ISO 8601 date format).
            Examples: '2025-11-25', '2024-01-01'
        
        Timezone Handling:
            - Parses the date string as a naive date object
            - Converts to datetime at start of day (00:00:00.000000)
            - Makes the datetime timezone-aware using Django's configured timezone
            - Applies filter using timezone-aware datetime for accurate comparison
            - This ensures correct filtering regardless of server timezone settings
        
        Args:
            queryset (QuerySet): The audit log queryset to filter
            name (str): The filter field name (not used, required by django-filter)
            value (str): Date string in YYYY-MM-DD format
            
        Returns:
            QuerySet: Filtered queryset containing records from the specified date onwards,
                     or the original queryset if date parsing fails
                     
        Examples:
            # Filter logs from November 20, 2025 onwards
            ?date_from=2025-11-20
            
            # Combined with date_to for a range
            ?date_from=2025-11-20&date_to=2025-11-22
        """
        if value:
            # Parse date-only string (YYYY-MM-DD)
            date_obj = parse_date(value)
            if date_obj:
                # Convert to datetime at start of day (00:00:00)
                dt_start = datetime.combine(date_obj, time.min)
                # Make timezone-aware
                dt_aware = timezone.make_aware(dt_start)
                return queryset.filter(performed_at__gte=dt_aware)
        return queryset
    
    def filter_date_to(self, queryset, name, value):
        """
        Filter audit logs until the specified date (inclusive, end of day).
        
        This method filters audit log records up to and including 23:59:59.999999 of the
        specified date. The filter is inclusive, meaning records with performed_at up to
        the last microsecond of the specified date will be included in the results.
        
        Date Format:
            Expected format is YYYY-MM-DD (ISO 8601 date format).
            Examples: '2025-11-25', '2024-12-31'
        
        Timezone Handling:
            - Parses the date string as a naive date object
            - Converts to datetime at end of day (23:59:59.999999)
            - Makes the datetime timezone-aware using Django's configured timezone
            - Applies filter using timezone-aware datetime for accurate comparison
            - This ensures correct filtering regardless of server timezone settings
        
        Args:
            queryset (QuerySet): The audit log queryset to filter
            name (str): The filter field name (not used, required by django-filter)
            value (str): Date string in YYYY-MM-DD format
            
        Returns:
            QuerySet: Filtered queryset containing records up to and including the
                     specified date, or the original queryset if date parsing fails
                     
        Examples:
            # Filter logs until November 20, 2025 (inclusive)
            ?date_to=2025-11-20
            
            # Combined with date_from for a range
            ?date_from=2025-11-18&date_to=2025-11-20
        """
        if value:
            # Parse date-only string (YYYY-MM-DD)
            date_obj = parse_date(value)
            if date_obj:
                # Convert to datetime at end of day (23:59:59.999999)
                dt_end = datetime.combine(date_obj, time.max)
                # Make timezone-aware
                dt_aware = timezone.make_aware(dt_end)
                return queryset.filter(performed_at__lte=dt_aware)
        return queryset


class AuditLogListView(generics.ListAPIView):
    """
    GET /api/admin/audit
    
    List audit logs with filtering and pagination.
    Only accessible by admin users.
    
    Query Parameters:
    - user_id: Filter by user ID who performed the action
    - date_from: Filter logs from this date (ISO 8601 format)
    - date_to: Filter logs until this date (ISO 8601 format)
    - action: Filter by action (case-insensitive partial match)
    - target_table: Filter by target table name (case-insensitive exact match)
    - page: Page number (default: 1)
    - page_size: Number of records per page (default: 50, max: 100)
    """
    queryset = AuditLog.objects.select_related('performed_by').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]
    pagination_class = AuditLogPagination
    filter_backends = [django_filters.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = AuditLogFilter
    ordering = ['-performed_at']
    ordering_fields = ['performed_at', 'action', 'target_table']
