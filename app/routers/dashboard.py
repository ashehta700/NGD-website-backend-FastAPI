# app/routers/dashboard.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func,and_, extract ,literal_column ,text
from datetime import datetime
from typing import Optional, List
from app.database import get_db
from app.models.visitors import Visitor
from app.models.users import User
from app.models.lookups import Country, OrganizationType
from app.models.dashboard import DownloadRequest, DownloadItem
from app.utils.response import success_response


router = APIRouter(prefix="/dashboard", tags=["Visitors Dashboard"])

# ---------------------------------------------------------
# 0 Visitors filter Options
# ---------------------------------------------------------


@router.get("/visitors/filter-options")
def get_visitor_filter_options(db: Session = Depends(get_db)):
    """
    Returns all countries that have visitor data.
    Used to populate filters in the dashboard UI.
    """
    countries = (
        db.query(
            Country.CountryCode.label("country_code"),
            Country.OBJECTID.label("country_id"),
            Country.CountryName.label("country_name"),
            func.count(Visitor.VisitorID).label("count")
        )
        .join(Country, Visitor.CountryID == Country.OBJECTID)
        .group_by(Country.CountryCode, Country.CountryName,Country.OBJECTID)
        .order_by(Country.CountryName)
        .all()
    )

    data = {
        "countries": [
            {
                "CountryCode": c.country_code,
                "Country_id": c.country_id,
                "CountryName": c.country_name,
                "VisitorCount": c.count
            }
            for c in countries
        ]
    }

    return success_response("Visitor filter options retrieved successfully", data)



# ---------------------------------------------------------
# 1️⃣ Visitors Summary Endpoint
# ---------------------------------------------------------
@router.get("/visitors/summary")
def visitors_summary(db: Session = Depends(get_db)):
    """
    Returns total visitors, per-month counts, and per-country counts.
    """

    year_expr = func.year(Visitor.VisitAt)
    month_expr = func.month(Visitor.VisitAt)

    # --- Visitors per month ---
    per_month = (
        db.query(
            year_expr.label("year"),
            month_expr.label("month"),
            func.count(Visitor.VisitorID).label("count"),
        )
        .group_by(year_expr, month_expr)
        .order_by(year_expr, month_expr)
        .all()
    )

    # --- Visitors per country ---
    per_country = (
        db.query(
            Country.CountryCode.label("country_code"),
            Country.CountryName.label("country_name"),
            func.count(Visitor.VisitorID).label("count"),
        )
        .join(Country, Visitor.CountryID == Country.OBJECTID)
        .group_by(Country.CountryCode, Country.CountryName)
        .order_by(func.count(Visitor.VisitorID).desc())
        .all()
    )

    # --- Total visitors ---
    total_visitors = db.query(func.count(Visitor.VisitorID)).scalar()

    data = {
        "total": total_visitors,
        "per_month": [
            {"year": r.year, "month": r.month, "count": r.count} for r in per_month
        ],
        "per_country": [
            {
                "country_code": r.country_code,
                "country_name": r.country_name,
                "count": r.count,
            }
            for r in per_country
        ],
    }

    return success_response("Visitors summary retrieved successfully", data)


