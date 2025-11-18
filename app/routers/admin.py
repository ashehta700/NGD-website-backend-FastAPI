from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import os
import shutil

from app.database import get_db
from app.auth.jwt_bearer import JWTBearer
from app.utils.response import success_response, error_response
from app.utils.email import send_reply_email, send_email_with_attachment , ADMIN_UPLOAD_DIR
from app.models.users import User
from app.models.lookups import Category ,Status ,ComplaintScreen , RequestInformation , Format , Projection
from app.models.requests import Request, Reply , Request_RequestInformation ,Request_Format  # ✅ import your models

router = APIRouter(prefix="/admin", tags=["Admin"])

# ------------------------
# Auth & Role Dependencies
# ------------------------

def get_current_user(payload: dict = Depends(JWTBearer()), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.UserID == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.RoleID != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return user





# ------------------------
# Assign role to request
# ------------------------
@router.post("/assign_request")
def assign_request(
    request_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    req = db.query(Request).filter(Request.Id == request_id).first()
    if not req:
        return error_response("Request not found", "REQUEST_NOT_FOUND")
    req.AssignedRoleId = role_id
    db.commit()
    return success_response("Request assigned successfully", {"request_id": req.Id})


# ------------------------
# List all requests (Admin only) - updated
# ------------------------
@router.get("/requests")
def list_requests(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    # Join with Status, Category, and User to get all needed info
    requests = (
        db.query(Request, Status, Category, User)
        .join(Status, Request.StatusId == Status.Id, isouter=True)
        .join(Category, Request.CategoryId == Category.Id, isouter=True)
        .join(User, Request.UserId == User.UserID, isouter=True)
        .all()
    )

    results = []
    for req, status, category, user in requests:
        results.append({
            "id": req.Id,
            "number": req.RequestNumber,
            "created_at": req.CreatedAt,
            "status_name_en": status.Name if status else None,
            "status_name_ar": status.Name_Ar if status else None,
            "type_name_en": category.Name if category else None,
            "type_name_ar": category.Name_Ar if category else None,
            "user_email": user.Email if user else None,
            "subject": req.Subject,
            "body": req.Body
        })

    return success_response("Requests fetched", {"requests": results})




# ------------------------
# Get Only one request Details (Admin only)
# ------------------------
# ------------------------
# Get Only one request Details (Admin only)
# ------------------------
@router.get("/request-details/")
def get_request_details(
    request_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    req = db.query(Request).filter(Request.Id == request_id).first()
    if not req:
        return error_response("Request not found", "REQUEST_NOT_FOUND")

    # Fetch user
    user = db.query(User).filter(User.UserID == req.UserId).first() if req.UserId else None

    # Fetch lookups for category, status, complaint screen
    category = db.query(Category).filter(Category.Id == req.CategoryId).first() if req.CategoryId else None
    status = db.query(Status).filter(Status.Id == req.StatusId).first() if req.StatusId else None
    complaint_screen = (
        db.query(ComplaintScreen).filter(ComplaintScreen.Id == req.ComplaintScreenId).first()
        if req.ComplaintScreenId else None
    )

    # Fetch many-to-many relations
    request_info = (
        db.query(RequestInformation)
        .join(Request_RequestInformation, Request_RequestInformation.c.RequestInformationId == RequestInformation.Id)
        .filter(Request_RequestInformation.c.RequestId == req.Id)
        .all()
    )
    formats = (
        db.query(Format)
        .join(Request_Format, Request_Format.c.FormatId == Format.Id)
        .filter(Request_Format.c.RequestId == req.Id)
        .all()
    )

    # Fetch replies
    replies = db.query(Reply).filter(Reply.RequestId == req.Id, Reply.IsDeleted == False).all()

    # Initialize RequestData fields if category is RequestData
    request_data_details = {}
    if category and category.Id == 8:  # RequestData
        from app.models.requests import RequestData
        rd = db.query(RequestData).filter(RequestData.RequestId == req.Id).first()
        if rd:
            projection = db.query(Projection).filter(Projection.Id == rd.ProjectionId).first() if rd.ProjectionId else None
            request_data_details = {
                "prospective_name": rd.ProspectiveName,
                "coordinates": {
                    "top_left": rd.Coordinate_TopLeft,
                    "bottom_right": rd.Coordinate_BottomRight
                } if rd.Coordinate_TopLeft or rd.Coordinate_BottomRight else {},
                "projection": projection.Name if projection else None,
                "other_specification": rd.OtherSpecification,
                "other_format": rd.OtherFormat,
                "intended_purpose": rd.IntendedPurpose,
                "requirements_details": rd.RequirementsDetails,
                "created_at": rd.CreatedAt,
            }

    # Build response
    details = {
        "id": req.Id,
        "number": req.RequestNumber,
        "status": {"Name_ar": status.Name_Ar, "Name_En": status.Name} if status else {},
        "type": {"Name_ar": category.Name_Ar, "Name_En": category.Name} if category else {},
        "user_email": user.Email if user else None,
        "subject": req.Subject,
        "body": req.Body,
        "complaint_screen": {"Name_ar": complaint_screen.Name_Ar, "Name_En": complaint_screen.Name} if complaint_screen else {},
        "assigned_role_id": req.AssignedRoleId,
        "attach_path": req.AttachPath,
        "created_at": req.CreatedAt,
        "created_by": req.CreatedByUserID,
        "updated_at": req.UpdatedAt,
        "updated_by": req.UpdatedByUserID,
        # Many-to-many
        "request_information": [{"Name_Ar": ri.Name_Ar, "name": ri.Name} for ri in request_info] if request_info else [],
        "formats": [{"name": f.Name} for f in formats] if formats else [],
        # Replies
        "replies": [
            {
                "id": reply.Id,
                "subject": reply.Subject,
                "body": reply.Body,
                "attachment_path": reply.AttachmentPath,
                "created_at": reply.CreatedAt,
                "created_by": reply.CreatedByUserID,
                "responder_user_id": reply.ResponderUserId,
            }
            for reply in replies
        ] if replies else [],
        # Include RequestData fields if any
        **request_data_details
    }

    return success_response("Request Details", {"request": details})



# ------------------------
# List requests assigned to current admin’s role
# ------------------------
@router.get("/assigned_requests")
def assigned_requests(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get all requests assigned to the user role
    requests = (
        db.query(Request,Status, Category, User)
        .filter(Request.AssignedRoleId == user.RoleID)
        .join(Status, Request.StatusId == Status.Id, isouter=True)
        .join(Category, Request.CategoryId == Category.Id, isouter=True)
        .join(User, Request.UserId == User.UserID, isouter=True)
        .all()
    )

    results = []
    for req, status, category, user in requests:
        results.append({
            "id": req.Id,
            "number": req.RequestNumber,
            "created_at": req.CreatedAt,
            "status_name_en": status.Name if status else None,
            "status_name_ar": status.Name_Ar if status else None,
            "type_name_en": category.Name if category else None,
            "type_name_ar": category.Name_Ar if category else None,
            "user_email": user.Email if user else None,
            "subject": req.Subject,
            "body": req.Body
        })

    return success_response("Assigned requests fetched", {"requests": results})


# ------------------------
# Admin reply to a request (with optional attachment)
# ------------------------
@router.post("/reply")
def admin_reply(
    request_id: int,
    status_id: int,  # 8 = in-progress, 9 = completed, etc.
    subject: str = None,
    body: str = None,
    attachment: UploadFile = File(None),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    req = db.query(Request).filter(Request.Id == request_id).first()
    if not req:
        return error_response("Request not found", "REQUEST_NOT_FOUND")

    # --- 1) Save attachment if exists ---
    attachment_path = None
    if attachment:
        orig_name = os.path.basename(attachment.filename)
        filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{orig_name.replace(' ', '_')}"
        attachment_path = os.path.join(ADMIN_UPLOAD_DIR, filename)
        with open(attachment_path, "wb") as buffer:
            shutil.copyfileobj(attachment.file, buffer)
        attachment_path = f"requests/reply/{filename}"   

    # --- 2) Create Reply record ---
    new_reply = Reply(
        RequestId=request_id,
        Subject=subject,
        Body=body,
        AttachmentPath=attachment_path,
        ResponderUserId=user.UserID,
        CreatedAt=datetime.utcnow(),
        CreatedByUserID=user.UserID
    )
    db.add(new_reply)

    # --- 3) Update request status ---
    req.StatusId = status_id
    req.UpdatedAt = datetime.utcnow()
    req.UpdatedByUserID = user.UserID

    db.commit()
    db.refresh(new_reply)
    db.refresh(req)

    # --- 4) Send email to request owner ---
    request_owner = db.query(User).filter(User.UserID == req.UserId).first()
    if not request_owner or not request_owner.Email:
        return error_response("Request owner email not found", "USER_EMAIL_NOT_FOUND")

    user_email = request_owner.Email

    email_subject = f"NGD - Response to your request {req.RequestNumber}"
    email_body = f"""
    <h4>Dear {request_owner.FirstName},</h4>
    <p>Your request <b>{req.RequestNumber}</b> has received a reply:</p>
    <p>{body or 'No message provided'}</p>
    <p>Thank you, NGD Team</p>
    """

    if attachment_path:
        # Send with attachment
        background_tasks.add_task(send_email_with_attachment, email_subject, email_body, user_email, attachment_path)
    else:
        # Send without attachment
        background_tasks.add_task(send_email, email_subject, email_body, user_email)

    return success_response(
        "Reply sent successfully",
        {"reply_id": new_reply.Id, "new_status": status_id, "request_id": req.Id}
    )

