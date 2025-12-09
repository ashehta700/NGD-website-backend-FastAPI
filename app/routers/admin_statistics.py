# app/routers/admin_statistics.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import get_db

# MODELS
from app.models.users import User
from app.models.visitors import Visitor
from app.models.lookups import Country
from app.models.contact_us import ContactUs
from app.models.news import News
from app.models.products import Product
from app.models.requests import Request, Reply
from app.models.survey import (
    UsersFeedbackQuestion,
    UsersFeedbackAnswer,
    Vote
)
from app.models.lookups import Category, Status
from sqlalchemy import extract

# RESPONSE
from app.utils.response import success_response

router = APIRouter(prefix="/admin", tags=["Admin Statistics"])


# -----------------------------------------------------------
# ⭐ ONE MASTER ENDPOINT FOR ALL ADMIN STATISTICS
# -----------------------------------------------------------
@router.get("/statistics/all")
def all_statistics(db: Session = Depends(get_db)):
    """
    Return all admin statistics in one clean endpoint:
    - Countries (users + visitors)
    - Contact form
    - News statistics
    - Products statistics
    - Requests statistics
    - Survey statistics
    """

    # -------------------------------------------------------
    # 1️⃣ COUNTRY STATISTICS
    # -------------------------------------------------------
    users_per_country = (
        db.query(
            Country.CountryCode,
            Country.CountryName,
            Country.CountryNameAr,
            func.count(User.UserID).label("total_users")
        )
        .outerjoin(Country, Country.OBJECTID == User.CountryID)
        .group_by(
            Country.CountryCode,
            Country.CountryName,
            Country.CountryNameAr
        )
        .all()
    )

    visitors_per_country = (
        db.query(
            Country.CountryCode,
            func.count(Visitor.VisitorID).label("total_visitors")
        )
        .outerjoin(Country, Country.OBJECTID == Visitor.CountryID)
        .group_by(Country.CountryCode)
        .all()
    )

    visitors_map = {v[0]: v[1] for v in visitors_per_country}

    countries_data = [
        {
            "country_code": c[0],
            "country_name": c[1],
            "country_name_ar": c[2],
            "total_users": c[3],
            "total_visitors": visitors_map.get(c[0], 0)
        }
        for c in users_per_country
    ]

    # -------------------------------------------------------
    # 2️⃣ CONTACT FORM STATISTICS
    # -------------------------------------------------------
    total_contacts = db.query(func.count(ContactUs.ContactID)).scalar() or 0
    total_responded = db.query(func.count(ContactUs.ContactID)) \
        .filter(ContactUs.ReplyStatus == True).scalar() or 0
    total_not_responded = total_contacts - total_responded

    contact_data = {
        "total_contact_forms": total_contacts,
        "total_responded": total_responded,
        "total_not_responded": total_not_responded
    }

    # -------------------------------------------------------
    # 3️⃣ NEWS STATISTICS
    # -------------------------------------------------------
    total_news = db.query(func.count(News.NewsID)) \
        .filter(News.Is_delete != True).scalar() or 0

    total_news_deleted = db.query(func.count(News.NewsID)) \
        .filter(News.Is_delete == True).scalar() or 0

    total_slides = db.query(func.count(News.NewsID)) \
        .filter(News.Is_slide == True, News.Is_delete != True).scalar() or 0

    total_reads = db.query(func.sum(News.Read_count)).scalar() or 0

    news_data = {
        "total_news": total_news,
        "total_deleted": total_news_deleted,
        "total_slides": total_slides,
        "total_reads": total_reads
    }

    # -------------------------------------------------------
    # 4️⃣ PRODUCTS STATISTICS
    # -------------------------------------------------------
    total_products = db.query(func.count(Product.ProductID)) \
        .filter(Product.IsDeleted != True).scalar() or 0

    total_products_deleted = db.query(func.count(Product.ProductID)) \
        .filter(Product.IsDeleted == True).scalar() or 0

    products_by_creator = (
        db.query(
            Product.CreatedByUserID,
            func.count(Product.ProductID)
        )
        .group_by(Product.CreatedByUserID)
        .all()
    )

    products_data = {
        "total_products": total_products,
        "total_deleted": total_products_deleted,
        "products_by_creator": [
            {"created_by": row[0], "total": row[1]}
            for row in products_by_creator
        ]
    }

    # -------------------------------------------------------
    # 5️⃣ REQUESTS STATISTICS (Enhanced)
    # -------------------------------------------------------

    # Total requests
    total_requests = db.query(func.count(Request.Id)).filter(Request.IsDeleted != True).scalar() or 0
    total_requests_deleted = db.query(func.count(Request.Id)).filter(Request.IsDeleted == True).scalar() or 0

    # Requests by Status with names
    requests_by_status = (
        db.query(
            Status.Id.label("status_id"),
            Status.Name.label("status_name"),
            func.count(Request.Id).label("total")
        )
        .join(Request, Request.StatusId == Status.Id)
        .filter(Request.IsDeleted != True)
        .group_by(Status.Id, Status.Name)
        .all()
    )

    # Requests by Category with names AND responses per category
    requests_by_category = (
        db.query(
            Category.Id.label("category_id"),
            Category.Name.label("category_name"),
            func.count(Request.Id).label("total"),
            func.coalesce(
                func.sum(
                    case(
                        (Reply.Id != None, 1),
                        else_=0
                    )
                ), 0
            ).label("total_responded"),
            func.coalesce(
                func.sum(
                    case(
                        (Reply.Id == None, 1),
                        else_=0
                    )
                ), 0
            ).label("total_not_responded")
        )
        .outerjoin(Request, Request.CategoryId == Category.Id)
        .outerjoin(Reply, (Reply.RequestId == Request.Id) & (Reply.IsDeleted != True))
        .filter(Request.IsDeleted != True)
        .group_by(Category.Id, Category.Name)
        .all()
    )
    # Total requests with replies (global)
    total_replied_requests = db.query(func.count(func.distinct(Reply.RequestId))) \
        .filter(Reply.IsDeleted != True).scalar() or 0

    requests_data = {
        "total_requests": total_requests,
        "total_deleted": total_requests_deleted,
        "requests_by_status": [
            {"status_id": r.status_id, "status_name": r.status_name, "total": r.total}
            for r in requests_by_status
        ],
        "requests_by_category": [
            {
                "category_id": r.category_id,
                "category_name": r.category_name,
                "total": r.total,
                "total_responded": r.total_responded,
                "total_not_responded": r.total_not_responded
            }
            for r in requests_by_category
        ],
        "total_requests_with_replies": total_replied_requests,
        "total_responded_requests": total_replied_requests,
        "total_not_responded_requests": total_requests - total_replied_requests
    }
    # -------------------------------------------------------
    # 6️⃣ SURVEY STATISTICS
    # -------------------------------------------------------
    total_questions = db.query(func.count(UsersFeedbackQuestion.Id)) \
        .filter(UsersFeedbackQuestion.IsDeleted != True).scalar() or 0

    total_answers = db.query(func.count(UsersFeedbackAnswer.Id)) \
        .filter(UsersFeedbackAnswer.IsDeleted != True).scalar() or 0

    answers_per_question = (
        db.query(
            UsersFeedbackAnswer.QuestionId,
            func.count(UsersFeedbackAnswer.Id)
        )
        .filter(UsersFeedbackAnswer.IsDeleted != True)
        .group_by(UsersFeedbackAnswer.QuestionId)
        .all()
    )

    total_votes = db.query(func.count(Vote.Id)).scalar() or 0

    yes_votes = db.query(func.count(Vote.Id)) \
        .filter(Vote.Answer == "Yes").scalar() or 0

    no_votes = db.query(func.count(Vote.Id)) \
        .filter(Vote.Answer == "No").scalar() or 0

    no_reasons = (
        db.query(Vote.SubAnswer, func.count(Vote.Id))
        .filter(Vote.Answer == "No")
        .group_by(Vote.SubAnswer)
        .all()
    )

    survey_data = {
        "feedback": {
            "total_questions": total_questions,
            "total_answers": total_answers,
            "answers_per_question": [
                {"question_id": row[0], "total": row[1]}
                for row in answers_per_question
            ],
        },
        "vote": {
            "total_votes": total_votes,
            "yes_votes": yes_votes,
            "no_votes": no_votes,
            "no_reasons": [
                {"reason": row[0], "total": row[1]}
                for row in no_reasons
            ]
        }
    }

    # -------------------------------------------------------
    # FINAL RESPONSE
    # -------------------------------------------------------
    full_data = {
        "countries": countries_data,
        "contact": contact_data,
        "news": news_data,
        "products": products_data,
        "requests": requests_data,
        "survey": survey_data
    }

    return success_response("All statistics retrieved successfully", data=full_data)






