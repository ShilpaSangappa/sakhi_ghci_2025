# Sakhi - Women's Health Companion
## GHCI Hackathon 2025 Submission

---

## Executive Summary

Sakhi is a comprehensive women's health companion application with a groundbreaking focus on menopause support in India. Built as a mobile-first platform, Sakhi addresses a critical gap in healthcare for 50+ million Indian women experiencing perimenopause and menopause by providing personalized tracking, AI-powered insights, and multilingual support in English, Hindi, Tamil, and Kannada.

The application combines period tracking, menopause symptom logging, community engagement, and AI-powered health guidance into a single, accessible platform. What sets Sakhi apart is its deep menopause analytics engine that provides personalized insights, treatment effectiveness tracking, and health risk assessments—features rarely found in existing health apps, especially ones that support Indic languages.

---

## The Problem

### Menopause: A Silent Health Crisis in India

Over 50 million Indian women are currently experiencing perimenopause or menopause, yet this critical life transition remains severely underserved:

- **Lack of Awareness**: 70% of Indian women report feeling unprepared for menopause symptoms
- **Limited Resources**: Most health apps focus on reproductive years, ignoring the 40+ age group
- **Language Barriers**: Existing solutions are predominantly English-only, excluding millions of regional language speakers
- **Cultural Stigma**: Menopause is rarely discussed openly, leaving women isolated and uninformed
- **Medical Desert**: Access to specialized menopause care is limited, especially outside major cities

Beyond menopause, women face broader challenges:
- Irregular period tracking without predictive insights
- Fragmented health information across multiple platforms
- Lack of culturally appropriate, anonymous community support
- Limited access to reliable health information in regional languages

---

## Our Solution: Sakhi

Sakhi is a comprehensive mobile health platform designed specifically for Indian women, with pioneering menopause support features:

### Core Features

**1. Menopause Analytics Dashboard**
- **Comprehensive Symptom Tracking**: Users log 12 key menopause symptoms including hot flashes, night sweats, mood changes, sleep issues, joint pain, brain fog, vaginal dryness, fatigue, anxiety, heart palpitations, and weight changes
- **Intelligent Stage Detection**: Automatically identifies user's menopause stage (pre-menopause, early perimenopause, late perimenopause, menopause, post-menopause) based on cycle patterns and age
- **Predictive Analytics**:
  - Estimates time until menopause milestone (12 months without period)
  - Calculates cycle variability and irregularity patterns
  - Projects perimenopause duration based on historical data
- **Symptom Intelligence**:
  - Identifies most common symptoms with severity scoring (0-10 scale)
  - Tracks symptom trends (improving, worsening, stable)
  - Provides hot flash frequency analysis with trend detection
  - Monitors sleep quality and mood patterns
- **Treatment Effectiveness Tracking**:
  - Logs HRT (Hormone Replacement Therapy), supplements, lifestyle changes, and exercise regimens
  - Tracks effectiveness ratings and side effects
  - Correlates treatments with symptom improvements
- **Health Risk Assessment**:
  - Evaluates bone health risk based on age and menopause stage
  - Assesses cardiovascular risk with HRT consideration
  - Provides personalized risk categories (low, medium, high)

**2. Period Tracker**
- Simple logging of period start/end dates, flow levels, and symptoms
- Cycle length calculation and next period predictions
- Regularity analysis to detect perimenopause transition
- Integration with menopause analytics for comprehensive hormonal health tracking

**3. AI-Powered Chatbot**
- **Conversational Health Guidance**: Powered by Claude AI (Anthropic) for natural, empathetic responses
- **Menopause-Specific Knowledge**: Trained to answer questions about symptoms, treatments, lifestyle changes, and emotional support
- **Multilingual Support**: Seamless conversation in English, Hindi (हिंदी), Tamil (தமிழ்), and Kannada (ಕನ್ನಡ)
- **Voice Interface**:
  - Speech-to-text using Sarvam AI for Indic languages
  - Text-to-speech responses for accessibility
  - Hands-free interaction for convenience

