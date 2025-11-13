from django.contrib.gis.db import models
from apps.accounts.models import User


class AuditLog(models.Model):
    """Model for tracking all system operations."""
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=100)
    target_table = models.CharField(max_length=100)
    target_id = models.BigIntegerField()
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    performed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['performed_by', 'performed_at']),
            models.Index(fields=['target_table', 'target_id']),
            models.Index(fields=['action']),
            models.Index(fields=['performed_at']),
        ]
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.action} on {self.target_table} by {self.performed_by}"


class LocationSnapshot(models.Model):
    """Model for storing location snapshots."""
    BROWSER_GEOLOCATION = 'browser_geolocation'
    GPS = 'gps'
    MANUAL = 'manual'
    
    SOURCE_CHOICES = [
        (BROWSER_GEOLOCATION, 'Browser Geolocation'),
        (GPS, 'GPS'),
        (MANUAL, 'Manual'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location_snapshots')
    recorded_at = models.DateTimeField(auto_now_add=True)
    location = models.PointField(geography=True)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    accuracy = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'location_snapshots'
        verbose_name = 'Location Snapshot'
        verbose_name_plural = 'Location Snapshots'
        indexes = [
            models.Index(fields=['user', 'recorded_at']),
            models.Index(fields=['recorded_at']),
        ]
        ordering = ['-recorded_at']

    def __str__(self):
        return f"Location for {self.user.full_name} at {self.recorded_at}"


class Device(models.Model):
    """Model for tracking devices used for attendance."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=255, unique=True)
    device_info = models.JSONField()
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'devices'
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['device_id']),
            models.Index(fields=['last_seen']),
        ]

    def __str__(self):
        return f"Device {self.device_id} for {self.user.full_name}"
