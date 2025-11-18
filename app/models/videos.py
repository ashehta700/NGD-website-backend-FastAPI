from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func , Unicode , UnicodeText ,Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Video(Base):
    __tablename__ = "Videos"
    __table_args__ = {"schema": "Website"}

    VideoID = Column(Integer, primary_key=True, index=True)
    TitleEn = Column(String(150), nullable=False)
    TitleAr = Column(Unicode(150), nullable=True)
    DescriptionEn = Column(Text, nullable=True)
    DescriptionAr = Column(UnicodeText, nullable=True)
    ImagePath = Column(String(500), nullable=True)
    Link = Column(String(500), nullable=True)
    CreatedAt = Column(DateTime, server_default=func.sysutcdatetime(), nullable=False)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"), nullable=True)
    UpdatedAt = Column(DateTime, nullable=True)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"), nullable=True)
    IsDeleted = Column(Boolean, default=False)

    created_by = relationship("User", foreign_keys=[CreatedByUserID], lazy="joined")
    updated_by = relationship("User", foreign_keys=[UpdatedByUserID], lazy="joined")
