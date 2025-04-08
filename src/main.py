from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.routers import health_records, analysis
from src.config import settings
from src.auth import get_current_user

app = FastAPI(title="Health Stats Data Processor")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    try:
        app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
        await app.mongodb_client.admin.command('ping')
        app.mongodb = app.mongodb_client[settings.MONGODB_NAME]
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        app.mongodb_client = None
        app.mongodb = None

@app.on_event("shutdown")
async def shutdown_db_client():
    if app.mongodb_client:
        app.mongodb_client.close()

@app.get("/health")
async def health_check():
    try:
        if app.mongodb_client:
            await app.mongodb_client.admin.command('ping')
            db_status = "healthy"
        else:
            db_status = "not connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok",
        "database": db_status
    }

# Include routers
app.include_router(
    health_records.router,
    prefix="/api/health-records",
    tags=["health_records"]
)

app.include_router(
    analysis.router,
    prefix="/api/analysis",
    tags=["analysis"]
)

@app.get("/")
async def root():
    return {"message": "Health Stats Data Processor API"}
