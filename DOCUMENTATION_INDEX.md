# Documentation Index

Complete index of all documentation for the Smart Attendance System.

## Getting Started

Start here if you're new to the project:

1. **[README.md](README.md)** - Project overview and quick start
2. **[DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)** - Set up your development environment
3. **[.kiro/specs/smart-attendance-system/requirements.md](.kiro/specs/smart-attendance-system/requirements.md)** - Understand system requirements
4. **[.kiro/specs/smart-attendance-system/design.md](.kiro/specs/smart-attendance-system/design.md)** - Learn the system architecture

## Setup and Configuration

### Development Environment

- **[DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)** - Complete development setup guide
  - Prerequisites and installation
  - Docker setup (recommended)
  - Local setup without Docker
  - Database migrations
  - Environment variables
  - Troubleshooting

- **[ENVIRONMENT_SETUP_GUIDE.md](ENVIRONMENT_SETUP_GUIDE.md)** - Environment-specific setup notes
  - Python environment setup
  - Docker Desktop configuration
  - Service verification

### Production Deployment

- **[PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)** - Production deployment guide
  - Server requirements and setup
  - SSL/TLS configuration
  - Environment configuration
  - Deployment steps
  - Backup and restore
  - Monitoring and maintenance
  - Scaling strategies
  - Security best practices

### Docker

- **[DOCKER_QUICK_REFERENCE.md](DOCKER_QUICK_REFERENCE.md)** - Quick reference for Docker commands
  - Starting and stopping services
  - Building images
  - Viewing logs
  - Database operations
  - Troubleshooting

- **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - Detailed Docker deployment guide
  - Architecture overview
  - Development vs production
  - Service management
  - Scaling
  - Monitoring

- **[DOCKER_IMPLEMENTATION_SUMMARY.md](DOCKER_IMPLEMENTATION_SUMMARY.md)** - Docker implementation details

## Project Specifications

### Requirements and Design

- **[.kiro/specs/smart-attendance-system/requirements.md](.kiro/specs/smart-attendance-system/requirements.md)**
  - User stories and acceptance criteria
  - Functional requirements
  - Non-functional requirements
  - EARS and INCOSE compliant requirements

- **[.kiro/specs/smart-attendance-system/design.md](.kiro/specs/smart-attendance-system/design.md)**
  - System architecture
  - Technology stack
  - Component design
  - Data models
  - API design
  - Security considerations
  - Performance optimization

- **[.kiro/specs/smart-attendance-system/tasks.md](.kiro/specs/smart-attendance-system/tasks.md)**
  - Implementation task list
  - Task status tracking
  - Task dependencies

## Implementation Documentation

### Backend

- **[backend/MODELS_IMPLEMENTATION.md](backend/MODELS_IMPLEMENTATION.md)**
  - Database models
  - Model relationships
  - Field descriptions
  - Constraints and indexes

- **[backend/apps/accounts/ADMIN_USER_MANAGEMENT.md](backend/apps/accounts/ADMIN_USER_MANAGEMENT.md)**
  - User management API
  - Admin operations
  - Permissions

- **[backend/apps/academics/COURSE_MANAGEMENT_IMPLEMENTATION.md](backend/apps/academics/COURSE_MANAGEMENT_IMPLEMENTATION.md)**
  - Course management
  - Enrollment management
  - Schedule management

- **[backend/apps/attendance/ATTENDANCE_MARKING_IMPLEMENTATION.md](backend/apps/attendance/ATTENDANCE_MARKING_IMPLEMENTATION.md)**
  - Attendance marking flow
  - QR code scanning
  - Location verification

- **[backend/apps/attendance/ATTENDANCE_OVERRIDE_IMPLEMENTATION.md](backend/apps/attendance/ATTENDANCE_OVERRIDE_IMPLEMENTATION.md)**
  - Admin override functionality
  - Audit logging

- **[backend/apps/attendance/RATE_LIMITING_AND_FRAUD_DETECTION.md](backend/apps/attendance/RATE_LIMITING_AND_FRAUD_DETECTION.md)**
  - Rate limiting implementation
  - Fraud detection algorithms
  - Anti-spoofing measures

- **[backend/apps/attendance/SESSION_MANAGEMENT_IMPLEMENTATION.md](backend/apps/attendance/SESSION_MANAGEMENT_IMPLEMENTATION.md)**
  - Session creation
  - QR token generation
  - Session lifecycle

- **[backend/apps/reports/TEACHER_REPORTING_IMPLEMENTATION.md](backend/apps/reports/TEACHER_REPORTING_IMPLEMENTATION.md)**
  - Report generation
  - CSV export
  - Filtering and pagination

- **[backend/apps/audit/AUDIT_LOG_ENDPOINT_IMPLEMENTATION.md](backend/apps/audit/AUDIT_LOG_ENDPOINT_IMPLEMENTATION.md)**
  - Audit log querying
  - Filtering and search

- **[backend/apps/audit/MONITORING_AND_LOGGING.md](backend/apps/audit/MONITORING_AND_LOGGING.md)**
  - Logging configuration
  - Health checks
  - Monitoring setup

### Frontend

- **[frontend/AUTHENTICATION_IMPLEMENTATION.md](frontend/AUTHENTICATION_IMPLEMENTATION.md)**
  - Authentication flow
  - JWT token management
  - Protected routes
  - Login/logout

- **[frontend/TEACHER_SESSION_INTERFACE_IMPLEMENTATION.md](frontend/TEACHER_SESSION_INTERFACE_IMPLEMENTATION.md)**
  - Session creation interface
  - QR code display
  - Session management
  - Geolocation capture

