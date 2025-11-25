# models/dashboard.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from app.database import Base

class DownloadRequest(Base):
    __tablename__ = "DOWNLOAD_REQUESTS"
    __table_args__ = {"schema": "dbo"}

    ReqNo = Column(Integer, primary_key=True, index=True)
    Title = Column(String(10))
    FullName = Column(String(100))
    OrgType = Column(String(50))
    OrgName = Column(String(100))
    DeptName = Column(String(100))
    JobTitle = Column(String(100))
    City = Column(String(50))
    Country = Column(String(50))
    PhoneNumber = Column(String(25))
    Email = Column(String(100))
    Purpose = Column(String(500))
    Date = Column(DateTime)
    FileName = Column(String(50))
    UserID = Column(Integer)

class DownloadItem(Base):
    __tablename__ = "DOWNLOAD_ITEMS"
    __table_args__ = {"schema": "dbo"}

    ID = Column(Integer, primary_key=True, index=True)
    ReqNo = Column(Integer, ForeignKey("dbo.DOWNLOAD_REQUESTS.ReqNo"))
    DatasetName = Column(String(50))
    DatasetURL = Column(String(255))
    GridCode = Column(String(50))
    EnglishName = Column(String(100))
    ArabicName = Column(String(100))
    AreaType = Column(String(50))
    Cost = Column(String(50))
    FileName = Column(String(50))


class NGDModsBiblio(Base):
    __tablename__ = "NGD_MODS_BIBLIO"
    __table_args__ = {"schema": "dbo"}

    MODS = Column(String(50), primary_key=True, nullable=False)
    ReportID = Column(String(50), primary_key=True, nullable=False)


class BibliographyDownloadRequest(Base):
    __tablename__ = "BIBLIOGRAPHY_DOWNLOAD_REQUESTS"
    __table_args__ = {"schema": "dbo"}

    ReqNo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    MODS = Column(String(255))
    MODSEngName = Column(String(255))
    Purpose = Column(String(255))
    Date = Column(DateTime)
    FileName = Column(String(255))
    UserID = Column(String(255))