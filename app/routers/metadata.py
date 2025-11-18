from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form ,Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.metadata import DatasetInfo, MetadataInfo
from app.schemas.metadata import (
    DatasetInfoCreate, DatasetInfoUpdate, DatasetInfoResponse,
    MetadataInfoCreate, MetadataInfoUpdate, MetadataInfoResponse
)
from app.utils.response import success_response, error_response
from app.utils.utils import require_admin
from app.utils.paths import static_path
import os
import shutil
from urllib.parse import quote
from typing import Optional
from datetime import date




router = APIRouter(prefix="/metadata", tags=["Metadata"])


# ---------- Helpers ----------


def build_image_url(request: Request, image_path: Optional[str]) -> Optional[str]:
    if not image_path:
        return None
    base_url = str(request.base_url).rstrip("/")
    return f"{base_url}/static/{quote(image_path)}"







# -------------------- PUBLIC ENDPOINTS --------------------
#  get the datasets only for the dropdown and the CARDs on Home page 
@router.get("/datasets")
def get_all_datasets_with_metadata(request: Request , db: Session = Depends(get_db)):
    """
    Get all datasets with their related metadata.
    """
    datasets = db.query(DatasetInfo).filter(DatasetInfo.IsDeleted == False).all()

    if not datasets:
        return error_response("No datasets found", "NO_DATASETS")

    data = []
    for dataset in datasets:
        metadata_list = (
            db.query(MetadataInfo)
            .all()
        )

        data.append({
            "DatasetID": dataset.DatasetID,
            "Name": dataset.Name,
            "NameAr": dataset.NameAr,
            "Title": dataset.Title,
            "TitleAr": dataset.TitleAr,
            # "Description": dataset.description,
            # "DescriptionAr": dataset.descriptionAr,
            "CRS_Name": dataset.CRS_Name,
            "EPSG": dataset.EPSG,
            "Keywords": dataset.Keywords,
            "KeywordsAr": dataset.KeywordsAr,
            "Img": build_image_url(request, dataset.img),
            
        })

    return success_response("Datasets with metadata retrieved successfully", data)

# get the specific dataset with its related metadata 
@router.get("/datasets/{dataset_id}")
def get_dataset_with_metadata(request: Request , dataset_id: int, db: Session = Depends(get_db)):
    """
    Get a single dataset with its related metadata entries.
    """
    dataset = db.query(DatasetInfo).filter(DatasetInfo.DatasetID == dataset_id).first()


    if not dataset:
        return error_response("Dataset not found", "NOT_FOUND")

    metadata_list = (
        db.query(MetadataInfo).filter(MetadataInfo.DatasetID == dataset_id , MetadataInfo.IsDeleted == False).all()
    )

    data = {
        "DatasetID": dataset.DatasetID,
        "Name": dataset.Name,
        "NameAr": dataset.NameAr,
        "Title": dataset.Title,
        "TitleAr": dataset.TitleAr,
        "Description": dataset.description,
        "DescriptionAr": dataset.descriptionAr,
        "CRS_Name": dataset.CRS_Name,
        "EPSG": dataset.EPSG,
        "Keywords": dataset.Keywords,
        "KeywordsAr": dataset.KeywordsAr,
        "Img": build_image_url(request, dataset.img),
        "Metadata": [
            {
                "MetadataID": m.MetadataID,
                "Name": m.Name,
                "NameAr": m.NameAr,
                "Title": m.Title,
                "TitleAr": m.TitleAr,
                "Description": m.description,
                "DescriptionAr": m.descriptionAr,
                # "URL": m.URL,
                # "CreationDate": m.CreationDate,
                # "Bounds": {
                #     "West": m.WestBound,
                #     "East": m.EastBound,
                #     "North": m.NorthBound,
                #     "South": m.SouthBound,
                # },
                # "Contact": {
                #     "ContactName": m.ContactName,
                #     "PositionName": m.PositionName,
                #     "Organization": m.Organization,
                #     "Email": m.Email,
                #     "Phone": m.Phone,
                #     "Role": m.Role,
                # },
            }
            for m in metadata_list
        ],
    }

    return success_response("Dataset with metadata retrieved successfully", data)


