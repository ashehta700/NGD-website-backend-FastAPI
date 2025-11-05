from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Unicode, UnicodeText
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Logo(Base):
    __tablename__ = "Logos"
    __table_args__ = {"schema": "Website"}

    LogoID = Column(Integer, primary_key=True, index=True)
    NameEn = Column(String(150), nullable=False)
    NameAr = Column(Unicode(255), nullable=False)
    ImagePath = Column(String(500), nullable=True)
    Link = Column(String(500), nullable=True)
    Category = Column(String(100), nullable=True)  # "partner" or "benefits"
    CreatedAt = Column(DateTime, nullable=False, default=datetime.utcnow)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"), nullable=True)
    UpdatedAt = Column(DateTime, nullable=True)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"), nullable=True)

    created_by = relationship("User", foreign_keys=[CreatedByUserID])
    updated_by = relationship("User", foreign_keys=[UpdatedByUserID])
