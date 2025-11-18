# routers/contact_us.py
import os, shutil
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from urllib.parse import quote
from typing import Optional
from app.database import get_db
from app.models.contact_us import ContactUs, ContactUsResponse
from app.models.users import User
from app.utils.email import send_email, send_email_with_attachment , CONTACT_DIR, SYSTEM_EMAIL
from app.utils.response import success_response, error_response
from app.utils.utils import get_optional_user, require_admin  # if you already have it, otherwise see below   # 👈 import config here
from app.utils.paths import static_path



router = APIRouter(prefix="/contact-us", tags=["ContactUs"])




def build_file_url(request: Request, relative_path: Optional[str]) -> Optional[str]:
    if not relative_path:
        return None
    base = str(request.base_url).rstrip("/")
    # relative_path expected like "contact/20250928_file.jpg"
    return f"{base}/static/{quote(relative_path)}"

# ---------- Public: create contact (multipart/form-data) ----------
@router.post("/", response_model=dict)
def create_contact(
    request: Request,
    background_tasks: BackgroundTasks,
    FirstName: Optional[str] = Form(None),
    LastName: Optional[str] = Form(None),
    Subject: Optional[str] = Form(None),
    Body: Optional[str] = Form(None),
    Email: Optional[str] = Form(None),
    PhoneNumber: Optional[str] = Form(None),
    attach: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)  # optional auth
):
    # --- 1) Handle file ---
    attach_rel = None
    if attach:
        os.makedirs(CONTACT_DIR, exist_ok=True)
        orig = os.path.basename(attach.filename)
        safe_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{orig.replace(' ', '_')}"
        save_path = os.path.join(CONTACT_DIR, safe_name)
        with open(save_path, "wb") as buff:
            shutil.copyfileobj(attach.file, buff)
        attach_rel = f"contact/{safe_name}"

    # --- 2) Determine email and user_id ---
    if current_user:
        user_email = current_user.Email
        PhoneNumber = current_user.PhoneNumber
        FirstName = current_user.FirstName
        LastName = current_user.LastName
        user_id = current_user.UserID
    else:
        user_email = Email
        user_id = None

    # --- 3) Save ContactUs ---
    new_contact = ContactUs(
        FirstName=FirstName,
        LastName=LastName,
        Subject=Subject,
        Body=Body,
        AttachPath=attach_rel,
        UserID=user_id,
        Email=user_email,
        PhoneNumber=PhoneNumber,
        ReplyStatus=False
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    # --- 4) Email to admin/system ---
    admin_subject = f"New ContactUs: {Subject or 'No subject'}"
    admin_body = f"""
    <p>A new contact form has been submitted.</p>
    <ul>
        <li><strong>Name:</strong>  {FirstName or ''}</li>
        <li><strong>Email:</strong> {user_email or 'N/A'}</li>
        <li><strong>Phone:</strong> {PhoneNumber or 'N/A'}</li>
        <li><strong>Subject:</strong> {Subject or 'N/A'}</li>
        <li><strong>Message:</strong> {Body or 'N/A'}</li>
        <li><strong>ContactID:</strong> {new_contact.ContactID}</li>
    </ul>
    """
    if attach_rel:
        background_tasks.add_task(send_email_with_attachment, admin_subject, admin_body, SYSTEM_EMAIL, attach_rel)
    else:
        background_tasks.add_task(send_email, admin_subject, admin_body, SYSTEM_EMAIL)

    # --- 5) Email to user ---
    if user_email:
        user_subject = "NGD - We received your message"
        user_body = f"""
        <h4>Dear {FirstName or 'User'},</h4>
        <p>We received your message (<strong>ID {new_contact.ContactID}</strong>).</p>
        <p>We will reply to you soon.</p>
        <p>Thanks, NGD</p>
        """
        background_tasks.add_task(send_email, user_subject, user_body, user_email)

    return success_response("Contact form submitted", {
        "ContactID": new_contact.ContactID,
        "Email Send Successfully to " : user_email , 
        "AttachPath": build_file_url(request, new_contact.AttachPath)
    })



@router.get("/admin", response_model=dict)
def list_contacts_admin(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    request: Request = None
):
    contacts = db.query(ContactUs).order_by(ContactUs.CreatedAt.desc()).all()
    out = []
    for c in contacts:
        out.append({
            "ContactID": c.ContactID,
            "FirstName": c.FirstName,
            "LastName": c.LastName,
            "Subject": c.Subject,
            "Body": c.Body,
            "Email": c.Email,
            "PhoneNumber": c.PhoneNumber,
            "AttachPath": build_file_url(request, c.AttachPath) if request else c.AttachPath,
            "ReplyStatus": c.ReplyStatus,
            "UserId": c.UserID,
            "CreatedAt": c.CreatedAt
        })
    return success_response("Contacts fetched", {"contacts": out})




@router.get("/admin/{contact_id}", response_model=dict)
def get_contact_details_admin(
    contact_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
    request: Request = None
):
    contact = db.query(ContactUs).filter(ContactUs.ContactID == contact_id).first()
    if not contact:
        return error_response("Contact not found", "CONTACT_NOT_FOUND")

    # Get all replies for this contact
    replies = db.query(ContactUsResponse).filter(ContactUsResponse.ContactID == contact.ContactID)\
        .order_by(ContactUsResponse.CreatedAt.asc()).all()
    
    reply_list = []
    for r in replies:
        reply_list.append({
            "ResponseID": r.ResponseID,
            "Subject": r.Subject,
            "Body": r.Body,
            "AttachPath": build_file_url(request, r.AttachPath) if r.AttachPath else None,
            "CreatedByUserID": r.CreatedByUserID,
            "CreatedAt": r.CreatedAt
        })

    contact_data = {
        "ContactID": contact.ContactID,
        "FirstName": contact.FirstName,
        "LastName": contact.LastName,
        "Subject": contact.Subject,
        "Body": contact.Body,
        "Email": contact.Email,
        "PhoneNumber": contact.PhoneNumber,
        "AttachPath": build_file_url(request, contact.AttachPath) if contact.AttachPath else None,
        "ReplyStatus": contact.ReplyStatus,
        "UserId": contact.UserID,
        "CreatedAt": contact.CreatedAt,
        "Replies": reply_list
    }

    return success_response("Contact details fetched", contact_data)


@router.post("/admin/{contact_id}/reply", response_model=dict)
def reply_contact_admin(
    contact_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    Subject: Optional[str] = Form(None),
    Body: Optional[str] = Form(None),
    attach: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    # 1️⃣ Fetch contact
    contact = db.query(ContactUs).filter(ContactUs.ContactID == contact_id).first()
    if not contact:
        return error_response("Contact not found", "CONTACT_NOT_FOUND")

    # 2️⃣ Handle attachment
    attach_rel = None
    if attach:
        reply_dir = static_path("contact", "reply", ensure=True)
        orig = os.path.basename(attach.filename)
        safe_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{orig.replace(' ', '_')}"
        save_path = os.path.join(reply_dir, safe_name)
        with open(save_path, "wb") as buff:
            shutil.copyfileobj(attach.file, buff)
        attach_rel = f"contact/reply/{safe_name}"

    # 3️⃣ Create reply record
    new_reply = ContactUsResponse(
        ContactID=contact.ContactID,
        Subject=Subject,
        Body=Body,
        AttachPath=attach_rel,
        CreatedByUserID=admin.UserID,
        CreatedAt=datetime.utcnow()
    )
    db.add(new_reply)

    # 4️⃣ Update contact status
    contact.ReplyStatus = True
    db.commit()
    db.refresh(new_reply)

    # 5️⃣ Send email to user (if exists)
    if contact.Email:
        reply_subject = Subject or f"Reply to your Contact Form #{contact.ContactID}"
        reply_body = f"""
        <p>Dear {contact.FirstName or 'User'},</p>
        <p>We have replied to your Contact Form #{contact.ContactID}.</p>
        <p>{Body or ''}</p>
        """

        if attach_rel:
            background_tasks.add_task(
                send_email_with_attachment,
                reply_subject,
                reply_body,
                contact.Email,
                attach_rel
            )
        else:
            background_tasks.add_task(send_email, reply_subject, reply_body, contact.Email)

    # 6️⃣ Return response
    return success_response("Reply sent successfully", {
        "reply_id": new_reply.ResponseID,
        "attach_url": build_file_url(request, attach_rel)
    })
