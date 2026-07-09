@echo off
REM Build script for Budget Tracker Android APK

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  Budget Tracker - Android APK Builder
echo ========================================
echo.

REM Check if in frontend directory
if not exist "package.json" (
    echo Error: Please run this script from the frontend directory
    pause
    exit /b 1
)

REM Check for Node modules
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    if !errorlevel! neq 0 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Prompt for build type
echo Choose build type:
echo 1. Debug APK (for testing)
echo 2. Release APK (for distribution)
set /p buildType="Enter choice (1 or 2): "

if "%buildType%"=="1" (
    set buildTarget=assembleDebug
    set outputFile=app-debug.apk
) else if "%buildType%"=="2" (
    set buildTarget=assembleRelease
    set outputFile=app-release.apk
) else (
    echo Invalid choice
    pause
    exit /b 1
)

echo.
echo Step 1: Building React app...
call npm run build
if !errorlevel! neq 0 (
    echo Error: Failed to build React app
    pause
    exit /b 1
)

echo.
echo Step 2: Syncing to Android project...
call npx cap sync android
if !errorlevel! neq 0 (
    echo Error: Failed to sync
    pause
    exit /b 1
)

echo.
echo Step 3: Building APK...
cd android
call gradlew.bat %buildTarget%
if !errorlevel! neq 0 (
    echo Error: Failed to build APK
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================
echo  Build Complete!
echo ========================================
echo.
echo APK location:
if "%buildType%"=="1" (
    echo android\app\build\outputs\apk\debug\app-debug.apk
) else (
    echo android\app\build\outputs\apk\release\app-release.apk
)
echo.
echo Ready to install on device/emulator!
echo.
pause
