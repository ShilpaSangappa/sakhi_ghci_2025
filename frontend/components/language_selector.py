"""
Language Selector Component for Sakhi App
"""

from kivy.uix.spinner import Spinner
from kivy.app import App
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from localization import set_language, get_text

class LanguageSelector(Spinner):
    """Language selector dropdown widget"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Language options
        self.languages = {
            'English': 'en',
            'हिंदी': 'hi',
            'தமிழ்': 'ta',
            'ಕನ್ನಡ': 'kn'
        }

        # Set spinner properties
        self.text = 'English'
        self.values = list(self.languages.keys())
        self.bind(text=self.on_language_change)

    def on_language_change(self, spinner, text):
        """Handle language change"""
        lang_code = self.languages.get(text, 'en')

        # Update global language
        set_language(lang_code)

        # Update app language
        app = App.get_running_app()
        if hasattr(app, 'user_language'):
            app.user_language = lang_code

        print(f"Language changed to: {lang_code}")

    def set_language_by_code(self, lang_code):
        """Set language by code"""
        # Reverse lookup
        for display_name, code in self.languages.items():
            if code == lang_code:
                self.text = display_name
                break
