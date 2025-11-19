# Vercel Deployment Guide

## Architecture

This project uses a **hybrid deployment** approach:
- **Frontend**: Deployed on Vercel (React app)
- **Backend**: Deployed on Railway or Render (Django + PostgreSQL + Redis)

## Prerequisites

1. GitHub account with your repository
2. Vercel account (free tier works)
3. Railway or Render account (free tier available)

## Step 1: Deploy Backend (Railway - Recommended)

### Option A: Railway (Easier)

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect Django and use `railway.json` config
5. Add PostgreSQL database:
   - Click "+ New" → "Database" → "Add PostgreSQL"
   - Railway automatically sets `DATABASE_URL`
6. Add Redis:
   - Click "+ New" → "Database" → "Add Redis"
   - Railway automatically sets `REDIS_URL`
7. Set environment variables in Railway dashboard:
   ```
   DJANGO_SETTINGS_MODULE=config.settings.production
   DJANGO_SECRET_KEY=<generate-random-50-char-string>
   DJANGO_ALLOWED_HOSTS=.railway.app
   CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```
8. Enable PostGIS extension:
   - Go to PostgreSQL service → "Connect" → Copy connection string
   - Use a PostgreSQL client or Railway's built-in terminal:
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```
9. Deploy and note your backend URL (e.g., `https://your-app.railway.app`)

### Option B: Render

1. Go to [render.com](https://render.com) and sign in with GitHub
2. Click "New +" → "Blueprint"
3. Connect your repository
4. Render will use `render.yaml` to create all services
5. Set environment variables:
   ```
   DJANGO_SECRET_KEY=<generate-random-50-char-string>
   CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ```
6. Enable PostGIS in database:
   - Go to your PostgreSQL service → "Shell"
   ```sql
   CREATE EXTENSION IF NOT EXISTS postgis;
   ```
7. Deploy and note your backend URL

## Step 2: Deploy Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "Add New..." → "Project"
3. Import your repository
4. Vercel auto-detects React and uses `vercel.json` config
5. Set environment variables:
   ```
   REACT_APP_API_URL=https://your-backend.railway.app/api
   REACT_APP_ENVIRONMENT=production
   ```
6. Click "Deploy"
7. Note your frontend URL (e.g., `https://your-app.vercel.app`)

## Step 3: Update Backend CORS

After deploying frontend, update backend environment variables:

**On Railway/Render:**
```
CORS_ALLOWED_ORIGINS=https://your-actual-frontend.vercel.app
DJANGO_ALLOWED_HOSTS=.railway.app,.vercel.app
```

Redeploy backend for changes to take effect.

## Step 4: Initialize Database

### Railway:
1. Go to your backend service → "Settings" → "Deploy"
2. Or use Railway CLI:
```bash
railway run python backend/manage.py migrate
railway run python backend/setup_initial_data.py
```

### Render:
The `render.yaml` includes a release command that runs migrations automatically.

To create initial data:
1. Go to your web service → "Shell"
2. Run:
```bash
python backend/setup_initial_data.py
```

## Step 5: Test Deployment

1. Visit your Vercel frontend URL
2. Try logging in with test credentials
3. Check that API calls work (Network tab in browser DevTools)
4. Test QR code generation and scanning

## Environment Variables Reference

### Backend (Railway/Render)
```
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=<random-50-char-string>
DJANGO_ALLOWED_HOSTS=.railway.app,.vercel.app
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
DATABASE_URL=<auto-set-by-platform>
REDIS_URL=<auto-set-by-platform>
DEBUG=False
```

### Frontend (Vercel)
```
REACT_APP_API_URL=https://your-backend.railway.app/api
REACT_APP_ENVIRONMENT=production
```

## Troubleshooting

### CORS Errors
- Ensure `CORS_ALLOWED_ORIGINS` includes your exact Vercel URL (with https://)
- Check that `DJANGO_ALLOWED_HOSTS` includes both platforms

### Database Connection Issues
- Verify PostGIS extension is enabled: `SELECT PostGIS_version();`
- Check `DATABASE_URL` is set correctly

### Static Files Not Loading
- Run `python manage.py collectstatic` in backend
- Check `STATIC_ROOT` and `STATIC_URL` settings

### API 404 Errors
- Verify `REACT_APP_API_URL` ends with `/api` (no trailing slash)
- Check backend health endpoint: `https://your-backend.railway.app/api/health/`

## Continuous Deployment

Both Vercel and Railway/Render support automatic deployments:
- Push to `main` branch → Auto-deploy to production
- Push to other branches → Create preview deployments

## Cost Estimates

### Free Tier Limits:
- **Vercel**: 100GB bandwidth, unlimited projects
- **Railway**: $5 free credit/month (enough for small apps)
- **Render**: Free tier with limitations (spins down after inactivity)

### Recommended for Production:
- Railway: ~$10-20/month (Hobby plan)
- Render: ~$7-15/month (Starter plan)
- Vercel: Free tier usually sufficient for frontend

## Next Steps

1. Set up custom domain (optional)
2. Configure SSL certificates (auto-handled by platforms)
3. Set up monitoring and logging
4. Configure backup strategy for database
5. Review security settings in production

## Support

- Railway: https://docs.railway.app
- Render: https://render.com/docs
- Vercel: https://vercel.com/docs
