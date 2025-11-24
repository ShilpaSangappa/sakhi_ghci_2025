"""
Authentication routes for Sakhi App
"""

from fastapi import APIRouter, HTTPException
from models import UserCreate, User, MessageResponse
from database import db

router = APIRouter()

@router.post("/register", response_model=MessageResponse)
async def register_user(user: UserCreate):
    """Register a new user or continue anonymously"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        if user.anonymous:
            # Anonymous user
            cursor.execute(
                'INSERT INTO users (name, language_pref, city, anonymous) VALUES (?, ?, ?, ?)',
                (user.name, user.language_pref, user.city, 1)
            )
            user_id = cursor.lastrowid
        else:
            # Check if phone already exists
            cursor.execute('SELECT id, name FROM users WHERE phone = ?', (user.phone,))
            existing_user = cursor.fetchone()

            if existing_user:
                # User already exists, return their ID
                conn.close()
                user_id = existing_user['id']
                return MessageResponse(message=f"User already registered with ID: {user_id}")

            # Create new user
            cursor.execute(
                'INSERT INTO users (phone, name, language_pref, city, anonymous) VALUES (?, ?, ?, ?, ?)',
                (user.phone, user.name, user.language_pref, user.city, 0)
            )
            user_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return MessageResponse(message=f"User registered successfully with ID: {user_id}")

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login_user(phone: str = None, name: str = None):
    """Login existing user by phone number"""
    conn = db.get_connection()
    cursor = conn.cursor()

    if not phone:
        conn.close()
        raise HTTPException(status_code=400, detail="Phone number is required")

    cursor.execute('SELECT * FROM users WHERE phone = ?', (phone,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="Mobile number not registered. Please sign up first.")

    user_dict = dict(user)
    return {
        "message": f"Login successful",
        "user_id": user_dict['id'],
        "name": user_dict['name'],
        "language_pref": user_dict['language_pref']
    }

@router.get("/user/{user_id}")
async def get_user(user_id: int):
    """Get user details by ID"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return dict(user)

@router.put("/user/{user_id}/language")
async def update_language(user_id: int, language: str):
    """Update user's language preference"""
    if language not in ['en', 'hi', 'ta', 'kn']:
        raise HTTPException(status_code=400, detail="Unsupported language")

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('UPDATE users SET language_pref = ? WHERE id = ?', (language, user_id))
    conn.commit()
    conn.close()

    return MessageResponse(message=f"Language updated to {language}")
