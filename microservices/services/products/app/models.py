from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from datetime import datetime
from .database import Base


class Product(Base):
    __tablename__ = "ProductsDB"
    __table_args__ = {"schema": "Website"}

    ProductID = Column(Integer, primary_key=True, index=True)
    NameEn = Column(String(150), nullable=False)
    NameAr = Column(String(150))
    DescriptionEn = Column(String)
    DescriptionAr = Column(String)
    ServicesName = Column(String(150))
    ServicesDescription = Column(String)
    ServicesLink = Column(String(500))
    ImagePath = Column(String(500))
    VideoPath = Column(String(500))
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedAt = Column(DateTime)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    IsDeleted = Column(Boolean, default=False, nullable=False)


