# Design Document

## Overview

The Smart Attendance Web System is a full-stack web application built with Django REST Framework (backend) and React with Tailwind CSS (frontend). The system uses PostgreSQL with PostGIS extension for geospatial data storage and queries. Authentication is handled via JWT tokens (access + refresh). The architecture follows a RESTful API design with role-based access control (RBAC) and comprehensive audit logging.

### Technology Stack

**Backend:**
- Django 4.2+ with Django REST Framework
- PostgreSQL 14+ with PostGIS extension
- djangorestframework-simplejwt for JWT authentication
- Gunicorn as WSGI server
- Redis for caching and rate limiting
- Celery for background tasks (optional)

**Frontend:**
- React 18+
- Tailwind CSS for styling
- React Query for data fetching and caching
- html5-qrcode or zxing-js for QR scanning
- Leaflet for map visualization

**Infrastructure:**
- Docker and Docker Compose for containerization
- NGINX as reverse proxy and TLS termination
- GitHub Actions for CI/CD

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Teacher    │  │   Student    │  │    Admin     │      │
│  │   Web App    │  │   Web App    │  │   Web App    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │ HTTPS/TLS
                    ┌────────▼────────┐
                    │  NGINX Reverse  │
                    │     Proxy       │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
┌─────────▼─────────┐ ┌─────▼──────┐ ┌────────▼────────┐
│  Django REST API  │ │   Redis    │ │  Static Files   │
│   (Gunicorn)      │ │  (Cache)   │ │   (Frontend)    │
└─────────┬─────────┘ └────────────┘ └─────────────────┘
          │
          │
┌─────────▼──────────────────────────────────────────────┐
│              PostgreSQL + PostGIS                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │  Users   │ │ Courses  │ │Sessions  │ │ Audit    │ │
│  │  Roles   │ │Schedules │ │ Records  │ │  Logs    │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
└────────────────────────────────────────────────────────┘
```

### Backend Application Structure

Django project organized into focused apps:

```
backend/
├── config/                 # Project settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/          # Authentication, users, roles
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── permissions.py
│   │   └── tests/
│   ├── academics/         # Courses, enrollments, schedules
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── tests/
│   ├── attendance/        # Sessions, tokens, records
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services.py    # Business logic
│   │   └── tests/
│   ├── geo/              # Location utilities
│   │   ├── utils.py       # Haversine, validation
│   │   └── tests/
│   ├── reports/          # Analytics and exports
│   │   ├── views.py
│   │   ├── renderers.py   # CSV renderer
│   │   └── tests/
│   └── audit/            # Audit logging
│       ├── models.py
│       ├── middleware.py
│       └── tests/
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
└── manage.py
```

### Frontend Application Structure

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── teacher/
│   │   │   ├── CreateSessionModal.jsx
│   │   │   ├── SessionDetail.jsx
│   │   │   ├── QRViewer.jsx
│   │   │   └── AttendanceList.jsx
│   │   ├── student/
│   │   │   ├── ScanPage.jsx
│   │   │   ├── QRScanner.jsx
│   │   │   ├── ManualCodeEntry.jsx
│   │   │   └── AttendanceHistory.jsx
│   │   ├── admin/
│   │   │   ├── UserManagement.jsx
│   │   │   ├── CourseManagement.jsx
│   │   │   ├── AuditLog.jsx
│   │   │   └── AttendanceOverride.jsx
│   │   └── shared/
│   │       ├── DataTable.jsx
│   │       ├── Modal.jsx
│   │       ├── Toast.jsx
│   │       └── MapPreview.jsx
│   ├── pages/
│   │   ├── TeacherDashboard.jsx
│   │   ├── StudentDashboard.jsx
│   │   └── AdminDashboard.jsx
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useGeolocation.js
│   │   └── useQRScanner.js
│   ├── services/
│   │   └── api.js          # Axios instance
│   ├── context/
│   │   └── AuthContext.jsx
│   ├── utils/
│   │   ├── storage.js
│   │   └── validators.js
│   └── App.jsx
├── package.json
└── tailwind.config.js
```

## Components and Interfaces

### Backend Components

#### 1. Authentication System

