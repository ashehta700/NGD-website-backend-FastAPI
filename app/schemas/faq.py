from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FAQBase(BaseModel):
    QuestionEn: Optional[str] = None
    QuestionAr: Optional[str] = None
    AnswerEn: Optional[str] = None
    AnswerAr: Optional[str] = None  
    CategoryID: Optional[int] = None

    class Config:
        orm_mode = True

class FAQCreate(BaseModel):
    QuestionEn: str
    QuestionAr: Optional[str] = None
    AnswerEn: Optional[str] = None
    AnswerAr: Optional[str] = None
    CategoryID: Optional[int]

class FAQUpdate(BaseModel):
    QuestionEn: Optional[str] = None
    QuestionAr: Optional[str] = None
    AnswerEn: Optional[str] = None
    AnswerAr: Optional[str] = None
    CategoryID: Optional[int]

class FAQResponse(FAQBase):
    FAQID: int
    CreatedAt: Optional[datetime] = None
    CreatedByUserID: Optional[int] = None
    UpdatedAt: Optional[datetime] = None
    UpdatedByUserID: Optional[int] = None
