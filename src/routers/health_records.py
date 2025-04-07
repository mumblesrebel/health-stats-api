from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
import pandas as pd
from src.auth import get_current_user
from src.models.health_record import HealthRecord
from src.services.data_processor import process_health_data

router = APIRouter()

@router.post("/upload")
async def upload_health_record(
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: app.mongodb)
):
    try:
        # Read file content
        contents = await file.read()
        
        # Process the file based on its type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(contents)
        elif file.filename.endswith('.xlsx'):
            df = pd.read_excel(contents)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Process the data
        processed_data = await process_health_data(df)
        
        # Create health record
        health_record = HealthRecord(
            user_id=current_user,
            file_name=file.filename,
            data=processed_data
        )
        
        # Save to database
        result = await db.health_records.insert_one(health_record.dict())
        
        return {"id": str(result.inserted_id)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/records", response_model=List[HealthRecord])
async def get_health_records(
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: app.mongodb)
):
    try:
        cursor = db.health_records.find({"user_id": current_user})
        records = await cursor.to_list(length=None)
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/records/{record_id}", response_model=HealthRecord)
async def get_health_record(
    record_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: app.mongodb)
):
    try:
        record = await db.health_records.find_one({
            "_id": record_id,
            "user_id": current_user
        })
        if not record:
            raise HTTPException(status_code=404, detail="Record not found")
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/records/{record_id}")
async def delete_health_record(
    record_id: str,
    current_user: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(lambda: app.mongodb)
):
    try:
        result = await db.health_records.delete_one({
            "_id": record_id,
            "user_id": current_user
        })
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Record not found")
        return {"message": "Record deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
