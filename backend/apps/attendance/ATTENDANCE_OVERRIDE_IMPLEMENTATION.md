# Attendance Record Override Implementation

## Overview
This document describes the implementation of the attendance record override functionality for admins (Task 11).

## Implementation Summary

### Task 11.1: Create Override Serializer ✅

**File:** `backend/apps/attendance/serializers.py`

**Implementation:**
- Created `AttendanceOverrideSerializer` class
- Fields:
  - `status`: ChoiceField with options: present, absent, rejected, pending
  - `reason`: CharField (required, non-empty, max 1000 chars)
- Validation:
  - `validate_reason()`: Ensures reason is provided and non-empty
  - `validate_status()`: Ensures status is one of the allowed values
- Meets Requirements: 7.1, 7.4

### Task 11.2: Create Override Endpoint ✅

**File:** `backend/apps/attendance/views.py`

**Implementation:**
- Created `AttendanceOverrideView` class (APIView)
- Endpoint: `PATCH /api/admin/attendance/:record_id`
- Permission: `IsAuthenticated` + `IsAdmin`
- Functionality:
  1. Validates request data using `AttendanceOverrideSerializer`
  2. Retrieves existing `AttendanceRecord` using `get_object_or_404`
  3. Stores old status and reason in variables
  4. Updates status and reason fields
  5. Creates audit log entry with:
     - `performed_by`: Admin user
     - `action`: 'override_attendance_record'
     - `target_table`: 'attendance_records'
     - `target_id`: Record ID
     - `old_data`: Old status, reason, student info, session info
     - `new_data`: New status, reason, student info, session info
  6. Returns updated attendance record with success message
- Uses `@transaction.atomic` for data consistency
- Meets Requirements: 7.1, 7.2, 7.3, 7.5

**File:** `backend/apps/audit/urls.py`

**Implementation:**
- Added route: `path('attendance/<int:record_id>/', AttendanceOverrideView.as_view(), name='attendance-override')`
- Full URL: `/api/admin/attendance/:record_id`

## Requirements Coverage

### Requirement 7.1 ✅
**"WHEN an Admin overrides an attendance record status, THE System SHALL require a textual reason for the override"**
- Implemented in `AttendanceOverrideSerializer.reason` field with `required=True` and `allow_blank=False`
- Additional validation in `validate_reason()` ensures non-empty string

### Requirement 7.2 ✅
**"WHEN an Admin overrides an attendance record, THE System SHALL create an audit log entry containing the Admin's user ID, old status, new status, reason, and timestamp"**
- Implemented in `AttendanceOverrideView.patch()` method
- Creates `AuditLog` entry with all required fields
- Timestamp automatically added via `performed_at` field (auto_now_add=True)

### Requirement 7.3 ✅
**"WHEN an Admin overrides an attendance record, THE System SHALL update the attendance record's status and reason fields"**
- Implemented in `AttendanceOverrideView.patch()` method
- Updates both `status` and `reason` fields
- Uses `save(update_fields=['status', 'reason', 'updated_at'])` for efficiency

### Requirement 7.4 ✅
**"THE System SHALL allow Admins to change attendance status to 'present', 'absent', 'rejected', or 'pending'"**
- Implemented in `AttendanceOverrideSerializer.status` field
- Uses `ChoiceField` with exactly these four options
- Additional validation in `validate_status()` method

### Requirement 7.5 ✅
**"THE System SHALL restrict attendance record override operations to users with Admin role only"**
- Implemented via `permission_classes = [IsAuthenticated, IsAdmin]`
- `IsAdmin` permission class checks user role

## API Specification

### Endpoint
```
PATCH /api/admin/attendance/:record_id
```

### Request Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Request Body
```json
{
  "status": "present|absent|rejected|pending",
  "reason": "Reason for override (required, non-empty)"
}
```

### Success Response (200 OK)
```json
{
  "success": true,
  "message": "Attendance record updated successfully",
  "data": {
    "id": 123,
    "session": 45,
    "student": 67,
    "student_name": "John Doe",
    "student_email": "john@example.com",
    "course_code": "CS101",
    "session_start": "2025-11-13T10:00:00Z",
    "marked_at": "2025-11-13T10:15:00Z",
    "method": "qr_scan",
    "status": "present",
    "distance_meters": 25.5,
    "reason": "Reason for override",
    "flagged_for_review": false
  },
  "timestamp": "2025-11-13T11:00:00Z"
}
```

### Error Responses

#### 400 Bad Request (Invalid Data)
```json
{
  "error_code": "VAL_001",
  "message": "Invalid request data",
  "details": {
    "reason": ["Reason must be provided and cannot be empty."]
  },
  "timestamp": "2025-11-13T11:00:00Z"
}
```

#### 403 Forbidden (Not Admin)
```json
{
  "detail": "You must be an admin to perform this action."
}
```

#### 404 Not Found (Record Not Found)
```json
{
  "detail": "Not found."
}
```

## Audit Log Entry Example

When an admin overrides an attendance record, the following audit log entry is created:

```json
{
  "performed_by": 1,
  "action": "override_attendance_record",
  "target_table": "attendance_records",
  "target_id": 123,
  "old_data": {
    "status": "rejected",
    "reason": "Outside allowed radius",
    "student_id": 67,
    "student_name": "John Doe",
    "session_id": 45,
    "course_code": "CS101"
  },
  "new_data": {
    "status": "present",
    "reason": "Student had technical issues with GPS",
    "student_id": 67,
    "student_name": "John Doe",
    "session_id": 45,
    "course_code": "CS101"
  },
  "performed_at": "2025-11-13T11:00:00Z"
}
```

## Testing Considerations

### Manual Testing Steps
1. Create an admin user
2. Create an attendance record (via student attendance marking)
3. Authenticate as admin and get JWT token
4. Send PATCH request to `/api/admin/attendance/:record_id` with valid data
5. Verify response contains updated record
6. Query audit logs to verify entry was created
7. Test validation errors (empty reason, invalid status)
8. Test permission enforcement (non-admin user)

### Test Cases to Implement (Optional Task 11.3)
- Test successful override with valid data
- Test rejection when reason is missing or empty
- Test rejection when status is invalid
- Test audit log creation with correct old_data and new_data
- Test permission enforcement (non-admin cannot access)
- Test 404 when record doesn't exist

## Files Modified

1. `backend/apps/attendance/serializers.py`
   - Added `AttendanceOverrideSerializer` class

2. `backend/apps/attendance/views.py`
   - Added import for `IsAdmin` permission
   - Added import for `AttendanceOverrideSerializer`
   - Added import for `get_object_or_404`
   - Added `AttendanceOverrideView` class

3. `backend/apps/audit/urls.py`
   - Added route for attendance override endpoint

## Completion Status

✅ Task 11.1: Create override serializer - COMPLETED
✅ Task 11.2: Create override endpoint - COMPLETED
⬜ Task 11.3: Write override tests - OPTIONAL (marked with *)

All required subtasks have been completed successfully. The implementation follows Django REST Framework best practices and meets all specified requirements.
