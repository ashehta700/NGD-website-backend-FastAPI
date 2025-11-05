from fastapi import APIRouter, Depends, Body, Request
from sqlalchemy.orm import Session
from rapidfuzz import fuzz, process
from urllib.parse import quote
from app.database import get_db
from app.models.faq import FAQ
from app.models.metadata import DatasetInfo, MetadataInfo
from app.models.news import News
from app.models.products import Product
from app.models.projects import Projects
from app.models.manual_guide import ManualGuide
from app.models.videos import Video
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

FALLBACK_MESSAGE = {
    "en": "Sorry, I couldn’t find an exact answer to that. You can contact our team at <a href='https://ngd.com/contact' target='_blank'>Customer Support</a> or call +966-XXX-XXXX.",
    "ar": "عذرًا، لم أجد إجابة دقيقة على سؤالك. يمكنك التواصل مع <a href='https://ngd.com/contact' target='_blank'>خدمة العملاء</a> أو الاتصال على +966-XXX-XXXX."
}


def build_image_url(request: Request, image_path):
    if not image_path:
        return None
    if image_path.startswith("app"):
        image_path = image_path[3:]
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}{quote(image_path)}"


def collect_search_data(db: Session):
    """Collect all searchable items (both Arabic and English fields)"""
    data = []

    def add_item(id, model, category, title_en, title_ar, desc_en, desc_ar, url, image):
        data.append({
            "id": id,
            "model": model,
            "category": category,
            "title_en": title_en or "",
            "title_ar": title_ar or "",
            "desc_en": desc_en or "",
            "desc_ar": desc_ar or "",
            "url": url,
            "image": image
        })

    # FAQ
    for f in db.query(FAQ).filter(FAQ.IsDelete == False).all():
        add_item(f.FAQID, "FAQ", "FAQ", f.QuestionEn, f.QuestionAr, f.AnswerEn, f.AnswerAr, f"/faq/{f.FAQID}", None)

    # DatasetInfo
    for d in db.query(DatasetInfo).all():
        add_item(d.DatasetID, "DatasetInfo", "Metadata", d.Name, d.NameAr, d.description, d.descriptionAr,
                 f"/datasets/{d.DatasetID}", getattr(d, "img", None))

    # MetadataInfo
    for m in db.query(MetadataInfo).all():
        add_item(m.MetadataID, "MetadataInfo", "Metadata", m.Name, m.NameAr, m.description, m.descriptionAr,
                 f"/metadata/{m.MetadataID}", getattr(m, "ImageUrl", None))

    # News
    for n in db.query(News).all():
        add_item(n.NewsID, "News", "News", n.TitleEn, n.TitleAr, n.DescriptionEn, n.DescriptionAr,
                 f"/news/{n.NewsID}", getattr(n, "ImagePath", None))

    # Product
    for p in db.query(Product).all():
        add_item(p.ProductID, "Product", "Products", p.NameEn, p.NameAr, p.DescriptionEn, p.DescriptionAr,
                 f"/products/{p.ProductID}", getattr(p, "ImagePath", None))

    # Projects
    for pr in db.query(Projects).all():
        add_item(pr.ProjectID, "Project", "Projects", pr.NameEn, pr.NameAr, pr.DescriptionEn, pr.DescriptionAr,
                 f"/projects/{pr.ProjectID}", getattr(pr, "ImagePath", None))

    # ManualGuide
    for g in db.query(ManualGuide).all():
        add_item(g.ManualGuideID, "ManualGuide", "ManualGuide", g.NameEn, g.NameAr, g.DescriptionEn, g.DescriptionAr,
                 f"/manual-guides/{g.ManualGuideID}", getattr(g, "ImageUrl", None))

    # Videos
    for v in db.query(Video).all():
        add_item(v.VideoID, "Video", "Videos", v.TitleEn, v.TitleAr, v.DescriptionEn, v.DescriptionAr,
                 f"/videos/{v.VideoID}", getattr(v, "ImagePath", None))

    return data


@router.post("/ask")
def ask_chatbot(
    request: Request,
    user_question: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Chatbot endpoint (auto language detection):
    - Searches across all models (FAQ, News, Products, etc.)
    - Matches Arabic and English fields automatically
    - Returns up to 3 human-style, clickable HTML responses
    """
    all_data = collect_search_data(db)
    if not all_data:
        return error_response("No data available for chatbot search.", "NO_DATA")

    # Combine both Arabic and English text for matching
    combined_texts = [
        f"{item['title_en']} {item['title_ar']} {item['desc_en']} {item['desc_ar']}".strip()
        for item in all_data
    ]

    # Fuzzy match user question against all text
    matches = process.extract(user_question, combined_texts, scorer=fuzz.token_sort_ratio, limit=3)

    results = []
    for match_text, score, index in matches:
        if score >= 25:  # minimum similarity threshold
            item = all_data[index]

            # Choose best language for response (auto detect)
            is_arabic = any("\u0600" <= ch <= "\u06FF" for ch in user_question)
            title = item["title_ar"] if is_arabic and item["title_ar"] else item["title_en"]
            desc = item["desc_ar"] if is_arabic and item["desc_ar"] else item["desc_en"]

            html_card = f"""
            <div style='margin-bottom:12px;'>
                <a href='{item["url"]}' target='_blank' style='text-decoration:none;color:#0077cc;font-weight:bold;'>{title}</a><br>
                <small>{(desc or '')[:120]}...</small>
            </div>
            """
            results.append(html_card)

    if not results:
        # Auto choose fallback language
        is_arabic = any("\u0600" <= ch <= "\u06FF" for ch in user_question)
        fallback_msg = FALLBACK_MESSAGE["ar"] if is_arabic else FALLBACK_MESSAGE["en"]
        return success_response("No relevant answers found.", {
            "message": fallback_msg,
            "answers": []
        })

    # Intro text
    is_arabic = any("\u0600" <= ch <= "\u06FF" for ch in user_question)
    intro = "وجدت بعض النتائج التي قد تساعدك:" if is_arabic else "I found a few things that might help you:"

    html_response = f"<p>{intro}</p>" + "".join(results)

    return success_response(
        "Chatbot search results retrieved successfully.",
        {"message": html_response, "answers": results}
    )
