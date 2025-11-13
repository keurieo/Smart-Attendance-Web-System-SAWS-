# Attendance Marking Implementation

## Overview
This document describes the implementation of the attendance marking feature (Task 7) for the Smart Attendance Web System.

## Endpoint
**POST** `/api/attendance/scan/`

## Authentication
- Requires JWT authentication
- Only users with STUDENT role can access

## Request Format
```json
{
  "token": "jwt_token_string_or_6digit_code",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "accuracy": 15.5,
  "device_info": {
    "device_id": "optional_device_identifier",
    "user_agent": "optional_user_agent_string"
  }
}
```

### Required Fields
- `token`: JWT token or 6-digit code from QR scan
- `latitude`: Student's latitude coordinate (-90 to 90)
- `longitude`: Student's longitude coordinate (-180 to 180)

### Optional Fields
- `accuracy`: GPS accuracy in meters
- `device_info`: Device information object

## Response Format

### Success Response (201 Created)
```json
{
  "success": true,
  "status": "present",
  "marked_at": "2025-11-13T10:15:30Z",
  "distance_meters": 25.3,
  "session": {
    "id": 123,
    "course_code": "CS101",
    "course_title": "Introduction to Computer Science",
    "start_at": "2025-11-13T10:00:00Z",
    "end_at": "2025-11-13T11:00:00Z"
  },
  "timestamp": "2025-11-13T10:15:30Z"
}
```

### Rejection Response (400 Bad Request)
```json
{
  "success": false,
  "status": "rejected",
  "marked_at": "2025-11-13T10:15:30Z",
  "distance_meters": 75.5,
  "reason": "Distance 75.5m exceeds allowed radius of 50m",
  "session": {
    "id": 123,
    "course_code": "CS101",
    "course_title": "Introduction to Computer Science",
    "start_at": "2025-11-13T10:00:00Z",
    "end_at": "2025-11-13T11:00:00Z"
  },
  "timestamp": "2025-11-13T10:15:30Z"
}
```

## Error Codes

### AUTH_003 - Insufficient Permissions
User is not a student or not authenticated.

### VAL_001 - Invalid Request Data
Request data validation failed (invalid coordinates, missing fields, etc.).

### ATT_003 - Token Error
- Token expired
- Invalid token format
- Token revoked or not found

### ATT_002 - Outside Time Window
Current time is not within the session's start and end time.

### ATT_004 - Duplicate Submission
Student has already marked attendance for this session.

### BIZ_002 - Not Enrolled
Student is not enrolled in the course.

## Validation Flow

1. **User Validation**: Verify user is authenticated and has STUDENT role
2. **Input Validation**: Validate request data format and coordinate ranges
3. **Token Validation**: 
   - Determine if token is JWT or 6-digit code
   - Verify token signature (for JWT)
   - Check token exists and is not revoked
   - Check token is not expired
4. **Time Window Validation**: Verify current time is within session start/end
5. **Enrollment Validation**: Verify student is enrolled in the course
6. **Location Validation**:
   - Check coordinates are not (0,0)
   - Check accuracy is acceptable (≤100m)
   - Calculate distance using Haversine formula
   - Compare distance against session radius
7. **Record Creation**: Create attendance record with appropriate status
8. **Side Effects**:
   - Create location snapshot
   - Create/update device record

## Database Operations

### Created Records
1. **AttendanceRecord**: Main attendance record with status and distance
2. **LocationSnapshot**: Student's location at time of marking
3. **Device**: Device information (created or updated)

### Constraints
- Unique constraint on (session_id, student_id) prevents duplicate submissions
- Transaction ensures atomicity of all operations

## Location Validation

Uses the `validate_location` function from `apps.geo.utils`:
- Calculates distance using Haversine formula
- Validates coordinates are not (0,0)
- Validates GPS accuracy is ≤100m
- Compares distance against session radius

## Device Tracking

Device tracking captures:
- User agent from HTTP headers
- Device ID (generated from user_agent hash if not provided)
- Last seen timestamp (auto-updated)
- Custom device info from request

## Location Snapshots

Location snapshots record:
- User ID
- Coordinates (Point geometry)
- Timestamp (auto-generated)
- Source: 'browser_geolocation'
- Accuracy (if provided)

## Implementation Files

### Modified Files
1. `backend/apps/attendance/serializers.py`
   - Added `AttendanceMarkingSerializer`
   - Added `AttendanceRecordSerializer`

2. `backend/apps/attendance/views.py`
   - Added `AttendanceMarkingView` class

3. `backend/apps/attendance/urls.py`
   - Added route for `/scan/` endpoint

### Dependencies
- `apps.geo.utils.validate_location`: Location validation
- `apps.attendance.services.verify_qr_token`: Token verification
- `apps.academics.models.Enrollment`: Enrollment validation
- `apps.audit.models.LocationSnapshot`: Location tracking
- `apps.audit.models.Device`: Device tracking

## Requirements Coverage

### Requirement 3: Student Attendance Marking via QR Scan
- ✅ 3.1: Token verification (exists, not expired, not revoked)
- ✅ 3.2: Geolocation capture
- ✅ 3.3: Distance calculation using Haversine
- ✅ 3.4: Rejection when outside radius
- ✅ 3.5: Present status when within radius
- ✅ 3.6: Time window validation
- ✅ 3.7: Duplicate prevention

### Requirement 4: Geolocation Validation
- ✅ 4.1: Haversine formula usage
- ✅ 4.2: Location storage
- ✅ 4.3: Distance storage

### Requirement 12: Session Time Window Validation
- ✅ 12.1: Start time validation
- ✅ 12.2: End time validation
- ✅ 12.3: Rejection outside window

### Requirement 14: Device Tracking
- ✅ 14.1: Device info capture
- ✅ 14.2: Device record creation
- ✅ 14.3: Last seen update
- ✅ 14.4: Device info storage

### Requirement 15: Location Snapshot Logging
- ✅ 15.2: Student location snapshot
- ✅ 15.3: Snapshot storage with timestamp

## Testing Recommendations

### Unit Tests
- Serializer validation (coordinates, token format)
- Token verification logic
- Location validation edge cases

### Integration Tests
- Successful attendance within radius and time
- Rejection scenarios (outside radius, outside time, expired token)
- Duplicate submission prevention
- Enrollment validation
- Location snapshot creation
- Device tracking

### End-to-End Tests
- Complete flow from QR scan to attendance record
- Both JWT and 6-digit code paths
- Error handling and user feedback
