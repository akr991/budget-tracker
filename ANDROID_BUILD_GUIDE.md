# Android APK Build Guide for Budget Tracker

## Prerequisites

Before building the APK, you need:

1. **Java Development Kit (JDK)** - Version 11 or higher
   - Download: https://www.oracle.com/java/technologies/downloads/
   - Or use: `choco install openjdk` (if using Chocolatey)

2. **Android Studio** or **Android SDK Command-line Tools**
   - Download: https://developer.android.com/studio
   - Or Command-line tools: https://developer.android.com/studio#command-tools

3. **Environment Variables Setup**
   - Set `JAVA_HOME` to your JDK installation path
   - Set `ANDROID_HOME` to your Android SDK path
   - Add `%ANDROID_HOME%\tools` and `%ANDROID_HOME%\platform-tools` to PATH

## Step 1: Update Backend API URL

Before building, configure your backend API URL:

```bash
# Edit .env.production to point to your deployed backend
VITE_API_URL=https://your-railway-app.railway.app/api
```

## Step 2: Build the Web Assets

```bash
cd frontend
npm run build
npx cap sync android
```

## Step 3: Build the APK

### Option A: Using Gradle (Command Line)

```bash
cd frontend/android

# Build debug APK (faster, for testing)
gradlew.bat assembleDebug

# Build release APK (optimized for distribution)
# First, generate a signing key:
keytool -genkey -v -keystore budget-tracker-release-key.keystore -alias budget-tracker -keyalg RSA -keysize 2048 -validity 10000

# Then build:
gradlew.bat assembleRelease
```

### Option B: Using Android Studio

1. Open `frontend/android` folder in Android Studio
2. Wait for Gradle sync to complete
3. Go to Build → Generate Signed Bundle/APK
4. Create/select a signing key
5. Select "APK" and build

## Output

- **Debug APK**: `frontend/android/app/build/outputs/apk/debug/app-debug.apk`
- **Release APK**: `frontend/android/app/build/outputs/apk/release/app-release.apk`

## Step 4: Install on Device/Emulator

### Install debug APK:
```bash
adb install frontend/android/app/build/outputs/apk/debug/app-debug.apk
```

### Or transfer to phone:
- Connect phone via USB
- Enable "Developer mode" and "USB debugging"
- Use Android File Transfer or ADB to install

## Architecture Notes

- **Frontend**: React + Vite wrapped in Capacitor
- **Backend**: FastAPI (running separately on Railway)
- **Communication**: HTTPS API calls
- **Storage**: App stores auth token in localStorage

## Troubleshooting

### "JAVA_HOME not set"
```bash
setx JAVA_HOME "C:\Program Files\Java\jdk-11"
```

### "ANDROID_HOME not set"
```bash
setx ANDROID_HOME "C:\Users\YourUsername\AppData\Local\Android\Sdk"
```

### Gradle build fails
```bash
cd frontend/android
gradlew.bat clean
gradlew.bat assembleDebug
```

### App won't connect to API
- Check that your backend URL is correct in `.env.production`
- Ensure backend is deployed and accessible
- Check CORS settings on backend
- Use device network inspector to debug API calls

## Releasing on Google Play Store

1. Build a signed release APK (see Step 3, Option A)
2. Create a Google Play Developer account
3. Upload APK to Google Play Console
4. Configure app details, screenshots, and privacy policy
5. Submit for review

More info: https://developer.android.com/studio/publish
