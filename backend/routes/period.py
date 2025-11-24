"""
Period tracker routes for Sakhi App
"""

from fastapi import APIRouter, HTTPException
from typing import List
from models import PeriodLogCreate, PeriodLog, MessageResponse, CycleAnalytics
from database import db
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/log", response_model=MessageResponse)
async def create_period_log(user_id: int, log: PeriodLogCreate):
    """Create a new period log entry"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''INSERT INTO period_logs (user_id, start_date, end_date, flow_level, symptoms, notes)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, log.start_date, log.end_date, log.flow_level, log.symptoms, log.notes)
        )
        conn.commit()
        log_id = cursor.lastrowid
        conn.close()

        return MessageResponse(message=f"Period log created with ID: {log_id}")

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/{user_id}")
async def get_period_logs(user_id: int):
    """Get all period logs for a user"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT * FROM period_logs WHERE user_id = ? ORDER BY start_date DESC',
        (user_id,)
    )
    logs = cursor.fetchall()
    conn.close()

    return [dict(log) for log in logs]

@router.get("/analytics/{user_id}", response_model=CycleAnalytics)
async def get_cycle_analytics(user_id: int):
    """Get cycle analytics for a user"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''SELECT start_date, end_date FROM period_logs
           WHERE user_id = ? ORDER BY start_date DESC LIMIT 10''',
        (user_id,)
    )
    logs = cursor.fetchall()
    conn.close()

    if not logs:
        return CycleAnalytics(
            average_cycle_length=28,
            last_period_date=None,
            next_period_estimate=None,
            regularity="unknown",
            total_logs=0
        )

    # Calculate average cycle length
    cycle_lengths = []
    for i in range(len(logs) - 1):
        current = datetime.strptime(logs[i]['start_date'], '%Y-%m-%d')
        next_log = datetime.strptime(logs[i + 1]['start_date'], '%Y-%m-%d')
        cycle_length = (current - next_log).days
        if cycle_length > 0:
            cycle_lengths.append(cycle_length)

    avg_cycle = sum(cycle_lengths) // len(cycle_lengths) if cycle_lengths else 28

    # Determine regularity (if cycle varies by more than 7 days, irregular)
    regularity = "regular"
    if cycle_lengths:
        max_variation = max(cycle_lengths) - min(cycle_lengths)
        if max_variation > 7:
            regularity = "irregular"

    # Last period and prediction
    last_period = datetime.strptime(logs[0]['start_date'], '%Y-%m-%d').date()
    next_period = last_period + timedelta(days=avg_cycle)

    return CycleAnalytics(
        average_cycle_length=avg_cycle,
        last_period_date=last_period,
        next_period_estimate=next_period,
        regularity=regularity,
        total_logs=len(logs)
    )

@router.delete("/log/{log_id}")
async def delete_period_log(log_id: int, user_id: int):
    """Delete a period log"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM period_logs WHERE id = ? AND user_id = ?', (log_id, user_id))
    conn.commit()
    conn.close()

    return MessageResponse(message="Period log deleted successfully")
