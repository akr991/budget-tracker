# Railway Deployment - Exact Steps

Copy and paste each command. Replace `YOUR_USERNAME` with your GitHub username.

---

## Step 1: Prepare Code for GitHub

### 1.1 Initialize Git (if not already done)

```bash
cd c:\project_budget
git init
git config user.name "Your Name"
git config user.email "your@email.com"
```

### 1.2 Add All Files

```bash
git add .
git commit -m "Budget Tracker - Initial commit with auth fixes and APK setup"
```

### 1.3 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `budget-tracker`
3. Description: `Personal Budget Cloud Tracker`
4. Choose Public or Private
5. Click "Create Repository"

### 1.4 Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/budget-tracker.git
git branch -M main
git push -u origin main
```

---

## Step 2: Create Railway Project

### 2.1 Go to Railway

https://railway.app/dashboard

### 2.2 Create New Project

1. Click "New Project" button
2. Click "Deploy from GitHub repo"
3. Find and select `budget-tracker` repository
4. Click "Deploy Now"

**Wait 2-3 minutes for Railway to detect services**

---

## Step 3: Add PostgreSQL Database

### 3.1 In Railway Dashboard

1. Click "New" button
2. Search for "PostgreSQL"
3. Click "PostgreSQL"
4. Railway creates a PostgreSQL service

### 3.2 Get Database Connection String

1. Click PostgreSQL service
2. Click "Data" tab
3. Look for: `Database URL`
4. Copy the full URL:
   ```
   postgresql://postgres:PASSWORD@domain.railway.internal:5432/railway
   ```

**Save this URL - you need it for backend!**

---

## Step 4: Configure Backend Service

### 4.1 Click Backend Service

In Railway dashboard, click on "Backend" service

### 4.2 Go to Variables

1. Click "Variables" tab
2. Click "Add Variable" or paste into editor:

```
SECRET_KEY=f7e3c8a9b2d1e4f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
DATABASE_URL=postgresql://postgres:PASSWORD@domain.railway.internal:5432/railway
ALLOWED_ORIGINS=http://localhost:5173
RATE_LIMIT_DEFAULT=100/minute
```

### 4.3 Important: Update SECRET_KEY

Change `SECRET_KEY` to a random string. In PowerShell:

```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 50 | % {[char]$_})
```

Copy the output and use it as SECRET_KEY.

### 4.4 Important: Paste Actual Database URL

Replace with the PostgreSQL URL you copied in Step 3.2:
```
DATABASE_URL=postgresql://postgres:PASSWORD@domain.railway.internal:5432/railway
```

### 4.5 Save Variables

Click "Save" and wait for automatic redeploy

### 4.6 Wait for Deployment

1. Click "Deployments" tab
2. Wait until status shows ✅ (green checkmark)
3. This takes 2-5 minutes

### 4.7 Get Backend URL

1. Click "Settings" tab
2. Look for "Domains"
3. Copy the URL (e.g., `https://budget-tracker-backend-production.railway.app`)

**Save this URL!**

---

## Step 5: Configure Frontend Service

### 5.1 Click Frontend Service

In Railway dashboard, click on "Frontend" service

### 5.2 Go to Variables

1. Click "Variables" tab
2. Add variable:

```
VITE_API_URL=https://budget-tracker-backend-production.railway.app/api
```

**Replace with your actual backend URL from Step 4.7**

### 5.3 Save Variables

Click "Save" and wait for automatic redeploy

### 5.4 Wait for Deployment

1. Click "Deployments" tab
2. Wait until status shows ✅ (green checkmark)
3. This takes 2-5 minutes

### 5.5 Get Frontend URL

1. Click "Settings" tab
2. Look for "Domains"
3. Copy the URL (e.g., `https://budget-tracker-frontend-production.railway.app`)

**Save this URL!**

---

## Step 6: Update Backend CORS

Now that you have the frontend URL, update backend:

### 6.1 Click Backend Service

### 6.2 Go to Variables

1. Click "Variables" tab
2. Find `ALLOWED_ORIGINS`
3. Update to your frontend URL:

```
ALLOWED_ORIGINS=https://budget-tracker-frontend-production.railway.app
```

**Replace with your actual frontend URL from Step 5.5**

### 6.3 Save Variables