# get the all link services for the dataset only from the metadata
@router.get("/datasets/{dataset_id}/services")
def get_dataset_with_metadata(dataset_id: int, db: Session = Depends(get_db)):
    """
    Get a single dataset with its related metadata entries.
    """
    dataset = db.query(DatasetInfo).filter(DatasetInfo.DatasetID == dataset_id).first()

    if not dataset:
        return error_response("Dataset not found", "NOT_FOUND")

    metadata_list = (
        db.query(MetadataInfo).filter(MetadataInfo.DatasetID == dataset_id ,MetadataInfo.IsDeleted == False).all()
    )

    data = {
        "DatasetID": dataset.DatasetID,
        "Name": dataset.Name,
        "NameAr": dataset.NameAr,
        "Metadata_servicesLink": [
            {
                "MetadataID": m.MetadataID,
                "Name": m.Name,
                "NameAr": m.NameAr,
                "URL": m.URL,
            }
            for m in metadata_list
        ],
    }

    return success_response("Dataset with metadata retrieved successfully", data)


# get the details for the specific dataset 
@router.get("/metadata/{metadata_id}")
def get_metadata_details(request: Request , metadata_id: int, db: Session = Depends(get_db)):
    """
    Get detailed metadata information by MetadataID.
    """
    metadata = db.query(MetadataInfo).filter(MetadataInfo.MetadataID ==metadata_id, MetadataInfo.IsDeleted == False).first()

    if not metadata:
        return error_response("Metadata not found", "NOT_FOUND")

    data = {
        "MetadataID": metadata.MetadataID,
        "DatasetID": metadata.DatasetID,
        "Name": metadata.Name,
        "NameAr": metadata.NameAr,
        "Title": metadata.Title,
        "TitleAr": metadata.TitleAr,
        "Description": metadata.description,
        "DescriptionAr": metadata.descriptionAr,
        "CreationDate": metadata.CreationDate,
        "ServicesURL": metadata.URL,
        "DocumentPath": build_image_url(request, metadata.FilePath),
        "Bounds": {
            "West": metadata.WestBound,
            "East": metadata.EastBound,
            "North": metadata.NorthBound,
            "South": metadata.SouthBound,
        },
        "MetadataStandard": {
            "Name": metadata.MetadataStandardName,
            "Version": metadata.MetadataStandardVersion,
        },
        "Contact": {
            "ContactName": metadata.ContactName,
            "PositionName": metadata.PositionName,
            "Organization": metadata.Organization,
            "Email": metadata.Email,
            "Phone": metadata.Phone,
            "Role": metadata.Role,
        },
    }

    return success_response("Metadata details retrieved successfully", data)


# -------------------- ADMIN ENDPOINTS --------------------

# ---- Dataset CRUD ----
@router.post("/admin/datasets")
def create_dataset(
    Name: str = Form(...),
    NameAr: str = Form(...),
    Title: str = Form(None),
    TitleAr: str = Form(None),
    description: str = Form(None),
    descriptionAr: str = Form(None),
    CRS_Name: str = Form(None),
    EPSG: int = Form(3857),
    Keywords: str = Form(None),
    KeywordsAr: str = Form(None),
    img: UploadFile = File(None),
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin)
):
    """
    Create a new dataset with optional image upload.
    """
    new_dataset = DatasetInfo(
        Name=Name,
        NameAr=NameAr,
        Title=Title,
        TitleAr=TitleAr,
        description=description,
        descriptionAr=descriptionAr,
        CRS_Name=CRS_Name,
        EPSG=EPSG,
        Keywords=Keywords,
        KeywordsAr=KeywordsAr,
        img=None
    )
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)

    # Handle image upload if provided
    if img:
        folder_path = static_path("dataset", str(new_dataset.DatasetID), ensure=True)
        file_path = os.path.join(folder_path, img.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)

        # Save relative path to DB
        new_dataset.img = f"dataset/{new_dataset.DatasetID}/{img.filename}"
        db.commit()

    return success_response("Dataset created successfully", {"DatasetID": new_dataset.DatasetID})


