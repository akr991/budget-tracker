# Auth Setup and Troubleshooting Guide

## Quick Setup for Testing

### Backend Setup

1. **Ensure Python 3.10+ is installed**
   ```bash
   python --version
   ```

2. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Backend `.env` file has been created at `backend/.env`**
   - Check that `SECRET_KEY` is set (default: `your-secret-key-change-this...`)
   - Check that `DATABASE_URL` is set (default: `sqlite:///./budget.db`)
   - Check that `ALLOWED_ORIGINS` includes `http://localhost:5173`

4. **Run the backend**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Expected output:
   ```
   Uvicorn running on http://0.0.0.0:8000
   ```

### Frontend Setup

1. **Install dependencies** (if not already done)
   ```bash
   cd frontend
   npm install
   ```

2. **Frontend `.env` file has been created at `frontend/.env`**
   - Check that `VITE_API_URL=http://localhost:8000/api`

3. **Run the frontend development server**
   ```bash
   npm run dev
   ```

   Expected output:
   ```
   VITE v5.4.21 dev server running at:
   
   > Local:   http://localhost:5173/
   ```

4. **Open browser to http://localhost:5173**

---

## Testing Auth Flow

### Test Registration

1. Click "New user? Register"
2. Fill in:
   - **Full Name**: Your Name (min 2 characters)
   - **Email**: test@example.com (valid email)
   - **Password**: password123 (min 8 characters)
3. Click "Create Account"

**Expected Result:**
- Success: App shows main dashboard
- Error: Check console for detailed error message (F12 → Console tab)

### Test Login

1. Click "Already have an account? Login"
2. Fill in:
   - **Email**: test@example.com
   - **Password**: password123
3. Click "Login"

**Expected Result:**
- Success: App shows main dashboard
- Error: Check console for detailed error message

---

## Debugging

### Check Backend Health

```bash
# In PowerShell or CMD
curl http://localhost:8000/health

# Should return: {"status":"ok"}
```

### Check Auth Endpoint

```bash
# Register test
curl -X POST http://localhost:8000/api/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"password123\",\"full_name\":\"Test User\"}"

# Should return: {"access_token":"...","token_type":"bearer"}
```

### Browser Console Logs

1. Open DevTools (F12)
2. Go to Console tab
3. Try to register/login
4. Look for logs starting with `[API Client]`, `[Auth]`, etc.

### Common Issues

#### Issue: "Cannot connect to backend"
- **Cause**: Backend not running on port 8000
- **Fix**: 
  ```bash
  cd backend
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```

#### Issue: "Invalid email or password"
- **Cause**: Email already exists or wrong login
- **Fix**: Try a new email for registration or check spelling

#### Issue: "Password must be at least 8 characters"
- **Cause**: Password is too short
- **Fix**: Use at least 8 characters

#### Issue: Backend responds with 422 Unprocessable Entity
- **Cause**: Request data format is wrong
- **Fix**: Check that all required fields are present
  - Register needs: `email`, `password`, `full_name`
  - Login needs: `email`, `password`

#### Issue: CORS Error in console
- **Cause**: Backend CORS not allowing frontend origin
- **Fix**: Check `backend/.env`:
  ```
  ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
  ```
  Restart backend after changing

#### Issue: 401 Unauthorized after login
- **Cause**: Token not being set or backend SECRET_KEY mismatch
- **Fix**: 
  - Check console for "[Auth] Token set" message
  - Restart backend to ensure new SECRET_KEY is loaded

---

## Database Inspection

### View registered users

If using SQLite (default):

```bash
# Using sqlite3 CLI
sqlite3 backend/budget.db

# In SQLite shell:
.tables
SELECT * FROM users;
.quit
```

Or use Python:

```python
from app.models.user import User
from app.db.session import SessionLocal

db = SessionLocal()
users = db.query(User).all()
for user in users:
    print(f"Email: {user.email}, Created: {user.created_at}")
db.close()
```

---

## Password Hashing Verification

Passwords are hashed using bcrypt. To verify manually:

```python
from app.core.security import verify_password, get_password_hash

# Create a test hash
test_password = "password123"
hashed = get_password_hash(test_password)
print(f"Hashed: {hashed}")

# Verify it works
is_valid = verify_password(test_password, hashed)
print(f"Valid: {is_valid}")
```

---

## API Endpoints

### Register
```
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "User Name"
}

Response 200:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

Response 200:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Get Profile (Requires Token)
```
GET /api/profile
Authorization: Bearer {access_token}

Response 200:
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "User Name",
  "is_active": true,
  "created_at": "2026-01-01T00:00:00+00:00"
}
```

---

## Testing with curl (Windows PowerShell)

```powershell
# Variables
$backend = "http://localhost:8000/api"
$email = "test@example.com"
$password = "password123"
$name = "Test User"

# Register
$registerBody = @{
    email = $email
    password = $password
    full_name = $name
} | ConvertTo-Json

$registerResponse = Invoke-WebRequest -Uri "$backend/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body $registerBody

$token = ($registerResponse.Content | ConvertFrom-Json).access_token
Write-Host "Token: $token"

# Use token to get profile
$profileResponse = Invoke-WebRequest -Uri "$backend/profile" `
  -Method GET `
  -Headers @{ Authorization = "Bearer $token" }

Write-Host "Profile: $($profileResponse.Content)"
```

---

## Performance Notes

- **First request may be slow** (1-2 seconds) - SQLAlchemy models are loaded on first use
- **Subsequent requests are fast** - typically < 100ms
- **Rate limiting** is enabled (100 requests per minute by default)

---

## Still Having Issues?

1. **Check browser console** (F12 → Console) for error messages
2. **Check backend logs** - look for stack traces
3. **Check environment files**:
   - `backend/.env` - should exist with proper settings
   - `frontend/.env` - should exist with `VITE_API_URL`
4. **Verify ports**:
   - Frontend: http://localhost:5173
   - Backend: http://localhost:8000
5. **Try clearing cache**:
   - Frontend: Clear browser cache/localStorage
   - Backend: Delete `budget.db` to reset database

---

## Next Steps

Once auth is working:
1. Explore the dashboard
2. Add income/expense entries
3. Create entries for India and UAE regions
4. Check the net worth calculations
5. Try exporting data to CSV

For more details, see [API_DOCS.md](../API_DOCS.md)
