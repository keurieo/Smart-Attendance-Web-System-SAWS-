# Makefile for Smart Attendance System
# Simplifies common Docker and development commands

.PHONY: help build up down restart logs shell test clean migrate superuser

# Default target
help:
	@echo "Smart Attendance System - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make build          - Build all Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs (all services)"
	@echo "  make logs-backend   - View backend logs"
	@echo "  make logs-frontend  - View frontend logs"
	@echo ""
	@echo "Backend:"
	@echo "  make shell          - Open Django shell"
	@echo "  make bash           - Open backend bash shell"
	@echo "  make migrate        - Run database migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make superuser      - Create Django superuser"
	@echo "  make test           - Run backend tests"
	@echo "  make lint           - Run code linting"
	@echo "  make collectstatic  - Collect static files"
	@echo ""
	@echo "Database:"
	@echo "  make dbshell        - Open database shell"
	@echo "  make backup         - Backup database"
	@echo "  make restore        - Restore database from backup"
	@echo ""
	@echo "Frontend:"
	@echo "  make frontend-shell - Open frontend shell"
	@echo "  make frontend-test  - Run frontend tests"
	@echo "  make frontend-lint  - Run frontend linting"
	@echo ""
	@echo "Production:"
	@echo "  make prod-build     - Build production images"
	@echo "  make prod-up        - Start production services"
	@echo "  make prod-down      - Stop production services"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove stopped containers"
	@echo "  make clean-all      - Remove containers, volumes, and images"
	@echo ""

# Development commands
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

status:
	docker-compose ps

# Backend commands
shell:
	docker-compose exec backend python manage.py shell

bash:
	docker-compose exec backend bash

migrate:
	docker-compose exec backend python manage.py migrate

makemigrations:
	docker-compose exec backend python manage.py makemigrations

superuser:
	docker-compose exec backend python manage.py createsuperuser

test:
	docker-compose exec backend pytest

lint:
	docker-compose exec backend flake8 apps config

collectstatic:
	docker-compose exec backend python manage.py collectstatic --noinput

# Database commands
dbshell:
	docker-compose exec db psql -U attendance_user -d attendance_db

backup:
	docker-compose exec db pg_dump -U attendance_user attendance_db > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Database backed up to backup_$$(date +%Y%m%d_%H%M%S).sql"

restore:
	@echo "Usage: make restore FILE=backup_20231115_120000.sql"
	@if [ -z "$(FILE)" ]; then echo "Error: FILE parameter required"; exit 1; fi
	docker-compose exec -T db psql -U attendance_user attendance_db < $(FILE)

# Frontend commands
frontend-shell:
	docker-compose exec frontend sh

frontend-test:
	docker-compose exec frontend npm test

frontend-lint:
	docker-compose exec frontend npm run lint

frontend-build:
	docker-compose exec frontend npm run build

# Production commands
prod-build:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

# Cleanup commands
clean:
	docker-compose down
	docker system prune -f

clean-all:
	docker-compose down -v
	docker system prune -af
	@echo "Warning: All containers, volumes, and images have been removed"

# Setup commands
setup: build up migrate superuser
	@echo "Setup complete! Access the application at http://localhost"

setup-prod: prod-build prod-up migrate collectstatic
	@echo "Production setup complete!"

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost/health || echo "NGINX health check failed"
	@curl -f http://localhost/api/health/ || echo "Backend health check failed"
