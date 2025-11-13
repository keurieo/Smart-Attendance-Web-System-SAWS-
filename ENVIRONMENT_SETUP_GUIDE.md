# Environment Setup Guide

This guide will help you complete the setup of the Smart Attendance System development environment.

## ✅ Completed Steps

1. **Python Environment**
   - Python 3.12.10 is installed
   - Virtual environment created at `backend/venv`
   - All Python dependencies installed successfully

2. **Environment Files**
   - `backend/.env` created from template
   - `frontend/.env` created from template

3. **Docker**
   - Docker Desktop is installed (version 28.5.2)
   - Docker Compose is available (version 2.40.3)

## 🔧 Next Steps Required

### Step 1: Start Docker Desktop

**Docker Desktop needs to be running** to start PostgreSQL and Redis containers.

1. Open Docker Desktop application
2. Wait for it to fully start (the whale icon should be steady in the system tray)
3. Verify it's running:
   ```powershell
   docker ps
   ```

### Step 2: Start Database Services

Once Docker Desktop is running, start PostgreSQL and Redis:

```powershell
# Start only the database and Redis services
docker-compose up -d db redis
```

This will:
- Start PostgreSQL 14 with PostGIS extension on port 5432
- Start Redis 7 on port 6379

Verify services are running:
```powershell
docker-compose ps
```

### Step 3: Run Database Migrations

Activate the virtual environment and run migrations:

```powershell
# Activate virtual environment
backend\venv\Scripts\activate

# Run migrations
python backend\manage.py migrate

# Create a superuser (admin account)
python backend\manage.py createsuperuser
```

### Step 4: Verify Backend Setup

Test that Django can connect to the database:

```powershell
# Still in virtual environment
python backend\manage.py check
```

If successful, you should see:
```
System check identified no issues (0 silenced).
```

### Step 5: Start Backend Development Server

```powershell
# Still in virtual environment
python backend\manage.py runserver
```

The backend API will be available at: http://localhost:8000

Test the API:
- Admin panel: http://localhost:8000/admin
- API root: http://localhost:8000/api

### Step 6: Setup Frontend (Optional for now)

If you want to run the frontend:

```powershell
# In a new terminal
cd frontend
npm install
npm start
```

The frontend will be available at: http://localhost:3000

## 🔍 Verification Checklist

- [ ] Docker Desktop is running
- [ ] PostgreSQL container is running (`docker-compose ps db`)
- [ ] Redis container is running (`docker-compose ps redis`)
- [ ] Database migrations completed successfully
- [ ] Superuser created
- [ ] Backend server starts without errors
- [ ] Can access admin panel at http://localhost:8000/admin

## 📝 Environment Configuration

### Backend Environment Variables (backend/.env)

The following are already configured:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development
DATABASE_URL=postgis://attendance_user:attendance_password@localhost:5432/attendance_db
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend Environment Variables (frontend/.env)

```env
REACT_APP_API_URL=http://localhost:8000/api
```

## 🐛 Troubleshooting

### Docker Desktop Not Starting

**Issue:** Docker commands fail with connection errors

**Solution:**
1. Open Docker Desktop manually
2. Check system tray for Docker whale icon
3. Wait for it to show "Docker Desktop is running"
4. If it fails to start, restart your computer

### Port Already in Use

**Issue:** Port 5432 or 6379 is already in use

**Solution:**
```powershell
# Check what's using the port
netstat -ano | findstr :5432
netstat -ano | findstr :6379

# Stop the conflicting service or change ports in docker-compose.yml
```

### Database Connection Error

**Issue:** Django can't connect to PostgreSQL

**Solution:**
1. Verify PostgreSQL is running: `docker-compose ps db`
2. Check the DATABASE_URL in `backend/.env`
3. Test connection:
   ```powershell
   docker-compose exec db psql -U attendance_user -d attendance_db
   ```

### Redis Connection Error

**Issue:** Rate limiting or caching doesn't work

**Solution:**
1. Verify Redis is running: `docker-compose ps redis`
2. Test connection:
   ```powershell
   docker-compose exec redis redis-cli ping
   ```
   Should return: `PONG`

### Migration Errors

**Issue:** Migrations fail with errors

**Solution:**
1. Drop and recreate the database:
   ```powershell
   docker-compose down -v
   docker-compose up -d db redis
   python backend\manage.py migrate
   ```

## 🚀 Quick Start Commands

After initial setup, use these commands to start development:

```powershell
# Start database services
docker-compose up -d db redis

# Activate Python environment
backend\venv\Scripts\activate

# Start backend server
python backend\manage.py runserver

# In another terminal, start frontend (optional)
cd frontend
npm start
```

## 📚 Additional Resources

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- PostGIS: https://postgis.net/documentation/
- Redis: https://redis.io/documentation
- Docker: https://docs.docker.com/

## 🎯 Next Development Steps

Once the environment is set up, you can:

1. Review the implementation tasks: `.kiro/specs/smart-attendance-system/tasks.md`
2. Check completed tasks (tasks 1-8 are done)
3. Continue with task 9 or other pending tasks
4. Run tests: `pytest backend/apps`
5. Access the admin panel to create test data

## 💡 Development Tips

1. **Keep Docker Desktop running** during development
2. **Use the virtual environment** for all Python commands
3. **Check logs** if something doesn't work:
   ```powershell
   docker-compose logs db
   docker-compose logs redis
   ```
4. **Run migrations** after pulling new code:
   ```powershell
   python backend\manage.py migrate
   ```
5. **Create test data** using Django admin or fixtures

## 🔐 Security Notes

- The current `.env` files use development credentials
- **Never commit `.env` files** to version control
- Change `SECRET_KEY` before deploying to production
- Use strong passwords for production databases
- Enable HTTPS in production

---

**Status:** Python environment ready ✅ | Docker services need to be started ⏳
