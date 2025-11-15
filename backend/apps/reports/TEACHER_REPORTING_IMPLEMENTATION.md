# Teacher Reporting Implementation

## Overview

This document describes the implementation of the teacher reporting feature (Task 12) for the Smart Attendance System.

## Implemented Features

### 1. Attendance Report View (Task 12.1)

**Endpoint**: `GET /api/reports/attendance`

**Query Parameters**:
- `course_id` (required): ID of the course to generate report for
- `from_date` (optional): Start date in YYYY-MM-DD format
- `to_date` (optional): End date in YYYY-MM-DD format

**Permissions**: 
- User must be authenticated
- User must have Teacher role
- Teacher must be assigned to the specified course

**Functionality**:
- Validates that the teacher is assigned to the requested course
- Filters attendance records by course and optional date range
- Joins with student user data to include name and email
- Orders results by session start time and student name
- Supports both JSON and CSV output formats via content negotiation

**Response Formats**:
- **JSON**: Returns array of attendance record objects
- **CSV**: Returns CSV file with attendance data (via Accept: text/csv header or ?format=csv)

**Error Handling**:
- `VAL_001`: Missing or invalid parameters
- `BIZ_001`: Course not found or teacher not assigned to course
- `VAL_002`: Invalid date format

### 2. CSV Export Renderer (Task 12.2)

**Class**: `CSVAttendanceRenderer`

**Features**:
- Custom Django REST Framework renderer for CSV output
- Efficient streaming for large datasets (>1000 records)
- Uses Python's csv module with StringIO for memory efficiency

**CSV Columns**:
1. `student_name`: Full name of the student
2. `email`: Student's email address
3. `session_date`: Date of the attendance session (YYYY-MM-DD)
4. `session_time`: Time of the attendance session (HH:MM:SS)
5. `status`: Attendance status (present, absent, rejected, pending)
6. `marked_at`: Timestamp when attendance was marked
7. `distance_meters`: Distance from teacher location (if applicable)
8. `reason`: Reason for rejection or override (if applicable)

## Usage Examples

### Get JSON Report

```bash
GET /api/reports/attendance?course_id=1&from_date=2025-11-01&to_date=2025-11-30
Accept: application/json
Authorization: Bearer <teacher_jwt_token>
```

### Get CSV Report

```bash
GET /api/reports/attendance?course_id=1&from_date=2025-11-01&to_date=2025-11-30
Accept: text/csv
Authorization: Bearer <teacher_jwt_token>
```

Or using format parameter:

```bash
GET /api/reports/attendance?course_id=1&from_date=2025-11-01&to_date=2025-11-30&format=csv
Authorization: Bearer <teacher_jwt_token>
```

### Get All Records for a Course

```bash
GET /api/reports/attendance?course_id=1
Accept: text/csv
Authorization: Bearer <teacher_jwt_token>
```

## Requirements Satisfied

This implementation satisfies the following requirements from the requirements document:

- **Requirement 11.1**: Teacher can request attendance reports for assigned courses only
- **Requirement 11.2**: CSV export functionality with proper formatting
- **Requirement 11.3**: Date range filtering support
- **Requirement 11.4**: Teacher assignment validation
- **Requirement 11.5**: Efficient streaming for large datasets (>1000 records)

## Database Queries

The implementation uses efficient database queries:
- `select_related()` to join student and session data in a single query
- Indexed fields for filtering (course, start_at)
- Ordered results for consistent output

## Performance Considerations

- Uses Django ORM's `select_related()` to minimize database queries
- CSV renderer uses StringIO for memory-efficient string building
- Supports streaming for large datasets without loading all data into memory
- Date filtering at database level for efficiency

## Security

- Role-based access control (IsTeacher permission)
- Course assignment validation (teacher must be assigned to course)
- No data leakage between institutions (filtered by course)
- JWT authentication required

## Future Enhancements

Potential improvements for future iterations:
- Add pagination for JSON responses
- Support additional export formats (Excel, PDF)
- Add more filtering options (status, student name)
- Include summary statistics in reports
- Add scheduled report generation and email delivery
