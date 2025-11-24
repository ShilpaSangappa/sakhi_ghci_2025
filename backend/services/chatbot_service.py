"""
Chatbot Service using Claude AI via LiteLLM with User Health Data Access
Provides personalized health guidance based on user's period tracking data
"""

from litellm import completion
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from database import db

class ChatbotService:
    """LLM-powered chatbot service using Claude via LiteLLM for women's health queries"""

    def __init__(self):
        # Get API key from environment variable
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            print("Warning: ANTHROPIC_API_KEY not set. Chatbot will use FAQ responses.")

        # LiteLLM will use the ANTHROPIC_API_KEY from environment

        # System prompt for Sakhi chatbot
        self.system_prompt = """You are Sakhi, a compassionate and knowledgeable women's health companion chatbot. You specialize in:
- Menstrual health and cycle tracking
- PCOS (Polycystic Ovary Syndrome)
- Period pain management
- Hormonal health
- General women's wellness

Your personality:
- Warm, supportive, and empathetic
- Culturally sensitive to Indian context
- Evidence-based but accessible
- Never judgmental
- Encouraging self-care and professional medical consultation when needed

Important guidelines:
- NEVER diagnose medical conditions
- Always recommend consulting a doctor for serious concerns
- Provide general health information and wellness tips
- Be supportive and normalize conversations about periods
- Respect privacy and confidentiality
- If user has logged health data, reference it to provide personalized guidance"""

    async def get_response(self, user_id: int, question: str, language: str, is_anonymous: bool = False) -> Dict:
        """Get chatbot response with optional user health context"""

        # Get user's health context if not anonymous
        user_context = ""
        if not is_anonymous and user_id:
            user_context = self._build_user_context(user_id)

        # If no API key, fall back to FAQ
        if not self.api_key:
            return {
                "answer": self._get_faq_fallback(question, language),
                "language": language,
                "ai_powered": False,
                "has_user_context": False
            }

        # Generate AI response using Claude via LiteLLM
        try:
            # Build the prompt with user context
            user_message = self._build_prompt(question, user_context, language, is_anonymous)

            # Use LiteLLM's completion function with Claude
            response = completion(
                model="claude-3-5-sonnet-20241022",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=800,
                temperature=0.7,  # Slightly creative but still reliable
                api_key=self.api_key
            )

            answer = response.choices[0].message.content

            return {
                "answer": answer,
                "language": language,
                "ai_powered": True,
                "has_user_context": bool(user_context and not is_anonymous)
            }

        except Exception as e:
            print(f"Error generating AI response: {e}")
            # Fallback to FAQ
            return {
                "answer": self._get_faq_fallback(question, language),
                "language": language,
                "ai_powered": False,
                "has_user_context": False
            }

    def _build_user_context(self, user_id: int) -> str:
        """Build context from user's health data"""
        conn = db.get_connection()
        cursor = conn.cursor()

        context_parts = []

        # Get recent period logs
        cursor.execute(
            '''SELECT start_date, end_date, flow_level, symptoms, notes
               FROM period_logs
               WHERE user_id = ?
               ORDER BY start_date DESC
               LIMIT 6''',
            (user_id,)
        )
        period_logs = cursor.fetchall()

        if period_logs:
            context_parts.append("User's Recent Period Data:")
            for i, log in enumerate(period_logs[:3], 1):  # Most recent 3 cycles
                log_dict = dict(log)
                duration = "ongoing"
                if log_dict['end_date']:
                    start = datetime.strptime(log_dict['start_date'], '%Y-%m-%d')
                    end = datetime.strptime(log_dict['end_date'], '%Y-%m-%d')
                    duration = f"{(end - start).days + 1} days"

                flow = {1: "light", 2: "medium", 3: "heavy"}.get(log_dict['flow_level'], "unknown")
                symptoms = log_dict['symptoms'] if log_dict['symptoms'] else "none reported"

                context_parts.append(f"- Cycle {i}: Started {log_dict['start_date']}, Duration: {duration}, Flow: {flow}, Symptoms: {symptoms}")

        # Calculate cycle statistics if enough data
        if len(period_logs) >= 2:
            cycle_lengths = []
            for i in range(len(period_logs) - 1):
                current = datetime.strptime(dict(period_logs[i])['start_date'], '%Y-%m-%d')
                next_period = datetime.strptime(dict(period_logs[i + 1])['start_date'], '%Y-%m-%d')
                cycle_length = (current - next_period).days
                if cycle_length > 0:
                    cycle_lengths.append(cycle_length)

            if cycle_lengths:
                avg_cycle = sum(cycle_lengths) / len(cycle_lengths)
                context_parts.append(f"\nAverage Cycle Length: {avg_cycle:.1f} days")

                # Regularity
                std_dev = (sum((x - avg_cycle) ** 2 for x in cycle_lengths) / len(cycle_lengths)) ** 0.5
                if std_dev <= 3:
                    regularity = "regular"
                elif std_dev <= 7:
                    regularity = "somewhat irregular"
                else:
                    regularity = "irregular"
                context_parts.append(f"Cycle Regularity: {regularity}")

        # Get recent community activity (anonymized)
        cursor.execute(
            '''SELECT COUNT(*) as post_count FROM posts WHERE user_id = ?''',
            (user_id,)
        )
        post_count = cursor.fetchone()['post_count']
        if post_count > 0:
            context_parts.append(f"\nUser is active in community (made {post_count} posts)")

        conn.close()

        if context_parts:
            return "\n".join(context_parts)
        return ""

    def _build_prompt(self, question: str, user_context: str, language: str, is_anonymous: bool) -> str:
        """Build the complete prompt for Claude"""

        prompt_parts = []

        # Add user context if available
        if user_context and not is_anonymous:
            prompt_parts.append("=== USER'S HEALTH DATA (for personalized response) ===")
            prompt_parts.append(user_context)
            prompt_parts.append("=== END OF USER DATA ===\n")
            prompt_parts.append("Please use this data to provide personalized, relevant guidance. Reference specific patterns you see if appropriate.")
            prompt_parts.append("")

        # Add language instruction if not English
        if language != 'en':
            lang_names = {'hi': 'Hindi', 'ta': 'Tamil', 'kn': 'Kannada'}
            lang_name = lang_names.get(language, 'English')
            prompt_parts.append(f"Please respond in {lang_name} language.")
            prompt_parts.append("")

        # Add the actual question
        prompt_parts.append(f"User's Question: {question}")

        if is_anonymous:
            prompt_parts.append("\n(Note: User is anonymous, no personal health data available. Provide general guidance only.)")

        return "\n".join(prompt_parts)

    def _get_faq_fallback(self, question: str, language: str) -> str:
        """Fallback FAQ responses when AI is unavailable"""

        # Pre-defined responses for common questions
        FAQ_RESPONSES = {
            "en": {
                "pcos": "PCOS (Polycystic Ovary Syndrome) is a hormonal disorder affecting women of reproductive age. Common symptoms include irregular periods, excess androgen, and polycystic ovaries. Management includes lifestyle changes, medication, and regular monitoring. I recommend consulting a gynecologist for proper diagnosis and treatment plan.",
                "period_pain": "To manage period pain: 1) Use heating pad on lower abdomen 2) Take over-the-counter pain relievers 3) Exercise regularly 4) Try relaxation techniques 5) Stay hydrated. If pain is severe or affecting your daily life, please consult a doctor.",
                "irregular_period": "Irregular periods can be normal, especially during puberty or perimenopause. However, if you're experiencing significant irregularity, it's best to consult a gynecologist to rule out conditions like PCOS, thyroid issues, or hormonal imbalances.",
                "doctor": "See a doctor if you experience: Very heavy bleeding (soaking through pad/tampon every hour), severe pain not relieved by medication, periods lasting >7 days, bleeding between periods, irregular periods affecting daily life, or periods stopping suddenly if you're not pregnant.",
                "default": "I'm Sakhi, your health companion. I can help you with questions about menstrual health, PCOS, period pain, and general women's health concerns. Feel free to ask me anything! If you have specific health concerns, I always recommend consulting with a healthcare provider."
            },
            "hi": {
                "pcos": "PCOS (पॉलीसिस्टिक ओवरी सिंड्रोम) प्रजनन आयु की महिलाओं को प्रभावित करने वाला एक हार्मोनल विकार है। सामान्य लक्षणों में अनियमित पीरियड, अतिरिक्त एंड्रोजन और पॉलीसिस्टिक अंडाशय शामिल हैं। प्रबंधन में जीवनशैली में बदलाव, दवा और नियमित निगरानी शामिल है। मैं उचित निदान और उपचार योजना के लिए स्त्री रोग विशेषज्ञ से परामर्श करने की सलाह देती हूँ।",
                "period_pain": "पीरियड के दर्द को प्रबंधित करने के लिए: 1) पेट के निचले हिस्से पर हीटिंग पैड का उपयोग करें 2) दर्द निवारक दवाएं लें 3) नियमित रूप से व्यायाम करें 4) विश्राम तकनीकों का प्रयास करें 5) हाइड्रेटेड रहें। यदि दर्द गंभीर है या आपके दैनिक जीवन को प्रभावित कर रहा है, तो कृपया डॉक्टर से परामर्श करें।",
                "irregular_period": "अनियमित पीरियड सामान्य हो सकते हैं, खासकर यौवन या रजोनिवृत्ति के दौरान। हालांकि, यदि आप महत्वपूर्ण अनियमितता का अनुभव कर रहे हैं, तो PCOS, थायराइड मुद्दों या हार्मोनल असंतुलन जैसी स्थितियों को खारिज करने के लिए स्त्री रोग विशेषज्ञ से परामर्श करना सबसे अच्छा है।",
                "doctor": "डॉक्टर को दिखाएं यदि आप अनुभव करते हैं: बहुत भारी रक्तस्राव, गंभीर दर्द, 7 दिनों से अधिक समय तक चलने वाले पीरियड, पीरियड्स के बीच रक्तस्राव, दैनिक जीवन को प्रभावित करने वाले अनियमित पीरियड, या यदि आप गर्भवती नहीं हैं तो अचानक पीरियड बंद हो जाना।",
                "default": "मैं सखी हूँ, आपकी स्वास्थ्य साथी। मैं आपको मासिक धर्म स्वास्थ्य, PCOS, पीरियड दर्द और सामान्य महिलाओं के स्वास्थ्य संबंधी प्रश्नों में मदद कर सकती हूँ। मुझसे कुछ भी पूछने में संकोच न करें! यदि आपके पास विशिष्ट स्वास्थ्य चिंताएं हैं, तो मैं हमेशा स्वास्थ्य सेवा प्रदाता से परामर्श करने की सलाह देती हूँ।"
            },
            "ta": {
                "pcos": "PCOS (பாலிசிஸ்டிக் ஓவரி சிண்ட்ரோம்) என்பது இனப்பெருக்க வயதுடைய பெண்களை பாதிக்கும் ஒரு ஹார்மோன் கோளாறு। பொதுவான அறிகுறிகளில் ஒழுங்கற்ற மாதவிடாய், அதிகப்படியான ஆண்ட்ரோஜன் மற்றும் பாலிசிஸ்டிக் கருப்பைகள் அடங்கும். சரியான நோய் கண்டறிதல் மற்றும் சிகிச்சை திட்டத்திற்கு மகப்பேறு மருத்துவரை அணுக பரிந்துரைக்கிறேன்।",
                "period_pain": "மாதவிடாய் வலியை நிர்வகிக்க: 1) அடிவயிற்றில் ஹீட்டிங் பேட் பயன்படுத்தவும் 2) வலி நிவாரணிகள் எடுத்துக்கொள்ளவும் 3) தவறாமல் உடற்பயிற்சி செய்யவும் 4) ரிலாக்சேஷன் தொழில்நுட்பங்களை முயற்சிக்கவும் 5) நீர்ச்சத்துடன் இருக்கவும். வலி கடுமையாக இருந்தால் அல்லது உங்கள் அன்றாட வாழ்க்கையை பாதிக்கிறது என்றால், தயவுசெய்து மருத்துவரை அணுகவும்।",
                "irregular_period": "ஒழுங்கற்ற மாதவிடாய் சாதாரணமானதாக இருக்கலாம், குறிப்பாக பருவமடையும் போது அல்லது மெனோபாஸ் காலத்தில். இருப்பினும், நீங்கள் குறிப்பிடத்தக்க ஒழுங்கின்மையை அனுபவித்தால், PCOS, தைராய்டு பிரச்சினைகள் அல்லது ஹார்மோன் சமநிலையின்மை போன்ற நிலைமைகளை நிராகரிக்க மகப்பேறு மருத்துவரை அணுகுவது சிறந்தது।",
                "doctor": "நீங்கள் அனுபவித்தால் மருத்துவரை பாருங்கள்: மிகவும் கனமான இரத்தப்போக்கு, கடுமையான வலி, 7 நாட்களுக்கு மேல் நீடிக்கும் மாதவிடாய், மாதவிடாய்களுக்கு இடையில் இரத்தப்போக்கு, அன்றாட வாழ்க்கையை பாதிக்கும் ஒழுங்கற்ற மாதவிடாய், அல்லது நீங்கள் கர்ப்பமாக இல்லாதபோது திடீரென மாதவிடாய் நின்றுவிட்டால்.",
                "default": "நான் சகி, உங்கள் சுகாதார தோழி. மாதவிடாய் சுகாதாரம், PCOS, மாதவிடாய் வலி மற்றும் பொதுவான பெண்களின் சுகாதார கவலைகள் பற்றிய கேள்விகளுக்கு நான் உங்களுக்கு உதவ முடியும். என்னிடம் எதையும் கேட்க தயங்க வேண்டாம்! குறிப்பிட்ட சுகாதார கவலைகள் இருந்தால், சுகாதார வழங்குநரை அணுக நான் எப்போதும் பரிந்துரைக்கிறேன்."
            },
            "kn": {
                "pcos": "PCOS (ಪಾಲಿಸಿಸ್ಟಿಕ್ ಓವರಿ ಸಿಂಡ್ರೋಮ್) ಸಂತಾನೋತ್ಪತ್ತಿ ವಯಸ್ಸಿನ ಮಹಿಳೆಯರ ಮೇಲೆ ಪರಿಣಾಮ ಬೀರುವ ಹಾರ್ಮೋನ್ ಅಸ್ವಸ್ಥತೆ. ಸರಿಯಾದ ರೋಗನಿರ್ಣಯ ಮತ್ತು ಚಿಕಿತ್ಸಾ ಯೋಜನೆಗಾಗಿ ಸ್ತ್ರೀರೋಗ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸಲು ನಾನು ಶಿಫಾರಸು ಮಾಡುತ್ತೇನೆ।",
                "period_pain": "ಮುಟ್ಟಿನ ನೋವನ್ನು ನಿರ್ವಹಿಸಲು: 1) ಕೆಳ ಹೊಟ್ಟೆಯ ಮೇಲೆ ಹೀಟಿಂಗ್ ಪ್ಯಾಡ್ ಬಳಸಿ 2) ನೋವು ನಿವಾರಕಗಳನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ 3) ನಿಯಮಿತವಾಗಿ ವ್ಯಾಯಾಮ ಮಾಡಿ 4) ವಿಶ್ರಾಂತಿ ತಂತ್ರಗಳನ್ನು ಪ್ರಯತ್ನಿಸಿ 5) ಹೈಡ್ರೇಟೆಡ್ ಆಗಿರಿ। ನೋವು ತೀವ್ರವಾಗಿದ್ದರೆ ಅಥವಾ ನಿಮ್ಮ ದೈನಂದಿನ ಜೀವನವನ್ನು ಪರಿಣಾಮ ಬೀರುತ್ತಿದ್ದರೆ, ದಯವಿಟ್ಟು ವೈದ್ಯರನ್ನು ಸಂಪರ್ಕಿಸಿ।",
                "irregular_period": "ಅನಿಯಮಿತ ಮುಟ್ಟು ಸಾಮಾನ್ಯವಾಗಿರಬಹುದು, ವಿಶೇಷವಾಗಿ ಪ್ರೌಢಾವಸ್ಥೆ ಅಥವಾ ಋತುಬಂಧ ಸಮಯದಲ್ಲಿ। ಆದಾಗ್ಯೂ, ನೀವು ಗಮನಾರ್ಹ ಅನಿಯಮಿತತೆಯನ್ನು ಅನುಭವಿಸುತ್ತಿದ್ದರೆ, PCOS, ಥೈರಾಯ್ಡ್ ಸಮಸ್ಯೆಗಳು ಅಥವಾ ಹಾರ್ಮೋನ್ ಅಸಮತೋಲನದಂತಹ ಪರಿಸ್ಥಿತಿಗಳನ್ನು ತಳ್ಳಿಹಾಕಲು ಸ್ತ್ರೀರೋಗ ತಜ್ಞರನ್ನು ಸಂಪರ್ಕಿಸುವುದು ಉತ್ತಮ।",
                "doctor": "ನೀವು ಅನುಭವಿಸಿದರೆ ವೈದ್ಯರನ್ನು ನೋಡಿ: ಅತಿ ಹೆಚ್ಚು ರಕ್ತಸ್ರಾವ, ತೀವ್ರ ನೋವು, 7 ದಿನಗಳಿಗಿಂತ ಹೆಚ್ಚು ಕಾಲ ಮುಟ್ಟು, ಮುಟ್ಟುಗಳ ನಡುವೆ ರಕ್ತಸ್ರಾವ, ದೈನಂದಿನ ಜೀವನವನ್ನು ಪರಿಣಾಮ ಬೀರುವ ಅನಿಯಮಿತ ಮುಟ್ಟು, ಅಥವಾ ನೀವು ಗರ್ಭಿಣಿಯಾಗಿಲ್ಲದಿದ್ದರೆ ಮುಟ್ಟು ಇದ್ದಕ್ಕಿದ್ದಂತೆ ನಿಂತುಹೋಗುವುದು।",
                "default": "ನಾನು ಸಖಿ, ನಿಮ್ಮ ಆರೋಗ್ಯ ಸಹಚರಿ. ಮುಟ್ಟಿನ ಆರೋಗ್ಯ, PCOS, ಮುಟ್ಟಿನ ನೋವು ಮತ್ತು ಸಾಮಾನ್ಯ ಮಹಿಳೆಯರ ಆರೋಗ್ಯ ಕಾಳಜಿಗಳ ಬಗ್ಗೆ ಪ್ರಶ್ನೆಗಳೊಂದಿಗೆ ನಾನು ನಿಮಗೆ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ। ನನ್ನನ್ನು ಏನು ಬೇಕಾದರೂ ಕೇಳಲು ಮುಕ್ತವಾಗಿರಿ! ನಿರ್ದಿಷ್ಟ ಆರೋಗ್ಯ ಕಾಳಜಿಗಳಿದ್ದರೆ, ನಾನು ಯಾವಾಗಲೂ ಆರೋಗ್ಯ ಸೇವಾ ಪೂರೈಕೆದಾರರನ್ನು ಸಂಪರ್ಕಿಸಲು ಶಿಫಾರಸು ಮಾಡುತ್ತೇನೆ।"
            }
        }

        question_lower = question.lower()

        # Determine topic
        if any(word in question_lower for word in ['pcos', 'polycystic', 'pcod']):
            topic = 'pcos'
        elif any(word in question_lower for word in ['pain', 'cramp', 'hurt', 'दर्द', 'வலி', 'ನೋವು']):
            topic = 'period_pain'
        elif any(word in question_lower for word in ['irregular', 'regular', 'अनियमित', 'ஒழுங்கற்ற', 'ಅನಿಯಮಿತ']):
            topic = 'irregular_period'
        elif any(word in question_lower for word in ['doctor', 'consult', 'see', 'डॉक्टर', 'மருத்துவர்', 'ವೈದ್ಯ']):
            topic = 'doctor'
        else:
            topic = 'default'

        lang_responses = FAQ_RESPONSES.get(language, FAQ_RESPONSES['en'])
        return lang_responses.get(topic, lang_responses['default'])

# Global chatbot service instance
chatbot_service = ChatbotService()
