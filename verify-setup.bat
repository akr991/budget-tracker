@echo off
REM Budget Tracker Auth Setup Verification Script

echo.
echo ========================================
echo  Budget Tracker - Auth Setup Check
echo ========================================
echo.

setlocal enabledelayedexpansion

REM Check backend .env
echo [1/4] Checking backend .env file...
if exist "backend\.env" (
    echo   [OK] backend/.env exists
) else (
    echo   [ERROR] backend/.env NOT found - Run setup first!
    exit /b 1
)

REM Check frontend .env
echo [2/4] Checking frontend .env file...
if exist "frontend\.env" (
    echo   [OK] frontend/.env exists
) else (
    echo   [ERROR] frontend/.env NOT found - Run setup first!
    exit /b 1
)

REM Check backend files
echo [3/4] Checking backend auth module...
if exist "backend\app\api\routes\auth.py" (
    echo   [OK] auth.py found
) else (
    echo   [ERROR] auth.py NOT found!
    exit /b 1
)

REM Check frontend auth component
echo [4/4] Checking frontend auth component...
if exist "frontend\src\components\LoginForm.jsx" (
    echo   [OK] LoginForm.jsx found
) else (
    echo   [ERROR] LoginForm.jsx NOT found!
    exit /b 1
)

echo.
echo ========================================
echo  Setup Verification Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Start Backend:
echo    cd backend
echo    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 2. In another terminal, start Frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open browser to http://localhost:5173
echo.
echo 4. Try registering a new user or logging in
echo.
pause