@router.get("/visitors/filter")
def visitors_filter(
    start_date: Optional[str] = Query(None, description="Format: YYYY-MM"),
    end_date: Optional[str] = Query(None, description="Format: YYYY-MM"),
    country_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Filters visitors by month-based date range and/or country.
    Returns:
    - Total visitors
    - Per-country counts
    - Time series per month for filtered countries
    """

    # --- Prepare date filters ---
    filters = []
    if start_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m")
            filters.append((extract("year", Visitor.VisitAt) * 100 + extract("month", Visitor.VisitAt)) 
                           >= start.year * 100 + start.month)
        except ValueError:
            return {"error": "Invalid start_date format. Use YYYY-MM"}
    if end_date:
        try:
            end = datetime.strptime(end_date, "%Y-%m")
            filters.append((extract("year", Visitor.VisitAt) * 100 + extract("month", Visitor.VisitAt)) 
                           <= end.year * 100 + end.month)
        except ValueError:
            return {"error": "Invalid end_date format. Use YYYY-MM"}
    if country_id:
        filters.append(Visitor.CountryID == country_id)

    # --- Aggregate total visitors per country ---
    per_country_query = (
        db.query(
            Country.CountryCode.label("country_code"),
            Country.CountryName.label("country_name"),
            func.count(Visitor.VisitorID).label("count")
        )
        .join(Country, Visitor.CountryID == Country.OBJECTID)
        .filter(*filters)
        .group_by(Country.CountryCode, Country.CountryName)
        .order_by(func.count(Visitor.VisitorID).desc())
    )
    per_country = per_country_query.all()
    total_visitors = sum(r.count for r in per_country)

    # --- Time series per month ---
    year_expr_visitors = extract("year", Visitor.VisitAt).label("year")
    month_expr_visitors = extract("month", Visitor.VisitAt).label("month")

    time_series_query = (
        db.query(
            year_expr_visitors,
            month_expr_visitors,
            func.count(Visitor.VisitorID).label("count")
        )
        .filter(*filters)
        .group_by(year_expr_visitors, month_expr_visitors)
        .order_by(year_expr_visitors, month_expr_visitors)
    )
    time_series = time_series_query.all()

    formatted_series = [
        {"month": f"{int(r.year)}-{int(r.month):02d}", "count": r.count} for r in time_series
    ]

    data = {
        "total": total_visitors,
        "countries": [
            {"country_code": r.country_code, "country_name": r.country_name, "count": r.count}
            for r in per_country
        ],
        "time_series": formatted_series
    }

    return success_response("Visitors filtered successfully", data)





#-------------------------------------------------------------------------------
#--------------------------Users------------------------------------------------
#-------------------------------------------------------------------------------



# ----------------------------
# 0 filters options for the users 
# ----------------------------

@router.get("/users/filter-options")
def get_user_filter_options(db: Session = Depends(get_db)):
    """
    Returns available filter options for users/downloads dashboard:
    - Countries with download requests
    - Organization names from requests
    - Dataset names from download items
    """

    # --- Countries that have requests ---
    countries = (
        db.query(
            DownloadRequest.Country.label("country_code"),
            Country.OBJECTID.label("country_id"),
            Country.CountryName.label("country_name"),
            func.count(DownloadRequest.ReqNo).label("count")
        )
        .outerjoin(Country, Country.CountryCode == DownloadRequest.Country)
        .group_by(DownloadRequest.Country, Country.CountryName,Country.OBJECTID)
        .order_by(Country.CountryName)
        .all()
    )

    # --- Organization names (distinct, non-null) ---
    OrgType = (
        db.query(DownloadRequest.OrgType)
        .filter(DownloadRequest.OrgType.isnot(None))
        .filter(DownloadRequest.OrgType != "")
        .distinct()
        .order_by(DownloadRequest.OrgType)
        .all()
    )

    # --- Dataset names (distinct, non-null) ---
    dataset_names = (
        db.query(DownloadItem.DatasetName)
        .filter(DownloadItem.DatasetName.isnot(None))
        .filter(DownloadItem.DatasetName != "")
        .distinct()
        .order_by(DownloadItem.DatasetName)
        .all()
    )

    data = {
        "countries": [
            {
                "CountryCode": c.country_code,
                "Country_id": c.country_id,
                "CountryName": c.country_name,
                "RequestCount": c.count
            }
            for c in countries
        ],
        "organizations": [o.OrgType for o in OrgType],
        "datasets": [d.DatasetName for d in dataset_names],
    }

    return success_response("User/download filter options retrieved successfully", data)



# ----------------------------
# 3️⃣ Users & Downloads Summary Endpoint
# ----------------------------
@router.get("/users/summary")
def users_summary(db: Session = Depends(get_db)):
    """
    Returns total users, total download requests, download items,
    and aggregated data per country, month, org type, and dataset.
    """

    total_users = db.query(func.count(User.UserID)).scalar() or 0
    total_requests = db.query(func.count(DownloadRequest.ReqNo)).scalar() or 0
    total_download_items = db.query(func.count(DownloadItem.ID)).scalar() or 0

    # ----------------------------------------
    # Users per month
    # ----------------------------------------
    user_year_expr = func.year(User.CreatedAt).label("year")
    user_month_expr = func.month(User.CreatedAt).label("month")

    users_per_month = (
        db.query(user_year_expr, user_month_expr, func.count(User.UserID).label("count"))
        .group_by(user_year_expr, user_month_expr)
        .order_by(user_year_expr, user_month_expr)
        .all()
    )
    print(users_per_month)

    # ----------------------------------------
    # Requests per country
    # ----------------------------------------
    requests_per_country = (
        db.query(
            DownloadRequest.Country.label("country_code"),
            Country.CountryName.label("country_name"),
            func.count(DownloadRequest.ReqNo).label("count")
        )
        .outerjoin(Country, Country.CountryCode == DownloadRequest.Country)
        .group_by(DownloadRequest.Country, Country.CountryName)
        .all()
    )

    # ----------------------------------------
    # Downloads per country
    # ----------------------------------------
    downloads_per_country = (
        db.query(
            DownloadRequest.Country.label("country_code"),
            Country.CountryName.label("country_name"),
            func.count(DownloadItem.ID).label("count")
        )
        .join(DownloadItem, DownloadItem.ReqNo == DownloadRequest.ReqNo)
        .outerjoin(Country, Country.CountryCode == DownloadRequest.Country)
        .group_by(DownloadRequest.Country, Country.CountryName)
        .all()
    )

    # ----------------------------------------
    # Requests per month
    # ----------------------------------------
    req_year_expr = func.year(DownloadRequest.Date).label("year")
    req_month_expr = func.month(DownloadRequest.Date).label("month")

    requests_per_month = (
        db.query(req_year_expr, req_month_expr, func.count(DownloadRequest.ReqNo).label("count"))
        .group_by(req_year_expr, req_month_expr)
        .order_by(req_year_expr, req_month_expr)
        .all()
    )

    # ----------------------------------------
    # Downloads per month
    # ----------------------------------------
    downloads_per_month = (
        db.query(req_year_expr, req_month_expr, func.count(DownloadItem.ID).label("count"))
        .join(DownloadItem, DownloadItem.ReqNo == DownloadRequest.ReqNo)
        .group_by(req_year_expr, req_month_expr)
        .order_by(req_year_expr, req_month_expr)
        .all()
    )

    # ----------------------------------------
    # Downloads per org type
    # ----------------------------------------
    downloads_per_orgtype = (
        db.query(
            DownloadRequest.OrgType.label("orgtype"),
            func.count(DownloadItem.ID).label("count")
        )
        .join(DownloadItem, DownloadItem.ReqNo == DownloadRequest.ReqNo)
        .group_by(DownloadRequest.OrgType)
        .all()
    )

    # ----------------------------------------
    # Downloads per dataset
    # ----------------------------------------
    downloads_per_dataset = (
        db.query(
            DownloadItem.DatasetName.label("dataset"),
            func.count(DownloadItem.ID).label("count")
        )
        .group_by(DownloadItem.DatasetName)
        .all()
    )

    # Helper to format YYYY-MM
    def format_year_month(year_val, month_val):
        if year_val is None or month_val is None:
            return None
        return f"{int(year_val)}-{int(month_val):02d}"

    data = {
        "total_users": total_users,
        "total_requests": total_requests,
        "total_download_items": total_download_items,

        # ✅ NEW: Users per month
        "users_per_month": [
            {"month": format_year_month(r.year, r.month), "count": r.count}
            for r in users_per_month
        ],

        "requests_per_country": [
            {"CountryCode": r.country_code, "CountryName": r.country_name, "count": r.count}
            for r in requests_per_country
        ],
        "downloads_per_country": [
            {"CountryCode": r.country_code, "CountryName": r.country_name, "count": r.count}
            for r in downloads_per_country
        ],
        "requests_per_month": [
            {"month": format_year_month(r.year, r.month), "count": r.count}
            for r in requests_per_month
        ],
        "downloads_per_month": [
            {"month": format_year_month(r.year, r.month), "count": r.count}
            for r in downloads_per_month
        ],
        "downloads_per_orgtype": [
            {"orgtype": r.orgtype, "count": r.count} for r in downloads_per_orgtype
        ],
        "downloads_per_dataset": [
            {"dataset": r.dataset, "count": r.count} for r in downloads_per_dataset
        ],
    }

    return success_response("Users & downloads summary retrieved successfully", data)

# ----------------------------
# 2️⃣ Users & Downloads Filter Endpoint
# ----------------------------
@router.get("/users/filter")
def users_filter(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    country: Optional[str] = Query(None),
    orgtype: Optional[List[str]] = Query(None, description="Filter by one or more organization types"),
    dataset_name: Optional[List[str]] = Query(None, description="Filter by one or more dataset names"),
    db: Session = Depends(get_db),
):
    """
    Filters users' download requests by date, country, org type, and dataset.
    Returns aggregated counts per country, month, org type, and dataset.
    
    orgtype and dataset_name can accept multiple values:
    - Single: ?orgtype=Type1
    - Multiple: ?orgtype=Type1&orgtype=Type2
    """

    # Base queries
    query_requests = db.query(DownloadRequest)
    query_downloads = db.query(DownloadRequest).join(DownloadItem, DownloadItem.ReqNo == DownloadRequest.ReqNo)

    # Apply filters
    if start_date:
        query_requests = query_requests.filter(DownloadRequest.Date >= start_date)
        query_downloads = query_downloads.filter(DownloadRequest.Date >= start_date)
    if end_date:
        query_requests = query_requests.filter(DownloadRequest.Date <= end_date)
        query_downloads = query_downloads.filter(DownloadRequest.Date <= end_date)
    if country:
        query_requests = query_requests.filter(DownloadRequest.Country == country)
        query_downloads = query_downloads.filter(DownloadRequest.Country == country)
    if orgtype:
        # Filter by one or more organization types
        query_downloads = query_downloads.filter(DownloadRequest.OrgType.in_(orgtype))
    if dataset_name:
        # Filter by one or more dataset names
        query_downloads = query_downloads.filter(DownloadItem.DatasetName.in_(dataset_name))

    # Totals
    total_requests = query_requests.count()
    total_download_items = query_downloads.count()

    # Aggregations
    requests_per_country = (
        query_requests
        .outerjoin(Country, Country.CountryCode == DownloadRequest.Country)
        .with_entities(
            DownloadRequest.Country.label("country_code"),
            Country.CountryName.label("country_name"),
            func.count(DownloadRequest.ReqNo).label("count")
        )
        .group_by(DownloadRequest.Country, Country.CountryName)
        .order_by(func.count(DownloadRequest.ReqNo).desc())
        .all()
    )

    downloads_per_country = (
        query_downloads
        .outerjoin(Country, Country.CountryCode == DownloadRequest.Country)
        .with_entities(
            DownloadRequest.Country.label("country_code"),
            Country.CountryName.label("country_name"),
            func.count(DownloadItem.ID).label("count")
        )
        .group_by(DownloadRequest.Country, Country.CountryName)
        .order_by(func.count(DownloadItem.ID).desc())
        .all()
    )

    # Group by YEAR and MONTH separately to avoid DATEPART binding issues
    year_expr_f = func.year(DownloadRequest.Date).label("year")
    month_expr_f = func.month(DownloadRequest.Date).label("month")

    requests_per_month = (
        query_requests.with_entities(year_expr_f, month_expr_f, func.count(DownloadRequest.ReqNo))
        .group_by(year_expr_f, month_expr_f)
        .order_by(year_expr_f, month_expr_f)
        .all()
    )

    downloads_per_month = (
        query_downloads.with_entities(year_expr_f, month_expr_f, func.count(DownloadItem.ID))
        .group_by(year_expr_f, month_expr_f)
        .order_by(year_expr_f, month_expr_f)
        .all()
    )

    downloads_per_orgtype = (
        query_downloads.with_entities(
            DownloadRequest.OrgType,
            func.count(DownloadItem.ID)
        )
        .group_by(DownloadRequest.OrgType)
        .order_by(func.count(DownloadItem.ID).desc())
        .all()
    )

    downloads_per_dataset = (
        query_downloads.with_entities(
            DownloadItem.DatasetName,
            func.count(DownloadItem.ID)
        )
        .group_by(DownloadItem.DatasetName)
        .order_by(func.count(DownloadItem.ID).desc())
        .all()
    )

    # Helper to format year/month -> YYYY-MM
    def format_year_month_f(year_val, month_val):
        if year_val is None or month_val is None:
            return None
        return f"{int(year_val)}-{int(month_val):02d}"

    data = {
        "total_requests": total_requests,
        "total_download_items": total_download_items,
        "requests_per_country": [{"CountryCode": r[0], "CountryName": r[1], "count": r[2]} for r in requests_per_country],
        "downloads_per_country": [{"CountryCode": r[0], "CountryName": r[1], "count": r[2]} for r in downloads_per_country],
        "requests_per_month": [{"month": format_year_month_f(r[0], r[1]), "count": r[2]} for r in requests_per_month],
        "downloads_per_month": [{"month": format_year_month_f(r[0], r[1]), "count": r[2]} for r in downloads_per_month],
        "downloads_per_orgtype": [{"orgtype": r[0], "count": r[1]} for r in downloads_per_orgtype],
        "downloads_per_dataset": [{"dataset": r[0], "count": r[1]} for r in downloads_per_dataset],
    }

    return success_response("Filtered users & downloads data retrieved successfully", data)