from pydantic import BaseModel
from typing import Optional

class FAQCategoryBase(BaseModel):
    NameEn: Optional[str]
    NameAr: Optional[str]

    class Config:
        orm_mode = True

class FAQCategoryCreate(BaseModel):
    NameEn: str
    NameAr: Optional[str] = None

class FAQCategoryResponse(FAQCategoryBase):
    CategoryID: int


class CategorySchema(BaseModel):
    Id: int
    Name: str
    Name_Ar: str

    model_config = {
        "from_attributes": True
    }

class ProjectionSchema(BaseModel):
    Id: int
    Name: str
    
    model_config = {
        "from_attributes": True
    }

class FormatSchema(BaseModel):
    Id: int
    Name: str
    Type: str
    
    model_config = {
        "from_attributes": True
    }

class RequestInformationSchema(BaseModel):
    Id: int
    Name: str
    Name_Ar: str
    model_config = {
        "from_attributes": True
    }

class StatusSchema(BaseModel):
    Id: int
    Name: str
    Name_Ar: str
    model_config = {
        "from_attributes": True
    }
class ComplaintScreenSchema(BaseModel):
    Id: int
    Name: str
    Name_Ar: str
    model_config = {
        "from_attributes": True
    }