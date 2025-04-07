from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId

class Parameter(BaseModel):
    name: str
    value: float
    unit: str
    status: str = "normal"  # normal, high, low, critical
    reference_range: Optional[Dict[str, float]] = None

class HealthRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    file_name: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    test_date: datetime
    test_type: str
    parameters: List[Parameter]
    provider: Optional[str] = None
    notes: Optional[str] = None
    
    model_config = {
        'validate_by_name': True,
        'json_encoders': {
            ObjectId: str
        },
        'arbitrary_types_allowed': True
    }
