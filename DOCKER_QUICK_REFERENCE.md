# Docker Quick Reference

Quick reference for common Docker commands used in this project.

## Starting and Stopping

```bash
# Start all services (development)
docker-compose up -d

# Start all services (production)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Restart a specific service
docker-compose restart backend

# Stop a specific service
docker-compose stop backend

# Start a specific service
docker-compose start backend
```

## Building

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build backend

# Build without cache
docker-compose build --no-cache

# Pull latest base images and rebuild
docker-compose pull
docker-compose build
```

## Logs and Monitoring

```bash
# View all logs
docker-compose logs

# Follow logs (live tail)
docker-compose logs -f

# View logs for specific service
docker-compose logs backend

# View last 100 lines
docker-compose logs --tail=100 backend

# Check service status
docker-compose ps

# View resource usage
docker stats
```

## Executing Commands

```bash
# Django management commands
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py shell
docker-compose exec backend python manage.py collectstatic --noinput

# Run tests
docker-compose exec backend pytest
docker-compose exec frontend npm test

# Access bash shell
docker-compose exec backend bash
docker-compose exec frontend sh

# Database shell
docker-compose exec db psql -U attendance_user -d attendance_db

# Redis CLI
docker-compose exec redis redis-cli
```

## Database Operations

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create migrations
docker-compose exec backend python manage.py makemigrations

# Backup database
docker-compose exec db pg_dump -U attendance_user attendance_db > backup.sql

# Restore database
docker-compose exec -T db psql -U attendance_user attendance_db < backup.sql

# Access database shell
docker-compose exec db psql -U attendance_user -d attendance_db
```

## Frontend Operations

```bash
# Install npm package
docker-compose exec frontend npm install <package-name>

# Run linter
docker-compose exec frontend npm run lint

# Format code
docker-compose exec frontend npm run format

# Build production bundle
docker-compose exec frontend npm run build
```

## Cleanup

```bash
# Remove stopped containers
docker-compose rm

# Remove all unused containers, networks, images
docker system prune

# Remove all unused volumes (WARNING: deletes data)
docker volume prune

# Remove specific volume
docker volume rm smart-attendance-web-system-saws-_postgres_data
```

## Troubleshooting

```bash
# View service health status
docker-compose ps

# Inspect container
docker inspect attendance_backend

# View container processes
docker-compose top

# Check container resource usage
docker stats attendance_backend

# Restart unhealthy service
docker-compose restart backend

# Rebuild and restart service
docker-compose up -d --build backend

# View detailed service configuration
docker-compose config
```

## Development Workflow

```bash
# 1. Start services
docker-compose up -d

# 2. Run migrations
docker-compose exec backend python manage.py migrate

# 3. Create superuser
docker-compose exec backend python manage.py createsuperuser

# 4. View logs
docker-compose logs -f

# 5. Make code changes (hot reload enabled)

# 6. Run tests
docker-compose exec backend pytest

# 7. Stop services
docker-compose down
```

## Production Deployment

```bash
# 1. Pull latest code
git pull

# 2. Build images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# 3. Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Run migrations
docker-compose exec backend python manage.py migrate

# 5. Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# 6. Check status
docker-compose ps

# 7. View logs
docker-compose logs -f
```

## Environment Variables

```bash
# View environment variables for a service
docker-compose exec backend env

# Run command with custom environment variable
docker-compose exec -e DEBUG=False backend python manage.py check
```

## Networking

```bash
# List networks
docker network ls

# Inspect network
docker network inspect smart-attendance-web-system-saws-_attendance_network

# Test connectivity between services
docker-compose exec backend ping db
docker-compose exec backend curl http://redis:6379
```

## Volumes

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect smart-attendance-web-system-saws-_postgres_data

# Backup volume
docker run --rm -v smart-attendance-web-system-saws-_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data

# Restore volume
docker run --rm -v smart-attendance-web-system-saws-_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

## Health Checks

```bash
# Check health status
docker-compose ps

# View health check details
docker inspect --format='{{json .State.Health}}' attendance_backend | python -m json.tool

# Test health endpoints
curl http://localhost/health
curl http://localhost/api/health/
```

## Scaling

```bash
# Scale backend to 3 instances
docker-compose up -d --scale backend=3

# View scaled instances
docker-compose ps backend
```

## Tips

- Use `-d` flag to run in detached mode (background)
- Use `-f` flag to follow logs in real-time
- Use `--no-cache` when building to ensure fresh build
- Use `--build` with `up` to rebuild before starting
- Use `--remove-orphans` to clean up old containers
- Always backup data before running `down -v`

## Common Issues

### Port already in use
```bash
# Find process using port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Change port in .env file
BACKEND_PORT=8001
```

### Permission denied
```bash
# Fix ownership
docker-compose exec backend chown -R appuser:appuser /app
```

### Out of disk space
```bash
# Clean up unused resources
docker system prune -a
docker volume prune
```

### Service won't start
```bash
# Check logs
docker-compose logs backend

# Rebuild service
docker-compose up -d --build backend
```