# -------------------- UPDATE DATASET --------------------
@router.put("/admin/datasets/{dataset_id}")
def update_dataset(
    dataset_id: int,
    Name: str = Form(None),
    NameAr: str = Form(None),
    Title: str = Form(None),
    TitleAr: str = Form(None),
    description: str = Form(None),
    descriptionAr: str = Form(None),
    CRS_Name: str = Form(None),
    EPSG: int = Form(None),
    Keywords: str = Form(None),
    KeywordsAr: str = Form(None),
    img: UploadFile = File(None),
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin)
):
    """
    Update dataset info and optionally replace the image.
    """
    dataset = db.query(DatasetInfo).filter(DatasetInfo.DatasetID == dataset_id).first()

    if not dataset:
        return error_response("Dataset not found", "NOT_FOUND")

    # Update fields if provided
    if Name is not None:
        dataset.Name = Name
    if NameAr is not None:
        dataset.NameAr = NameAr
    if Title is not None:
        dataset.Title = Title
    if TitleAr is not None:
        dataset.TitleAr = TitleAr
    if description is not None:
        dataset.description = description
    if descriptionAr is not None:
        dataset.descriptionAr = descriptionAr
    if CRS_Name is not None:
        dataset.CRS_Name = CRS_Name
    if EPSG is not None:
        dataset.EPSG = EPSG
    if Keywords is not None:
        dataset.Keywords = Keywords
    if KeywordsAr is not None:
        dataset.KeywordsAr = KeywordsAr

    # Handle image upload/replacement
    if img:
        folder_path = static_path("dataset", str(dataset.DatasetID), ensure=True)

        file_path = os.path.join(folder_path, img.filename)

        # Remove old image if exists
        if dataset.img:
            old_path = static_path(dataset.img)
            if os.path.exists(old_path):
                os.remove(old_path)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)

        dataset.img = f"dataset/{dataset.DatasetID}/{img.filename}"

    db.commit()
    db.refresh(dataset)

    return success_response("Dataset updated successfully", {"DatasetID": dataset.DatasetID})