- **[frontend/STUDENT_QR_SCANNING_IMPLEMENTATION.md](frontend/STUDENT_QR_SCANNING_IMPLEMENTATION.md)**
  - QR code scanning
  - Manual code entry
  - Location capture
  - Attendance history

- **[frontend/ERROR_HANDLING_AND_VALIDATION_IMPLEMENTATION.md](frontend/ERROR_HANDLING_AND_VALIDATION_IMPLEMENTATION.md)**
  - Error handling utilities
  - Form validation
  - Loading states
  - User feedback

- **[frontend/src/components/shared/README.md](frontend/src/components/shared/README.md)**
  - Shared component documentation
  - DataTable, Modal, Toast, MapPreview

- **[frontend/src/hooks/README.md](frontend/src/hooks/README.md)**
  - Custom hooks documentation
  - useAuth, useGeolocation, useAsync

- **[frontend/src/utils/README.md](frontend/src/utils/README.md)**
  - Utility functions
  - Validators, error handlers

## Configuration Files

### Environment Variables

- **backend/.env.example** - Backend environment template
- **frontend/.env.example** - Frontend environment template
- **.env.example** - Root environment template (Docker Compose)

### Docker Configuration

- **docker-compose.yml** - Development Docker Compose configuration
- **docker-compose.prod.yml** - Production Docker Compose overrides
- **backend/Dockerfile** - Backend container definition
- **frontend/Dockerfile** - Frontend production container
- **frontend/Dockerfile.dev** - Frontend development container
- **nginx/nginx.conf** - Development nginx configuration
- **nginx/nginx.prod.conf** - Production nginx configuration

### Application Configuration

- **backend/config/settings/base.py** - Base Django settings
- **backend/config/settings/development.py** - Development settings
- **backend/config/settings/production.py** - Production settings
- **backend/pyproject.toml** - Python tool configuration (black, isort, mypy)
- **backend/.flake8** - Flake8 linting configuration
- **backend/pytest.ini** - Pytest configuration
- **frontend/package.json** - Frontend dependencies and scripts
- **frontend/tailwind.config.js** - Tailwind CSS configuration
- **frontend/.eslintrc.json** - ESLint configuration
- **frontend/.prettierrc** - Prettier configuration

## Additional Resources

### Project Management

- **[SETUP.md](SETUP.md)** - Original setup instructions
- **[SETUP_STATUS.md](SETUP_STATUS.md)** - Setup progress tracking
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference guide

### CI/CD

- **[.github/workflows/ci.yml](.github/workflows/ci.yml)** - GitHub Actions CI/CD pipeline

### Steering Rules

- **[.kiro/steering/product.md](.kiro/steering/product.md)** - Product overview
- **[.kiro/steering/structure.md](.kiro/steering/structure.md)** - Project structure conventions
- **[.kiro/steering/tech.md](.kiro/steering/tech.md)** - Technology stack and tools

## Documentation by Role

### For Developers

1. Start with [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)
2. Review [.kiro/specs/smart-attendance-system/design.md](.kiro/specs/smart-attendance-system/design.md)
3. Check implementation docs in `backend/` and `frontend/`
4. Use [DOCKER_QUICK_REFERENCE.md](DOCKER_QUICK_REFERENCE.md) for daily commands

### For DevOps/System Administrators

1. Start with [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)
2. Review [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
3. Set up monitoring using [backend/apps/audit/MONITORING_AND_LOGGING.md](backend/apps/audit/MONITORING_AND_LOGGING.md)
4. Configure backups as described in [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md)

### For Project Managers

1. Review [README.md](README.md) for project overview
2. Check [.kiro/specs/smart-attendance-system/requirements.md](.kiro/specs/smart-attendance-system/requirements.md)
3. Track progress in [.kiro/specs/smart-attendance-system/tasks.md](.kiro/specs/smart-attendance-system/tasks.md)

### For QA/Testers

1. Review [.kiro/specs/smart-attendance-system/requirements.md](.kiro/specs/smart-attendance-system/requirements.md)
2. Set up test environment using [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)
3. Check test documentation in `backend/apps/*/tests/`

## Quick Links

### Most Common Tasks

- **Start development environment**: See [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md#quick-start-with-docker-recommended)
- **Deploy to production**: See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md#deployment-steps)
- **Run database migrations**: See [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md#database-migrations)
- **Create backup**: See [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md#backup-and-restore)
- **View logs**: See [DOCKER_QUICK_REFERENCE.md](DOCKER_QUICK_REFERENCE.md#logs-and-monitoring)
- **Troubleshoot issues**: See [DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md#troubleshooting) or [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md#troubleshooting)

### API Endpoints

- **Authentication**: `/api/accounts/token/` (login), `/api/accounts/token/refresh/` (refresh)
- **User Management**: `/api/admin/users/`
- **Course Management**: `/api/admin/courses/`, `/api/admin/enrollments/`
- **Attendance Sessions**: `/api/teacher/sessions/`
- **Attendance Marking**: `/api/student/attendance/scan/`
- **Reports**: `/api/teacher/reports/`
- **Audit Logs**: `/api/admin/audit/`
- **Health Check**: `/api/health/`

## Contributing

When adding new documentation:

1. Add the file to the appropriate section in this index
2. Update [README.md](README.md) if it's a major document
3. Follow the existing documentation style and format
4. Include code examples where appropriate
5. Add troubleshooting sections for common issues

## Support

For questions or issues:

1. Check the relevant documentation section above
2. Search existing issues in the repository
3. Review troubleshooting sections in setup guides
4. Create a new issue with detailed information

---

**Last Updated**: November 15, 2025

**Documentation Version**: 1.0
