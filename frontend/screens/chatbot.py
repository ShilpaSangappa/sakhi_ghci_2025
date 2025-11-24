"""
Chatbot Screen for Sakhi App
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
import sys
import os
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from localization import get_text

API_BASE_URL = "http://localhost:8000"

class ChatbotScreen(Screen):
    """Chatbot screen with AI assistant"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chat_history = []
        self.build_ui()

    def build_ui(self):
        """Build the chatbot UI"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Header
        header = BoxLayout(size_hint=(1, 0.08), spacing=10)

        back_btn = Button(
            text=get_text('common.back'),
            size_hint=(0.3, 1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)

        title = Label(
            text=get_text('chatbot.title'),
            font_size='20sp',
            size_hint=(0.7, 1),
            bold=True
        )
        header.add_widget(title)

        layout.add_widget(header)

        # Common questions
        questions_label = Label(
            text=get_text('chatbot.common_questions'),
            font_size='14sp',
            size_hint=(1, 0.05)
        )
        layout.add_widget(questions_label)

        # Quick question buttons
        quick_questions = BoxLayout(size_hint=(1, 0.12), spacing=5)

        q1_btn = Button(
            text=get_text('chatbot.q1'),
            font_size='10sp',
            background_color=(0.4, 0.6, 0.8, 1)
        )
        q1_btn.bind(on_press=lambda x: self.ask_question(get_text('chatbot.q1')))

        q2_btn = Button(
            text=get_text('chatbot.q2'),
            font_size='10sp',
            background_color=(0.5, 0.7, 0.4, 1)
        )
        q2_btn.bind(on_press=lambda x: self.ask_question(get_text('chatbot.q2')))

        quick_questions.add_widget(q1_btn)
        quick_questions.add_widget(q2_btn)

        layout.add_widget(quick_questions)

        # Chat history
        self.chat_scroll = ScrollView(size_hint=(1, 0.6))
        self.chat_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=5)
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))

        # Welcome message
        welcome_msg = self.create_bot_message(
            "Hi! I'm Sakhi, your health companion. How can I help you today?"
        )
        self.chat_layout.add_widget(welcome_msg)

        self.chat_scroll.add_widget(self.chat_layout)
        layout.add_widget(self.chat_scroll)

        # Input section
        input_section = BoxLayout(size_hint=(1, 0.15), spacing=10)

        self.message_input = TextInput(
            hint_text=get_text('chatbot.placeholder'),
            multiline=False,
            size_hint=(0.65, 1)
        )

        voice_btn = Button(
            text=get_text('chatbot.voice_input'),
            size_hint=(0.2, 1),
            background_color=(0.7, 0.5, 0.8, 1)
        )
        voice_btn.bind(on_press=self.voice_input)

        send_btn = Button(
            text=get_text('common.submit'),
            size_hint=(0.15, 1),
            background_color = (1.0, 0.0, 0.4, 1)
        )
        send_btn.bind(on_press=self.send_message)

        input_section.add_widget(self.message_input)
        input_section.add_widget(voice_btn)
        input_section.add_widget(send_btn)

        layout.add_widget(input_section)

        self.add_widget(layout)

    def create_user_message(self, text):
        """Create a user message bubble"""
        msg_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=60,
            spacing=5
        )

        # Spacer
        msg_layout.add_widget(Label(size_hint=(0.1, 1)))

        # Message
        msg = Label(
            text=text,
            size_hint=(0.9, 1),
            text_size=(250, None),
            halign='right',
            valign='middle',
            color=(0.2, 0.6, 0.8, 1)
        )
        msg_layout.add_widget(msg)

        return msg_layout

    def create_bot_message(self, text):
        """Create a bot message bubble"""
        msg_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=80,
            spacing=5
        )

        # Message
        msg = Label(
            text=text,
            size_hint=(0.9, 1),
            text_size=(250, None),
            halign='left',
            valign='middle',
            color=(0.3, 0.7, 0.4, 1)
        )
        msg_layout.add_widget(msg)

        # Spacer
        msg_layout.add_widget(Label(size_hint=(0.1, 1)))

        return msg_layout

    def ask_question(self, question):
        """Ask a predefined question"""
        self.message_input.text = question
        self.send_message(None)

    def send_message(self, instance):
        """Send a message to the chatbot"""
        message = self.message_input.text.strip()
        if not message:
            return

        # Add user message
        user_msg = self.create_user_message(message)
        self.chat_layout.add_widget(user_msg)

        # Clear input
        self.message_input.text = ""

        # Get response from LLM-powered backend
        response = self.get_api_response(message)

        # Add bot response
        bot_msg = self.create_bot_message(response)
        self.chat_layout.add_widget(bot_msg)

        # Scroll to bottom
        self.chat_scroll.scroll_y = 0

    def get_api_response(self, message):
        """Get AI-powered response from backend"""
        try:
            # Get app instance
            app = App.get_running_app()
            user_id = app.get_user_id()
            current_lang = app.get_user_language()

            if not user_id:
                return "Please login to use the chatbot."

            # Call backend API
            response = requests.post(
                f"{API_BASE_URL}/chat/ask",
                params={"user_id": user_id},
                json={
                    "question": message,
                    "language": current_lang
                },
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                answer = data.get('answer', '')
                ai_powered = data.get('ai_powered', False)

                # Add AI badge if powered by LLM
                if ai_powered:
                    answer = f"🤖 {answer}"

                return answer
            else:
                return "Sorry, I couldn't process your request. Please try again."

        except Exception as e:
            print(f"Error getting chatbot response: {e}")
            # Fallback to simple response
            return self.get_simple_response(message)

    def get_simple_response(self, message):
        """Get a simple fallback response based on message"""
        message_lower = message.lower()

        if 'pcos' in message_lower:
            return "PCOS is a hormonal disorder. I recommend consulting a gynecologist for proper diagnosis and treatment."
        elif 'pain' in message_lower or 'cramp' in message_lower:
            return "For period pain, try: heating pads, light exercise, and over-the-counter pain relief. If severe, see a doctor."
        elif 'irregular' in message_lower:
            return "Irregular periods can have various causes. Track your cycle and consult a doctor if it persists."
        else:
            return "I'm here to help with women's health questions. Feel free to ask about periods, PCOS, or general health concerns!"

    def voice_input(self, instance):
        """Handle voice input"""
        # TODO: Implement voice recognition
        from kivy.uix.popup import Popup
        popup = Popup(
            title=get_text('chatbot.listening'),
            content=Label(text="Voice input coming soon..."),
            size_hint=(0.8, 0.3)
        )
        popup.open()

    def go_back(self, instance):
        """Go back to home screen"""
        app = App.get_running_app()
        app.change_screen('home')

    def on_enter(self):
        """Refresh UI when entering screen"""
        # Don't rebuild UI to preserve chat history
        pass
