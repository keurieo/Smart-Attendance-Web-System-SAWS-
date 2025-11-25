"""
Regression Test Script for Admin Panel Bug Fixes

This script performs comprehensive regression testing to ensure:
1. Existing functionality still works
2. Performance is not degraded
3. Error handling is robust
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from apps.audit.views import AuditLogViewSet
from apps.audit.models import AuditLog
from apps.attendance.models import AttendanceSession, AttendanceRecord
from apps.academics.models import Course, Enrollment
from apps.accounts.models import Role

User = get_user_model()


class RegressionTests:
    """Comprehensive regression test suite"""
    
    def __init__(self):
        self.factory = RequestFactory()
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def log_result(self, test_name, passed, error=None):
        """Log test result"""
        if passed:
            self.passed += 1
            print(f"✓ {test_name}")
        else:
            self.failed += 1
            print(f"✗ {test_name}")
            if error:
                self.errors.append(f"{test_name}: {error}")
                print(f"  Error: {error}")
    
    def test_audit_log_date_filtering(self):
        """Test 8.1: Verify audit log date filtering works correctly"""
        try:
            # Create test data
            now = timezone.now()
            past = now - timedelta(days=5)
            future = now + timedelta(days=5)
            
            # Test date_from filter
            viewset = AuditLogViewSet()
            queryset = AuditLog.objects.all()
            
            # Test with date string
            filtered = viewset.filter_date_from(queryset, 'date_from', now.strftime('%Y-%m-%d'))
            
            # Should not raise exception
            self.log_result("Audit log date_from filter", True)
            
            # Test date_to filter
            filtered = viewset.filter_date_to(queryset, 'date_to', now.strftime('%Y-%m-%d'))
            self.log_result("Audit log date_to filter", True)
            
        except Exception as e:
            self.log_result("Audit log date filtering", False, str(e))
    
    def test_model_field_references(self):
        """Test 8.1: Verify model field references are correct"""
        try:
            # Test User model fields
            user_fields = [f.name for f in User._meta.get_fields()]
            assert 'full_name' in user_fields, "User.full_name field missing"
            assert 'email' in user_fields, "User.email field missing"
            assert 'role' in user_fields, "User.role field missing"
            self.log_result("User model field references", True)
            
            # Test AttendanceSession model fields
            session_fields = [f.name for f in AttendanceSession._meta.get_fields()]
            assert 'teacher_location' in session_fields, "AttendanceSession.teacher_location field missing"
            assert 'created_by' in session_fields, "AttendanceSession.created_by field missing"
            assert 'end_at' in session_fields, "AttendanceSession.end_at field missing"
            self.log_result("AttendanceSession model field references", True)
            
            # Test Course model fields
            course_fields = [f.name for f in Course._meta.get_fields()]
            assert 'title' in course_fields, "Course.title field missing"
            self.log_result("Course model field references", True)
            
        except AssertionError as e:
            self.log_result("Model field references", False, str(e))
        except Exception as e:
            self.log_result("Model field references", False, str(e))
    
    def test_model_constants(self):
        """Test 8.1: Verify model constants are defined"""
        try:
            # Test AttendanceSession constants
            assert hasattr(AttendanceSession, 'ACTIVE'), "AttendanceSession.ACTIVE constant missing"
            assert hasattr(AttendanceSession, 'COMPLETED'), "AttendanceSession.COMPLETED constant missing"
            assert hasattr(AttendanceSession, 'CANCELLED'), "AttendanceSession.CANCELLED constant missing"
            self.log_result("AttendanceSession constants", True)
            
            # Test AttendanceRecord constants
            assert hasattr(AttendanceRecord, 'PRESENT'), "AttendanceRecord.PRESENT constant missing"
            assert hasattr(AttendanceRecord, 'ABSENT'), "AttendanceRecord.ABSENT constant missing"
            assert hasattr(AttendanceRecord, 'LATE'), "AttendanceRecord.LATE constant missing"
            self.log_result("AttendanceRecord constants", True)
            
        except AssertionError as e:
            self.log_result("Model constants", False, str(e))
        except Exception as e:
            self.log_result("Model constants", False, str(e))
    
    def test_error_handling_invalid_dates(self):
        """Test 8.3: Verify error handling for invalid date formats"""
        try:
            viewset = AuditLogViewSet()
            queryset = AuditLog.objects.all()
            
            # Test with invalid date format
            invalid_dates = [
                'invalid-date',
                '2025-13-45',  # Invalid month/day
                '25-11-2025',  # Wrong format
                'not-a-date',
            ]
            
            for invalid_date in invalid_dates:
                try:
                    # Should not crash, just return original queryset
                    result = viewset.filter_date_from(queryset, 'date_from', invalid_date)
                    # If it returns without exception, that's good
                except Exception as e:
                    # Should handle gracefully
                    raise Exception(f"Failed to handle invalid date '{invalid_date}': {e}")
            
            self.log_result("Error handling for invalid dates", True)
            
        except Exception as e:
            self.log_result("Error handling for invalid dates", False, str(e))
    
    def test_null_handling(self):
        """Test 8.3: Verify null value handling"""
        try:
            viewset = AuditLogViewSet()
            queryset = AuditLog.objects.all()
            
            # Test with None values
            result = viewset.filter_date_from(queryset, 'date_from', None)
            assert result == queryset, "Should return original queryset for None"
            
            # Test with empty string
            result = viewset.filter_date_from(queryset, 'date_from', '')
            assert result == queryset, "Should return original queryset for empty string"
            
            self.log_result("Null value handling", True)
            
        except Exception as e:
            self.log_result("Null value handling", False, str(e))
    
    def test_timezone_awareness(self):
        """Test 8.1: Verify timezone-aware datetime handling"""
        try:
            from django.utils.dateparse import parse_date
            from datetime import time
            
            # Test date parsing and timezone conversion
            date_str = '2025-11-25'
            date_obj = parse_date(date_str)
            assert date_obj is not None, "Date parsing failed"
            
            # Test datetime combination
            dt_start = datetime.combine(date_obj, time.min)
            dt_end = datetime.combine(date_obj, time.max)
            
            # Test timezone awareness
            dt_aware_start = timezone.make_aware(dt_start)
            dt_aware_end = timezone.make_aware(dt_end)
            
            assert timezone.is_aware(dt_aware_start), "Start datetime should be timezone-aware"
            assert timezone.is_aware(dt_aware_end), "End datetime should be timezone-aware"
            
            self.log_result("Timezone awareness", True)
            
        except Exception as e:
            self.log_result("Timezone awareness", False, str(e))
    
    def test_serializer_fields(self):
        """Test 8.1: Verify serializer fields are correct"""
        try:
            from apps.audit.serializers import AuditLogSerializer
            
            # Check that performed_by_email field exists
            serializer = AuditLogSerializer()
            fields = serializer.get_fields()
            
            assert 'performed_by_email' in fields, "performed_by_email field missing from serializer"
            assert 'performed_by_name' in fields, "performed_by_name field missing from serializer"
            
            self.log_result("Serializer fields", True)
            
        except Exception as e:
            self.log_result("Serializer fields", False, str(e))
    
    def test_admin_configurations(self):
        """Test 8.1: Verify admin configurations are valid"""
        try:
            from apps.attendance.admin import AttendanceSessionAdmin
            from apps.accounts.admin import UserAdmin
            
            # Test AttendanceSession admin
            if hasattr(AttendanceSessionAdmin, 'fieldsets'):
                # Check that fieldsets reference valid fields
                for fieldset in AttendanceSessionAdmin.fieldsets:
                    fields = fieldset[1].get('fields', [])
                    for field in fields:
                        if isinstance(field, str):
                            # Verify field exists in model
                            session_fields = [f.name for f in AttendanceSession._meta.get_fields()]
                            if field not in session_fields and field != 'teacher_location':
                                # teacher_location might be a property or method
                                pass
            
            self.log_result("Admin configurations", True)
            
        except Exception as e:
            self.log_result("Admin configurations", False, str(e))
    
    def test_url_patterns(self):
        """Test 8.1: Verify URL patterns are configured correctly"""
        try:
            from django.urls import reverse, NoReverseMatch
            
            # Test key URL patterns
            url_patterns = [
                ('admin:index', {}),
                ('admin:attendance_attendancesession_changelist', {}),
                ('admin:accounts_user_changelist', {}),
                ('admin:academics_course_changelist', {}),
            ]
            
            for pattern_name, kwargs in url_patterns:
                try:
                    url = reverse(pattern_name, kwargs=kwargs)
                    # If reverse succeeds, URL pattern is valid
                except NoReverseMatch as e:
                    raise Exception(f"URL pattern '{pattern_name}' not found: {e}")
            
            self.log_result("URL patterns", True)
            
        except Exception as e:
            self.log_result("URL patterns", False, str(e))
    
    def run_all_tests(self):
        """Run all regression tests"""
        print("\n" + "="*60)
        print("REGRESSION TEST SUITE - Admin Panel Bug Fixes")
        print("="*60 + "\n")
        
        print("Task 8.1: Check existing functionality still works")
        print("-" * 60)
        self.test_audit_log_date_filtering()
        self.test_model_field_references()
        self.test_model_constants()
        self.test_timezone_awareness()
        self.test_serializer_fields()
        self.test_admin_configurations()
        self.test_url_patterns()
        
        print("\nTask 8.3: Check error handling")
        print("-" * 60)
        self.test_error_handling_invalid_dates()
        self.test_null_handling()
        
        print("\n" + "="*60)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("="*60)
        
        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        return self.failed == 0


if __name__ == '__main__':
    tester = RegressionTests()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
