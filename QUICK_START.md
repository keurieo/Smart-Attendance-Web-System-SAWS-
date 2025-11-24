# Quick Start Guide

## TL;DR - Get Testing in 3 Steps

```powershell
# 1. Start Docker Desktop (manually)

# 2. Run this command
.\run-tests.ps1

# 3. Review results
```

That's it!

---

## What's the Problem?

Your system needs **GDAL** (a geospatial library) to run. It's not installed on Windows.

**Solution**: Use Docker - it has GDAL pre-installed.

---

## Detailed Steps

### Step 1: Start Docker Desktop

1. Open Docker Desktop application
2. Wait for "Docker Desktop is running" message
3. Verify: Open PowerShell and run `docker ps`

### Step 2: Run Tests

```powershell
.\run-tests.ps1
```

This script will:
- ✅ Build containers (includes GDAL)
- ✅ Start database and Redis
- ✅ Run migrations
- ✅ Execute all tests
- ✅ Show results

### Step 3: Review Results

The script will show:
- ✅ Green = Tests passed
- ❌ Red = Tests failed (note which ones)

---

## If Docker Isn't Available

### Alternative: Install GDAL Manually

1. Download: https://trac.osgeo.org/osgeo4w/
2. Install GDAL package
3. Add to PATH: `C:\OSGeo4W\bin`
4. Run: `cd backend && python -m pytest -v`

**Note**: This takes 30-60 minutes vs 10 minutes with Docker

---

## After Tests Run

### All Tests Pass ✅

Your system works! Access it at:
- Backend: http://localhost:8000
- Admin: http://localhost:8000/admin
- Frontend: http://localhost:3000

### Some Tests Fail ❌

1. Note which tests failed
2. Check error messages
3. Read `TEST_REPORT.md` for details
4. Fix issues and re-run tests

---

## Common Issues

### "Docker is not running"
- Start Docker Desktop application
- Wait for full initialization
- Try again

### "Cannot find docker-compose"
- Docker Desktop includes docker-compose
- Restart Docker Desktop
- Check Docker Desktop settings

### "Port already in use"
```powershell
# Stop existing containers
docker-compose down

# Try again
.\run-tests.ps1
```

---

## Useful Commands

```powershell
# View running containers
docker ps

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Run specific test
docker-compose exec backend python -m pytest apps/attendance/tests/test_token_services.py -v

# Access Django shell
docker-compose exec backend python manage.py shell

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

---

## Files to Read

1. **`TESTING_COMPLETE_SUMMARY.md`** - Full explanation
2. **`ISSUES_SUMMARY.md`** - Detailed issue analysis
3. **`TEST_REPORT.md`** - Test execution details
4. **`run-tests.ps1`** - The test script

---

## Need More Help?

Check these files:
- `ISSUES_SUMMARY.md` - Troubleshooting guide
- `TESTING_AND_FIXES.md` - Testing specification
- `README.md` - Project documentation

---

**Bottom Line**: Start Docker Desktop, run `.\run-tests.ps1`, review results. That's all you need to do!
