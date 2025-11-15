# Session Management Implementation

## Overview

This document describes the implementation of session management endpoints for the Smart Attendance System, specifically task 14 from the implementation plan.

## Implemented Features

### 14.1 Session Detail Endpoint

**Endpoint:** `GET /api/attendance/sessions/:id`

**Authentication:** Required (JWT)

**Permissions:** IsTeacher - Teacher must be assigned to the session's course

**Functionality:**
- Retrieves detailed information about a specific attendance session
- Validates that the requesting teacher is assigned to the session's course
- Returns session details including:
  - Basic session information (course, time window, location, radius)
  - Complete list of attendance records with student names and statuses
  - Summary statistics (total attendance, present count, absent count, rejected count)

**Response Format:**
```json
{
  "id": 1,
  "course_id": 1,
  "course_code": "CS101",
  "course_title": "Introduction to Computer Science",
  "start_at": "2025-11-15T10:00:00Z",
  "end_at": "2025-11-15T11:00:00Z",
  "radius_meters": 50,
  "status": "active",
  "notes": "Regular class session",
  "created_at": "2025-11-15T09:45:00Z",
  "attendance_records": [
    {
      "id": 1,
      "student": 5,
      "student_name": "John Doe",
      "student_email": "john.doe@example.com",
      "course_code": "CS101",
      "session_start": "2025-11-15T10:00:00Z",
      "marked_at": "2025-11-15T10:05:00Z",
      "method": "qr_scan",
      "status": "present",
      "distance_meters": 25.5,
      "reason": "",
      "flagged_for_review": false
    }
  ],
  "total_attendance": 25,
  "present_count": 23,
  "absent_count": 0,
  "rejected_count": 2
}
```

**Error Responses:**
- `403 Forbidden`: Teacher not assigned to the session's course
- `404 Not Found`: Session does not exist

**Implementation Details:**
- Added `retrieve` method to `AttendanceSessionViewSet`
- Uses `select_related('student')` for efficient database queries
- Calculates attendance statistics in a single query
- Orders attendance records by `marked_at` descending (most recent first)

### 14.2 Session Expiration Logic

**Functionality:**
- Automatically updates session status to "expired" when `end_at` time is reached
- Implemented at the database query level for efficiency
- No background tasks or cron jobs required

**Implementation Approach:**

1. **Custom Manager (`AttendanceSessionManager`):**
   - Overrides `get_queryset()` to automatically update expired sessions
   - Whenever sessions are queried, expired sessions are updated in bulk
   - Provides convenience methods:
     - `active_sessions()`: Returns only currently active sessions
     - `expired_sessions()`: Returns only expired sessions

2. **Model Methods:**
   - `is_expired()`: Checks if the session has passed its end time
   - `update_status_if_expired()`: Manually updates status if expired

**How It Works:**

When any query is made on `AttendanceSession.objects`, the custom manager:
1. Executes a bulk update query: `UPDATE attendance_sessions SET status='expired' WHERE end_at < NOW() AND status='active'`
2. Returns the queryset for the original query

This ensures that:
- Session status is always current when queried
- No background tasks are needed
- Minimal performance impact (single UPDATE query per request)
- Works automatically with all existing views and queries

**Example Usage:**

```python
# Automatically updates expired sessions before returning results
active_sessions = AttendanceSession.objects.filter(status='active')

# Get only truly active sessions (not expired)
active_sessions = AttendanceSession.objects.active_sessions()

# Check if a specific session is expired
session = AttendanceSession.objects.get(id=1)
if session.is_expired():
    session.update_status_if_expired()
```

## Requirements Satisfied

- **Requirement 2.1**: Teacher can view session details for assigned courses
- **Requirement 2.2**: Session details include attendance records with student information
- **Requirement 12.4**: Sessions automatically expire when end_at is reached

## Testing Recommendations

### Manual Testing

1. **Session Detail Endpoint:**
   ```bash
   # Create a session as a teacher
   POST /api/attendance/sessions
   
   # Retrieve session details
   GET /api/attendance/sessions/{session_id}
   
   # Try to access another teacher's session (should fail)
   GET /api/attendance/sessions/{other_session_id}
   ```

2. **Session Expiration:**
   ```bash
   # Create a session with end_at in the past
   POST /api/attendance/sessions
   {
     "end_at": "2025-11-14T10:00:00Z"  # Past time
   }
   
   # Query sessions - should automatically be marked as expired
   GET /api/attendance/sessions
   ```

### Automated Testing

Test cases to implement (optional):
- Test session detail retrieval by assigned teacher
- Test permission denial for non-assigned teacher
- Test attendance record inclusion in response
- Test statistics calculation (counts)
- Test automatic expiration on query
- Test `active_sessions()` and `expired_sessions()` methods
- Test `is_expired()` and `update_status_if_expired()` methods

## Database Performance

The implementation is optimized for performance:

1. **Session Detail Endpoint:**
   - Uses `select_related('student')` to avoid N+1 queries
   - Single query for attendance records
   - Efficient aggregation for statistics

2. **Session Expiration:**
   - Bulk UPDATE query (not per-record)
   - Only updates sessions that need updating (WHERE clause filters)
   - Indexed on `status` and `end_at` fields for fast queries

## Future Enhancements

Potential improvements for production:
1. Add pagination for attendance records in session detail
2. Add filtering options (by status, date range)
3. Add caching for frequently accessed sessions
4. Consider background task for expiration if query-time updates cause issues
5. Add WebSocket notifications for real-time session status updates
