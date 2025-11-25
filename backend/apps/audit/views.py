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
        Filter logs from the specified date (inclusive, start of day).
        
        Accepts date strings in YYYY-MM-DD format and filters records
        from 00:00:00 of that date onwards. Handles timezone conversion
        to ensure accurate filtering regardless of server timezone.
        
        Args:
            queryset: The queryset to filter
            name: The filter field name
            value: Date string in YYYY-MM-DD format
            
        Returns:
            Filtered queryset or original if date parsing fails
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
        Filter logs until the specified date (inclusive, end of day).
        
        Accepts date strings in YYYY-MM-DD format and filters records
        until 23:59:59.999999 of that date. Handles timezone conversion
        to ensure accurate filtering regardless of server timezone.
        
        Args:
            queryset: The queryset to filter
            name: The filter field name
            value: Date string in YYYY-MM-DD format
            
        Returns:
            Filtered queryset or original if date parsing fails
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
