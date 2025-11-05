from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import os, shutil
from urllib.parse import quote

from .database import SessionLocal
from .models import Product
from .schemas import ProductResponse, ProductCreate, ProductUpdate
from .auth import OptionalJWTBearer
from .utils import success_response, error_response


router = APIRouter(prefix="/products", tags=["Products"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def format_product(product: Product, request: Request) -> dict:
    item = ProductResponse.from_orm(product).dict()
    if item.get("ImagePath"):
        imagename = quote(os.path.basename(item["ImagePath"]))
        item["ImagePath"] = f"{request.base_url}static/Products/images/{imagename}"
    if item.get("VideoPath"):
        videoname = quote(os.path.basename(item["VideoPath"]))
        item["VideoPath"] = f"{request.base_url}static/Products/videos/{videoname}"
    return item


@router.get("/all")
def get_all_products(request: Request, db: Session = Depends(get_db)):
    products = (
        db.query(Product)
        .filter(Product.IsDeleted != True)
        .order_by(Product.CreatedAt.desc())
        .all()
    )
    data = [format_product(p, request) for p in products]
    return success_response("Products retrieved successfully", data)


def require_admin(payload: Optional[dict] = Depends(OptionalJWTBearer())):
    if not payload or payload.get("role_id") != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return payload


@router.get("/admin")
def get_all_products_admin(request: Request, _: dict = Depends(require_admin), db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.CreatedAt.desc()).all()
    data = [format_product(p, request) for p in products]
    return success_response("Products retrieved successfully", data)


@router.get("/{product_id}")
def get_product(product_id: int, request: Request, _: dict = Depends(require_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.ProductID == product_id, Product.IsDeleted != True).first()
    if not product:
        return error_response("Product not found", "NOT_FOUND")
    data = format_product(product, request)
    return success_response("Product retrieved successfully", data)


@router.post("/add")
def create_product(
    NameEn: str = Form(...),
    NameAr: Optional[str] = Form(None),
    DescriptionEn: Optional[str] = Form(None),
    DescriptionAr: Optional[str] = Form(None),
    ServicesName: Optional[str] = Form(None),
    ServicesDescription: Optional[str] = Form(None),
    ServicesLink: Optional[str] = Form(None),
    ImagePath: Optional[UploadFile] = File(None),
    VideoPath: Optional[UploadFile] = File(None),
    payload: dict = Depends(require_admin),
    db: Session = Depends(get_db),
    request: Request = None
):
    image_path = None
    video_path = None

    if ImagePath:
        os.makedirs("/app/static/Products/images", exist_ok=True)
        image_path = f"/app/static/Products/images/{ImagePath.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(ImagePath.file, buffer)

    if VideoPath:
        os.makedirs("/app/static/Products/videos", exist_ok=True)
        video_path = f"/app/static/Products/videos/{VideoPath.filename}"
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(VideoPath.file, buffer)

    new_product = Product(
        NameEn=NameEn,
        NameAr=NameAr,
        DescriptionEn=DescriptionEn,
        DescriptionAr=DescriptionAr,
        ServicesName=ServicesName,
        ServicesDescription=ServicesDescription,
        ServicesLink=ServicesLink,
        ImagePath=image_path,
        VideoPath=video_path,
        CreatedAt=datetime.utcnow(),
        CreatedByUserID=payload.get("user_id"),
        IsDeleted=False
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    data = format_product(new_product, request)
    return success_response("Product created successfully", data)


@router.put("/{product_id}")
def update_product(
    product_id: int,
    NameEn: Optional[str] = Form(None),
    NameAr: Optional[str] = Form(None),
    DescriptionEn: Optional[str] = Form(None),
    DescriptionAr: Optional[str] = Form(None),
    ServicesName: Optional[str] = Form(None),
    ServicesDescription: Optional[str] = Form(None),
    ServicesLink: Optional[str] = Form(None),
    ImagePath: Optional[UploadFile] = File(None),
    VideoPath: Optional[UploadFile] = File(None),
    payload: dict = Depends(require_admin),
    db: Session = Depends(get_db),
    request: Request = None
):
    product = db.query(Product).filter(Product.ProductID == product_id, Product.IsDeleted != True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if NameEn is not None: product.NameEn = NameEn
    if NameAr is not None: product.NameAr = NameAr
    if DescriptionEn is not None: product.DescriptionEn = DescriptionEn
    if DescriptionAr is not None: product.DescriptionAr = DescriptionAr
    if ServicesName is not None: product.ServicesName = ServicesName
    if ServicesDescription is not None: product.ServicesDescription = ServicesDescription
    if ServicesLink is not None: product.ServicesLink = ServicesLink

    if ImagePath:
        os.makedirs("/app/static/Products/images", exist_ok=True)
        if product.ImagePath and os.path.exists(product.ImagePath):
            try:
                os.remove(product.ImagePath)
            except OSError:
                pass
        image_path = f"/app/static/Products/images/{ImagePath.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(ImagePath.file, buffer)
        product.ImagePath = image_path

    if VideoPath:
        os.makedirs("/app/static/Products/videos", exist_ok=True)
        if product.VideoPath and os.path.exists(product.VideoPath):
            try:
                os.remove(product.VideoPath)
            except OSError:
                pass
        video_path = f"/app/static/Products/videos/{VideoPath.filename}"
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(VideoPath.file, buffer)
        product.VideoPath = video_path

    product.UpdatedAt = datetime.utcnow()
    product.UpdatedByUserID = payload.get("user_id")
    db.commit()
    db.refresh(product)
    data = format_product(product, request)
    return success_response("Product updated successfully", data)


@router.delete("/{product_id}")
def delete_product(product_id: int, payload: dict = Depends(require_admin), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.ProductID == product_id, Product.IsDeleted != True).first()
    if not product:
        return error_response("Product not found", "NOT_FOUND")
    product.IsDeleted = True
    product.UpdatedAt = datetime.utcnow()
    product.UpdatedByUserID = payload.get("user_id")
    db.commit()
    return success_response("Product soft-deleted successfully")


