from pydantic import BaseModel, EmailStr
from typing import Optional ,List
from datetime import datetime




class ProjectResponse(BaseModel):
    ProjectID: Optional[int]
    NameEn: Optional[str]
    NameAr: Optional[str]
    DescriptionEn: Optional[str]
    DescriptionAr: Optional[str]
    ServicesName: Optional[str]
    ServicesLink: Optional[str]
    ImagePath: Optional[str]
    VideoPath: Optional[str]
    CreatedAt: Optional[datetime]

    class Config:
        from_attributes = True
        
# return projects as a list   
class ProjectListResponse(BaseModel):
    success: bool
    message: str
    data: List[ProjectResponse]  
        
# ---------- create new Project ----------
class ProjectCreate(BaseModel):
    NameEn: str
    NameAr: str
    DescriptionEn: Optional[str] = None
    DescriptionAr: Optional[str] = None
    ServicesName: Optional[str] = None
    ServicesLink: Optional[str] = None
    ImagePath: Optional[str] = None
    VideoPath: Optional[str] = None


# ---------- Update a Project ----------
class ProjectUpdate(BaseModel):
    NameEn: Optional[str] = None
    NameAr: Optional[str]  = None
    DescriptionEn: Optional[str] = None
    DescriptionAr: Optional[str] = None
    ServicesName: Optional[str] = None
    ServicesLink: Optional[str] = None
    ImagePath: Optional[str] = None
    VideoPath: Optional[str]    = None    
    
    class Config:
        extra = "allow"  # allows fields not declared, or partials    