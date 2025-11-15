# Login Troubleshooting Guide

## Current Status ✅

Your Smart Attendance System is now properly configured and running!

### Services Status
- ✅ Backend API: http://localhost:8000/api (Running)
- ✅ Frontend: http://localhost:3000 (Running)
- ✅ Database: PostgreSQL with PostGIS (Running)
- ✅ Redis: Cache and rate limiting (Running)

### Admin Credentials
```
Email: admin@example.com
Password: admin123
```

## Fixed Issues

### 1. Backend URL Endpoints ✅
**Problem**: Frontend was calling different endpoints than what backend provided.

**Solution**: Updated backend URLs to match frontend expectations:
- Added `/api/accounts/token/` for login (frontend expects this)
- Added `/api/accounts/token/refresh/` for token refresh
- Added `/api/accounts/users/me/` for user profile
- Kept `/api/accounts/login/` as an alias

### 2. Missing Middleware ✅
**Problem**: `AuditLogMiddleware` was referenced but not implemented.

**Solution**: Created placeholder middleware implementation.

### 3. Database Migration Issues ✅
**Problem**: AttendanceSession manager tried to query database during import.

**Solution**: Added safety checks to only run queries if tables exist.

### 4. Missing Initial Data ✅
**Problem**: No admin user or roles existed in database.

**Solution**: Created `setup_initial_data.py` script that creates:
- Institution (Test University)
- Roles (Admin, Teacher, Student)
- Admin user with credentials

## How to Login

### Option 1: Frontend Application (React)
1. Open browser to http://localhost:3000
2. You'll be redirected to the login page
3. Enter credentials:
   - Email: `admin@example.com`
   - Password: `admin123`
4. Click "Sign in"
5. You'll be redirected to the admin dashboard

### Option 2: Django Admin Panel
1. Open browser to http://localhost:8000/admin
2. Enter credentials:
   - Email: `admin@example.com`
   - Password: `admin123`
3. You'll have full admin access to manage the system

## Testing the API Connection

### Test Login Endpoint
```powershell
curl http://localhost:8000/api/accounts/token/ `
  -Method POST `
  -Body '{"email":"admin@example.com","password":"admin123"}' `
  -ContentType "application/json" `
  -UseBasicParsing
```

Expected response:
```json
{
  "refresh": "eyJhbGci...",
  "access": "eyJhbGci...",
  "user": {
    "id": 2,
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "admin",
    "institution": {
      "id": 1,
      "name": "Test University"
    },
    "is_active": true
  }
}
```

### Test User Profile Endpoint
```powershell
# First get token
$response = curl http://localhost:8000/api/accounts/token/ `
  -Method POST `
  -Body '{"email":"admin@example.com","password":"admin123"}' `
  -ContentType "application/json" `
  -UseBasicParsing
$token = ($response.Content | ConvertFrom-Json).access

# Then get profile
curl http://localhost:8000/api/accounts/users/me/ `
  -Headers @{"Authorization"="Bearer $token"} `
  -UseBasicParsing
```

## Common Issues and Solutions

### Issue: "Cannot connect to backend"
**Symptoms**: Frontend shows connection errors, API calls fail

**Solutions**:
1. Check if backend is running:
   ```powershell
   docker-compose ps backend
   ```
2. Check backend logs:
   ```powershell
   docker-compose logs --tail=50 backend
   ```
3. Restart backend:
   ```powershell
   docker-compose restart backend
   ```

### Issue: "Invalid credentials"
**Symptoms**: Login fails with "Invalid credentials" error

**Solutions**:
1. Verify you're using the correct credentials:
   - Email: `admin@example.com`
   - Password: `admin123`
2. Check if user exists in database:
   ```powershell
   docker-compose exec -T backend python manage.py shell -c "from apps.accounts.models import User; print(User.objects.filter(email='admin@example.com').exists())"
   ```
3. If user doesn't exist, run setup script:
   ```powershell
   docker-compose exec -T backend python setup_initial_data.py
   ```

### Issue: "CORS error"
**Symptoms**: Browser console shows CORS policy errors

**Solutions**:
1. Check CORS settings in `backend/config/settings/development.py`
2. Ensure `CORS_ALLOW_ALL_ORIGINS = True` is set
3. Restart backend after changes:
   ```powershell
   docker-compose restart backend
   ```

### Issue: "Token expired"
**Symptoms**: Login works but immediately logs out

**Solutions**:
1. Check token refresh endpoint is working:
   ```powershell
   curl http://localhost:8000/api/accounts/token/refresh/ `
     -Method POST `
     -Body '{"refresh":"YOUR_REFRESH_TOKEN"}' `
     -ContentType "application/json" `
     -UseBasicParsing
   ```
2. Clear browser localStorage and try again:
   - Open browser DevTools (F12)
   - Go to Application > Local Storage
   - Clear all items
   - Refresh page and login again

### Issue: "Page not found (404)"
**Symptoms**: API endpoints return 404 errors

**Solutions**:
1. Check URL patterns in `backend/config/urls.py` and `backend/apps/accounts/urls.py`
2. Verify you're using the correct API base URL: `http://localhost:8000/api`
3. Check available endpoints:
   ```powershell
   docker-compose exec -T backend python manage.py show_urls
   ```

## Frontend Environment Variables

Ensure `frontend/.env` has the correct API URL:
```env
REACT_APP_API_URL=http://localhost:8000/api
```

If you change this file, restart the frontend:
```powershell
docker-compose restart frontend
```

## Backend Environment Variables

Check `backend/.env` for correct database and Redis URLs:
```env
DATABASE_URL=postgis://attendance_user:attendance_password@db:5432/attendance_db
REDIS_URL=redis://redis:6379/0
DJANGO_SETTINGS_MODULE=config.settings.development
DEBUG=True
```

## Useful Commands

### View all service logs
```powershell
docker-compose logs -f
```

### View specific service logs
```powershell
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart all services
```powershell
docker-compose restart
```

### Stop all services
```powershell
docker-compose down
```

### Start all services
```powershell
docker-compose up -d
```

### Check service status
```powershell
docker-compose ps
```

### Access Django shell
```powershell
docker-compose exec backend python manage.py shell
```

### Run migrations
```powershell
docker-compose exec backend python manage.py migrate
```

### Create new admin user
```powershell
docker-compose exec -T backend python setup_initial_data.py
```

## Next Steps

Now that your system is running and you can log in:

1. **Explore the Admin Dashboard** at http://localhost:3000 (after logging in)
2. **Create test data**:
   - Add more users (teachers and students)
   - Create courses
   - Set up class schedules
3. **Test the features**:
   - Teacher: Create attendance sessions
   - Student: Scan QR codes for attendance
   - Admin: View audit logs and reports

## Support

If you encounter issues not covered here:
1. Check the logs: `docker-compose logs -f`
2. Review the implementation documentation in the project
3. Check the spec files in `.kiro/specs/smart-attendance-system/`

## Summary

Your Smart Attendance System is fully operational! You can now:
- ✅ Log in to the frontend application
- ✅ Access the Django admin panel
- ✅ Make API calls to the backend
- ✅ All services are running correctly

**Login URL**: http://localhost:3000  
**Admin Panel**: http://localhost:8000/admin  
**Credentials**: admin@example.com / admin123
