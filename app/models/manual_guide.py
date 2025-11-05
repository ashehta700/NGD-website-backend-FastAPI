from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey ,UnicodeText  
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class ManualGuide(Base):
    __tablename__ = "ManualGuide"
    __table_args__ = {"schema": "Website"}

    ManualGuideID = Column(Integer, primary_key=True, index=True)
    NameEn = Column(String(150), nullable=False)
    NameAr = Column(UnicodeText)
    DescriptionEn = Column(String)
    DescriptionAr = Column(UnicodeText)
    Path = Column(String(500))
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    IsDelete = Column(Boolean, default=False)
    UpdatedAt = Column(DateTime, nullable=True)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))

    CreatedByUser = relationship("User", foreign_keys=[CreatedByUserID])
    UpdatedByUser = relationship("User", foreign_keys=[UpdatedByUserID])
