from app.auth.jwt_bearer import JWTBearer
from app.database import get_db
from app.models.users import User
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, Request
from typing import Optional





# this method is used for get the current user that is login 
def get_current_user(payload: dict = Depends(JWTBearer()), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.UserID == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_optional_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """
    Return User if JWT token exists and is valid, otherwise None.
    """
    try:
        payload = JWTBearer()(request)  # manually call JWTBearer
        if payload and "user_id" in payload:
            user = db.query(User).filter(User.UserID == payload["user_id"]).first()
            return user
    except:
        pass
    return None

# this is method is used for check the user is Admin or not with Role 1 for Super Admins 
def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.RoleID != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return user


# Helper to resolve identity (user vs visitor)
def _resolve_identity(request: Request, payload: Optional[dict]):
    user_id = None
    visitor_id = None

    if payload and "user_id" in payload:
        user_id = payload["user_id"]
    else:
        visitor_id = request.headers.get("X-Visitor-Id")
        try:
            visitor_id = int(visitor_id) if visitor_id else None
        except ValueError:
            visitor_id = None
    return user_id, visitor_id




# this method is used for making clean text for arabic words that if have any spaces or something like this 
def clean_text(value: str) -> str:
    if not value:
        return value
    # Trim spaces
    cleaned = value.strip()
    # Remove common invisible Unicode spaces
    bad_chars = ["\u00A0", "\u200B", "\u200C", "\u200D", "\u200E", "\u200F", "\u202C", "\uFEFF"]
    for bad in bad_chars:
        cleaned = cleaned.replace(bad, "")
    return cleaned


def extract_email_domain(email: str) -> Optional[str]:
    """
    Return the lower-cased domain part of an email address.
    """
    if not email or "@" not in email:
        return None
    return email.split("@", 1)[1].strip().lower()