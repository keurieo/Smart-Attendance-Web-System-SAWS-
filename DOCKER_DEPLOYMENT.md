# Docker Deployment Guide

This guide covers deploying the Smart Attendance System using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available
- 10GB free disk space

## Quick Start (Development)

1. **Clone the repository and navigate to the project directory**

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and update values as needed for your environment.

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

6. **Access the application**
   - Frontend: http://localhost
   - Backend API: http://localhost/api
   - Django Admin: http://localhost/admin

## Architecture

The Docker setup includes the following services:

- **db**: PostgreSQL 14 with PostGIS extension
- **redis**: Redis 7 for caching and rate limiting
- **backend**: Django application with Gunicorn
- **frontend**: React application (dev server or nginx)
- **nginx**: Reverse proxy and load balancer

## Development vs Production

### Development Mode (Default)

Uses `docker-compose.yml` with:
- Hot reload for both frontend and backend
- Source code mounted as volumes
- Debug mode enabled
- Development Dockerfile for frontend (npm start)
- Exposed ports for direct service access

### Production Mode

Uses `docker-compose.yml` + `docker-compose.prod.yml` with:
- Optimized production builds
- No source code mounting
- Debug mode disabled
- Multi-stage frontend build with nginx
- SSL/TLS termination
- Enhanced security headers

## Production Deployment

### 1. Prepare Environment

Create a production `.env` file:

```bash
cp .env.example .env
```

Update the following critical values:

```env
# Database
POSTGRES_PASSWORD=<strong-random-password>

# Django
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<generate-strong-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Frontend
REACT_APP_API_URL=https://yourdomain.com/api
FRONTEND_DOCKERFILE=Dockerfile
NODE_ENV=production
```

### 2. Generate Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Set Up SSL Certificates

See `nginx/ssl/README.md` for detailed instructions.

For Let's Encrypt:
```bash
sudo certbot certonly --standalone -d yourdomain.com
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
```

### 4. Build and Start Services

```bash
# Build images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 5. Initialize Database

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Create superuser
docker-compose exec backend python manage.py createsuperuser
```

### 6. Verify Deployment

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs -f

# Test health endpoints
curl http://localhost/health
curl http://localhost/api/health/
```

## Common Commands

### Service Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a specific service
docker-compose restart backend

# View logs
docker-compose logs -f [service_name]

# View service status
docker-compose ps
```

### Database Operations

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create migrations
docker-compose exec backend python manage.py makemigrations

# Access database shell
docker-compose exec db psql -U attendance_user -d attendance_db

# Backup database
docker-compose exec db pg_dump -U attendance_user attendance_db > backup.sql

# Restore database
docker-compose exec -T db psql -U attendance_user attendance_db < backup.sql
```

### Backend Operations

```bash
# Django shell
docker-compose exec backend python manage.py shell

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Run tests
docker-compose exec backend pytest

# Check code quality
docker-compose exec backend flake8 apps config
```

### Frontend Operations

```bash
# Install new package
docker-compose exec frontend npm install <package-name>

# Run linter
docker-compose exec frontend npm run lint

# Build production bundle
docker-compose exec frontend npm run build
```

## Scaling

### Horizontal Scaling

Scale backend workers:
```bash
docker-compose up -d --scale backend=3
```

Update nginx upstream configuration to load balance across multiple backend instances.

### Resource Limits

Add resource limits in `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Monitoring

### Health Checks

All services include health checks:

```bash
# Check health status
docker-compose ps

# View health check logs
docker inspect --format='{{json .State.Health}}' attendance_backend
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Metrics

For production monitoring, integrate with:
- Prometheus for metrics collection
- Grafana for visualization
- ELK stack for log aggregation

## Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec db pg_dump -U attendance_user attendance_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Restore from backup
gunzip -c backup_20231115_120000.sql.gz | docker-compose exec -T db psql -U attendance_user attendance_db
```

### Volume Backup

```bash
# Backup volumes
docker run --rm -v attendance_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore volumes
docker run --rm -v attendance_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose logs [service_name]

# Check service status
docker-compose ps

# Rebuild service
docker-compose up -d --build [service_name]
```

### Database Connection Issues

```bash
# Check database is running
docker-compose ps db

# Test database connection
docker-compose exec backend python manage.py dbshell

# Check database logs
docker-compose logs db
```

### Permission Issues

```bash
# Fix ownership of volumes
docker-compose exec backend chown -R appuser:appuser /app

# Reset volumes (WARNING: deletes data)
docker-compose down -v
docker-compose up -d
```

### Out of Memory

```bash
# Check resource usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
# Or add resource limits to docker-compose.yml
```

### SSL Certificate Issues

```bash
# Verify certificate files exist
ls -la nginx/ssl/

# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect localhost:443
```

## Security Best Practices

1. **Never commit secrets to version control**
   - Use `.env` files (excluded in `.gitignore`)
   - Use Docker secrets for sensitive data

2. **Use strong passwords**
   - Database passwords
   - Django SECRET_KEY
   - Admin user passwords

3. **Keep images updated**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

4. **Enable SSL/TLS in production**
   - Use valid certificates from trusted CA
   - Enable HSTS headers (configured in nginx.prod.conf)

5. **Limit exposed ports**
   - Only expose nginx ports (80, 443) in production
   - Use internal networking for service communication

6. **Run containers as non-root**
   - Backend Dockerfile includes non-root user
   - Frontend nginx runs as nginx user

7. **Regular backups**
   - Automate database backups
   - Store backups securely off-site

## Performance Optimization

### Database

- Enable connection pooling (configured in Django settings)
- Regular VACUUM and ANALYZE operations
- Monitor slow queries

### Caching

- Redis caching enabled for API responses
- Static file caching via nginx
- Browser caching headers configured

### Frontend

- Production build minifies and optimizes code
- Gzip compression enabled in nginx
- Static assets served with long cache headers

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        run: |
          ssh user@server 'cd /app && git pull && docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build'
```

## Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review documentation in `/docs`
- Open an issue on GitHub

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [NGINX Documentation](https://nginx.org/en/docs/)
