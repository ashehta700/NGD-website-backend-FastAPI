from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime , Boolean , Unicode, UnicodeText
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship
from app.models import lookups




class News(Base):
    __tablename__ = "News"
    __table_args__ = {'schema': 'Website'} 
    
    NewsID = Column(Integer, primary_key=True, index=True)
    TitleEn = Column(String(255))
    TitleAr = Column(Unicode(255), nullable=False)
    DescriptionEn = Column(String(255))
    DescriptionAr = Column(UnicodeText)
    ImagePath = Column(String(255))
    VideoPath = Column(String(255))
    CreatedAt = Column(DateTime)
    UpdatedAt = Column(DateTime)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    Is_slide = Column(Boolean, default=False)
    Is_delete = Column(Boolean, default=False)
    Read_count = Column(Integer())
    
    