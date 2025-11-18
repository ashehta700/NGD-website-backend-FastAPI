from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# ---------------- DatasetInfo ----------------
class DatasetInfoBase(BaseModel):
    Name: str
    NameAr: str
    Title: Optional[str] = None
    TitleAr: Optional[str] = None
    description: Optional[str] = None
    descriptionAr: Optional[str] = None
    CRS_Name: Optional[str] = None
    EPSG: Optional[int] = 3857
    Keywords: Optional[str] = None
    KeywordsAr: Optional[str] = None
    img: Optional[str] = None

class DatasetInfoCreate(DatasetInfoBase):
    pass

class DatasetInfoUpdate(DatasetInfoBase):
    pass

class DatasetInfoResponse(DatasetInfoBase):
    DatasetID: int
    class Config:
        orm_mode = True


# ---------------- MetadataInfo ----------------
class MetadataInfoBase(BaseModel):
    DatasetID: int
    Name: str
    NameAr: str
    Title: Optional[str] = None
    TitleAr: Optional[str] = None
    description: Optional[str] = None
    descriptionAr: Optional[str] = None
    CreationDate: Optional[date] = None
    URL: Optional[str] = None
    WestBound: Optional[float] = None
    EastBound: Optional[float] = None
    NorthBound: Optional[float] = None
    SouthBound: Optional[float] = None
    MetadataStandardName: Optional[str] = "ISO19115"
    MetadataStandardVersion: Optional[str] = "1.0"
    ContactName: Optional[str] = None
    PositionName: Optional[str] = None
    Organization: Optional[str] = None
    Email: Optional[str] = None
    Phone: Optional[str] = None
    Role: Optional[str] = None

class MetadataInfoCreate(MetadataInfoBase):
    pass

class MetadataInfoUpdate(MetadataInfoBase):
    pass

class MetadataInfoResponse(MetadataInfoBase):
    MetadataID: int
    class Config:
        orm_mode = True