**4. Community Platform**
- **Anonymous Posting**: Users can share experiences, questions, and support without revealing identity
- **Multilingual Content**: Posts automatically tagged by language, with translation capabilities
- **Upvote System**: Community-curated quality content rises to the top
- **Comment Threads**: Foster supportive discussions and shared experiences
- **Menopause-Focused Content**: Seed data includes posts about hot flashes, HRT experiences, lifestyle tips, and emotional support

**5. Local Meetups**
- **Hybrid Events**: Support for both in-person and virtual meetups
- **City-Based Discovery**: Find meetups in your local area (Bangalore, Delhi, Chennai, Mumbai, etc.)
- **Language-Specific Groups**: Meetups conducted in preferred languages
- **Community Building**: Topics include yoga workshops, menopause support groups, nutrition seminars, and wellness walks
- **RSVP System**: Track participants and build consistent community connections

---

## Technical Architecture

### Technology Stack

**Backend (Python/FastAPI)**
- **Framework**: FastAPI for high-performance REST API
- **Database**: SQLite with comprehensive schema for users, period logs, menopause symptoms, treatments, community posts, and meetups
- **AI Integration**:
  - Claude AI (Anthropic) API for conversational chatbot
  - Sarvam AI for Indic language speech-to-text and text-to-speech
- **Analytics Engine**: Custom-built menopause analytics with statistical calculations (averages, trends, predictions)
- **CORS Enabled**: Cross-origin support for frontend integration

**Frontend (Python/Kivy)**
- **Framework**: Kivy for cross-platform mobile development (Android, iOS, Desktop)
- **Font Support**: Nirmala UI font integration for proper rendering of Hindi (Devanagari), Tamil, and Kannada scripts
- **Responsive Design**: Optimized for mobile screens (360x640 default)
- **Navigation**: Screen manager for smooth transitions between features

**Data Model**
```python
Users: id, phone, name, language_pref, city, age, menopause_stage, anonymous
Period Logs: user_id, start_date, end_date, flow_level, symptoms, notes
Menopause Symptoms: user_id, log_date, [12 symptom fields], notes
Menopause Treatments: user_id, treatment_type, name, start_date, effectiveness, side_effects
Community Posts: user_id, content, language, anonymous_name, upvotes
Meetups: title, description, city, date, time, type, location, language
```

### API Endpoints

**Authentication & User Management**
- `POST /auth/register` - User registration
- `GET /auth/user/{user_id}` - Get user profile
- `PUT /auth/user/{user_id}` - Update user details

**Period Tracking**
- `POST /period/log` - Log period data
- `GET /period/logs/{user_id}` - Retrieve period history
- `GET /analytics/cycle/{user_id}` - Cycle analytics and predictions

**Menopause Tracking** *(Unique Innovation)*
- `POST /menopause/symptom/log` - Log daily symptoms
- `GET /menopause/symptom/logs/{user_id}` - Retrieve symptom history
- `POST /menopause/treatment/add` - Add treatment
- `GET /menopause/treatment/list/{user_id}` - List active treatments
- `GET /menopause/analytics/{user_id}` - Comprehensive analytics (20+ data points)

**Community**
- `POST /community/post` - Create post
- `GET /community/feed` - Get community feed with language filtering
- `POST /community/post/{post_id}/upvote` - Upvote post
- `POST /community/post/{post_id}/comment` - Add comment

**Meetups**
- `POST /meetups/create` - Create meetup
- `GET /meetups/list` - List upcoming meetups with filters
- `POST /meetups/{meetup_id}/join` - RSVP to meetup

**Chatbot**
- `POST /chat/ask` - Ask health question with AI response

---

## Real-World Application & Impact

### Target Audience

**Primary Users**: Indian women aged 40-60 experiencing perimenopause or menopause
- 50+ million women in India currently in this demographic
- Growing population as life expectancy increases
- Underserved by existing health technology

**Secondary Users**: Women of all ages for period tracking and general health
- 400+ million women in reproductive age in India
- Preventive health tracking from early adulthood
- Building health data history for future perimenopause transition

### Impact Metrics

**Healthcare Access**
- Provides menopause-specific tracking and insights currently unavailable in mainstream apps
- Reduces need for frequent doctor visits through self-monitoring and AI guidance
- Empowers women with data to have informed conversations with healthcare providers
- Breaks cultural silence by normalizing menopause discussions

