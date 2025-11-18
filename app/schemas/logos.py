from pydantic import BaseModel
from typing import Optional
from datetime import datetime

VALID_CATEGORIES = {"partner", "benefits"}

class LogoBase(BaseModel):
    NameEn: Optional[str]
    NameAr: Optional[str]
    ImagePath: Optional[str]
    Link: Optional[str]
    Category: Optional[str]

    class Config:
        from_attributes=True

class LogoCreate(BaseModel):
    NameEn: str
    NameAr: Optional[str] = None
    Link: Optional[str] = None
    Category: str  # Should be "partner" or "benefits"

    def validate_category(self):
        if self.Category.lower() not in VALID_CATEGORIES:
            raise ValueError(f"Invalid Category. Allowed values: {VALID_CATEGORIES}")

class LogoUpdate(BaseModel):
    NameEn: Optional[str] = None
    NameAr: Optional[str] = None
    Link: Optional[str] = None
    Category: Optional[str] = None

class LogoResponse(LogoBase):
    LogoID: int
    CreatedAt: datetime
    CreatedByUserID: Optional[int]
    UpdatedAt: Optional[datetime]
    UpdatedByUserID: Optional[int]
