from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from sqlalchemy import func , or_
from datetime import datetime
from typing import Optional, List
from app.models.users import User
from app.models.survey import UsersFeedbackQuestion, QuestionChoice, UsersFeedbackAnswer , Vote
from app.schemas.survey import BulkAnswerRequest
from app.auth.jwt_bearer import JWTBearer
from app.utils.response import success_response, error_response
from sqlalchemy.orm import Session, joinedload 
from app.database import get_db
from app.utils.utils import clean_text , _resolve_identity  



router = APIRouter(prefix="/survey", tags=["Survey"])





# -------------------------------
# 1) POST  Data For Vote Question on home Page 
# -------------------------------
def _resolve_identity(request: Request, token_payload: dict):
    """
    Helper: resolve identity from JWT or request cookies
    """
    user_id = None
    visitor_id = None

    if token_payload and "user_id" in token_payload:
        user_id = token_payload["user_id"]

    # If user is not authenticated, try to get visitor_id from cookies or headers
    if not user_id:
        visitor_id = request.cookies.get("visitor_id") or request.headers.get("X-Visitor-Id")

    return user_id, visitor_id




@router.post("/vote")
def submit_vote(
    Answer: str = Body(..., embed=True),
    SubAnswer: str = Body(None, embed=True),
    request: Request = None,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(JWTBearer(auto_error=False))
):
    """
    Submit a user or visitor vote.
    - Prevents duplicate voting.
    - Stores "No" votes with optional SubAnswer.
    """
    user_id, visitor_id = _resolve_identity(request, token_payload)

    # ✅ Validate input
    if Answer not in ["Yes", "No"]:
        return error_response("Answer must be 'Yes' or 'No'.", "INVALID_ANSWER")

    if not user_id and not visitor_id:
        return error_response("Either UserId or VisitorId is required.", "NO_IDENTITY")

    # ✅ Check if user or visitor already voted
    existing_vote = (
        db.query(Vote)
        .filter(
            (Vote.UserId == user_id) if user_id else (Vote.VisitorId == visitor_id)
        )
        .first()
    )

    if existing_vote:
        # Return existing info — no new vote created
        return success_response("User has already voted before.", {
            "AlreadyVoted": True,
            "Id": existing_vote.Id,
            "Answer": existing_vote.Answer,
            "SubAnswer": existing_vote.SubAnswer,
            "CreatedAt": existing_vote.CreatedAt,
        })

    # ✅ Create new vote
    vote = Vote(
        UserId=user_id if user_id else None,
        VisitorId=visitor_id if visitor_id else None,
        Answer=Answer,
        SubAnswer=SubAnswer if Answer == "No" else None,
        CreatedAt=datetime.utcnow()
    )

    db.add(vote)
    db.commit()
    db.refresh(vote)

    return success_response("Vote submitted successfully.", {
        "AlreadyVoted": False,
        "Id": vote.Id,
        "Answer": vote.Answer,
        "SubAnswer": vote.SubAnswer,
        "UserId": vote.UserId,
        "VisitorId": vote.VisitorId,
        "CreatedAt": vote.CreatedAt,
    })


# -------------------------------
# 2) Get All Statistics for Vote Question on Home Page 
# -------------------------------
@router.get("/vote/stats")
def get_vote_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Vote.Id)).scalar() or 0
    yes_count = db.query(func.count(Vote.Id)).filter(Vote.Answer == "Yes").scalar() or 0
    no_count = db.query(func.count(Vote.Id)).filter(Vote.Answer == "No").scalar() or 0

    percentage_yes = round((yes_count / total) * 100, 2) if total > 0 else 0
    percentage_no = round((no_count / total) * 100, 2) if total > 0 else 0

    return success_response("Vote statistics", {
        "total_votes": total,
        "yes_votes": yes_count,
        "no_votes": no_count,
        "yes_percentage": percentage_yes,
        "no_percentage": percentage_no
    })





