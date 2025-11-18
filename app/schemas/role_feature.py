from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AppFeatureBase(BaseModel):
    NameEn: str
    NameAr: Optional[str] = None
    DescriptionEn: Optional[str] = None
    DescriptionAr: Optional[str] = None
    Link: Optional[str] = None

class AppFeatureCreate(AppFeatureBase):
    pass

class AppFeatureUpdate(BaseModel):
    NameEn: Optional[str] = None
    NameAr: Optional[str] = None
    DescriptionEn: Optional[str] = None
    DescriptionAr: Optional[str] = None
    Link: Optional[str] = None

class AppFeatureOut(AppFeatureBase):
    AppFeatureID: int
    class Config:
        orm_mode = True


class RoleBase(BaseModel):
    NameEn: str
    NameAr: Optional[str] = None
    DescriptionEn: Optional[str] = None
    DescriptionAr: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    NameEn: Optional[str] = None
    NameAr: Optional[str] = None
    DescriptionEn: Optional[str] = None
    DescriptionAr: Optional[str] = None

class RoleOut(RoleBase):
    RoleID: int
    features: List[AppFeatureOut] = []
    class Config:
        orm_mode = True
