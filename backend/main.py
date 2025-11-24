"""
Main FastAPI application for Sakhi backend
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import db
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(
    title="Sakhi API",
    description="Women's Health Companion API",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    print("Starting Sakhi API...")
    db.seed_sample_data()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": "Sakhi - Your Health Companion",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": "/auth",
            "period_tracker": "/period",
            "community": "/community",
            "meetups": "/meetups",
            "chatbot": "/chat",
            "analytics": "/analytics",
            "menopause": "/menopause"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Import and include routers
from routes import auth, period, community, meetups, chatbot, analytics, menopause

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(period.router, prefix="/period", tags=["Period Tracker"])
app.include_router(community.router, prefix="/community", tags=["Community"])
app.include_router(meetups.router, prefix="/meetups", tags=["Meetups"])
app.include_router(chatbot.router, prefix="/chat", tags=["Chatbot"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(menopause.router, prefix="/menopause", tags=["Menopause"])

if __name__ == "__main__":
    import uvicorn
    print("Starting Sakhi API server...")
    print("Access API docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
