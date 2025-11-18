# app/routers/auth.py
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from app.models.users import User
from app.schemas.users import UserCreate, UserLogin
from app.auth.jwt_handler import create_access_token
from app.auth.jwt_bearer import ALGORITHM, SECRET_KEY
from app.utils.response import success_response, error_response
from app.database import get_db
from app.utils.email import send_email
from app.auth.tokens import create_verification_token, verify_verification_token
import jwt
from app.models.lookups import  UserTitle, OrganizationType, Country, City
from datetime import datetime
from app.utils.utils import get_optional_user
from app.models.role_feature import Role
import os
from dotenv import load_dotenv

load_dotenv()


router = APIRouter(prefix="/auth", tags=["Auth"])

#load the base URL for the front end application
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL")


# ✅ Lookups endpoint for user registration
@router.get("/lookups")
def get_registration_lookups(db: Session = Depends(get_db)):
    """
    Returns lookup data used for registration forms
    such as available roles or other dropdowns.
    """
    try:
        # Example: Fetch only roles allowed for public registration
        roles = db.query(Role).filter(Role.RoleID != 1)
        UserTitles = db.query(UserTitle).all()
        OrganizationTypes = db.query(OrganizationType).all()
        # Exclude Geom column (geometry type) which pyodbc doesn't support
        Countries = db.query(
            Country.OBJECTID.label("id"),
            Country.CountryCode.label("code"),
            Country.CountryName.label("name")
        ).all()
        Cities = db.query(City).all()

        roles_data = [
            {"role_id": role.RoleID, "NameEn": role.NameEn , "NameAr": role.NameAr}
            for role in roles
        ]

        # You can add other lookup sets later, e.g.:
        titles =  [{"id": title.Id, "title": title.Title} for title in UserTitles]
        organizations =  [{"id": org.OrganizationTypeID, "NameEn": org.NameEn,"NameAr":org.NameAr} for org in OrganizationTypes]
        # Access labeled columns by attribute name
        countries = [{"id": country.id, "NameEn": country.name, "CountryCode": country.code} for country in Countries]
        cities = [{"id": city.CityID, "NameEn": city.NameEn,"NameAr":city.NameAr} for city in Cities]
        # departments = [{"id": 1, "name": "IT"}, {"id": 2, "name": "HR"}]

        lookups = {
            "roles": roles_data,
            "titles": titles,
            "Organizations": organizations,
            "countries": countries,
            "cities": cities,
            # "departments": departments,
        }

        return success_response("Lookups loaded successfully", lookups)

    except Exception as e:
        return error_response(f"Error fetching lookup data: {str(e)}", "LOOKUP_ERROR")



# this is endpoint for Registering a new Account (Admin or Self Registration)
@router.post("/register")
def register(
    user: UserCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)  # <-- allow admin or none
):
    # Check for existing user
    existing_user = db.query(User).filter(User.Email == user.Email).first()
    if existing_user:
        return error_response("Email already registered", "EMAIL_EXISTS")

    # Hash password
    hashed_password = bcrypt.hash(user.Password)

    # Create new user object
    new_user = User(
        FirstName=user.FirstName,
        LastName=user.LastName,
        OrganizationTypeID=user.OrganizationTypeID,
        OrganizationName=user.OrganizationName,
        Department=user.Department,
        JobTitle=user.JobTitle,
        CityID=user.CityID,
        CountryID=user.CountryID,
        PhoneNumber=user.PhoneNumber,
        TitleId=user.TitleId,
        Email=user.Email,
        DateOfBirth=user.DateOfBirth,
        UserType=user.UserType,
        PasswordHash=hashed_password,
        RoleID=user.RoleID or 2,
        IsApproved=False,
        EmailVerified=False,
        IsActive=False,
        CreatedAt=datetime.now(),
        CreatedByUserID=current_user.UserID if current_user else None,  # 👈 NEW LINE
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate email verification link
    token = create_verification_token(user.Email)
    verify_url = f"{FRONTEND_BASE_URL}/auth/verify-email?token={token}"

    email_body = f"""
    <h3>Hello {user.FirstName},</h3>
    <p>Welcome to NGD! Please verify your email by clicking the link below:</p>
    <a href="{verify_url}">Verify My Email</a>
    <p>This link will expire in 1 hour.</p>
    """

    # Send verification email in background
    background_tasks.add_task(send_email, "Verify your NGD account", email_body, user.Email)

    return success_response(
        "Registration successful. Please verify your email.",
        {"email": user.Email, "created_by": current_user.UserID if current_user else None}
    )




# this endpoint for verify the email
@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    email = verify_verification_token(token)
    if not email:
        return error_response("Invalid or expired token", "TOKEN_INVALID")

    user = db.query(User).filter(User.Email == email).first()
    if not user:
        return error_response("User not found", "USER_NOT_FOUND")

    user.EmailVerified = True
    db.commit()

    return success_response("Email verified successfully. Waiting for admin approval.")


# this endpoint for Login to the System
@router.post("/login")
def login(user: UserLogin, request: Request, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.Email == user.Email).first()

    # 1️⃣ Check if user exists and password matches
    if not db_user or not bcrypt.verify(user.Password, db_user.PasswordHash):
        return error_response("Invalid email or password", "INVALID_CREDENTIALS")

    # 2️⃣ Check if user is approved
    if not getattr(db_user, "IsApproved", True):  # adjust field name if different
        return error_response("Your account is not yet approved by the administrator", "ACCOUNT_NOT_APPROVED")

    # 3️⃣ Check if user is active
    if not getattr(db_user, "IsActive", True):  # adjust field name if different
        return error_response("Your account is deactivated. Please contact support.", "ACCOUNT_INACTIVE")

    # 4️⃣ Build photo URL
    base_url = str(request.base_url).rstrip("/")
    photo_relative_path = db_user.PhotoPath or ""
    photo_url = f"{base_url}/{photo_relative_path.lstrip('/')}" if photo_relative_path else None

    # 5️⃣ Create JWT token
    token = create_access_token(
        data={
            "sub": db_user.Email,
            "user_id": db_user.UserID,
            "role_id": db_user.RoleID,
            "first_name": db_user.FirstName,
            "last_name": db_user.LastName,
            "photo_url": photo_url,
        }
    )

    # 6️⃣ Return success response
    return success_response("Login successful", {"access_token": token})



# for forget and reset password for user
@router.post("/forgot-password")
def forgot_password(request: Request, email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.Email == email).first()
    if not user:
        return error_response("Email not found", "EMAIL_NOT_FOUND")

    token = create_verification_token(email)
    reset_url = f"{FRONTEND_BASE_URL}/auth/reset-password?token={token}"
    email_body = f"""
    <h3>Password Reset Request</h3>
    <p>Click below to reset your password:</p>
    <a href="{reset_url}">Reset Password</a>
    <p>This link will expire in 1 hour.</p>
    """
    background_tasks.add_task(send_email, "Password Reset - NGD", email_body, email)

    return success_response("Password reset email sent successfully.", {"email": email})


@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    email = verify_verification_token(token)
    if not email:
        return error_response("Invalid or expired token", "TOKEN_INVALID")

    user = db.query(User).filter(User.Email == email).first()
    if not user:
        return error_response("User not found", "USER_NOT_FOUND")

    user.PasswordHash = bcrypt.hash(new_password)
    db.commit()

    return success_response("Password has been reset successfully.")