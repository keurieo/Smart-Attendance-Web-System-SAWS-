# Project Structure

## Repository Layout

```
.
├── backend/              # Django backend application
├── frontend/             # React frontend application
├── nginx/                # NGINX reverse proxy configuration
├── .github/workflows/    # CI/CD pipelines
└── docker-compose.yml    # Multi-container orchestration
```

## Backend Structure

```
backend/
├── apps/                 # Django applications (domain-driven)
│   ├── accounts/         # User authentication, roles, permissions
│   ├── academics/        # Courses, enrollments, academic structure
│   ├── attendance/       # Sessions, QR tokens, attendance records
│   ├── audit/            # Audit logging and middleware
│   ├── geo/              # Geolocation utilities and validation
│   └── reports/          # Data export and analytics
├── config/               # Django project configuration
│   ├── settings/         # Split settings (base, development, production)
│   ├── urls.py           # Root URL configuration
│   └── wsgi.py           # WSGI application entry point
├── requirements/         # Python dependencies by environment
├── manage.py             # Django management script
├── pytest.ini            # Pytest configuration
├── pyproject.toml        # Black, isort, mypy configuration
└── .flake8               # Flake8 linting rules
```

### Django App Structure

Each app follows Django conventions:
- `models.py` - Database models
- `views.py` - API views (DRF ViewSets)
- `serializers.py` - DRF serializers
- `urls.py` - URL routing
- `admin.py` - Django admin configuration
- `apps.py` - App configuration
- `permissions.py` - Custom permissions (when needed)
- `services.py` - Business logic layer (when needed)
- `tests/` - Test modules
- `migrations/` - Database migrations

## Frontend Structure

```
frontend/
├── public/               # Static assets
└── src/
    ├── components/       # Reusable React components
    ├── pages/            # Page-level components (routes)
    ├── hooks/            # Custom React hooks
    ├── services/         # API service layer (axios)
    ├── utils/            # Utility functions
    ├── App.js            # Root component
    └── index.js          # Application entry point
```

## Configuration Files

- `.env` files: Environment-specific configuration (not committed)
- `.env.example` files: Template for environment variables
- `docker-compose.yml`: Service orchestration for local development
- `Dockerfile`: Container definitions for backend and frontend
- `nginx.conf`: Reverse proxy and static file serving

## Key Conventions

### Backend

- **Custom User Model**: `accounts.User` (AUTH_USER_MODEL)
- **API Prefix**: All API endpoints under `/api/`
- **Authentication**: JWT tokens via `/api/accounts/token/`
- **Permissions**: Role-based (Admin, Teacher, Student)
- **Line Length**: 120 characters (black, flake8)
- **Imports**: Sorted with isort (black profile)

### Frontend

- **API Base URL**: Configured via `REACT_APP_API_URL` environment variable
- **Routing**: React Router v6 with nested routes
- **State Management**: React Query for server state
- **Styling**: Tailwind utility classes
- **Component Naming**: PascalCase for components, camelCase for utilities

## Database

- **Engine**: PostgreSQL with PostGIS extension
- **Migrations**: Django migrations in each app's `migrations/` folder
- **Spatial Data**: Uses GeoDjango for location-based queries

## Testing

- **Backend**: pytest with fixtures in `conftest.py`
- **Frontend**: React Testing Library with Jest
- **Test Location**: `tests/` folder within each app/module