# -------------------------------
# 3) GET all survey questions - Grouped by Category
# -------------------------------
@router.get("/questions")
def get_questions(db: Session = Depends(get_db)):
    # Fetch all questions where IsDeleted is False or NULL
    questions = (
        db.query(UsersFeedbackQuestion)
        .filter(or_(UsersFeedbackQuestion.IsDeleted == False, UsersFeedbackQuestion.IsDeleted == None))
        .options(
            joinedload(UsersFeedbackQuestion.category),
            joinedload(UsersFeedbackQuestion.type),
            joinedload(UsersFeedbackQuestion.choices),
        )
        .all()
    )

    # Group by category
    categories_dict = {}
    for q in questions:
        category_key = q.category.Id if q.category else "Uncategorized"

        if category_key not in categories_dict:
            categories_dict[category_key] = {
                "CategoryId": q.category.Id if q.category else None,
                "Category_en": q.category.Category if q.category else "Uncategorized",
                "Category_ar": q.category.Category_Ar if q.category else "غير مصنف",
                "Questions": []
            }

        question_data = {
            "Id": q.Id,
            "MainQuestion_en": clean_text(q.MainQuestion),
            "MainQuestion_ar": clean_text(q.MainQuestion_Ar),
            "Type": {
                "Id": q.type.Id if q.type else None,
                "Type_en": q.type.TypeOfQuestion if q.type else None,
            } if q.type else None,
        }

        # Only add choices if they exist
        choices = [
            {
                "ChoiceId": c.Id,
                "Choice_en": clean_text(c.Choice),
                "Choice_ar": clean_text(c.Choice_Ar),
            }
            for c in (q.choices or []) if c.IsDeleted in [False, None]
        ]
        if choices:
            question_data["Choices"] = choices

        categories_dict[category_key]["Questions"].append(question_data)

    # Convert dict → list
    categories_list = list(categories_dict.values())

    return success_response("Survey questions grouped by category", {"categories": categories_list})




# -------------------------------
# 4) POST bulk answers (multi-choice or text)
# -------------------------------
@router.post("/answers")
def submit_bulk_answers(
    payload: BulkAnswerRequest,
    request: Request = None,
    db: Session = Depends(get_db),
    token_payload: Optional[dict] = Depends(JWTBearer(auto_error=False))
):
    user_id, visitor_id = _resolve_identity(request, token_payload)

    # Ensure we have at least one identity
    if not user_id and not visitor_id:
        raise HTTPException(status_code=400, detail="Either UserId or VisitorId is required.")

    if not payload.answers:
        raise HTTPException(status_code=400, detail="No answers provided.")

    db_answers = []

    for item in payload.answers:
        # Validate: either ChoiceId or TextAnswer must be provided
        if not item.ChoiceId and not item.TextAnswer:
            raise HTTPException(
                status_code=400,
                detail=f"Either ChoiceId or TextAnswer is required for QuestionId {item.QuestionId}"
            )

        # Validate QuestionId exists
        question_exists = db.query(UsersFeedbackQuestion).filter(
            UsersFeedbackQuestion.Id == item.QuestionId,
            UsersFeedbackQuestion.IsDeleted == False
        ).first()
        if not question_exists:
            raise HTTPException(status_code=400, detail=f"Invalid QuestionId: {item.QuestionId}")

        # Normalize ChoiceId into a list
        choices = [item.ChoiceId] if isinstance(item.ChoiceId, int) else (item.ChoiceId or [])

        # Validate all choices exist for this question
        if choices:
            valid_choices = db.query(QuestionChoice.Id).filter(
                QuestionChoice.QuestionId == item.QuestionId,
                QuestionChoice.Id.in_(choices)
            ).all()
            valid_choice_ids = {c.Id for c in valid_choices}
            invalid = set(choices) - valid_choice_ids
            if invalid:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid ChoiceId(s) {list(invalid)} for QuestionId {item.QuestionId}"
                )

        # Insert one record per choice
        for choice_id in choices:
            answer = UsersFeedbackAnswer(
                VisitorId=visitor_id,
                QuestionId=item.QuestionId,
                ChoiceId=choice_id,
                please_specify=item.TextAnswer if item.TextAnswer else None,
                CreatedAt=datetime.utcnow(),
                CreatedByUserID=user_id if user_id else None,
            )
            db_answers.append(answer)

        # If no ChoiceId but there is TextAnswer → insert text-only record
        if not choices and item.TextAnswer:
            answer = UsersFeedbackAnswer(
                VisitorId=visitor_id,
                QuestionId=item.QuestionId,
                ChoiceId=None,
                please_specify=item.TextAnswer,
                CreatedAt=datetime.utcnow(),
                CreatedByUserID=user_id if user_id else None,
            )
            db_answers.append(answer)

    # Save to DB
    db.add_all(db_answers)
    db.commit()

    # Refresh IDs
    for answer in db_answers:
        db.refresh(answer)

    return success_response(
        "Bulk answers submitted",
        [
            {
                "Id": a.Id,
                "QuestionId": a.QuestionId,
                "ChoiceId": a.ChoiceId,
                "TextAnswer": a.please_specify,
                "VisitorId": a.VisitorId,
                "UserId": a.CreatedByUserID,
            }
            for a in db_answers
        ]
    )

