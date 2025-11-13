# Database Models Implementation Summary

This document summarizes the database models implemented for the Smart Attendance System.

## Completed Tasks

✅ Task 2.1: Core Authentication Models
✅ Task 2.2: Academic Models  
✅ Task 2.3: Attendance Models
✅ Task 2.4: Audit and Tracking Models

## Models Implemented

### Accounts App (`apps/accounts/models.py`)

1. **Institution**
   - Fields: name, timezone, created_at, updated_at
   - Represents educational institutions

2. **Role**
   - Fields: name (admin/teacher/student), created_at
   - Defines user roles with choices

3. **User** (Custom User Model)
   - Extends: AbstractBaseUser, PermissionsMixin
   - Fields: email (unique), full_name, role (FK), institution (FK), is_active, is_staff, created_at, updated_at, last_login
   - Custom manager: UserManager with create_user and create_superuser methods
   - USERNAME_FIELD: email
   - Indexes: email, role

4. **TeacherProfile**
   - Fields: user (OneToOne), employee_id (unique), department_id, office_location (PointField), created_at, updated_at
   - Extended profile for teachers

5. **StudentProfile**
   - Fields: user (OneToOne), roll_number (unique), enrollment_year, department_id, created_at, updated_at
   - Extended profile for students

### Academics App (`apps/academics/models.py`)

1. **Course**
   - Fields: institution (FK), code, title, department_id, instructor (FK to User), created_at, updated_at
   - Unique constraint: (institution, code)
   - Indexes: (institution, code), instructor

2. **Enrollment**
   - Fields: student (FK to User), course (FK), active, enrolled_at, updated_at
   - Unique constraint: (student, course)
   - Indexes: (student, course), (course, active)

3. **Schedule**
   - Fields: course (FK), weekday (choices 0-6), start_time, duration_minutes, location (PointField), room, created_at, updated_at
   - Indexes: (course, weekday)

### Attendance App (`apps/attendance/models.py`)

1. **AttendanceSession**
   - Fields: course (FK), schedule (FK, nullable), created_by (FK to User), start_at, end_at, teacher_location (PointField), radius_meters (10-500), status (active/expired/cancelled), notes, created_at, updated_at
   - Validators: MinValueValidator(10), MaxValueValidator(500) on radius_meters
   - Indexes: (course, start_at), created_by, status

2. **QRToken**
   - Fields: session (FK), token (unique), code6, created_at, expires_at, is_revoked
   - Indexes: token, session, code6

3. **AttendanceRecord**
   - Fields: session (FK), student (FK to User), marked_at, method (qr_scan/manual_code/admin_override), token (FK, nullable), student_location (PointField, nullable), distance_meters, status (present/absent/rejected/pending), reason, flagged_for_review, updated_at
   - Unique constraint: (session, student)
   - Indexes: (session, student), (student, marked_at), status, flagged_for_review

### Audit App (`apps/audit/models.py`)

1. **AuditLog**
   - Fields: performed_by (FK to User, nullable), action, target_table, target_id, old_data (JSONField), new_data (JSONField), performed_at
   - Indexes: (performed_by, performed_at), (target_table, target_id), action, performed_at
   - Ordering: -performed_at

2. **LocationSnapshot**
   - Fields: user (FK), recorded_at, location (PointField), source (browser_geolocation/gps/manual), accuracy
   - Indexes: (user, recorded_at), recorded_at
   - Ordering: -recorded_at

3. **Device**
   - Fields: user (FK), device_id (unique), device_info (JSONField), last_seen, created_at
   - Indexes: user, device_id, last_seen

## Migrations Created

All migrations have been created in the respective app migration directories:

- `backend/apps/accounts/migrations/0001_initial.py`
- `backend/apps/academics/migrations/0001_initial.py`
- `backend/apps/attendance/migrations/0001_initial.py`
- `backend/apps/audit/migrations/0001_initial.py`

## Admin Registrations

All models have been registered in Django admin with appropriate configurations:

- `backend/apps/accounts/admin.py` - Institution, Role, User, TeacherProfile, StudentProfile
- `backend/apps/academics/admin.py` - Course, Enrollment, Schedule
- `backend/apps/attendance/admin.py` - AttendanceSession, QRToken, AttendanceRecord
- `backend/apps/audit/admin.py` - AuditLog, LocationSnapshot, Device

## Key Features

### Geospatial Support
- Uses PostGIS PointField with geography=True for location storage
- Fields: office_location, location (Schedule), teacher_location, student_location, location (LocationSnapshot)
- All coordinates stored in WGS84 (SRID 4326)

### Validation
- Email uniqueness on User model
- Radius validation (10-500 meters) on AttendanceSession
- Unique constraints on critical relationships (enrollment, attendance records)

### Audit Trail
- Comprehensive audit logging with old_data and new_data JSON fields
- Location snapshots for all geolocation captures
- Device tracking for attendance submissions

### Indexes
- Strategic indexes on frequently queried fields
- Composite indexes for common query patterns
- Unique indexes for business constraints

## Next Steps

To apply these migrations to the database:

1. Ensure PostgreSQL with PostGIS is running
2. Ensure Redis is running
3. Set up Python virtual environment and install dependencies:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate  # On Windows
   pip install -r requirements/development.txt
   ```

4. Configure environment variables in `.env` file

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create initial roles:
   ```bash
   python manage.py shell
   >>> from apps.accounts.models import Role
   >>> Role.objects.create(name='admin')
   >>> Role.objects.create(name='teacher')
   >>> Role.objects.create(name='student')
   ```

7. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Requirements Satisfied

This implementation satisfies the following requirements from the requirements document:

- **Requirement 1.1, 1.2**: User authentication with roles (admin, teacher, student)
- **Requirement 5.1, 5.2**: User management with email, password, full_name, role
- **Requirement 13.1, 13.4**: Multi-institution support with timezone configuration
- **Requirement 6.1-6.5**: Course and enrollment management
- **Requirement 2.1-2.6**: Attendance session creation with QR tokens
- **Requirement 3.1-3.7**: Attendance marking with geolocation validation
- **Requirement 10.1-10.5**: Comprehensive audit logging
- **Requirement 14.1-14.5**: Device tracking
- **Requirement 15.1-15.5**: Location snapshot logging

## Design Compliance

All models follow the design specifications in `.kiro/specs/smart-attendance-system/design.md`:

- Custom User model extending AbstractBaseUser
- PostGIS geography fields for geospatial data
- Appropriate foreign key relationships
- Comprehensive indexing strategy
- JSON fields for flexible data storage (audit logs, device info)
- Proper validation and constraints
