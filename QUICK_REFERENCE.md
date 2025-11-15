# Quick Reference - Development Commands

## 🚀 Start Development

```powershell
# Start Docker services
docker-compose up -d db redis

# Activate Python environment
backend\venv\Scripts\activate

# Start backend server
python backend\manage.py runserver
```

## 🛠️ Common Django Commands

```powershell
# Run migrations
python backend\manage.py migrate

# Create superuser
python backend\manage.py createsuperuser

# Create new migration
python backend\manage.py makemigrations

# Django shell
python backend\manage.py shell

# Check for issues
python backend\manage.py check
```

## 🧪 Testing

```powershell
# Run all tests
pytest backend/apps

# Run specific app tests
pytest backend/apps/attendance

# Run with coverage
pytest --cov=apps backend/apps
```

## 🐳 Docker Commands

```powershell
# View running containers
docker-compose ps

# View logs
docker-compose logs -f db
docker-compose logs -f redis

# Stop services
docker-compose down

# Restart services
docker-compose restart db redis
```

## 📦 Package Management

```powershell
# Install new package
pip install package-name
pip freeze > backend\requirements\base.txt

# Update dependencies
pip install -r backend\requirements\development.txt --upgrade
```
