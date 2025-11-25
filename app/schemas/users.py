# Updated schemas/users.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class UserCreate(BaseModel):
    TitleId: Optional[int] = None
    FirstName: str
    LastName: str
    OrganizationTypeID: Optional[int] = None
    OrganizationName: Optional[str] = None
    Department: Optional[str] = None
    JobTitle: Optional[str] = None
    CityID: Optional[int] = None
    CountryID: Optional[int] = None
    PhoneNumber: Optional[str] = None
    Email: EmailStr
    Password: str
    RoleID: Optional[int] = 2  # Default to user if not admin
    UserType: Optional[str] = None
    PhotoPath: Optional[str] = None
    DateOfBirth: Optional[date] = None


class UserLogin(BaseModel):
    Email: EmailStr
    Password: str


class UserResponse(BaseModel):
    UserID: Optional[int]
    TitleId: Optional[int]
    FirstName: Optional[str]
    LastName: Optional[str]
    OrganizationTypeID: Optional[int]
    OrganizationName: Optional[str]
    Department: Optional[str]
    JobTitle: Optional[str]
    CityID: Optional[int]
    CountryID: Optional[int]
    PhoneNumber: Optional[str]
    Email: EmailStr
    RoleID: Optional[int]
    UserType: Optional[str]
    PhotoPath: Optional[str]
    PhotoURL: Optional[str] = None
    DateOfBirth: Optional[date]
    IsApproved: Optional[bool]
    EmailVerified: Optional[bool]
    IsActive: Optional[bool]

    class Config:
        orm_mode = True



class UserUpdate(BaseModel):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    TitleId: Optional[int] = None
    OrganizationTypeID: Optional[int] = None
    OrganizationName: Optional[str] = None
    Department: Optional[str] = None
    JobTitle: Optional[str] = None
    CityID: Optional[int] = None
    CountryID: Optional[int] = None
    PhoneNumber: Optional[str] = None
    Email: Optional[str] = None
    RoleID: Optional[int] = None
    UserType: Optional[str] = None
    DateOfBirth: Optional[date] = None
        
# Change password 
class ResetPasswordRequest(BaseModel):
    new_password: str
    target_user_id: Optional[int] = None
    

class UserStatusUpdate(BaseModel):
    is_active: bool
    