# -------------------- DELETE DATASET --------------------
@router.delete("/admin/datasets/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db), admin_user=Depends(require_admin)):
    """
    Delete a dataset and its associated image and metadata.
    """
    dataset = db.query(DatasetInfo).filter(DatasetInfo.DatasetID == dataset_id).first()
    if not dataset:
        return error_response("Dataset not found", "NOT_FOUND")

    # Soft delete instead of removing
    dataset.IsDeleted = True

    db.commit()

    return success_response("Dataset was soft delete  successfully", {"DatasetID": dataset_id})



# ---- Metadata CRUD ----
@router.post("/admin/metadata")
def create_metadata(
    DatasetID: int = Form(...),
    Name: str = Form(...),
    NameAr: str = Form(...),
    Title: str = Form(None),
    TitleAr: str = Form(None),
    description: str = Form(None),
    descriptionAr: str = Form(None),
    CreationDate: Optional[date] = Form(None),
    URL: str = Form(None),
    WestBound: float = Form(None),
    EastBound: float = Form(None),
    NorthBound: float = Form(None),
    SouthBound: float = Form(None),
    MetadataStandardName: str = Form("ISO19115"),
    MetadataStandardVersion: str = Form("1.0"),
    ContactName: str = Form(None),
    PositionName: str = Form(None),
    Organization: str = Form(None),
    Email: str = Form(None),
    Phone: str = Form(None),
    Role: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    """
    Create new metadata with optional document upload.
    """
    # check dataset
    dataset = db.query(DatasetInfo).filter(DatasetInfo.DatasetID == DatasetID, DatasetInfo.IsDeleted == False).first()
    if not dataset:
        return error_response("Dataset not found or deleted", "NOT_FOUND")

    new_metadata = MetadataInfo(
        DatasetID=DatasetID,
        Name=Name,
        NameAr=NameAr,
        Title=Title,
        TitleAr=TitleAr,
        description=description,
        descriptionAr=descriptionAr,
        CreationDate=CreationDate,
        URL=URL,
        WestBound=WestBound,
        EastBound=EastBound,
        NorthBound=NorthBound,
        SouthBound=SouthBound,
        MetadataStandardName=MetadataStandardName,
        MetadataStandardVersion=MetadataStandardVersion,
        ContactName=ContactName,
        PositionName=PositionName,
        Organization=Organization,
        Email=Email,
        Phone=Phone,
        Role=Role,
        FilePath=None,
    )
    db.add(new_metadata)
    db.commit()
    db.refresh(new_metadata)

    # handle file upload
    if file:
        folder_path = static_path("dataset", str(DatasetID), "metadata", ensure=True)
        file_path = os.path.join(folder_path, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        new_metadata.FilePath = f"dataset/{DatasetID}/metadata/{file.filename}"
        db.commit()

    return success_response("Metadata created successfully", {"MetadataID": new_metadata.MetadataID})


@router.put("/admin/metadata/{metadata_id}")
def update_metadata(
    metadata_id: int,
    DatasetID: Optional[int] = Form(None),
    Name: Optional[str] = Form(None),
    NameAr: Optional[str] = Form(None),
    Title: Optional[str] = Form(None),
    TitleAr: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    descriptionAr: Optional[str] = Form(None),
    CreationDate: Optional[date] = Form(None),
    URL: Optional[str] = Form(None),
    WestBound: Optional[float] = Form(None),
    EastBound: Optional[float] = Form(None),
    NorthBound: Optional[float] = Form(None),
    SouthBound: Optional[float] = Form(None),
    MetadataStandardName: Optional[str] = Form(None),
    MetadataStandardVersion: Optional[str] = Form(None),
    ContactName: Optional[str] = Form(None),
    PositionName: Optional[str] = Form(None),
    Organization: Optional[str] = Form(None),
    Email: Optional[str] = Form(None),
    Phone: Optional[str] = Form(None),
    Role: Optional[str] = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    """
    Update metadata fields and optionally replace the attached document.
    """
    metadata = db.query(MetadataInfo).filter(MetadataInfo.MetadataID == metadata_id, MetadataInfo.IsDeleted == False).first()
    if not metadata:
        return error_response("Metadata not found", "NOT_FOUND")

    # Update only provided fields
    update_fields = {
        "DatasetID": DatasetID,
        "Name": Name,
        "NameAr": NameAr,
        "Title": Title,
        "TitleAr": TitleAr,
        "description": description,
        "descriptionAr": descriptionAr,
        "CreationDate": CreationDate,
        "URL": URL,
        "WestBound": WestBound,
        "EastBound": EastBound,
        "NorthBound": NorthBound,
        "SouthBound": SouthBound,
        "MetadataStandardName": MetadataStandardName,
        "MetadataStandardVersion": MetadataStandardVersion,
        "ContactName": ContactName,
        "PositionName": PositionName,
        "Organization": Organization,
        "Email": Email,
        "Phone": Phone,
        "Role": Role
    }

    for key, value in update_fields.items():
        if value is not None:
            setattr(metadata, key, value)

    # Replace file if uploaded
    if file:
        folder_path = static_path("dataset", str(metadata.DatasetID), "metadata", ensure=True)
        file_path = os.path.join(folder_path, file.filename)

        # delete old file if exists
        if metadata.FilePath:
            old_path = static_path(metadata.FilePath)
            if os.path.exists(old_path):
                os.remove(old_path)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        metadata.FilePath = f"dataset/{metadata.DatasetID}/metadata/{file.filename}"

    db.commit()
    db.refresh(metadata)

    return success_response("Metadata updated successfully", {"MetadataID": metadata.MetadataID})


@router.delete("/admin/metadata/{metadata_id}")
def delete_metadata(metadata_id: int, db: Session = Depends(get_db), user=Depends(require_admin)):
    """
    Soft delete metadata (mark IsDeleted=True)
    """
    metadata = db.query(MetadataInfo).filter(MetadataInfo.MetadataID == metadata_id).first()
    if not metadata:
        return error_response("Metadata not found", "NOT_FOUND")

    metadata.IsDeleted = True
    db.commit()

    return success_response("Metadata soft deleted successfully", {"MetadataID": metadata.MetadataID})