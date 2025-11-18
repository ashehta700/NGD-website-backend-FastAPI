from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ManualGuideBase(BaseModel):
    NameEn: Optional[str] = None
    NameAr: Optional[str] = None
    DescriptionEn: Optional[str] = None
    DescriptionAr: Optional[str] = None
    Path: Optional[str] = None

    

class ManualGuideResponse(BaseModel):
    ManualGuideID: int
    NameEn: str
    NameAr: Optional[str]
    DescriptionEn: Optional[str]
    DescriptionAr: Optional[str]
    Path: Optional[str]
    CreatedAt: datetime
    CreatedByUserID: Optional[int]
    UpdatedAt: Optional[datetime]
    UpdatedByUserID: Optional[int]

    model_config = ConfigDict(from_attributes=True)
