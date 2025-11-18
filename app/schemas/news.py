from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NewsBase(BaseModel):
    TitleEn: Optional[str]
    TitleAr: Optional[str]
    DescriptionEn: Optional[str]
    DescriptionAr: Optional[str]
    ImagePath: Optional[str]
    VideoPath: Optional[str]
    Is_slide: Optional[bool] = False
    Is_delete: Optional[bool] = False
    Read_count: Optional[int] = 0

    class Config:
        from_attributes = True  # allows .from_orm()




class NewsResponse(NewsBase):
    NewsID: int
    CreatedAt: datetime
    UpdatedAt: Optional[datetime]
    CreatedByUserID: Optional[int]
    UpdatedByUserID: Optional[int]
