# app/routers/domains.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional
from app.database import get_db
from app.utils.response import success_response, error_response
from app.utils.utils import get_current_user
from app.models.users import Domain

router = APIRouter(prefix="/domains", tags=["Domains"])


# --------------------------
# 1️⃣ List Domains (All)
# --------------------------
@router.get("/")
def list_domains(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=200),
    search: Optional[str] = Query(None, description="Search by domain name"),
    type: Optional[str] = Query(None, description="accept, refused"),
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.RoleID != 1:
        return error_response("Only admins can view domains", "FORBIDDEN")

    query = db.query(Domain)

    # --- Search ---
    if search:
        like_term = f"%{search}%"
        query = query.filter(Domain.Domain.ilike(like_term))

    # --- Filter by Type ---
    if type:
        query = query.filter(func.lower(Domain.Type) == type.lower())

    total = query.count()
    skip = (page - 1) * limit

    items = (
        query.order_by(Domain.Domain.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    data = {
        "page": page,
        "limit": limit,
        "count": len(items),
        "total": total,
        "domains": [
            {
                "ID": d.Id,
                "Domain": d.Domain,
                "Type": d.Type,
            }
            for d in items
        ],
    }

    return success_response("Domains retrieved successfully", data)


# --------------------------
# 2️⃣ Get Single Domain
# --------------------------
@router.get("/{domain_id}")
def get_domain(domain_id: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    if current.RoleID != 1:
        return error_response("Only admins can view domain", "FORBIDDEN")

    domain = db.query(Domain).filter(Domain.Id == domain_id).first()
    if not domain:
        return error_response("Domain not found", "DOMAIN_NOT_FOUND")

    return success_response(
        "Domain retrieved successfully",
        {
            "ID": domain.Id,
            "Domain": domain.Domain,
            "Type": domain.Type,
        },
    )


# --------------------------
# 3️⃣ Create Domain
# --------------------------
@router.post("/")
def create_domain(
    domain: str = Query(..., description="Domain name"),
    type: str = Query(..., description="accept or refused"),
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.RoleID != 1:
        return error_response("Only admins can create domains", "FORBIDDEN")

    exists = (
        db.query(Domain)
        .filter(func.lower(Domain.Domain) == domain.lower())
        .first()
    )

    if exists:
        return error_response("Domain already exists", "DOMAIN_EXISTS")

    new_domain = Domain(
        Domain=domain.lower(),
        Type=type.lower(),
    )

    db.add(new_domain)
    db.commit()
    db.refresh(new_domain)

    return success_response(
        "Domain created successfully",
        {
            "ID": new_domain.Id,
            "Domain": new_domain.Domain,
            "Type": new_domain.Type,
        },
    )


# --------------------------
# 4️⃣ Update Domain
# --------------------------
@router.put("/{domain_id}")
def update_domain(
    domain_id: int,
    domain: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    current=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current.RoleID != 1:
        return error_response("Only admins can update domains", "FORBIDDEN")

    item = db.query(Domain).filter(Domain.Id == domain_id).first()
    if not item:
        return error_response("Domain not found", "DOMAIN_NOT_FOUND")

    if domain:
        item.Domain = domain.lower()

    if type:
        item.Type = type.lower()

    db.commit()

    return success_response(
        "Domain updated successfully",
        {
            "ID": item.Id,
            "Domain": item.Domain,
            "Type": item.Type,
        },
    )


# --------------------------
# 5️⃣ Delete Domain
# --------------------------
@router.delete("/{domain_id}")
def delete_domain(domain_id: int, current=Depends(get_current_user), db: Session = Depends(get_db)):
    if current.RoleID != 1:
        return error_response("Only admins can delete domains", "FORBIDDEN")

    domain = db.query(Domain).filter(Domain.Id == domain_id).first()
    if not domain:
        return error_response("Domain not found", "DOMAIN_NOT_FOUND")

    db.delete(domain)
    db.commit()

    return success_response("Domain deleted successfully", {"domain_id": domain_id})
