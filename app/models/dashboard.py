# models.py
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

      
Base = declarative_base()


# -------------------------
# Visitors Table
# -------------------------
class Visitor(Base):
    __tablename__ = "Visitors"
    __table_args__ = {"schema": "Website"}

    VisitorID = Column(Integer, primary_key=True, index=True)
    IPAddress = Column(String)
    Location = Column(String)
    X = Column(Float)
    Y = Column(Float)
    Geom = Column(String)
    VisitAt = Column(DateTime)
    SessionID = Column(String)
    CountryID = Column(Integer)


# -------------------------
# Countries Table
# -------------------------
class Country(Base):
    __tablename__ = "COUNTRIES_LIST"
    __table_args__ = {"schema": "dbo"}

    OBJECTID = Column(Integer, primary_key=True, index=True)
    CountryCode = Column(String)
    CountryName = Column(String)
    Latitude = Column(Float)
    Longitude = Column(Float)
    Geom = Column(String)


# -------------------------
# View: VIEW_DOWNLOAD_REQUESTS
# (joined data from DOWNLOAD_REQUESTS + DOWNLOAD_ITEMS)
# -------------------------
class DownloadRequest(Base):
    __tablename__ = "VIEW_DOWNLOAD_REQUESTS"
    __table_args__ = {"schema": "dbo"}

    itemid = Column(Integer, primary_key=True, index=True)
    ReqNo = Column(String)
    DatasetName = Column(String)
    GridCode = Column(String)
    EnglishName = Column(String)
    ArabicName = Column(String)
    AreaType = Column(String)
    OrgType = Column(String)
    # OrgName = Column(String)
    # City = Column(String)
    # Country = Column(String)
    CountryCode = Column(String)
    CountryName = Column(String)
    requestdate = Column(DateTime)
    Latitude = Column(Float)
    Longitude = Column(Float)
    Geom = Column(String)


from sqlalchemy import Index

Index("ix_downloadrequest_filters", DownloadRequest.CountryName, DownloadRequest.OrgType, DownloadRequest.DatasetName, DownloadRequest.requestdate)
  
  
Index("ix_downloadrequest_filters",
      DownloadRequest.CountryName,
      DownloadRequest.OrgType,
      DownloadRequest.DatasetName,
      DownloadRequest.requestdate)