**Models:**
- `User` (extends AbstractBaseUser): id, email, password_hash, full_name, role, institution, is_active, created_at, last_login
- `Role`: id, name (admin/teacher/student)
- `TeacherProfile`: user_id, employee_id, department_id, office_location
- `StudentProfile`: user_id, roll_number, enrollment_year, department_id

**Key Services:**
- JWT token generation and validation
- Password hashing (bcrypt/argon2)
- Role-based permission checking

**Permissions Classes:**
- `IsAdmin`: Allows only admin users
- `IsTeacher`: Allows only teacher users
- `IsTeacherForCourse`: Allows teacher assigned to specific course
- `IsStudentEnrolled`: Allows student enrolled in specific course

#### 2. Attendance Session Management

**Models:**
- `AttendanceSession`: id, course, schedule, created_by, start_at, end_at, teacher_location (PointField), radius_meters, status, notes
- `QRToken`: id, session, token (unique), code6, created_at, expires_at, is_revoked
- `AttendanceRecord`: id, session, student, marked_at, method, token, student_location (PointField), distance_meters, status, reason

**Key Services:**
- `SessionCreationService`:
  - Validates teacher assignment to course
  - Captures teacher geolocation
  - Generates cryptographically secure token (HMAC-SHA256 or JWT)
  - Generates 6-digit fallback code
  - Creates session and token records
  
- `AttendanceMarkingService`:
  - Validates token (exists, not expired, not revoked)
  - Validates time window (current time within session start/end)
  - Captures student geolocation
  - Calculates distance using Haversine formula
  - Validates distance against radius
  - Creates attendance record with appropriate status
  - Prevents duplicate submissions (unique constraint)

#### 3. Geolocation Services

**Location Validation Algorithm:**

```python
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two points on Earth using Haversine formula.
    Returns distance in meters.
    """
    R = 6371000  # Earth radius in meters
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = (math.sin(dphi/2) ** 2 + 
         math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def validate_location(student_lat, student_lon, teacher_lat, teacher_lon, 
                     radius_meters, accuracy=None):
    """
    Validate if student location is within allowed radius of teacher location.
    Returns (is_valid, distance_meters, reason)
    """
    # Check for invalid coordinates
    if (student_lat == 0.0 and student_lon == 0.0):
        return False, None, "Invalid location data"
    
    # Check accuracy if provided
    if accuracy and accuracy > 100:
        return False, None, "Location accuracy insufficient"
    
    # Calculate distance
    distance = haversine_distance(teacher_lat, teacher_lon, 
                                  student_lat, student_lon)
    
    # Validate against radius
    if distance <= radius_meters:
        return True, distance, None
    else:
        return False, distance, "Outside allowed radius"
```

**Anti-Fraud Detection:**
- Detect identical coordinates across multiple students
- Flag submissions with large client-server time delta
- Track device fingerprints and flag suspicious patterns
- Monitor for improbable location changes (speed analysis)

#### 4. QR Token Generation

**Token Structure (JWT approach):**

```python
import jwt
import secrets
from datetime import datetime, timedelta

def generate_qr_token(session_id, expires_at, secret_key):
    """
    Generate cryptographically secure JWT token for attendance session.
    """
    nonce = secrets.token_urlsafe(16)
    
    payload = {
        'session_id': session_id,
        'nonce': nonce,
        'iat': datetime.utcnow(),
        'exp': expires_at,
        'type': 'attendance_qr'
    }
    
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token, nonce

def generate_6digit_code():
    """
    Generate random 6-digit numeric code.
    """
    return f"{secrets.randbelow(1000000):06d}"

def verify_qr_token(token, secret_key):
    """
    Verify and decode JWT token.
    Returns (is_valid, payload, error_message)
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return True, payload, None
    except jwt.ExpiredSignatureError:
        return False, None, "Token expired"
    except jwt.InvalidTokenError:
        return False, None, "Invalid token"
```

#### 5. Audit Logging System

**Model:**
- `AuditLog`: id, performed_by, action, target_table, target_id, old_data (JSONB), new_data (JSONB), performed_at

**Middleware:**
- Automatically logs all model changes
- Captures user context from request
- Stores before/after state as JSON

**Logged Operations:**
- User CRUD operations
- Attendance record overrides
- Session creation and modification
- Role changes
- Course and enrollment changes

### Frontend Components

