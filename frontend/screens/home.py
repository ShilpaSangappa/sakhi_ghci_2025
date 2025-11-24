"""
Home Screen for Sakhi App
Main dashboard with navigation to all features
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from localization import get_text

class HomeScreen(Screen):
    """Home screen with feature navigation"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        """Build the home screen UI"""
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # Header
        app = App.get_running_app()
        user_name = app.get_user_name() if app.user_name else "Guest"

        header = Label(
            text=f"{get_text('auth.welcome')}, {user_name}!",
            font_size='20sp',
            size_hint=(1, 0.1),
            bold=True
        )
        layout.add_widget(header)

        # App title
        app_title = Label(
            text=get_text('app_name'),
            font_size='28sp',
            size_hint=(1, 0.15),
            bold=True,
            color=(0.2, 0.6, 0.8, 1)
        )
        layout.add_widget(app_title)

        # Tagline
        tagline = Label(
            text=get_text('tagline'),
            font_size='14sp',
            size_hint=(1, 0.08),
            color=(0.5, 0.5, 0.5, 1)
        )
        layout.add_widget(tagline)

        # Feature buttons grid
        features_grid = GridLayout(cols=2, spacing=10, size_hint=(1, 0.6))

        # Period Tracker button
        period_btn = Button(
            text=get_text('navigation.period_tracker'),
            background_color=(0.8, 0.3, 0.5, 1),
            font_size='14sp'
        )
        period_btn.bind(on_press=lambda x: self.navigate_to('period_tracker'))
        features_grid.add_widget(period_btn)

        # Community button
        community_btn = Button(
            text=get_text('navigation.community'),
            background_color=(0.4, 0.6, 0.8, 1),
            font_size='14sp'
        )
        community_btn.bind(on_press=lambda x: self.navigate_to('community'))
        features_grid.add_widget(community_btn)

        # Meetups button
        meetups_btn = Button(
            text=get_text('navigation.meetups'),
            background_color=(0.5, 0.7, 0.4, 1),
            font_size='14sp'
        )
        meetups_btn.bind(on_press=lambda x: self.navigate_to('meetups'))
        features_grid.add_widget(meetups_btn)

        # Analytics button
        analytics_btn = Button(
            text=get_text('navigation.analytics'),
            background_color=(0.7, 0.5, 0.8, 1),
            font_size='14sp'
        )
        analytics_btn.bind(on_press=lambda x: self.navigate_to('analytics'))
        features_grid.add_widget(analytics_btn)

        # Chatbot button (full width)
        chatbot_btn = Button(
            text=get_text('navigation.chatbot'),
            background_color=(0.3, 0.7, 0.6, 1),
            font_size='14sp',
            size_hint=(1, None),
            height=60
        )
        chatbot_btn.bind(on_press=lambda x: self.navigate_to('chatbot'))

        layout.add_widget(features_grid)
        layout.add_widget(chatbot_btn)

        # Logout button
        logout_btn = Button(
            text=get_text('settings.logout'),
            size_hint=(1, 0.08),
            background_color=(0.8, 0.3, 0.3, 1),
            font_size='12sp'
        )
        logout_btn.bind(on_press=self.on_logout)
        layout.add_widget(logout_btn)

        self.add_widget(layout)

    def navigate_to(self, screen_name):
        """Navigate to a different screen"""
        app = App.get_running_app()
        app.change_screen(screen_name)

    def on_logout(self, instance):
        """Handle logout"""
        app = App.get_running_app()
        app.logout()

    def on_enter(self):
        """Called when entering this screen"""
        # Refresh UI with current language
        self.clear_widgets()
        self.build_ui()
