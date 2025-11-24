"""
Meetups routes for Sakhi App
"""

from fastapi import APIRouter, HTTPException
from typing import List
from models import MeetupCreate, Meetup, MessageResponse
from database import db

router = APIRouter()

@router.post("/create", response_model=MessageResponse)
async def create_meetup(user_id: int, meetup: MeetupCreate):
    """Create a new meetup"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''INSERT INTO meetups (title, description, city, date, time, meetup_type, location, language, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (meetup.title, meetup.description, meetup.city, meetup.date, meetup.time,
             meetup.meetup_type, meetup.location, meetup.language, user_id)
        )
        conn.commit()
        meetup_id = cursor.lastrowid
        conn.close()

        return MessageResponse(message=f"Meetup created with ID: {meetup_id}")

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def get_meetups(city: str = None, user_id: int = None):
    """Get all meetups, optionally filtered by city"""
    conn = db.get_connection()
    cursor = conn.cursor()

    if city:
        cursor.execute('SELECT * FROM meetups WHERE city = ? ORDER BY date ASC', (city,))
    else:
        cursor.execute('SELECT * FROM meetups ORDER BY date ASC')

    meetups = cursor.fetchall()

    # Get participant counts and check if user joined
    result = []
    for meetup in meetups:
        meetup_dict = dict(meetup)

        # Get participant count
        cursor.execute(
            'SELECT COUNT(*) as count FROM meetup_participants WHERE meetup_id = ?',
            (meetup_dict['id'],)
        )
        count = cursor.fetchone()['count']
        meetup_dict['participants_count'] = count

        # Check if user joined
        meetup_dict['user_joined'] = False
        if user_id:
            cursor.execute(
                'SELECT * FROM meetup_participants WHERE meetup_id = ? AND user_id = ?',
                (meetup_dict['id'], user_id)
            )
            if cursor.fetchone():
                meetup_dict['user_joined'] = True

        # Check if user starred
        meetup_dict['user_starred'] = False
        if user_id:
            cursor.execute(
                'SELECT * FROM meetup_stars WHERE meetup_id = ? AND user_id = ?',
                (meetup_dict['id'], user_id)
            )
            if cursor.fetchone():
                meetup_dict['user_starred'] = True

        result.append(meetup_dict)

    conn.close()
    return result

@router.get("/{meetup_id}")
async def get_meetup(meetup_id: int, user_id: int = None):
    """Get a specific meetup by ID"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM meetups WHERE id = ?', (meetup_id,))
    meetup = cursor.fetchone()

    if not meetup:
        conn.close()
        raise HTTPException(status_code=404, detail="Meetup not found")

    meetup_dict = dict(meetup)

    # Get participant count
    cursor.execute(
        'SELECT COUNT(*) as count FROM meetup_participants WHERE meetup_id = ?',
        (meetup_id,)
    )
    count = cursor.fetchone()['count']
    meetup_dict['participants_count'] = count

    # Check if user joined
    meetup_dict['user_joined'] = False
    if user_id:
        cursor.execute(
            'SELECT * FROM meetup_participants WHERE meetup_id = ? AND user_id = ?',
            (meetup_id, user_id)
        )
        if cursor.fetchone():
            meetup_dict['user_joined'] = True

    # Check if user starred
    meetup_dict['user_starred'] = False
    if user_id:
        cursor.execute(
            'SELECT * FROM meetup_stars WHERE meetup_id = ? AND user_id = ?',
            (meetup_id, user_id)
        )
        if cursor.fetchone():
            meetup_dict['user_starred'] = True

    conn.close()
    return meetup_dict

@router.post("/{meetup_id}/join")
async def join_meetup(meetup_id: int, user_id: int):
    """Join a meetup"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        # Check if already joined
        cursor.execute(
            'SELECT * FROM meetup_participants WHERE meetup_id = ? AND user_id = ?',
            (meetup_id, user_id)
        )
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Already joined this meetup")

        cursor.execute(
            'INSERT INTO meetup_participants (meetup_id, user_id) VALUES (?, ?)',
            (meetup_id, user_id)
        )
        conn.commit()
        conn.close()

        return MessageResponse(message="Successfully joined meetup")

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{meetup_id}/leave")
async def leave_meetup(meetup_id: int, user_id: int):
    """Leave a meetup"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'DELETE FROM meetup_participants WHERE meetup_id = ? AND user_id = ?',
        (meetup_id, user_id)
    )
    conn.commit()
    conn.close()

    return MessageResponse(message="Successfully left meetup")

@router.post("/{meetup_id}/star")
async def star_meetup(meetup_id: int, user_id: int):
    """Star a meetup"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        # Check if already starred
        cursor.execute(
            'SELECT * FROM meetup_stars WHERE meetup_id = ? AND user_id = ?',
            (meetup_id, user_id)
        )
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Already starred this meetup")

        # Add star
        cursor.execute(
            'INSERT INTO meetup_stars (meetup_id, user_id) VALUES (?, ?)',
            (meetup_id, user_id)
        )

        # Increment star count
        cursor.execute(
            'UPDATE meetups SET stars = stars + 1 WHERE id = ?',
            (meetup_id,)
        )

        conn.commit()
        conn.close()

        return MessageResponse(message="Meetup starred successfully")

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{meetup_id}", response_model=MessageResponse)
async def update_meetup(meetup_id: int, user_id: int, meetup: MeetupCreate):
    """Update a meetup (only creator can update)"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        # Verify user is the creator
        cursor.execute('SELECT created_by FROM meetups WHERE id = ?', (meetup_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            raise HTTPException(status_code=404, detail="Meetup not found")

        if result['created_by'] != user_id:
            conn.close()
            raise HTTPException(status_code=403, detail="Only creator can update this meetup")

        # Update the meetup
        cursor.execute(
            '''UPDATE meetups
               SET title = ?, description = ?, city = ?, date = ?, time = ?,
                   meetup_type = ?, location = ?, language = ?
               WHERE id = ? AND created_by = ?''',
            (meetup.title, meetup.description, meetup.city, meetup.date, meetup.time,
             meetup.meetup_type, meetup.location, meetup.language, meetup_id, user_id)
        )
        conn.commit()
        conn.close()

        return MessageResponse(message="Meetup updated successfully")

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{meetup_id}")
async def delete_meetup(meetup_id: int, user_id: int):
    """Delete a meetup (only creator can delete)"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        # Verify user is the creator before deleting
        cursor.execute('SELECT created_by FROM meetups WHERE id = ?', (meetup_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            raise HTTPException(status_code=404, detail="Meetup not found")

        if result['created_by'] != user_id:
            conn.close()
            raise HTTPException(status_code=403, detail="Only creator can delete this meetup")

        # Delete the meetup
        cursor.execute('DELETE FROM meetups WHERE id = ? AND created_by = ?', (meetup_id, user_id))
        conn.commit()
        conn.close()

        return MessageResponse(message="Meetup deleted successfully")

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
