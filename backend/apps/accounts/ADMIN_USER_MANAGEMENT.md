# Admin User Management Implementation

## Overview
This document describes the implementation of admin user management functionality for the Smart Attendance Web System.

## Implementation Summary

### Task 9.1: User Management Serializers ✅

Created three new serializers in `backend/apps/accounts/serializers.py`:

1. **UserSerializer**
   - Used for listing and retrieving user data
   - Returns: id, email, full_name, role, institution_name, is_active, timestamps
   - Read-only fields for security

2. **UserCreateSerializer**
   - Used for creating new users
   - Validates: email uniqueness, role validity, institution existence
   - Automatically hashes passwords using bcrypt via Django's `set_password()`
   - Required fields: email, password, full_name, role, institution_id

3. **UserUpdateSerializer**
   - Used for updating existing users
   - Allows updating: full_name, role, is_active
   - Validates role changes
   - Supports partial updates (PATCH)

### Task 9.2: User Management Endpoints ✅

Created `AdminUserManagementViewSet` in `backend/apps/accounts/views.py`:

**Endpoints:**
- `GET /api/accounts/admin/users/` - List users with pagination and filtering
- `POST /api/accounts/admin/users/` - Create new user
- `GET /api/accounts/admin/users/:id/` - Retrieve specific user
- `PATCH /api/accounts/admin/users/:id/` - Update user (partial)
- `PUT /api/accounts/admin/users/:id/` - Update user (full)
- `DELETE /api/accounts/admin/users/:id/` - Soft delete user (deactivate)

**Features:**
- **Pagination**: 50 users per page (configurable up to 100)
- **Filtering**: 
  - By role: `?role=admin|teacher|student`
  - By active status: `?is_active=true|false`
  - By search: `?search=<email or name>`
- **Institution Isolation**: Users can only manage users in their own institution
- **Permission Control**: All endpoints require `IsAdmin` permission
- **Soft Delete**: DELETE endpoint sets `is_active=False` instead of deleting records

### Task 9.3: Audit Logging ✅

Implemented comprehensive audit logging for all user operations:

**Audit Log Utility Function:**
- `create_audit_log()` - Helper function to create audit entries
- Stores: performed_by, action, target_table, target_id, old_data, new_data

**Logged Operations:**
1. **User Creation** (`user_created`)
   - Logs: email, full_name, role, institution_id, is_active
   
2. **User Update** (`user_updated`)
   - Logs: old and new values for email, full_name, role, is_active
   
3. **User Deactivation** (`user_deactivated`)
   - Logs: old and new values showing is_active change from True to False

**Audit Data Format:**
```json
{
  "performed_by": <user_id>,
  "action": "user_created|user_updated|user_deactivated",
  "target_table": "users",
  "target_id": <user_id>,
  "old_data": {...},  // For updates and deletes
  "new_data": {...},  // For creates and updates
  "performed_at": "<timestamp>"
}
```

## API Usage Examples

### List Users
```bash
GET /api/accounts/admin/users/?role=teacher&is_active=true&page=1
Authorization: Bearer <admin_jwt_token>
```

### Create User
```bash
POST /api/accounts/admin/users/
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "email": "teacher@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "role": "teacher",
  "institution_id": 1
}
```

### Update User
```bash
PATCH /api/accounts/admin/users/5/
Authorization: Bearer <admin_jwt_token>
Content-Type: application/json

{
  "role": "admin",
  "is_active": true
}
```

### Deactivate User
```bash
DELETE /api/accounts/admin/users/5/
Authorization: Bearer <admin_jwt_token>
```

## Requirements Satisfied

✅ **Requirement 5.1**: Admin can create user accounts with email, password, full name, and role  
✅ **Requirement 5.2**: Email uniqueness validation  
✅ **Requirement 5.3**: Role changes are recorded in audit log  
✅ **Requirement 5.4**: Soft delete (deactivation) without removing records  
✅ **Requirement 5.5**: Operations restricted to Admin role only  
✅ **Requirement 10.2**: Audit logging for user create, update, and delete operations

## Security Features

1. **Password Hashing**: All passwords hashed using bcrypt before storage
2. **Permission Control**: IsAdmin permission required for all endpoints
3. **Institution Isolation**: Admins can only manage users in their institution
4. **Soft Delete**: User records preserved for audit trail
5. **Audit Trail**: Complete history of all user management operations
6. **Input Validation**: Email format, role validity, institution existence

## Testing Recommendations

1. Test user creation with valid and invalid data
2. Test email uniqueness constraint
3. Test role validation (admin, teacher, student only)
4. Test institution isolation (admin cannot see/modify users from other institutions)
5. Test permission enforcement (non-admin users cannot access endpoints)
6. Test pagination and filtering
7. Test audit log creation for all operations
8. Test soft delete functionality
9. Test password hashing (passwords should never be stored in plain text)

## Notes

- The implementation uses Django REST Framework's ModelViewSet for clean, RESTful API design
- Pagination is implemented to handle large user lists efficiently
- All operations are logged for compliance and debugging
- The soft delete approach preserves data integrity and audit trails
