# Smart Attendance System

A web-based attendance management system using QR codes and geolocation verification for educational institutions.

## Features

- **QR Code Attendance**: Teachers create time-limited QR codes for attendance sessions
- **Geolocation Verification**: Validates student physical presence within configurable radius
- **Multi-Role Support**: Admin, Teacher, and Student roles with appropriate permissions
- **Comprehensive Audit Trail**: Tracks all system operations with detailed logging
- **Real-time Validation**: Prevents fraud with rate limiting and anti-spoofing measures
- **Reporting**: Export attendance data in CSV format with filtering options

## Technology Stack

### Backend
- Django 4.2+ with Django REST Framework
- PostgreSQL 14+ with PostGIS extension
- Redis for caching and rate limiting
- JWT authentication

### Frontend
- React 18+
- Tailwind CSS
- React Query for data fetching
- Leaflet for map visualization

### Infrastructure
- Docker & Docker Compose
- NGINX reverse proxy
- GitHub Actions CI/CD

## Getting Started

### Quick Start

For detailed setup instructions, see:
- **Development Setup**: [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)
- **Production Deployment**: [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
- **Deploy to Vercel/Railway**: [QUICK_DEPLOY.md](QUICK_DEPLOY.md) ⚡ (15 minutes)

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd smart-attendance-system
```

2. Create environment files:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

3. Update the `.env` files with your configuration.

4. Start the services:
```bash
docker-compose up -d
```

5. Run database migrations:
```bash
docker-compose exec backend python manage.py migrate
```

6. Create a superuser:
```bash
docker-compose exec backend python manage.py createsuperuser
```

7. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- Admin Panel: http://localhost:8000/admin

For more detailed instructions, troubleshooting, and production deployment, see [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md).

## Development Setup

### Backend Development

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements/development.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start development server:
```bash
python manage.py runserver
```

### Frontend Development

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm start
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Code Quality

### Backend
```bash
# Linting
flake8 apps config

# Formatting
black apps config
isort apps config

# Type checking
mypy apps
```

### Frontend
```bash
# Linting
npm run lint

# Formatting
npm run format
```

## Project Structure

```
.
├── backend/
│   ├── apps/
│   │   ├── accounts/      # User authentication and management
│   │   ├── academics/     # Courses and enrollments
│   │   ├── attendance/    # Attendance sessions and records
│   │   ├── audit/         # Audit logging
│   │   ├── geo/           # Geolocation utilities
│   │   └── reports/       # Reporting and analytics
│   ├── config/            # Django settings
│   └── requirements/      # Python dependencies
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/    # React components
│       ├── pages/         # Page components
│       ├── hooks/         # Custom hooks
│       ├── services/      # API services
│       └── utils/         # Utility functions
├── nginx/                 # NGINX configuration
└── docker-compose.yml     # Docker services configuration
```

## Documentation

### Setup and Deployment

- **[DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)** - Complete development environment setup guide
  - Local development with and without Docker
  - Database migrations and initialization
  - Environment configuration
  - Troubleshooting common issues

- **[PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)** - Production deployment guide
  - Server setup and configuration
  - SSL/TLS setup with Let's Encrypt
  - Docker Compose production deployment
  - Backup and restore procedures
  - Monitoring and maintenance
  - Scaling strategies

### Quick References

- **[DOCKER_QUICK_REFERENCE.md](DOCKER_QUICK_REFERENCE.md)** - Common Docker commands
- **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - Docker-specific deployment details

### Project Specifications

- **[Requirements](.kiro/specs/smart-attendance-system/requirements.md)** - Detailed system requirements
- **[Design](.kiro/specs/smart-attendance-system/design.md)** - System architecture and design
- **[Tasks](.kiro/specs/smart-attendance-system/tasks.md)** - Implementation task list

### Implementation Guides

- **[backend/MODELS_IMPLEMENTATION.md](backend/MODELS_IMPLEMENTATION.md)** - Database models documentation
- **[frontend/AUTHENTICATION_IMPLEMENTATION.md](frontend/AUTHENTICATION_IMPLEMENTATION.md)** - Frontend authentication
- **[frontend/TEACHER_SESSION_INTERFACE_IMPLEMENTATION.md](frontend/TEACHER_SESSION_INTERFACE_IMPLEMENTATION.md)** - Teacher interface
- **[frontend/STUDENT_QR_SCANNING_IMPLEMENTATION.md](frontend/STUDENT_QR_SCANNING_IMPLEMENTATION.md)** - Student scanning interface
- **[frontend/ERROR_HANDLING_AND_VALIDATION_IMPLEMENTATION.md](frontend/ERROR_HANDLING_AND_VALIDATION_IMPLEMENTATION.md)** - Error handling

## API Documentation

API documentation will be available at `/api/docs` once implemented in task 24.3.

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

See LICENSE file for details.

## Support

For issues and questions, please create an issue in the repository.
