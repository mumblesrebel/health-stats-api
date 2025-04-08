from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os
import datetime

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
        print(f"Attempting to connect to MongoDB...")
        app.mongodb_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=5000
        )
        print(f"Client created, attempting to ping server...")
        await app.mongodb_client.admin.command('ping')
        print(f"Server ping successful, selecting database...")
        app.mongodb = app.mongodb_client[settings.MONGODB_NAME]
        server_info = await app.mongodb_client.server_info()
        print(f"Successfully connected to MongoDB version {server_info.get('version')}")
        print(f"Using database: {settings.MONGODB_NAME}")
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        if hasattr(e, 'details'):
            print(f"Error details: {e.details}")
        app.mongodb_client = None
        app.mongodb = None
        raise Exception(f"Failed to connect to MongoDB: {str(e)}")

@app.on_event("shutdown")
async def shutdown_db_client():
    if app.mongodb_client:
        app.mongodb_client.close()

@app.get("/health")
async def health_check():
    try:
        if app.mongodb_client:
            await app.mongodb_client.admin.command('ping')
            db_info = await app.mongodb_client.server_info()
            db_status = {
                "status": "healthy",
                "version": db_info.get('version'),
                "connection": "connected",
                "database": settings.MONGODB_NAME
            }
        else:
            db_status = {
                "status": "error",
                "connection": "not connected",
                "database": settings.MONGODB_NAME
            }
    except Exception as e:
        db_status = {
            "status": "error",
            "connection": "error",
            "message": str(e),
            "database": settings.MONGODB_NAME
        }
    
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.datetime.utcnow().isoformat(),
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
