from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.utils.response import success_response 
from datetime import datetime
from app.models.users import User
from app.models.visitors import Visitor
from app.models.dashboard import DownloadRequest 
from app.models.lookups import UserTitle
from app.database import get_db
from sqlalchemy import func

router = APIRouter(prefix="/statistics", tags=["Statistics"])



# get the statistics for the home page like the total numbers of the users or visitors 
@router.get("")
async def get_summary(request: Request, db: Session = Depends(get_db)):
    users_count = db.query(User).count()
    visitors_count = db.query(Visitor).count()
    downloads_count = db.query(DownloadRequest).count()
    requests_count = (
        db.query(func.count(func.distinct(DownloadRequest.ReqNo)))
        .scalar()
    )
    # titles_count = db.query(UserTitle).count()

    data = {
        "total_users": users_count,
        "total_visitors": visitors_count,
        "total_requests": requests_count,
        "total_downloads": downloads_count,
    }

    return success_response("Statistics summary", data)