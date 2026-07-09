# 🚀 Railway Deployment - COMPLETE SETUP (Step by Step)

## ✅ What's Already Done

- ✅ GitHub repository created: `akr991/budget-tracker`
- ✅ All code pushed to GitHub
- ✅ Backend Dockerfile configured  
- ✅ Frontend Dockerfile configured
- ✅ All environment configs ready
- ✅ Database schema prepared

## 📋 What You Need to Do in Railway Dashboard

### STEP 1: Create Railway Project & Link GitHub

**Time: 5 minutes**

1. Go to https://railway.app/dashboard
2. Click **"New Project"** button (top right)
3. Select **"Deploy from GitHub repo"**
4. **Search and select**: `akr991/budget-tracker`
5. Click **"Deploy Now"**
6. **Wait 2-3 minutes** for Railway to detect your Dockerfiles
7. You should see 2 services detected:
   - `backend` (from backend/Dockerfile)
   - `frontend` (from frontend/Dockerfile)

---

### STEP 2: Add PostgreSQL Database Service

**Time: 3 minutes**

1. In your Railway project dashboard
2. Click **"New"** button (top right)
3. Search for and select **"PostgreSQL"**
4. Railway creates a PostgreSQL instance
5. ⏳ **Wait 2-3 minutes** for PostgreSQL to initialize

### Get Your Database Connection String

1. Click on **PostgreSQL** service
2. Click **"Data"** tab (on left side)
3. Look for **"Database URL"** section
4. **Copy** the full URL (looks like): 
   ```
   postgresql://postgres:PASSWORD@domain.railway.internal:5432/railway
   ```
5. **Save this URL** - you'll need it next!

---

### STEP 3: Configure Backend Service

**Time: 5 minutes**

#### 3A. Go to Backend Variables

1. Click **"backend"** service in your project
2. Click **"Variables"** tab (on left side)
3. You should see an editor with existing variables

#### 3B. Add/Update These Variables

**Copy and paste each one:**

```
SECRET_KEY=aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890AbC
DATABASE_URL=postgresql://postgres:PASSWORD@domain.railway.internal:5432/railway
ALLOWED_ORIGINS=http://localhost:5173
RATE_LIMIT_DEFAULT=100/minute
GOLD_PRICE_API_URL=
GOLD_PRICE_API_KEY=
```

⚠️ **Important**:
- Replace `DATABASE_URL` with the one you copied from PostgreSQL (Step 2)
- Leave `GOLD_PRICE_API_URL` and `GOLD_PRICE_API_KEY` empty for now

#### 3C. Save Variables

1. Click **"Save"** button
2. Railway automatically redeploys backend
3. Wait for ✅ status in Deployments

#### 3D: Get Backend URL

After deployment completes:

1. Click **"Settings"** tab (on left side)
2. Look for **"Domains"** section
3. You'll see a Railway-generated URL like:
   ```
   https://budget-tracker-backend-production.railway.app
   ```
4. **Save this URL** - very important!

---

### STEP 4: Configure Frontend Service

**Time: 3 minutes**

#### 4A. Go to Frontend Variables

1. Click **"frontend"** service
2. Click **"Variables"** tab

#### 4B. Add Frontend Variable

**Copy and paste this:**

```
VITE_API_URL=https://budget-tracker-backend-production.railway.app/api
```

⚠️ **Replace** with your actual backend URL from Step 3D

#### 4C. Save Variables

1. Click **"Save"**
2. Wait for frontend to redeploy ✅

#### 4D: Get Frontend URL

1. Click **"Settings"** tab
2. Find your Frontend URL like:
   ```
   https://budget-tracker-frontend-production.railway.app
   ```
3. **Save this URL**

---

### STEP 5: Update Backend CORS

**Time: 2 minutes**

Now update backend to allow your frontend URL:

1. Go to **backend** service
2. Click **"Variables"** tab
3. Find `ALLOWED_ORIGINS`
4. Update it to:
   ```
   ALLOWED_ORIGINS=https://budget-tracker-frontend-production.railway.app
   ```
   ⚠️ **Use your actual frontend URL from Step 4D**
5. Click **"Save"**
6. Click **"Redeploy"** button
7. Wait for ✅ status

---

## ✅ Test Your Deployment

### Test 1: Check Backend is Running

```
curl https://YOUR-BACKEND-URL.railway.app/health
```

Should return:
```json
{"status":"ok"}
```

### Test 2: Check Frontend Loads

1. Open in browser: `https://YOUR-FRONTEND-URL.railway.app`
2. Should see **login form** with email and password fields
3. Press F12 to open DevTools → Console tab
4. Should see: `[API Client] Base URL: https://your-backend-url.railway.app/api`

### Test 3: Try to Register

1. Click "New user? Register"
2. Enter:
   - Full Name: `Test User`
   - Email: `test@example.com`
   - Password: `password123`
3. Click "Create Account"
4. **Should see dashboard!** ✅

---

## 📝 Summary of Your Live URLs

After deployment:

| Service | URL | Type |
|---------|-----|------|
| **Frontend** | https://budget-tracker-frontend-production.railway.app | Your App |
| **Backend API** | https://budget-tracker-backend-production.railway.app | API Server |
| **API Docs** | https://budget-tracker-backend-production.railway.app/docs | Swagger UI |
| **Database** | Railway Managed | PostgreSQL |

---

## 🔄 Continuous Deployment (Auto-Deploy on Git Push)

Now whenever you push code to GitHub:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Railway **automatically**:
1. Detects the new commit
2. Rebuilds Docker images
3. Deploys new services
4. Your app updates! 🚀

---

## 🆘 Troubleshooting

### Issue: Frontend blank page

**Solution:**
1. Click backend service → "Logs" tab
2. Check for error messages
3. If DATABASE_URL error, copy it again from PostgreSQL service
4. Save and redeploy backend

### Issue: "Cannot connect to backend" error

**Solution:**
1. Check frontend Variables → VITE_API_URL
2. Make sure it matches your actual backend URL
3. Frontend service → "Redeploy"
4. Wait 2-3 minutes for rebuild

### Issue: API 502 Bad Gateway

**Solution:**
1. Go to backend service → "Logs"
2. Look for database connection errors
3. Verify DATABASE_URL is correct
4. Backend service → "Redeploy"

### Issue: CORS error in browser console

**Solution:**
1. Get your exact frontend URL
2. Backend service → Variables
3. Update ALLOWED_ORIGINS to match frontend URL
4. Backend service → "Redeploy"

---

## 🎉 You're Done!

Your Budget Tracker is now:

✅ **Live on HTTPS** - Automatic SSL certificates  
✅ **Auto-deployed** - Every git push deploys automatically  
✅ **Scalable** - Railway handles traffic automatically  
✅ **Monitored** - View logs and metrics in dashboard  
✅ **Backed up** - PostgreSQL data is secure  

---

## 📊 Next Steps

1. **Monitor logs**:
   - Backend service → "Logs" tab
   - Watch real-time requests

2. **Track metrics**:
   - Any service → "Metrics" tab
   - View CPU, memory, requests

3. **Share your app**:
   - Frontend URL: https://budget-tracker-frontend-production.railway.app
   - Works anywhere on the internet!

4. **Make changes**:
   - Update code locally
   - `git push origin main`
   - Railway auto-deploys! 🚀

---

**Deployment complete!** 🎊

Your app is now live on Railway with automatic HTTPS, PostgreSQL database, and continuous deployment from GitHub!

For questions about Railway features, visit: https://railway.app/docs
