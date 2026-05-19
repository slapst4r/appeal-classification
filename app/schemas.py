from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

class CategoryResult(BaseModel):
    category: str
    reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ClassificationResponse(BaseModel):
    id: int
    category: Optional[CategoryResult] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ClassificationRequest(BaseModel):
    text: str = Field(..., max_length=2000)

class AppealFromDB(ClassificationResponse):
    text: str
    contains_explicit: bool
    unclassified_reason: Optional[str]

    model_config = ConfigDict(from_attributes=True)
    

class AnalyticsResponse(BaseModel):
    total_appeals: int
    categories_distribution: dict[str, int] #распределение категорий
    profanity_share: float  #отношение цензурных к нецензурным