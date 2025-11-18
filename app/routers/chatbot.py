# routers/chatbot.py
from fastapi import APIRouter, Depends, Body, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.response import success_response, error_response
from app.routers.search import global_search  # reuse global search logic

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

FALLBACK_MESSAGE = {
    "en": "Sorry, I couldn’t find an exact answer to that. You can contact our team at <a href='https://ngd.com/contact' target='_blank'>Customer Support</a> or call +966-XXX-XXXX.",
    "ar": "عذرًا، لم أجد إجابة دقيقة على سؤالك. يمكنك التواصل مع <a href='https://ngd.com/contact' target='_blank'>خدمة العملاء</a> أو الاتصال على +966-XXX-XXXX."
}

@router.post("/ask")
def ask_chatbot(
    request: Request,
    user_question: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """Chatbot endpoint that returns clean and minimal HTML response."""

    is_arabic = any("\u0600" <= ch <= "\u06FF" for ch in user_question)

    try:
        results = global_search(db, user_question, request, skip=0, limit=3)
    except Exception as e:
        return error_response(f"Error occurred while searching: {str(e)}", "INTERNAL_ERROR")

    # Fallback if no results found
    if not results:
        fallback_msg = FALLBACK_MESSAGE["ar"] if is_arabic else FALLBACK_MESSAGE["en"]
        return success_response("No relevant answers found.", {"message": fallback_msg})

    # Intro text
    intro = "وجدت بعض النتائج التي قد تساعدك:" if is_arabic else "I found a few things that might help you:"

    # Build compact HTML cards
    html_cards = []
    for r in results:
        title = r.get("title", "")
        description = (r.get("description") or "")[:120]
        image_html = f"<img src='{r['image']}' alt='' width='50' height='50' style='border-radius:6px;margin-right:8px;' />" if r.get("image") else ""
        
        # Note: strip() and no multiline indentation to keep it tight
        card = (
            f"<div style='display:flex;align-items:center;margin-bottom:8px;'>"
            f"{image_html}"
            f"<div><a href='{r['url']}' target='_blank' style='color:#0077cc;font-weight:bold;text-decoration:none;'>{title}</a>"
            f"<br><small>{description}...</small></div></div>"
        )
        html_cards.append(card)

    html_response = f"<p>{intro}</p>{''.join(html_cards)}"

    # Return only cleaned-up HTML message
    return success_response("Chatbot search results retrieved successfully.", {"message": html_response})
