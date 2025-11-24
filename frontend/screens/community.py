"""
Community Screen for Sakhi App
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.app import App
import sys
import os
import requests
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from localization import get_text

API_BASE_URL = "http://localhost:8000"

class CommunityScreen(Screen):
    """Community forum screen"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        """Build the community UI"""
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
            text=get_text('community.title'),
            font_size='20sp',
            size_hint=(0.7, 1),
            bold=True
        )
        header.add_widget(title)

        layout.add_widget(header)

        # Create post section
        post_section = BoxLayout(orientation='vertical', size_hint=(1, 0.3), spacing=5)

        post_label = Label(
            text=get_text('community.create_post'),
            font_size='16sp',
            size_hint=(1, None),
            height=30
        )
        post_section.add_widget(post_label)

        self.post_input = TextInput(
            hint_text=get_text('community.post_placeholder'),
            multiline=True,
            size_hint=(1, 0.7)
        )
        post_section.add_widget(self.post_input)

        # Anonymous checkbox
        anon_layout = BoxLayout(size_hint=(1, None), height=40)
        self.anon_checkbox = CheckBox(size_hint=(None, 1), width=40)
        anon_label = Label(
            text=get_text('community.anonymous'),
            size_hint=(0.6, 1)
        )
        post_btn = Button(
            text=get_text('common.submit'),
            size_hint=(0.3, 1),
            background_color = (1.0, 0.0, 0.4, 1)
        )
        post_btn.bind(on_press=self.create_post)

        anon_layout.add_widget(self.anon_checkbox)
        anon_layout.add_widget(anon_label)
        anon_layout.add_widget(post_btn)

        post_section.add_widget(anon_layout)

        layout.add_widget(post_section)

        # Posts feed
        feed_label = Label(
            text=get_text('community.title'),
            font_size='18sp',
            size_hint=(1, 0.06),
            bold=True
        )
        layout.add_widget(feed_label)

        # Scrollable posts
        scroll = ScrollView(size_hint=(1, 0.56))
        self.posts_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=5)
        self.posts_layout.bind(minimum_height=self.posts_layout.setter('height'))

        # Load all posts (sample + real posts from backend)
        self.load_posts()

        scroll.add_widget(self.posts_layout)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def create_post_card(self, content, author, time, upvotes, post_id=None, creator_id=None):
        """Create a post card widget"""
        # Get current user
        app = App.get_running_app()
        current_user_id = app.get_user_id()
        is_creator = (creator_id == current_user_id) if creator_id and current_user_id else False

        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=140 if is_creator else 120,  # Taller if showing delete button
            padding=10,
            spacing=5
        )

        # Post content
        content_label = Label(
            text=content,
            size_hint=(1, 0.6),
            text_size=(320, None),
            halign='left',
            valign='top'
        )
        card.add_widget(content_label)

        # Post meta (author, time, upvotes)
        meta_layout = BoxLayout(size_hint=(1, 0.2))
        meta_layout.add_widget(Label(
            text=f"{get_text('community.posted_by')} {author} • {time}",
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            size_hint=(0.7, 1)
        ))

        upvote_btn = Button(
            text=f"↑ {upvotes}",
            size_hint=(0.3, 1),
            background_color=(0.3, 0.7, 0.4, 1)
        )
        # Bind upvote button if post_id is provided
        if post_id:
            upvote_btn.bind(on_press=lambda x: self.upvote_post(post_id))
        meta_layout.add_widget(upvote_btn)

        card.add_widget(meta_layout)

        # Actions (comment, reply)
        actions_layout = BoxLayout(size_hint=(1, 0.2))
        comment_btn = Button(
            text=get_text('community.comments'),
            size_hint=(0.5, 1),
            background_color=(0.4, 0.6, 0.8, 1)
        )
        # Bind comment button if post_id is provided
        if post_id:
            comment_btn.bind(on_press=lambda x: self.show_comments(post_id))

        reply_btn = Button(
            text=get_text('community.reply'),
            size_hint=(0.5, 1),
            background_color=(0.5, 0.5, 0.8, 1)
        )
        # Bind reply button if post_id is provided
        if post_id:
            reply_btn.bind(on_press=lambda x: self.reply_to_post(post_id))

        actions_layout.add_widget(comment_btn)
        actions_layout.add_widget(reply_btn)

        card.add_widget(actions_layout)

        # Add delete button if user is the creator
        if is_creator and post_id:
            delete_btn = Button(
                text="Delete Post",
                size_hint=(1, 0.15),
                background_color=(0.9, 0.3, 0.3, 1)
            )
            delete_btn.bind(on_press=lambda x: self.delete_post(post_id))
            card.add_widget(delete_btn)

        return card

    def load_posts(self):
        """Load posts from backend API and sample posts"""
        # Clear existing posts
        self.posts_layout.clear_widgets()

        # Get app instance
        app = App.get_running_app()
        user_lang = app.get_user_language() if app.user_language else 'en'

        # Sample posts (always show these)
        sample_posts = [
            {"content": "I've been experiencing irregular periods. Is this normal?",
             "author": "User1234", "time": "2h ago", "upvotes": 5},
            {"content": "Any tips for managing period pain naturally?",
             "author": "User5678", "time": "4h ago", "upvotes": 8},
            {"content": "PCOS support group - join us!",
             "author": "User9012", "time": "6h ago", "upvotes": 3}
        ]

        # Try to fetch real posts from backend
        try:
            response = requests.get(
                f"{API_BASE_URL}/community/posts",
                params={"user_lang": user_lang, "limit": 20},
                timeout=3
            )

            if response.status_code == 200:
                real_posts = response.json()
                # Add real posts first (newest first)
                for post in real_posts:
                    author = post.get('display_name', 'Anonymous')
                    created_at = post.get('created_at', '')
                    time_ago = self.get_time_ago(created_at)

                    post_card = self.create_post_card(
                        post['content'],
                        author,
                        time_ago,
                        post.get('upvotes', 0),
                        post_id=post.get('id'),
                        creator_id=post.get('user_id')
                    )
                    self.posts_layout.add_widget(post_card)
        except Exception as e:
            print(f"Could not fetch posts from backend: {e}")

        # Always add sample posts at the end
        for post in sample_posts:
            post_card = self.create_post_card(
                post['content'],
                post['author'],
                post['time'],
                post['upvotes']
            )
            self.posts_layout.add_widget(post_card)

    def get_time_ago(self, timestamp_str):
        """Convert timestamp to 'time ago' format"""
        try:
            # Remove timezone info and parse as naive datetime
            timestamp_str = timestamp_str.split('.')[0]  # Remove microseconds
            created = datetime.fromisoformat(timestamp_str)
            now = datetime.now()
            diff = now - created

            minutes = int(diff.total_seconds() / 60)
            if minutes < 1:
                return "just now"
            if minutes < 60:
                return f"{minutes}m ago"
            hours = int(minutes / 60)
            if hours < 24:
                return f"{hours}h ago"
            days = int(hours / 24)
            if days == 1:
                return "1 day ago"
            return f"{days} days ago"
        except Exception as e:
            print(f"Error parsing timestamp {timestamp_str}: {e}")
            return "just now"

    def create_post(self, instance):
        """Create a new post"""
        content = self.post_input.text.strip()
        if not content:
            return

        # Get app instance
        app = App.get_running_app()
        user_id = app.get_user_id()
        user_lang = app.get_user_language() if app.user_language else 'en'

        if not user_id:
            from kivy.uix.popup import Popup
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please login first"),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return

        # Call backend API to create post
        try:
            response = requests.post(
                f"{API_BASE_URL}/community/posts",
                params={"user_id": user_id},
                json={
                    "content": content,
                    "language": user_lang,
                    "anonymous": self.anon_checkbox.active
                },
                timeout=5
            )

            if response.status_code == 200:
                # Clear input
                self.post_input.text = ""
                self.anon_checkbox.active = False

                # Reload posts to show the new one
                self.load_posts()

                from kivy.uix.popup import Popup
                popup = Popup(
                    title=get_text('common.success'),
                    content=Label(text="Post created successfully!"),
                    size_hint=(0.8, 0.3)
                )
                popup.open()
            else:
                raise Exception(f"API returned {response.status_code}")

        except Exception as e:
            print(f"Error creating post: {e}")
            from kivy.uix.popup import Popup
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text=f"Could not create post. Make sure backend is running."),
                size_hint=(0.8, 0.3)
            )
            popup.open()

    def upvote_post(self, post_id):
        """Upvote a post"""
        app = App.get_running_app()
        user_id = app.get_user_id()

        if not user_id:
            from kivy.uix.popup import Popup
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please login to upvote"),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return

        try:
            response = requests.post(
                f"{API_BASE_URL}/community/posts/{post_id}/upvote",
                params={"user_id": user_id},
                timeout=5
            )

            if response.status_code == 200:
                # Reload posts to show updated upvote count
                self.load_posts()
                from kivy.uix.popup import Popup
                popup = Popup(
                    title=get_text('common.success'),
                    content=Label(text="Post upvoted!"),
                    size_hint=(0.8, 0.3)
                )
                popup.open()
            elif response.status_code == 400:
                from kivy.uix.popup import Popup
                popup = Popup(
                    title=get_text('common.error'),
                    content=Label(text="You already upvoted this post"),
                    size_hint=(0.8, 0.3)
                )
                popup.open()
            else:
                raise Exception(f"API returned {response.status_code}")

        except Exception as e:
            print(f"Error upvoting post: {e}")
            from kivy.uix.popup import Popup
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Could not upvote post"),
                size_hint=(0.8, 0.3)
            )
            popup.open()

    def show_comments(self, post_id):
        """Show comments for a post"""
        try:
            response = requests.get(
                f"{API_BASE_URL}/community/posts/{post_id}/comments",
                timeout=3
            )

            if response.status_code == 200:
                comments = response.json()
                comments_text = "\n\n".join([
                    f"{c.get('author_name', 'Anonymous')}: {c.get('content', '')}"
                    for c in comments
                ]) if comments else "No comments yet"

                from kivy.uix.popup import Popup
                popup = Popup(
                    title="Comments",
                    content=Label(text=comments_text, text_size=(280, None)),
                    size_hint=(0.9, 0.7)
                )
                popup.open()
            else:
                raise Exception(f"API returned {response.status_code}")

        except Exception as e:
            print(f"Error loading comments: {e}")
            from kivy.uix.popup import Popup
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Could not load comments"),
                size_hint=(0.8, 0.3)
            )
            popup.open()

    def reply_to_post(self, post_id):
        """Reply to a post (add a comment)"""
        app = App.get_running_app()
        user_id = app.get_user_id()
        user_lang = app.get_user_language() if app.user_language else 'en'

        if not user_id:
            from kivy.uix.popup import Popup
            popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please login to reply"),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return

        # Create reply input popup
        from kivy.uix.popup import Popup

        content_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        reply_input = TextInput(
            hint_text="Write your reply...",
            multiline=True,
            size_hint=(1, 0.7)
        )
        content_layout.add_widget(reply_input)

        def submit_reply(instance):
            reply_text = reply_input.text.strip()
            if not reply_text:
                return

            try:
                response = requests.post(
                    f"{API_BASE_URL}/community/posts/{post_id}/comments",
                    params={"user_id": user_id},
                    json={"content": reply_text, "language": user_lang},
                    timeout=5
                )

                if response.status_code == 200:
                    popup.dismiss()
                    from kivy.uix.popup import Popup
                    success_popup = Popup(
                        title=get_text('common.success'),
                        content=Label(text="Reply posted!"),
                        size_hint=(0.8, 0.3)
                    )
                    success_popup.open()
                else:
                    raise Exception(f"API returned {response.status_code}")

            except Exception as e:
                print(f"Error posting reply: {e}")
                from kivy.uix.popup import Popup
                error_popup = Popup(
                    title=get_text('common.error'),
                    content=Label(text="Could not post reply"),
                    size_hint=(0.8, 0.3)
                )
                error_popup.open()

        submit_btn = Button(
            text=get_text('common.submit'),
            size_hint=(1, 0.2),
            background_color=(1.0, 0.0, 0.4, 1)
        )
        submit_btn.bind(on_press=submit_reply)
        content_layout.add_widget(submit_btn)

        popup = Popup(
            title="Reply to Post",
            content=content_layout,
            size_hint=(0.9, 0.6)
        )
        popup.open()

    def delete_post(self, post_id):
        """Delete a post with confirmation"""
        # Create confirmation dialog
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)

        content.add_widget(Label(
            text="Are you sure you want to delete this post?",
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

        from kivy.uix.popup import Popup
        popup = Popup(
            title="Confirm Delete",
            content=content,
            size_hint=(0.8, 0.4)
        )

        cancel_btn.bind(on_press=popup.dismiss)

        def on_confirm(instance):
            popup.dismiss()
            self.perform_delete_post(post_id)

        confirm_btn.bind(on_press=on_confirm)
        popup.open()

    def perform_delete_post(self, post_id):
        """Perform the actual post deletion"""
        app = App.get_running_app()
        user_id = app.get_user_id()

        if not user_id:
            from kivy.uix.popup import Popup
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Please login first"),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()
            return

        # Call backend API to delete
        try:
            response = requests.delete(
                f"{API_BASE_URL}/community/posts/{post_id}",
                params={"user_id": user_id},
                timeout=5
            )

            if response.status_code == 200:
                # Reload posts to show updated list
                self.load_posts()

                from kivy.uix.popup import Popup
                success_popup = Popup(
                    title=get_text('common.success'),
                    content=Label(text="Post deleted successfully!"),
                    size_hint=(0.8, 0.3)
                )
                success_popup.open()
            else:
                raise Exception(f"API returned {response.status_code}")

        except Exception as e:
            print(f"Error deleting post: {e}")
            from kivy.uix.popup import Popup
            error_popup = Popup(
                title=get_text('common.error'),
                content=Label(text="Could not delete post. Make sure backend is running."),
                size_hint=(0.8, 0.3)
            )
            error_popup.open()

    def go_back(self, instance):
        """Go back to home screen"""
        app = App.get_running_app()
        app.change_screen('home')

    def on_enter(self):
        """Refresh UI when entering screen"""
        self.clear_widgets()
        self.build_ui()
