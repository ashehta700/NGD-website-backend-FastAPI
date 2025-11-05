from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class ProjectDetailBase(BaseModel):
    Year: Optional[int] = None
    Quarter: Optional[int] = None
    ServiceName: Optional[str] = None
    ServiceLink: Optional[str] = None
    ServiceDescription: Optional[str] = None
    ServiceDescriptionAr: Optional[str] = None
    Details: Optional[str] = None
    DetailsAr: Optional[str] = None
    Communication: Optional[str] = None
    CommunicationAr: Optional[str] = None
    Attribute: Optional[Dict[str, str]] = None
    AttributeAr: Optional[Dict[str, str]] = None
    PdfName: Optional[str] = None
    PdfPath: Optional[str] = None


class ProjectDetailCreate(ProjectDetailBase):
    Year: int
    Quarter: int


class ProjectDetailUpdate(ProjectDetailBase):
    # explicitly allow partial updates
    class Config:
        extra = "allow"   # ignore unknown fields if sent
        from_attributes = True


class ProjectDetailResponse(ProjectDetailBase):
    ProjectDetailID: int
    ProjectID: int
    CreatedAt: datetime

    class Config:
        from_attributes = True
