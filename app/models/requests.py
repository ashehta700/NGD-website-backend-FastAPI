# models/request.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey,Unicode,UnicodeText,Table
from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import lookups
from app.models.role_feature import Role

class Request(Base):
    __tablename__ = "Requests"
    __table_args__ = {"schema": "Requests"}

    Id = Column(Integer, primary_key=True, index=True)
    UserId = Column(Integer, nullable=False)
    CategoryId = Column(Integer, ForeignKey("Requests.Category.Id"), nullable=False)
    ComplaintScreenId = Column(Integer, ForeignKey("Requests.ComplaintScreen.Id"), nullable=False) #FK to ComplaintScreen (only for Complaints)
    Subject = Column(Unicode(250), nullable=True)
    Body = Column(UnicodeText, nullable=True)  
    AttachPath = Column(String(500), nullable=True)


    #-- RequestData-specific fields:
    # ProspectiveName = Column(String(200), nullable=True)
    # Coordinate_TopLeft = Column(String(50), nullable=True)
    # Coordinate_BottomRight = Column(String(50), nullable=True)
    # ProjectionId = Column(Integer, ForeignKey("Requests.Projection.Id"), nullable=True)
    # OtherSpecification = Column(String(200), nullable=True)
    # OtherFormat = Column(String(200), nullable=True)
    # IntendedPurpose = Column(String(300), nullable=True)
    # RequirementsDetails = Column(Text, nullable=True)


    #-- Workflow
    StatusId = Column(Integer, ForeignKey("Requests.Status.Id"), nullable=True)
    AssignedRoleId = Column(Integer, ForeignKey("Website.Roles.RoleID"), nullable=True)
    RequestNumber = Column(String(50), nullable=True)


    #Audit
    CreatedAt = Column(DateTime, server_default=func.sysdatetime(), nullable=False)
    CreatedByUserID = Column(Integer, nullable=True)
    UpdatedAt = Column(DateTime, nullable=True)
    UpdatedByUserID = Column(Integer, nullable=True)
    IsDeleted = Column(Boolean, default=False)

    # relationships (optional, helpful)
    #replies = relationship("Reply", back_populates="request", cascade="all, delete-orphan")



class RequestData(Base):
    __tablename__ = "RequestData"
    __table_args__ = {"schema": "Requests"}

    Id = Column(Integer, primary_key=True, index=True)
    RequestId = Column(Integer, ForeignKey("Requests.Requests.Id", ondelete="CASCADE"), nullable=False)
    ProspectiveName = Column(String(200), nullable=True)
    Coordinate_TopLeft = Column(String(50), nullable=True)
    Coordinate_BottomRight = Column(String(50), nullable=True)
    ProjectionId = Column(Integer, ForeignKey("Requests.Projection.Id"), nullable=True)
    OtherSpecification = Column(String(200), nullable=True)
    OtherFormat = Column(String(200), nullable=True)
    IntendedPurpose = Column(String(300), nullable=True)
    RequirementsDetails = Column(Text, nullable=True)
    CreatedAt = Column(DateTime)



# Many-to-many relationships
Request_RequestInformation = Table(
    "Request_RequestInformation", Base.metadata,
    Column("RequestId", Integer, ForeignKey("Requests.Requests.Id", ondelete="CASCADE"), primary_key=True),
    Column("RequestInformationId", Integer, ForeignKey("Requests.RequestInformation.Id"), primary_key=True),
    schema="Requests"
)

Request_Format = Table(
    "Request_Format", Base.metadata,
    Column("RequestId", Integer, ForeignKey("Requests.Requests.Id", ondelete="CASCADE"), primary_key=True),
    Column("FormatId", Integer, ForeignKey("Requests.Format.Id"), primary_key=True),
    schema="Requests"
)



# The table for replay to the requests
class Reply(Base):
    __tablename__ = "Reply"
    __table_args__ = {"schema": "Requests"}

    Id = Column(Integer, primary_key=True, index=True)
    RequestId = Column(Integer, ForeignKey("Requests.Requests.Id"), nullable=False)
    ResponderUserId = Column(Integer, ForeignKey("Website.Users.UserID"), nullable=False)
    Subject = Column(String(250), nullable=True)
    Body = Column(Text, nullable=True)
    AttachmentPath = Column(String(500), nullable=True)
    CreatedAt = Column(DateTime, server_default=func.sysdatetime())
    CreatedByUserID = Column(Integer, nullable=True)
    IsDeleted = Column(Boolean, default=False)

    # request = relationship("Request", back_populates="replies")
