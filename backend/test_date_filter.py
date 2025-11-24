#!/usr/bin/env python
"""Quick test script to debug date filtering."""
import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.utils import timezone
from apps.audit.models import AuditLog
from apps.accounts.models import User, Role, Institution

# Create test data
institution = Institution.objects.first() or Institution.objects.create(name="Test Institution")
admin_role = Role.objects.get_or_create(name='admin')[0]
admin_user = User.objects.create_user(
    email='testadmin@test.com',
    password='test123',
    full_name='Test Admin',
    role=admin_role,
    institution=institution
)

now = timezone.now()
print(f"Current time: {now}")
print(f"Current time ISO: {now.isoformat()}")

# Create logs at different times
log1 = AuditLog.objects.create(
    performed_by=admin_user,
    action='TEST1',
    target_table='test',
    target_id=1,
    performed_at=now - timedelta(days=5)
)
print(f"Log1 time: {log1.performed_at} (5 days ago)")

log2 = AuditLog.objects.create(
    performed_by=admin_user,
    action='TEST2',
    target_table='test',
    target_id=2,
    performed_at=now - timedelta(days=3)
)
print(f"Log2 time: {log2.performed_at} (3 days ago)")

log3 = AuditLog.objects.create(
    performed_by=admin_user,
    action='TEST3',
    target_table='test',
    target_id=3,
    performed_at=now - timedelta(days=2)
)
print(f"Log3 time: {log3.performed_at} (2 days ago)")

log4 = AuditLog.objects.create(
    performed_by=admin_user,
    action='TEST4',
    target_table='test',
    target_id=4,
    performed_at=now - timedelta(days=1)
)
print(f"Log4 time: {log4.performed_at} (1 day ago)")

log5 = AuditLog.objects.create(
    performed_by=admin_user,
    action='TEST5',
    target_table='test',
    target_id=5,
    performed_at=now
)
print(f"Log5 time: {log5.performed_at} (now)")

# Test filtering
date_from = (now - timedelta(days=2)).isoformat()
print(f"\nFilter date_from: {date_from}")
print(f"Expected: logs 3, 4, 5 (last 2 days)")

filtered = AuditLog.objects.filter(performed_at__gte=now - timedelta(days=2))
print(f"Actual count: {filtered.count()}")
for log in filtered:
    print(f"  - {log.action} at {log.performed_at}")

# Cleanup
AuditLog.objects.filter(action__startswith='TEST').delete()
admin_user.delete()
