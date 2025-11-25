# Docker Usage Guide - Smart Attendance System

This guide explains how to run the Smart Attendance System using Docker.

## Prerequisites

- Docker Desktop installed and running
- At least 4GB of RAM available for Docker
- Ports 80, 3000, 5432, 8000, and 16379 available

## Quick Start

### Option 1: Using PowerShell Scripts (Recommended)

**Start the application:**
```powershell
.\start-docker.ps1
```

**Stop the application:**
```powershell
.\stop-docker.ps1
```

### Option 2: Using Docker Compose Commands

**Start all services:**
```powershell
docker-compose up -d
```

**Stop all services:**
```powershell
docker-compose down
```

**Stop and remove all data (fresh start):**
```powershell
docker-compose down -v
```

## Access Points

Once the containers are running, you can access:

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Django Admin Panel**: http://localhost:8000/admin
- **NGINX Proxy**: http://localhost (port 80)

## Default Credentials

```
Email:    admin@example.com
Password: admin123
```

## Container Architecture

The application consists of 5 Docker containers:

1. **attendance_db** - PostgreSQL 14 with PostGIS extension
2. **attendance_redis** - Redis 7 for caching and rate limiting
3. **attendance_backend** - Django backend API
4. **attendance_frontend** - React frontend application
5. **attendance_nginx** - NGINX reverse proxy

## Common Commands

### View Container Status
```powershell
docker ps
```

### View Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Restart a Service
```powershell
docker-compose restart backend
docker-compose restart frontend
```

### Execute Commands in Containers

**Backend (Django) commands:**
```powershell
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic

# Django shell
docker-compose exec backend python manage.py shell

# Run tests
docker-compose exec backend pytest
```

**Database commands:**
```powershell
# Access PostgreSQL shell
docker-compose exec db psql -U attendance_user -d attendance_db

# Backup database
docker-compose exec db pg_dump -U attendance_user attendance_db > backup.sql

# Restore database
docker-compose exec -T db psql -U attendance_user attendance_db < backup.sql
```

**Frontend commands:**
```powershell
# Install new npm package
docker-compose exec frontend npm install <package-name>

# Run linting
docker-compose exec frontend npm run lint
```

## Troubleshooting

### Containers Won't Start

1. **Check if Docker is running:**
   ```powershell
   docker --version
   ```

2. **Check for port conflicts:**
   ```powershell
   netstat -ano | findstr :80
   netstat -ano | findstr :3000
   netstat -ano | findstr :8000
   ```

3. **View container logs:**
   ```powershell
   docker-compose logs
   ```

### Database Connection Issues

If the backend can't connect to the database:

1. **Check database container is healthy:**
   ```powershell
   docker ps
   ```

2. **Verify environment variables in `.env` file**

3. **Restart containers:**
   ```powershell
   docker-compose down
   docker-compose up -d
   ```

### Backend Shows Errors

1. **Check backend logs:**
   ```powershell
   docker-compose logs backend
   ```

2. **Ensure migrations are applied:**
   ```powershell
   docker-compose exec backend python manage.py migrate
   ```

3. **Restart backend:**
   ```powershell
   docker-compose restart backend
   ```

### Frontend Not Loading

1. **Check frontend logs:**
   ```powershell
   docker-compose logs frontend
   ```

2. **Verify environment variables in `frontend/.env`**

3. **Rebuild frontend container:**
   ```powershell
   docker-compose up -d --build frontend
   ```

### Port Already in Use

If you get a "port already in use" error:

1. **Find the process using the port:**
   ```powershell
   netstat -ano | findstr :<port_number>
   ```

2. **Kill the process or change the port in `.env` file**

3. **For Redis port conflicts (common on Windows):**
   - The `.env` file is already configured to use port 16379 instead of 6379
   - If still having issues, try a different high port number (e.g., 16380)

## Environment Configuration

### Root `.env` File

The root `.env` file contains Docker Compose configuration:

```env
# Database
POSTGRES_DB=attendance_db
POSTGRES_USER=attendance_user
POSTGRES_PASSWORD=change_this_password_in_production
POSTGRES_PORT=5432

# Redis
REDIS_PORT=16379

# Backend
BACKEND_PORT=8000
DJANGO_SETTINGS_MODULE=config.settings.development
DEBUG=True

# Frontend
FRONTEND_PORT=3000
REACT_APP_API_URL=http://localhost/api

# NGINX
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
```

### Backend `.env` File

Located at `backend/.env`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development

# Database (uses Docker service names)
DATABASE_URL=postgis://attendance_user:change_this_password_in_production@db:5432/attendance_db

# Redis (uses Docker service names)
REDIS_URL=redis://redis:6379/0
```

**Important:** The backend `.env` uses Docker service names (`db`, `redis`) instead of `localhost`.

## Development Workflow

### Making Code Changes

The containers are configured with volume mounts, so code changes are reflected immediately:

- **Backend**: Changes to Python files will auto-reload (Django development server)
- **Frontend**: Changes to React files will trigger hot-reload

### Running Tests

```powershell
# Backend tests
docker-compose exec backend pytest

# Frontend tests
docker-compose exec frontend npm test
```

### Database Migrations

After modifying Django models:

```powershell
# Create migrations
docker-compose exec backend python manage.py makemigrations

# Apply migrations
docker-compose exec backend python manage.py migrate
```

## Production Deployment

For production deployment, see:
- `DOCKER_DEPLOYMENT.md` - Production Docker setup
- `PRODUCTION_DEPLOYMENT.md` - General production guide

## Data Persistence

Docker volumes are used for data persistence:

- `postgres_data` - Database data
- `redis_data` - Redis data
- `static_volume` - Django static files
- `media_volume` - User uploaded files

To completely reset the application (delete all data):

```powershell
docker-compose down -v
docker-compose up -d
docker-compose exec backend python setup_initial_data.py
```

## Performance Tips

1. **Allocate more resources to Docker:**
   - Open Docker Desktop → Settings → Resources
   - Increase CPU and Memory allocation

2. **Use Docker BuildKit for faster builds:**
   ```powershell
   $env:DOCKER_BUILDKIT=1
   docker-compose build
   ```

3. **Prune unused Docker resources:**
   ```powershell
   docker system prune -a
   ```

## Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify all containers are running: `docker ps`
3. Review this guide's troubleshooting section
4. Check the main `README.md` for additional documentation

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Documentation](https://docs.djangoproject.com/)
- [React Documentation](https://react.dev/)
