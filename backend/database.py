"""
Database configuration and initialization for Sakhi App
Uses SQLite for local development and demo
"""

import sqlite3
from datetime import datetime, timedelta
import os
import random

class Database:
    def __init__(self, db_path="data/sakhi.db"):
        # Get project root directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(base_dir, db_path)

        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self.init_database()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn

    def init_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE,
                name TEXT,
                language_pref TEXT DEFAULT 'en',
                city TEXT,
                anonymous BOOLEAN DEFAULT 0,
                age INTEGER,
                menopause_stage TEXT CHECK(menopause_stage IN ('pre-menopause', 'early-perimenopause', 'late-perimenopause', 'menopause', 'post-menopause')) DEFAULT 'pre-menopause',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Add menopause columns if they don't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN age INTEGER")
        except:
            pass  # Column already exists

        try:
            cursor.execute("ALTER TABLE users ADD COLUMN menopause_stage TEXT CHECK(menopause_stage IN ('pre-menopause', 'early-perimenopause', 'late-perimenopause', 'menopause', 'post-menopause')) DEFAULT 'pre-menopause'")
        except:
            pass  # Column already exists

        # Period logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS period_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                flow_level INTEGER CHECK(flow_level IN (1, 2, 3)),
                symptoms TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Community posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                anonymous_name TEXT,
                upvotes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Meetups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                city TEXT NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                meetup_type TEXT DEFAULT 'In-Person',
                location TEXT,
                language TEXT DEFAULT 'English',
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        ''')

        # Add new columns if they don't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE meetups ADD COLUMN meetup_type TEXT DEFAULT 'In-Person'")
        except:
            pass  # Column already exists

        try:
            cursor.execute("ALTER TABLE meetups ADD COLUMN location TEXT")
        except:
            pass  # Column already exists

        try:
            cursor.execute("ALTER TABLE meetups ADD COLUMN language TEXT DEFAULT 'English'")
        except:
            pass  # Column already exists

        try:
            cursor.execute("ALTER TABLE meetups ADD COLUMN stars INTEGER DEFAULT 0")
        except:
            pass  # Column already exists

        # Meetup participants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetup_participants (
                meetup_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (meetup_id, user_id),
                FOREIGN KEY (meetup_id) REFERENCES meetups(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Post upvotes table (to track who upvoted what)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_upvotes (
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (post_id, user_id),
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Meetup stars table (to track who starred what)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meetup_stars (
                meetup_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (meetup_id, user_id),
                FOREIGN KEY (meetup_id) REFERENCES meetups(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Chat history table (for chatbot)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Menopause symptoms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menopause_symptoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                log_date DATE NOT NULL,
                hot_flashes INTEGER DEFAULT 0 CHECK(hot_flashes >= 0),
                night_sweats INTEGER DEFAULT 0 CHECK(night_sweats BETWEEN 0 AND 10),
                mood_changes INTEGER DEFAULT 0 CHECK(mood_changes BETWEEN 0 AND 10),
                sleep_issues INTEGER DEFAULT 0 CHECK(sleep_issues BETWEEN 0 AND 10),
                joint_pain INTEGER DEFAULT 0 CHECK(joint_pain BETWEEN 0 AND 10),
                brain_fog INTEGER DEFAULT 0 CHECK(brain_fog BETWEEN 0 AND 10),
                vaginal_dryness INTEGER DEFAULT 0 CHECK(vaginal_dryness BETWEEN 0 AND 10),
                fatigue INTEGER DEFAULT 0 CHECK(fatigue BETWEEN 0 AND 10),
                weight_gain REAL DEFAULT 0,
                anxiety INTEGER DEFAULT 0 CHECK(anxiety BETWEEN 0 AND 10),
                heart_palpitations INTEGER DEFAULT 0 CHECK(heart_palpitations BETWEEN 0 AND 10),
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Menopause treatments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menopause_treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                treatment_type TEXT NOT NULL,
                treatment_name TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                dosage TEXT,
                effectiveness INTEGER CHECK(effectiveness BETWEEN 0 AND 10),
                side_effects TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        conn.commit()
        conn.close()
        print(f"✓ Database initialized at {self.db_path}")

    def seed_sample_data(self):
        """Add sample data for demo purposes"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if data already exists
        cursor.execute('SELECT COUNT(*) FROM users')
        if cursor.fetchone()[0] > 0:
            print("Sample data already exists")
            conn.close()
            return

        # Add sample users with menopause data
        users = [
            ("9876543210", "Priya", "en", "Bangalore", 0, 46, "early-perimenopause"),
            ("9876543211", "Ananya", "hi", "Delhi", 0, 50, "late-perimenopause"),
            ("9876543212", "Lakshmi", "ta", "Chennai", 0, 52, "menopause"),
            ("9876543213", "Kavya", "kn", "Bangalore", 0, 54, "post-menopause"),
            ("9876543214", "Meera", "en", "Mumbai", 0, 42, "pre-menopause"),
        ]

        cursor.executemany(
            'INSERT INTO users (phone, name, language_pref, city, anonymous, age, menopause_stage) VALUES (?, ?, ?, ?, ?, ?, ?)',
            users
        )

        # Add sample posts (menopause-focused)
        posts = [
            (1, "I've been experiencing irregular periods and hot flashes. Is this perimenopause?", "en", None, 12),
            (2, "मुझे रात में पसीना आता है। क्या यह रजोनिवृत्ति का लक्षण है?", "hi", None, 15),
            (3, "மாதவிடாய் நின்ற பிறகு எலும்பு ஆரோக்கியத்தை எப்படி பராமரிக்கலாம்?", "ta", None, 8),
            (4, "ಮೆನೋಪಾಸ್ ಸಮಯದಲ್ಲಿ ತೂಕ ಹೆಚ್ಚಾಗುವುದು ಹೇಗೆ ನಿಯಂತ್ರಿಸುವುದು?", "kn", None, 10),
            (5, "Anyone else dealing with brain fog during perimenopause? Tips please!", "en", None, 18),
            (1, "HRT has been life-changing for me. Happy to answer questions!", "en", None, 22),
        ]

        cursor.executemany(
            'INSERT INTO posts (user_id, content, language, anonymous_name, upvotes) VALUES (?, ?, ?, ?, ?)',
            posts
        )

        # Add sample comments
        comments = [
            (1, 2, "Yes, these are classic perimenopause symptoms. Consult a gynecologist!", "en"),
            (2, 3, "मुझे भी यही लक्षण थे। योग और ठंडे पानी से स्नान मदद करता है।", "hi"),
            (5, 4, "I use a symptom tracking app and it helps me identify triggers", "en"),
            (6, 3, "What type of HRT are you on? I'm considering it too", "en"),
        ]

        cursor.executemany(
            'INSERT INTO comments (post_id, user_id, content, language) VALUES (?, ?, ?, ?)',
            comments
        )

        # Add sample meetups (menopause-focused)
        meetups = [
            ("Perimenopause Support Group", "Monthly meetup to share experiences and tips", "Bangalore", "2025-12-01", "18:00", 1),
            ("Menopause Wellness Workshop", "Learn about managing symptoms naturally", "Delhi", "2025-12-05", "16:00", 2),
            ("Post-Menopause Health Talk", "Bone health and heart health after menopause", "Chennai", "2025-12-10", "17:00", 4),
        ]

        cursor.executemany(
            'INSERT INTO meetups (title, description, city, date, time, created_by) VALUES (?, ?, ?, ?, ?, ?)',
            meetups
        )

        # Generate synthetic period logs and menopause symptoms for each user profile
        self._generate_menopause_data(cursor)

        conn.commit()
        conn.close()
        print("✓ Sample data added successfully")

    def _generate_menopause_data(self, cursor):
        """Generate realistic menopause tracking data for different user profiles"""
        base_date = datetime(2024, 11, 23)  # Start from one year ago

        # Profile 1: Priya (46) - Early Perimenopause
        # Cycles starting to vary (25-35 days), mild symptoms
        cycle_lengths = [28, 30, 27, 32, 29, 26, 35, 28, 31, 27, 33, 29]
        current_date = base_date - timedelta(days=365)
        for i, cycle_len in enumerate(cycle_lengths):
            period_duration = random.randint(4, 6)
            flow = random.choice([1, 2, 2, 3])
            symptoms = random.choice([
                "cramps,mood_swings",
                "headache,fatigue",
                "cramps,breast_tenderness",
                "mood_swings,bloating"
            ])
            cursor.execute(
                'INSERT INTO period_logs (user_id, start_date, end_date, flow_level, symptoms, notes) VALUES (?, ?, ?, ?, ?, ?)',
                (1, current_date.date(), (current_date + timedelta(days=period_duration)).date(), flow, symptoms, "")
            )
            current_date += timedelta(days=cycle_len)

            # Add menopause symptoms (mild, occasional)
            for j in range(cycle_len // 7):  # Weekly symptom logs
                symptom_date = current_date - timedelta(days=cycle_len) + timedelta(days=j*7)
                cursor.execute(
                    '''INSERT INTO menopause_symptoms
                    (user_id, log_date, hot_flashes, night_sweats, mood_changes, sleep_issues, joint_pain, brain_fog, fatigue, anxiety)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (1, symptom_date.date(), random.randint(0, 2), random.randint(0, 3),
                     random.randint(2, 5), random.randint(1, 4), random.randint(0, 3),
                     random.randint(1, 4), random.randint(2, 5), random.randint(1, 4))
                )

        # Profile 2: Ananya (50) - Late Perimenopause
        # Irregular cycles (30-60 days), skipping cycles, moderate-severe symptoms
        cycle_lengths = [32, 45, 28, 58, 35, 67, 42, 89, 38]  # Increasing gaps
        current_date = base_date - timedelta(days=365)
        for i, cycle_len in enumerate(cycle_lengths):
            period_duration = random.randint(3, 7)
            flow = random.choice([1, 1, 2, 3])  # More variable flow
            symptoms = random.choice([
                "cramps,mood_swings,hot_flashes",
                "headache,fatigue,night_sweats",
                "mood_swings,bloating,joint_pain",
                "fatigue,brain_fog,anxiety"
            ])
            cursor.execute(
                'INSERT INTO period_logs (user_id, start_date, end_date, flow_level, symptoms, notes) VALUES (?, ?, ?, ?, ?, ?)',
                (2, current_date.date(), (current_date + timedelta(days=period_duration)).date(), flow, symptoms, "Very irregular")
            )
            current_date += timedelta(days=cycle_len)

            # Add menopause symptoms (moderate-severe, frequent)
            for j in range(min(cycle_len // 3, 20)):  # More frequent logging
                symptom_date = current_date - timedelta(days=cycle_len) + timedelta(days=j*3)
                cursor.execute(
                    '''INSERT INTO menopause_symptoms
                    (user_id, log_date, hot_flashes, night_sweats, mood_changes, sleep_issues, joint_pain, brain_fog, vaginal_dryness, fatigue, anxiety, heart_palpitations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (2, symptom_date.date(), random.randint(5, 12), random.randint(4, 8),
                     random.randint(4, 8), random.randint(5, 9), random.randint(3, 7),
                     random.randint(4, 8), random.randint(3, 7), random.randint(5, 8),
                     random.randint(4, 7), random.randint(2, 6))
                )

        # Profile 3: Lakshmi (52) - Menopause (10 months since last period)
        # Last period 10 months ago, tracking countdown to 12 months
        last_period = base_date - timedelta(days=300)
        cursor.execute(
            'INSERT INTO period_logs (user_id, start_date, end_date, flow_level, symptoms, notes) VALUES (?, ?, ?, ?, ?, ?)',
            (3, (last_period - timedelta(days=45)).date(), (last_period - timedelta(days=40)).date(), 1, "light_flow", "Very light")
        )
        cursor.execute(
            'INSERT INTO period_logs (user_id, start_date, end_date, flow_level, symptoms, notes) VALUES (?, ?, ?, ?, ?, ?)',
            (3, last_period.date(), (last_period + timedelta(days=3)).date(), 1, "spotting", "Last period")
        )

        # Add menopause symptoms (high severity, gradually improving)
        for i in range(40):  # Weekly logs for 10 months
            symptom_date = last_period + timedelta(days=i*7)
            severity_modifier = max(0, 10 - (i // 10))  # Symptoms gradually improve
            cursor.execute(
                '''INSERT INTO menopause_symptoms
                (user_id, log_date, hot_flashes, night_sweats, mood_changes, sleep_issues, joint_pain, brain_fog, vaginal_dryness, fatigue, anxiety, weight_gain)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (3, symptom_date.date(), random.randint(8, 15), random.randint(6, 9),
                 random.randint(5, 8), random.randint(6, 9), random.randint(4, 8),
                 random.randint(5, 8), random.randint(6, 9), random.randint(5, 8),
                 random.randint(5, 8), random.uniform(2.0, 8.0))
            )

        # Add treatment tracking (HRT started 3 months ago)
        hrt_start = base_date - timedelta(days=90)
        cursor.execute(
            '''INSERT INTO menopause_treatments
            (user_id, treatment_type, treatment_name, start_date, dosage, effectiveness, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (3, "HRT", "Estradiol + Progesterone", hrt_start.date(), "1mg/100mg daily", 7, "Significant improvement in symptoms")
        )

        # Profile 4: Kavya (54) - Post-Menopause (2 years since last period)
        # No periods for 2 years, managing long-term health
        last_period = base_date - timedelta(days=730)
        cursor.execute(
            'INSERT INTO period_logs (user_id, start_date, end_date, flow_level, symptoms, notes) VALUES (?, ?, ?, ?, ?, ?)',
            (4, last_period.date(), (last_period + timedelta(days=3)).date(), 1, "spotting", "Final period")
        )

        # Add menopause symptoms (decreased but persistent)
        for i in range(24):  # Monthly logs for 2 years
            symptom_date = last_period + timedelta(days=i*30)
            # Symptoms decrease over time but some persist
            hot_flash_severity = max(0, 8 - (i // 3))
            cursor.execute(
                '''INSERT INTO menopause_symptoms
                (user_id, log_date, hot_flashes, night_sweats, mood_changes, sleep_issues, joint_pain, vaginal_dryness, fatigue, weight_gain)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (4, symptom_date.date(), hot_flash_severity, random.randint(0, 4),
                 random.randint(1, 4), random.randint(2, 5), random.randint(4, 7),
                 random.randint(5, 8), random.randint(2, 5), random.uniform(8.0, 12.0))
            )

        # Add treatments (supplements for bone health)
        cursor.execute(
            '''INSERT INTO menopause_treatments
            (user_id, treatment_type, treatment_name, start_date, dosage, effectiveness, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (4, "Supplement", "Calcium + Vitamin D", (base_date - timedelta(days=365)).date(), "1200mg Ca + 2000IU D3 daily", 8, "For bone health")
        )
        cursor.execute(
            '''INSERT INTO menopause_treatments
            (user_id, treatment_type, treatment_name, start_date, dosage, effectiveness, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (4, "Exercise", "Weight-bearing exercise", (base_date - timedelta(days=365)).date(), "3x per week", 7, "Helps with bone density and mood")
        )

        # Profile 5: Meera (42) - Pre-Menopause (Regular cycles as baseline)
        # Regular 28-day cycles, minimal symptoms
        cycle_lengths = [28, 29, 27, 28, 28, 29, 27, 28, 28, 27, 29, 28]
        current_date = base_date - timedelta(days=365)
        for i, cycle_len in enumerate(cycle_lengths):
            period_duration = random.randint(4, 5)
            flow = 2  # Regular medium flow
            symptoms = random.choice([
                "cramps",
                "cramps,mood_swings",
                "headache",
                "bloating"
            ])
            cursor.execute(
                'INSERT INTO period_logs (user_id, start_date, end_date, flow_level, symptoms, notes) VALUES (?, ?, ?, ?, ?, ?)',
                (5, current_date.date(), (current_date + timedelta(days=period_duration)).date(), flow, symptoms, "Regular cycle")
            )
            current_date += timedelta(days=cycle_len)

            # Minimal menopause symptoms (baseline)
            if i % 2 == 0:  # Less frequent logging
                cursor.execute(
                    '''INSERT INTO menopause_symptoms
                    (user_id, log_date, hot_flashes, night_sweats, mood_changes, sleep_issues, fatigue)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (5, current_date.date(), 0, 0, random.randint(1, 3), random.randint(1, 3), random.randint(1, 4))
                )

# Global database instance
db = Database()

if __name__ == "__main__":
    # Initialize and seed database
    print("Initializing database...")
    db.seed_sample_data()
    print("Database setup complete!")
