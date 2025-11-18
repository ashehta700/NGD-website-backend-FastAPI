from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class VideoBase(BaseModel):
    TitleEn: Optional[str] = None
    TitleAr: Optional[str] = None
    DescriptionEn: Optional[str] = None
    DescriptionAr: Optional[str] = None
    Link: Optional[HttpUrl] = None  # YouTube link
    Category: Optional[str] = None

class VideoCreate(VideoBase):
    TitleEn: str  # required
    Link: HttpUrl # required (YouTube URL)

class VideoUpdate(VideoBase):
    pass  # all optional

class VideoOut(VideoBase):
    VideoID: int
    ImagePath: Optional[str] = None
    CreatedAt: datetime
    CreatedByUserID: Optional[int]
    UpdatedAt: Optional[datetime]
    UpdatedByUserID: Optional[int]

    class Config:
        orm_mode = True
