from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.post("/", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_project = models.Project(**project.model_dump(), owner_id=current_user.id)
    new_project.members.append(current_user)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/", response_model=List[schemas.ProjectResponse])
def get_projects(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    projects = db.query(models.Project).filter(
        (models.Project.owner_id == current_user.id) | 
        (models.Project.members.any(models.User.id == current_user.id))
    ).all()
    return projects


@router.get("/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if project.owner_id != current_user.id and not any(m.id == current_user.id for m in project.members):
        raise HTTPException(status_code=403, detail="Not authorized to view this project")
        
    return project


@router.post("/{project_id}/members", response_model=schemas.ProjectResponse)
def add_project_member(project_id: int, member_data: schemas.ProjectMemberAdd, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if project.owner_id != current_user.id and current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Not authorized to modify project members")
        
    user_to_add = db.query(models.User).filter(models.User.id == member_data.user_id).first()
    if not user_to_add:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user_to_add in project.members:
        raise HTTPException(status_code=400, detail="User is already a member of this project")
        
    project.members.append(user_to_add)
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}/members/{user_id}", response_model=schemas.ProjectResponse)
def remove_project_member(project_id: int, user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if project.owner_id != current_user.id and current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Not authorized to modify project members")
        
    user_to_remove = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_remove:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user_to_remove not in project.members:
        raise HTTPException(status_code=400, detail="User is not a member of this project")
        
    project.members.remove(user_to_remove)
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if project.owner_id != current_user.id and current_user.role != models.RoleEnum.admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted successfully"}

