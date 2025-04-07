from fastapi import APIRouter, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict
import pandas as pd
import numpy as np
from src.auth import get_current_user
from src.services.analysis import (
    calculate_trends,
    detect_anomalies,
    generate_health_score,
    get_reference_ranges
)

router = APIRouter()

@router.get("/trends/{parameter}")
async def get_parameter_trends(
    parameter: str,
    timeframe: str = "1y",
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: app.mongodb)
):
    try:
        # Get user's health records
        cursor = db.health_records.find({"user_id": current_user})
        records = await cursor.to_list(length=None)
        
        if not records:
            return {"message": "No data available"}
        
        # Convert records to DataFrame
        df = pd.DataFrame(records)
        
        # Calculate trends
        trends = await calculate_trends(df, parameter, timeframe)
        
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/anomalies")
async def detect_parameter_anomalies(
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: app.mongodb)
):
    try:
        # Get user's health records
        cursor = db.health_records.find({"user_id": current_user})
        records = await cursor.to_list(length=None)
        
        if not records:
            return {"message": "No data available"}
        
        # Convert records to DataFrame
        df = pd.DataFrame(records)
        
        # Detect anomalies
        anomalies = await detect_anomalies(df)
        
        return anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health-score")
async def get_health_score(
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: app.mongodb)
):
    try:
        # Get user's health records
        cursor = db.health_records.find({"user_id": current_user})
        records = await cursor.to_list(length=None)
        
        if not records:
            return {"message": "No data available"}
        
        # Convert records to DataFrame
        df = pd.DataFrame(records)
        
        # Calculate health score
        score = await generate_health_score(df)
        
        return {"health_score": score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reference-ranges")
async def get_parameter_ranges():
    try:
        ranges = await get_reference_ranges()
        return ranges
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
