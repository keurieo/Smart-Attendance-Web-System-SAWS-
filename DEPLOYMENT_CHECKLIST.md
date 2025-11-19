# Deployment Checklist

## Pre-Deployment

- [ ] All tests passing locally
- [ ] Environment variables documented
- [ ] Database migrations up to date
- [ ] Static files collected and tested
- [ ] CORS settings configured
- [ ] Security settings reviewed

## Backend Deployment (Railway/Render)

### Railway
- [ ] Create Railway account
- [ ] Connect GitHub repository
- [ ] Add PostgreSQL database
- [ ] Add Redis database
- [ ] Enable PostGIS extension: `CREATE EXTENSION IF NOT EXISTS postgis;`
- [ ] Set environment variables:
  - [ ] `DJANGO_SETTINGS_MODULE=config.settings.production`
  - [ ] `DJANGO_SECRET_KEY=<random-50-char-string>`
  - [ ] `DJANGO_ALLOWED_HOSTS=.railway.app`
  - [ ] `CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app`
- [ ] Deploy backend
- [ ] Run migrations: `python backend/manage.py migrate`
- [ ] Create superuser: `python backend/setup_initial_data.py`
- [ ] Test health endpoint: `/api/health/`
- [ ] Note backend URL for frontend config

### Render (Alternative)
- [ ] Create Render account
- [ ] Deploy using Blueprint (`render.yaml`)
- [ ] Enable PostGIS in database shell
- [ ] Set environment variables
- [ ] Verify deployment
- [ ] Note backend URL

## Frontend Deployment (Vercel)

- [ ] Create Vercel account
- [ ] Connect GitHub repository
- [ ] Set environment variables:
  - [ ] `REACT_APP_API_URL=https://your-backend.railway.app/api`
  - [ ] `REACT_APP_ENVIRONMENT=production`
- [ ] Deploy frontend
- [ ] Note frontend URL

## Post-Deployment

- [ ] Update backend `CORS_ALLOWED_ORIGINS` with actual Vercel URL
- [ ] Update backend `DJANGO_ALLOWED_HOSTS` to include both platforms
- [ ] Redeploy backend with updated settings
- [ ] Test login functionality
- [ ] Test QR code generation
- [ ] Test QR code scanning
- [ ] Test geolocation features
- [ ] Test all user roles (Admin, Teacher, Student)
- [ ] Verify API endpoints work
- [ ] Check browser console for errors
- [ ] Test on mobile devices
- [ ] Set up monitoring (optional)
- [ ] Configure custom domain (optional)
- [ ] Set up automated backups

## Security Review

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set
- [ ] HTTPS enforced
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] SQL injection protection (Django ORM)
- [ ] XSS protection enabled
- [ ] CSRF protection enabled
- [ ] Secure cookies configured

## Monitoring Setup (Optional)

- [ ] Set up Sentry for error tracking
- [ ] Configure logging
- [ ] Set up uptime monitoring
- [ ] Database backup strategy
- [ ] Performance monitoring

## Rollback Plan

If deployment fails:
1. Check deployment logs on Railway/Render
2. Verify environment variables
3. Check database connection
4. Review CORS settings
5. Rollback to previous deployment if needed

## Support Resources

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Django Deployment: https://docs.djangoproject.com/en/4.2/howto/deployment/
