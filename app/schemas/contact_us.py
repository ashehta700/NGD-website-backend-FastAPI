# schemas/contact_us.py
from pydantic import BaseModel
from typing import Optional


class ContactUsCreate(BaseModel):
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Subject: Optional[str] = None
    Body: Optional[str] = None
    AttachPath: Optional[str] = None
    UserID: Optional[int] = None   # ✅ allow null instead of forcing int
    Email: Optional[str] = None
    PhoneNumber: Optional[str] = None


class ContactUsReplyCreate(BaseModel):
    Subject: Optional[str]
    Body: Optional[str]
    AttachPath: Optional[str]
    CreatedByUserID: int
