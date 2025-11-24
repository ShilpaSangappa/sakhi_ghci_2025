"""
Analytics routes for Sakhi App
Provides AI-powered health insights and predictions
"""

from fastapi import APIRouter, HTTPException
from models import MessageResponse
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.health_analytics import health_analytics

router = APIRouter()

@router.get("/period/{user_id}")
async def get_period_analytics(user_id: int):
    """
    Get AI-powered period analytics and predictions for a user
    Returns insights, predictions, recommendations, and cycle statistics
    """
    try:
        insights = await health_analytics.analyze_period_patterns(user_id)
        return insights

    except Exception as e:
        print(f"Error generating analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate analytics: {str(e)}"
        )

@router.get("/health-summary/{user_id}")
async def get_health_summary(user_id: int):
    """
    Get a summary of user's health tracking data
    Includes cycle count, tracking consistency, and basic stats
    """
    try:
        from database import db

        conn = db.get_connection()
        cursor = conn.cursor()

        # Get total cycles tracked
        cursor.execute(
            'SELECT COUNT(*) as count FROM period_logs WHERE user_id = ?',
            (user_id,)
        )
        result = cursor.fetchone()
        total_cycles = result['count'] if result else 0

        # Get most recent log
        cursor.execute(
            '''SELECT start_date, end_date FROM period_logs
               WHERE user_id = ?
               ORDER BY start_date DESC LIMIT 1''',
            (user_id,)
        )
        recent_log = cursor.fetchone()

        conn.close()

        return {
            "total_cycles_tracked": total_cycles,
            "last_period_date": recent_log['start_date'] if recent_log else None,
            "tracking_active": total_cycles > 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
