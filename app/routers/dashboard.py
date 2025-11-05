from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from app.models.dashboard import Visitor, Country, DownloadRequest
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from fastapi import APIRouter


router = APIRouter(prefix="/dashboard", tags=["DashBoard"])

# Pydantic Models
class StatisticsResponse(BaseModel):
    total_count: int
    by_country: dict
    by_category: dict
    time_series: List[dict]

class DashboardDataResponse(BaseModel):
    markers: List[dict]
    statistics: dict
    total: int


@router.get("/countries")
def get_countries(db: Session = Depends(get_db)):
    """Fetch all countries with boundaries"""
    sql = text("""
        SELECT  
            CountryName,
            Latitude,
            Longitude,
            CASE 
                WHEN COLUMNPROPERTY(OBJECT_ID('Website.COUNTRIES_LIST'), 'geom', 'AllowsNull') IS NOT NULL
                THEN geom.STAsText()
                ELSE NULL
            END AS WKT
        FROM dbo.COUNTRIES_LIST
    """)
    result = db.execute(sql)
    countries = []
    for row in result:
        countries.append({
            "name": row.CountryName,
            "lat": row.Latitude,
            "lon": row.Longitude,
            "geom": row.WKT
        })
    return countries

@router.get("/filters")
def get_filters(db: Session = Depends(get_db)):
    """Get available filter options"""
    org_types = (
        db.query(DownloadRequest.OrgType)
        .distinct()
        .filter(DownloadRequest.OrgType.isnot(None))
        .order_by(DownloadRequest.OrgType)
        .all()
    )
    countries = (
        db.query(DownloadRequest.CountryName)
        .distinct()
        .filter(DownloadRequest.CountryName.isnot(None))
        .order_by(DownloadRequest.CountryName)
        .all()
    )
    return {
        "org_types": [o[0] for o in org_types if o[0]],
        "countries": [c[0] for c in countries if c[0]],
    }

@router.get("/data/visitors")
def get_visitors_data(
    country: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Fetch visitor data with statistics"""
    sql = """
        SELECT 
            VisitorID,
            IPAddress,
            Location,
            X,
            Y,
            VisitAt,
            -- CountryID,
            geom.STAsText() AS WKT
        FROM Website.Visitors
        WHERE 1=1
    """
    
    if country:
        sql += f" AND Location = '{country}'"
    if start_date:
        sql += f" AND CAST(VisitAt AS DATE) >= '{start_date}'"
    if end_date:
        sql += f" AND CAST(VisitAt AS DATE) <= '{end_date}'"
    
    result = db.execute(text(sql))
    visitors = []
    for row in result:
        visitors.append({
            "lat": row.Y,
            "lon": row.X,
            "label": f"Visitor {row.IPAddress}",
            "time": row.VisitAt.isoformat() if row.VisitAt else None,
            "geom": row.WKT
        })
    
    # Get statistics
    stats_sql = """
        SELECT 
            COUNT(*) as total,
            Location,
            CAST(VisitAt AS DATE) as visit_date
        FROM Website.Visitors
        WHERE 1=1
    """
    
    if country:
        stats_sql += f" AND Location = '{country}'"
    if start_date:
        stats_sql += f" AND CAST(VisitAt AS DATE) >= '{start_date}'"
    if end_date:
        stats_sql += f" AND CAST(VisitAt AS DATE) <= '{end_date}'"
    
    stats_sql += " GROUP BY Location, CAST(VisitAt AS DATE) ORDER BY visit_date"
    
    stats_result = db.execute(text(stats_sql))
    
    by_country = {}
    time_series = []
    total = 0
    
    for row in stats_result:
        total += row.total
        by_country[row.Location] = by_country.get(row.Location, 0) + row.total
        time_series.append({
            "date": row.visit_date.isoformat() if row.visit_date else None,
            "count": row.total,
            "country": row.Location
        })
    
    return {
        "markers": visitors,
        "statistics": {
            "total": total,
            "by_country": by_country,
            "time_series": sorted(time_series, key=lambda x: x["date"])
        }
    }

@router.get("/data/users")
def get_users_data(
    country: Optional[str] = None,
    orgtype: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Fetch user download request data with extended statistics"""
    sql = """
        SELECT 
            itemid,
            ReqNo,
            OrgType,
            CountryName,
            requestdate,
            Latitude,
            Longitude,
            DatasetName,
            geom.STAsText() AS WKT
        FROM dbo.VIEW_DOWNLOAD_REQUESTS
        WHERE 1=1
    """
    
    filters = []
    if country:
        filters.append(f"CountryName = '{country}'")
    if orgtype:
        filters.append(f"OrgType = '{orgtype}'")
    if start_date:
        filters.append(f"CAST(requestdate AS DATE) >= '{start_date}'")
    if end_date:
        filters.append(f"CAST(requestdate AS DATE) <= '{end_date}'")
    
    if filters:
        sql += " AND " + " AND ".join(filters)
    
    result = db.execute(text(sql))
    users = []
    
    for row in result:
        users.append({
            "lat": row.Latitude,
            "lon": row.Longitude,
            "label": f"{row.OrgType} - {row.DatasetName}",
            "time": row.requestdate.isoformat() if row.requestdate else None,
            "geom": row.WKT,
            "orgtype": row.OrgType,
            "country": row.CountryName,
            "dataset": row.DatasetName,
            "itemid": row.itemid,
            "reqno": row.ReqNo
        })
    
    # Extended statistics
    by_country = {}
    by_orgtype = {}
    by_dataset = {}
    total_items = 0
    total_requests_set = set()  # Unique ReqNo
    time_series = []

    stats_sql = """
        SELECT 
            CountryName,
            OrgType,
            DatasetName,
            COUNT(itemid) AS total_items,
            COUNT(DISTINCT ReqNo) AS total_requests,
            CAST(requestdate AS DATE) AS request_date
        FROM dbo.VIEW_DOWNLOAD_REQUESTS
        WHERE 1=1
    """

    if filters:
        stats_sql += " AND " + " AND ".join(filters)
    
    stats_sql += """
        GROUP BY CountryName, OrgType, DatasetName, CAST(requestdate AS DATE)
        ORDER BY request_date
    """

    stats_result = db.execute(text(stats_sql))
    
    for row in stats_result:
        total_items += row.total_items
        by_country[row.CountryName] = by_country.get(row.CountryName, 0) + row.total_items
        by_orgtype[row.OrgType] = by_orgtype.get(row.OrgType, 0) + row.total_items
        by_dataset[row.DatasetName] = by_dataset.get(row.DatasetName, 0) + row.total_items
        total_requests_set.add(row.total_requests)
        time_series.append({
            "date": row.request_date.isoformat() if row.request_date else None,
            "items": row.total_items,
            "requests": row.total_requests,
            "orgtype": row.OrgType,
            "dataset": row.DatasetName
        })

    return {
        "markers": users,
        "statistics": {
            "total_items": total_items,
            "total_requests": sum(total_requests_set),
            "by_country": by_country,
            "by_orgtype": by_orgtype,
            "by_dataset": by_dataset,
            "time_series": sorted(time_series, key=lambda x: x["date"])
        }
    }


@router.get("/data/combined")
def get_combined_data(
    type: str = "visitor",
    country: Optional[str] = None,
    orgtype: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Combined endpoint for compatibility"""
    if type == "visitor":
        return get_visitors_data(country, start_date, end_date, db)
    elif type == "user":
        return get_users_data(country, orgtype, start_date, end_date, db)
    else:
        raise HTTPException(status_code=400, detail="Invalid type")

