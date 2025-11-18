# app/models/users.py
from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Boolean, Unicode, UnicodeText
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship
from app.models import lookups
from app.models.role_feature import Role

class User(Base):
    __tablename__ = "Users"
    __table_args__ = {'schema': 'Website'}

    UserID = Column(Integer, primary_key=True, index=True)
    TitleId = Column(Integer, ForeignKey("Website.UsersTitle.Id"))
    FirstName = Column(UnicodeText)
    LastName = Column(UnicodeText)
    OrganizationTypeID = Column(Integer, ForeignKey("Website.OrganizationTypes.OrganizationTypeID"))
    OrganizationName = Column(UnicodeText)
    Department = Column(UnicodeText)
    JobTitle = Column(Unicode(100))
    CityID = Column(Integer, ForeignKey("Website.Cities.CityID"))
    CountryID = Column(Integer, ForeignKey("dbo.COUNTRIES_LIST.OBJECTID"))
    PhoneNumber = Column(String(50), unique=True, index=True)
    Email = Column(String(150), unique=True, index=True, nullable=False)
    PasswordHash = Column(String(255), nullable=False)
    RoleID = Column(Integer, ForeignKey("Website.Roles.RoleID"))
    UserType = Column(UnicodeText)
    PhotoPath = Column(String(500))
    DateOfBirth = Column(Date)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedAt = Column(DateTime)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    IsDeleted = Column(Boolean, default=False, nullable=False)

    # ✅ Newly added fields
    IsApproved = Column(Boolean, default=False)
    EmailVerified = Column(Boolean, default=False)
    IsActive = Column(Boolean, default=False)

    role = relationship("role_feature.Role", foreign_keys=[RoleID])
    organization_type = relationship("lookups.OrganizationType", foreign_keys=[OrganizationTypeID])
    city = relationship("lookups.City", foreign_keys=[CityID])
    country = relationship("lookups.Country", foreign_keys=[CountryID])
