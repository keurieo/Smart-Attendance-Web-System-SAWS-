# How to Run Regression Tests

This guide explains how to run the full regression test suite for the admin panel bug fixes.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose available
- All services configured in `docker-compose.yml`

## Quick Start

### 1. Start Docker Services

```bash
# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs if needed
docker-compose logs -f backend
```

### 2. Run Automated Tests

```bash
# Run full test suite (41 tests)
docker-compose exec backend python -m pytest -v

# Run only audit log tests
docker-compose exec backend python -m pytest apps/audit/tests/test_audit_log_views.py -v

# Run with coverage report
docker-compose exec backend python -m pytest --cov=apps --cov-report=html
```

### 3. Run Static Verification Scripts

These can run without Docker:

```bash
cd backend

# Verify code fixes
python verify_fixes.py

# Verify performance
python verify_performance.py

# Verify error handling
python verify_error_handling.py
```

### 4. Manual Testing

Follow the checklist in `REGRESSION_TEST_CHECKLIST.md`:

#### Test Admin Dashboard
```bash
# Access admin panel
http://localhost:8000/admin/

# Login with admin credentials
# Verify dashboard loads without errors
# Check all metrics display correctly
```

#### Test Audit Log API
```bash
# Test basic endpoint
curl http://localhost:8000/api/admin/audit/

# Test date_from filter
curl "http://localhost:8000/api/admin/audit/?date_from=2025-11-20"

# Test date_to filter
curl "http://localhost:8000/api/admin/audit/?date_to=2025-11-20"

# Test date range
curl "http://localhost:8000/api/admin/audit/?date_from=2025-11-20&date_to=2025-11-22"

# Test invalid date (should not crash)
curl "http://localhost:8000/api/admin/audit/?date_from=invalid-date"
```

## Expected Test Results

### Automated Tests
```
apps/audit/tests/test_audit_log_views.py::test_audit_log_with_null_performed_by PASSED
apps/audit/tests/test_audit_log_views.py::test_filter_by_date_from PASSED
apps/audit/tests/test_audit_log_views.py::test_filter_by_date_range PASSED
apps/audit/tests/test_audit_log_views.py::test_filter_by_date_to PASSED

================================ 41 passed in X.XXs ================================
```

### Static Verification
```
STATIC CODE VERIFICATION - Admin Panel Bug Fixes
============================================================
RESULTS: 31 passed, 0 failed, 0 warnings
```

### Performance Verification
```
PERFORMANCE VERIFICATION - Admin Panel Bug Fixes
============================================================
RESULTS: 12 passed, 0 failed, 0 warnings
```

### Error Handling Verification
```
ERROR HANDLING VERIFICATION - Admin Panel Bug Fixes
============================================================
RESULTS: 21 passed, 0 failed, 0 warnings
```

## Troubleshooting

### Docker Not Running
```bash
# Start Docker Desktop
# Then run:
docker-compose up -d
```

### GDAL Library Error
```bash
# This is expected when running tests without Docker
# Solution: Use Docker environment
docker-compose exec backend python -m pytest
```

### Database Connection Error
```bash
# Ensure PostgreSQL container is running
docker-compose ps

# Restart services if needed
docker-compose restart backend db
```

### Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8000

# Stop the process or change port in docker-compose.yml
```

## Performance Benchmarks

### Expected Performance
- **Admin dashboard load**: < 2 seconds
- **Audit log API response**: < 500ms
- **Date filter response**: < 500ms
- **Database queries per page**: < 20

### Measuring Performance

#### Using Browser DevTools
1. Open Chrome DevTools (F12)
2. Go to Network tab
3. Navigate to admin dashboard
4. Check "Finish" time in Network tab

#### Using curl
```bash
# Measure API response time
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/api/admin/audit/"

# Create curl-format.txt:
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_starttransfer:  %{time_starttransfer}\n
time_total:  %{time_total}\n
```

#### Using Django Debug Toolbar
1. Install: `pip install django-debug-toolbar`
2. Add to INSTALLED_APPS
3. View query count and execution time in toolbar

## Test Coverage

### Areas Covered
- ✅ Date filtering with valid dates
- ✅ Date filtering with invalid dates
- ✅ Date filtering with null values
- ✅ Audit logs with null performed_by
- ✅ Serializer field handling
- ✅ Model field references
- ✅ Admin configurations
- ✅ Template variables
- ✅ URL patterns
- ✅ Permission checks
- ✅ Error handling
- ✅ Performance optimization

### Areas Requiring Manual Testing
- ⏳ User authentication flow
- ⏳ Attendance session creation
- ⏳ QR code generation and scanning
- ⏳ Geolocation validation
- ⏳ Report generation and export
- ⏳ Cross-browser compatibility
- ⏳ Mobile responsiveness

## Continuous Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and run tests
        run: |
          docker-compose up -d
          docker-compose exec -T backend python -m pytest -v
```

## Reporting Issues

If tests fail:

1. **Capture Error Output**
   ```bash
   docker-compose exec backend python -m pytest -v > test_output.txt 2>&1
   ```

2. **Check Logs**
   ```bash
   docker-compose logs backend > backend_logs.txt
   ```

3. **Gather System Info**
   ```bash
   docker --version
   docker-compose --version
   python --version
   ```

4. **Create Issue Report**
   - Test command used
   - Error output
   - Log files
   - System information
   - Steps to reproduce

## Clean Up

```bash
# Stop services
docker-compose down

# Remove volumes (caution: deletes data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Next Steps

After all tests pass:

1. ✅ Review test results
2. ✅ Check performance metrics
3. ✅ Verify error handling
4. ✅ Complete manual testing checklist
5. ✅ Update documentation
6. ✅ Deploy to staging environment
7. ✅ Perform user acceptance testing
8. ✅ Deploy to production

## Support

For questions or issues:
- Check `REGRESSION_VERIFICATION_SUMMARY.md` for detailed results
- Review `REGRESSION_TEST_CHECKLIST.md` for manual testing steps
- Run verification scripts for quick checks
- Check Docker logs for runtime errors

---

**Last Updated**: November 25, 2025
**Status**: Ready for testing
**Confidence**: HIGH
