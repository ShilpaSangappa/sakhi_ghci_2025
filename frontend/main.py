"""
Main Kivy application for Sakhi App
Entry point for the mobile application
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.lang import Builder
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from localization import set_language, get_current_language

# Import all screens
from screens.login import LoginScreen
from screens.home import HomeScreen
from screens.period_tracker import PeriodTrackerScreen
from screens.community import CommunityScreen
from screens.meetups import MeetupsScreen
from screens.analytics import AnalyticsScreen
from screens.chatbot import ChatbotScreen

# Import and setup fonts for Indic languages
from config import setup_fonts

# Set window size for development (mobile size)
Window.size = (360, 640)

# Setup fonts before creating any widgets
setup_fonts()

class SakhiApp(App):
    """Main Sakhi Application"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_id = None
        self.user_name = None
        self.user_language = 'en'

    def build(self):
        """Build the application"""
        # Create screen manager
        self.screen_manager = ScreenManager()

        # Add all screens
        self.screen_manager.add_widget(LoginScreen(name='login'))
        self.screen_manager.add_widget(HomeScreen(name='home'))
        self.screen_manager.add_widget(PeriodTrackerScreen(name='period_tracker'))
        self.screen_manager.add_widget(CommunityScreen(name='community'))
        self.screen_manager.add_widget(MeetupsScreen(name='meetups'))
        self.screen_manager.add_widget(AnalyticsScreen(name='analytics'))
        self.screen_manager.add_widget(ChatbotScreen(name='chatbot'))

        # Set initial screen
        self.screen_manager.current = 'login'

        return self.screen_manager

    def set_user(self, user_id, user_name, language='en'):
        """Set current user information"""
        self.user_id = user_id
        self.user_name = user_name
        self.user_language = language
        set_language(language)

    def get_user_id(self):
        """Get current user ID"""
        return self.user_id

    def get_user_name(self):
        """Get current user name"""
        return self.user_name

    def get_user_language(self):
        """Get current user language"""
        return self.user_language

    def change_screen(self, screen_name):
        """Change to a different screen"""
        self.screen_manager.current = screen_name

    def logout(self):
        """Logout user and return to login screen"""
        self.user_id = None
        self.user_name = None
        self.user_language = 'en'
        self.screen_manager.current = 'login'

if __name__ == '__main__':
    SakhiApp().run()