#### 1. Authentication Flow

**Components:**
- `LoginForm`: Email/password input, JWT token storage
- `ProtectedRoute`: Route wrapper that checks authentication
- `AuthContext`: Global auth state (user, role, tokens)

**Flow:**
1. User submits credentials
2. API returns access + refresh tokens
3. Store tokens in localStorage
4. Set Authorization header for subsequent requests
5. Auto-refresh on token expiration

#### 2. Teacher Session Creation

**Components:**
- `CreateSessionModal`: Form for session parameters
- `QRViewer`: Displays QR code and 6-digit code
- `SessionCountdown`: Visual timer for session expiration

**Flow:**
1. Teacher selects course and schedule
2. System requests geolocation permission
3. Capture teacher coordinates
4. Submit session creation request with location
5. Display generated QR code and 6-digit code
6. Show countdown timer
7. Allow session extension or early termination

**Geolocation Capture:**
```javascript
const useGeolocation = () => {
  const [location, setLocation] = useState(null);
  const [error, setError] = useState(null);
  
  const getCurrentLocation = () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation not supported'));
        return;
      }
      
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          };
          setLocation(coords);
          resolve(coords);
        },
        (error) => {
          setError(error.message);
          reject(error);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0
        }
      );
    });
  };
  
  return { location, error, getCurrentLocation };
};
```

#### 3. Student QR Scanning

**Components:**
- `ScanPage`: Main scanning interface
- `QRScanner`: Camera-based QR scanner
- `ManualCodeEntry`: Fallback 6-digit input
- `AttendanceResult`: Success/failure feedback

**Flow:**
1. Student opens scan page
2. Request camera permission
3. Scan QR code or enter 6-digit code
4. Request geolocation permission
5. Capture student coordinates
6. Submit attendance with token + location
7. Display result (success with distance, or rejection with reason)

**QR Scanner Implementation:**
```javascript
import { Html5QrcodeScanner } from 'html5-qrcode';

const QRScanner = ({ onScanSuccess, onScanError }) => {
  const scannerRef = useRef(null);
  
  useEffect(() => {
    const scanner = new Html5QrcodeScanner(
      "qr-reader",
      { 
        fps: 10, 
        qrbox: { width: 250, height: 250 },
        aspectRatio: 1.0
      },
      false
    );
    
    scanner.render(
      (decodedText) => {
        onScanSuccess(decodedText);
        scanner.clear();
      },
      (error) => {
        // Handle scan errors silently
      }
    );
    
    scannerRef.current = scanner;
    
    return () => {
      scanner.clear();
    };
  }, []);
  
  return <div id="qr-reader"></div>;
};
```

#### 4. Admin Management Interface

**Components:**
- `UserManagement`: CRUD for users
- `CourseManagement`: CRUD for courses and enrollments
- `AttendanceOverride`: Override attendance with reason
- `AuditLog`: Searchable audit trail

**Key Features:**
- Data tables with pagination, sorting, filtering
- Modal forms for create/edit operations
- Confirmation dialogs for destructive actions
- Real-time validation feedback

## Data Models

### Core Entity Relationships

```
Institution (1) ──< (N) User
User (1) ──< (N) TeacherProfile
User (1) ──< (N) StudentProfile
User (1) ──< (N) Course (as instructor)
Course (1) ──< (N) Schedule
Course (1) ──< (N) Enrollment >── (N) Student
Course (1) ──< (N) AttendanceSession
AttendanceSession (1) ──< (N) QRToken
AttendanceSession (1) ──< (N) AttendanceRecord >── (1) Student
User (1) ──< (N) AuditLog (as performer)
User (1) ──< (N) LocationSnapshot
User (1) ──< (N) Device
```

### Database Schema Highlights

**Geospatial Fields:**
- Use PostGIS `GEOGRAPHY(POINT)` type for location storage
- Stores coordinates as (longitude, latitude) in WGS84
- Enables efficient spatial queries with GIST indexes

**Indexes:**
- `users.role_id`, `users.email` (unique)
- `attendance_sessions.course_id`, `attendance_sessions.start_at`
- `attendance_records.session_id`, `attendance_records.student_id`
- `attendance_records(session_id, student_id)` unique constraint
- `qr_tokens.token` (unique), `qr_tokens.session_id`
- GIST indexes on geography columns for spatial queries

