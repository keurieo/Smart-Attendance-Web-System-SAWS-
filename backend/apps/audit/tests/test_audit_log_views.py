"""
Tests for audit log query endpoint.
"""

from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.accounts.models import User, Role, Institution
from apps.audit.models import AuditLog


class AuditLogQueryTests(TestCase):
    """Test audit log query endpoint with filtering and pagination."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create institution
        self.institution = Institution.objects.create(
            name='Test University',
            timezone='UTC'
        )
        
        # Create roles
        self.admin_role = Role.objects.create(name='admin')
        self.teacher_role = Role.objects.create(name='teacher')
        self.student_role = Role.objects.create(name='student')
        
        # Create users
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='admin123',
            full_name='Admin User',
            role=self.admin_role,
            institution=self.institution
        )
        
        self.teacher_user = User.objects.create_user(
            email='teacher@test.com',
            password='teacher123',
            full_name='Teacher User',
            role=self.teacher_role,
            institution=self.institution
        )
        
        self.student_user = User.objects.create_user(
            email='student@test.com',
            password='student123',
            full_name='Student User',
            role=self.student_role,
            institution=self.institution
        )
        
        # Create audit log entries
        self.now = timezone.now()
        
        # Logs by admin user
        self.log1 = AuditLog.objects.create(
            performed_by=self.admin_user,
            action='CREATE_USER',
            target_table='users',
            target_id=1,
            new_data={'email': 'newuser@test.com'},
            performed_at=self.now - timedelta(days=5)
        )
        
        self.log2 = AuditLog.objects.create(
            performed_by=self.admin_user,
            action='UPDATE_USER',
            target_table='users',
            target_id=1,
            old_data={'role': 'student'},
            new_data={'role': 'teacher'},
            performed_at=self.now - timedelta(days=3)
        )
        
        # Logs by teacher user
        self.log3 = AuditLog.objects.create(
            performed_by=self.teacher_user,
            action='CREATE_SESSION',
            target_table='attendance_sessions',
            target_id=10,
            new_data={'course_id': 5},
            performed_at=self.now - timedelta(days=2)
        )
        
        self.log4 = AuditLog.objects.create(
            performed_by=self.teacher_user,
            action='CREATE_SESSION',
            target_table='attendance_sessions',
            target_id=11,
            new_data={'course_id': 6},
            performed_at=self.now - timedelta(days=1)
        )
        
        # Log for different table
        self.log5 = AuditLog.objects.create(
            performed_by=self.admin_user,
            action='OVERRIDE_ATTENDANCE',
            target_table='attendance_records',
            target_id=20,
            old_data={'status': 'absent'},
            new_data={'status': 'present', 'reason': 'Medical excuse'},
            performed_at=self.now
        )
        
        self.url = reverse('audit-log-list')
    
    def test_list_audit_logs_as_admin(self):
        """Test that admin can list all audit logs."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 5)
        self.assertEqual(len(response.data['results']), 5)
    
    def test_list_audit_logs_as_teacher_forbidden(self):
        """Test that teacher cannot access audit logs."""
        self.client.force_authenticate(user=self.teacher_user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_audit_logs_as_student_forbidden(self):
        """Test that student cannot access audit logs."""
        self.client.force_authenticate(user=self.student_user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_audit_logs_unauthenticated(self):
        """Test that unauthenticated users cannot access audit logs."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_filter_by_user_id(self):
        """Test filtering audit logs by user ID."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url, {'user_id': self.teacher_user.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Verify all results are from teacher user
        for log in response.data['results']:
            self.assertEqual(log['performed_by'], self.teacher_user.id)
    
    def test_filter_by_date_from(self):
        """Test filtering audit logs from a specific date."""
        self.client.force_authenticate(user=self.admin_user)
        
        date_from = (self.now - timedelta(days=2)).isoformat()
        response = self.client.get(self.url, {'date_from': date_from})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return logs from last 2 days (log3, log4, log5)
        self.assertEqual(response.data['count'], 3)
    
    def test_filter_by_date_to(self):
        """Test filtering audit logs until a specific date."""
        self.client.force_authenticate(user=self.admin_user)
        
        date_to = (self.now - timedelta(days=3)).isoformat()
        response = self.client.get(self.url, {'date_to': date_to})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return logs older than 3 days (log1, log2)
        self.assertEqual(response.data['count'], 2)
    
    def test_filter_by_date_range(self):
        """Test filtering audit logs by date range."""
        self.client.force_authenticate(user=self.admin_user)
        
        date_from = (self.now - timedelta(days=4)).isoformat()
        date_to = (self.now - timedelta(days=1)).isoformat()
        
        response = self.client.get(self.url, {
            'date_from': date_from,
            'date_to': date_to
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return logs in the middle range (log2, log3, log4)
        self.assertEqual(response.data['count'], 3)
    
    def test_filter_by_action(self):
        """Test filtering audit logs by action."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url, {'action': 'CREATE_SESSION'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Verify all results have CREATE_SESSION action
        for log in response.data['results']:
            self.assertIn('CREATE_SESSION', log['action'])
    
    def test_filter_by_action_case_insensitive(self):
        """Test that action filtering is case-insensitive."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url, {'action': 'create_session'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_filter_by_action_partial_match(self):
        """Test that action filtering supports partial matches."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url, {'action': 'CREATE'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should match CREATE_USER and CREATE_SESSION
        self.assertEqual(response.data['count'], 3)
    
    def test_filter_by_target_table(self):
        """Test filtering audit logs by target table."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url, {'target_table': 'users'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Verify all results target users table
        for log in response.data['results']:
            self.assertEqual(log['target_table'], 'users')
    
    def test_filter_by_target_table_case_insensitive(self):
        """Test that target table filtering is case-insensitive."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url, {'target_table': 'USERS'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_multiple_filters_combined(self):
        """Test combining multiple filters."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url, {
            'user_id': self.admin_user.id,
            'target_table': 'users'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        # Verify results match both filters
        for log in response.data['results']:
            self.assertEqual(log['performed_by'], self.admin_user.id)
            self.assertEqual(log['target_table'], 'users')
    
    def test_pagination_default_page_size(self):
        """Test default pagination with 50 records per page."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        
        # With only 5 logs, all should be on first page
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
    
    def test_pagination_custom_page_size(self):
        """Test pagination with custom page size."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url, {'page_size': 2})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIsNotNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
    
    def test_pagination_second_page(self):
        """Test accessing second page of results."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url, {'page': 2, 'page_size': 2})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIsNotNone(response.data['previous'])
    
    def test_pagination_max_page_size(self):
        """Test that page size is capped at maximum."""
        self.client.force_authenticate(user=self.admin_user)
        
        # Try to request more than max (100)
        response = self.client.get(self.url, {'page_size': 200})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should still work, but limited to max
        self.assertEqual(len(response.data['results']), 5)
    
    def test_ordering_by_performed_at_descending(self):
        """Test that results are ordered by performed_at descending by default."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # First result should be the most recent (log5)
        self.assertEqual(response.data['results'][0]['id'], self.log5.id)
        # Last result should be the oldest (log1)
        self.assertEqual(response.data['results'][-1]['id'], self.log1.id)
    
    def test_response_includes_user_details(self):
        """Test that response includes user email and name."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        first_log = response.data['results'][0]
        self.assertIn('performed_by_email', first_log)
        self.assertIn('performed_by_name', first_log)
        self.assertIsNotNone(first_log['performed_by_email'])
        self.assertIsNotNone(first_log['performed_by_name'])
    
    def test_response_includes_all_fields(self):
        """Test that response includes all expected fields."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        first_log = response.data['results'][0]
        expected_fields = [
            'id', 'performed_by', 'performed_by_email', 'performed_by_name',
            'action', 'target_table', 'target_id', 'old_data', 'new_data',
            'performed_at'
        ]
        
        for field in expected_fields:
            self.assertIn(field, first_log)
    
    def test_filter_with_no_results(self):
        """Test filtering that returns no results."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url, {'action': 'NONEXISTENT_ACTION'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_audit_log_with_null_performed_by(self):
        """Test handling of audit logs with null performed_by (system actions)."""
        # Create a system-generated log
        system_log = AuditLog.objects.create(
            performed_by=None,
            action='SYSTEM_CLEANUP',
            target_table='sessions',
            target_id=999,
            performed_at=self.now
        )
        
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)
        
        # Find the system log in results
        system_log_result = next(
            (log for log in response.data['results'] if log['id'] == system_log.id),
            None
        )
        
        self.assertIsNotNone(system_log_result)
        self.assertIsNone(system_log_result['performed_by'])
        self.assertIsNone(system_log_result['performed_by_email'])
        self.assertIsNone(system_log_result['performed_by_name'])
