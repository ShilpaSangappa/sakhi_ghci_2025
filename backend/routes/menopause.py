"""
Menopause tracking and analytics routes for Sakhi App
"""

from fastapi import APIRouter, HTTPException
from typing import List
from models import (
    MenopauseSymptomCreate, MenopauseSymptom,
    MenopauseTreatmentCreate, MenopauseTreatment,
    MenopauseAnalytics, MessageResponse
)
from database import db
from datetime import datetime, timedelta
import statistics

router = APIRouter()

@router.post("/symptom/log", response_model=MessageResponse)
async def log_menopause_symptom(user_id: int, symptom: MenopauseSymptomCreate):
    """Log menopause symptoms for a specific date"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''INSERT INTO menopause_symptoms
            (user_id, log_date, hot_flashes, night_sweats, mood_changes, sleep_issues,
             joint_pain, brain_fog, vaginal_dryness, fatigue, weight_gain, anxiety, heart_palpitations, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, symptom.log_date, symptom.hot_flashes, symptom.night_sweats,
             symptom.mood_changes, symptom.sleep_issues, symptom.joint_pain,
             symptom.brain_fog, symptom.vaginal_dryness, symptom.fatigue,
             symptom.weight_gain, symptom.anxiety, symptom.heart_palpitations, symptom.notes)
        )
        conn.commit()
        log_id = cursor.lastrowid
        conn.close()

        return MessageResponse(message=f"Menopause symptom logged with ID: {log_id}")

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symptom/logs/{user_id}")
async def get_symptom_logs(user_id: int, limit: int = 30):
    """Get menopause symptom logs for a user"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''SELECT * FROM menopause_symptoms
           WHERE user_id = ? ORDER BY log_date DESC LIMIT ?''',
        (user_id, limit)
    )
    logs = cursor.fetchall()
    conn.close()

    return [dict(log) for log in logs]

@router.post("/treatment/add", response_model=MessageResponse)
async def add_treatment(user_id: int, treatment: MenopauseTreatmentCreate):
    """Add a menopause treatment"""
    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            '''INSERT INTO menopause_treatments
            (user_id, treatment_type, treatment_name, start_date, end_date, dosage, effectiveness, side_effects, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, treatment.treatment_type, treatment.treatment_name, treatment.start_date,
             treatment.end_date, treatment.dosage, treatment.effectiveness, treatment.side_effects, treatment.notes)
        )
        conn.commit()
        treatment_id = cursor.lastrowid
        conn.close()

        return MessageResponse(message=f"Treatment added with ID: {treatment_id}")

    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/treatment/list/{user_id}")
