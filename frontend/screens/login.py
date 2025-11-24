"""
Login Screen for Sakhi App
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.app import App
import sys
import os
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from localization import get_text, set_language, translator

API_BASE_URL = "http://localhost:8000"

class LoginScreen(Screen):
    """Login screen with language selection"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_signup_mode = True  # Default to signup mode
        self.build_ui()

    def build_ui(self):
        """Build the login UI"""
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Title
        title = Label(
            text="Sign Up" if self.is_signup_mode else "Login",
            font_size='24sp',
            size_hint=(1, 0.12),
            bold=True
        )
        layout.add_widget(title)

        # Subtitle
        subtitle = Label(
            text=get_text('tagline'),
            font_size='16sp',
            size_hint=(1, 0.08),
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(subtitle)

        # Mode toggle buttons
        mode_layout = BoxLayout(size_hint=(1, 0.08), spacing=5)

        signup_btn = Button(
            text="Sign Up",
            background_color=(1.0, 0.0, 0.4, 1) if self.is_signup_mode else (0.7, 0.7, 0.7, 1)
        )
        signup_btn.bind(on_press=lambda x: self.switch_mode(True))
        mode_layout.add_widget(signup_btn)

        login_btn = Button(
            text="Login",
            background_color=(1.0, 0.0, 0.4, 1) if not self.is_signup_mode else (0.7, 0.7, 0.7, 1)
        )
        login_btn.bind(on_press=lambda x: self.switch_mode(False))
        mode_layout.add_widget(login_btn)

        layout.add_widget(mode_layout)

        # Language selector
        lang_label = Label(
            text=get_text('auth.select_language'),
            font_size='14sp',
            size_hint=(1, 0.08)
        )
        layout.add_widget(lang_label)

        # Get current language and map to display name
        current_lang = translator.current_language
        lang_display_map = {
            'en': 'English',
            'hi': 'हिंदी',
            'ta': 'தமிழ்',
            'kn': 'ಕನ್ನಡ'
        }

        self.language_spinner = Spinner(
            text=lang_display_map.get(current_lang, 'English'),
            values=('English', 'हिंदी', 'தமிழ்', 'ಕನ್ನಡ'),
            size_hint=(1, 0.1),
            background_color = (1.0, 0.0, 0.4, 1)
        )
        self.language_spinner.bind(text=self.on_language_change)
        layout.add_widget(self.language_spinner)

        # Phone number input
        phone_label = Label(
            text=get_text('auth.phone_placeholder'),
            font_size='14sp',
            size_hint=(1, 0.08)
        )
        layout.add_widget(phone_label)

        self.phone_input = TextInput(
            hint_text=get_text('auth.phone_placeholder'),
            multiline=False,
            size_hint=(1, 0.1),
            input_filter='int'
        )
        layout.add_widget(self.phone_input)

        # Name input (only for signup mode)
        if self.is_signup_mode:
            name_label = Label(
                text=get_text('auth.name_placeholder'),
                font_size='14sp',
                size_hint=(1, 0.08)
            )
            layout.add_widget(name_label)

            self.name_input = TextInput(
                hint_text=get_text('auth.name_placeholder'),
                multiline=False,
                size_hint=(1, 0.1)
            )
            layout.add_widget(self.name_input)
        else:
            # Add placeholder for login mode (no name field)
            self.name_input = None

        # Login/Signup button
        action_btn = Button(
            text="Sign Up" if self.is_signup_mode else "Login",
            size_hint=(1, 0.12),
            background_color = (1.0, 0.0, 0.4, 1),
            font_size='16sp'
        )
        action_btn.bind(on_press=self.on_submit)
        layout.add_widget(action_btn)

        # Anonymous button
        anonymous_btn = Button(
            text=get_text('auth.anonymous_mode'),
            size_hint=(1, 0.12),
            background_color=(0.5, 0.5, 0.5, 1),
            font_size='14sp'
        )
        anonymous_btn.bind(on_press=self.on_anonymous_login)
        layout.add_widget(anonymous_btn)

        self.add_widget(layout)

    def on_language_change(self, spinner, text):
        """Handle language change"""
        # Map display name to language code
        lang_map = {
            'English': 'en',
            'हिंदी': 'hi',
            'தமிழ்': 'ta',
            'ಕನ್ನಡ': 'kn'
        }

        lang_code = lang_map.get(text, 'en')
        set_language(lang_code)

        # Refresh UI with new language
        self.clear_widgets()
        self.build_ui()

    def switch_mode(self, is_signup):
        """Switch between signup and login mode"""
        self.is_signup_mode = is_signup
        self.clear_widgets()
        self.build_ui()

    def on_submit(self, instance):
        """Handle signup or login submission"""
        if self.is_signup_mode:
            self.on_signup(instance)
        else:
            self.on_login_only(instance)

    def on_signup(self, instance):
        """Handle signup button press"""
        phone = self.phone_input.text.strip()
        name = self.name_input.text.strip() if self.name_input else ""

        if not phone:
            self.show_popup(get_text('common.error'), "Please enter your phone number")
            return

        # Validate phone number is exactly 10 digits
        if not phone.isdigit() or len(phone) != 10:
            self.show_popup(get_text('common.error'), "Phone number must be exactly 10 digits")
            return

        if not name:
            self.show_popup(get_text('common.error'), "Please enter your name")
            return

        lang_code = translator.current_language

        # Check if user already exists
        user_exists, user_id, existing_name = self.login_user(phone)

        if user_exists:
            self.show_popup(get_text('common.error'), f"Phone number already registered. Please use Login instead.")
            return

        # Register new user
        success, user_id = self.register_user(phone, name, lang_code, anonymous=False)

        if success:
            # Set user in app
            app = App.get_running_app()
            app.set_user(user_id, name, lang_code)

            # Navigate to home screen
            app.change_screen('home')
        else:
            self.show_popup(get_text('common.error'), "Registration failed. Please try again.")

    def on_login_only(self, instance):
        """Handle login button press (login mode only)"""
        phone = self.phone_input.text.strip()

        if not phone:
            self.show_popup(get_text('common.error'), "Please enter your phone number")
            return

        # Validate phone number is exactly 10 digits
        if not phone.isdigit() or len(phone) != 10:
            self.show_popup(get_text('common.error'), "Phone number must be exactly 10 digits")
            return

        lang_code = translator.current_language

        # Try to login
        success, user_id, existing_name = self.login_user(phone)

        if success:
            # User exists, login successful
            app = App.get_running_app()
            app.set_user(user_id, existing_name, lang_code)
            app.change_screen('home')
        else:
            # User doesn't exist
            self.show_popup(get_text('common.error'), "Mobile number not registered. Please use Sign Up to create an account.")

    def on_anonymous_login(self, instance):
        """Handle anonymous login"""
        name = "Guest"
        lang_code = translator.current_language

        # Register anonymous user
        success, user_id = self.register_user(None, name, lang_code, anonymous=True)

        if success:
            # Set user in app
            app = App.get_running_app()
            app.set_user(user_id, name, lang_code)

            # Navigate to home screen
            app.change_screen('home')
        else:
            self.show_popup(get_text('common.error'), "Login failed. Please try again.")

    def login_user(self, phone):
        """Try to login existing user via API"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/login",
                params={"phone": phone},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                user_id = data.get('user_id')
                name = data.get('name')
                return True, user_id, name
            else:
                # User doesn't exist
                return False, None, None

        except Exception as e:
            print(f"Login error: {e}")
            return False, None, None

    def register_user(self, phone, name, language, anonymous=False):
        """Register user via API"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/auth/register",
                json={
                    "phone": phone,
                    "name": name,
                    "language_pref": language,
                    "city": None,
                    "anonymous": anonymous
                },
                timeout=5
            )

            if response.status_code == 200:
                # Extract user ID from message
                message = response.json().get('message', '')
                user_id = int(message.split(':')[-1].strip())
                return True, user_id
            else:
                return False, None

        except Exception as e:
            print(f"Registration error: {e}")
            # For demo, create a mock user ID
            import random
            return True, random.randint(1, 1000)

    def show_popup(self, title, message):
        """Show a popup message"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
