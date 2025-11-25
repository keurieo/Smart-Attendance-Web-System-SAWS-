# Requirements Document

## Introduction

This document outlines the requirements for fixing critical bugs in the Django Admin Panel that are preventing proper functionality. These bugs include incorrect model references, missing fields in serializers, broken date filtering, and template variable errors that cause the admin panel to fail loading or display incorrect data.

## Glossary

- **Admin Panel**: The Django administrative interface at `/admin/` used by administrators to manage system data
- **Audit Log**: System records tracking all user actions and system events
- **Serializer**: Django REST Framework component that converts model instances to JSON format
- **Date Filter**: Query parameter that filters records based on date ranges
- **Dashboard Metrics**: Key performance indicators displayed on the admin dashboard
- **Template Variable**: Dynamic data placeholder in Django templates
- **Model Reference**: Python code that accesses Django model classes and their fields

## Requirements

### Requirement 1

**User Story:** As an administrator, I want the audit log API to handle system-generated actions without errors, so that I can view all audit logs including those without a specific user.

#### Acceptance Criteria

1. WHEN the audit log API returns a record with null performed_by field, THE Admin Panel SHALL include a performed_by_email field in the response
2. IF performed_by is null, THEN THE Admin Panel SHALL set performed_by_email to null or "System"
3. THE Admin Panel SHALL serialize audit log records without raising KeyError for performed_by_email
4. WHEN displaying audit logs in the UI, THE Admin Panel SHALL show "System" for records with null performed_by
5. THE Admin Panel SHALL pass the test_audit_log_with_null_performed_by test case

### Requirement 2

**User Story:** As an administrator, I want to filter audit logs by date ranges accurately, so that I can find specific records from particular time periods.

#### Acceptance Criteria

1. WHEN filtering audit logs with date_from parameter, THE Admin Panel SHALL return only records created on or after that date
2. WHEN filtering audit logs with date_to parameter, THE Admin Panel SHALL return only records created on or before that date
3. WHEN filtering with both date_from and date_to, THE Admin Panel SHALL return records within the inclusive date range
4. THE Admin Panel SHALL parse date strings in ISO format (YYYY-MM-DD) correctly
5. THE Admin Panel SHALL handle timezone conversions properly when comparing dates

### Requirement 3

**User Story:** As an administrator, I want the dashboard to load without errors, so that I can access the admin panel and view system metrics.

#### Acceptance Criteria

1. WHEN accessing /admin/, THE Admin Panel SHALL load the dashboard without NoReverseMatch errors
2. THE Admin Panel SHALL use correct URL names for all admin model links (admin:attendance_attendancesession_changelist)
3. WHEN rendering templates, THE Admin Panel SHALL reference only existing model fields
4. THE Admin Panel SHALL use correct field names for User model (full_name, email, created_at, role.name)
5. THE Admin Panel SHALL use correct field names for AttendanceSession model (title, created_by, status)

### Requirement 4

**User Story:** As an administrator, I want dashboard metrics to display accurate data, so that I can monitor system health and usage.

#### Acceptance Criteria

1. THE Admin Panel SHALL query AttendanceSession model (not Session) for active sessions count
2. WHEN counting active sessions, THE Admin Panel SHALL filter by status=AttendanceSession.ACTIVE
3. THE Admin Panel SHALL use end_at field (not expires_at) for session expiration checks
4. WHEN counting attendance records, THE Admin Panel SHALL use status=AttendanceRecord.PRESENT
5. THE Admin Panel SHALL use created_by field (not teacher) in select_related queries

### Requirement 5

**User Story:** As an administrator, I want all admin forms to display correct fields, so that I can edit records without encountering field errors.

#### Acceptance Criteria

1. WHEN displaying AttendanceSession admin form, THE Admin Panel SHALL use teacher_location field (not location)
2. THE Admin Panel SHALL reference only fields that exist in the model definition
3. WHEN saving forms, THE Admin Panel SHALL validate against actual model fields
4. THE Admin Panel SHALL display field errors for invalid data
5. THE Admin Panel SHALL successfully save valid form data without field name errors

### Requirement 6

**User Story:** As an administrator, I want template variables to reference correct model attributes, so that the admin interface displays accurate information.

#### Acceptance Criteria

1. WHEN displaying user information, THE Admin Panel SHALL use user.full_name (not user.first_name)
2. WHEN displaying user email, THE Admin Panel SHALL use user.email (not user.username)
3. WHEN displaying course information, THE Admin Panel SHALL use course.title (not course.name)
4. WHEN checking user role, THE Admin Panel SHALL use user.role.name == 'admin' (not user.role == 'ADMIN')
5. WHEN displaying role name, THE Admin Panel SHALL use user.role.get_name_display() method

### Requirement 7

**User Story:** As an administrator, I want the admin panel to handle missing context data gracefully, so that pages load even when optional data is unavailable.

#### Acceptance Criteria

1. WHEN metrics data is not available, THE Admin Panel SHALL check for metrics existence before rendering
2. THE Admin Panel SHALL wrap metrics display in {% if metrics %} template conditional
3. WHEN accessing recent sessions, THE Admin Panel SHALL use metrics.recent_sessions (not recent_sessions)
4. WHEN accessing recent users, THE Admin Panel SHALL use metrics.recent_users (not recent_users)
5. THE Admin Panel SHALL display empty state message when metrics are unavailable

### Requirement 8

**User Story:** As an administrator, I want date filtering to work correctly with timezone awareness, so that I can filter records accurately regardless of server timezone.

#### Acceptance Criteria

1. THE Admin Panel SHALL convert date filter strings to timezone-aware datetime objects
2. WHEN comparing dates, THE Admin Panel SHALL use the same timezone for all comparisons
3. THE Admin Panel SHALL use inclusive comparison operators (>= and <=) for date ranges
4. WHEN date_from is provided, THE Admin Panel SHALL set time to 00:00:00 of that day
5. WHEN date_to is provided, THE Admin Panel SHALL set time to 23:59:59 of that day

### Requirement 9

**User Story:** As an administrator, I want all test cases to pass, so that I can be confident the admin panel works correctly.

#### Acceptance Criteria

1. THE Admin Panel SHALL pass test_audit_log_with_null_performed_by test
2. THE Admin Panel SHALL pass test_filter_by_date_from test with correct record count
3. THE Admin Panel SHALL pass test_filter_by_date_range test with correct record count
4. THE Admin Panel SHALL pass test_filter_by_date_to test with correct record count
5. WHEN running full test suite, THE Admin Panel SHALL achieve 100% test pass rate

### Requirement 10

**User Story:** As an administrator, I want Python cache to be cleared after fixes, so that changes take effect immediately.

#### Acceptance Criteria

1. WHEN code changes are deployed, THE Admin Panel SHALL clear all __pycache__ directories
2. THE Admin Panel SHALL delete all .pyc bytecode files
3. WHEN using Docker, THE Admin Panel SHALL restart backend container after code changes
4. THE Admin Panel SHALL reload Django server to pick up template changes
5. WHEN accessing admin after fixes, THE Admin Panel SHALL use updated code without cached errors
