from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, File, UploadFile ,Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.lookups import Category, Format, Projection, RequestInformation, Status, ComplaintScreen
from app.models.requests import Request
from app.models.users import User
from app.schemas.lookups import CategorySchema, FormatSchema, ProjectionSchema, RequestInformationSchema, StatusSchema, ComplaintScreenSchema
from app.schemas.requests import RequestCreate, RequestResponse, ReplyCreate
from app.utils.response import success_response, error_response
from app.utils.email import send_email , send_request_email, send_reply_email, send_email_with_attachment , REQUEST_DIR, SYSTEM_EMAIL   # 👈 import config
from datetime import datetime
import os
import shutil
from typing import Optional, List
from app.utils.utils import get_current_user
from sqlalchemy import text

router = APIRouter(prefix="/requests", tags=["Requests"])



# Lookup endpoint
@router.get("/lookups", response_model=dict)
def get_lookups(db: Session = Depends(get_db)):
    categories = db.query(Category).filter(Category.IsDeleted==0).all()
    projections = db.query(Projection).all()
    formats = db.query(Format).filter(Format.IsDeleted==0).all()
    request_info = db.query(RequestInformation).filter(RequestInformation.IsDeleted==0).all()
    statuses = db.query(Status).all()
    complaint_screens = db.query(ComplaintScreen).filter(ComplaintScreen.IsDeleted==0).all()

    return success_response("Lookup data fetched", {
        "categories": [CategorySchema.from_orm(c).dict() for c in categories],
        "projections": [ProjectionSchema.from_orm(p).dict() for p in projections],
        "formats": [FormatSchema.from_orm(f).dict() for f in formats],
        "request_information": [RequestInformationSchema.from_orm(r).dict() for r in request_info],
        "statuses": [StatusSchema.from_orm(s).dict() for s in statuses],
        "complaint_screens": [ComplaintScreenSchema.from_orm(cs).dict() for cs in complaint_screens],
    })


# Create request (user) - final version
@router.post("/", response_model=dict)
def create_request(
    background_tasks: BackgroundTasks,
    CategoryId: int = Form(...),
    ComplaintScreenId: Optional[int] = Form(None),
    Subject: Optional[str] = Form(None),
    Body: Optional[str] = Form(None),
    ProspectiveName: Optional[str] = Form(None),
    Coordinate_TopLeft: Optional[str] = Form(None),
    Coordinate_BottomRight: Optional[str] = Form(None),
    ProjectionId: Optional[int] = Form(None),
    OtherSpecification: Optional[str] = Form(None),
    OtherFormat: Optional[str] = Form(None),
    IntendedPurpose: Optional[str] = Form(None),
    RequirementsDetails: Optional[str] = Form(None),
    RequestInformationIds: Optional[str] = Form(None),
    FormatIds: Optional[str] = Form(None),
    attach: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create a new request for logged-in users with RequestData table."""

    # --- 1) Handle attachment ---
    attach_rel = None
    if attach:
        orig_name = os.path.basename(attach.filename)
        safe_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{orig_name.replace(' ', '_')}"
        save_path = os.path.join(REQUEST_DIR, safe_name)
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(attach.file, buffer)
        attach_rel = f"requests/{safe_name}"

    # --- 2) Generate request number ---
    last_request = db.query(Request).order_by(Request.Id.desc()).first()
    next_number = 1 if not last_request else last_request.Id + 1
    request_number = f"RQ-{datetime.now().strftime('%Y%m%d')}-{str(next_number).zfill(4)}"

    # --- 3) Projection validation ---
    if ProjectionId in (0, "0", "", None):
        ProjectionId = None
    elif ProjectionId and not db.query(Projection).filter(Projection.Id == ProjectionId).first():
        raise HTTPException(status_code=400, detail="Invalid ProjectionId")

    # --- 4) Create main request ---
    new_request = Request(
        UserId=user.UserID,
        CategoryId=CategoryId,
        ComplaintScreenId=ComplaintScreenId,
        Subject=Subject,
        Body=Body,
        AssignedRoleId=None,
        RequestNumber=request_number,
        StatusId=7,
        CreatedAt=datetime.utcnow(),
        AttachPath=attach_rel
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    # --- 5) Create RequestData if category is 8 ---
    new_request_data = None
    if CategoryId == 8:
        from app.models.requests import RequestData
        new_request_data = RequestData(
            RequestId=new_request.Id,
            ProspectiveName=ProspectiveName,
            Coordinate_TopLeft=Coordinate_TopLeft,
            Coordinate_BottomRight=Coordinate_BottomRight,
            ProjectionId=ProjectionId,
            OtherSpecification=OtherSpecification,
            OtherFormat=OtherFormat,
            IntendedPurpose=IntendedPurpose,
            RequirementsDetails=RequirementsDetails,
            CreatedAt=datetime.utcnow()
        )
        db.add(new_request_data)
        db.commit()
        db.refresh(new_request_data)

    # --- 6) Many-to-many relationships ---
    def parse_int_list(value: Optional[str]) -> List[int]:
        if not value:
            return []
        return [int(v.strip()) for v in value.split(",") if v.strip().isdigit()]


    # RequestInformation M2M
    info_ids = parse_int_list(RequestInformationIds)
    if info_ids:
        for info_id in info_ids:
            db.execute(
                text("INSERT INTO [Requests].[Request_RequestInformation] (RequestId, RequestInformationId) VALUES (:req, :info)"),
                {"req": new_request.Id, "info": info_id}
            )

    # Format M2M
    format_ids = parse_int_list(FormatIds)
    if format_ids:
        for format_id in format_ids:
            db.execute(
                text("INSERT INTO [Requests].[Request_Format] (RequestId, FormatId) VALUES (:req, :fmt)"),
                {"req": new_request.Id, "fmt": format_id}
            )

    db.commit()

    # --- 7) Emails ---
    category = db.query(Category).filter(Category.Id == CategoryId).first()
    category_name = category.Name if category else "Unknown Category"

    admin_subject = f"New Request {request_number} - {category_name}"
    admin_body = f"""
    <p>A new request has been submitted.</p>
    <ul>
        <li><strong>User:</strong> {user.FirstName} ({user.Email})</li>
        <li><strong>Subject:</strong> {Subject or 'N/A'}</li>
        <li><strong>Body:</strong> {Body or 'N/A'}</li>
        <li><strong>Category:</strong> {category_name}</li>
        <li><strong>RequestNumber:</strong> {request_number}</li>
    </ul>
    """
    if attach_rel:
        background_tasks.add_task(send_email_with_attachment, admin_subject, admin_body, SYSTEM_EMAIL, attach_rel)
    else:
        background_tasks.add_task(send_email, admin_subject, admin_body, SYSTEM_EMAIL)

    user_subject = f"NGD - Request {request_number} received"
    user_body = f"""
    <h4>Dear {user.FirstName},</h4>
    <p>Your request has been received successfully.</p>
    <p><strong>Request Number:</strong> {request_number}</p>
    <p>Category: {category_name}</p>
    <p>We will contact you soon.</p>
    <p>Thanks, NGD</p>
    """
    background_tasks.add_task(send_email, user_subject, user_body, user.Email)

    return success_response(
        "Request created successfully",
        {
            "request_id": new_request.Id,
            "request_number": request_number,
            "AttachPath": attach_rel
        }
    )