Click "Save" → Click "Redeploy" button

### 6.4 Wait for Redeploy

Status should show ✅ (green)

---

## Step 7: Test Everything

### 7.1 Test Backend Health

In PowerShell:

```powershell
$backend = "https://YOUR-BACKEND-URL.railway.app"
Invoke-WebRequest -Uri "$backend/health" -Method GET
```

Should return: `{"status":"ok"}`

### 7.2 Test Frontend

1. Open in browser: `https://YOUR-FRONTEND-URL.railway.app`
2. Should see login form
3. Try to register:
   - Full Name: `Test User`
   - Email: `test@example.com`
   - Password: `password123`
4. Click "Create Account"
5. Should see dashboard ✅

### 7.3 Check Browser Console

1. Press F12
2. Go to Console tab
3. Look for: `[API Client] Base URL: https://YOUR-BACKEND-URL.railway.app/api`
4. Try login - should work
5. Check Network tab - API requests should succeed

---

## Step 8: Continuous Deployment Setup

Now when you push code, Railway auto-deploys:

### 8.1 Make a Code Change

Edit any file, e.g., update `frontend/src/App.jsx`:

```bash
cd c:\project_budget
# Make your change...
```

### 8.2 Push to GitHub

```bash
git add .
git commit -m "Updated [describe change]"
git push origin main
```

### 8.3 Railway Auto-Deploys

1. Go to Railway dashboard
2. Watch "Deployments" tab
3. New deployment should start automatically
4. Wait for ✅ status

---

## Environment Variables Reference

### Backend Variables (in Railway Dashboard)

```
SECRET_KEY              → Random 32+ character string (CHANGE THIS!)
DATABASE_URL            → From PostgreSQL service Data tab
ALLOWED_ORIGINS         → Your frontend HTTPS URL
RATE_LIMIT_DEFAULT      → 100/minute (recommended)
```

### Frontend Variables (in Railway Dashboard)

```
VITE_API_URL            → Your backend HTTPS URL + /api
```

---

## Troubleshooting

### Backend shows error in Logs

1. Backend service → "Logs" tab
2. Look for red error messages
3. Common issues:
   - `DATABASE_URL` wrong → Copy again from PostgreSQL service
   - `SECRET_KEY` too short → Make it 32+ characters
   - Connection timeout → Wait for PostgreSQL to be ready

### Frontend won't load

1. Frontend service → "Logs" tab
2. If `npm run build` fails:
   - Check `frontend/package.json` dependencies
   - Try building locally: `cd frontend && npm run build`
3. If it shows 502:
   - Backend might be down
   - Check backend logs
   - Click Backend "Redeploy"

### Can't login

1. Check browser Console (F12)
2. Look for `[API Client]` logs
3. Check `VITE_API_URL` in frontend variables - must match backend URL
4. Try API directly: `https://backend-url/docs`

### Database connection error

1. PostgreSQL service → "Data" tab
2. Copy connection string
3. Backend service → Variables
4. Update `DATABASE_URL` with new URL
5. Backend service → Redeploy

---

## Quick URLs After Deployment

```
Frontend:   https://budget-tracker-frontend-production.railway.app
Backend:    https://budget-tracker-backend-production.railway.app
API Docs:   https://budget-tracker-backend-production.railway.app/docs
Database:   Managed by Railway (no direct access needed)
```

---

## Final Verification

After deployment is complete:

✅ Frontend URL works (shows login form)
✅ Can register new account
✅ Can login
✅ Dashboard loads
✅ No CORS errors in browser console
✅ No 502 errors
✅ API requests show in Network tab (F12)

If all ✅, you're done! 🎉

---

## What Happens Next

1. **Auto-deploy on git push** - Every push to main deploys automatically
2. **Logs available** - Check Railway dashboard for real-time logs
3. **Monitor performance** - Railway tracks CPU, memory, requests
4. **Scale up** - Click Settings to increase resources if needed

---

## Summary

| Component | Status | URL |
|-----------|--------|-----|
| Frontend | ✅ Deployed | https://your-frontend.railway.app |
| Backend | ✅ Deployed | https://your-backend.railway.app |
| Database | ✅ PostgreSQL | Managed by Railway |

**All with automatic HTTPS, auto-scaling, and continuous deployment!** 🚀
