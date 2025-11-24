"""
Voice Input Component for Sakhi App
"""

from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from localization import get_text

class VoiceInputWidget(Button):
    """Voice input button widget"""

    def __init__(self, on_voice_result=None, **kwargs):
        super().__init__(**kwargs)

        self.text = get_text('chatbot.voice_input')
        self.background_color = (0.7, 0.5, 0.8, 1)
        self.on_voice_result = on_voice_result

        self.bind(on_press=self.start_voice_input)

    def start_voice_input(self, instance):
        """Start voice input"""
        # Show listening popup
        self.show_listening_popup()

        # TODO: Implement actual voice recognition
        # For now, just simulate
        self.simulate_voice_recognition()

    def show_listening_popup(self):
        """Show listening popup"""
        self.popup = Popup(
            title=get_text('chatbot.listening'),
            content=Label(text=f"{get_text('chatbot.speak')}..."),
            size_hint=(0.8, 0.3),
            auto_dismiss=True
        )
        self.popup.open()

    def simulate_voice_recognition(self):
        """Simulate voice recognition (placeholder)"""
        # In production, use speech_recognition library
        import threading
        import time

        def recognize():
            time.sleep(2)  # Simulate processing
            result = "What is PCOS?"  # Mock result

            # Close popup
            if self.popup:
                self.popup.dismiss()

            # Call callback with result
            if self.on_voice_result:
                self.on_voice_result(result)

        thread = threading.Thread(target=recognize)
        thread.start()

    def recognize_speech(self):
        """Actual speech recognition implementation"""
        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()

            with sr.Microphone() as source:
                audio = recognizer.listen(source, timeout=5)

            # Recognize speech
            text = recognizer.recognize_google(audio)

            # Close popup
            if self.popup:
                self.popup.dismiss()

            # Call callback
            if self.on_voice_result:
                self.on_voice_result(text)

        except Exception as e:
            print(f"Voice recognition error: {e}")

            if self.popup:
                self.popup.dismiss()

            # Show error popup
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Voice recognition failed"),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()
