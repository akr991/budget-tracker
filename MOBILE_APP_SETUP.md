# Mobile App Setup Guide

This guide explains how to prepare your Budget Tracker backend for the Android mobile app.

## Architecture

```
┌─────────────────────────────────────────────────┐
│         Android Phone (APK)                     │
│  ┌──────────────────────────────────────────┐   │
│  │  React + Capacitor Frontend (Budget UI)  │   │
│  └──────────────────────────────────────────┘   │
│              ↓                                   │
│         HTTPS API Calls                          │
│              ↓                                   │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│         Railway Deployed Backend                │
│  ┌──────────────────────────────────────────┐   │
│  │  FastAPI Server (Port 8000)              │   │
│  │  - Authentication (JWT)                  │   │
│  │  - Finance tracking APIs                 │   │
│  │  - PostgreSQL Database                   │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## Backend Deployment Checklist

### 1. CORS Configuration (Critical for mobile app)

Update your `backend/core/config.py` to allow HTTPS traffic:

```python
from typing import List

class Settings:
    # Allow your mobile app domain and development URLs
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",      # Dev frontend
        "http://localhost:3000",      # Alternative dev port
        "capacitor://localhost",      # Capacitor development
        "ionic://localhost",          # Ionic development
        # Add your production domain when released:
        # "https://budgettracker.example.com",
    ]
    
    # For production, be specific about origins
    # AVOID using "*" in production
```

Update `backend/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. API Security Headers

Update your backend to send proper security headers:

```python
from fastapi import FastAPI
from fastapi.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

app = FastAPI(middleware=[Middleware(SecurityHeaderMiddleware)])
```

### 3. HTTPS Requirements

Mobile apps REQUIRE HTTPS for security:

- ✅ Production: Use Railway (automatic HTTPS)
- ✅ Development: Use Capacitor's `capacitor://localhost` scheme OR use ngrok for HTTPS tunneling
- ❌ Plain HTTP will NOT work on mobile (security policy)

### 4. Testing the Backend with Mobile App

Before building APK:

```bash
# 1. Deploy backend to Railway
cd backend
git push railway main

# 2. Get your Railway URL (e.g., https://budgettracker-app.railway.app)

# 3. Update frontend API URL
# Edit: frontend/.env.production
VITE_API_URL=https://budgettracker-app.railway.app/api

# 4. Rebuild frontend
cd ../frontend
npm run build
npx cap sync android

# 5. Build APK
./build-apk.bat
```

## Environment Variables for Mobile

### Backend (.env)

```bash
# Must be set correctly for mobile app
DATABASE_URL=postgresql://user:password@host/dbname
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:5173,capacitor://localhost,https://budgettracker-app.railway.app

# Optional: For features
GOLD_API_KEY=your-api-key
```

### Frontend (.env.production)

```bash
# Your deployed Railway backend URL
VITE_API_URL=https://budgettracker-app.railway.app/api
```

## Mobile App Configuration

### Capacitor Config (capacitor.config.json)

Already configured for:
- HTTPS traffic via `androidScheme: "https"`
- Proper API timeout handling
- Capacitor HTTP plugin for intercepting requests

## Troubleshooting Mobile Connectivity

### App can't reach backend

1. **Check backend is running**
   ```bash
   curl https://your-railway-app.railway.app/api/health
   ```

2. **Check CORS settings**
   - Backend must allow mobile app origins
   - Check logs: `Error: Cross-Origin Request Blocked`

3. **Check API URL in app**
   - Frontend `.env.production` must be correct
   - Rebuild and resync: `npx cap sync android`

4. **Check network connectivity**
   - Mobile must have internet access
   - Try connecting to WiFi

5. **Enable debug logging**
   ```javascript
   // In src/api/client.js
   api.interceptors.response.use(
     response => response,
     error => {
       console.error('API Error:', error.response?.status, error.message);
       throw error;
     }
   );
   ```

## Security Best Practices for Mobile

1. **Use HTTPS only** - No plain HTTP
2. **JWT tokens stored safely** - Using localStorage (auto-cleared on app uninstall)
3. **Validate user input** - Backend should validate all requests
4. **Rate limiting** - Protect against brute force attacks
5. **Update Capacitor** - Keep plugins updated for security patches

```bash
# Check for security updates
npm audit
npm audit fix

# Update Capacitor
npm update @capacitor/core @capacitor/android
```

## Monitoring Mobile App Issues

### Enable detailed logging

Add to `backend/main.py`:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"Response: {response.status_code}")
    return response
```

### Check Railway logs

```bash
# View deployment logs
railway logs

# View real-time logs
railway logs --follow
```

## Performance Optimization for Mobile

1. **API response optimization**
   - Paginate large datasets
   - Use field filtering (`?fields=id,name,amount`)
   - Cache frequently accessed data

2. **Frontend optimization**
   - Already bundled with Vite
   - Use React.memo for expensive components
   - Implement virtual scrolling for large lists

3. **Network optimization**
   - Implement request timeout handling
   - Add retry logic for failed requests
   - Use request debouncing for searches

Example retry logic:

```javascript
export const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

api.interceptors.response.use(
  response => response,
  async error => {
    const config = error.config;
    if (!config || !config.retry) config.retry = 0;
    
    config.retry += 1;
    if (config.retry <= 3 && error.response?.status >= 500) {
      await new Promise(resolve => setTimeout(resolve, 1000 * config.retry));
      return api(config);
    }
    return Promise.reject(error);
  }
);
```

## Next Steps

1. ✅ Update backend CORS configuration
2. ✅ Deploy backend to Railway
3. ✅ Update `.env.production` with your backend URL
4. ✅ Run `./build-apk.bat` to create APK
5. ✅ Test on Android device/emulator
6. ✅ Submit to Google Play Store when ready

See `ANDROID_BUILD_GUIDE.md` for detailed build instructions.
