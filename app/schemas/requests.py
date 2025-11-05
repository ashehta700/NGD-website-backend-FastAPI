from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RequestInformationBase(BaseModel):
    Id: int
    Name: str
    Name_Ar: str

    class Config:
        orm_mode = True

class FormatBase(BaseModel):
    Id: int
    Name: str
    Type: str

    class Config:
        orm_mode = True

class RequestCreate(BaseModel):
    UserId: int
    CategoryId: int
    ComplaintScreenId: Optional[int]
    Subject: Optional[str]
    Body: Optional[str]
    # Make the rest optional
    ProspectiveName: Optional[str] = None
    Coordinate_TopLeft: Optional[str] = None
    Coordinate_BottomRight: Optional[str] = None
    ProjectionId: Optional[int] = None
    OtherSpecification: Optional[str] = None
    OtherFormat: Optional[str] = None
    IntendedPurpose: Optional[str] = None
    RequirementsDetails: Optional[str] = None
    AssignedRoleId: Optional[int] = None
    RequestInformationIds: Optional[List[int]] = None
    FormatIds: Optional[List[int]] = None

class RequestResponse(BaseModel):
    Id: int
    RequestNumber: Optional[str]
    Subject: Optional[str]
    StatusId: Optional[int]
    CreatedAt: datetime

    class Config:
        orm_mode = True

class ReplyCreate(BaseModel):
    RequestId: int
    Subject: Optional[str]
    Body: Optional[str]
