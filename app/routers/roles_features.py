from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.role_feature import Role, AppFeature, RoleApp
from app.schemas.role_feature import *
from app.utils.response import success_response, error_response
from app.utils.utils import require_admin, get_current_user
from app.models.users import User

router = APIRouter(prefix="/features", tags=["App Features & Roles"])


# ---------------------- APP FEATURES ----------------------

@router.post("/appfeatures", dependencies=[Depends(require_admin)])
def create_app_feature(payload: AppFeatureCreate, db: Session = Depends(get_db)):
    feature = AppFeature(**payload.dict())
    db.add(feature)
    db.commit()
    db.refresh(feature)
    return success_response("App feature created successfully", {"AppFeatureID": feature.AppFeatureID})


@router.get("/appfeatures" , dependencies=[Depends(require_admin)])
def get_all_features(db: Session = Depends(get_db)):
    features = db.query(AppFeature).all()
    data = []
    for f in features:
        role_ids = [ra.RoleID for ra in f.role_apps]  # get all roles linked to this feature
        data.append({
            "AppFeatureID": f.AppFeatureID,
            "NameEn": f.NameEn,
            "NameAr": f.NameAr,
            "DescriptionEn": f.DescriptionEn,
            "DescriptionAr": f.DescriptionAr,
            "Link": f.Link,
            "RoleIDs": role_ids,  # ✅ include related Role IDs
        })
    return success_response("App features retrieved successfully", data)


@router.put("/appfeatures/{feature_id}", dependencies=[Depends(require_admin)])
def update_feature(feature_id: int, payload: AppFeatureUpdate, db: Session = Depends(get_db)):
    feature = db.query(AppFeature).filter(AppFeature.AppFeatureID == feature_id).first()
    if not feature:
        return error_response("Feature not found", "NOT_FOUND")

    for key, value in payload.dict(exclude_unset=True).items():
        setattr(feature, key, value)
    db.commit()
    db.refresh(feature)
    return success_response("Feature updated successfully", {"AppFeatureID": feature.AppFeatureID})


@router.delete("/appfeatures/{feature_id}", dependencies=[Depends(require_admin)])
def delete_feature(feature_id: int, db: Session = Depends(get_db)):
    feature = db.query(AppFeature).filter(AppFeature.AppFeatureID == feature_id).first()
    if not feature:
        return error_response("Feature not found", "NOT_FOUND")
    db.delete(feature)
    db.commit()
    return success_response("Feature deleted successfully", None)


# ---------------------- ROLES ----------------------

@router.post("/roles", dependencies=[Depends(require_admin)])
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    role = Role(**payload.dict())
    db.add(role)
    db.commit()
    db.refresh(role)
    return success_response("Role created successfully", {"RoleID": role.RoleID})


@router.get("/roles", dependencies=[Depends(require_admin)])
def get_all_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    data = []
    for r in roles:
        data.append({
            "RoleID": r.RoleID,
            "NameEn": r.NameEn,
            "NameAr": r.NameAr,
            "Features": [
                {"AppFeatureID": f.AppFeatureID, "NameEn": f.NameEn, "Link": f.Link}
                for f in r.features
            ]
        })
    return success_response("Roles retrieved successfully", data)


@router.post("/roles/{role_id}/assign_features", dependencies=[Depends(require_admin)])
def assign_features_to_role(
    role_id: int,
    feature_ids: list[int],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    role = db.query(Role).filter(Role.RoleID == role_id).first()
    if not role:
        return error_response("Role not found", "NOT_FOUND")

    # --- Get existing RoleApp links ---
    existing_links = db.query(RoleApp).filter(RoleApp.RoleID == role_id).all()
    existing_feature_ids = {link.AppFeatureID for link in existing_links}

    # --- Compute differences ---
    new_feature_ids = set(feature_ids)
    to_add = new_feature_ids - existing_feature_ids
    to_remove = existing_feature_ids - new_feature_ids

    # --- Add new RoleApp entries ---
    for fid in to_add:
        db.add(RoleApp(RoleID=role_id, AppFeatureID=fid, CreatedByUserID=user.UserID))

    # --- Remove RoleApp entries not included anymore ---
    if to_remove:
        db.query(RoleApp).filter(
            RoleApp.RoleID == role_id,
            RoleApp.AppFeatureID.in_(to_remove)
        ).delete(synchronize_session=False)

    db.commit()

    return success_response(
        "Features updated successfully",
        {
            "RoleID": role.RoleID,
            "AddedFeatures": list(to_add),
            "RemovedFeatures": list(to_remove),
            "CurrentFeatures": list(new_feature_ids)
        }
    )



@router.get("/roles/{role_id}")
def get_role_details(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.RoleID == role_id).first()
    if not role:
        return error_response("Role not found", "NOT_FOUND")

    data = {
        "RoleID": role.RoleID,
        "NameEn": role.NameEn,
        "NameAr": role.NameAr,
        "Features": [
            {"AppFeatureID": f.AppFeatureID, "NameEn": f.NameEn, "Link": f.Link}
            for f in role.features
        ]
    }
    return success_response("Role details retrieved successfully", data)
