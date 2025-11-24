"""
Translation Manager for Sakhi App
Handles static UI translations (no API calls - instant switching)
"""

import json
import os

class TranslationManager:
    def __init__(self):
        self.translations = {}
        self.current_language = 'en'
        self.supported_languages = ['en', 'hi', 'ta', 'kn']
        self.load_translations()

    def load_translations(self):
        """Load all static translation files"""
        base_path = os.path.dirname(os.path.abspath(__file__))

        for lang in self.supported_languages:
            file_path = os.path.join(base_path, f"{lang}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations[lang] = json.load(f)
                print(f"✓ Loaded {lang} translations")
            else:
                print(f"✗ Warning: {lang}.json not found")

    def set_language(self, lang_code):
        """Switch UI language - instant, no API call"""
        if lang_code in self.supported_languages:
            self.current_language = lang_code
            print(f"Language switched to: {lang_code}")
            return True
        else:
            print(f"Unsupported language: {lang_code}")
            return False

    def get(self, key_path, lang=None):
        """
        Get translation by key path (e.g., 'auth.login')
        Returns translated string in current or specified language

        Args:
            key_path: Dot-separated path to translation key
            lang: Optional language code (uses current if not specified)

        Returns:
            Translated string or key_path if not found
        """
        target_lang = lang if lang else self.current_language
        keys = key_path.split('.')
        translation = self.translations.get(target_lang, {})

        for key in keys:
            if isinstance(translation, dict):
                translation = translation.get(key)
            else:
                break

            if translation is None:
                # Fallback to English if translation not found
                if target_lang != 'en':
                    return self.get(key_path, 'en')
                return key_path

        return translation if isinstance(translation, str) else key_path

    def get_all(self, section, lang=None):
        """
        Get all translations for a section

        Args:
            section: Section name (e.g., 'auth', 'navigation')
            lang: Optional language code

        Returns:
            Dictionary of translations for that section
        """
        target_lang = lang if lang else self.current_language
        return self.translations.get(target_lang, {}).get(section, {})

    def get_supported_languages(self):
        """Get list of supported language codes"""
        return self.supported_languages

    def is_rtl(self, lang=None):
        """Check if language is right-to-left"""
        # None of our supported languages are RTL
        target_lang = lang if lang else self.current_language
        rtl_languages = []  # Add 'ur', 'ar' etc. if needed
        return target_lang in rtl_languages

    def get_language_info(self):
        """Get information about all supported languages"""
        return [
            {'code': 'en', 'name': 'English', 'native': 'English'},
            {'code': 'hi', 'name': 'Hindi', 'native': 'हिंदी'},
            {'code': 'ta', 'name': 'Tamil', 'native': 'தமிழ்'},
            {'code': 'kn', 'name': 'Kannada', 'native': 'ಕನ್ನಡ'}
        ]

# Global instance
translator = TranslationManager()

# Convenience functions
def get_text(key, lang=None):
    """
    Shorthand function to get translated text

    Usage:
        get_text('auth.login')  # Returns login text in current language
        get_text('common.save', 'hi')  # Returns save text in Hindi
    """
    return translator.get(key, lang)

def get_text_formatted(key, **kwargs):
    """
    Get translated text with variable substitution

    Usage:
        get_text_formatted('welcome_message', name='Priya')
        # If translation is "Welcome, {name}!", returns "Welcome, Priya!"
    """
    text = translator.get(key)
    try:
        return text.format(**kwargs)
    except:
        return text

def set_language(lang_code):
    """Set the current language"""
    return translator.set_language(lang_code)

def get_current_language():
    """Get the current language code"""
    return translator.current_language

if __name__ == "__main__":
    # Test the translation manager
    print("=== Testing Translation Manager ===\n")

    # Test English
    print("English:")
    print(f"  Login: {get_text('auth.login')}")
    print(f"  Period Tracker: {get_text('navigation.period_tracker')}")

    # Test Hindi
    set_language('hi')
    print("\nHindi:")
    print(f"  Login: {get_text('auth.login')}")
    print(f"  Period Tracker: {get_text('navigation.period_tracker')}")

    # Test Tamil
    set_language('ta')
    print("\nTamil:")
    print(f"  Login: {get_text('auth.login')}")
    print(f"  Period Tracker: {get_text('navigation.period_tracker')}")

    # Test Kannada
    set_language('kn')
    print("\nKannada:")
    print(f"  Login: {get_text('auth.login')}")
    print(f"  Period Tracker: {get_text('navigation.period_tracker')}")

    # Test section retrieval
    set_language('en')
    print("\nAll navigation items (English):")
    nav_items = translator.get_all('navigation')
    for key, value in nav_items.items():
        print(f"  {key}: {value}")
