# Development Setup Guide

Complete guide for setting up the Smart Attendance System development environment.

## Prerequisites

### Required Software

- **Docker Desktop** 20.10+ (includes Docker Compose)
  - Download: https://www.docker.com/products/docker-desktop
  - Minimum 4GB RAM allocated to Docker
  - 10GB free disk space

- **Git** (for version control)
  - Download: https://git-scm.com/downloads

### Optional (for local development without Docker)

- **Python** 3.11+
- **Node.js** 18+
- **PostgreSQL** 14+ with PostGIS extension
- **Redis** 7+

## Quick Start with Docker (Recommended)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd smart-attendance-system
```

### 2. Create Environment Files

```bash
# Copy environment templates
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 3. Configure Environment Variables

Edit `backend/.env`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (matches docker-compose.yml)
DATABASE_URL=postgis://attendance_user:attendance_password@db:5432/attendance_db

# Redis (matches docker-compose.yml)
REDIS_URL=redis://redis:6379/0

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Email (optional for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Edit `frontend/.env`:

```env
# API URL
REACT_APP_API_URL=http://localhost:8000/api
```

### 4. Start All Services

```bash
# Start all containers in detached mode
docker-compose up -d
```

This will start:
- PostgreSQL 14 with PostGIS (port 5432)
- Redis 7 (port 6379)
- Django backend (port 8000)
- React frontend (port 3000)
- NGINX reverse proxy (port 80)

### 5. Initialize the Database

```bash
# Run database migrations
docker-compose exec backend python manage.py migrate

# Create a superuser account
docker-compose exec backend python manage.py createsuperuser
```

Follow the prompts to create your admin account:
- Email: your-email@example.com
- Password: (choose a strong password)
- Full name: Your Name

### 6. Verify Installation

Check that all services are running:

```bash
docker-compose ps
```

All services should show status "Up" or "Up (healthy)".

### 7. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Django Admin**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/docs (if implemented)

### 8. Create Test Data (Optional)

Log in to Django admin (http://localhost:8000/admin) and create:

1. **Institution**: Add your institution with timezone
2. **Roles**: Admin, Teacher, Student (may be pre-created)
3. **Users**: Create test users for each role
4. **Courses**: Add test courses
5. **Enrollments**: Enroll students in courses

## Local Development (Without Docker)

### Backend Setup

#### 1. Install Python Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements/development.txt
```

#### 2. Install and Configure PostgreSQL with PostGIS

**Option A: Using Docker (Recommended)**

```bash
docker run -d --name attendance_db \
  -e POSTGRES_DB=attendance_db \
  -e POSTGRES_USER=attendance_user \
  -e POSTGRES_PASSWORD=attendance_password \
  -p 5432:5432 \
  postgis/postgis:14-3.3
```

**Option B: Local Installation**

1. Install PostgreSQL 14+: https://www.postgresql.org/download/
2. Install PostGIS extension: https://postgis.net/install/
3. Create database:

```sql
CREATE DATABASE attendance_db;
CREATE USER attendance_user WITH PASSWORD 'attendance_password';
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO attendance_user;

-- Connect to attendance_db
\c attendance_db

-- Enable PostGIS extension
CREATE EXTENSION postgis;
```

#### 3. Install and Configure Redis

**Option A: Using Docker (Recommended)**

```bash
docker run -d --name attendance_redis \
  -p 6379:6379 \
  redis:7-alpine
```

**Option B: Local Installation**

- Windows: https://github.com/microsoftarchive/redis/releases
- macOS: `brew install redis`
- Linux: `sudo apt-get install redis-server`

#### 4. Configure Environment

Edit `backend/.env`:

```env
DATABASE_URL=postgis://attendance_user:attendance_password@localhost:5432/attendance_db
REDIS_URL=redis://localhost:6379/0
```

#### 5. Run Migrations

```bash
python manage.py migrate
```

#### 6. Create Superuser

```bash
python manage.py createsuperuser
```

#### 7. Start Development Server

```bash
python manage.py runserver
```

Backend will be available at http://localhost:8000

### Frontend Setup

#### 1. Install Node.js Dependencies

```bash
cd frontend

# Install packages
npm install
```

#### 2. Configure Environment

Edit `frontend/.env`:

```env
REACT_APP_API_URL=http://localhost:8000/api
```

#### 3. Start Development Server

```bash
npm start
```

Frontend will be available at http://localhost:3000

## Database Migrations

### Understanding Migrations

Django migrations are version control for your database schema. Each migration file represents a change to the database structure.

### Migration Files Location

Migrations are located in each app's `migrations/` directory:

```
backend/apps/
├── accounts/migrations/
│   └── 0001_initial.py
├── academics/migrations/
│   └── 0001_initial.py
├── attendance/migrations/
│   └── 0001_initial.py
└── audit/migrations/
    └── 0001_initial.py
```

### Common Migration Commands

```bash
# Apply all pending migrations
python manage.py migrate

# Create new migrations after model changes
python manage.py makemigrations

# Show migration status
python manage.py showmigrations

# View SQL for a migration (without applying)
python manage.py sqlmigrate accounts 0001

# Revert to a specific migration
python manage.py migrate accounts 0001

# Revert all migrations for an app
python manage.py migrate accounts zero
```

### Initial Database Schema

The initial migrations create the following tables:

**accounts app:**
- `accounts_institution` - Educational institutions
- `accounts_role` - User roles (Admin, Teacher, Student)
- `accounts_user` - Custom user model with authentication
- `accounts_teacherprofile` - Teacher-specific data
- `accounts_studentprofile` - Student-specific data

**academics app:**
- `academics_course` - Course information
- `academics_enrollment` - Student course enrollments
- `academics_schedule` - Class schedules with location

**attendance app:**
- `attendance_attendancesession` - Attendance sessions created by teachers
- `attendance_qrtoken` - QR tokens and 6-digit codes
- `attendance_attendancerecord` - Student attendance records
- `attendance_device` - Device tracking for fraud prevention
- `attendance_locationsnapshot` - Location history

**audit app:**
- `audit_auditlog` - System-wide audit trail

### Resetting the Database

If you need to start fresh:

**With Docker:**

```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Start services again
docker-compose up -d

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

**Without Docker:**

```bash
# Drop and recreate database
dropdb attendance_db
createdb attendance_db

# Enable PostGIS
psql -d attendance_db -c "CREATE EXTENSION postgis;"

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Environment Variables Reference

### Backend Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Django secret key for cryptographic signing | - | Yes |
| `DEBUG` | Enable debug mode | `False` | No |
| `DJANGO_SETTINGS_MODULE` | Django settings module | `config.settings.development` | Yes |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost` | Yes |
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `REDIS_URL` | Redis connection string | - | Yes |
| `CORS_ALLOWED_ORIGINS` | Comma-separated CORS origins | - | Yes |
| `EMAIL_BACKEND` | Email backend class | `console.EmailBackend` | No |
| `EMAIL_HOST` | SMTP server host | - | No |
| `EMAIL_PORT` | SMTP server port | `587` | No |
| `EMAIL_USE_TLS` | Use TLS for email | `True` | No |
| `EMAIL_HOST_USER` | SMTP username | - | No |
| `EMAIL_HOST_PASSWORD` | SMTP password | - | No |

### Frontend Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `REACT_APP_API_URL` | Backend API base URL | - | Yes |
| `NODE_ENV` | Node environment | `development` | No |

## Development Workflow

### Daily Development

```bash
# 1. Start services (if using Docker)
docker-compose up -d

# 2. View logs (optional)
docker-compose logs -f backend

# 3. Make code changes
# - Backend: Changes auto-reload with Django dev server
# - Frontend: Changes auto-reload with React dev server

# 4. Run tests
docker-compose exec backend pytest
docker-compose exec frontend npm test

# 5. Stop services when done
docker-compose down
```

### After Pulling New Code

```bash
# 1. Pull latest changes
git pull

# 2. Rebuild containers (if Dockerfile changed)
docker-compose up -d --build

# 3. Run new migrations
docker-compose exec backend python manage.py migrate

# 4. Install new dependencies (if requirements changed)
docker-compose exec backend pip install -r requirements/development.txt
docker-compose exec frontend npm install
```

### Creating New Features

```bash
# 1. Create a new branch
git checkout -b feature/your-feature-name

# 2. Make model changes in apps/*/models.py

# 3. Create migrations
docker-compose exec backend python manage.py makemigrations

# 4. Apply migrations
docker-compose exec backend python manage.py migrate

# 5. Write tests in apps/*/tests/

# 6. Run tests
docker-compose exec backend pytest

# 7. Commit changes
git add .
git commit -m "Add your feature"
git push origin feature/your-feature-name
```

## Testing

### Backend Tests

```bash
# Run all tests
docker-compose exec backend pytest

# Run specific app tests
docker-compose exec backend pytest apps/accounts/

# Run specific test file
docker-compose exec backend pytest apps/accounts/tests/test_models.py

# Run with coverage
docker-compose exec backend pytest --cov=apps --cov-report=html

# Run with verbose output
docker-compose exec backend pytest -v
```

### Frontend Tests

```bash
# Run all tests
docker-compose exec frontend npm test

# Run tests in watch mode
docker-compose exec frontend npm test -- --watch

# Run with coverage
docker-compose exec frontend npm test -- --coverage
```

## Code Quality

### Backend Code Quality

```bash
# Linting with flake8
docker-compose exec backend flake8 apps config

# Format code with black
docker-compose exec backend black apps config

# Sort imports with isort
docker-compose exec backend isort apps config

# Type checking with mypy
docker-compose exec backend mypy apps

# Run all quality checks
docker-compose exec backend sh -c "flake8 apps config && black --check apps config && isort --check apps config && mypy apps"
```

### Frontend Code Quality

```bash
# Linting with ESLint
docker-compose exec frontend npm run lint

# Format code with Prettier
docker-compose exec frontend npm run format

# Check formatting
docker-compose exec frontend npm run format:check
```

## Troubleshooting

### Docker Desktop Not Running

**Symptom:** `docker` commands fail with connection errors

**Solution:**
1. Open Docker Desktop application
2. Wait for it to fully start (whale icon steady in system tray)
3. Verify: `docker ps`

### Port Already in Use

**Symptom:** Error binding to port 3000, 8000, 5432, or 6379

**Solution:**

```bash
# Find process using port (Windows)
netstat -ano | findstr :8000

# Find process using port (macOS/Linux)
lsof -i :8000

# Stop the conflicting service or change port in docker-compose.yml
```

### Database Connection Failed

**Symptom:** Django can't connect to PostgreSQL

**Solution:**

```bash
# Check PostgreSQL is running
docker-compose ps db

# Check logs
docker-compose logs db

# Verify DATABASE_URL in backend/.env

# Test connection
docker-compose exec db psql -U attendance_user -d attendance_db
```

### Redis Connection Failed

**Symptom:** Rate limiting or caching doesn't work

**Solution:**

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping
# Should return: PONG

# Check logs
docker-compose logs redis
```

### Migration Errors

**Symptom:** Migrations fail with database errors

**Solution:**

```bash
# Check migration status
docker-compose exec backend python manage.py showmigrations

# Try fake migration (if table already exists)
docker-compose exec backend python manage.py migrate --fake

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
docker-compose exec backend python manage.py migrate
```

### Frontend Build Errors

**Symptom:** npm install or build fails

**Solution:**

```bash
# Clear node_modules and reinstall
docker-compose exec frontend rm -rf node_modules package-lock.json
docker-compose exec frontend npm install

# Or rebuild container
docker-compose up -d --build frontend
```

### Permission Denied Errors

**Symptom:** Cannot write files or access directories

**Solution:**

```bash
# Fix ownership (Linux/macOS)
sudo chown -R $USER:$USER .

# Or run as root in container
docker-compose exec -u root backend chown -R appuser:appuser /app
```

## Additional Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **React Documentation**: https://react.dev/
- **PostGIS Documentation**: https://postgis.net/documentation/
- **Docker Documentation**: https://docs.docker.com/
- **Project Requirements**: `.kiro/specs/smart-attendance-system/requirements.md`
- **Project Design**: `.kiro/specs/smart-attendance-system/design.md`
- **Implementation Tasks**: `.kiro/specs/smart-attendance-system/tasks.md`

## Next Steps

After completing the setup:

1. **Explore the Admin Panel**: http://localhost:8000/admin
2. **Review the API**: http://localhost:8000/api
3. **Create Test Data**: Add institutions, users, courses
4. **Run Tests**: Verify everything works
5. **Start Development**: Follow the implementation tasks

## Getting Help

- Check existing documentation in the project
- Review error logs: `docker-compose logs -f`
- Search for similar issues in the repository
- Create an issue with detailed error information
