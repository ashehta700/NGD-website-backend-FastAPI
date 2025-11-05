from sqlalchemy import Column, Integer, String, Float, DateTime
from geoalchemy2 import Geometry
from datetime import datetime
from app.database import Base

class Visitor(Base):
    __tablename__ = "Visitors"
    __table_args__ = {"schema": "Website"}

    VisitorID = Column(Integer, primary_key=True, index=True)
    IPAddress = Column(String(50))
    Location = Column(String(255))
    X = Column(Float)
    Y = Column(Float)
    Geom = Column(Geometry(geometry_type='POINT', srid=4326))
    VisitAt = Column(DateTime, default=datetime.utcnow)
    SessionID = Column(String(100))
