# Sakhi - Your Health Companion 🌸

**A multilingual women's health app for GHCI Hackathon 2025**

Sakhi is a comprehensive mobile application designed to empower women with health tracking, community support, and AI-powered assistance in their native language.

---

## 🌟 Features

### 1. **Period Tracking** 📅
- Log menstrual cycles with symptoms and flow levels
- Predictive analytics for next period
- Cycle regularity insights
- Historical data visualization

### 2. **Anonymous Community Forum** 💬
- Post health questions anonymously
- Upvote helpful responses
- Comment and engage with others
- Multilingual post translation

### 3. **Location-Based Meetups** 📍
- Create and join support group meetups
- Find health workshops in your city
- RSVP and track participants
- Privacy-focused location sharing

### 4. **Analytics Dashboard** 📊
- Cycle trends and patterns
- Symptom tracking over time
- Personalized health insights
- Visual data representation

### 5. **AI Chatbot (Sakhi)** 🤖
- 24/7 health question answering
- Multilingual support (English, Hindi, Tamil, Kannada)
- Voice input and output
- Pre-trained on women's health FAQs

### 6. **Hybrid Translation System** 🌍
- **Static UI**: Instant language switching (no API calls)
- **Dynamic Content**: AI-powered translation with caching
- **95% cost reduction** compared to full AI translation
- Supports: English, Hindi (हिंदी), Tamil (தமிழ்), Kannada (ಕನ್ನಡ)

### 7. **Voice Input/Output** 🎤
- Speech-to-text for easy input
- Text-to-speech for accessibility
- Supports Indic languages
- Perfect for less tech-savvy users

---

## 🏗️ Architecture

### **Tech Stack**

#### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite (local deployment)
- **API Design**: RESTful
- **Translation**: Google Translate + Caching

#### Frontend
- **Framework**: Kivy (Python)
- **UI**: Custom components with Material Design
- **Navigation**: Screen Manager
- **State Management**: App-level user context

#### AI/ML
- **LLM**: Configurable (OpenAI/Gemini for demo)
- **Speech**: Google Speech Recognition + gTTS
- **Translation**: Hybrid approach (static + dynamic)

---

## 📁 Project Structure

```
sakhi-app/
├── frontend/                    # Kivy mobile app
│   ├── screens/                # All app screens
│   │   ├── login.py           # Login with language selector
│   │   ├── home.py            # Main dashboard
│   │   ├── period_tracker.py # Period logging
│   │   ├── community.py       # Forum posts
│   │   ├── meetups.py         # Meetup listings
│   │   ├── analytics.py       # Health analytics
│   │   └── chatbot.py         # AI assistant
│   ├── components/            # Reusable UI components
│   │   ├── language_selector.py
│   │   └── voice_input.py
│   └── main.py                # App entry point
│
├── backend/                    # FastAPI backend
│   ├── routes/                # API endpoints
│   │   ├── auth.py           # Authentication
│   │   ├── period.py         # Period tracking
│   │   ├── community.py      # Forum posts
│   │   ├── meetups.py        # Meetups
│   │   └── chatbot.py        # AI chatbot
│   ├── services/
│   │   └── translation_service.py  # Hybrid translation
│   ├── main.py               # FastAPI app
│   ├── database.py           # SQLite setup
│   └── models.py             # Pydantic models
│
├── localization/              # Translation files
│   ├── en.json               # English
│   ├── hi.json               # Hindi
│   ├── ta.json               # Tamil
│   ├── kn.json               # Kannada
│   ├── translation_manager.py     # Static UI translation
│   └── translation_cache.db       # Dynamic content cache
│
├── data/                      # Database
│   └── sakhi.db              # SQLite database
│
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

---

## 🚀 Quick Start

### **Prerequisites**

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) Android device or emulator for mobile testing

### **1. Clone the Repository**

```bash
cd sakhi-app
```

### **2. Create Virtual Environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Initialize Database**

```bash
cd backend
python database.py
```

This will create the SQLite database and populate it with sample data.

### **5. Start Backend Server**

```bash
# In backend directory
python main.py
```

The API will be available at: `http://localhost:8000`

