from sqlalchemy import Column, Integer, String, Text, Date, Float, ForeignKey ,Boolean ,Unicode , UnicodeText
from sqlalchemy.orm import relationship
from app.database import Base

class DatasetInfo(Base):
    __tablename__ = "DatasetInfo"
    __table_args__ = {"schema": "Metadata"}

    DatasetID = Column(Integer, primary_key=True, index=True)
    Name = Column(String(200), nullable=False)
    NameAr = Column(Unicode(200), nullable=False)
    Title = Column(Text)
    TitleAr = Column(UnicodeText)
    description = Column(Text)
    descriptionAr = Column(UnicodeText)
    CRS_Name = Column(String(200))
    EPSG = Column(Integer, default=3857)
    Keywords = Column(Text)
    KeywordsAr = Column(UnicodeText)
    img = Column(Text)
    IsDeleted = Column(Boolean, default=False)

    metadata_info = relationship("MetadataInfo", back_populates="dataset", cascade="all, delete")


class MetadataInfo(Base):
    __tablename__ = "MetadataInfo"
    __table_args__ = {"schema": "Metadata"}

    MetadataID = Column(Integer, primary_key=True, index=True)
    DatasetID = Column(Integer, ForeignKey("Metadata.DatasetInfo.DatasetID"))
    Name = Column(String(200), nullable=False)
    NameAr = Column(Unicode(200), nullable=False)
    Title = Column(Text)
    TitleAr = Column(Unicode(200))
    description = Column(Text)
    descriptionAr = Column(UnicodeText)
    CreationDate = Column(Date)
    URL = Column(Unicode(500))
    WestBound = Column(Float)
    EastBound = Column(Float)
    NorthBound = Column(Float)
    SouthBound = Column(Float)
    MetadataStandardName = Column(String(200), default="ISO19115")
    MetadataStandardVersion = Column(String(50), default="1.0")
    ContactName = Column(String(200))
    PositionName = Column(String(200))
    Organization = Column(String(200))
    Email = Column(String(100))
    Phone = Column(String(50))
    Role = Column(String(50))
    FilePath = Column(Text)
    IsDeleted = Column(Boolean, default=False)

    dataset = relationship("DatasetInfo", back_populates="metadata_info")