def build_timeline(query, date_column):
    """
    Returns a dict like {year: {month: count}}
    Works for SQL Server using func.year / func.month.
    """
    year_expr = func.year(date_column).label("year")
    month_expr = func.month(date_column).label("month")

    results = (
        query
        .with_entities(
            year_expr,
            month_expr,
            func.count().label("total")
        )
        .group_by(year_expr, month_expr)
        .order_by(year_expr, month_expr)
        .all()
    )

    timeline = {}
    for r in results:
        y, m, total = int(r.year), int(r.month), r.total
        if y not in timeline:
            timeline[y] = {i: 0 for i in range(1, 13)}
        timeline[y][m] = total

    return timeline


@router.get("/statistics/timeline")
def timeline_statistics(db: Session = Depends(get_db)):
    data = {
        "users": build_timeline(db.query(User), User.CreatedAt),
        "visitors": build_timeline(db.query(Visitor), Visitor.VisitAt),
        "contact": build_timeline(db.query(ContactUs), ContactUs.CreatedAt),
        "requests": build_timeline(db.query(Request).filter(Request.IsDeleted != True), Request.CreatedAt),
        "survey_answers": build_timeline(db.query(UsersFeedbackAnswer).filter(UsersFeedbackAnswer.IsDeleted != True), UsersFeedbackAnswer.CreatedAt),
        "votes": build_timeline(db.query(Vote), Vote.CreatedAt),
    }

    return success_response("Timeline statistics retrieved successfully", data=data)
