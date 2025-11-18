from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.projects import Projects
from app.models.users import User
from app.schemas.projects import ProjectResponse,ProjectCreate,ProjectUpdate
from app.utils.response import success_response, error_response
from app.database import get_db
from app.utils.utils import  require_admin


router = APIRouter(prefix="/projects", tags=["Projects"])




# ----------- Public Endpoint -----------
@router.get("/all")
def get_projects_home(db: Session = Depends(get_db)):
    projects = db.query(Projects).order_by(Projects.CreatedAt.desc()).all()
    projects_data = [ProjectResponse.from_orm(p).dict() for p in projects]
    return success_response("Projects retrieved successfully", projects_data)

# ----------- Admin Endpoints -----------
@router.get("/admin")
def get_all_projects_admin(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    projects = db.query(Projects).order_by(Projects.CreatedAt.desc()).all()
    projects_data = [ProjectResponse.from_orm(p).dict() for p in projects]
    return success_response("Projects retrieved successfully", projects_data)

@router.get("/{project_id}")
def get_project(project_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    project = db.query(Projects).filter(Projects.ProjectID == project_id).first()
    if not project:
        return error_response("Project not found", "NOT_FOUND")
    project_data = ProjectResponse.from_orm(project).dict()
    return success_response("Project retrieved successfully", project_data)

@router.post("/add")
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    new_project = Projects(
        **payload.dict(),
        CreatedAt=datetime.utcnow(),
        CreatedByUserID=current_user.UserID
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    project_data = ProjectResponse.from_orm(new_project).dict()
    return success_response("Project created successfully", project_data)



# Update project (use ProjectUpdate with partial fields)
@router.put("/{project_id}")
def update_project(
    project_id: int,
    payload: ProjectUpdate = Body(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    project = db.query(Projects).filter(Projects.ProjectID == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(project, field, value)
    project.UpdatedAt = datetime.utcnow()
    project.UpdatedByUserID = current_user.UserID
    db.commit()
    db.refresh(project)
    project_data = ProjectResponse.from_orm(project).dict()
    return success_response("Project updated successfully", project_data)




@router.delete("/{project_id}")
def delete_project(project_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    project = db.query(Projects).filter(Projects.ProjectID == project_id).first()
    if not project:
        return error_response("Project not found", "NOT_FOUND")
    db.delete(project)
    db.commit()
    return success_response("Project deleted successfully" )