**Constraints:**
- Foreign keys with appropriate CASCADE/PROTECT rules
- Unique constraints on email, enrollment pairs, session-student pairs
- Check constraints on radius_meters (10-500 range)
- NOT NULL constraints on critical fields

## Error Handling

### Backend Error Responses

**Standard Error Format:**
```json
{
  "error_code": "ATTENDANCE_001",
  "message": "Outside allowed radius",
  "details": {
    "distance_meters": 75.3,
    "allowed_radius": 50,
    "session_id": 123
  },
  "timestamp": "2025-11-13T09:05:23Z"
}
```

**Error Categories:**

1. **Authentication Errors (AUTH_xxx)**
   - AUTH_001: Invalid credentials
   - AUTH_002: Token expired
   - AUTH_003: Insufficient permissions

2. **Validation Errors (VAL_xxx)**
   - VAL_001: Missing required field
   - VAL_002: Invalid format
   - VAL_003: Constraint violation

3. **Attendance Errors (ATT_xxx)**
   - ATT_001: Outside allowed radius
   - ATT_002: Outside time window
   - ATT_003: Token expired
   - ATT_004: Duplicate submission
   - ATT_005: Location accuracy insufficient

4. **Business Logic Errors (BIZ_xxx)**
   - BIZ_001: Teacher not assigned to course
   - BIZ_002: Student not enrolled in course
   - BIZ_003: Session already expired

### Frontend Error Handling

**Error Display Strategy:**
- Toast notifications for transient errors
- Inline validation messages for form errors
- Modal dialogs for critical errors requiring acknowledgment
- Retry mechanisms for network failures

**User-Friendly Messages:**
- Technical errors translated to plain language
- Actionable guidance (e.g., "Please enable location services")
- Contact support option for unrecoverable errors

## Testing Strategy

### Backend Testing

**Unit Tests:**
- Model validation logic
- Haversine distance calculation
- Token generation and verification
- Permission classes
- Serializer validation

**Integration Tests:**
- API endpoint flows (create session → scan → record created)
- Authentication and authorization
- Database constraints and transactions
- Geospatial queries

**Test Coverage Goals:**
- Minimum 80% code coverage
- 100% coverage for critical paths (attendance marking, token validation)

**Example Test Cases:**
```python
class AttendanceMarkingTests(APITestCase):
    def test_successful_attendance_within_radius(self):
        # Create session with teacher location
        # Submit student attendance within radius
        # Assert attendance record created with status='present'
        
    def test_rejected_attendance_outside_radius(self):
        # Create session with teacher location
        # Submit student attendance outside radius
        # Assert response status 400 with reason
        
    def test_duplicate_attendance_prevented(self):
        # Submit attendance twice for same student-session
        # Assert second submission returns 400
        
    def test_expired_token_rejected(self):
        # Create session with past end_at
        # Submit attendance
        # Assert token expired error
```

### Frontend Testing

**Component Tests:**
- Render tests for all major components
- User interaction simulations (button clicks, form submissions)
- Mock API responses

**Integration Tests:**
- End-to-end flows using Cypress or Playwright
- Teacher creates session → Student scans → Attendance recorded
- Admin override flow

**Accessibility Tests:**
- Keyboard navigation
- Screen reader compatibility
- WCAG 2.1 AA compliance

## Security Considerations

### Transport Security
- Enforce HTTPS/TLS 1.3 for all connections
- HSTS headers with long max-age
- Secure cookie flags (HttpOnly, Secure, SameSite)

### Authentication Security
- JWT tokens with short expiration (15 minutes access, 7 days refresh)
- Refresh token rotation on use
- Token revocation list for logout
- Password requirements: min 8 chars, complexity rules
- Rate limiting on login endpoint (5 attempts per 15 minutes)

### API Security
- CORS configuration (whitelist allowed origins)
- CSRF protection for state-changing operations
- Input validation and sanitization
- SQL injection prevention (parameterized queries)
- XSS prevention (output encoding)

### Rate Limiting
- Global: 100 requests/minute per IP
- Authentication: 5 requests/15 minutes per IP
- Attendance submission: 10 requests/minute per student
- Implemented using Redis with sliding window algorithm

