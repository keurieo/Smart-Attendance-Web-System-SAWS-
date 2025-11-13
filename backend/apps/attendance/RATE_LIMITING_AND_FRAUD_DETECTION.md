# Rate Limiting and Fraud Detection Implementation

This document describes the implementation of rate limiting and fraud detection for the Smart Attendance Web System.

## Overview

Task 8 has been completed with the following components:
- Redis-based rate limiting for attendance marking endpoint
- Fraud detection for suspicious attendance submissions
- Automatic flagging of suspicious records for admin review

## Components Implemented

### 1. Rate Limiting Module (`ratelimit.py`)

**Location:** `backend/apps/attendance/ratelimit.py`

**Features:**
- Custom rate limiting decorator using Redis cache
- Sliding window algorithm for accurate rate limiting
- Two-tier rate limiting:
  - **User-based:** 10 requests per minute per student user ID
  - **IP-based:** 50 requests per minute per IP address
- Returns HTTP 429 (Too Many Requests) when limits exceeded
- Includes retry_after information in error response

**Key Functions:**
- `get_client_ip(request)`: Extracts client IP from request headers
- `rate_limit_key(prefix, identifier)`: Generates hashed cache keys
- `check_rate_limit(cache_key, limit, window_seconds)`: Implements sliding window rate limiting
- `attendance_rate_limit`: Decorator that applies rate limits to views

**Configuration:**
Rate limiting can be disabled by setting `RATELIMIT_ENABLE = False` in Django settings.

**Error Response Format:**
```json
{
  "error_code": "RATE_001",
  "message": "Rate limit exceeded",
  "details": {
    "limit_type": "user",
    "limit": 10,
    "window": "1 minute",
    "current_count": 11,
    "retry_after": 45
  },
  "timestamp": "2025-11-13T10:30:00Z"
}
```

### 2. Fraud Detection Module (`fraud_detection.py`)

**Location:** `backend/apps/attendance/fraud_detection.py`

**Features:**
- Detects identical coordinates across multiple students
- Detects time delta anomalies between device and server timestamps
- Automatically flags suspicious records for admin review
- Appends fraud information to attendance record reason field

**Key Functions:**

#### `detect_identical_coordinates(session, student_location, threshold=5)`
Detects when more than 5 students submit identical coordinates (within 1 meter) for the same session.

**Parameters:**
- `session`: AttendanceSession instance
- `student_location`: Point object with student's coordinates
- `threshold`: Maximum allowed students at identical location (default: 5)

**Returns:**
- `(is_suspicious, count_at_location)`

#### `detect_time_delta_anomaly(device_timestamp, server_timestamp, threshold_seconds=300)`
Detects when device timestamp differs from server timestamp by more than 5 minutes.

**Parameters:**
- `device_timestamp`: datetime from device
- `server_timestamp`: datetime from server
- `threshold_seconds`: Maximum allowed time difference (default: 300)

**Returns:**
- `(is_suspicious, time_delta_seconds)`

#### `check_fraud_indicators(session, student_location, device_timestamp, server_timestamp)`
Main entry point that runs all fraud detection checks.

**Returns:**
```python
{
    'should_flag': bool,
    'reasons': ['identical_coordinates', 'time_delta_anomaly'],
    'details': {
        'identical_coordinates_count': 6,
        'time_delta_seconds': 450
    }
}
```

#### `flag_attendance_for_review(attendance_record, fraud_reasons, fraud_details)`
Flags an attendance record for admin review by:
- Setting `flagged_for_review = True`
- Appending fraud information to `reason` field

### 3. Integration with Attendance Marking View

**Location:** `backend/apps/attendance/views.py`

**Changes:**
1. Added `@attendance_rate_limit` decorator to `AttendanceMarkingView.post()`
2. Integrated fraud detection after attendance record creation
3. Updated response to include fraud detection information

**Flow:**
1. Rate limiting check (before processing)
2. Token validation
3. Location validation
4. Attendance record creation
5. **Fraud detection checks** (new)
6. **Flag record if suspicious** (new)
7. Location snapshot creation
8. Device tracking
9. Response with fraud indicators (if flagged)

**Response with Fraud Detection:**
```json
{
  "success": true,
  "status": "present",
  "marked_at": "2025-11-13T10:30:00Z",
  "distance_meters": 25.5,
  "flagged_for_review": true,
  "fraud_indicators": ["identical_coordinates"],
  "session": {...},
  "timestamp": "2025-11-13T10:30:00Z"
}
```

### 4. Updated Serializer

**Location:** `backend/apps/attendance/serializers.py`

**Changes:**
- Added `device_timestamp` field to `AttendanceMarkingSerializer`
- Allows clients to send device timestamp for time delta detection

**Request Format:**
```json
{
  "token": "jwt_token_or_6digit_code",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "accuracy": 15.5,
  "device_info": {...},
  "device_timestamp": "2025-11-13T10:29:55Z"
}
```