**Language Inclusivity**
- Supports 4 languages covering 1 billion+ speakers
- Text and voice interfaces lower literacy barriers
- Culturally appropriate content for Indian context

**Community Support**
- Anonymous platform reduces stigma around menopause and period discussions
- Creates support networks for women experiencing similar transitions
- Facilitates local meetups for in-person community building

**Data-Driven Health**
- Comprehensive analytics transform subjective experiences into quantifiable data
- Treatment effectiveness tracking helps women and doctors optimize care
- Early risk detection for bone health and cardiovascular issues

### Use Case Scenarios

**Scenario 1: Priya (46, Early Perimenopause)**
Priya notices her periods becoming irregular but doesn't know why. Using Sakhi, she logs her cycles and symptoms. The app identifies her as being in early perimenopause based on cycle variability (increased from 2 days to 12 days standard deviation). She reads community posts from women sharing similar experiences, reducing her anxiety. The AI chatbot answers her questions about perimenopause in English, and she finds a local support group meetup in Bangalore.

**Scenario 2: Lakshmi (52, Menopause)**
Lakshmi hasn't had a period in 13 months. She's experiencing severe hot flashes (averaging 8 per day). She logs her symptoms daily in Tamil using voice input. The analytics dashboard shows her hot flash trend is "increasing" and her sleep quality is deteriorating. She shares this data report with her doctor, who prescribes HRT. After 2 months, she tracks the treatment effectiveness (8/10) and sees her symptom trend shift to "improving." Her experience, shared anonymously on the community, helps other women considering HRT.

**Scenario 3: Kavya (54, Post-Menopause)**
Kavya is 2 years post-menopause but still experiences occasional joint pain and mood changes. The app's bone health risk assessment shows "medium" risk due to her age and menopause stage. She logs lifestyle treatments (calcium supplements, yoga, walking) and tracks their effectiveness. She discovers a nutrition seminar meetup in her city and connects with other post-menopausal women managing similar health concerns.

---

## Innovation & Differentiation

### What Makes Sakhi Unique

**1. Menopause-First Approach**
- While competitors focus on fertility and pregnancy, Sakhi prioritizes the 40+ demographic
- Comprehensive symptom tracking (12 key indicators) rarely found in general health apps
- Stage-based insights tailored to perimenopause, menopause, and post-menopause

**2. Advanced Analytics Engine**
- Calculates cycle variability, symptom trends, and predictive milestones
- Treatment effectiveness correlation with symptom improvements
- Health risk assessments for bone health and cardiovascular issues
- Statistical analysis including standard deviation, averages, and trend detection

**3. Culturally Appropriate Design**
- Indic language support with proper font rendering (Nirmala UI for Devanagari, Tamil, Kannada)
- Anonymous community features respecting cultural sensitivity around women's health
- Local meetup system for India-specific community building

**4. AI Integration**
- Claude AI provides empathetic, accurate health guidance
- Sarvam AI enables voice interaction in regional languages
- Context-aware responses tailored to menopause and women's health

**5. Holistic Health Tracking**
- Integrates period tracking with menopause symptoms for complete hormonal health picture
- Connects physical symptoms (hot flashes) with mental health (mood, anxiety)
- Lifestyle and treatment tracking in one unified platform

---

## Demo Data & Testing

The application includes comprehensive synthetic data for 5 demo user profiles representing different menopause stages:

**Profile 1: Priya (46, Early Perimenopause)**
- 8 period logs showing increasing cycle irregularity (28-45 day cycles)
- 60 symptom logs with mild-to-moderate hot flashes (2-4 per day)
- Cycle variability: 12.3 days (significantly irregular)
- Most common symptoms: Hot flashes (avg 3.2/10), mood changes, fatigue

**Profile 2: Ananya (50, Late Perimenopause)**
- 6 period logs with large gaps (45-90 days between periods)
- 52 symptom logs with moderate-to-severe symptoms
- Average hot flashes: 6.4 per day (increasing trend)
- Active treatment: Herbal supplements (effectiveness: 6/10)

**Profile 3: Lakshmi (52, Menopause)**
- 4 period logs, last period 13 months ago
- 48 symptom logs with severe hot flashes (8-10 per day)
- Sleep quality: 3.2/10 (poor due to night sweats)
- Active treatment: HRT (effectiveness: 8/10)

