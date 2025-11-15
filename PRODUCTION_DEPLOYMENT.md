# Production Deployment Guide

Complete guide for deploying the Smart Attendance System to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Server Setup](#server-setup)
4. [SSL/TLS Configuration](#ssltls-configuration)
5. [Environment Configuration](#environment-configuration)
6. [Deployment Steps](#deployment-steps)
7. [Post-Deployment Verification](#post-deployment-verification)
8. [Backup and Restore](#backup-and-restore)
9. [Monitoring and Maintenance](#monitoring-and-maintenance)
10. [Scaling](#scaling)
11. [Troubleshooting](#troubleshooting)

## Prerequisites

### Server Requirements

- **Operating System**: Ubuntu 20.04 LTS or later (recommended)
- **CPU**: Minimum 2 cores (4+ recommended)
- **RAM**: Minimum 4GB (8GB+ recommended)
- **Storage**: Minimum 20GB SSD (50GB+ recommended)
- **Network**: Static IP address or domain name

### Required Software

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- Certbot (for Let's Encrypt SSL certificates)

### Domain and DNS

- Registered domain name
- DNS A record pointing to your server IP
- (Optional) DNS AAAA record for IPv6

## Pre-Deployment Checklist

Before deploying to production, ensure you have:

- [ ] Server with required specifications
- [ ] Domain name configured with DNS
- [ ] SSH access to the server
- [ ] Firewall configured (ports 80, 443, 22)
- [ ] SSL certificates obtained or ready to obtain
- [ ] Database backup strategy planned
- [ ] Monitoring solution selected
- [ ] Email service configured (for notifications)
- [ ] Strong passwords generated for all services
- [ ] Django SECRET_KEY generated
- [ ] Environment variables documented

## Server Setup

### 1. Initial Server Configuration

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common git

# Create application user
sudo useradd -m -s /bin/bash appuser
sudo usermod -aG sudo appuser
```

### 2. Install Docker

```bash
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker appuser

# Verify installation
docker --version
docker compose version
```

### 3. Configure Firewall

```bash
# Install UFW (if not already installed)
sudo apt install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### 4. Clone Repository

```bash
# Switch to application user
su - appuser

# Clone repository
cd /home/appuser
git clone <repository-url> smart-attendance
cd smart-attendance
```

## SSL/TLS Configuration

### Option 1: Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt install -y certbot

# Stop any services using port 80
docker-compose down

# Obtain certificate (standalone mode)
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates will be saved to:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem

# Copy certificates to project directory
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
sudo chown -R appuser:appuser nginx/ssl

# Set up automatic renewal
sudo certbot renew --dry-run

# Add renewal hook to copy certificates
sudo tee /etc/letsencrypt/renewal-hooks/deploy/copy-certs.sh > /dev/null <<'EOF'
#!/bin/bash
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /home/appuser/smart-attendance/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /home/appuser/smart-attendance/nginx/ssl/key.pem
chown appuser:appuser /home/appuser/smart-attendance/nginx/ssl/*.pem
docker exec attendance_nginx nginx -s reload
EOF

sudo chmod +x /etc/letsencrypt/renewal-hooks/deploy/copy-certs.sh
```

### Option 2: Custom SSL Certificate

```bash
# Create ssl directory
mkdir -p nginx/ssl

# Copy your certificate files
cp /path/to/your/certificate.crt nginx/ssl/cert.pem
cp /path/to/your/private.key nginx/ssl/key.pem

# Set proper permissions
chmod 600 nginx/ssl/key.pem
chmod 644 nginx/ssl/cert.pem
```

### Option 3: Self-Signed Certificate (Development/Testing Only)

```bash
# Create ssl directory
mkdir -p nginx/ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"

# Set proper permissions
chmod 600 nginx/ssl/key.pem
chmod 644 nginx/ssl/cert.pem
```

## Environment Configuration

### 1. Generate Django SECRET_KEY

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Generate Strong Passwords

```bash
# Generate random password
openssl rand -base64 32
```

### 3. Create Production Environment File

Create `backend/.env`:

```env
# Django Settings
SECRET_KEY=<generated-secret-key-from-step-1>
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database
DATABASE_URL=postgis://attendance_user:<strong-password>@db:5432/attendance_db

# Redis
REDIS_URL=redis://redis:6379/0

# CORS Settings
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email Configuration (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-specific-password>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Security Settings
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Optional: Sentry for error tracking
SENTRY_DSN=<your-sentry-dsn>

# Optional: AWS S3 for static files
USE_S3=False
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AWS_STORAGE_BUCKET_NAME=<your-bucket-name>
AWS_S3_REGION_NAME=us-east-1
```

Create `frontend/.env`:

```env
# API Configuration
REACT_APP_API_URL=https://yourdomain.com/api

# Environment
NODE_ENV=production
```

Create `.env` (root level for Docker Compose):

```env
# PostgreSQL
POSTGRES_DB=attendance_db
POSTGRES_USER=attendance_user
POSTGRES_PASSWORD=<strong-password>

# Application
COMPOSE_PROJECT_NAME=attendance_prod
FRONTEND_DOCKERFILE=Dockerfile
```

### 4. Secure Environment Files

```bash
# Set restrictive permissions
chmod 600 backend/.env frontend/.env .env

# Ensure .env files are in .gitignore
echo "*.env" >> .gitignore
echo "!*.env.example" >> .gitignore
```

## Deployment Steps

### 1. Build Docker Images

```bash
# Build all images
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# This will:
# - Build optimized production frontend with nginx
# - Build backend with Gunicorn
# - Pull PostgreSQL and Redis images
```

### 2. Start Services

```bash
# Start all services in detached mode
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify all services are running
docker compose ps
```

Expected output:
```
NAME                    STATUS              PORTS
attendance_backend      Up (healthy)        8000/tcp
attendance_db           Up (healthy)        5432/tcp
attendance_frontend     Up                  80/tcp
attendance_nginx        Up                  0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
attendance_redis        Up (healthy)        6379/tcp
```

### 3. Initialize Database

```bash
# Run migrations
docker compose exec backend python manage.py migrate

# Create initial data (roles, etc.)
docker compose exec backend python manage.py loaddata initial_data

# Collect static files
docker compose exec backend python manage.py collectstatic --noinput

# Create superuser
docker compose exec backend python manage.py createsuperuser
```

### 4. Verify Deployment

```bash
# Check service health
docker compose ps

# Check logs for errors
docker compose logs backend
docker compose logs frontend
docker compose logs nginx

# Test health endpoint
curl https://yourdomain.com/api/health/
```

## Post-Deployment Verification

### 1. Functional Testing

Test the following functionality:

- [ ] **Homepage loads**: https://yourdomain.com
- [ ] **API responds**: https://yourdomain.com/api/
- [ ] **Admin panel accessible**: https://yourdomain.com/admin
- [ ] **Login works**: Test with superuser credentials
- [ ] **SSL certificate valid**: Check browser padlock icon
- [ ] **HTTPS redirect works**: http://yourdomain.com redirects to https
- [ ] **Static files load**: Check CSS, JS, images
- [ ] **Database connection**: Create test data in admin
- [ ] **Redis connection**: Test rate limiting
- [ ] **Email sending**: Test password reset

### 2. Security Testing

```bash
# Check SSL configuration
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Check security headers
curl -I https://yourdomain.com

# Expected headers:
# - Strict-Transport-Security
# - X-Content-Type-Options
# - X-Frame-Options
# - Content-Security-Policy
```

### 3. Performance Testing

```bash
# Test response time
curl -w "@curl-format.txt" -o /dev/null -s https://yourdomain.com/api/health/

# Create curl-format.txt:
cat > curl-format.txt <<'EOF'
    time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
      time_redirect:  %{time_redirect}\n
   time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
         time_total:  %{time_total}\n
EOF
```

## Backup and Restore

### Automated Backup Setup

#### 1. Create Backup Script

```bash
# Create backup directory
sudo mkdir -p /var/backups/attendance
sudo chown appuser:appuser /var/backups/attendance

# Create backup script
cat > /home/appuser/backup.sh <<'EOF'
#!/bin/bash

# Configuration
BACKUP_DIR="/var/backups/attendance"
PROJECT_DIR="/home/appuser/smart-attendance"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory for today
mkdir -p "$BACKUP_DIR/$DATE"

# Backup database
echo "Backing up database..."
cd "$PROJECT_DIR"
docker compose exec -T db pg_dump -U attendance_user attendance_db | gzip > "$BACKUP_DIR/$DATE/database.sql.gz"

# Backup uploaded files (if any)
echo "Backing up media files..."
docker compose exec -T backend tar czf - /app/media 2>/dev/null > "$BACKUP_DIR/$DATE/media.tar.gz" || true

# Backup environment files
echo "Backing up configuration..."
cp backend/.env "$BACKUP_DIR/$DATE/backend.env"
cp frontend/.env "$BACKUP_DIR/$DATE/frontend.env"
cp .env "$BACKUP_DIR/$DATE/root.env"

# Create backup manifest
echo "Creating manifest..."
cat > "$BACKUP_DIR/$DATE/manifest.txt" <<MANIFEST
Backup Date: $(date)
Database Size: $(du -h "$BACKUP_DIR/$DATE/database.sql.gz" | cut -f1)
Media Size: $(du -h "$BACKUP_DIR/$DATE/media.tar.gz" | cut -f1)
MANIFEST

# Remove old backups
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} + 2>/dev/null || true

# Upload to remote storage (optional)
# aws s3 sync "$BACKUP_DIR/$DATE" s3://your-bucket/backups/$DATE/

echo "Backup completed: $BACKUP_DIR/$DATE"
EOF

chmod +x /home/appuser/backup.sh
```

#### 2. Schedule Automated Backups

```bash
# Add to crontab
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * /home/appuser/backup.sh >> /var/log/attendance-backup.log 2>&1

# Add this line for weekly full backups on Sunday at 3 AM
0 3 * * 0 /home/appuser/backup.sh >> /var/log/attendance-backup.log 2>&1
```

### Manual Backup

```bash
# Navigate to project directory
cd /home/appuser/smart-attendance

# Create backup directory
mkdir -p backups
cd backups

# Backup database
docker compose exec -T db pg_dump -U attendance_user attendance_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup volumes
docker run --rm \
  -v attendance_prod_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres_volume_$(date +%Y%m%d_%H%M%S).tar.gz /data

# Backup environment files
tar czf env_backup_$(date +%Y%m%d_%H%M%S).tar.gz ../backend/.env ../frontend/.env ../.env
```

### Restore from Backup

#### 1. Restore Database

```bash
# Stop application
docker compose down

# Start only database
docker compose up -d db

# Wait for database to be ready
sleep 10

# Drop existing database (WARNING: This deletes all data)
docker compose exec db psql -U attendance_user -d postgres -c "DROP DATABASE IF EXISTS attendance_db;"
docker compose exec db psql -U attendance_user -d postgres -c "CREATE DATABASE attendance_db;"
docker compose exec db psql -U attendance_user -d attendance_db -c "CREATE EXTENSION postgis;"

# Restore from backup
gunzip -c backup_20231115_020000.sql.gz | docker compose exec -T db psql -U attendance_user attendance_db

# Start all services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

#### 2. Restore Media Files

```bash
# Restore media files
gunzip -c media.tar.gz | docker compose exec -T backend tar xzf - -C /
```

#### 3. Restore Environment Files

```bash
# Extract environment files
tar xzf env_backup_20231115_020000.tar.gz

# Copy to correct locations
cp backend/.env ../backend/.env
cp frontend/.env ../frontend/.env
cp .env ../.env

# Restart services
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart
```

### Disaster Recovery

#### Complete System Restore

```bash
# 1. Set up new server (follow Server Setup section)

# 2. Clone repository
git clone <repository-url> smart-attendance
cd smart-attendance

# 3. Restore environment files
tar xzf env_backup.tar.gz

# 4. Start services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d db redis

# 5. Restore database
gunzip -c database_backup.sql.gz | docker compose exec -T db psql -U attendance_user attendance_db

# 6. Start all services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 7. Verify restoration
docker compose ps
curl https://yourdomain.com/api/health/
```

## Monitoring and Maintenance

### Log Management

```bash
# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend

# View last 100 lines
docker compose logs --tail=100 backend

# Save logs to file
docker compose logs > logs_$(date +%Y%m%d).txt

# Configure log rotation
sudo tee /etc/logrotate.d/docker-compose > /dev/null <<'EOF'
/var/lib/docker/containers/*/*.log {
  rotate 7
  daily
  compress
  missingok
  delaycompress
  copytruncate
}
EOF
```

### Health Monitoring

```bash
# Create health check script
cat > /home/appuser/health-check.sh <<'EOF'
#!/bin/bash

# Check if services are running
if ! docker compose ps | grep -q "Up"; then
    echo "ERROR: Some services are down"
    docker compose ps
    exit 1
fi

# Check API health endpoint
if ! curl -f -s https://yourdomain.com/api/health/ > /dev/null; then
    echo "ERROR: API health check failed"
    exit 1
fi

echo "All health checks passed"
EOF

chmod +x /home/appuser/health-check.sh

# Add to crontab for monitoring every 5 minutes
crontab -e
# Add: */5 * * * * /home/appuser/health-check.sh || echo "Health check failed" | mail -s "Attendance System Alert" admin@yourdomain.com
```

### Database Maintenance

```bash
# Vacuum database (reclaim storage)
docker compose exec db psql -U attendance_user -d attendance_db -c "VACUUM ANALYZE;"

# Check database size
docker compose exec db psql -U attendance_user -d attendance_db -c "SELECT pg_size_pretty(pg_database_size('attendance_db'));"

# Check table sizes
docker compose exec db psql -U attendance_user -d attendance_db -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema') ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```

### Updates and Upgrades

```bash
# Pull latest code
cd /home/appuser/smart-attendance
git pull origin main

# Rebuild images
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Run migrations
docker compose exec backend python manage.py migrate

# Restart services with zero downtime
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --no-deps --build backend

# Verify update
docker compose ps
curl https://yourdomain.com/api/health/
```

## Scaling

### Horizontal Scaling

#### Scale Backend Workers

```bash
# Scale backend to 3 instances
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --scale backend=3

# Verify scaling
docker compose ps backend
```

#### Load Balancer Configuration

Update `nginx/nginx.prod.conf`:

```nginx
upstream backend {
    least_conn;
    server backend:8000 max_fails=3 fail_timeout=30s;
    # Add more backend instances
    # server backend_2:8000 max_fails=3 fail_timeout=30s;
    # server backend_3:8000 max_fails=3 fail_timeout=30s;
}
```

### Vertical Scaling

#### Increase Resource Limits

Add to `docker-compose.prod.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
  
  db:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Database Scaling

#### Read Replicas

For high-traffic deployments, set up PostgreSQL read replicas:

```yaml
services:
  db_replica:
    image: postgis/postgis:14-3.3
    environment:
      POSTGRES_DB: attendance_db
      POSTGRES_USER: attendance_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_replica_data:/var/lib/postgresql/data
```

Configure Django to use read replicas in `config/settings/production.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'attendance_db',
        'USER': 'attendance_user',
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': '5432',
    },
    'replica': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'attendance_db',
        'USER': 'attendance_user',
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'db_replica',
        'PORT': '5432',
    }
}

DATABASE_ROUTERS = ['config.db_router.ReplicaRouter']
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose logs [service_name]

# Check service status
docker compose ps

# Rebuild service
docker compose up -d --build [service_name]

# Check resource usage
docker stats
```

### SSL Certificate Issues

```bash
# Verify certificate files
ls -la nginx/ssl/

# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Renew Let's Encrypt certificate
sudo certbot renew --force-renewal
```

### Database Performance Issues

```bash
# Check active connections
docker compose exec db psql -U attendance_user -d attendance_db -c "SELECT count(*) FROM pg_stat_activity;"

# Check slow queries
docker compose exec db psql -U attendance_user -d attendance_db -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"

# Analyze query performance
docker compose exec backend python manage.py shell
>>> from django.db import connection
>>> from django.db import reset_queries
>>> # Run your query
>>> print(connection.queries)
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Check Docker disk usage
docker system df

# Clean up unused resources
docker system prune -a --volumes

# Remove old logs
sudo journalctl --vacuum-time=7d

# Remove old backups
find /var/backups/attendance -type d -mtime +30 -exec rm -rf {} +
```

### Memory Issues

```bash
# Check memory usage
free -h

# Check container memory usage
docker stats

# Restart services to free memory
docker compose restart

# Increase swap space (if needed)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Application Errors

```bash
# Check Django logs
docker compose logs backend | grep ERROR

# Check nginx logs
docker compose logs nginx | grep error

# Access Django shell for debugging
docker compose exec backend python manage.py shell

# Run Django checks
docker compose exec backend python manage.py check --deploy
```

## Security Best Practices

1. **Keep software updated**
   ```bash
   sudo apt update && sudo apt upgrade -y
   docker compose pull
   ```

2. **Use strong passwords**
   - Database passwords: 32+ characters
   - Django SECRET_KEY: 50+ characters
   - User passwords: Enforce complexity requirements

3. **Enable firewall**
   ```bash
   sudo ufw enable
   sudo ufw status
   ```

4. **Regular security audits**
   ```bash
   # Check for security updates
   sudo apt list --upgradable
   
   # Scan for vulnerabilities
   docker scan attendance_backend
   ```

5. **Monitor logs for suspicious activity**
   ```bash
   # Check failed login attempts
   docker compose exec backend python manage.py shell
   >>> from apps.audit.models import AuditLog
   >>> AuditLog.objects.filter(action='login_failed').count()
   ```

6. **Implement rate limiting**
   - Already configured in the application
   - Monitor Redis for rate limit hits

7. **Regular backups**
   - Automated daily backups
   - Test restore procedures monthly
   - Store backups off-site

## Support and Resources

- **Documentation**: Check project documentation in `/docs`
- **Logs**: `docker compose logs -f`
- **Health Check**: https://yourdomain.com/api/health/
- **Admin Panel**: https://yourdomain.com/admin
- **Issue Tracker**: GitHub repository issues

## Rollback Procedure

If deployment fails:

```bash
# 1. Stop current deployment
docker compose down

# 2. Checkout previous version
git log --oneline  # Find previous commit
git checkout <previous-commit-hash>

# 3. Restore database backup
gunzip -c /var/backups/attendance/latest/database.sql.gz | docker compose exec -T db psql -U attendance_user attendance_db

# 4. Rebuild and start
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 5. Verify rollback
curl https://yourdomain.com/api/health/
```

## Conclusion

This guide covers the complete production deployment process. For additional help:

- Review the development setup guide: `DEVELOPMENT_SETUP.md`
- Check Docker quick reference: `DOCKER_QUICK_REFERENCE.md`
- Review project requirements: `.kiro/specs/smart-attendance-system/requirements.md`
- Review project design: `.kiro/specs/smart-attendance-system/design.md`

Remember to:
- Test thoroughly before deploying to production
- Keep backups current and test restore procedures
- Monitor application health and performance
- Keep all software updated
- Follow security best practices
