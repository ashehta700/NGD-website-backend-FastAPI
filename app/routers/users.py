from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi import APIRouter, Depends, HTTPException, Path, Form, File, UploadFile, Body, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.users import User
from app.schemas.users import UserResponse, UserCreate, UserUpdate, ResetPasswordRequest
from app.auth.jwt_bearer import JWTBearer
from passlib.context import CryptContext
from typing import List, Optional
from datetime import datetime
import os
from app.utils.response import success_response, error_response
from app.database import get_db
from app.utils.utils import get_current_user
from app.auth.tokens import create_verification_token ,  verify_verification_token
from app.utils.email import send_email
from app.utils.paths import static_path

router = APIRouter(prefix="/users", tags=["Users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")







# @router.get("/getcount")
# def get_user_count( db: Session = Depends(get_db)):
#     user = db.query(User).count()
#     return success_response("User count retrieved successfully", {"user_count": user})





#List all users for only super admin user
@router.get("/", dependencies=[Depends(JWTBearer())])
def get_users(request: Request, current=Depends(get_current_user), db: Session = Depends(get_db)):
    if current.RoleID != 1:
        return error_response("Only admins can view all users", "FORBIDDEN")
    
    users = db.query(User).filter(User.IsDeleted == False).all()
    results = []
    for user in users:
        user_dict = user.__dict__.copy()
        user_dict.pop("PasswordHash", None)
        if user.PhotoPath:
            user_dict["PhotoURL"] = f"{request.base_url}static/uploads/{user.PhotoPath.split('/')[-1]}"
        results.append(user_dict)

    return success_response("Users retrieved successfully", results)



# get only the details for user id  for super admin user only with role id 1
@router.get("/{user_id}")
def get_user(request: Request, user_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)):
    user = db.query(User).filter(User.UserID == user_id).first()
    if not user:
        return error_response("User not found", "USER_NOT_FOUND")

    if current.RoleID != 1:
        return error_response("Only admins can view user details", "FORBIDDEN")

    user_dict = user.__dict__.copy()
    user_dict.pop("PasswordHash", None)
    if user.PhotoPath:
        user_dict["PhotoURL"] = f"{request.base_url}{user.PhotoPath}"

    return success_response("User retrieved successfully", user_dict)


# get the details for the current user with token
@router.get("/profile/me")
def get_me(request: Request, current=Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.UserID == current.UserID).first()
    if not user:
        return error_response("User not found", "USER_NOT_FOUND")

    user_dict = user.__dict__.copy()
    user_dict.pop("PasswordHash", None)
    if user.PhotoPath:
        user_dict["PhotoURL"] = f"{request.base_url}static/uploads/{user.PhotoPath.split('/')[-1]}"

    return success_response("Profile retrieved successfully", user_dict)



# edit on each user from the super admin user only with role id 1
@router.put("/{user_id}")
def update_user(user_update: UserUpdate, user_id: int = Path(...), current=Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.UserID == user_id).first()
    if not db_user:
        return error_response("User not found", "USER_NOT_FOUND")

    is_owner = current.UserID == user_id
    is_admin = current.RoleID == 1
    if not (is_owner or is_admin):
        return error_response("Not authorized", "FORBIDDEN")

    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db_user.UpdatedAt = datetime.utcnow()
    db_user.UpdatedByUserID = current.UserID

    db.commit()
    db.refresh(db_user)

    user_dict = db_user.__dict__.copy()
    user_dict.pop("PasswordHash", None)
    user_dict.pop("PhotoURL", None)

    return success_response("User updated successfully", user_dict)





UPLOAD_DIR = static_path("profile_images", ensure=True)


# for upload profile photo for the user
@router.post("/{user_id}/upload-photo")
def upload_profile_photo(user_id: int, file: UploadFile = File(...), current=Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.UserID == user_id).first()
    if not user:
        return error_response("User not found", "USER_NOT_FOUND")

    is_owner = current.UserID == user_id
    is_admin = current.RoleID == 1
    if not is_owner and not is_admin:
        return error_response("Not authorized", "FORBIDDEN")

    ext = file.filename.split(".")[-1]
    filename = f"{user_id}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    user.PhotoPath = f"static/profile_images/{filename}"
    user.UpdatedAt = datetime.utcnow()
    user.UpdatedByUserID = current.UserID
    db.commit()

    return success_response("Photo uploaded successfully", {"photo_url": user.PhotoPath})



# for soft delete the specific user form the admin user only with roled id 1 
@router.delete("/{user_id}")
def delete_user(user_id: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    if current["role_id"] != 1:
        return error_response("Only admins can delete users", "FORBIDDEN")

    user = db.query(User).filter(User.UserID == user_id, User.IsDeleted == False).first()
    if not user:
        return error_response("User not found", "USER_NOT_FOUND")

    user.IsDeleted = True
    db.commit()

    return success_response("User marked as deleted successfully")



# for approve the user and update it forom only super admin user only with role id 1
@router.put("/{user_id}/approve")
def approve_user(user_id: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    if current.RoleID != 1:
        return error_response("Only admins can approve users", "FORBIDDEN")

    user = db.query(User).filter(User.UserID == user_id).first()
    if not user:
        return error_response("User not found", "USER_NOT_FOUND")

    user.IsApproved = True
    user.IsActive = True
    db.commit()

    return success_response(f"User ID {user_id} approved and activated successfully.")
