from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.utils.response import success_response
from datetime import datetime
from app.schemas.visitors import VisitorCreate
from app.models.visitors import Visitor
import uuid
from app.database import get_db

router = APIRouter(prefix="/track", tags=["Visitors"])


# this endpoint is used for the tracking the user with the session  
@router.post("/auto")
async def auto_track(visitor: VisitorCreate, request: Request, db: Session = Depends(get_db)):
    # Get client IP
    ip_address = request.headers.get("x-forwarded-for")
    if ip_address:
        ip_address = ip_address.split(",")[0]  # first in case of multiple
    else:
        ip_address = request.client.host

    now = datetime.utcnow()

    # Use provided session ID or generate new one
    session_id = visitor.SessionID or str(uuid.uuid4())

    # 🔹 Check if session already exists
    existing_session = db.query(
        Visitor.VisitorID,
        Visitor.VisitAt
    ).filter(
        Visitor.SessionID == session_id
    ).order_by(
        Visitor.VisitAt.desc()
    ).first()

    if existing_session:
        # Session already exists → just update VisitAt
        db.execute(
            text("UPDATE Website.Visitors SET VisitAt = :visit WHERE VisitorID = :vid"),
            {"visit": now, "vid": existing_session.VisitorID}
        )
        db.commit()
        visitor_id = existing_session.VisitorID
    else:
        # 🔹 Create new session
        if visitor.X is not None and visitor.Y is not None:
            geom_wkt = f"POINT({visitor.X} {visitor.Y})"
            stmt = text("""
                INSERT INTO Website.Visitors (IPAddress, Location, X, Y, Geom, VisitAt, SessionID)
                OUTPUT inserted.VisitorID
                VALUES (:ip, :loc, :x, :y, geometry::STGeomFromText(:geom, 4326), :visit, :sess)
            """)
            params = {
                "ip": ip_address,
                "loc": visitor.Location,
                "x": visitor.X,
                "y": visitor.Y,
                "geom": geom_wkt,
                "visit": now,
                "sess": session_id
            }
        else:
            stmt = text("""
                INSERT INTO Website.Visitors (IPAddress, Location, X, Y, Geom, VisitAt, SessionID)
                OUTPUT inserted.VisitorID
                VALUES (:ip, :loc, :x, :y, NULL, :visit, :sess)
            """)
            params = {
                "ip": ip_address,
                "loc": visitor.Location,
                "x": visitor.X,
                "y": visitor.Y,
                "visit": now,
                "sess": session_id
            }

        result = db.execute(stmt, params)
        visitor_id = result.fetchone()[0]
        db.commit()

    return success_response("Visitor tracked", {
        "VisitorID": visitor_id,
        "IPAddress": ip_address,
        "VisitAt": now.isoformat(),
        "SessionID": session_id
    })





    