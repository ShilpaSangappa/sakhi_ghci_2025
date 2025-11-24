# Sakhi App - Setup Guide 🚀

Complete step-by-step guide to set up and run the Sakhi app for the GHCI Hackathon demo.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.8 or higher installed
- [ ] pip package manager
- [ ] Git (optional, for version control)
- [ ] 2GB free disk space
- [ ] Internet connection (for API calls)

### **Check Python Version**

```bash
python --version
# Should show: Python 3.8.x or higher

# On some systems, use:
python3 --version
```

---

## 🔧 Installation Steps

### **Step 1: Navigate to Project Directory**

```bash
cd sakhi-app
```

### **Step 2: Create Virtual Environment**

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### **Step 3: Upgrade pip**

```bash
python -m pip install --upgrade pip
```

### **Step 4: Install Dependencies**

```bash
pip install -r requirements.txt
```

**Note:** This may take 5-10 minutes. If any package fails, see Troubleshooting section below.

### **Step 5: Initialize Database**

```bash
cd backend
python database.py
```

You should see:
```
✓ Database initialized at data/sakhi.db
✓ Sample data added successfully
```

### **Step 6: Test Translation System**

```bash
cd ../localization
python translation_manager.py
```

You should see translations in all 4 languages.

---

## 🎬 Running the Application

### **Terminal 1: Start Backend Server**

```bash
# Navigate to backend directory
cd backend
python main.py
```

Expected output:
```
Starting Sakhi API server...
INFO:     Uvicorn running on http://0.0.0.0:8000
Access API docs at: http://localhost:8000/docs
```

**Keep this terminal running!**

### **Terminal 2: Start Frontend App**

Open a **new terminal** and activate venv:

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

Then run the frontend:

```bash
cd frontend
python main.py
```

A Kivy window (360x640) should open showing the login screen.

---

## 🎯 Testing the App

### **1. Login Flow**

1. Select a language from dropdown (try Hindi - हिंदी)
2. Notice UI instantly changes - no loading!
3. Enter name: "Priya"
4. Enter phone: "9876543210" (or any 10-digit number)
5. Click "Continue"

**OR**

Click "Continue Anonymously" to skip registration.

### **2. Explore Features**

Once logged in, test each feature:

#### **Period Tracker**
- Click "Period Tracker" button
- Enter start date: `2025-11-01`
- Enter end date: `2025-11-05`
- Select flow level: Medium
- Add symptoms: "Cramps, headache"
- Click Save

#### **Community**
- Click "Community" button
- Type a question in the text box
- Check "Post Anonymously"
- Click Submit
- Scroll to see existing posts (some in different languages)

#### **Chatbot**
- Click "Ask Sakhi" button
- Click one of the quick question buttons OR
- Type: "What is PCOS?"
- See response in your selected language

#### **Meetups**
- Click "Meetups" button
- Browse available meetups
- Click "Join" on any meetup

#### **Analytics**
- Click "Analytics" button
- View cycle statistics
- See insights and predictions

### **3. Test Language Switching**

1. Go back to Home screen
2. (Currently language switching is on login screen only)
3. To test: Logout → Change language → Login again
4. Notice all UI text updates instantly!

---

## 🔍 Verify API Endpoints

While the app is running, open a browser:

1. **API Documentation**: http://localhost:8000/docs
2. **Health Check**: http://localhost:8000/health
3. **Root**: http://localhost:8000/

You should see the API is running.

### **Test API Manually**

```bash
# Test user registration
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","language_pref":"en","anonymous":false}'

# Get posts
curl "http://localhost:8000/community/posts?user_lang=en&limit=5"
```

---

## 🐛 Troubleshooting

### **Issue: Kivy installation fails**

**Windows:**
```bash
pip install --upgrade pip wheel setuptools
pip install kivy[base] kivy_examples --no-cache-dir
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev
sudo apt-get install -y libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
pip install kivy
```

**Mac:**
```bash
brew install pkg-config sdl2 sdl2_image sdl2_ttf sdl2_mixer
pip install kivy
```

### **Issue: PyAudio installation fails (for voice input)**

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**Mac:**
```bash
brew install portaudio
pip install pyaudio
```

### **Issue: Port 8000 already in use**

```bash
# Find process using port 8000
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Kill the process or use a different port:
uvicorn main:app --port 8001
```

Then update `API_BASE_URL` in frontend files.

### **Issue: Database not found**

```bash
# Reinitialize database
cd backend
python database.py
```

### **Issue: Translation not working**

```bash
# Clear translation cache
rm localization/translation_cache.db

# Test translation service
cd backend/services
python translation_service.py
```

### **Issue: ModuleNotFoundError**

Make sure you activated the virtual environment:

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### **Issue: Kivy window not appearing**

Try setting environment variable:

```bash
# Windows
set KIVY_GL_BACKEND=angle_sdl2

# Linux/Mac
export KIVY_GL_BACKEND=gl
```

---

## 📦 Building Android APK (Optional)

**Note:** This takes ~30 minutes on first build.

### **Prerequisites**

- Java JDK 8 or 11
- Android SDK
- At least 10GB free disk space

### **Install Buildozer**

```bash
pip install buildozer
```

### **Create Buildozer Spec**

```bash
cd sakhi-app
buildozer init
```

### **Edit buildozer.spec**

Update these lines:

```ini
[app]
title = Sakhi
package.name = sakhi
package.domain = org.ghci

requirements = python3,kivy==2.2.1,kivymd,requests,googletrans==4.0.0rc1

android.permissions = INTERNET,RECORD_AUDIO,ACCESS_FINE_LOCATION

orientation = portrait
```

### **Build APK**

```bash
buildozer -v android debug
```

**First build takes 20-30 minutes!**

The APK will be in: `bin/sakhi-*-debug.apk`

### **Install on Android Device**

```bash
# Enable USB debugging on your phone
# Connect phone via USB

adb devices  # Verify device connected
adb install bin/sakhi-*-debug.apk
```

---

## 🎥 Demo Preparation Checklist

Before the hackathon demo:

- [ ] Backend server is running (check http://localhost:8000/health)
- [ ] Frontend app opens without errors
- [ ] Database has sample data
- [ ] Test login flow (both regular and anonymous)
- [ ] Test language switching (all 4 languages)
- [ ] Prepare 2-3 posts in different languages to show translation
- [ ] Test chatbot with common questions
- [ ] Have analytics screen open to show insights
- [ ] Prepare your demo script (see README.md)
- [ ] Record a backup video in case of technical issues

---

## 📝 Quick Command Reference

```bash
# Activate virtual environment
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Start backend
cd backend && python main.py

# Start frontend (in new terminal)
cd frontend && python main.py

# Reinitialize database
cd backend && python database.py

# Test translations
cd localization && python translation_manager.py

# Run tests
pytest backend/tests/ -v

# Build APK
buildozer -v android debug
```

---

## 🆘 Getting Help

If you encounter issues not covered here:

1. Check error logs in terminal
2. Verify all dependencies are installed: `pip list`
3. Check Python version: `python --version`
4. Restart both backend and frontend
5. Clear cache and reinitialize database

---

## ✅ Verification Checklist

Before presenting, verify:

- [ ] Backend responds to API calls
- [ ] Frontend displays without errors
- [ ] Language switching works instantly
- [ ] All 7 screens are accessible
- [ ] Database has sample posts/meetups
- [ ] Translation cache is working
- [ ] Voice input button appears (even if not functional)
- [ ] Analytics shows data

---

**You're all set! Good luck with the hackathon! 🎉**
