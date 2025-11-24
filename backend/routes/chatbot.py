"""
Chatbot routes for Sakhi App
"""

from fastapi import APIRouter, HTTPException
from models import ChatRequest, ChatResponse, MessageResponse
from database import db
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.translation_service import translation_service
from backend.services.chatbot_service import chatbot_service

router = APIRouter()

# Pre-defined responses for common questions (for demo)
FAQ_RESPONSES = {
    "en": {
        "pcos": "PCOS (Polycystic Ovary Syndrome) is a hormonal disorder affecting women of reproductive age. Common symptoms include irregular periods, excess androgen, and polycystic ovaries. Management includes lifestyle changes, medication, and regular monitoring.",
        "period_pain": "To manage period pain: 1) Use heating pad on lower abdomen 2) Take over-the-counter pain relievers 3) Exercise regularly 4) Try relaxation techniques 5) Stay hydrated. If pain is severe, consult a doctor.",
        "irregular_period": "Irregular periods can be normal, especially during puberty or perimenopause. However, if you're experiencing significant irregularity, it's best to consult a gynecologist to rule out conditions like PCOS, thyroid issues, or hormonal imbalances.",
        "doctor": "See a doctor if you experience: Very heavy bleeding, severe pain, periods lasting >7 days, bleeding between periods, irregular periods affecting daily life, or periods stopping suddenly if you're not pregnant."
    },
    "hi": {
        "pcos": "PCOS (पॉलीसिस्टिक ओवरी सिंड्रोम) प्रजनन आयु की महिलाओं को प्रभावित करने वाला एक हार्मोनल विकार है। सामान्य लक्षणों में अनियमित पीरियड, अतिरिक्त एंड्रोजन और पॉलीसिस्टिक अंडाशय शामिल हैं। प्रबंधन में जीवनशैली में बदलाव, दवा और नियमित निगरानी शामिल है।",
        "period_pain": "पीरियड के दर्द को प्रबंधित करने के लिए: 1) पेट के निचले हिस्से पर हीटिंग पैड का उपयोग करें 2) दर्द निवारक दवाएं लें 3) नियमित रूप से व्यायाम करें 4) विश्राम तकनीकों का प्रयास करें 5) हाइड्रेटेड रहें। यदि दर्द गंभीर है, तो डॉक्टर से परामर्श करें।",
        "irregular_period": "अनियमित पीरियड सामान्य हो सकते हैं, खासकर यौवन या रजोनिवृत्ति के दौरान। हालांकि, यदि आप महत्वपूर्ण अनियमितता का अनुभव कर रहे हैं, तो PCOS, थायराइड मुद्दों या हार्मोनल असंतुलन जैसी स्थितियों को खारिज करने के लिए स्त्री रोग विशेषज्ञ से परामर्श करना सबसे अच्छा है।",
        "doctor": "डॉक्टर को दिखाएं यदि आप अनुभव करते हैं: बहुत भारी रक्तस्राव, गंभीर दर्द, 7 दिनों से अधिक समय तक चलने वाले पीरियड, पीरियड्स के बीच रक्तस्राव, दैनिक जीवन को प्रभावित करने वाले अनियमित पीरियड, या यदि आप गर्भवती नहीं हैं तो अचानक पीरियड बंद हो जाना।"
    },
    "ta": {
        "pcos": "PCOS (பாலிசிஸ்டிக் ஓவரி சிண்ட்ரோம்) என்பது இனப்பெருக்க வயதுடைய பெண்களை பாதிக்கும் ஒரு ஹார்மோன் கோளாறு. பொதுவான அறிகுறிகளில் ஒழுங்கற்ற மாதவிடாய், அதிகப்படியான ஆண்ட்ரோஜன் மற்றும் பாலிசிஸ்டிக் கருப்பைகள் அடங்கும். நிர்வாகத்தில் வாழ்க்கை முறை மாற்றங்கள், மருந்து மற்றும் வழக்கமான கண்காணிப்பு அடங்கும்.",
        "period_pain": "மாதவிடாய் வலியை நிர்வகிக்க: 1) அடிவயிற்றில் ஹீட்டிங் பேட் பயன்படுத்தவும் 2) வலி நிவாரணிகள் எடுத்துக்கொள்ளவும் 3) தவறாமல் உடற்பயிற்சி செய்யவும் 4) ரிலாக்சேஷன் தொழில்நுட்பங்களை முயற்சிக்கவும் 5) நீர்ச்சத்துடன் இருக்கவும். வலி கடுமையாக இருந்தால், மருத்துவரை அணுகவும்.",
        "irregular_period": "ஒழுங்கற்ற மாதவிடாய் சாதாரணமானதாக இருக்கலாம், குறிப்பாக பருவமடையும் போது அல்லது மெனோபாஸ் காலத்தில். இருப்பினும், நீங்கள் குறிப்பிடத்தக்க ஒழுங்கின்மையை அனுபவித்தால், PCOS, தைராய்டு பிரச்சினைகள் அல்லது ஹார்மோன் சமநிலையின்மை போன்ற நிலைமைகளை நிராகரிக்க மகப்பேறு மருத்துவரை அணுகுவது சிறந்தது.",
        "doctor": "நீங்கள் அனுபவித்தால் மருத்துவரை பாருங்கள்: மிகவும் கனமான இரத்தப்போக்கு, கடுமையான வலி, 7 நாட்களுக்கு மேல் நீடிக்கும் மாதவிடாய், மாதவிடாய்களுக்கு இடையில் இரத்தப்போக்கு, அன்றாட வாழ்க்கையை பாதிக்கும் ஒழுங்கற்ற மாதவிடாய், அல்லது நீங்கள் கர்ப்பமாக இல்லாதபோது திடீரென மாதவிடாய் நின்றுவிட்டால்."
    },
    "kn": {
        "pcos": "PCOS (ಪಾಲಿಸಿಸ್ಟಿಕ್ ಓವರಿ ಸಿಂಡ್ರೋಮ್) ಸಂತಾನೋತ್ಪತ್ತಿ ವಯಸ್ಸಿನ ಮಹಿಳೆಯರ ಮೇಲೆ ಪರಿಣಾಮ ಬೀರುವ ಹಾರ್ಮೋನ್ ಅಸ್ವಸ್ಥತೆ. ಸಾಮಾನ್ಯ ಲಕ್ಷಣಗಳಲ್ಲಿ ಅನಿಯಮಿತ ಮುಟ್ಟು, ಅತಿಯಾದ ಆಂಡ್ರೋಜನ್ ಮತ್ತು ಪಾಲಿಸಿಸ್ಟಿಕ್ ಅಂಡಾಶಯಗಳು ಸೇರಿವೆ. ನಿರ್ವಹಣೆಯಲ್ಲಿ ಜೀವನಶೈಲಿ ಬದಲಾವಣೆಗಳು, ಔಷಧಿ ಮತ್ತು ನಿಯಮಿತ ಮೇಲ್ವಿಚಾರಣೆ ಸೇರಿವೆ.",
        "period_pain": "ಮುಟ್ಟಿನ ನೋವನ್ನು ನಿರ್ವಹಿಸಲು: 1) ಕೆಳ ಹೊಟ್ಟೆಯ ಮೇಲೆ ಹೀಟಿಂಗ್ ಪ್ಯಾಡ್ ಬಳಸಿ 2) ನೋವು ನಿವಾರಕಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ 3) ನಿಯಮಿತವಾಗಿ ವ್ಯಾಯಾಮ ಮಾಡಿ 4) ವಿಶ್ರಾಂತಿ ತಂತ್ರಗಳನ್ನು ಪ್ರಯತ್ನಿಸಿ 5) ಹೈಡ್ರೇಟೆಡ್ ಆಗಿರಿ. ನೋವು ತೀವ್ರವಾಗಿದ್ದರೆ, ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
        "irregular_period": "ಅನಿಯಮಿತ ಮುಟ್ಟು ಸಾಮಾನ್ಯವಾಗಿರಬಹುದು, ವಿಶೇಷವಾಗಿ ಪ್ರೌಢಾವಸ್ಥೆ ಅಥವಾ ಋತುಬಂಧ ಸಮಯದಲ್ಲಿ. ಆದಾಗ್ಯೂ, ನೀವು ಗಮನಾರ್ಹ ಅನಿಯಮಿತತೆಯನ್ನು ಅನುಭವಿಸುತ್ತಿದ್ದರೆ, PCOS, ಥೈರಾಯ್ಡ್ ಸಮಸ್ಯೆಗಳು ಅಥವಾ ಹಾರ್ಮೋನ್ ಅಸಮತೋಲನದಂತಹ ಪರಿಸ್ಥಿತಿಗಳನ್ನು ತಳ್ಳಿಹಾಕಲು ಸ್ತ್ರೀರೋಗ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸುವುದು ಉತ್ತಮ.",
        "doctor": "ನೀವು ಅನುಭವಿಸಿದರೆ ವೈದ್ಯರನ್ನು ನೋಡಿ: ಅತಿ ಹೆಚ್ಚು ರಕ್ತಸ್ರಾವ, ತೀವ್ರ ನೋವು, 7 ದಿನಗಳಿಗಿಂತ ಹೆಚ್ಚು ಕಾಲ ಮುಟ್ಟು, ಮುಟ್ಟುಗಳ ನಡುವೆ ರಕ್ತಸ್ರಾವ, ದೈನಂದಿನ ಜೀವನವನ್ನು ಪರಿಣಾಮ ಬೀರುವ ಅನಿಯಮಿತ ಮುಟ್ಟು, ಅಥವಾ ನೀವು ಗರ್ಭಿಣಿಯಾಗಿಲ್ಲದಿದ್ದರೆ ಮುಟ್ಟು ಇದ್ದಕ್ಕಿದ್ದಂತೆ ನಿಂತುಹೋಗುವುದು."
    }
}