**API Documentation**: `http://localhost:8000/docs`

### **6. Run Frontend App**

In a new terminal:

```bash
# In frontend directory
cd frontend
python main.py
```

The Kivy app window will open (360x640 mobile size).

---

## 🎯 Demo Flow for Hackathon

### **1. Language Selection (00:00 - 00:30)**
- Open app → Select Hindi
- Show instant UI translation (no loading!)
- Switch to Tamil → instant again
- Highlight: "This is our hybrid approach - static UI translations are cached locally"

### **2. User Registration (00:30 - 01:00)**
- Register with phone number
- Or continue anonymously
- Show language preference saved

### **3. Period Tracking (01:00 - 02:00)**
- Log a period with symptoms
- Show cycle prediction
- Navigate to analytics
- Display cycle trends chart

### **4. Community Forum (02:00 - 03:30)**
- View posts in different languages
- Click "Translate" on a Tamil post → translates to Hindi
- Click again → instant (from cache!)
- Create anonymous post
- Upvote and comment

### **5. AI Chatbot (03:30 - 04:30)**
- Ask: "What is PCOS?" in Hindi
- Get response in Hindi
- Use voice input (demo)
- Switch to English → chat continues seamlessly

### **6. Meetups (04:30 - 05:00)**
- Browse meetups in Bangalore
- Join a PCOS support group
- Show participant count

### **7. Translation Cost Savings (05:00 - 05:30)**
- Open backend logs
- Show cache hit rate: 95%
- Explain: "We only translate user content once, then cache it"
- Show estimated cost: $10/month vs $300/month

---

## 🔧 Configuration

### **Environment Variables**

Create a `.env` file in the root directory:

```env
# Backend
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_PATH=data/sakhi.db

# Translation
TRANSLATION_PROVIDER=google  # or 'ai4bharat'
GOOGLE_TRANSLATE_API_KEY=your_key_here  # (optional)

# LLM (for chatbot)
OPENAI_API_KEY=your_key_here  # (optional)
LLM_MODEL=gpt-3.5-turbo

# Speech
SPEECH_PROVIDER=google  # or 'bhashini'
```

### **Supported Languages**

The app currently supports 4 languages with full UI translation:

1. **English** (`en`)
2. **Hindi** (`hi`) - हिंदी
3. **Tamil** (`ta`) - தமிழ்
4. **Kannada** (`kn`) - ಕನ್ನಡ

To add more languages:
1. Create `localization/{lang_code}.json`
2. Add to `supported_languages` in `translation_manager.py`

---

## 📱 Building Android APK

### **Using Buildozer**

```bash
# Install buildozer
pip install buildozer

# Initialize buildozer spec
buildozer init

# Build APK (first time takes ~30 minutes)
buildozer -v android debug

# The APK will be in bin/
# Install on device:
adb install bin/sakhi-*.apk
```

### **Buildozer Configuration**

Edit `buildozer.spec`:

```ini
[app]
title = Sakhi
package.name = sakhi
package.domain = org.ghci

# Requirements
requirements = python3,kivy,kivymd,requests,googletrans

# Permissions
android.permissions = INTERNET,RECORD_AUDIO,ACCESS_FINE_LOCATION

# Orientation
orientation = portrait

# Icon and splash
icon.filename = assets/icon.png
presplash.filename = assets/splash.png
```

---

## 🧪 Testing

### **Run Backend Tests**

```bash
cd backend
pytest tests/ -v
```

### **Test Translation System**

```bash
cd localization
python translation_manager.py
```

### **Test API Endpoints**

```bash
# Using curl
curl http://localhost:8000/health

# Using Python
python
>>> import requests
>>> requests.get('http://localhost:8000/health').json()
```

---

## 📊 Performance Metrics

### **Translation Cost Comparison**

