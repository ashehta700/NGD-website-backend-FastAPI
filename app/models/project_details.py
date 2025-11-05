import json
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.types import TypeDecorator, UnicodeText
from app.database import Base
from datetime import datetime

class JSONDict(TypeDecorator):
    impl = UnicodeText

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        raise ValueError("Attribute must be a dict")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return json.loads(value)
        except Exception:
            return {}
        

class ProjectDetails(Base):
    __tablename__ = "ProjectDetails"
    __table_args__ = {"schema": "Website"}

    ProjectDetailID = Column(Integer, primary_key=True, index=True)
    ProjectID = Column(Integer, ForeignKey("Website.Projects.ProjectID"), nullable=False)
    Year = Column(Integer, nullable=False)
    Quarter = Column(Integer, nullable=False)

    ServiceName = Column(String(150))
    ServiceLink = Column(String(500))
    ServiceDescription = Column(String)
    ServiceDescriptionAr = Column(UnicodeText)  # NEW
    Details = Column(String)
    DetailsAr = Column(UnicodeText)            # NEW
    Communication = Column(String)
    CommunicationAr = Column(UnicodeText)       # NEW

    Attribute = Column(JSONDict)           # dict {key: description}
    AttributeAr = Column(JSONDict)         # dict (Arabic)  # NEW

    PdfName = Column(String(150))
    PdfPath = Column(String(500))

    CreatedAt = Column(DateTime, default=datetime.utcnow)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedAt = Column(DateTime)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    IsDeleted = Column(Boolean, default=False)
