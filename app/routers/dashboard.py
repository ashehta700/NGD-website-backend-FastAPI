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
from fastapi_cache.decorator import cache


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
    """Get available filter options including dataset names"""
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
    datasets = (
        db.query(DownloadRequest.DatasetName)
        .distinct()
        .filter(DownloadRequest.DatasetName.isnot(None))
        .order_by(DownloadRequest.DatasetName)
        .all()
    )

    return {
        "org_types": [o[0] for o in org_types if o[0]],
        "countries": [c[0] for c in countries if c[0]],
        "datasets": [d[0] for d in datasets if d[0]],
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
@cache(expire=3600)  # cache for 1 hour
def get_users_data(
    country: Optional[str] = None,
    orgtype: Optional[str] = None,
    dataset: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Fast optimized user download data endpoint with caching"""

    filters = ["1=1"]
    params = {}

    if country:
        filters.append("CountryName = :country")
        params["country"] = country
    if orgtype:
        filters.append("OrgType = :orgtype")
        params["orgtype"] = orgtype
    if dataset:
        filters.append("DatasetName = :dataset")
        params["dataset"] = dataset
    if start_date:
        filters.append("CAST(requestdate AS DATE) >= :start_date")
        params["start_date"] = start_date
    if end_date:
        filters.append("CAST(requestdate AS DATE) <= :end_date")
        params["end_date"] = end_date

    where_clause = " AND ".join(filters)

    sql = text(f"""
        SELECT 
            itemid, ReqNo, OrgType, CountryName, DatasetName,
            requestdate, Latitude, Longitude, geom.STAsText() AS WKT
        FROM dbo.VIEW_DOWNLOAD_REQUESTS
        WHERE {where_clause}
    """)
    result = db.execute(sql, params).fetchall()

    users = [
        {
            "lat": r.Latitude,
            "lon": r.Longitude,
            "label": f"{r.OrgType or ''} - {r.DatasetName or ''}",
            "time": r.requestdate.isoformat() if r.requestdate else None,
            "geom": r.WKT,
            "orgtype": r.OrgType,
            "country": r.CountryName,
            "dataset": r.DatasetName,
            "itemid": r.itemid,
            "reqno": r.ReqNo
        }
        for r in result
    ]

    stats_sql = text(f"""
        SELECT 
            CountryName,
            OrgType,
            DatasetName,
            COUNT(itemid) AS total_items,
            COUNT(DISTINCT ReqNo) AS total_requests,
            CAST(requestdate AS DATE) AS request_date
        FROM dbo.VIEW_DOWNLOAD_REQUESTS
        WHERE {where_clause}
        GROUP BY CountryName, OrgType, DatasetName, CAST(requestdate AS DATE)
        ORDER BY request_date
    """)

    stats_result = db.execute(stats_sql, params).fetchall()

    by_country, by_orgtype, by_dataset = {}, {}, {}
    total_items = 0
    total_requests = 0
    time_series = []

    for r in stats_result:
        total_items += r.total_items
        total_requests += r.total_requests
        by_country[r.CountryName] = by_country.get(r.CountryName, 0) + r.total_items
        by_orgtype[r.OrgType] = by_orgtype.get(r.OrgType, 0) + r.total_items
        by_dataset[r.DatasetName] = by_dataset.get(r.DatasetName, 0) + r.total_items

        time_series.append({
            "date": r.request_date.isoformat() if r.request_date else None,
            "items": r.total_items,
            "requests": r.total_requests,
            "orgtype": r.OrgType,
            "dataset": r.DatasetName,
        })

    return {
        "markers": users,
        "statistics": {
            "total_items": total_items,
            "total_requests": total_requests,
            "by_country": by_country,
            "by_orgtype": by_orgtype,
            "by_dataset": by_dataset,
            "time_series": time_series,
        },
    }





# @router.get("/data/combined")
# def get_combined_data(
#     type: str = "visitor",
#     country: Optional[str] = None,
#     orgtype: Optional[str] = None,
#     dataset: Optional[str] = None,
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None,
#     db: Session = Depends(get_db),
# ):
#     """Combined endpoint for dashboard compatibility"""
#     if type == "visitor":
#         return get_visitors_data(country, start_date, end_date, db)
#     elif type == "user":
#         return get_users_data(country, orgtype, dataset, start_date, end_date, db)
#     else:
#         raise HTTPException(status_code=400, detail="Invalid type")

