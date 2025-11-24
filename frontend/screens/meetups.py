"""
Meetups Screen for Sakhi App
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.app import App
import sys
import os
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from localization import get_text

API_BASE_URL = "http://localhost:8000"

class MeetupsScreen(Screen):
    """Meetups screen"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        """Build the meetups UI"""
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
            text=get_text('meetups.title'),
            font_size='20sp',
            size_hint=(0.7, 1),
            bold=True
        )
        header.add_widget(title)

        layout.add_widget(header)

        # Create meetup button
        create_btn = Button(
            text=get_text('meetups.create_meetup'),
            size_hint=(1, 0.1),
            background_color = (1.0, 0.0, 0.4, 1),
            font_size='16sp'
        )
        create_btn.bind(on_press=self.create_meetup)
        layout.add_widget(create_btn)

        # Meetups list
        meetups_label = Label(
            text=get_text('meetups.upcoming'),
            font_size='18sp',
            size_hint=(1, 0.06),
            bold=True
        )
        layout.add_widget(meetups_label)

        # Scrollable meetups
        scroll = ScrollView(size_hint=(1, 0.76))
        self.meetups_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=5)
        self.meetups_layout.bind(minimum_height=self.meetups_layout.setter('height'))

        # Load meetups from backend
        self.load_meetups()

        scroll.add_widget(self.meetups_layout)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def create_meetup_card(self, meetup):
        """Create a meetup card widget with minimal information"""
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=160,
            padding=10,
            spacing=5
        )

        # Title
        title_label = Label(
            text=meetup['title'],
            font_size='16sp',
            size_hint=(1, None),
            height=30,
            bold=True,
            text_size=(320, None),
            halign='left'
        )
        card.add_widget(title_label)

        # Minimal details - meetup type, language, date and time
        details = f"Type: {meetup.get('meetup_type', 'In-Person')}\n"
        if meetup.get('language'):
            details += f"Languages: {meetup['language']}\n"
        if meetup.get('date') and meetup.get('time'):
            details += f"When: {meetup['date']} at {meetup['time']}"

        details_label = Label(
            text=details,
            font_size='13sp',
            size_hint=(1, None),
            height=60,
            text_size=(320, None),
            halign='left',
            valign='top',
            color=(0.5, 0.5, 0.5, 1)
        )
        card.add_widget(details_label)

        # More Info and Star buttons row
        info_star_row = BoxLayout(size_hint=(1, None), height=35, spacing=5)

        more_info_btn = Button(
            text="More Info",
            size_hint=(0.7, 1),
            background_color=(0.4, 0.6, 0.8, 1)
        )
        more_info_btn.bind(on_press=lambda x: self.show_meetup_details(meetup))
        info_star_row.add_widget(more_info_btn)

        # Thumbs up button
        app = App.get_running_app()
        user_id = app.get_user_id()
        likes_count = meetup.get('stars', 0)
        user_liked = meetup.get('user_starred', False)

        if user_liked:
            like_btn = Button(
                text=f"^ {likes_count}",
                size_hint=(0.3, 1),
                background_color=(0.3, 0.7, 0.4, 1),
                disabled=True
            )
        else:
            like_btn = Button(
                text=f"^ {likes_count}",
                size_hint=(0.3, 1),
                background_color=(0.6, 0.8, 0.6, 1)
            )
            if meetup.get('id'):
                like_btn.bind(on_press=lambda x: self.star_meetup(meetup.get('id')))

        info_star_row.add_widget(like_btn)
        card.add_widget(info_star_row)

        # Check if current user is the creator
        is_creator = (meetup.get('created_by') == user_id) if meetup.get('id') else False

        if is_creator:
            # Show Edit/Delete buttons for creator
            creator_actions = BoxLayout(size_hint=(1, None), height=35, spacing=5)

            edit_btn = Button(
                text="Edit",
                background_color=(0.8, 0.6, 0.2, 1)
            )
            edit_btn.bind(on_press=lambda x: self.edit_meetup(meetup))
            creator_actions.add_widget(edit_btn)

            delete_btn = Button(
                text="Delete",
                background_color=(0.9, 0.3, 0.3, 1)
            )
            delete_btn.bind(on_press=lambda x: self.delete_meetup(meetup.get('id'), meetup['title']))
            creator_actions.add_widget(delete_btn)

            card.add_widget(creator_actions)
        else:
            # Show Join button for non-creators
            user_joined = meetup.get('user_joined', False)

            if user_joined:
                # Show "Joined" button (disabled)
                join_btn = Button(
                    text="✓ Joined",
                    size_hint=(1, None),
                    height=35,
                    background_color=(0.5, 0.5, 0.5, 1),
                    disabled=True
                )
            else:
                # Show "Join" button (enabled)
                join_btn = Button(
                    text=get_text('meetups.join'),
                    size_hint=(1, None),
                    height=35,
                    background_color=(0.3, 0.7, 0.4, 1)
                )
                join_btn.bind(on_press=lambda x: self.join_meetup(meetup.get('id'), meetup['title']))

            card.add_widget(join_btn)

        return card

    def load_meetups(self):
        """Load meetups from backend"""
        self.meetups_layout.clear_widgets()

        # Get app instance
        app = App.get_running_app()
        user_id = app.get_user_id()

        # Sample meetups (always show)
        sample_meetups = [
            {
                'id': None,
                'title': 'PCOS Support Group',
                'date': '2025-12-01',
                'time': '18:00',
                'city': 'Bangalore',
                'description': 'Monthly support group for women with PCOS',
                'participants': 12
            },
            {
                'id': None,
                'title': "Women's Health Workshop",
                'date': '2025-12-05',
                'time': '16:00',
                'city': 'Delhi',
                'description': 'Learn about menstrual health and wellness',
                'participants': 8
            }
        ]

        # Try to fetch real meetups from backend
        try:
            response = requests.get(
                f"{API_BASE_URL}/meetups/list",
                params={"user_id": user_id} if user_id else {},
                timeout=3
            )

            if response.status_code == 200:
                real_meetups = response.json()
                # Add real meetups first
                for meetup in real_meetups:
                    card = self.create_meetup_card(meetup)
                    self.meetups_layout.add_widget(card)
        except Exception as e:
            print(f"Could not fetch meetups from backend: {e}")

        # Always add sample meetups
        for meetup in sample_meetups:
            card = self.create_meetup_card(meetup)
            self.meetups_layout.add_widget(card)

    def create_meetup(self, instance):
        """Open create meetup dialog"""
        # Create scrollable content for the form
        scroll = ScrollView(size_hint=(1, 1))
        form_content = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        form_content.bind(minimum_height=form_content.setter('height'))

        # Title input
        form_content.add_widget(Label(text=get_text('meetups.title_placeholder'), size_hint_y=None, height=30))
        title_input = TextInput(
            hint_text=get_text('meetups.title_placeholder'),
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_content.add_widget(title_input)

        # Description input
        form_content.add_widget(Label(text=get_text('meetups.description'), size_hint_y=None, height=30))
        desc_input = TextInput(
            hint_text=get_text('meetups.desc_placeholder'),
            multiline=True,
            size_hint_y=None,
            height=60
        )
        form_content.add_widget(desc_input)

        # Meetup Type
        form_content.add_widget(Label(text='Meetup Type', size_hint_y=None, height=30))
        type_spinner = Spinner(
            text='In-Person',
            values=('In-Person', 'Virtual'),
            size_hint_y=None,
            height=40
        )
        form_content.add_widget(type_spinner)

        # Location/Link input (dynamic based on type)
        location_label = Label(text='Location/Address', size_hint_y=None, height=30)
        form_content.add_widget(location_label)
        location_input = TextInput(
            hint_text='Enter meeting address',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_content.add_widget(location_input)

        # Update hint text and city state when type changes
        def on_type_change(spinner, text):
            if text == 'Virtual':
                location_label.text = 'Meeting Link'
                location_input.hint_text = 'Enter meeting link (Zoom, Meet, etc.)'
                city_input.disabled = True
                city_input.hint_text = 'Not required for virtual meetups'
                city_input.text = ''
            else:
                location_label.text = 'Location/Address'
                location_input.hint_text = 'Enter meeting address'
                city_input.disabled = False
                city_input.hint_text = 'Enter city name'

        type_spinner.bind(text=on_type_change)

        # City input
        form_content.add_widget(Label(text=get_text('meetups.city'), size_hint_y=None, height=30))
        city_input = TextInput(
            hint_text='Enter city name',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_content.add_widget(city_input)

        # Languages (multiple selection with checkboxes)
        form_content.add_widget(Label(text='Languages (select all that apply)', size_hint_y=None, height=30))

        language_checkboxes = {}
        languages = ['English', 'Hindi', 'Tamil', 'Kannada', 'Multilingual']

        for lang in languages:
            lang_box = BoxLayout(size_hint_y=None, height=35)
            checkbox = CheckBox(size_hint=(None, 1), width=40)
            lang_label = Label(text=lang, size_hint=(0.8, 1), halign='left')
            lang_box.add_widget(checkbox)
            lang_box.add_widget(lang_label)
            form_content.add_widget(lang_box)
            language_checkboxes[lang] = checkbox

        # Date input
        form_content.add_widget(Label(text='Date (YYYY-MM-DD)', size_hint_y=None, height=30))
        date_input = TextInput(
            hint_text='2025-12-01',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_content.add_widget(date_input)

        # Time input
        form_content.add_widget(Label(text='Time (HH:MM)', size_hint_y=None, height=30))
        time_input = TextInput(
            hint_text='18:00',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_content.add_widget(time_input)

        scroll.add_widget(form_content)

        # Main container with buttons
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(scroll)

        # Buttons at bottom
        btn_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)

        cancel_btn = Button(
            text=get_text('common.cancel'),
            background_color=(0.5, 0.5, 0.5, 1)
        )

        create_btn = Button(
            text=get_text('common.submit'),
            background_color = (1.0, 0.0, 0.4, 1)
        )

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(create_btn)
        content.add_widget(btn_layout)

        # Create popup
        popup = Popup(
            title=get_text('meetups.create_meetup'),
            content=content,
            size_hint=(0.9, 0.9)
        )

        # Button actions
        cancel_btn.bind(on_press=popup.dismiss)

        def on_submit(instance):
            # Collect selected languages
            selected_langs = [lang for lang, cb in language_checkboxes.items() if cb.active]
            languages_str = ', '.join(selected_langs) if selected_langs else 'English'

            self.submit_meetup(
                popup,
                title_input.text,
                desc_input.text,
                city_input.text,
                date_input.text,
                time_input.text,
                type_spinner.text,
                location_input.text,
                languages_str
            )

        create_btn.bind(on_press=on_submit)

        popup.open()

    def submit_meetup(self, popup, title, description, city, date, time, meetup_type, location, language):
        """Submit new meetup to backend"""
        # Validate inputs - city not required for virtual meetups
        if not title or not date or not time or not location:
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please fill all required fields (Title, Date, Time, Location/Link)"),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()
            return

        if meetup_type == 'In-Person' and not city:
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="City is required for in-person meetups"),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()
            return

        # Get app instance
        app = App.get_running_app()
        user_id = app.get_user_id()

        if not user_id:
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please login first"),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()
            return

        # Call backend API
        try:
            response = requests.post(
                f"{API_BASE_URL}/meetups/create",
                params={"user_id": user_id},
                json={
                    "title": title,
                    "description": description,
                    "city": city,
                    "date": date,
                    "time": time,
                    "meetup_type": meetup_type,
                    "location": location,
                    "language": language
                },
                timeout=5
            )

            if response.status_code == 200:
                # Close create dialog
                popup.dismiss()

                # Reload meetups
                self.load_meetups()

                # Show success message
                success_popup = Popup(
                    title=get_text('common.success'),
                    content=Label(text="Meetup created successfully!"),
                    size_hint=(0.8, 0.3)
                )
                success_popup.open()
            else:
                raise Exception(f"API returned {response.status_code}")

        except Exception as e:
            print(f"Error creating meetup: {e}")
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Could not create meetup. Make sure backend is running."),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()

    def show_meetup_details(self, meetup):
        """Show full meetup details in a popup"""
        # Create content layout
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Scroll view for details
        scroll = ScrollView(size_hint=(1, 0.9))
        details_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=[5, 10, 5, 10])
        details_layout.bind(minimum_height=details_layout.setter('height'))

        # Title
        title_label = Label(
            text=f"Title: {meetup['title']}",
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=40
        )
        title_label.bind(size=lambda *x: setattr(title_label, 'text_size', (title_label.width - 10, None)))
        details_layout.add_widget(title_label)

        # Description
        if meetup.get('description'):
            desc_label = Label(
                text=f"Description: {meetup['description']}",
                font_size='14sp',
                size_hint_y=None,
                height=60,
                valign='top'
            )
            desc_label.bind(size=lambda *x: setattr(desc_label, 'text_size', (desc_label.width - 10, None)))
            details_layout.add_widget(desc_label)

        # Meetup Type
        type_label = Label(
            text=f"Type: {meetup.get('meetup_type', 'In-Person')}",
            font_size='14sp',
            size_hint_y=None,
            height=30
        )
        type_label.bind(size=lambda *x: setattr(type_label, 'text_size', (type_label.width - 10, None)))
        details_layout.add_widget(type_label)

        # Location/Link
        if meetup.get('location'):
            loc_label_text = "Link" if meetup.get('meetup_type') == 'Virtual' else "Location"
            loc_label = Label(
                text=f"{loc_label_text}: {meetup['location']}",
                font_size='14sp',
                size_hint_y=None,
                height=50,
                valign='top'
            )
            loc_label.bind(size=lambda *x: setattr(loc_label, 'text_size', (loc_label.width - 10, None)))
            details_layout.add_widget(loc_label)

        # City (only for in-person)
        if meetup.get('city') and meetup.get('meetup_type') != 'Virtual':
            city_label = Label(
                text=f"{get_text('meetups.city')}: {meetup['city']}",
                font_size='14sp',
                size_hint_y=None,
                height=30
            )
            city_label.bind(size=lambda *x: setattr(city_label, 'text_size', (city_label.width - 10, None)))
            details_layout.add_widget(city_label)

        # Languages
        if meetup.get('language'):
            lang_label = Label(
                text=f"Languages: {meetup['language']}",
                font_size='14sp',
                size_hint_y=None,
                height=30
            )
            lang_label.bind(size=lambda *x: setattr(lang_label, 'text_size', (lang_label.width - 10, None)))
            details_layout.add_widget(lang_label)

        # Date and Time
        datetime_label = Label(
            text=f"{get_text('meetups.date_time')}: {meetup['date']} {meetup['time']}",
            font_size='14sp',
            size_hint_y=None,
            height=30
        )
        datetime_label.bind(size=lambda *x: setattr(datetime_label, 'text_size', (datetime_label.width - 10, None)))
        details_layout.add_widget(datetime_label)

        # Participants
        participant_count = meetup.get('participants_count', meetup.get('participants', 0))
        participant_label = Label(
            text=f"{get_text('meetups.participants')}: {participant_count}",
            font_size='14sp',
            size_hint_y=None,
            height=30
        )
        participant_label.bind(size=lambda *x: setattr(participant_label, 'text_size', (participant_label.width - 10, None)))
        details_layout.add_widget(participant_label)

        scroll.add_widget(details_layout)
        content.add_widget(scroll)

        # Close button
        close_btn = Button(
            text="Close",
            size_hint=(1, 0.1),
            background_color=(0.5, 0.5, 0.5, 1)
        )
        content.add_widget(close_btn)

        # Create popup
        popup = Popup(
            title="Meetup Details",
            content=content,
            size_hint=(0.9, 0.8)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

    def edit_meetup(self, meetup):
        """Open edit meetup dialog"""
        # Create scrollable content for the form
        scroll = ScrollView(size_hint=(1, 1))
        form_content = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        form_content.bind(minimum_height=form_content.setter('height'))

        # Title input
        form_content.add_widget(Label(text=get_text('meetups.title_placeholder'), size_hint_y=None, height=30))
        title_input = TextInput(
            text=str(meetup.get('title', '')),
            hint_text=get_text('meetups.title_placeholder'),
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_content.add_widget(title_input)

        # Description input
        form_content.add_widget(Label(text=get_text('meetups.description'), size_hint_y=None, height=30))
        desc_input = TextInput(
            text=str(meetup.get('description') or ''),
            hint_text=get_text('meetups.desc_placeholder'),
            multiline=True,
            size_hint_y=None,
            height=60
        )
        form_content.add_widget(desc_input)

        # Meetup Type
        form_content.add_widget(Label(text='Meetup Type', size_hint_y=None, height=30))
        type_spinner = Spinner(
            text=str(meetup.get('meetup_type', 'In-Person')),
            values=('In-Person', 'Virtual'),
            size_hint_y=None,
            height=40
        )
        form_content.add_widget(type_spinner)

        # Location/Link input
        location_label = Label(
            text='Meeting Link' if meetup.get('meetup_type') == 'Virtual' else 'Location/Address',
            size_hint_y=None,
            height=30
        )
        form_content.add_widget(location_label)
        location_input = TextInput(
            text=str(meetup.get('location') or ''),
            hint_text='Enter meeting link' if meetup.get('meetup_type') == 'Virtual' else 'Enter meeting address',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_content.add_widget(location_input)

        # City input
        form_content.add_widget(Label(text=get_text('meetups.city'), size_hint_y=None, height=30))
        city_input = TextInput(
            text=str(meetup.get('city') or ''),
            hint_text='Enter city name',
            multiline=False,
            size_hint_y=None,
            height=40,
            disabled=(meetup.get('meetup_type') == 'Virtual')
        )
        form_content.add_widget(city_input)

        # Update hint text and city state when type changes
        def on_type_change(spinner, text):
            if text == 'Virtual':
                location_label.text = 'Meeting Link'
                location_input.hint_text = 'Enter meeting link (Zoom, Meet, etc.)'
                city_input.disabled = True
                city_input.hint_text = 'Not required for virtual meetups'
            else:
                location_label.text = 'Location/Address'
                location_input.hint_text = 'Enter meeting address'
                city_input.disabled = False
                city_input.hint_text = 'Enter city name'

        type_spinner.bind(text=on_type_change)

        # Languages (multiple selection with checkboxes)
        form_content.add_widget(Label(text='Languages (select all that apply)', size_hint_y=None, height=30))

        language_checkboxes = {}
        languages = ['English', 'Hindi', 'Tamil', 'Kannada', 'Multilingual']
        existing_langs = [lang.strip() for lang in meetup.get('language', 'English').split(',')]

        for lang in languages:
            lang_box = BoxLayout(size_hint_y=None, height=35)
            checkbox = CheckBox(size_hint=(None, 1), width=40, active=(lang in existing_langs))
            lang_label = Label(text=lang, size_hint=(0.8, 1), halign='left')
            lang_box.add_widget(checkbox)
            lang_box.add_widget(lang_label)
            form_content.add_widget(lang_box)
            language_checkboxes[lang] = checkbox

        # Date input
        form_content.add_widget(Label(text='Date (YYYY-MM-DD)', size_hint_y=None, height=30))
        date_input = TextInput(
            text=str(meetup['date']),
            hint_text='2025-12-01',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_content.add_widget(date_input)

        # Time input
        form_content.add_widget(Label(text='Time (HH:MM)', size_hint_y=None, height=30))
        time_input = TextInput(
            text=meetup['time'],
            hint_text='18:00',
            multiline=False,
            size_hint_y=None,
            height=40
        )
        form_content.add_widget(time_input)

        scroll.add_widget(form_content)

        # Main container with buttons
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(scroll)

        # Buttons at bottom
        btn_layout = BoxLayout(size_hint=(1, None), height=50, spacing=10)

        cancel_btn = Button(
            text=get_text('common.cancel'),
            background_color=(0.5, 0.5, 0.5, 1)
        )

        update_btn = Button(
            text="Update",
            background_color = (1.0, 0.0, 0.4, 1)
        )

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(update_btn)
        content.add_widget(btn_layout)

        # Create popup
        popup = Popup(
            title="Edit Meetup",
            content=content,
            size_hint=(0.9, 0.9)
        )

        # Button actions
        cancel_btn.bind(on_press=popup.dismiss)

        def on_update(instance):
            # Collect selected languages
            selected_langs = [lang for lang, cb in language_checkboxes.items() if cb.active]
            languages_str = ', '.join(selected_langs) if selected_langs else 'English'

            self.update_meetup(
                popup,
                meetup.get('id'),
                title_input.text,
                desc_input.text,
                city_input.text,
                date_input.text,
                time_input.text,
                type_spinner.text,
                location_input.text,
                languages_str
            )

        update_btn.bind(on_press=on_update)
        popup.open()

    def update_meetup(self, popup, meetup_id, title, description, city, date, time, meetup_type, location, language):
        """Update an existing meetup"""
        # Validate inputs
        if not title or not date or not time or not location:
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please fill all required fields (Title, Date, Time, Location/Link)"),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()
            return

        if meetup_type == 'In-Person' and not city:
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="City is required for in-person meetups"),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()
            return

        # Get app instance
        app = App.get_running_app()
        user_id = app.get_user_id()

        if not user_id:
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please login first"),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()
            return

        # Call backend API
        try:
            response = requests.put(
                f"{API_BASE_URL}/meetups/{meetup_id}",
                params={"user_id": user_id},
                json={
                    "title": title,
                    "description": description,
                    "city": city,
                    "date": date,
                    "time": time,
                    "meetup_type": meetup_type,
                    "location": location,
                    "language": language
                },
                timeout=5
            )

            if response.status_code == 200:
                # Close edit dialog
                popup.dismiss()

                # Reload meetups
                self.load_meetups()

                # Show success message
                success_popup = Popup(
                    title=get_text('common.success'),
                    content=Label(text="Meetup updated successfully!"),
                    size_hint=(0.8, 0.3)
                )
                success_popup.open()
            else:
                raise Exception(f"API returned {response.status_code}")

        except Exception as e:
            print(f"Error updating meetup: {e}")
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Could not update meetup. Make sure backend is running."),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()

    def delete_meetup(self, meetup_id, title):
        """Delete a meetup with confirmation"""
        # Create confirmation dialog
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        content.add_widget(Label(
            text=f"Are you sure you want to delete:\n\"{title}\"?",
            size_hint=(1, 0.7)
        ))

        btn_layout = BoxLayout(size_hint=(1, 0.3), spacing=10)

        cancel_btn = Button(
            text=get_text('common.cancel'),
            background_color=(0.5, 0.5, 0.5, 1)
        )

        confirm_btn = Button(
            text="Delete",
            background_color=(0.9, 0.3, 0.3, 1)
        )

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        content.add_widget(btn_layout)

        popup = Popup(
            title="Confirm Delete",
            content=content,
            size_hint=(0.8, 0.4)
        )

        cancel_btn.bind(on_press=popup.dismiss)

        def on_confirm(instance):
            popup.dismiss()
            self.perform_delete(meetup_id, title)

        confirm_btn.bind(on_press=on_confirm)
        popup.open()

    def perform_delete(self, meetup_id, title):
        """Perform the actual deletion"""
        # Get app instance
        app = App.get_running_app()
        user_id = app.get_user_id()

        if not user_id:
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please login first"),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()
            return

        # If no meetup_id (sample meetup), can't delete
        if not meetup_id:
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Cannot delete sample meetups"),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()
            return

        # Call backend API to delete
        try:
            response = requests.delete(
                f"{API_BASE_URL}/meetups/{meetup_id}",
                params={"user_id": user_id},
                timeout=5
            )

            if response.status_code == 200:
                # Reload meetups
                self.load_meetups()

                success_popup = Popup(
                    title=get_text('common.success'),
                    content=Label(text=f"Deleted: {title}"),
                    size_hint=(0.8, 0.3)
                )
                success_popup.open()
            else:
                raise Exception(f"API returned {response.status_code}")

        except Exception as e:
            print(f"Error deleting meetup: {e}")
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Could not delete meetup"),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()

    def join_meetup(self, meetup_id, title):
        """Join a meetup"""
        # Get app instance
        app = App.get_running_app()
        user_id = app.get_user_id()

        if not user_id:
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please login first"),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return

        # If no meetup_id (sample meetup), just show success
        if not meetup_id:
            popup = Popup(
                title=get_text('common.success'),
                content=Label(text=f"Joined: {title}"),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return

        # Call backend API to join
        try:
            response = requests.post(
                f"{API_BASE_URL}/meetups/{meetup_id}/join",
                params={"user_id": user_id},
                timeout=5
            )

            if response.status_code == 200:
                # Reload meetups to update participant count and button state
                self.load_meetups()

                popup = Popup(
                    title=get_text('common.success'),
                    content=Label(text=f"Joined: {title}"),
                    size_hint=(0.8, 0.3)
                )
                popup.open()
            elif response.status_code == 400:
                # Already joined
                popup = Popup(
                    title=get_text('common.error'),
                    content=Label(text="You have already joined this meetup"),
                    size_hint=(0.8, 0.3)
                )
                popup.open()
                # Reload to update button state
                self.load_meetups()
            else:
                raise Exception(f"API returned {response.status_code}")

        except Exception as e:
            print(f"Error joining meetup: {e}")
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Could not join meetup"),
                size_hint=(0.8, 0.3)
            )
            popup.open()

    def star_meetup(self, meetup_id):
        """Star a meetup"""
        # Get app instance
        app = App.get_running_app()
        user_id = app.get_user_id()

        if not user_id:
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please login to star meetups"),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return

        # Call backend API to star
        try:
            response = requests.post(
                f"{API_BASE_URL}/meetups/{meetup_id}/star",
                params={"user_id": user_id},
                timeout=5
            )

            if response.status_code == 200:
                # Reload meetups to update star count and button state
                self.load_meetups()

                popup = Popup(
                    title=get_text('common.success'),
                    content=Label(text="Meetup starred!"),
                    size_hint=(0.8, 0.3)
                )
                popup.open()
            elif response.status_code == 400:
                # Already starred
                popup = Popup(
                    title=get_text('common.error'),
                    content=Label(text="You have already starred this meetup"),
                    size_hint=(0.8, 0.3)
                )
                popup.open()
                # Reload to update button state
                self.load_meetups()
            else:
                raise Exception(f"API returned {response.status_code}")

        except Exception as e:
            print(f"Error starring meetup: {e}")
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Could not star meetup. Make sure backend is running."),
                size_hint=(0.8, 0.3)
            )
            popup.open()

    def go_back(self, instance):
        """Go back to home screen"""
        app = App.get_running_app()
        app.change_screen('home')

    def on_enter(self):
        """Refresh UI when entering screen"""
        self.clear_widgets()
        self.build_ui()
