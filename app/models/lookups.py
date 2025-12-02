from sqlalchemy import Column, Integer, String, ForeignKey, DateTime ,LargeBinary, Unicode, UnicodeText, Boolean, Float
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from geoalchemy2 import Geometry








# lookups for users 
class UserTitle(Base):
    __tablename__ = "UsersTitle"
    __table_args__ = {"schema": "Website"}  
    
    Id = Column(Integer, primary_key=True)
    Title = Column(String(100), nullable=False)





class OrganizationType(Base):
    __tablename__ = "OrganizationTypes"
    __table_args__ = {"schema": "Website"}

    OrganizationTypeID = Column(Integer, primary_key=True)
    NameEn = Column(String(100), nullable=False)
    NameAr = Column(Unicode(255), nullable=False)
    DescriptionEn = Column(String)
    DescriptionAr = Column(UnicodeText)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedAt = Column(DateTime)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))


# class Country(Base):
#     __tablename__ = "Countries"
#     __table_args__ = {"schema": "Website"}

#     CountryID = Column(Integer, primary_key=True)
#     NameEn = Column(String(100), nullable=False)
#     NameAr = Column(Unicode(255), nullable=False)
#     IsoCode2 = Column(String(2))
#     IsoCode3 = Column(String(3))
#     # Geom = Column(LargeBinary)  
#     CreatedAt = Column(DateTime, default=datetime.utcnow)
#     CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
#     UpdatedAt = Column(DateTime)
#     UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))

# -------------------------
# Countries Table
# -------------------------
class Country(Base):
    __tablename__ = "COUNTRIES_LIST"
    __table_args__ = {"schema": "dbo"}

    OBJECTID = Column(Integer, primary_key=True, index=True)
    CountryCode = Column(String)
    CountryName = Column(String)
    CountryNameAr = Column(Unicode(200))
    Latitude = Column(Float)
    Longitude = Column(Float)
    Geom = Column(String) 


class City(Base):
    __tablename__ = "Cities"
    __table_args__ = {"schema": "Website"}

    CityID = Column(Integer, primary_key=True)
    NameEn = Column(String(100), nullable=False)
    NameAr = Column(Unicode(255), nullable=False)
    CountryID = Column(Integer, ForeignKey("dbo.COUNTRIES_LIST.OBJECTID"), nullable=False)
    # Geom = Column(LargeBinary)  
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedAt = Column(DateTime)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))

    country = relationship("Country")


# lookups for categoty for the FAQ 
class FAQCategory(Base):
    __tablename__ = "FAQCategories"
    __table_args__ = {"schema": "Website"}

    CategoryID = Column(Integer, primary_key=True, index=True)
    NameEn = Column(String(100), nullable=False)
    NameAr = Column(Unicode(255), nullable=False)
    IsDelete = Column(Boolean, nullable=False, default=False)


# -------------------------
# Survey Lookups
# -------------------------
class SurveyQuestionCategory(Base):
    __tablename__ = "QuestionCategory"
    __table_args__ = {"schema": "Survey"}

    Id = Column(Integer, primary_key=True)
    Category = Column(String(50))
    Category_Ar = Column(Unicode(50))
    CreatedAt = Column(DateTime)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedAt = Column(DateTime)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    IsDeleted = Column(Boolean, default=False)


    # ✅ Relationship back to questions
    questions = relationship("UsersFeedbackQuestion", back_populates="category")
    
    
    

class SurveyTypeOfQuestion(Base):
    __tablename__ = "TypeOfQuestion"
    __table_args__ = {"schema": "Survey"}

    Id = Column(Integer, primary_key=True)
    TypeOfQuestion = Column(String(50))
    CreatedAt = Column(DateTime)
    CreatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    UpdatedAt = Column(DateTime)
    UpdatedByUserID = Column(Integer, ForeignKey("Website.Users.UserID"))
    IsDeleted = Column(Boolean, default=False)
    
    
    # ✅ Relationship back to questions
    questions = relationship("UsersFeedbackQuestion", back_populates="type")
    
    
    
# -------------------------
# Requests Lookups
# -------------------------


# table for categry for requests 
class Category(Base):
    __tablename__ = "Category"
    __table_args__ = {"schema": "Requests"}

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(100), nullable=False)
    Name_Ar = Column(Unicode(100), nullable=False)
    CreatedAt = Column(DateTime)
    IsDeleted = Column(Boolean, default=False)



# the category for data user want to download
class RequestInformation(Base):
    __tablename__ = "RequestInformation"
    __table_args__ = {"schema": "Requests"}

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(200), nullable=False)
    Name_Ar = Column(Unicode(200), nullable=False)
    CreatedAt = Column(DateTime)
    IsDeleted = Column(Boolean, default=False)




# formats type for the data that user want to download
class Format(Base):
    __tablename__ = "Format"
    __table_args__ = {"schema": "Requests"}

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(150), nullable=False)
    Type = Column(String(150), nullable=False)
    CreatedAt = Column(DateTime)
    IsDeleted = Column(Boolean, default=False)



# type for the projection for the user want to download
class Projection(Base):
    __tablename__ = "Projection"
    __table_args__ = {"schema": "Requests"}

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(100), nullable=False)
    CreatedAt = Column(DateTime)




#the status of request
class Status(Base):
    __tablename__ = "Status"
    __table_args__ = {"schema": "Requests"}

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(50), nullable=False)
    Name_Ar = Column(String(50))
    CreatedAt = Column(DateTime)
    
    
    
    
    
#the screens that the user choice on the  request
class ComplaintScreen(Base):
    __tablename__ = "ComplaintScreen"
    __table_args__ = {"schema": "Requests"}

    Id = Column(Integer, primary_key=True, index=True)
    Name = Column(String(150), nullable=False)
    Name_Ar = Column(String(150), nullable=False)
    CreatedAt = Column(DateTime)
    IsDeleted = Column(Boolean, default=False)