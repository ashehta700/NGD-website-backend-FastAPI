from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductResponse(BaseModel):
    ProductID: Optional[int]
    NameEn: Optional[str]
    NameAr: Optional[str]
    DescriptionEn: Optional[str]
    DescriptionAr: Optional[str]
    ServicesName: Optional[str]
    ServicesDescription: Optional[str]
    ServicesLink: Optional[str]
    ImagePath: Optional[str]
    VideoPath: Optional[str]
    CreatedAt: Optional[datetime]

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    NameEn: str
    NameAr: Optional[str] = None
    DescriptionEn: Optional[str] = None
    DescriptionAr: Optional[str] = None
    ServicesName: Optional[str] = None
    ServicesDescription: Optional[str] = None
    ServicesLink: Optional[str] = None


class ProductUpdate(BaseModel):
    NameEn: Optional[str] = None
    NameAr: Optional[str] = None
    DescriptionEn: Optional[str] = None
    DescriptionAr: Optional[str] = None
    ServicesName: Optional[str] = None
    ServicesDescription: Optional[str] = None
    ServicesLink: Optional[str] = None

