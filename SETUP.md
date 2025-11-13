# Setup Instructions

This document provides detailed setup instructions for the Smart Attendance System.

## Local Development Setup

### Backend Setup

1. **Install Python 3.11+**
   - Download from https://www.python.org/downloads/
   - Verify installation: `python --version`

2. **Install PostgreSQL with PostGIS**
   - Option 1: Use Docker (recommended)
     ```bash
     docker run -d --name attendance_db \
       -e POSTGRES_DB=attendance_db \
       -e POSTGRES_USER=attendance_user \
       -e POSTGRES_PASSWORD=attendance_password \
       -p 5432:5432 \
       postgis/postgis:14-3.3
     ```
   
   - Option 2: Install locally
     - PostgreSQL: https://www.postgresql.org/download/
     - PostGIS: https://postgis.net/install/

3. **Install Redis**
   - Option 1: Use Docker (recommended)
     ```bash
     docker run -d --name attendance_redis \
       -p 6379:6379 \
       redis:7-alpine
     ```
   
   - Option 2: Install locally
     - Redis: https://redis.io/download

4. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements/development.txt
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis URLs
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start development server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Install Node.js 18+**
   - Download from https://nodejs.org/
   - Verify installation: `node --version`

2. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API URL
   ```

4. **Start development server**
   ```bash
   npm start
   ```

## Docker Setup (Recommended)

1. **Install Docker and Docker Compose**
   - Docker Desktop: https://www.docker.com/products/docker-desktop

2. **Create environment files**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Run migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - Admin: http://localhost:8000/admin

## Production Deployment

### Environment Variables

Required environment variables for production:

**Backend (.env)**
```
SECRET_KEY=<generate-strong-secret-key>
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgis://user:password@host:5432/dbname
REDIS_URL=redis://host:6379/0
CORS_ALLOWED_ORIGINS=https://your-domain.com
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
SENTRY_DSN=<optional-sentry-dsn>
```

**Frontend (.env)**
```
REACT_APP_API_URL=https://your-domain.com/api
```

### SSL/TLS Configuration

1. Obtain SSL certificates (Let's Encrypt recommended)
2. Place certificates in `nginx/ssl/`
3. Update `nginx/nginx.conf` to enable HTTPS server block
4. Restart nginx: `docker-compose restart nginx`

### Database Backup

Set up automated backups:

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U attendance_user attendance_db | gzip > backup_$DATE.sql.gz
EOF

chmod +x backup.sh

# Add to crontab for daily backups
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

### Monitoring

1. **Application Logs**
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

2. **Database Logs**
   ```bash
   docker-compose logs -f db
   ```

3. **Health Check**
   - Backend: http://your-domain.com/api/health (to be implemented in task 23.2)

## Troubleshooting

### Database Connection Issues

1. Check PostgreSQL is running:
   ```bash
   docker-compose ps db
   ```

2. Verify connection string in `.env`

3. Test connection:
   ```bash
   docker-compose exec backend python manage.py dbshell
   ```

### Redis Connection Issues

1. Check Redis is running:
   ```bash
   docker-compose ps redis
   ```

2. Test connection:
   ```bash
   docker-compose exec redis redis-cli ping
   ```

### Frontend Build Issues

1. Clear node_modules and reinstall:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Clear cache:
   ```bash
   npm cache clean --force
   ```

### Port Conflicts

If ports 80, 443, 3000, 5432, 6379, or 8000 are in use:

1. Stop conflicting services
2. Or modify ports in `docker-compose.yml`

## Next Steps

After setup is complete:

1. Review the requirements document: `.kiro/specs/smart-attendance-system/requirements.md`
2. Review the design document: `.kiro/specs/smart-attendance-system/design.md`
3. Follow the implementation tasks: `.kiro/specs/smart-attendance-system/tasks.md`
4. Start with task 2: Implement database models and migrations
