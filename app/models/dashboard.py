# models.py
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Visitor(Base):
    __tablename__ = "Visitors"
    __table_args__ = {"schema": "Website"}
    VisitorID = Column(Integer, primary_key=True)
    IPAddress = Column(String)
    Location = Column(String)
    X = Column(Float)
    Y = Column(Float)
    Geom = Column(String)
    VisitAt = Column(DateTime)
    SessionID = Column(String)
    CountryID = Column(Integer)

class Country(Base):
    __tablename__ = "COUNTRIES_LIST"
    __table_args__ = {"schema": "dbo"}
    OBJECTID = Column(Integer, primary_key=True)
    CountryCode = Column(String)
    CountryName = Column(String)
    Latitude = Column(Float)
    Longitude = Column(Float)
    Geom = Column(String)

class DownloadRequest(Base):
    __tablename__ = "VIEW_DOWNLOAD_REQUESTS"
    __table_args__ = {"schema": "dbo"}
    OBJECTID = Column(Integer, primary_key=True)
    Title = Column(String)
    FullName = Column(String)
    OrgType = Column(String)
    OrgName = Column(String)
    City = Column(String)
    Country = Column(String)
    PhoneNumber = Column(String)
    Email = Column(String)
    Purpose = Column(String)
    Date = Column(DateTime)
    FileName = Column(String)
    CountryName = Column(String)
    Latitude = Column(Float)
    Longitude = Column(Float)
    Geom = Column(String)
