# Railway Deployment - Quick Checklist

## ⚡ Quick Start (5 Minutes)

### Prerequisites
- [ ] GitHub account
- [ ] Railway account (railway.app)
- [ ] Code pushed to GitHub

### Step-by-Step

#### 1️⃣ Create Railway Project
```
1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your budget-tracker repository
5. Click "Deploy Now"
```

#### 2️⃣ Add PostgreSQL Database
```
1. Click "New" → "Add Service"
2. Search "PostgreSQL"
3. Select and add
4. Go to PostgreSQL → "Data" tab
5. Copy connection string (save it!)
```

#### 3️⃣ Configure Backend Service

**Get your backend service:**
- Railway auto-creates from your Dockerfile

**Set environment variables:**
1. Backend service → "Variables"
2. Add:
   ```
   SECRET_KEY=generate-random-32-char-string-here
   DATABASE_URL=postgresql://postgres:PASSWORD@domain:5432/railway
   ALLOWED_ORIGINS=https://YOUR-FRONTEND-URL.railway.app
   RATE_LIMIT_DEFAULT=100/minute
   ```
3. Save → Redeploy

**Note the Backend URL** (Backend service → Settings → copy domain)

#### 4️⃣ Configure Frontend Service

**Set environment variables:**
1. Frontend service → "Variables"
2. Add:
   ```
   VITE_API_URL=https://YOUR-BACKEND-URL.railway.app/api
   ```
3. Save → Redeploy

**Note the Frontend URL** (Frontend service → Settings → copy domain)

#### 5️⃣ Update Backend CORS

Now update backend with correct frontend URL:

1. Backend service → "Variables"
2. Update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://your-frontend-url-from-step-4.railway.app
   ```
3. Click "Redeploy"

#### 6️⃣ Test

```
Frontend: https://your-frontend-url.railway.app
Backend API: https://your-backend-url.railway.app/api
API Docs: https://your-backend-url.railway.app/docs
```

✅ Done!

---

## 🔍 Verify Everything Works

### Test Backend
```bash
curl https://YOUR-BACKEND-URL.railway.app/health
# Should return: {"status":"ok"}
```

### Test Frontend
1. Open: `https://YOUR-FRONTEND-URL.railway.app`
2. Try to register new account
3. Open browser DevTools (F12)
4. Check Console for `[API Client] Base URL: ...`

### Check Logs
- **Backend errors**: Backend service → Logs tab
- **Frontend errors**: Open browser Console (F12)
- **Database errors**: Backend service → Logs

---

## 📋 Environment Variables

### Backend (`backend/.env`)

| Variable | Value | Example |
|----------|-------|---------|
| `SECRET_KEY` | Random 32+ chars | `abc123xyz789...` |
| `DATABASE_URL` | PostgreSQL URL | `postgresql://postgres:pass@host:5432/railway` |
| `ALLOWED_ORIGINS` | Frontend HTTPS URL | `https://app-frontend.railway.app` |
| `RATE_LIMIT_DEFAULT` | Rate limit | `100/minute` |

### Frontend (`frontend/.env.production`)

| Variable | Value | Example |
|----------|-------|---------|
| `VITE_API_URL` | Backend API URL | `https://app-backend.railway.app/api` |

---

## ⚠️ Common Issues & Fixes

### Issue: Frontend shows blank page
```
1. Check build in Frontend service → Logs
2. Verify npm run build succeeded
3. Click Redeploy
```

### Issue: Can't login - "Cannot connect to backend"
```
1. Check VITE_API_URL in Frontend Variables
2. Make sure it matches your actual backend URL
3. Frontend service → Redeploy
```

### Issue: API 502 Bad Gateway
```
1. Backend service → Logs
2. Check for DATABASE_URL errors
3. Verify PostgreSQL service is running
4. Backend service → Redeploy
```

### Issue: CORS error in browser
```
1. Get your exact frontend URL
2. Backend service → Variables
3. Update ALLOWED_ORIGINS with frontend URL
4. Backend service → Redeploy
```

### Issue: Database connection error
```
1. PostgreSQL service → Data tab
2. Copy new connection string
3. Backend service → Variables
4. Update DATABASE_URL
5. Backend service → Redeploy
```

---

## 🚀 After Deployment

### Auto-Deploy on Git Push
Every git push to main automatically redeploys:
```bash
git add .
git commit -m "Update feature"
git push origin main
# Railway auto-deploys!
```

### Monitor Performance
- Railway dashboard → Service → Metrics
- View CPU, memory, request counts
- Check deployment history

### Create Admin User (Optional)
```bash
# Via Railway terminal
python backend/create_admin.py
```

---

## 📊 Services Summary

| Service | Type | Port | Location |
|---------|------|------|----------|
| Frontend | React + Nginx | 80/443 | Railway |
| Backend | FastAPI Python | 8000 | Railway |
| Database | PostgreSQL | 5432 | Railway (managed) |

All services communicate over HTTPS.

---

## 🔗 Useful Railway Commands

### Via Railway CLI (optional)
```bash
# Install: npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# Deploy
railway up

# View logs
railway logs --service backend
railway logs --service frontend
```

---

## ✅ Final Checklist

Before considering deployment complete:

- [ ] Backend deployed (check "Deployments" shows green)
- [ ] Frontend deployed (check "Deployments" shows green)
- [ ] PostgreSQL running
- [ ] Can open frontend URL in browser
- [ ] Can register new account
- [ ] Can login with account
- [ ] Can see dashboard
- [ ] No CORS errors in browser console
- [ ] No 502 errors in browser
- [ ] API logs show requests (Backend → Logs)

---

## 💡 Pro Tips

1. **Test locally first**
   ```bash
   npm run dev          # Frontend
   uvicorn app.main:app --reload  # Backend
   ```

2. **Use Railway dashboard** for everything - no CLI needed

3. **Enable email notifications** for deployment failures

4. **Keep git history clean** - one commit per feature

5. **Use environment-specific domains** if you have multiple environments

---

## 🆘 Need Help?

1. Check Railway dashboard logs
2. Check browser console (F12) for frontend errors
3. Test API manually: `https://backend-url.railway.app/docs`
4. Check backend logs: Backend service → Logs tab
5. Verify environment variables are set correctly

---

**You're all set!** 🎉

Your Budget Tracker is now live on Railway with:
- Automatic HTTPS
- Auto-scaling infrastructure
- PostgreSQL database
- Continuous deployment on git push
