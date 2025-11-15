# CI/CD Pipeline Documentation

## Overview

The Smart Attendance System uses GitHub Actions for continuous integration and deployment. The pipeline automatically runs on pushes and pull requests to the `main` and `develop` branches.

## Pipeline Stages

### 1. Backend Linting and Tests

**Services:**
- PostgreSQL 14 with PostGIS extension
- Redis 7

**Steps:**
1. **Linting**: Runs flake8 to check code style (max line length: 120)
2. **Type Checking**: Runs mypy for static type analysis (non-blocking)
3. **Testing**: Executes pytest with coverage reporting
   - Minimum coverage threshold: 80%
   - Generates XML coverage report for Codecov
4. **Coverage Upload**: Uploads coverage data to Codecov (if configured)

### 2. Frontend Linting and Tests

**Steps:**
1. **Linting**: Runs ESLint to check code style
2. **Testing**: Executes Jest tests with coverage
   - Coverage thresholds: 80% for branches, functions, lines, and statements
   - Continues on error to allow build to proceed
3. **Coverage Upload**: Uploads coverage data to Codecov (if configured)
4. **Build**: Creates production bundle to verify build process

### 3. Build Docker Images

**Triggered on:** Push events only (not pull requests)

**Backend Image:**
- Built from `backend/Dockerfile`
- Pushed to GitHub Container Registry (ghcr.io)
- Tagged with branch name, commit SHA, and 'latest' (main branch only)
- Uses layer caching for faster builds

**Frontend Image:**
- Built from `frontend/Dockerfile`
- Pushed to GitHub Container Registry (ghcr.io)
- Tagged with branch name, commit SHA, and 'latest' (main branch only)
- Uses layer caching for faster builds

### 4. Code Quality Summary

Provides a summary of all code quality checks performed:
- Backend: flake8, mypy, pytest with 80% coverage
- Frontend: ESLint, Jest with 80% coverage, production build

### 5. Deploy to Registry

**Triggered on:** Push to `main` branch only

Displays deployment information including:
- Image names and registry location
- Tags applied to images
- Instructions for pulling and deploying images

## Coverage Reporting

The pipeline is configured to work with Codecov for coverage tracking:

1. Backend coverage is generated in XML format
2. Frontend coverage is generated in JSON format
3. Both are uploaded with appropriate flags for separate tracking
4. Coverage upload failures are non-blocking

To enable Codecov integration:
1. Sign up at https://codecov.io
2. Connect your GitHub repository
3. No additional secrets needed (uses GITHUB_TOKEN)

## Local Testing

Before pushing, you can run the same checks locally:

### Backend
```bash
cd backend

# Linting
flake8 apps config --max-line-length=120 --exclude=migrations

# Type checking
mypy apps --ignore-missing-imports

# Tests with coverage
pytest --cov=apps --cov-report=term-missing --cov-fail-under=80
```

### Frontend
```bash
cd frontend

# Linting
npm run lint

# Tests with coverage
npm test -- --watchAll=false --coverage
```

## Docker Image Usage

After images are built and pushed, you can pull them:

```bash
# Pull latest images (main branch)
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPO/backend:latest
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPO/frontend:latest

# Pull specific commit
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPO/backend:main-abc1234
docker pull ghcr.io/YOUR_USERNAME/YOUR_REPO/frontend:main-abc1234
```

## Permissions

The workflow requires the following permissions:
- `contents: read` - To checkout code
- `packages: write` - To push Docker images to GitHub Container Registry

These are automatically provided by the `GITHUB_TOKEN` secret.

## Troubleshooting

### Coverage Threshold Failures

If tests fail due to coverage being below 80%:
1. Add more tests to increase coverage
2. Review uncovered code paths
3. Consider if the threshold should be adjusted (update pytest.ini or package.json)

### Type Checking Issues

mypy type checking is non-blocking but warnings should be addressed:
1. Add type hints to function signatures
2. Use `# type: ignore` comments sparingly for unavoidable issues
3. Update mypy configuration in pyproject.toml if needed

### Docker Build Failures

If Docker builds fail:
1. Test locally: `docker build -t test-image ./backend`
2. Check Dockerfile syntax
3. Verify all required files are present
4. Review build logs for specific errors

## Future Enhancements

Potential improvements to consider:
- Add security scanning (Snyk, Trivy)
- Add performance testing
- Add end-to-end tests with Cypress/Playwright
- Add automatic deployment to staging environment
- Add release automation with semantic versioning
