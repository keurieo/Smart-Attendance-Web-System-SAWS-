from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit log entries."""
    performed_by_email = serializers.SerializerMethodField()
    performed_by_name = serializers.SerializerMethodField()
    
    def get_performed_by_email(self, obj):
        """Return email of user who performed action, or None if system action."""
        return obj.performed_by.email if obj.performed_by else None
    
    def get_performed_by_name(self, obj):
        """Return full name of user who performed action, or None if system action."""
        return obj.performed_by.full_name if obj.performed_by else None
    
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
