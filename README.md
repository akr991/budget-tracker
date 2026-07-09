# Personal Budget Cloud Tracker

Full-stack cloud application for personal budget tracking with region-separated finance data for India and UAE, plus aggregated Total Net Worth.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, JWT auth, PostgreSQL-ready
- Frontend: React + Vite, mobile-first responsive UI, Chart.js
- Mobile: React + Capacitor, native Android APK
- Deployment: Dockerized, Railway-ready, Google Play ready

## Core Sections

- India dashboard
- UAE dashboard
- Total Net Worth dashboard

Each region supports:
- Income tracking (monthly and yearly summaries + trends)
- Expense tracking
- Loan EMI tracking (remaining months, outstanding, completion alerts)
- Debt tracking (repayments and outstanding)
- Investment tracking (profit/loss and growth trends)
- Gold tracking (grams/sovereigns + optional live price fetch)

## Available Platforms

- 🌐 **Web**: React web app (localhost:5173)
- 📱 **Android**: Native APK via Capacitor
- ☁️ **Cloud**: Deployed on Railway

## Project Structure

- backend/: FastAPI server, models, routers, services
- frontend/: React mobile-first dashboard + Capacitor Android project
- DATABASE_SCHEMA.md: relational database design
- API_DOCS.md: endpoint reference
- docker-compose.yml: local full-stack startup
- ANDROID_BUILD_GUIDE.md: APK build instructions
- MOBILE_APP_SETUP.md: Mobile deployment guide

## Quick Start

1. Copy backend/.env.example to backend/.env and set values:
   - SECRET_KEY
   - DATABASE_URL
   - ALLOWED_ORIGINS

2. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

3. Run API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Open docs:
- http://localhost:8000/docs
- http://localhost:8000/redoc

## Frontend Setup

1. Copy frontend/.env.example to frontend/.env and set VITE_API_URL.
2. Install dependencies and run:

```bash
cd frontend
npm install
npm run dev
```

3. Open app:
- http://localhost:5173

## Android APK Setup

Build a native Android application:

```bash
cd frontend

# Update API URL for your deployed backend
# Edit: .env.production
# VITE_API_URL=https://your-backend-url.railway.app/api

# Build APK (requires Java and Android SDK installed)
./build-apk.bat
```

**Before building**, see:
- [ANDROID_BUILD_GUIDE.md](ANDROID_BUILD_GUIDE.md) - Complete build instructions
- [MOBILE_APP_SETUP.md](MOBILE_APP_SETUP.md) - Backend configuration for mobile

Output APK location:
- Debug: `frontend/android/app/build/outputs/apk/debug/app-debug.apk`
- Release: `frontend/android/app/build/outputs/apk/release/app-release.apk`

## Docker Compose (Local)

```bash
docker compose up --build
```

Services:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432

## Railway Deployment

Deploy as three Railway services in one project:

1. PostgreSQL service:
- Add Railway PostgreSQL plugin
- Copy connection string into backend DATABASE_URL

2. Backend service:
- Source root: backend/
- Build uses backend/Dockerfile
- Environment variables:
  - SECRET_KEY
  - DATABASE_URL
  - ALLOWED_ORIGINS (set to frontend Railway domain)
  - RATE_LIMIT_DEFAULT (optional)
  - GOLD_PRICE_API_URL and GOLD_PRICE_API_KEY (optional)

3. Frontend service:
- Source root: frontend/
- Build uses frontend/Dockerfile
- Environment variables:
  - VITE_API_URL (set to backend Railway URL + /api)

## Features Included

- JWT auth (register/login/logout)
- Region-based data segregation (india/uae)
- CRUD APIs for all finance modules
- Rate limiting middleware
- Validation with Pydantic
- CSV export by module and region
- Monthly summary notification endpoint
- User profile and settings (dark mode and notifications)
- Responsive mobile-first UI with charts and region tabs

## Optional Integrations

- Live gold API: configure GOLD_PRICE_API_URL and GOLD_PRICE_API_KEY
- Cloud sync: provided via central backend and DB-backed persistence