### Data Privacy
- Geolocation data retention policy (180 days)
- PII encryption at rest (optional)
- Audit log access restricted to admins
- GDPR compliance: data export and deletion capabilities

### Anti-Fraud Measures
- Device fingerprinting
- Anomaly detection (identical coordinates, impossible speeds)
- Admin review queue for flagged submissions
- Token replay prevention (nonce tracking)

## Performance Optimization

### Database Optimization
- Connection pooling (pgBouncer)
- Query optimization with EXPLAIN ANALYZE
- Appropriate indexes on frequently queried columns
- Partitioning for large tables (attendance_records by date)
- Read replicas for reporting queries

### Caching Strategy
- Redis caching for:
  - User sessions and permissions
  - Course rosters (5 minute TTL)
  - Active sessions list (1 minute TTL)
- HTTP caching headers for static assets
- Query result caching for expensive reports

### API Performance
- Pagination for list endpoints (default 50 items)
- Field filtering (allow clients to request specific fields)
- Bulk operations where appropriate
- Async processing for heavy operations (CSV exports)

### Frontend Optimization
- Code splitting and lazy loading
- Image optimization and lazy loading
- Service worker for offline capability (optional)
- React Query for intelligent data caching
- Debouncing for search inputs

## Deployment Architecture

### Container Setup

**Docker Compose (Development):**
```yaml
version: '3.8'
services:
  db:
    image: postgis/postgis:14-3.3
    environment:
      POSTGRES_DB: attendance_db
      POSTGRES_USER: attendance_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7-alpine
    
  backend:
    build: ./backend
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./backend:/app
    environment:
      DATABASE_URL: postgis://attendance_user:secure_password@db:5432/attendance_db
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      - db
      - redis
    
  frontend:
    build: ./frontend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
```

### Production Deployment

**Infrastructure:**
- Kubernetes cluster or managed container service (ECS, Cloud Run)
- Managed PostgreSQL with PostGIS (RDS, Cloud SQL)
- Managed Redis (ElastiCache, Memorystore)
- CDN for static assets (CloudFront, Cloud CDN)
- Load balancer with SSL termination

**Scaling Strategy:**
- Horizontal scaling of API servers (stateless)
- Database read replicas for reporting
- Redis cluster for high availability
- Auto-scaling based on CPU/memory metrics

### CI/CD Pipeline

**GitHub Actions Workflow:**
1. Lint and type-check (flake8, mypy, ESLint)
2. Run unit tests with coverage report
3. Build Docker images
4. Push to container registry
5. Deploy to staging environment
6. Run integration tests
7. Manual approval gate
8. Deploy to production
9. Run smoke tests
10. Rollback on failure

## Monitoring and Observability

### Logging
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Centralized logging (ELK stack, CloudWatch, Stackdriver)
- Log retention: 30 days for INFO, 90 days for ERROR

### Metrics
- Application metrics: request rate, latency, error rate
- Business metrics: sessions created, attendance marked, rejection rate
- Infrastructure metrics: CPU, memory, disk, network
- Custom metrics: average distance, location accuracy distribution

### Alerting
- High error rate (>5% of requests)
- Slow response time (p95 >2 seconds)
- Database connection pool exhaustion
- Failed authentication spike (potential attack)
- Disk space low (<20% free)

### Health Checks
- `/api/health` endpoint returning:
  - Database connectivity
  - Redis connectivity
  - Disk space
  - Memory usage
- Kubernetes liveness and readiness probes

## Operational Procedures

### Backup and Recovery
- Automated daily database backups
- Point-in-time recovery capability
- Backup retention: 30 days
- Regular restore testing (monthly)

### Data Retention
- Attendance records: indefinite (or per institution policy)
- Location snapshots: 180 days
- Audit logs: 1 year
- Expired QR tokens: 7 days after expiration

### Maintenance Windows
- Database maintenance: Weekly, off-peak hours
- Application updates: Rolling deployment (zero downtime)
- Emergency patches: Immediate deployment with rollback plan

### Disaster Recovery
- RTO (Recovery Time Objective): 4 hours
- RPO (Recovery Point Objective): 1 hour
- Multi-region deployment for critical institutions (optional)
- Documented runbooks for common failure scenarios
