# app/routers/dashboard.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func,and_, extract ,literal_column ,text , distinct ,or_
from datetime import datetime
from typing import Optional, List
from app.database import get_db
from app.models.visitors import Visitor
from app.models.users import User
from app.models.lookups import Country, OrganizationType
from app.models.dashboard import DownloadRequest, DownloadItem
from app.utils.response import success_response
from datetime import datetime

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
            Country.CountryNameAr.label("country_name_ar"),
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
                "CountryNameAr": c.country_name_ar,
                "VisitorCount": c.count
            }
            for c in countries
        ]
    }

    return success_response("Visitor filter options retrieved successfully" , data=data)



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
            Country.CountryNameAr.label("country_name_ar"),
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
                "country_name_ar": r.country_name_ar,
                "count": r.count,
            }
            for r in per_country
        ],
    }

    return success_response("Visitors summary retrieved successfully", data=data)


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
            Country.CountryNameAr.label("country_name_ar"),
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
            {"country_code": r.country_code, "country_name": r.country_name, "country_name_ar": r.country_name_ar, "count": r.count}
            for r in per_country
        ],
        "time_series": formatted_series
    }

    return success_response("Visitors filtered successfully", data=data)





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
            Country.CountryNameAr.label("country_name_ar"),
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
                "CountryNameAr": c.country_name_ar,
                "RequestCount": c.count
            }
            for c in countries
        ],
        "organizations": [o.OrgType for o in OrgType],
        "datasets": [d.DatasetName for d in dataset_names],
    }

    return success_response("User/download filter options retrieved successfully", data=data)



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
            Country.CountryNameAr.label("country_name_ar"),
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
            Country.CountryNameAr.label("country_name_ar"),
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
            {"CountryCode": r.country_code, "CountryName": r.country_name, "CountryNameAr": r.country_name_ar, "count": r.count}
            for r in requests_per_country
        ],
        "downloads_per_country": [
            {"CountryCode": r.country_code, "CountryName": r.country_name, "CountryNameAr": r.country_name_ar, "count": r.count}
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

    return success_response("Users & downloads summary retrieved successfully", data=data)

# ----------------------------
# 2️⃣ Users & Downloads Filter Endpoint
# ----------------------------
@router.get("/users/filter")
def users_filter(
    start_date: Optional[str] = Query(None, description="Format: YYYY-MM"),
    end_date: Optional[str] = Query(None, description="Format: YYYY-MM"),
    country: Optional[str] = Query(None, description="Filter with CountryCode"),
    orgtype: Optional[List[str]] = Query(None),
    dataset_name: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Filters registered users and download requests, returns:
    - total users, total request users, total requests, total downloads
    - data per country (only countries with requests for filtered datasets)
    - data per month
    - downloads per org type and dataset
    """

    # -----------------------------
    # 1️⃣ APPLY FILTERS
    # -----------------------------
    filters_users = []
    filters_requests = []

    if start_date:
        s = datetime.strptime(start_date, "%Y-%m")
        filters_users.append(User.CreatedAt >= s)
        filters_requests.append(DownloadRequest.Date >= s)
    if end_date:
        e = datetime.strptime(end_date, "%Y-%m")
        filters_users.append(User.CreatedAt <= e)
        filters_requests.append(DownloadRequest.Date <= e)
    if country:
        filters_users.append(User.country.has(Country.CountryCode == country))
        filters_requests.append(DownloadRequest.Country == country)
    if orgtype:
        filters_users.append(User.organization_type.has(OrganizationType.NameEn.in_(orgtype)))
        filters_requests.append(DownloadRequest.OrgType.in_(orgtype))

    # -----------------------------
    # 2️⃣ FILTERED DOWNLOAD REQUESTS
    # -----------------------------
    request_query = (
        db.query(
            DownloadRequest.ReqNo,
            DownloadRequest.UserID,
            DownloadRequest.Country,
            DownloadRequest.OrgType,
            DownloadRequest.Date,
            DownloadItem.DatasetName
        )
        .join(DownloadItem, DownloadItem.ReqNo == DownloadRequest.ReqNo)
        .filter(*filters_requests)
    )

    if dataset_name:
        request_query = request_query.filter(DownloadItem.DatasetName.in_(dataset_name))

    request_subq = request_query.subquery()

    # -----------------------------
    # 3️⃣ REGISTERED USERS BASED ON FILTERS
    # -----------------------------
    # If dataset filter exists, only consider users who requested these datasets
    if dataset_name:
        filtered_users_query = db.query(User).filter(
            User.UserID.in_(db.query(request_subq.c.UserID).distinct()),
            *filters_users
        )
    else:
        filtered_users_query = db.query(User).filter(*filters_users)

    filtered_users_subq = filtered_users_query.subquery()

    # -----------------------------
    # 4️⃣ TOTALS
    # -----------------------------
    total_users = filtered_users_query.count()
    total_request_users = db.query(func.count(distinct(request_subq.c.UserID))).scalar() or 0
    total_requests = db.query(func.count(distinct(request_subq.c.ReqNo))).scalar() or 0
    total_downloads = db.query(func.count(request_subq.c.DatasetName)).scalar() or 0

    # -----------------------------
    # 5️⃣ DATA PER COUNTRY
    # -----------------------------
    requests_per_country = (
        db.query(
            request_subq.c.Country.label("CountryCode"),
            func.count(distinct(request_subq.c.UserID)).label("request_user"),
            func.count(distinct(request_subq.c.ReqNo)).label("total_requests"),
            func.count(request_subq.c.DatasetName).label("total_download")
        )
        .group_by(request_subq.c.Country)
        .subquery()
    )

    registered_users_per_country = (
        db.query(
            filtered_users_subq.c.CountryID.label("CountryID"),
            func.count(filtered_users_subq.c.UserID).label("register_user")
        )
        .group_by(filtered_users_subq.c.CountryID)
        .subquery()
    )

    data_per_country = (
        db.query(
            Country.CountryCode,
            Country.CountryName,
            Country.CountryNameAr,
            func.coalesce(registered_users_per_country.c.register_user, 0).label("register_user"),
            func.coalesce(requests_per_country.c.request_user, 0).label("request_user"),
            func.coalesce(requests_per_country.c.total_requests, 0).label("total_requests"),
            func.coalesce(requests_per_country.c.total_download, 0).label("total_download")
        )
        .outerjoin(
            registered_users_per_country,
            registered_users_per_country.c.CountryID == Country.OBJECTID
        )
        .join(
            requests_per_country,
            requests_per_country.c.CountryCode == Country.CountryCode
        )  # Only countries with requests after dataset filter
        .order_by(Country.CountryName)
        .all()
    )

    # -----------------------------
    # 6️⃣ DATA PER MONTH
    # -----------------------------
    requests_per_month = (
        db.query(
            extract("year", request_subq.c.Date).label("year"),
            extract("month", request_subq.c.Date).label("month"),
            func.count(distinct(request_subq.c.ReqNo)).label("requests"),
            func.count(distinct(request_subq.c.UserID)).label("request_users"),
            func.count(request_subq.c.DatasetName).label("downloads")
        )
        .group_by(
            extract("year", request_subq.c.Date),
            extract("month", request_subq.c.Date)
        )
        .order_by(
            extract("year", request_subq.c.Date),
            extract("month", request_subq.c.Date)
        )
        .all()
    )

    users_per_month = (
        db.query(
            extract("year", filtered_users_subq.c.CreatedAt).label("year"),
            extract("month", filtered_users_subq.c.CreatedAt).label("month"),
            func.count(filtered_users_subq.c.UserID).label("register_users")
        )
        .group_by(
            extract("year", filtered_users_subq.c.CreatedAt),
            extract("month", filtered_users_subq.c.CreatedAt)
        )
        .order_by(
            extract("year", filtered_users_subq.c.CreatedAt),
            extract("month", filtered_users_subq.c.CreatedAt)
        )
        .all()
    )

    month_data = {}
    for r in requests_per_month:
        key = f"{int(r.year)}-{int(r.month):02d}"
        month_data[key] = {
            "month": key,
            "requests": r.requests,
            "request_users": r.request_users,
            "downloads": r.downloads,
            "register_users": 0
        }
    for u in users_per_month:
        key = f"{int(u.year)}-{int(u.month):02d}"
        if key not in month_data:
            month_data[key] = {
                "month": key,
                "requests": 0,
                "request_users": 0,
                "downloads": 0,
                "register_users": u.register_users
            }
        else:
            month_data[key]["register_users"] = u.register_users

    # -----------------------------
    # 7️⃣ DOWNLOADS PER ORG TYPE
    # -----------------------------
    downloads_per_orgtype = (
        db.query(
            request_subq.c.OrgType,
            func.count(distinct(request_subq.c.ReqNo)).label("count")
        )
        .group_by(request_subq.c.OrgType)
        .all()
    )

    # -----------------------------
    # 8️⃣ DOWNLOADS PER DATASET
    # -----------------------------
    downloads_per_dataset = (
        db.query(
            request_subq.c.DatasetName,
            func.count(request_subq.c.DatasetName).label("count")
        )
        .group_by(request_subq.c.DatasetName)
        .all()
    )

    # -----------------------------
    # 9️⃣ FINAL RESPONSE
    # -----------------------------
    response = {
        "total_users": total_users,
        "total_request_users": total_request_users,
        "total_requests": total_requests,
        "total_downloads": total_downloads,
        "total_countries": len(data_per_country),
        "data_per_country": [
            {
                "CountryCode": r.CountryCode,
                "CountryName": r.CountryName,
                "CountryNameAr": r.CountryNameAr,
                "register_user": r.register_user,
                "request_user": r.request_user,
                "total_requests": r.total_requests,
                "total_download": r.total_download
            }
            for r in data_per_country
        ],
        "data_per_month": list(month_data.values()),
        "downloads_per_orgtype": [
            {"orgtype": r.OrgType, "count": r.count} for r in downloads_per_orgtype
        ],
        "downloads_per_dataset": [
            {"dataset": r.DatasetName, "count": r.count} for r in downloads_per_dataset
        ]
    }

    return success_response("Filtered user downloads successfully", data=response)  
