# Audit Log Endpoint Implementation

## Overview

This document describes the implementation of the audit log querying endpoint as specified in task 13.1.

## Endpoint

**GET** `/api/admin/audit/`

Returns a paginated list of audit log entries with filtering capabilities.

## Authentication & Authorization

- **Authentication**: JWT token required
- **Permission**: `IsAdmin` - Only users with admin role can access this endpoint

## Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `user_id` | integer | Filter by user ID who performed the action | `?user_id=5` |
| `date_from` | datetime | Filter logs from this date (ISO 8601 format) | `?date_from=2025-01-01T00:00:00Z` |
| `date_to` | datetime | Filter logs until this date (ISO 8601 format) | `?date_to=2025-12-31T23:59:59Z` |
| `action` | string | Filter by action (case-insensitive partial match) | `?action=create` |
| `target_table` | string | Filter by target table name (case-insensitive exact match) | `?target_table=users` |
| `page` | integer | Page number (default: 1) | `?page=2` |
| `page_size` | integer | Number of records per page (default: 50, max: 100) | `?page_size=25` |

## Response Format

### Success Response (200 OK)

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/admin/audit/?page=2",
  "previous": null,
  "results": [
    {
      "id": 123,
      "performed_by": 5,
      "performed_by_email": "admin@example.com",
      "performed_by_name": "John Admin",
      "action": "attendance_override",
      "target_table": "attendance_records",
      "target_id": 456,
      "old_data": {
        "status": "absent"
      },
      "new_data": {
        "status": "present",
        "reason": "Medical certificate provided"
      },
      "performed_at": "2025-11-15T10:30:00Z"
    },
    {
      "id": 122,
      "performed_by": 3,
      "performed_by_email": "teacher@example.com",
      "performed_by_name": "Jane Teacher",
      "action": "session_created",
      "target_table": "attendance_sessions",
      "target_id": 789,
      "old_data": null,
      "new_data": {
        "course_id": 10,
        "start_at": "2025-11-15T09:00:00Z",
        "end_at": "2025-11-15T10:30:00Z",
        "radius_meters": 50
      },
      "performed_at": "2025-11-15T08:55:00Z"
    }
  ]
}
```

### Error Responses

**401 Unauthorized** - Missing or invalid JWT token
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden** - User is not an admin
```json
{
  "detail": "You must be an admin to perform this action."
}
```

## Implementation Details

### Files Created/Modified

1. **backend/apps/audit/views.py** (Created)
   - `AuditLogListView`: Main view for listing audit logs
   - `AuditLogPagination`: Custom pagination class (50 records per page)
   - `AuditLogFilter`: Filter class using django-filter

2. **backend/apps/audit/serializers.py** (Created)
   - `AuditLogSerializer`: Serializes audit log entries with user details

3. **backend/apps/audit/urls.py** (Modified)
   - Added route for audit log endpoint

4. **backend/requirements/base.txt** (Modified)
   - Added `django-filter==23.5` dependency

5. **backend/config/settings/base.py** (Modified)
   - Added `django_filters` to `INSTALLED_APPS`

### Key Features

1. **Filtering**: Uses django-filter for flexible query parameter filtering
   - `user_id`: Filters by the user who performed the action
   - `date_from` and `date_to`: Date range filtering on `performed_at` field
   - `action`: Case-insensitive partial match on action field
   - `target_table`: Case-insensitive exact match on target table

2. **Pagination**: 
   - Default page size: 50 records
   - Maximum page size: 100 records
   - Configurable via `page_size` query parameter

3. **Ordering**: 
   - Default: Descending by `performed_at` (newest first)
   - Supports ordering by: `performed_at`, `action`, `target_table`

4. **Performance Optimization**:
   - Uses `select_related('performed_by')` to reduce database queries
   - Database indexes on frequently queried fields (defined in model)

5. **Security**:
   - Requires JWT authentication
   - Restricted to admin users only via `IsAdmin` permission

## Example Usage

### Get all audit logs (first page)
```bash
curl -H "Authorization: Bearer <jwt_token>" \
  http://localhost:8000/api/admin/audit/
```

### Filter by user and date range
```bash
curl -H "Authorization: Bearer <jwt_token>" \
  "http://localhost:8000/api/admin/audit/?user_id=5&date_from=2025-11-01T00:00:00Z&date_to=2025-11-30T23:59:59Z"
```

### Filter by action type
```bash
curl -H "Authorization: Bearer <jwt_token>" \
  "http://localhost:8000/api/admin/audit/?action=override"
```

### Filter by target table
```bash
curl -H "Authorization: Bearer <jwt_token>" \
  "http://localhost:8000/api/admin/audit/?target_table=attendance_records"
```

### Combine multiple filters with pagination
```bash
curl -H "Authorization: Bearer <jwt_token>" \
  "http://localhost:8000/api/admin/audit/?user_id=5&action=create&page=2&page_size=25"
```

## Testing

The endpoint can be tested using:
1. Django REST Framework browsable API (when DEBUG=True)
2. Postman or similar API testing tools
3. curl commands as shown above
4. Automated tests (to be implemented in task 13.2)

## Requirements Satisfied

This implementation satisfies **Requirement 10.5** from the requirements document:

> "THE System SHALL allow Admins to query audit logs filtered by user, date range, action type, and target table"

All specified filtering capabilities are implemented:
- ✅ Filter by user (via `user_id` parameter)
- ✅ Filter by date range (via `date_from` and `date_to` parameters)
- ✅ Filter by action type (via `action` parameter)
- ✅ Filter by target table (via `target_table` parameter)
- ✅ Pagination with 50 records per page
- ✅ Ordered by `performed_at` descending
- ✅ Admin-only access via `IsAdmin` permission
