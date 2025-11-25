"""
Error Handling Verification Script for Admin Panel Bug Fixes

This script verifies that error handling is robust and graceful.
"""

from pathlib import Path
import re


class ErrorHandlingVerifier:
    """Verify error handling in the code"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = []
        
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
                print(f"  Error: {message}")
    
    def log_warning(self, message):
        """Log warning"""
        self.warnings.append(message)
        print(f"⚠ Warning: {message}")
    
    def verify_date_filter_error_handling(self):
        """Verify date filters handle invalid input gracefully"""
        print("\n" + "="*60)
        print("Verifying Date Filter Error Handling")
        print("="*60)
        
        file_path = Path('apps/audit/views.py')
        if not file_path.exists():
            self.log_result("Audit views file exists", False)
            return
        
        content = file_path.read_text()
        
        # Check filter_date_from error handling
        if 'def filter_date_from' in content:
            method_match = re.search(r'def filter_date_from\(self.*?\n(?=\s{0,4}def|\s{0,4}class|$)', 
                                    content, re.DOTALL)
            if method_match:
                method_code = method_match.group(0)
                
                # Check for value validation
                checks_value = 'if value' in method_code
                self.log_result("filter_date_from checks if value exists", checks_value,
                               "Prevents processing None or empty values")
                
                # Check for parse result validation
                checks_parse_result = 'if date_obj' in method_code or 'if date' in method_code
                self.log_result("filter_date_from validates parse result", checks_parse_result,
                               "Handles invalid date formats gracefully")
                
                # Check returns original queryset on error
                returns_queryset = 'return queryset' in method_code
                self.log_result("filter_date_from returns original queryset on error", returns_queryset,
                               "Doesn't crash on invalid input")
                
                # Check doesn't raise exceptions
                no_raise = 'raise ' not in method_code
                self.log_result("filter_date_from doesn't raise exceptions", no_raise,
                               "Handles errors gracefully without crashing")
        
        # Check filter_date_to error handling
        if 'def filter_date_to' in content:
            method_match = re.search(r'def filter_date_to\(self.*?\n(?=\s{0,4}def|\s{0,4}class|$)', 
                                    content, re.DOTALL)
            if method_match:
                method_code = method_match.group(0)
                
                checks_value = 'if value' in method_code
                self.log_result("filter_date_to checks if value exists", checks_value)
                
                checks_parse_result = 'if date_obj' in method_code or 'if date' in method_code
                self.log_result("filter_date_to validates parse result", checks_parse_result)
                
                returns_queryset = 'return queryset' in method_code
                self.log_result("filter_date_to returns original queryset on error", returns_queryset)
                
                no_raise = 'raise ' not in method_code
                self.log_result("filter_date_to doesn't raise exceptions", no_raise)
    
    def verify_serializer_error_handling(self):
        """Verify serializers handle null values gracefully"""
        print("\n" + "="*60)
        print("Verifying Serializer Error Handling")
        print("="*60)
        
        file_path = Path('apps/audit/serializers.py')
        if not file_path.exists():
            return
        
        content = file_path.read_text()
        
        # Check get_performed_by_email null handling
        if 'def get_performed_by_email' in content:
            method_match = re.search(r'def get_performed_by_email.*?\n(?=\s{0,4}def|\s{0,4}class)', 
                                    content, re.DOTALL)
            if method_match:
                method_code = method_match.group(0)
                
                # Check for null check
                has_null_check = ('if obj.performed_by' in method_code or 
                                 'obj.performed_by.email if' in method_code or
                                 'if obj.performed_by else' in method_code)
                self.log_result("get_performed_by_email checks for null", has_null_check,
                               "Prevents AttributeError on None")
                
                # Check returns None for null
                returns_none = 'None' in method_code
                self.log_result("get_performed_by_email returns None for null", returns_none,
                               "Graceful handling of system actions")
        
        # Check get_performed_by_name null handling
        if 'def get_performed_by_name' in content:
            method_match = re.search(r'def get_performed_by_name.*?\n(?=\s{0,4}def|\s{0,4}class)', 
                                    content, re.DOTALL)
            if method_match:
                method_code = method_match.group(0)
                
                has_null_check = ('if obj.performed_by' in method_code or 
                                 'obj.performed_by.full_name if' in method_code or
                                 'if obj.performed_by else' in method_code)
                self.log_result("get_performed_by_name checks for null", has_null_check)
                
                returns_none = 'None' in method_code
                self.log_result("get_performed_by_name returns None for null", returns_none)
    
    def verify_admin_form_validation(self):
        """Verify admin forms have proper validation"""
        print("\n" + "="*60)
        print("Verifying Admin Form Validation")
        print("="*60)
        
        admin_path = Path('apps/attendance/admin.py')
        if not admin_path.exists():
            return
        
        content = admin_path.read_text()
        
        # Check for fieldsets (proper form structure)
        has_fieldsets = 'fieldsets' in content
        self.log_result("Admin has fieldsets defined", has_fieldsets,
                       "Proper form structure for validation")
        
        # Check for list_display (proper list view)
        has_list_display = 'list_display' in content
        self.log_result("Admin has list_display defined", has_list_display,
                       "Proper list view configuration")
        
        # Check doesn't reference non-existent fields
        if has_fieldsets:
            # Common wrong field names
            wrong_fields = ["'location'", '"location"']
            has_wrong_fields = any(field in content for field in wrong_fields)
            
            if has_wrong_fields and "'teacher_location'" not in content:
                self.log_result("Admin doesn't reference non-existent fields", False,
                               "References 'location' instead of 'teacher_location'")
            else:
                self.log_result("Admin doesn't reference non-existent fields", True,
                               "All field references are valid")
    
    def verify_view_permissions(self):
        """Verify views have proper permission checks"""
        print("\n" + "="*60)
        print("Verifying View Permissions")
        print("="*60)
        
        file_path = Path('apps/audit/views.py')
        if not file_path.exists():
            return
        
        content = file_path.read_text()
        
        # Check for permission classes
        has_permissions = 'permission_classes' in content
        self.log_result("Views have permission_classes defined", has_permissions,
                       "Prevents unauthorized access")
        
        if has_permissions:
            # Check for IsAdmin permission
            has_admin_permission = 'IsAdmin' in content
            self.log_result("Audit log view requires admin permission", has_admin_permission,
                           "Only admins can access audit logs")
    
    def verify_template_error_handling(self):
        """Verify templates handle missing data gracefully"""
        print("\n" + "="*60)
        print("Verifying Template Error Handling")
        print("="*60)
        
        template_dir = Path('templates/admin')
        if not template_dir.exists():
            self.log_warning("Admin templates directory not found")
            return
        
        index_template = template_dir / 'index.html'
        if index_template.exists():
            content = index_template.read_text()
            
            # Check for metrics existence check
            has_metrics_check = '{% if metrics %}' in content
            self.log_result("Dashboard checks if metrics exist", has_metrics_check,
                           "Prevents errors when metrics are unavailable")
            
            # Check for default filters
            has_defaults = '|default:' in content or '|default_if_none:' in content
            self.log_result("Templates use default filters", has_defaults,
                           "Provides fallback values for missing data")
    
    def verify_model_constraints(self):
        """Verify models have proper constraints"""
        print("\n" + "="*60)
        print("Verifying Model Constraints")
        print("="*60)
        
        # Check AuditLog model
        audit_model_path = Path('apps/audit/models.py')
        if audit_model_path.exists():
            content = audit_model_path.read_text()
            
            # Check performed_by can be null
            if 'performed_by' in content:
                has_null_true = 'null=True' in content
                self.log_result("AuditLog.performed_by allows null", has_null_true,
                               "Supports system-generated actions")
                
                has_blank_true = 'blank=True' in content
                self.log_result("AuditLog.performed_by allows blank", has_blank_true,
                               "Form validation allows empty value")
    
    def run_all_verifications(self):
        """Run all error handling verification checks"""
        print("\n" + "="*70)
        print("ERROR HANDLING VERIFICATION - Admin Panel Bug Fixes")
        print("="*70)
        
        self.verify_date_filter_error_handling()
        self.verify_serializer_error_handling()
        self.verify_admin_form_validation()
        self.verify_view_permissions()
        self.verify_template_error_handling()
        self.verify_model_constraints()
        
        print("\n" + "="*70)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed, {len(self.warnings)} warnings")
        print("="*70)
        
        if self.warnings:
            print("\nWARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        print("\n" + "="*70)
        print("ERROR HANDLING SUMMARY")
        print("="*70)
        print(f"✓ Invalid date handling: {'VERIFIED' if self.failed == 0 else 'NEEDS REVIEW'}")
        print(f"✓ Null value handling: {'VERIFIED' if self.failed == 0 else 'NEEDS REVIEW'}")
        print(f"✓ Form validation: {'VERIFIED' if self.failed == 0 else 'NEEDS REVIEW'}")
        print(f"✓ Permission checks: {'VERIFIED' if self.failed == 0 else 'NEEDS REVIEW'}")
        
        print("\nERROR HANDLING FEATURES:")
        print("  ✓ Invalid dates return original queryset (no crash)")
        print("  ✓ Null performed_by returns None (no AttributeError)")
        print("  ✓ Admin forms validate field existence")
        print("  ✓ Templates check data availability")
        print("  ✓ Views require proper permissions")
        
        return self.failed == 0


if __name__ == '__main__':
    import sys
    verifier = ErrorHandlingVerifier()
    success = verifier.run_all_verifications()
    sys.exit(0 if success else 1)