async def get_treatments(user_id: int):
    """Get all treatments for a user"""
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''SELECT * FROM menopause_treatments
           WHERE user_id = ? ORDER BY start_date DESC''',
        (user_id,)
    )
    treatments = cursor.fetchall()
    conn.close()

    return [dict(treatment) for treatment in treatments]

@router.get("/analytics/{user_id}", response_model=MenopauseAnalytics)
async def get_menopause_analytics(user_id: int):
    """Get comprehensive menopause analytics for a user"""
    conn = db.get_connection()
    cursor = conn.cursor()

    # Get user info
    cursor.execute('SELECT age, menopause_stage FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    age = user['age']
    menopause_stage = user['menopause_stage']

    # Get period logs
    cursor.execute(
        '''SELECT start_date FROM period_logs
           WHERE user_id = ? ORDER BY start_date DESC LIMIT 20''',
        (user_id,)
    )
    period_logs = cursor.fetchall()

    # Calculate cycle analytics
    days_since_last_period = None
    cycle_variability = 0.0
    average_cycle_length = 28
    longest_gap = None

    if period_logs:
        last_period = datetime.strptime(period_logs[0]['start_date'], '%Y-%m-%d')
        days_since_last_period = (datetime.now() - last_period).days

        # Calculate cycle lengths
        cycle_lengths = []
        for i in range(len(period_logs) - 1):
            current = datetime.strptime(period_logs[i]['start_date'], '%Y-%m-%d')
            next_period = datetime.strptime(period_logs[i + 1]['start_date'], '%Y-%m-%d')
            cycle_length = (current - next_period).days
            if cycle_length > 0:
                cycle_lengths.append(cycle_length)

        if cycle_lengths:
            average_cycle_length = int(sum(cycle_lengths) / len(cycle_lengths))
            cycle_variability = statistics.stdev(cycle_lengths) if len(cycle_lengths) > 1 else 0.0
            longest_gap = max(cycle_lengths)

    # Get symptom logs
    cursor.execute(
        '''SELECT * FROM menopause_symptoms
           WHERE user_id = ? ORDER BY log_date DESC LIMIT 90''',
        (user_id,)
    )
    symptom_logs = cursor.fetchall()
    total_symptom_logs = len(symptom_logs)

    # Calculate symptom analytics
    most_common_symptoms = []
    symptom_trend = "stable"
    overall_symptom_score = 0.0
    avg_hot_flashes_per_day = 0.0
    hot_flash_trend = "stable"
    avg_sleep_quality = 10.0
    avg_mood_score = 5.0

    if symptom_logs:
        # Calculate averages for each symptom
        symptom_fields = [
            'hot_flashes', 'night_sweats', 'mood_changes', 'sleep_issues',
            'joint_pain', 'brain_fog', 'vaginal_dryness', 'fatigue',
            'anxiety', 'heart_palpitations'
        ]

        symptom_data = {}
        for field in symptom_fields:
            values = [log[field] for log in symptom_logs if log[field] > 0]
            if values:
                avg = sum(values) / len(values)
                frequency = len(values)
                symptom_data[field] = {'avg_severity': avg, 'frequency': frequency}

        # Sort by frequency and get top symptoms
        most_common_symptoms = [
            {'symptom': k.replace('_', ' ').title(), 'avg_severity': round(v['avg_severity'], 1), 'frequency': v['frequency']}
            for k, v in sorted(symptom_data.items(), key=lambda x: x[1]['frequency'], reverse=True)[:5]
        ]

        # Calculate overall symptom score (average of all non-zero symptoms)
        all_symptom_values = []
        for log in symptom_logs:
            log_symptoms = [log[field] for field in symptom_fields if log[field] > 0]
            if log_symptoms:
                all_symptom_values.append(sum(log_symptoms) / len(log_symptoms))
        overall_symptom_score = sum(all_symptom_values) / len(all_symptom_values) if all_symptom_values else 0.0

        # Hot flash analytics
        hot_flash_counts = [log['hot_flashes'] for log in symptom_logs]
        avg_hot_flashes_per_day = sum(hot_flash_counts) / len(hot_flash_counts)

        # Trend analysis (compare first half vs second half)
        if len(symptom_logs) >= 10:
            mid = len(symptom_logs) // 2
            recent_avg = sum([log['hot_flashes'] for log in symptom_logs[:mid]]) / mid
            older_avg = sum([log['hot_flashes'] for log in symptom_logs[mid:]]) / (len(symptom_logs) - mid)

            if recent_avg > older_avg * 1.2:
                hot_flash_trend = "increasing"
            elif recent_avg < older_avg * 0.8:
                hot_flash_trend = "decreasing"

            # Overall symptom trend
            recent_symptom_avg = sum([
                sum([log[f] for f in symptom_fields]) / len(symptom_fields)
                for log in symptom_logs[:mid]
            ]) / mid
            older_symptom_avg = sum([
                sum([log[f] for f in symptom_fields]) / len(symptom_fields)
                for log in symptom_logs[mid:]
            ]) / (len(symptom_logs) - mid)

            if recent_symptom_avg > older_symptom_avg * 1.2:
                symptom_trend = "worsening"
            elif recent_symptom_avg < older_symptom_avg * 0.8:
                symptom_trend = "improving"

        # Sleep and mood
        sleep_values = [log['sleep_issues'] for log in symptom_logs if log['sleep_issues'] > 0]
        avg_sleep_quality = 10 - (sum(sleep_values) / len(sleep_values)) if sleep_values else 10.0

        mood_values = [log['mood_changes'] for log in symptom_logs if log['mood_changes'] > 0]
        avg_mood_score = 10 - (sum(mood_values) / len(mood_values)) if mood_values else 10.0

    # Get treatment data
    cursor.execute(
        '''SELECT * FROM menopause_treatments
           WHERE user_id = ? AND (end_date IS NULL OR end_date >= date('now'))
           ORDER BY start_date DESC''',
        (user_id,)
    )
    active_treatments_data = cursor.fetchall()
    conn.close()

    active_treatments = [
        {
            'type': t['treatment_type'],
            'name': t['treatment_name'],
            'effectiveness': t['effectiveness']
        }
        for t in active_treatments_data
    ]

    treatment_effectiveness = None
    if active_treatments_data:
        effectiveness_values = [t['effectiveness'] for t in active_treatments_data if t['effectiveness']]
        if effectiveness_values:
            treatment_effectiveness = sum(effectiveness_values) / len(effectiveness_values)

    # Calculate predictions and milestones
    estimated_menopause_date = None
    days_until_menopause_milestone = None
    perimenopause_duration_months = None

    if days_since_last_period:
        if days_since_last_period < 365:
            # Still in perimenopause, estimate when reaching 12-month mark
            days_until_menopause_milestone = 365 - days_since_last_period
            estimated_menopause_date = (datetime.now() + timedelta(days=days_until_menopause_milestone)).date()
        elif menopause_stage in ['early-perimenopause', 'late-perimenopause']:
            # In perimenopause but irregular - estimate based on age
            typical_menopause_age = 51
            if age:
                years_until = max(0, typical_menopause_age - age)
                estimated_menopause_date = (datetime.now() + timedelta(days=years_until * 365)).date()

    # Calculate perimenopause duration if applicable
    if menopause_stage in ['late-perimenopause', 'menopause', 'post-menopause'] and period_logs:
        # Estimate based on when cycles started becoming irregular
        if cycle_variability > 7:  # Irregular cycles
            perimenopause_duration_months = min(len(period_logs), 60)  # Cap at 5 years

    # Health risk assessment
    bone_health_risk = "low"
    cardiovascular_risk = "low"

    if age:
        if menopause_stage in ['menopause', 'post-menopause']:
            bone_health_risk = "medium"
            cardiovascular_risk = "medium"

            # Increase risk based on age
            if age >= 60:
                bone_health_risk = "high"
                cardiovascular_risk = "high"

            # Treatment reduces risk
            if active_treatments_data:
                hrt_treatments = [t for t in active_treatments_data if t['treatment_type'] == 'HRT']
                if hrt_treatments:
                    if bone_health_risk == "high":
                        bone_health_risk = "medium"
                    if cardiovascular_risk == "high":
                        cardiovascular_risk = "medium"

    return MenopauseAnalytics(
        age=age,
        menopause_stage=menopause_stage,
        days_since_last_period=days_since_last_period,
        cycle_variability=round(cycle_variability, 1),
        average_cycle_length=average_cycle_length,
        longest_gap=longest_gap,
        total_symptom_logs=total_symptom_logs,
        most_common_symptoms=most_common_symptoms,
        symptom_trend=symptom_trend,
        overall_symptom_score=round(overall_symptom_score, 1),
        avg_hot_flashes_per_day=round(avg_hot_flashes_per_day, 1),
        hot_flash_trend=hot_flash_trend,
        avg_sleep_quality=round(avg_sleep_quality, 1),
        avg_mood_score=round(avg_mood_score, 1),
        active_treatments=active_treatments,
        treatment_effectiveness=round(treatment_effectiveness, 1) if treatment_effectiveness else None,
        estimated_menopause_date=estimated_menopause_date,
        days_until_menopause_milestone=days_until_menopause_milestone,
        perimenopause_duration_months=perimenopause_duration_months,
        bone_health_risk=bone_health_risk,
        cardiovascular_risk=cardiovascular_risk
    )
