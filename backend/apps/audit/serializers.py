from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit log entries."""
    performed_by_email = serializers.EmailField(source='performed_by.email', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.full_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'performed_by',
            'performed_by_email',
            'performed_by_name',
            'action',
            'target_table',
            'target_id',
            'old_data',
            'new_data',
            'performed_at',
        ]
        read_only_fields = fields
