"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime

# User models
class UserCreate(BaseModel):
    phone: Optional[str] = None
    name: str
    language_pref: str = 'en'
    city: Optional[str] = None
    anonymous: bool = False

class User(BaseModel):
    id: int
    phone: Optional[str]
    name: str
    language_pref: str
    city: Optional[str]
    anonymous: bool
    created_at: datetime

# Period tracker models
class PeriodLogCreate(BaseModel):
    start_date: date
    end_date: Optional[date] = None
    flow_level: int  # 1=Light, 2=Medium, 3=Heavy
    symptoms: Optional[str] = None
    notes: Optional[str] = None

class PeriodLog(BaseModel):
    id: int
    user_id: int
    start_date: date
    end_date: Optional[date]
    flow_level: int
    symptoms: Optional[str]
    notes: Optional[str]
    created_at: datetime

# Community models
class PostCreate(BaseModel):
    content: str
    language: str = 'en'
    anonymous: bool = False

class Post(BaseModel):
    id: int
    user_id: int
    content: str
    language: str
    anonymous_name: Optional[str]
    upvotes: int
    created_at: datetime
    translated: bool = False

class CommentCreate(BaseModel):
    content: str
    language: str = 'en'

class Comment(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    language: str
    created_at: datetime

# Meetup models
class MeetupCreate(BaseModel):
    title: str
    description: Optional[str] = None
    city: str
    date: date
    time: str
    meetup_type: str = 'In-Person'  # 'In-Person' or 'Virtual'
    location: Optional[str] = None  # Address for in-person or link for virtual
    language: str = 'English'  # Language of the meetup

class Meetup(BaseModel):
    id: int
    title: str
    description: Optional[str]
    city: str
    date: date
    time: str
    meetup_type: str = 'In-Person'
    location: Optional[str]
    language: str = 'English'
    created_by: int
    participants_count: int = 0
    user_joined: bool = False
    created_at: datetime

# Chatbot models
class ChatRequest(BaseModel):
    question: str
    language: str = 'en'

class ChatResponse(BaseModel):
    answer: str
    language: str
    translated: bool = False
    ai_powered: bool = False

# Analytics models
class CycleAnalytics(BaseModel):
    average_cycle_length: int
    last_period_date: Optional[date]
    next_period_estimate: Optional[date]
    regularity: str  # "regular" or "irregular"
    total_logs: int

# Menopause models
class MenopauseSymptomCreate(BaseModel):
    log_date: date
    hot_flashes: int = 0
    night_sweats: int = 0
    mood_changes: int = 0
    sleep_issues: int = 0
    joint_pain: int = 0
    brain_fog: int = 0
    vaginal_dryness: int = 0
    fatigue: int = 0
    weight_gain: float = 0.0
    anxiety: int = 0
    heart_palpitations: int = 0
    notes: Optional[str] = None

class MenopauseSymptom(BaseModel):
    id: int
    user_id: int
    log_date: date
    hot_flashes: int
    night_sweats: int
    mood_changes: int
    sleep_issues: int
    joint_pain: int
    brain_fog: int
    vaginal_dryness: int
    fatigue: int
    weight_gain: float
    anxiety: int
    heart_palpitations: int
    notes: Optional[str]
    created_at: datetime

class MenopauseTreatmentCreate(BaseModel):
    treatment_type: str  # "HRT", "Supplement", "Lifestyle", "Exercise", etc.
    treatment_name: str
    start_date: date
    end_date: Optional[date] = None
    dosage: Optional[str] = None
    effectiveness: Optional[int] = None  # 0-10 scale
    side_effects: Optional[str] = None
    notes: Optional[str] = None

class MenopauseTreatment(BaseModel):
    id: int
    user_id: int
    treatment_type: str
    treatment_name: str
    start_date: date
    end_date: Optional[date]
    dosage: Optional[str]
    effectiveness: Optional[int]
    side_effects: Optional[str]
    notes: Optional[str]
    created_at: datetime

class MenopauseAnalytics(BaseModel):
    # User profile
    age: Optional[int]
    menopause_stage: str

    # Cycle tracking
    days_since_last_period: Optional[int]
    cycle_variability: float  # Standard deviation of cycle lengths
    average_cycle_length: int
    longest_gap: Optional[int]  # Longest gap between periods

    # Symptom analytics
    total_symptom_logs: int
    most_common_symptoms: List[dict]  # [{symptom: name, avg_severity: float, frequency: int}]
    symptom_trend: str  # "improving", "worsening", "stable"
    overall_symptom_score: float  # 0-10 scale

    # Hot flash specific
    avg_hot_flashes_per_day: float
    hot_flash_trend: str  # "increasing", "decreasing", "stable"

    # Sleep & mood
    avg_sleep_quality: float  # Inverse of sleep_issues
    avg_mood_score: float

    # Treatment effectiveness
    active_treatments: List[dict]
    treatment_effectiveness: Optional[float]  # Average effectiveness if on treatment

    # Predictions & milestones
    estimated_menopause_date: Optional[date]
    days_until_menopause_milestone: Optional[int]  # Days until 12-month mark
    perimenopause_duration_months: Optional[int]

    # Health risks
    bone_health_risk: str  # "low", "medium", "high"
    cardiovascular_risk: str  # "low", "medium", "high"

# Response models
class MessageResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    error: str
    success: bool = False
