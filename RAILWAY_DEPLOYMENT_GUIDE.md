# Railway Deployment Guide - Budget Tracker

Complete step-by-step guide to deploy Budget Tracker to Railway with Frontend, Backend, and PostgreSQL database.

## Prerequisites

- GitHub account with your code pushed
- Railway account (https://railway.app)
- Git installed locally

---

## Step 1: Prepare Your Code

### 1.1 Push to GitHub

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit - Budget Tracker app"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/budget-tracker.git
git branch -M main
git push -u origin main
```

### 1.2 Verify Files Exist

Make sure these files exist in your repository:
- ✅ `backend/Dockerfile` - Python FastAPI image
- ✅ `backend/railway.toml` - Backend Railway config
- ✅ `backend/requirements.txt` - Python dependencies
- ✅ `backend/.env.example` - Environment template (for reference)
- ✅ `frontend/Dockerfile` - Node + Nginx image
- ✅ `frontend/railway.toml` - Frontend Railway config
- ✅ `docker-compose.yml` - Local reference (not used in Railway)

### 1.3 Create Environment Files

**For Backend - Create `backend/.env`:**
```
SECRET_KEY=your-random-secret-key-min-32-chars-CHANGE_THIS_IN_PRODUCTION
DATABASE_URL=postgresql://postgres:PASSWORD@localhost:5432/budget_tracker
ALLOWED_ORIGINS=https://YOUR-FRONTEND-DOMAIN.railway.app
RATE_LIMIT_DEFAULT=100/minute
GOLD_PRICE_API_URL=
GOLD_PRICE_API_KEY=
```

**For Frontend - Create `frontend/.env.production`:**
```
VITE_API_URL=https://YOUR-BACKEND-DOMAIN.railway.app/api
```

**Update values before deploying!**

---

## Step 2: Create Railway Project

### 2.1 Create Project on Railway

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Click "Deploy from GitHub repo"
4. Select your `budget-tracker` repository
5. Click "Deploy Now"

Railway will automatically detect your services from Dockerfiles.

---

## Step 3: Create PostgreSQL Database

### 3.1 Add PostgreSQL Service

1. In Railway dashboard, click "New" → "Add Service"
2. Search for and select "PostgreSQL"
3. Railway creates a PostgreSQL instance

### 3.2 Get Database Connection String

1. In Railway dashboard, go to PostgreSQL service
2. Click "Data" tab
3. Copy the connection string
4. It looks like: `postgresql://postgres:PASSWORD@domain:port/railway`

**Save this - you'll need it for backend environment variables**

---

## Step 4: Deploy Backend Service

### 4.1 Create Backend Service (if not auto-created)

1. In Railway dashboard, click "New" → "GitHub Repo"
2. Select your repository
3. In "Services" tab, select `backend` folder as root

### 4.2 Configure Backend Environment Variables

1. Go to Backend service → "Variables"
2. Set these variables:

```
SECRET_KEY = (Generate a random 32+ character string)
DATABASE_URL = postgresql://postgres:PASSWORD@hostname:PORT/railway
ALLOWED_ORIGINS = https://YOUR-FRONTEND-URL.railway.app,http://localhost:5173
RATE_LIMIT_DEFAULT = 100/minute
GOLD_PRICE_API_URL = (leave empty if not using)
GOLD_PRICE_API_KEY = (leave empty if not using)
```

### 4.3 Set Build Configuration

1. Go to Backend service → "Build & Deploy"
2. Verify:
   - **Builder**: Dockerfile
   - **Dockerfile Path**: `Dockerfile` (should be auto-detected)
   - **Service Root**: `backend/`

### 4.4 Set Runtime Port

1. Go to Backend service → "Settings"
2. Click "Generate Domain" (Railway auto-generates HTTPS URL)
3. Port should be `8000` (auto-detected from Dockerfile EXPOSE)

### 4.5 Deploy Backend

1. Go to Backend service → "Deployments"
2. Click "Redeploy" or wait for automatic deployment from git push
3. Wait for "✓ Deployment Successful"

**Note the Backend URL** (e.g., `https://budget-tracker-backend-production.railway.app`)

---

## Step 5: Deploy Frontend Service

### 5.1 Create Frontend Service (if not auto-created)

1. Click "New" → "GitHub Repo"
2. Select your repository
3. In "Services" tab, select `frontend` folder as root

### 5.2 Configure Frontend Environment Variables

1. Go to Frontend service → "Variables"
2. Set:

```
VITE_API_URL = https://budget-tracker-backend-production.railway.app/api
```

Replace with your actual backend URL from Step 4.5

### 5.3 Set Build Configuration

1. Go to Frontend service → "Build & Deploy"
2. Verify:
   - **Builder**: Dockerfile
   - **Dockerfile Path**: `Dockerfile` (should be auto-detected)
   - **Service Root**: `frontend/`

### 5.4 Set Runtime Port

1. Go to Frontend service → "Settings"
2. Click "Generate Domain" (Railway auto-generates HTTPS URL)
3. Port should be `80` (Nginx default)

### 5.5 Deploy Frontend

1. Go to Frontend service → "Deployments"
2. Click "Redeploy" or wait for automatic deployment
3. Wait for "✓ Deployment Successful"

**Note the Frontend URL** (e.g., `https://budget-tracker-frontend-production.railway.app`)

---

## Step 6: Update CORS and API URLs

### 6.1 Update Backend CORS

Now that you have the frontend URL, update backend environment:

1. Backend service → "Variables"
2. Update `ALLOWED_ORIGINS`:

```
ALLOWED_ORIGINS = https://budget-tracker-frontend-production.railway.app
```

3. Click "Redeploy" to apply changes

### 6.2 Update Frontend API URL

If not already done:

1. Frontend service → "Variables"
2. Update `VITE_API_URL`:

```
VITE_API_URL = https://budget-tracker-backend-production.railway.app/api
```

3. Click "Redeploy" to apply changes

---

## Step 7: Initialize Database

### 7.1 Run Database Migrations

After backend deployment, you need to initialize tables:

```bash
# Option 1: Manual initialization (recommended first time)
# Backend will auto-create tables on first startup via init_db.py

# Option 2: Create admin user (optional)
# Use Railway dashboard's "Web" terminal:
cd backend
python create_admin.py
```

### 7.2 Verify Database Connection

1. Backend service → "Logs"
2. Look for:
   ```
   Application startup complete.
   ```
3. Check for database connection errors

---

## Step 8: Test Deployment

### 8.1 Test Backend API

```bash
# Test health endpoint
curl https://YOUR-BACKEND-URL.railway.app/health

# Should return: {"status":"ok"}

# Test registration
curl -X POST https://YOUR-BACKEND-URL.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'

# Should return: {"access_token":"...","token_type":"bearer"}
```

### 8.2 Test Frontend

1. Open frontend URL in browser: `https://YOUR-FRONTEND-URL.railway.app`
2. Try to register a new account
3. Try to login
4. Check browser console (F12) for errors

### 8.3 Verify API Connection

1. Open browser DevTools (F12)
2. Go to Console tab
3. Should see: `[API Client] Base URL: https://YOUR-BACKEND-URL.railway.app/api`
4. Try registration - should work

---

## Step 9: Configure Custom Domain (Optional)

### 9.1 Add Custom Domain

1. Railway Dashboard → Service Settings
2. Click "Add Custom Domain"
3. Enter your domain (e.g., `app.yourdomain.com`)
4. Add CNAME record to your DNS provider pointing to Railway's domain

### 9.2 Update Configuration

Update environment variables with custom domains:
- Backend: `ALLOWED_ORIGINS = https://your-custom-frontend-domain.com`
- Frontend: `VITE_API_URL = https://your-custom-backend-domain.com/api`

---

## Troubleshooting

### Issue: Frontend blank/404 errors

**Cause**: Nginx can't find dist files
- **Fix**: Check build logs for `npm run build` errors
- Ensure `dist/` directory is created before Nginx starts
- Rebuild: Frontend service → "Redeploy"

### Issue: API 502 Bad Gateway

**Cause**: Backend service crashed or unreachable
- **Fix**: 
  1. Check Backend service → "Logs" for errors
  2. Check DATABASE_URL is correct
  3. Verify PostgreSQL service is running
  4. Click "Redeploy"

### Issue: CORS error in browser

**Cause**: Frontend URL not in backend ALLOWED_ORIGINS
- **Fix**:
  1. Get exact frontend URL from Railway
  2. Backend service → Variables
  3. Update ALLOWED_ORIGINS with frontend URL
  4. Click "Redeploy"

### Issue: Database connection refused

**Cause**: Wrong DATABASE_URL or PostgreSQL not ready
- **Fix**:
  1. PostgreSQL service → "Data" tab → copy connection string
  2. Backend service → Variables → update DATABASE_URL
  3. Wait 1-2 minutes for Railway to provision PostgreSQL
  4. Click "Redeploy"

### Issue: Login fails with "Cannot connect to backend"

**Cause**: Frontend VITE_API_URL is incorrect
- **Fix**:
  1. Get correct backend URL from Railway
  2. Frontend service → Variables
  3. Update VITE_API_URL with backend URL
  4. Click "Redeploy"

### Issue: Deployment stuck/failed

**Cause**: Build error or timeout
- **Fix**:
  1. Check "Deployment" tab for error messages
  2. Check "Logs" for build errors
  3. Verify all required files exist in repository
  4. Try manual redeploy: "Redeploy" button
  5. Check git logs: `git log --oneline`

---

## Environment Variables Reference

### Backend Required Variables

```
SECRET_KEY                   # Min 32 random characters (bcrypt secret)
DATABASE_URL                 # PostgreSQL connection string from Railway
ALLOWED_ORIGINS              # Frontend URL (https://your-frontend.railway.app)
RATE_LIMIT_DEFAULT           # e.g., "100/minute"
```

### Backend Optional Variables

```
GOLD_PRICE_API_URL           # External API for live gold price
GOLD_PRICE_API_KEY           # API key for gold price service
```

### Frontend Required Variables

```
VITE_API_URL                 # Backend API URL (https://your-backend.railway.app/api)
```

---

## Production Checklist

- [ ] GitHub repo created and code pushed
- [ ] PostgreSQL service created on Railway
- [ ] Backend service created with correct root directory
- [ ] Frontend service created with correct root directory
- [ ] Backend deployed successfully (check logs)
- [ ] Frontend deployed successfully (check logs)
- [ ] Database CONNECTION_URL configured in backend
- [ ] CORS ALLOWED_ORIGINS set to frontend URL
- [ ] VITE_API_URL set in frontend to backend URL
- [ ] Can register new user
- [ ] Can login with registered user
- [ ] Can access dashboard and view data
- [ ] Frontend shows correct API URL in console
- [ ] No CORS errors in browser console
- [ ] No 502/503 errors from backend

---

## Post-Deployment

### 1. Create Initial Admin User

Connect to Railway backend container and run:

```bash
python create_admin.py
```

This creates account: `admin@budgettracker.com` with password `@run@162991!`

### 2. Monitor Logs

Railway dashboard → Service → "Logs" to monitor:
- Deploy events
- API requests
- Errors and warnings
- Performance metrics

### 3. Automatic Deployments

Every git push to main branch will automatically:
1. Build Docker images
2. Run new containers
3. Restart services (no downtime for multi-instance)

### 4. Scaling (Future)

Railway allows:
- Increase memory/CPU per service
- Add more instances for load balancing
- Configure autoscaling

---

## Quick Reference URLs

After deployment:

```
Frontend: https://YOUR-FRONTEND-URL.railway.app
Backend: https://YOUR-BACKEND-URL.railway.app
API Docs: https://YOUR-BACKEND-URL.railway.app/docs
Database: PostgreSQL managed by Railway
```

---

## Summary

**3 Services Deployed:**

1. **PostgreSQL Database** - Managed PostgreSQL instance
2. **Backend (FastAPI)** - Python API server on port 8000
3. **Frontend (React)** - Nginx serving built React app on port 80

**All behind HTTPS with Railway-managed certificates**

**Auto-deploy on git push to main branch**

**Logs and metrics available in Railway dashboard**

---

## Need Help?

Check Rails logs:
- Backend service → "Logs" tab
- Frontend service → "Logs" tab
- PostgreSQL service → "Data" tab

Test manually:
```bash
# Test backend health
curl https://YOUR-BACKEND-URL.railway.app/health

# Test API docs
https://YOUR-BACKEND-URL.railway.app/docs
```

Browser DevTools (F12):
- Console tab → Look for [API Client] logs
- Network tab → Check API requests
- Application tab → Check localStorage for auth token