**Profile 4: Kavya (54, Post-Menopause)**
- 2 period logs from 2+ years ago
- 46 symptom logs showing declining symptoms (improving trend)
- Bone health risk: Medium, Cardiovascular risk: Medium
- Active treatment: Calcium + Vitamin D supplements

**Profile 5: Meera (42, Pre-Menopause)**
- 20 period logs with regular 28-day cycles
- 40 symptom logs (baseline for future comparison)
- Cycle variability: 2.1 days (very regular)

**Total Dataset**: 246+ symptom logs, 36 period logs, 3 active treatments

---

## Future Roadmap

**Phase 1 (Current)**: Core menopause tracking, analytics, and community features

**Phase 2 (Next 6 months)**:
- Integration with wearable devices (smartwatches) for automatic symptom detection
- Telemedicine integration for virtual consultations with menopause specialists
- Expanded AI chatbot with image analysis for skin/hair changes
- Nutrition and exercise recommendations based on symptom patterns

**Phase 3 (Next 12 months)**:
- Partnerships with Indian healthcare providers and pharmacies
- Insurance integration for treatment cost tracking
- Clinical research partnerships using anonymized data
- Expansion to additional Indic languages (Marathi, Bengali, Telugu)

**Phase 4 (Long-term)**:
- AI-powered early detection of menopause-related health risks
- Personalized treatment recommendation engine
- Mental health support integration (therapy, meditation)
- Global expansion with localization for other markets

---

## Technical Achievements

### Implementation Highlights

**Database Architecture**
- Flexible SQLite schema supporting complex queries for analytics
- Efficient indexing for fast retrieval of symptom logs and period data
- Proper foreign key relationships maintaining data integrity
- Synthetic data generation algorithm creating realistic, diverse user profiles

**Analytics Algorithm**
- Statistical calculations including mean, standard deviation, trends
- Predictive modeling for menopause milestone estimation
- Correlation analysis between treatments and symptom improvements
- Risk assessment algorithms factoring age, stage, and treatment status

**Multilingual Support**
- Proper Unicode handling for Indic scripts
- Font registration system for Devanagari, Tamil, and Kannada
- Language-aware community content filtering and translation
- Voice I/O integration with Sarvam AI for regional languages

**API Design**
- RESTful architecture with clear endpoint structure
- Pydantic models ensuring data validation and type safety
- Comprehensive error handling and HTTP status codes
- CORS configuration for cross-platform frontend integration

---

## Conclusion

Sakhi represents a significant step forward in women's health technology for India. By focusing on the underserved menopause demographic and providing culturally appropriate, multilingual support, we're addressing a critical healthcare gap affecting 50+ million women.

Our comprehensive analytics engine transforms subjective experiences into actionable data, empowering women to understand their bodies, track treatments, and make informed health decisions. The combination of AI-powered guidance, community support, and local meetups creates a holistic ecosystem for women's health beyond what any single existing app provides.

Most importantly, Sakhi breaks the cultural silence around menopause. By providing a safe, anonymous platform where women can share experiences, ask questions, and support each other in their preferred language, we're normalizing these conversations and building a supportive community.

This is just the beginning. With further development, clinical partnerships, and user growth, Sakhi has the potential to become the leading women's health platform in India, improving health outcomes and quality of life for millions of women navigating perimenopause, menopause, and beyond.

---

## Project Links

### Codebase Repository
**GitHub**: https://github.com/ShilpaSangappa/sakhi_ghci_2025
- Full source code (backend and frontend)
- Setup instructions and dependencies
- API documentation
- Sample data and testing scripts

### Video Demonstration
**YouTube**: https://drive.google.com/drive/folders/1AnUyCzrg4H9fJVranyjJFcn1gYpFAjcS?usp=sharing
- Complete walkthrough of all features
- Menopause analytics dashboard demo
- AI chatbot interaction in multiple languages
- Community and meetups functionality
- Technical architecture overview

---

**Team**: Siva Sakthi, Ekta Rai, Shilpa Sangappa
**Event**: Grace Hopper Celebration India (GHCI) Hackathon 2025
**Category**: Women's Health Technology
**Contact**: [shilpa.sangappa@gmail.com]