## Configuration

### Redis Configuration

Already configured in `backend/config/settings/base.py`:

```python
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
```

### Environment Variables

Set in `.env` file:
```
REDIS_URL=redis://localhost:6379/0
```

## Testing

### Manual Testing

1. **Test Rate Limiting:**
```bash
# Send 11 requests within 1 minute from same user
for i in {1..11}; do
  curl -X POST http://localhost:8000/api/student/attendance/scan \
    -H "Authorization: Bearer <token>" \
    -H "Content-Type: application/json" \
    -d '{"token": "123456", "latitude": 40.7128, "longitude": -74.0060}'
done
```

Expected: First 10 succeed, 11th returns HTTP 429

2. **Test Identical Coordinates Detection:**
- Have 6 students submit attendance with identical coordinates
- Check that records are flagged with `flagged_for_review=True`

3. **Test Time Delta Detection:**
```bash
curl -X POST http://localhost:8000/api/student/attendance/scan \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "123456",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "device_timestamp": "2025-11-13T10:00:00Z"
  }'
```

Expected: If server time is >5 minutes different, record is flagged

### Automated Testing

Unit tests should be created for:
- Rate limiting logic
- Fraud detection functions
- Integration with attendance marking endpoint

## Admin Review

Admins can query flagged records:

```python
# Get all flagged attendance records
flagged_records = AttendanceRecord.objects.filter(flagged_for_review=True)

# Get flagged records for a specific session
session_flagged = AttendanceRecord.objects.filter(
    session_id=123,
    flagged_for_review=True
)
```

The `reason` field contains detailed information about why the record was flagged:
```
"Flagged for review: identical_coordinates, time_delta_anomaly (identical_coordinates_count=6; time_delta_seconds=450)"
```

## Performance Considerations

### Rate Limiting
- Uses Redis for fast in-memory operations
- Sliding window algorithm provides accurate rate limiting
- Cache keys are hashed for privacy
- Old timestamps are automatically cleaned up

### Fraud Detection
- Identical coordinates check uses PostGIS spatial query (efficient with GIST index)
- Time delta check is simple arithmetic (very fast)
- Fraud checks run after record creation (doesn't block submission)
- Flagging is done with single UPDATE query

## Security Considerations

1. **Rate Limiting:**
   - Prevents brute force attacks on attendance endpoint
   - Protects against DoS attacks
   - User IDs and IPs are hashed in cache keys

2. **Fraud Detection:**
   - Detects coordinate sharing/spoofing
   - Detects time manipulation attempts
   - Records are flagged but not automatically rejected (allows admin review)

3. **Privacy:**
   - Cache keys use hashed identifiers
   - Fraud details stored in reason field (admin-only access)

## Requirements Satisfied

✅ **Requirement 9.1:** Rate limit of 10 requests per minute per student user ID  
✅ **Requirement 9.2:** Rate limit of 50 requests per minute per IP address  
✅ **Requirement 9.3:** Detect >5 students with identical coordinates  
✅ **Requirement 9.4:** Detect time delta >300 seconds  
✅ **Requirement 9.5:** Return HTTP 429 when rate limit exceeded  

## Future Enhancements

1. **Additional Fraud Indicators:**
   - Impossible speed detection (location changes too fast)
   - Device fingerprint analysis
   - Pattern detection (same device used by multiple students)

2. **Machine Learning:**
   - Train model on historical fraud patterns
   - Anomaly detection for unusual behavior

3. **Admin Dashboard:**
   - Real-time fraud alerts
   - Fraud statistics and trends
   - Bulk review/approval interface

4. **Rate Limiting Improvements:**
   - Configurable limits per institution
   - Dynamic rate limiting based on behavior
   - Whitelist for trusted users/IPs

## Troubleshooting

### Rate Limiting Not Working
- Check Redis connection: `redis-cli ping`
- Verify `RATELIMIT_ENABLE = True` in settings
- Check cache configuration in settings

### Fraud Detection Not Flagging
- Verify PostGIS is installed and working
- Check that `flagged_for_review` field exists in database
- Review fraud detection thresholds (may need adjustment)

### Performance Issues
- Monitor Redis memory usage
- Check PostGIS query performance with EXPLAIN ANALYZE
- Consider adding more indexes if needed

## Related Files

- `backend/apps/attendance/ratelimit.py` - Rate limiting implementation
- `backend/apps/attendance/fraud_detection.py` - Fraud detection implementation
- `backend/apps/attendance/views.py` - Integration with attendance marking
- `backend/apps/attendance/serializers.py` - Request/response serializers
- `backend/apps/attendance/models.py` - AttendanceRecord model with flagged_for_review field
- `backend/config/settings/base.py` - Redis and rate limiting configuration
