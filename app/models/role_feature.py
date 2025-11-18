from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text , Unicode , UnicodeText
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class RoleApp(Base):
    __tablename__ = "RoleApp"
    __table_args__ = {"schema": "Website"}

    RoleAppID = Column(Integer, primary_key=True, index=True)
    RoleID = Column(Integer, ForeignKey("Website.Roles.RoleID"), nullable=False)
    AppFeatureID = Column(Integer, ForeignKey("Website.AppFeatures.AppFeatureID"), nullable=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"), nullable=True)

    # relationships
    role = relationship("Role", back_populates="role_apps")
    app_feature = relationship("AppFeature", back_populates="role_apps")


class Role(Base):
    __tablename__ = "Roles"
    __table_args__ = {"schema": "Website"}

    RoleID = Column(Integer, primary_key=True, index=True)
    NameEn = Column(String(100), nullable=False)
    NameAr = Column(Unicode(100))
    DescriptionEn = Column(Text)
    DescriptionAr = Column(UnicodeText)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedAt = Column(DateTime)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))

    # link to RoleApp
    role_apps = relationship("RoleApp", back_populates="role", cascade="all, delete-orphan")

    # convenience access to AppFeatures via RoleApp
    features = relationship("AppFeature", secondary="Website.RoleApp", viewonly=True)


class AppFeature(Base):
    __tablename__ = "AppFeatures"
    __table_args__ = {"schema": "Website"}

    AppFeatureID = Column(Integer, primary_key=True, index=True)
    NameEn = Column(String(100), nullable=False)
    NameAr = Column(Unicode(100))
    DescriptionEn = Column(Text)
    DescriptionAr = Column(UnicodeText)
    Link = Column(String(500))
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedAt = Column(DateTime)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))

    # link to RoleApp
    role_apps = relationship("RoleApp", back_populates="app_feature")

    # convenience access to Roles via RoleApp
    roles = relationship("Role", secondary="Website.RoleApp", viewonly=True)
