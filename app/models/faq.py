from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Unicode, UnicodeText ,Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class FAQ(Base):
    __tablename__ = "FAQ"
    __table_args__ = {"schema": "Website"}

    FAQID = Column(Integer, primary_key=True, index=True)
    QuestionEn = Column(Text, nullable=False)
    QuestionAr = Column(Unicode(255), nullable=False)
    AnswerEn = Column(Text, nullable=True)
    AnswerAr = Column(UnicodeText)
    CategoryID = Column(Integer, ForeignKey("Website.FAQCategories.CategoryID"), nullable=True)
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"), nullable=True)
    UpdatedAt = Column(DateTime, nullable=True)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"), nullable=True)
    IsDelete = Column(Boolean, nullable=False, default=False)

