# Monitoring and Logging Implementation

This document describes the monitoring and logging features implemented for the Smart Attendance System.

## Structured Logging

### Overview

The system now uses structured JSON logging with request ID tracking for distributed tracing. This makes logs easier to parse, search, and analyze in production environments.

### Features

1. **Request ID Tracking**: Every request gets a unique request ID that's tracked throughout the request lifecycle
2. **JSON Formatting**: Production logs are output in JSON format for easy parsing by log aggregation tools
3. **Colored Console Output**: Development logs use colored output for better readability
4. **Log Levels by Environment**: Different log levels for development vs production

### Components

#### RequestIDMiddleware

Located in `apps/audit/logging_middleware.py`, this middleware:
- Generates or extracts request IDs from the `X-Request-ID` header
- Stores the request ID in thread-local storage
- Adds the request ID to response headers
- Makes request IDs available to all log statements

#### Custom Formatters

Located in `apps/audit/formatters.py`:

1. **JSONFormatter**: Outputs structured JSON logs with:
   - Timestamp (ISO 8601 format)
   - Log level
   - Logger name, module, function, line number
   - Message
   - Request ID
   - Exception details (if present)
   - Extra fields (user info, request info)

2. **ColoredConsoleFormatter**: Development-friendly colored output with:
   - Color-coded log levels
   - Request ID prefix (first 8 characters)
   - Human-readable format

### Configuration

#### Development (`config/settings/development.py`)

- Uses `ColoredConsoleFormatter` for console output
- Log level: DEBUG for app code, INFO for Django
- Includes SQL query logging

#### Production (`config/settings/production.py`)

- Uses `JSONFormatter` for all output
- Log level: INFO for app code, WARNING for Django
- Includes file logging with rotation (10MB files, 10 backups)
- Logs to `/var/log/attendance/app.log` (configurable via `LOG_FILE_PATH` env var)

### Usage Examples

```python
import logging

logger = logging.getLogger(__name__)

# Basic logging
logger.info("User logged in successfully")

# Logging with extra context
logger.info("Attendance marked", extra={
    'extra_data': {
        'session_id': session.id,
        'student_id': student.id,
        'distance': distance_meters
    }
})

# Error logging with exception
try:
    # some code
except Exception as e:
    logger.error("Failed to process attendance", exc_info=True)
```

### JSON Log Format Example

```json
{
  "timestamp": "2025-11-15T10:30:45.123456Z",
  "level": "INFO",
  "logger": "apps.attendance.views",
  "module": "views",
  "function": "mark_attendance",
  "line": 145,
  "message": "Attendance marked successfully",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "extra": {
    "session_id": 123,
    "student_id": 456,
    "distance": 45.3
  }
}
```

## Health Check Endpoints

### Overview

The system provides three health check endpoints for monitoring and orchestration:

1. `/api/admin/health/` - Comprehensive health check
2. `/api/admin/health/ready/` - Readiness probe
3. `/api/admin/health/live/` - Liveness probe

### Endpoints

#### 1. Health Check (`/api/admin/health/`)

**Purpose**: Comprehensive system health check for monitoring tools

**Access**: Public (no authentication required)

**Checks**:
- Database connectivity (PostgreSQL)
- Redis connectivity
- PostGIS extension availability

**Response Format**:

```json
{
  "status": "healthy",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection successful"
    },
    "postgis": {
      "status": "healthy",
      "message": "PostGIS available: 3.3.2"
    }
  }
}
```

**Status Codes**:
- `200 OK`: All components healthy
- `503 Service Unavailable`: One or more components unhealthy

#### 2. Readiness Check (`/api/admin/health/ready/`)

**Purpose**: Kubernetes readiness probe - indicates if the app is ready to serve traffic

**Access**: Public (no authentication required)

**Checks**:
- Database connectivity (critical component only)

**Response Format**:

```json
{
  "status": "ready"
}
```

**Status Codes**:
- `200 OK`: Application ready
- `503 Service Unavailable`: Application not ready

#### 3. Liveness Check (`/api/admin/health/live/`)

**Purpose**: Kubernetes liveness probe - indicates if the app is alive

**Access**: Public (no authentication required)

**Checks**:
- None (if Django can respond, it's alive)

**Response Format**:

```json
{
  "status": "alive"
}
```

**Status Codes**:
- `200 OK`: Always (if reachable)

### Usage in Kubernetes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: attendance-backend
spec:
  containers:
  - name: backend
    image: attendance-backend:latest
    livenessProbe:
      httpGet:
        path: /api/admin/health/live/
        port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /api/admin/health/ready/
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 5
```

### Usage in Docker Compose

```yaml
services:
  backend:
    image: attendance-backend:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/admin/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Monitoring Integration

The health check endpoint can be integrated with monitoring tools:

- **Prometheus**: Use blackbox exporter to scrape health endpoint
- **Datadog**: Configure HTTP check on health endpoint
- **AWS CloudWatch**: Use Route 53 health checks
- **Uptime monitoring**: Pingdom, UptimeRobot, etc.

## Environment Variables

### Logging

- `LOG_FILE_PATH`: Path to log file in production (default: `/var/log/attendance/app.log`)
- `DJANGO_SETTINGS_MODULE`: Set to `config.settings.production` for JSON logging

### Health Checks

No additional environment variables required. Health checks use existing database and Redis configurations.

## Best Practices

1. **Request ID Propagation**: Include the `X-Request-ID` header in requests to external services
2. **Structured Logging**: Use the `extra` parameter to add context to log messages
3. **Log Levels**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
4. **Sensitive Data**: Never log passwords, tokens, or PII
5. **Health Check Monitoring**: Set up alerts when health checks fail
6. **Log Retention**: Configure log rotation and retention policies

## Troubleshooting

### Request IDs Not Appearing

- Ensure `RequestIDMiddleware` is in the middleware list
- Check that the middleware is before other middleware that might handle the request

### Health Check Failing

- Check database connectivity: `docker-compose exec backend python manage.py dbshell`
- Check Redis connectivity: `docker-compose exec redis redis-cli ping`
- Review logs for detailed error messages

### JSON Logs Not Formatted

- Verify `DJANGO_SETTINGS_MODULE=config.settings.production`
- Check that `JSONFormatter` is configured in LOGGING settings

## Future Enhancements

Potential improvements for monitoring and logging:

1. **Application Metrics**: Add custom metrics for business events (sessions created, attendance marked)
2. **Distributed Tracing**: Integrate with OpenTelemetry or Jaeger
3. **Log Aggregation**: Set up ELK stack or similar for centralized logging
4. **Performance Monitoring**: Add APM tools like New Relic or Datadog APM
5. **Custom Health Checks**: Add checks for external dependencies (email service, etc.)