def get_faq_response(question: str, language: str) -> str:
    """Get FAQ response based on question keywords"""
    question_lower = question.lower()

    # Determine topic
    if any(word in question_lower for word in ['pcos', 'polycystic', 'pcod']):
        return FAQ_RESPONSES[language].get('pcos', FAQ_RESPONSES['en']['pcos'])
    elif any(word in question_lower for word in ['pain', 'cramp', 'hurt', 'दर्द', 'வலி', 'ನೋವು']):
        return FAQ_RESPONSES[language].get('period_pain', FAQ_RESPONSES['en']['period_pain'])
    elif any(word in question_lower for word in ['irregular', 'regular', 'अनियमित', 'ஒழுங்கற்ற', 'ಅನಿಯಮಿತ']):
        return FAQ_RESPONSES[language].get('irregular_period', FAQ_RESPONSES['en']['irregular_period'])
    elif any(word in question_lower for word in ['doctor', 'consult', 'see', 'डॉक्टर', 'மருத்துவர்', 'ವೈದ್ಯ']):
        return FAQ_RESPONSES[language].get('doctor', FAQ_RESPONSES['en']['doctor'])
    else:
        # Default response
        default_responses = {
            'en': "I'm Sakhi, your health companion. I can help you with questions about menstrual health, PCOS, period pain, and general women's health concerns. Feel free to ask me anything!",
            'hi': "मैं सखी हूँ, आपकी स्वास्थ्य साथी। मैं आपको मासिक धर्म स्वास्थ्य, PCOS, पीरियड दर्द और सामान्य महिलाओं के स्वास्थ्य संबंधी प्रश्नों में मदद कर सकती हूँ। मुझसे कुछ भी पूछने में संकोच न करें!",
            'ta': "நான் சகி, உங்கள் சுகாதார தோழி. மாதவிடாய் சுகாதாரம், PCOS, மாதவிடாய் வலி மற்றும் பொதுவான பெண்களின் சுகாதார கவலைகள் பற்றிய கேள்விகளுக்கு நான் உங்களுக்கு உதவ முடியும். என்னிடம் எதையும் கேட்க தயங்க வேண்டாம்!",
            'kn': "ನಾನು ಸಖಿ, ನಿಮ್ಮ ಆರೋಗ್ಯ ಸಹಚರಿ. ಮುಟ್ಟಿನ ಆರೋಗ್ಯ, PCOS, ಮುಟ್ಟಿನ ನೋವು ಮತ್ತು ಸಾಮಾನ್ಯ ಮಹಿಳೆಯರ ಆರೋಗ್ಯ ಕಾಳಜಿಗಳ ಬಗ್ಗೆ ಪ್ರಶ್ನೆಗಳೊಂದಿಗೆ ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ. ನನ್ನನ್ನು ಏನು ಬೇಕಾದರೂ ಕೇಳಲು ಮುಕ್ತವಾಗಿರಿ!"
        }
        return default_responses.get(language, default_responses['en'])

