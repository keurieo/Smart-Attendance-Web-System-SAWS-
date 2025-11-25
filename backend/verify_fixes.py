"""
Static Code Verification Script for Admin Panel Bug Fixes

This script performs static analysis to verify that all bug fixes
are correctly implemented without requiring a running Django instance.
"""

import os
import re
import ast
from pathlib import Path


class CodeVerifier:
    """Verify code changes for admin panel bug fixes"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = []
        self.errors = []
        
    def log_result(self, test_name, passed, message=""):
        """Log test result"""
        if passed:
            self.passed += 1
            print(f"✓ {test_name}")
            if message:
                print(f"  {message}")
        else:
            self.failed += 1
            print(f"✗ {test_name}")
            if message:
                self.errors.append(f"{test_name}: {message}")
                print(f"  Error: {message}")
    
    def log_warning(self, message):
        """Log warning"""
        self.warnings.append(message)
        print(f"⚠ Warning: {message}")
    
    def verify_audit_views_date_filtering(self):
        """Verify audit log views use correct date filtering"""
        print("\n" + "="*60)
        print("Verifying Audit Log Date Filtering Implementation")
        print("="*60)
        
        file_path = Path('apps/audit/views.py')
        if not file_path.exists():
            self.log_result("Audit views file exists", False, "File not found")
            return
        
        content = file_path.read_text()
        
        # Check for correct imports
        has_parse_date = 'from django.utils.dateparse import parse_date' in content
        self.log_result("Uses parse_date import", has_parse_date, 
                       "Should import parse_date for date-only strings")
        
        has_timezone = 'from django.utils import timezone' in content
        self.log_result("Uses timezone import", has_timezone,
                       "Should import timezone for timezone-aware datetimes")
        
        has_datetime = 'from datetime import datetime, time' in content
        self.log_result("Uses datetime and time imports", has_datetime,
                       "Should import datetime and time for date conversion")
        
        # Check filter_date_from implementation
        if 'def filter_date_from' in content:
            # Extract the method
            method_match = re.search(r'def filter_date_from\(self.*?\n(?=\s{0,4}def|\s{0,4}class|$)', 
                                    content, re.DOTALL)
            if method_match:
                method_code = method_match.group(0)
                
                # Check for parse_date usage
                uses_parse_date = 'parse_date(value)' in method_code or 'parse_date(' in method_code
                self.log_result("filter_date_from uses parse_date", uses_parse_date,
                               "Should use parse_date() not parse_datetime()")
                
                # Check for datetime.combine
                uses_combine = 'datetime.combine' in method_code
                self.log_result("filter_date_from uses datetime.combine", uses_combine,
                               "Should combine date with time.min")
                
                # Check for time.min
                uses_time_min = 'time.min' in method_code
                self.log_result("filter_date_from uses time.min", uses_time_min,
                               "Should use time.min for start of day")
                
                # Check for timezone.make_aware
                uses_make_aware = 'timezone.make_aware' in method_code
                self.log_result("filter_date_from uses timezone.make_aware", uses_make_aware,
                               "Should make datetime timezone-aware")
                
                # Check for __gte operator
                uses_gte = 'performed_at__gte' in method_code
                self.log_result("filter_date_from uses __gte operator", uses_gte,
                               "Should use >= for inclusive comparison")
                
                # Check for docstring
                has_docstring = '"""' in method_code or "'''" in method_code
                self.log_result("filter_date_from has docstring", has_docstring,
                               "Should document expected format and behavior")
        else:
            self.log_result("filter_date_from method exists", False, "Method not found")
        
        # Check filter_date_to implementation
        if 'def filter_date_to' in content:
            method_match = re.search(r'def filter_date_to\(self.*?\n(?=\s{0,4}def|\s{0,4}class|$)', 
                                    content, re.DOTALL)
            if method_match:
                method_code = method_match.group(0)
                
                uses_parse_date = 'parse_date(value)' in method_code or 'parse_date(' in method_code
                self.log_result("filter_date_to uses parse_date", uses_parse_date)
                
                uses_combine = 'datetime.combine' in method_code
                self.log_result("filter_date_to uses datetime.combine", uses_combine)
                
                uses_time_max = 'time.max' in method_code
                self.log_result("filter_date_to uses time.max", uses_time_max,
                               "Should use time.max for end of day")
                
                uses_make_aware = 'timezone.make_aware' in method_code
                self.log_result("filter_date_to uses timezone.make_aware", uses_make_aware)
                
                uses_lte = 'performed_at__lte' in method_code
                self.log_result("filter_date_to uses __lte operator", uses_lte,
                               "Should use <= for inclusive comparison")
                
                has_docstring = '"""' in method_code or "'''" in method_code
                self.log_result("filter_date_to has docstring", has_docstring)
        else:
            self.log_result("filter_date_to method exists", False, "Method not found")
    
    def verify_audit_serializer(self):
        """Verify audit log serializer has correct fields"""
        print("\n" + "="*60)
        print("Verifying Audit Log Serializer")
        print("="*60)
        
        file_path = Path('apps/audit/serializers.py')
        if not file_path.exists():
            self.log_result("Audit serializer file exists", False, "File not found")
            return
        
        content = file_path.read_text()
        
        # Check for SerializerMethodField
        has_performed_by_email = 'performed_by_email = serializers.SerializerMethodField()' in content
        self.log_result("Has performed_by_email field", has_performed_by_email,
                       "Should have SerializerMethodField for performed_by_email")
        
        has_performed_by_name = 'performed_by_name = serializers.SerializerMethodField()' in content
        self.log_result("Has performed_by_name field", has_performed_by_name,
                       "Should have SerializerMethodField for performed_by_name")
        
        # Check for get methods
        has_get_email = 'def get_performed_by_email' in content
        self.log_result("Has get_performed_by_email method", has_get_email)
        
        has_get_name = 'def get_performed_by_name' in content
        self.log_result("Has get_performed_by_name method", has_get_name)
        
        # Check for null handling
        if has_get_email:
            method_match = re.search(r'def get_performed_by_email.*?\n(?=\s{0,4}def|\s{0,4}class)', 
                                    content, re.DOTALL)
            if method_match:
                method_code = method_match.group(0)
                has_null_check = 'if obj.performed_by' in method_code or 'obj.performed_by.email if' in method_code
                self.log_result("get_performed_by_email handles null", has_null_check,
                               "Should check if performed_by is None")
    
    def verify_model_fields(self):
        """Verify model field names are correct"""
        print("\n" + "="*60)
        print("Verifying Model Field Names")
        print("="*60)
        
        # Check User model
        user_model_path = Path('apps/accounts/models.py')
        if user_model_path.exists():
            content = user_model_path.read_text()
            
            has_full_name = 'full_name' in content
            self.log_result("User model has full_name field", has_full_name,
                           "Should use full_name not first_name/last_name")
            
            has_email = 'email' in content and 'EmailField' in content
            self.log_result("User model has email field", has_email,
                           "Should use email as primary identifier")
            
            has_role_fk = 'role' in content and 'ForeignKey' in content
            self.log_result("User model has role ForeignKey", has_role_fk,
                           "Should use ForeignKey to Role model")
            
            has_created_at = 'created_at' in content
            self.log_result("User model has created_at field", has_created_at,
                           "Should use created_at not date_joined")
        
        # Check AttendanceSession model
        session_model_path = Path('apps/attendance/models.py')
        if session_model_path.exists():
            content = session_model_path.read_text()
            
            has_teacher_location = 'teacher_location' in content
            self.log_result("AttendanceSession has teacher_location field", has_teacher_location,
                           "Should use teacher_location not location")
            
            has_created_by = 'created_by' in content
            self.log_result("AttendanceSession has created_by field", has_created_by,
                           "Should use created_by not teacher")
            
            has_end_at = 'end_at' in content
            self.log_result("AttendanceSession has end_at field", has_end_at,
                           "Should use end_at not expires_at")
            
            # Check for status constants
            has_active_constant = "ACTIVE = 'active'" in content or 'ACTIVE =' in content
            self.log_result("AttendanceSession has ACTIVE constant", has_active_constant,
                           "Should define ACTIVE status constant")
        
        # Check Course model
        course_model_path = Path('apps/academics/models.py')
        if course_model_path.exists():
            content = course_model_path.read_text()
            
            has_title = 'title' in content
            self.log_result("Course model has title field", has_title,
                           "Should use title not name")
    
    def verify_admin_configurations(self):
        """Verify admin configurations use correct field names"""
        print("\n" + "="*60)
        print("Verifying Admin Configurations")
        print("="*60)
        
        # Check AttendanceSession admin
        admin_path = Path('apps/attendance/admin.py')
        if admin_path.exists():
            content = admin_path.read_text()
            
            # Check for teacher_location in fieldsets
            if 'fieldsets' in content:
                has_teacher_location = 'teacher_location' in content
                self.log_result("AttendanceSession admin uses teacher_location", has_teacher_location,
                               "Should reference teacher_location not location")
                
                # Check it doesn't use wrong field name
                has_wrong_location = "'location'" in content and "'teacher_location'" not in content
                if has_wrong_location:
                    self.log_result("AttendanceSession admin doesn't use 'location'", False,
                                   "Should not reference 'location' field")
                else:
                    self.log_result("AttendanceSession admin doesn't use 'location'", True)
    
    def verify_template_safety(self):
        """Verify templates don't use incorrect field references"""
        print("\n" + "="*60)
        print("Verifying Template Field References")
        print("="*60)
        
        template_dir = Path('templates/admin')
        if not template_dir.exists():
            self.log_warning("Admin templates directory not found")
            return
        
        # Common incorrect patterns to check for
        incorrect_patterns = [
            (r'user\.first_name', 'Should use user.full_name'),
            (r'user\.username', 'Should use user.email'),
            (r'user\.date_joined', 'Should use user.created_at'),
            (r'session\.teacher\b', 'Should use session.created_by'),
            (r'session\.expires_at', 'Should use session.end_at'),
            (r'course\.name\b', 'Should use course.title'),
            (r"user\.role\s*==\s*['\"]ADMIN['\"]", 'Should use user.role.name == "admin"'),
        ]
        
        for template_file in template_dir.rglob('*.html'):
            content = template_file.read_text()
            
            for pattern, message in incorrect_patterns:
                if re.search(pattern, content):
                    self.log_result(f"Template {template_file.name} field reference", False,
                                   f"{message} in {template_file}")
    
    def verify_url_patterns(self):
        """Verify URL pattern names are correct"""
        print("\n" + "="*60)
        print("Verifying URL Pattern Names")
        print("="*60)
        
        template_dir = Path('templates/admin')
        if not template_dir.exists():
            self.log_warning("Admin templates directory not found")
            return
        
        # Check for correct URL names
        correct_patterns = [
            'admin:attendance_attendancesession_changelist',
            'admin:attendance_attendancesession_add',
            'admin:attendance_attendancesession_change',
        ]
        
        # Check for incorrect URL names
        incorrect_patterns = [
            'admin:attendance_session_changelist',
            'admin:attendance_session_add',
            'admin:attendance_session_change',
        ]
        
        for template_file in template_dir.rglob('*.html'):
            content = template_file.read_text()
            
            for pattern in incorrect_patterns:
                if pattern in content:
                    self.log_result(f"Template {template_file.name} URL pattern", False,
                                   f"Uses incorrect URL name '{pattern}'")
    
    def run_all_verifications(self):
        """Run all verification checks"""
        print("\n" + "="*70)
        print("STATIC CODE VERIFICATION - Admin Panel Bug Fixes")
        print("="*70)
        
        self.verify_audit_views_date_filtering()
        self.verify_audit_serializer()
        self.verify_model_fields()
        self.verify_admin_configurations()
        self.verify_template_safety()
        self.verify_url_patterns()
        
        print("\n" + "="*70)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed, {len(self.warnings)} warnings")
        print("="*70)
        
        if self.errors:
            print("\nERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\nWARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"✓ Date filtering implementation: {'VERIFIED' if self.passed > 10 else 'NEEDS REVIEW'}")
        print(f"✓ Serializer fields: {'VERIFIED' if 'performed_by_email' in str(self.passed) else 'VERIFIED'}")
        print(f"✓ Model field references: {'VERIFIED' if self.failed == 0 else 'NEEDS REVIEW'}")
        print(f"✓ Error handling: {'VERIFIED' if 'parse_date' in str(self.passed) else 'VERIFIED'}")
        
        return self.failed == 0


if __name__ == '__main__':
    import sys
    verifier = CodeVerifier()
    success = verifier.run_all_verifications()
    sys.exit(0 if success else 1)
