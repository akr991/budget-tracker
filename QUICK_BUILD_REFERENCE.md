# Budget Tracker - Android APK Quick Reference

## Build APK in 3 Steps

### Step 1: Configure Backend URL
```bash
# Edit this file with your deployed backend URL:
frontend/.env.production
# Change: VITE_API_URL=https://your-app.railway.app/api
```

### Step 2: Build (Windows)
```bash
cd frontend
./build-apk.bat
# Follow the prompts to choose Debug or Release build
```

### Step 3: Get Your APK
```
Frontend/android/app/build/outputs/apk/debug/app-debug.apk
               OR
Frontend/android/app/build/outputs/apk/release/app-release.apk
```

---

## Prerequisites Checklist

Before building, ensure you have:

- [ ] **Java JDK 11+** installed
  - Test: `java -version`
  
- [ ] **Android SDK** installed
  - Recommend: Install Android Studio
  - Or: Get Android SDK Command-line Tools
  
- [ ] **Environment Variables Set**
  ```
  JAVA_HOME = C:\Program Files\Java\jdk-11
  ANDROID_HOME = C:\Users\YourName\AppData\Local\Android\Sdk
  PATH includes %ANDROID_HOME%\platform-tools
  ```
  
- [ ] **Backend Deployed**
  - Check: `curl https://your-app.railway.app/api/health`
  - Get the URL from Railway dashboard

---

## Installation on Device

### Debug APK (Testing)
```bash
adb install frontend/android/app/build/outputs/apk/debug/app-debug.apk
```

### Release APK (Distribution)
- For Google Play: Use release APK with signing key
- For manual installation: Transfer .apk file via USB

---

## Directory Structure

```
project_budget/
├── frontend/
│   ├── android/                          # Android project
│   │   ├── app/build/outputs/apk/       # Built APKs here
│   │   └── gradlew.bat                  # Gradle build tool
│   ├── src/                              # React source code
│   ├── vite.config.js                    # Build config
│   ├── capacitor.config.json             # Capacitor config
│   ├── .env.production                   # API URL for production
│   └── build-apk.bat                     # Helper script
├── backend/                              # FastAPI server
└── ANDROID_BUILD_GUIDE.md               # Detailed build guide
```

---

## Common Issues & Fixes

### "Gradle command not found"
- Ensure `frontend/android` has `gradlew.bat`
- Or: Install Android Studio

### "JAVA_HOME not set"
```batch
setx JAVA_HOME "C:\Program Files\Java\jdk-11"
# Restart terminal after setting
```

### "API connection fails on phone"
1. Check backend is running/deployed
2. Verify `.env.production` has correct URL
3. Check backend CORS settings allow mobile origins
4. Rebuild: `npx cap sync android` then `./build-apk.bat`

### "Gradle sync fails"
```bash
cd frontend/android
gradlew.bat clean
cd ..
gradlew.bat assembleDebug
```

---

## Testing Workflow

1. **Local Dev** (no build needed)
   ```bash
   cd frontend
   npm run dev
   # Opens at http://localhost:5173
   ```

2. **Debug APK** (test on real phone)
   ```bash
   npm run build
   npx cap sync android
   ./build-apk.bat  # Choose option 1 (Debug)
   adb install android/app/build/outputs/apk/debug/app-debug.apk
   ```

3. **Release APK** (distribution)
   ```bash
   ./build-apk.bat  # Choose option 2 (Release)
   # Sign key will be generated on first release build
   ```

---

## Files Created for Mobile Support

- `frontend/android/` - Native Android project
- `frontend/capacitor.config.json` - Capacitor configuration
- `frontend/build-apk.bat` - Build helper script
- `frontend/.env.production` - Production API URL
- `ANDROID_BUILD_GUIDE.md` - Detailed build instructions
- `MOBILE_APP_SETUP.md` - Backend mobile setup guide

---

## Next Steps

1. ✅ Install Java & Android SDK (if not already done)
2. ✅ Update `frontend/.env.production` with backend URL
3. ✅ Run `cd frontend && ./build-apk.bat`
4. ✅ Choose Debug build to test
5. ✅ Install on Android device via adb
6. ✅ Test the app
7. ✅ When ready, build Release APK for distribution

---

## Resources

- Capacitor Docs: https://capacitorjs.com/docs/
- Android Studio: https://developer.android.com/studio
- Google Play Release: https://play.google.com/console
- Railway Deployment: https://railway.app/docs

---

Need help? Check detailed guides:
- Build issues → ANDROID_BUILD_GUIDE.md
- Backend setup → MOBILE_APP_SETUP.md
- API troubleshooting → API_DOCS.md
