# Course and Enrollment Management Implementation

## Overview
This document describes the implementation of course and enrollment management functionality for the Smart Attendance Web System.

## Implemented Components

### 1. Serializers (apps/academics/serializers.py)

#### CourseSerializer
- **Fields**: institution_id, code, title, department_id, instructor_id
- **Validations**:
  - Validates instructor exists and has teacher role (Requirement 6.4)
  - Validates institution matches instructor's institution
  - Provides read-only fields for institution_name, instructor_name, instructor_email
- **Requirements Addressed**: 6.1, 6.2, 6.5

#### EnrollmentSerializer
- **Fields**: student_id, course_id, active
- **Validations**:
  - Validates student exists and has student role (Requirement 6.2)
  - Validates course exists
  - Enforces unique constraint on (student_id, course_id) (Requirement 6.3)
- **Requirements Addressed**: 6.1, 6.2, 6.5

#### ScheduleSerializer
- **Fields**: course_id, weekday, start_time, duration_minutes, latitude, longitude, room
- **Validations**:
  - Validates course exists
  - Validates weekday is in range 0-6
  - Validates duration is positive
  - Validates latitude/longitude ranges
  - Checks for invalid coordinates (0, 0)
  - Converts lat/lon to PostGIS Point geometry
- **Requirements Addressed**: 6.1, 6.2, 6.5

### 2. Views (apps/academics/views.py)

#### AdminCourseViewSet
- **Endpoints**:
  - POST /api/academics/admin/courses/ - Create course (Requirement 6.1)
  - GET /api/academics/admin/courses/ - List courses
  - GET /api/academics/admin/courses/:id/ - Retrieve course
  - PUT/PATCH /api/academics/admin/courses/:id/ - Update course
  - DELETE /api/academics/admin/courses/:id/ - Delete course
- **Features**:
  - IsAdmin permission required
  - Institution-based data isolation
  - Filtering by instructor_id and department_id
  - Audit logging for all operations
  - Validates teacher role when assigning instructor (Requirement 6.4)

#### AdminEnrollmentViewSet
- **Endpoints**:
  - POST /api/academics/admin/enrollments/ - Create enrollment (Requirement 6.2)
  - GET /api/academics/admin/enrollments/ - List enrollments
  - GET /api/academics/admin/enrollments/:id/ - Retrieve enrollment
  - PUT/PATCH /api/academics/admin/enrollments/:id/ - Update enrollment
  - DELETE /api/academics/admin/enrollments/:id/ - Delete enrollment
- **Features**:
  - IsAdmin permission required
  - Institution-based data isolation
  - Filtering by course_id, student_id, and active status
  - Audit logging for all operations
  - Validates student role when creating enrollment (Requirement 6.2)
  - Enforces unique constraint on (student_id, course_id) (Requirement 6.3)

#### AdminScheduleViewSet
- **Endpoints**:
  - POST /api/academics/admin/schedules/ - Create schedule
  - GET /api/academics/admin/schedules/ - List schedules
  - GET /api/academics/admin/schedules/:id/ - Retrieve schedule
  - PUT/PATCH /api/academics/admin/schedules/:id/ - Update schedule (Requirement 6.5)
  - DELETE /api/academics/admin/schedules/:id/ - Delete schedule
- **Features**:
  - IsAdmin permission required
  - Institution-based data isolation
  - Filtering by course_id and weekday
  - Audit logging for all operations
  - Handles geospatial location data

### 3. URL Configuration (apps/academics/urls.py)

All endpoints are properly wired up with appropriate HTTP methods:
- List/Create: GET and POST on collection endpoints
- Retrieve/Update/Delete: GET, PUT, PATCH, DELETE on detail endpoints

## Requirements Coverage

### Requirement 6.1: Course Creation
✅ Implemented POST /api/admin/courses endpoint with IsAdmin permission
✅ Requires course code, title, and instructor assignment
✅ Validates instructor has teacher role

### Requirement 6.2: Student Enrollment
✅ Implemented POST /api/admin/enrollments endpoint with IsAdmin permission
✅ Validates student user has student role
✅ Creates enrollment linking student to course

### Requirement 6.3: Unique Enrollment Constraint
✅ Enforces unique constraint preventing duplicate enrollments
✅ Validation in serializer raises error for duplicate (student_id, course_id)

### Requirement 6.4: Teacher Assignment Validation
✅ Validates user has teacher role when assigning instructor to course
✅ Validation occurs in CourseSerializer.validate_instructor_id()

### Requirement 6.5: Schedule Management
✅ Implemented PATCH /api/admin/schedules/:id endpoint with IsAdmin permission
✅ Requires weekday, start time, duration, and location coordinates
✅ Handles PostGIS Point geometry for location storage

## Security Features

1. **Permission Control**: All endpoints require IsAdmin permission
2. **Data Isolation**: All queries filter by user's institution
3. **Audit Logging**: All create, update, and delete operations are logged
4. **Input Validation**: Comprehensive validation in serializers
5. **Role Validation**: Enforces role requirements for instructors and students

## API Examples

### Create Course
```http
POST /api/academics/admin/courses/
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "code": "CS101",
  "title": "Introduction to Computer Science",
  "department_id": "CS",
  "instructor_id": 5
}
```

### Create Enrollment
```http
POST /api/academics/admin/enrollments/
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "student_id": 10,
  "course_id": 3,
  "active": true
}
```

### Update Schedule
```http
PATCH /api/academics/admin/schedules/7/
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "weekday": 1,
  "start_time": "10:00:00",
  "duration_minutes": 90,
  "latitude": 40.7128,
  "longitude": -74.0060,
  "room": "Room 301"
}
```

## Testing Notes

The implementation follows Django REST Framework best practices and includes:
- Proper serializer validation
- ViewSet-based CRUD operations
- Pagination support (50 items per page)
- Filtering capabilities
- Comprehensive error handling
- Audit trail for all operations

To test the endpoints, ensure:
1. PostgreSQL with PostGIS extension is running
2. Database migrations are applied
3. Test users with appropriate roles exist
4. JWT authentication is configured