@router.post("/ask", response_model=ChatResponse)
async def ask_chatbot(user_id: int, request: ChatRequest):
    """Ask a question to the chatbot using LLM with user context"""
    try:
        # Check if user is anonymous
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT is_anonymous FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        is_anonymous = user_row['is_anonymous'] if user_row else True
        conn.close()

        # Get AI-powered response with user context
        response_data = await chatbot_service.get_response(
            user_id=user_id,
            question=request.question,
            language=request.language,
            is_anonymous=is_anonymous
        )

        answer = response_data['answer']
        ai_powered = response_data.get('ai_powered', False)

        # Save to chat history
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO chat_history (user_id, question, answer, language)
               VALUES (?, ?, ?, ?)''',
            (user_id, request.question, answer, request.language)
        )
        conn.commit()
        conn.close()

        return ChatResponse(
            answer=answer,
            language=request.language,
            translated=False,
            ai_powered=ai_powered
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{user_id}")
async def get_chat_history(user_id: int, limit: int = 10):
    """Get chat history for a user"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT * FROM chat_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
        (user_id, limit)
    )
    history = cursor.fetchall()
    conn.close()

    return [dict(chat) for chat in history]

@router.delete("/history/{user_id}")
async def clear_chat_history(user_id: int):
    """Clear chat history for a user"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

    return MessageResponse(message="Chat history cleared successfully")
