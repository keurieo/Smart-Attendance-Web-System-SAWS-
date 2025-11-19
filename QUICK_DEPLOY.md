# Quick Deploy Guide

Get your Smart Attendance System live in 15 minutes!

## 1. Deploy Backend (5 minutes)

### Using Railway (Recommended)

1. **Sign up**: Go to [railway.app](https://railway.app) → Sign in with GitHub
2. **New Project**: Click "New Project" → "Deploy from GitHub repo" → Select this repo
3. **Add Database**: Click "+ New" → "Database" → "Add PostgreSQL"
4. **Add Redis**: Click "+ New" → "Database" → "Add Redis"
5. **Enable PostGIS**: 
   - Click PostgreSQL service → "Connect" tab → Copy connection string
   - Click "Data" tab → "Query" → Run: `CREATE EXTENSION IF NOT EXISTS postgis;`
6. **Set Variables**: Click your web service → "Variables" → Add:
   ```
   DJANGO_SETTINGS_MODULE=config.settings.production
   DJANGO_SECRET_KEY=<click "Generate" for random string>
   DJANGO_ALLOWED_HOSTS=.railway.app
   ```
7. **Deploy**: Railway auto-deploys. Wait 2-3 minutes.
8. **Get URL**: Copy your backend URL (e.g., `smart-attendance-production.up.railway.app`)

## 2. Deploy Frontend (5 minutes)

### Using Vercel

1. **Sign up**: Go to [vercel.com](https://vercel.com) → Sign in with GitHub
2. **New Project**: Click "Add New..." → "Project" → Import this repo
3. **Configure**: Vercel auto-detects settings from `vercel.json`
4. **Set Variables**: Add environment variables:
   ```
   REACT_APP_API_URL=https://your-backend-url.railway.app/api
   REACT_APP_ENVIRONMENT=production
   ```
5. **Deploy**: Click "Deploy". Wait 2-3 minutes.
6. **Get URL**: Copy your frontend URL (e.g., `smart-attendance.vercel.app`)

## 3. Connect Them (2 minutes)

1. **Update Backend CORS**:
   - Go back to Railway → Your web service → "Variables"
   - Add: `CORS_ALLOWED_ORIGINS=https://your-frontend-url.vercel.app`
   - Backend auto-redeploys

2. **Initialize Database**:
   - Railway → Your web service → "Settings" → "Deploy"
   - Or use Railway CLI:
   ```bash
   railway run python backend/manage.py migrate
   railway run python backend/setup_initial_data.py
   ```

## 4. Test It (3 minutes)

1. Visit your Vercel URL
2. Login with default credentials (from `setup_initial_data.py`)
3. Test creating a session (Teacher role)
4. Test scanning QR code (Student role)

## Done! 🎉

Your app is now live at:
- Frontend: `https://your-app.vercel.app`
- Backend: `https://your-backend.railway.app`

## Troubleshooting

**CORS Error?**
- Check `CORS_ALLOWED_ORIGINS` includes your exact Vercel URL with `https://`

**API 404?**
- Verify `REACT_APP_API_URL` ends with `/api` (no trailing slash)

**Database Error?**
- Ensure PostGIS extension is enabled
- Check migrations ran successfully

**Need Help?**
- Check `VERCEL_DEPLOYMENT_GUIDE.md` for detailed instructions
- Review `DEPLOYMENT_CHECKLIST.md` for complete steps

## Cost

Both platforms offer free tiers:
- **Railway**: $5 free credit/month (enough for testing)
- **Vercel**: Free for personal projects

For production use, expect ~$10-20/month total.