| Metric | Full AI Translation | Hybrid Approach | Savings |
|--------|-------------------|-----------------|---------|
| UI Calls/Day | 50,000 | 0 | 100% |
| Content Calls/Day | 10,000 | 500 | 95% |
| Monthly Cost | $300-600 | $10-20 | **95%** |
| UI Response Time | 200-500ms | <10ms | **95% faster** |
| Cache Hit Rate | N/A | 90-95% | - |

### **Database Statistics**

```sql
-- Total users
SELECT COUNT(*) FROM users;

-- Active posts
SELECT COUNT(*) FROM posts;

-- Translation cache efficiency
SELECT
  COUNT(*) as cached_items,
  SUM(access_count) as total_accesses,
  (SUM(access_count) - COUNT(*)) as api_calls_saved
FROM translation_cache;
```

---

## 🎨 UI/UX Design Principles

1. **Large Touch Targets**: Buttons ≥ 48px height for easy tapping
2. **High Contrast**: Readable text with WCAG AA compliance
3. **Voice-First**: Voice input on every text field
4. **Minimal Text**: Icons with labels for universal understanding
5. **Color Coding**: Consistent colors per feature
   - Period Tracker: Pink/Red (#CC4466)
   - Community: Blue (#4488CC)
   - Meetups: Green (#66AA66)
   - Analytics: Purple (#8866CC)
   - Chatbot: Teal (#44AAAA)

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Development Guidelines**

- Follow PEP 8 for Python code
- Add docstrings to all functions
- Write tests for new features
- Update translations in all 4 languages
- Test on both desktop and mobile

---

## 🐛 Troubleshooting

### **Backend won't start**
```bash
# Check if port 8000 is already in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000  # Linux/Mac

# Kill process or use different port
uvicorn main:app --port 8001
```

### **Kivy installation issues**
```bash
# Install dependencies first (Windows)
pip install --upgrade pip wheel setuptools
pip install kivy[base] kivy_examples

# Linux
sudo apt-get install python3-kivy

# Mac
brew install pkg-config sdl2 sdl2_image sdl2_ttf sdl2_mixer
```

### **Translation not working**
```bash
# Test translation service
cd backend/services
python translation_service.py

# Clear cache if needed
# Delete localization/translation_cache.db
```

### **Voice input not working**
```bash
# Install PyAudio (Windows - requires Microsoft C++ Build Tools)
pip install pipwin
pipwin install pyaudio

# Linux
sudo apt-get install portaudio19-dev python3-pyaudio

# Mac
brew install portaudio
pip install pyaudio
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**GHCI Hackathon 2025 Submission**

- Built with ❤️ for women's health empowerment
- Focused on accessibility and inclusivity
- Multilingual support for Indic languages

---

## 🙏 Acknowledgments

- **AI4Bharat** for Indic language models
- **Google Translate** for translation API
- **Kivy** community for mobile framework
- **FastAPI** for excellent documentation
- All women who shared their health journey to inspire this app

---

## 📞 Contact & Support

- **Demo Video**: [Link to video]
- **Presentation**: [Link to slides]
- **GitHub Issues**: [Report bugs here]

---

## 🚧 Future Roadmap

### **Phase 1 (Post-Hackathon)**
- [ ] Integrate AI4Bharat IndicBERT for better Indic translation
- [ ] Add more languages (Bengali, Marathi, Telugu)
- [ ] Implement real voice recognition
- [ ] Add push notifications for period predictions

### **Phase 2**
- [ ] Telemedicine integration
- [ ] Partner with gynecologists for verified answers
- [ ] Add medication reminders
- [ ] Symptom checker with ML

### **Phase 3**
- [ ] iOS version
- [ ] Web app (Progressive Web App)
- [ ] Integration with health wearables
- [ ] Anonymous health records export

---

## 📈 Impact Metrics (Target)

- **Users**: 10,000 in first 6 months
- **Languages**: 7 Indic languages by end of year 1
- **Community Posts**: 1,000+ health discussions
- **Meetups**: 50+ support group meetups organized
- **Cost Savings**: $50,000+ saved through hybrid translation

---

**Made with 💙 for GHCI Hackathon 2025**

*Empowering women through technology, one conversation at a time.*
