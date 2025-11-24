"""
Period Tracker Screen for Sakhi App
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
import sys
import os
import requests
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from localization import get_text

API_BASE_URL = "http://localhost:8000"

class PeriodTrackerScreen(Screen):
    """Period tracking screen"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        """Build the period tracker UI"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Header
        header = BoxLayout(size_hint=(1, 0.1), spacing=10)

        back_btn = Button(
            text=get_text('common.back'),
            size_hint=(0.3, 1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        back_btn.bind(on_press=self.go_back)
        header.add_widget(back_btn)

        title = Label(
            text=get_text('period_tracker.title'),
            font_size='20sp',
            size_hint=(0.7, 1),
            bold=True
        )
        header.add_widget(title)

        layout.add_widget(header)

        # Log period form
        form_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.6), spacing=10)

        # Start date
        form_layout.add_widget(Label(
            text=get_text('period_tracker.start_date'),
            size_hint=(1, None),
            height=30
        ))
        self.start_date_input = TextInput(
            hint_text='YYYY-MM-DD',
            multiline=False,
            size_hint=(1, None),
            height=40
        )
        form_layout.add_widget(self.start_date_input)

        # End date
        form_layout.add_widget(Label(
            text=get_text('period_tracker.end_date'),
            size_hint=(1, None),
            height=30
        ))
        self.end_date_input = TextInput(
            hint_text='YYYY-MM-DD',
            multiline=False,
            size_hint=(1, None),
            height=40
        )
        form_layout.add_widget(self.end_date_input)

        # Flow level
        form_layout.add_widget(Label(
            text=get_text('period_tracker.flow'),
            size_hint=(1, None),
            height=30
        ))
        self.flow_spinner = Spinner(
            text=get_text('period_tracker.flow_medium'),
            values=(
                get_text('period_tracker.flow_light'),
                get_text('period_tracker.flow_medium'),
                get_text('period_tracker.flow_heavy')
            ),
            size_hint=(1, None),
            height=40
        )
        form_layout.add_widget(self.flow_spinner)

        # Symptoms
        form_layout.add_widget(Label(
            text=get_text('period_tracker.symptoms'),
            size_hint=(1, None),
            height=30
        ))
        self.symptoms_input = TextInput(
            hint_text=get_text('period_tracker.symptoms'),
            multiline=True,
            size_hint=(1, None),
            height=60
        )
        form_layout.add_widget(self.symptoms_input)

        layout.add_widget(form_layout)

        # Save button
        save_btn = Button(
            text=get_text('common.save'),
            size_hint=(1, 0.1),
            background_color = (1.0, 0.0, 0.4, 1),
            font_size='16sp'
        )
        save_btn.bind(on_press=self.save_period_log)
        layout.add_widget(save_btn)

        # AI Insights button
        insights_btn = Button(
            text="📊 View AI Insights",
            size_hint=(1, 0.1),
            background_color=(0.4, 0.7, 0.9, 1),
            font_size='16sp'
        )
        insights_btn.bind(on_press=self.show_ai_insights)
        layout.add_widget(insights_btn)

        # History section
        history_label = Label(
            text=get_text('period_tracker.history'),
            font_size='18sp',
            size_hint=(1, 0.08),
            bold=True
        )
        layout.add_widget(history_label)

        # Scrollable history
        scroll = ScrollView(size_hint=(1, 0.12))
        self.history_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))

        # Load history from backend
        self.load_history()

        scroll.add_widget(self.history_layout)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def load_history(self):
        """Load period history from backend"""
        self.history_layout.clear_widgets()

        # Get app instance
        app = App.get_running_app()
        user_id = app.get_user_id()

        if not user_id:
            self.history_layout.add_widget(Label(
                text=get_text('period_tracker.login_to_see_history'),
                size_hint_y=None,
                height=40
            ))
            return

        try:
            # Fetch logs from backend
            response = requests.get(
                f"{API_BASE_URL}/period/logs/{user_id}",
                timeout=3
            )

            if response.status_code == 200:
                logs = response.json()

                # Fetch analytics first and show at top
                self.load_analytics(user_id)

                if not logs:
                    self.history_layout.add_widget(Label(
                        text=get_text('period_tracker.no_logs'),
                        size_hint_y=None,
                        height=40
                    ))
                else:
                    # Show last 3 logs
                    for log in logs[:3]:
                        log_text = f"{log['start_date']} to {log['end_date'] or 'ongoing'}"
                        self.history_layout.add_widget(Label(
                            text=log_text,
                            size_hint_y=None,
                            height=40
                        ))
            else:
                raise Exception("Failed to fetch logs")

        except Exception as e:
            print(f"Could not load history: {e}")
            self.history_layout.add_widget(Label(
                text=f"{get_text('period_tracker.next_period')}: Calculating...",
                size_hint_y=None,
                height=40
            ))

    def load_analytics(self, user_id):
        """Load cycle analytics"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/period/analytics/{user_id}",
                timeout=3
            )

            if response.status_code == 200:
                analytics = response.json()
                next_period = analytics.get('next_period_estimate', 'Unknown')

                self.history_layout.add_widget(Label(
                    text=f"{get_text('period_tracker.next_period')}: {next_period}",
                    size_hint_y=None,
                    height=40,
                    bold=True,
                    color=(0.8, 0.3, 0.5, 1)
                ))
        except Exception as e:
            print(f"Could not load analytics: {e}")

    def save_period_log(self, instance):
        """Save period log to backend"""
        start_date = self.start_date_input.text.strip()
        end_date = self.end_date_input.text.strip()
        symptoms = self.symptoms_input.text.strip()

        # Validate inputs
        if not start_date:
            from kivy.uix.popup import Popup
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please enter start date (YYYY-MM-DD)"),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return

        # Get app instance
        app = App.get_running_app()
        user_id = app.get_user_id()

        if not user_id:
            from kivy.uix.popup import Popup
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please login first"),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return

        # Map flow level to integer
        flow_text = self.flow_spinner.text
        flow_map = {
            get_text('period_tracker.flow_light'): 1,
            get_text('period_tracker.flow_medium'): 2,
            get_text('period_tracker.flow_heavy'): 3
        }
        flow_level = flow_map.get(flow_text, 2)

        # Call backend API
        try:
            response = requests.post(
                f"{API_BASE_URL}/period/log",
                params={"user_id": user_id},
                json={
                    "start_date": start_date,
                    "end_date": end_date if end_date else None,
                    "flow_level": flow_level,
                    "symptoms": symptoms,
                    "notes": None
                },
                timeout=5
            )

            if response.status_code == 200:
                # Clear inputs
                self.start_date_input.text = ""
                self.end_date_input.text = ""
                self.symptoms_input.text = ""

                # Reload history
                self.load_history()

                from kivy.uix.popup import Popup
                popup = Popup(
                    title=get_text('common.success'),
                    content=Label(text="Period log saved successfully!"),
                    size_hint=(0.8, 0.3)
                )
                popup.open()
            else:
                raise Exception(f"API returned {response.status_code}")

        except Exception as e:
            print(f"Error saving period log: {e}")
            from kivy.uix.popup import Popup
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Could not save log. Make sure backend is running."),
                size_hint=(0.8, 0.3)
            )
            popup.open()

    def show_ai_insights(self, instance):
        """Display AI-powered insights in a popup"""
        from kivy.uix.popup import Popup

        # Get app instance
        app = App.get_running_app()
        user_id = app.get_user_id()

        if not user_id:
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please login to view insights"),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return

        # Fetch AI insights from backend
        try:
            response = requests.get(
                f"{API_BASE_URL}/analytics/period/{user_id}",
                timeout=10  # Longer timeout for AI processing
            )

            if response.status_code == 200:
                insights_data = response.json()
                self.display_insights_popup(insights_data)
            else:
                raise Exception(f"API returned {response.status_code}")

        except Exception as e:
            print(f"Error loading AI insights: {e}")
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Could not load AI insights. Make sure backend is running."),
                size_hint=(0.8, 0.3)
            )
            popup.open()

    def display_insights_popup(self, insights_data):
        """Display insights in a scrollable popup"""
        from kivy.uix.popup import Popup

        # Create scrollable content
        scroll = ScrollView(size_hint=(1, 1))
        content_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=[10, 10, 10, 10])
        content_layout.bind(minimum_height=content_layout.setter('height'))

        # Title
        ai_badge = "🤖 AI-Powered" if insights_data.get('ai_powered', False) else "📊 Basic"
        title_label = Label(
            text=f"{ai_badge} Health Insights",
            font_size='18sp',
            bold=True,
            size_hint_y=None,
            height=40
        )
        content_layout.add_widget(title_label)

        # Cycle Statistics
        if insights_data.get('cycle_stats'):
            stats = insights_data['cycle_stats']

            stats_header = Label(
                text="📈 Cycle Statistics",
                font_size='16sp',
                bold=True,
                size_hint_y=None,
                height=35,
                color=(0.4, 0.7, 0.9, 1)
            )
            content_layout.add_widget(stats_header)

            stats_text = f"Average Cycle: {stats.get('avg_cycle_length', 'N/A')} days\n"
            stats_text += f"Regularity: {stats.get('regularity', 'N/A')}\n"
            stats_text += f"Period Duration: {stats.get('avg_period_duration', 'N/A')} days\n"
            stats_text += f"Cycles Tracked: {stats.get('total_cycles_tracked', 0)}"

            stats_label = Label(
                text=stats_text,
                size_hint_y=None,
                height=100,
                text_size=(300, None),
                halign='left',
                valign='top'
            )
            stats_label.bind(size=lambda *x: setattr(stats_label, 'text_size', (stats_label.width - 20, None)))
            content_layout.add_widget(stats_label)

        # Next Period Prediction
        if insights_data.get('next_period_prediction'):
            pred = insights_data['next_period_prediction']

            pred_header = Label(
                text="🗓️ Next Period Prediction",
                font_size='16sp',
                bold=True,
                size_hint_y=None,
                height=35,
                color=(0.8, 0.3, 0.5, 1)
            )
            content_layout.add_widget(pred_header)

            pred_text = f"Estimated Date: {pred.get('estimated_date', 'Unknown')}\n"
            pred_text += f"Confidence: {pred.get('confidence', 'N/A')}\n"
            if pred.get('reasoning'):
                pred_text += f"Why: {pred['reasoning']}"

            pred_label = Label(
                text=pred_text,
                size_hint_y=None,
                height=80,
                text_size=(300, None),
                halign='left',
                valign='top'
            )
            pred_label.bind(size=lambda *x: setattr(pred_label, 'text_size', (pred_label.width - 20, None)))
            content_layout.add_widget(pred_label)

        # Key Insights
        if insights_data.get('insights'):
            insights_header = Label(
                text="💡 Key Insights",
                font_size='16sp',
                bold=True,
                size_hint_y=None,
                height=35,
                color=(0.3, 0.7, 0.4, 1)
            )
            content_layout.add_widget(insights_header)

            for insight in insights_data['insights']:
                insight_label = Label(
                    text=f"• {insight}",
                    size_hint_y=None,
                    height=60,
                    text_size=(300, None),
                    halign='left',
                    valign='top'
                )
                insight_label.bind(size=lambda *x: setattr(insight_label, 'text_size', (insight_label.width - 20, None)))
                content_layout.add_widget(insight_label)

        # Recommendations
        if insights_data.get('recommendations'):
            rec_header = Label(
                text="✨ Recommendations",
                font_size='16sp',
                bold=True,
                size_hint_y=None,
                height=35,
                color=(0.9, 0.6, 0.2, 1)
            )
            content_layout.add_widget(rec_header)

            for rec in insights_data['recommendations']:
                rec_label = Label(
                    text=f"• {rec}",
                    size_hint_y=None,
                    height=60,
                    text_size=(300, None),
                    halign='left',
                    valign='top'
                )
                rec_label.bind(size=lambda *x: setattr(rec_label, 'text_size', (rec_label.width - 20, None)))
                content_layout.add_widget(rec_label)

        # Health Flags (if any)
        if insights_data.get('health_flags'):
            flags_header = Label(
                text="⚠️ Health Notes",
                font_size='16sp',
                bold=True,
                size_hint_y=None,
                height=35,
                color=(0.9, 0.4, 0.3, 1)
            )
            content_layout.add_widget(flags_header)

            for flag in insights_data['health_flags']:
                flag_label = Label(
                    text=f"• {flag}",
                    size_hint_y=None,
                    height=60,
                    text_size=(300, None),
                    halign='left',
                    valign='top',
                    color=(0.9, 0.4, 0.3, 1)
                )
                flag_label.bind(size=lambda *x: setattr(flag_label, 'text_size', (flag_label.width - 20, None)))
                content_layout.add_widget(flag_label)

        # Lifestyle Tips
        if insights_data.get('lifestyle_tips'):
            tips_header = Label(
                text="🌟 Lifestyle Tips",
                font_size='16sp',
                bold=True,
                size_hint_y=None,
                height=35,
                color=(0.6, 0.5, 0.8, 1)
            )
            content_layout.add_widget(tips_header)

            for tip in insights_data['lifestyle_tips']:
                tip_label = Label(
                    text=f"• {tip}",
                    size_hint_y=None,
                    height=50,
                    text_size=(300, None),
                    halign='left',
                    valign='top'
                )
                tip_label.bind(size=lambda *x: setattr(tip_label, 'text_size', (tip_label.width - 20, None)))
                content_layout.add_widget(tip_label)

        scroll.add_widget(content_layout)

        # Create popup with close button
        main_layout = BoxLayout(orientation='vertical', spacing=10)
        main_layout.add_widget(scroll)

        close_btn = Button(
            text="Close",
            size_hint=(1, None),
            height=50,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        main_layout.add_widget(close_btn)

        popup = Popup(
            title="Health Analytics",
            content=main_layout,
            size_hint=(0.95, 0.9)
        )

        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def go_back(self, instance):
        """Go back to home screen"""
        app = App.get_running_app()
        app.change_screen('home')

    def on_enter(self):
        """Refresh UI when entering screen"""
        self.clear_widgets()
        self.build_ui()
