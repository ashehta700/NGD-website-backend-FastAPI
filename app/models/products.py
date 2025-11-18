from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UnicodeText, Boolean , Unicode
from app.database import Base
from datetime import datetime


class Product(Base):
    __tablename__ = "ProductsDB"
    __table_args__ = {"schema": "Website"}

    ProductID = Column(Integer, primary_key=True, index=True)
    NameEn = Column(String(150), nullable=False)
    NameAr = Column(Unicode(150))
    DescriptionEn = Column(UnicodeText)
    DescriptionAr = Column(UnicodeText)
    ServicesName = Column(Unicode(150))
    ServicesDescription = Column(UnicodeText)
    ServicesLink = Column(String(500))
    ImagePath = Column(String(500))
    VideoPath = Column(String(500))
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedAt = Column(DateTime)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    IsDeleted = Column(Boolean, nullable=False, default=False)


