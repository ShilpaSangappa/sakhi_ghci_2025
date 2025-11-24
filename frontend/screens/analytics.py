"""
Menopause Analytics Screen for Sakhi App
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
import sys
import os
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from localization import get_text
from config import API_BASE_URL

class AnalyticsScreen(Screen):
    """Menopause analytics dashboard screen"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.analytics_data = None
        self.build_ui()

    def build_ui(self):
        """Build the menopause analytics UI"""
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
            text=get_text('analytics.title'),
            font_size='20sp',
            size_hint=(0.7, 1),
            bold=True
        )
        header.add_widget(title)

        layout.add_widget(header)

        # Fetch analytics data
        self.fetch_analytics_data()

        # Analytics cards
        scroll = ScrollView(size_hint=(1, 0.92))
        analytics_layout = GridLayout(cols=1, spacing=15, size_hint_y=None, padding=10)
        analytics_layout.bind(minimum_height=analytics_layout.setter('height'))

        if self.analytics_data:
            # Menopause stage card
            stage_display = self.analytics_data.get('menopause_stage', 'Unknown').replace('-', ' ').title()
            stage_card = self.create_stat_card(
                "Menopause Stage",
                stage_display,
                (0.8, 0.3, 0.6, 1)
            )
            analytics_layout.add_widget(stage_card)

            # Days since last period (key metric)
            if self.analytics_data.get('days_since_last_period'):
                days = self.analytics_data['days_since_last_period']
                days_card = self.create_stat_card(
                    "Days Since Last Period",
                    f"{days} days",
                    (0.6, 0.4, 0.8, 1)
                )
                analytics_layout.add_widget(days_card)

                # Countdown to menopause milestone
                if self.analytics_data.get('days_until_menopause_milestone'):
                    milestone_days = self.analytics_data['days_until_menopause_milestone']
                    milestone_card = self.create_stat_card(
                        "Days to Menopause (12 mo)",
                        f"{milestone_days} days",
                        (0.9, 0.6, 0.3, 1)
                    )
                    analytics_layout.add_widget(milestone_card)

            # Cycle variability (irregularity indicator)
            variability = self.analytics_data.get('cycle_variability', 0)
            variability_status = "Regular" if variability < 7 else "Irregular"
            variability_card = self.create_stat_card(
                "Cycle Regularity",
                f"{variability_status} (±{variability:.1f} days)",
                (0.3, 0.7, 0.4, 1) if variability < 7 else (0.9, 0.5, 0.3, 1)
            )
            analytics_layout.add_widget(variability_card)

            # Hot flashes per day
            hot_flashes = self.analytics_data.get('avg_hot_flashes_per_day', 0)
            if hot_flashes > 0:
                hot_flash_card = self.create_stat_card(
                    "Avg Hot Flashes/Day",
                    f"{hot_flashes:.1f}",
                    (0.9, 0.4, 0.3, 1)
                )
                analytics_layout.add_widget(hot_flash_card)

            # Overall symptom score
            symptom_score = self.analytics_data.get('overall_symptom_score', 0)
            if symptom_score > 0:
                symptom_card = self.create_stat_card(
                    "Overall Symptom Severity",
                    f"{symptom_score:.1f}/10",
                    (0.8, 0.5, 0.3, 1)
                )
                analytics_layout.add_widget(symptom_card)

            # Most common symptoms section
            if self.analytics_data.get('most_common_symptoms'):
                symptoms_header = Label(
                    text="Most Common Symptoms",
                    font_size='18sp',
                    size_hint_y=None,
                    height=40,
                    bold=True
                )
                analytics_layout.add_widget(symptoms_header)

                for symptom in self.analytics_data['most_common_symptoms'][:5]:
                    symptom_text = f"• {symptom['symptom']}: {symptom['avg_severity']:.1f}/10 ({symptom['frequency']} times)"
                    symptom_label = Label(
                        text=symptom_text,
                        size_hint_y=None,
                        height=40,
                        text_size=(320, None),
                        halign='left',
                        valign='middle'
                    )
                    analytics_layout.add_widget(symptom_label)

            # Insights section
            insights_label = Label(
                text="Health Insights",
                font_size='18sp',
                size_hint_y=None,
                height=40,
                bold=True
            )
            analytics_layout.add_widget(insights_label)

            # Generate insights
            insights = self.generate_insights()
            for insight in insights:
                insight_label = Label(
                    text=f"• {insight}",
                    size_hint_y=None,
                    height=60,
                    text_size=(320, None),
                    halign='left',
                    valign='middle'
                )
                analytics_layout.add_widget(insight_label)

            # Treatment effectiveness
            if self.analytics_data.get('active_treatments'):
                treatment_header = Label(
                    text="Active Treatments",
                    font_size='18sp',
                    size_hint_y=None,
                    height=40,
                    bold=True
                )
                analytics_layout.add_widget(treatment_header)

                for treatment in self.analytics_data['active_treatments']:
                    treatment_text = f"• {treatment['name']} ({treatment['type']})"
                    if treatment.get('effectiveness'):
                        treatment_text += f" - Effectiveness: {treatment['effectiveness']}/10"
                    treatment_label = Label(
                        text=treatment_text,
                        size_hint_y=None,
                        height=50,
                        text_size=(320, None),
                        halign='left',
                        valign='middle'
                    )
                    analytics_layout.add_widget(treatment_label)

            # Health risks
            risks_header = Label(
                text="Health Risk Assessment",
                font_size='18sp',
                size_hint_y=None,
                height=40,
                bold=True
            )
            analytics_layout.add_widget(risks_header)

            bone_risk = self.analytics_data.get('bone_health_risk', 'unknown').title()
            cardio_risk = self.analytics_data.get('cardiovascular_risk', 'unknown').title()

            risk_text = f"• Bone Health Risk: {bone_risk}\n• Cardiovascular Risk: {cardio_risk}"
            risk_label = Label(
                text=risk_text,
                size_hint_y=None,
                height=80,
                text_size=(320, None),
                halign='left',
                valign='middle'
            )
            analytics_layout.add_widget(risk_label)

        else:
            # Error or loading message
            error_label = Label(
                text="Unable to load analytics data.\nPlease ensure you are logged in.",
                size_hint_y=None,
                height=100,
                color=(1, 0.3, 0.3, 1)
            )
            analytics_layout.add_widget(error_label)

        scroll.add_widget(analytics_layout)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def fetch_analytics_data(self):
        """Fetch menopause analytics from API"""
        try:
            app = App.get_running_app()
            user_id = app.get_user_id()

            if not user_id:
                print("No user ID found")
                return

            response = requests.get(f"{API_BASE_URL}/menopause/analytics/{user_id}")
            if response.status_code == 200:
                self.analytics_data = response.json()
                print("Analytics data loaded successfully")
            else:
                print(f"Failed to fetch analytics: {response.status_code}")
        except Exception as e:
            print(f"Error fetching analytics data: {e}")

    def generate_insights(self):
        """Generate personalized insights based on analytics data"""
        insights = []

        if not self.analytics_data:
            return insights

        # Stage-specific insights
        stage = self.analytics_data.get('menopause_stage', '')

        if stage == 'early-perimenopause':
            insights.append("You're in early perimenopause. Your cycles are starting to vary - this is normal.")
            insights.append("Track your symptoms to identify patterns and triggers.")
        elif stage == 'late-perimenopause':
            insights.append("You're in late perimenopause. Longer gaps between periods are expected.")
            insights.append("Consider discussing treatment options with your doctor if symptoms are severe.")
        elif stage == 'menopause':
            days_until = self.analytics_data.get('days_until_menopause_milestone', 0)
            if days_until:
                insights.append(f"You're {days_until} days away from reaching the 12-month milestone for menopause.")
        elif stage == 'post-menopause':
            insights.append("You're in post-menopause. Focus on bone health and cardiovascular wellness.")

        # Symptom trend insights
        trend = self.analytics_data.get('symptom_trend', '')
        if trend == 'improving':
            insights.append("Your symptoms are improving over time - keep up your management strategies!")
        elif trend == 'worsening':
            insights.append("Your symptoms are worsening. Consider consulting your healthcare provider.")

        # Hot flash insights
        hot_flash_trend = self.analytics_data.get('hot_flash_trend', '')
        if hot_flash_trend == 'increasing':
            insights.append("Hot flashes are increasing. Try avoiding triggers like spicy foods, caffeine, and alcohol.")
        elif hot_flash_trend == 'decreasing':
            insights.append("Hot flashes are decreasing - your body is adjusting.")

        # Treatment insights
        if self.analytics_data.get('treatment_effectiveness'):
            eff = self.analytics_data['treatment_effectiveness']
            if eff >= 7:
                insights.append(f"Your treatments are highly effective (effectiveness: {eff:.1f}/10)")
            elif eff < 5:
                insights.append("Consider discussing alternative treatments with your doctor.")

        # Health risk insights
        bone_risk = self.analytics_data.get('bone_health_risk', '')
        if bone_risk in ['medium', 'high']:
            insights.append("Maintain bone health with calcium, vitamin D, and weight-bearing exercise.")

        return insights if insights else ["Continue tracking your symptoms for personalized insights."]

    def create_stat_card(self, title, value, color):
        """Create a statistics card"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=100,
            padding=15,
            spacing=10
        )

        # Card background (simulated with button)
        card_bg = Button(
            background_color=color,
            size_hint=(1, 1)
        )

        # Overlay layout for text
        overlay = BoxLayout(orientation='vertical')

        title_label = Label(
            text=title,
            font_size='14sp',
            size_hint=(1, 0.4),
            color=(1, 1, 1, 1)
        )
        overlay.add_widget(title_label)

        value_label = Label(
            text=value,
            font_size='24sp',
            size_hint=(1, 0.6),
            bold=True,
            color=(1, 1, 1, 1)
        )
        overlay.add_widget(value_label)

        # Create a layout to stack button and overlay
        stacked = BoxLayout()
        stacked.add_widget(card_bg)

        card.add_widget(overlay)

        return card

    def go_back(self, instance):
        """Go back to home screen"""
        app = App.get_running_app()
        app.change_screen('home')

    def on_enter(self):
        """Refresh UI when entering screen"""
        self.clear_widgets()
        self.build_ui()
