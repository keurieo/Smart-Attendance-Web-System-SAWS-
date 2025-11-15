# Technology Stack

## Backend

- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: PostgreSQL 14+ with PostGIS extension for geospatial queries
- **Cache/Queue**: Redis 7
- **Authentication**: JWT via django-rest-framework-simplejwt
- **Python Version**: 3.11+

### Backend Dependencies

- `django-environ` for environment configuration
- `django-redis` for caching
- `django-ratelimit` for rate limiting
- `django-cors-headers` for CORS handling
- `gunicorn` for production WSGI server

### Code Quality Tools

- **Linting**: flake8 (configured in `.flake8`)
- **Formatting**: black (line length: 120)
- **Import Sorting**: isort (black profile)
- **Type Checking**: mypy
- **Testing**: pytest with pytest-django

## Frontend

- **Framework**: React 18.2+
- **Styling**: Tailwind CSS 3.3+
- **Data Fetching**: TanStack React Query (v5)
- **HTTP Client**: Axios
- **Routing**: React Router v6
- **QR Code**: qrcode.react for generation, html5-qrcode for scanning
- **Maps**: Leaflet with react-leaflet

### Frontend Code Quality

- **Linting**: ESLint (react-app config)
- **Formatting**: Prettier

## Infrastructure

- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: NGINX
- **CI/CD**: GitHub Actions

## Common Commands

### Backend

```bash
# Development server
cd backend
python manage.py runserver

# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser

# Testing
pytest

# Code quality
flake8 apps config
black apps config
isort apps config
mypy apps
```

### Frontend

```bash
# Development server
cd frontend
npm start

# Build for production
npm run build

# Testing
npm test

# Code quality
npm run lint
npm run format
```

### Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service_name]

# Execute commands in container
docker-compose exec backend python manage.py [command]
docker-compose exec frontend npm [command]

# Stop services
docker-compose down

# Rebuild services
docker-compose up -d --build
```

## Environment Configuration

- Backend: `backend/.env` (use `.env.example` as template)
- Frontend: `frontend/.env` (use `.env.example` as template)
- Settings module: `config.settings.development` or `config.settings.production`
