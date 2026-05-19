from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import models, schemas, auth
from database import get_db

router = APIRouter(prefix="/api", tags=["tasks"])

@router.post("/projects/{project_id}/tasks", response_model=schemas.TaskResponse)
def create_task(project_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and not any(m.id == current_user.id for m in project.members):
        raise HTTPException(status_code=403, detail="Not authorized to add tasks to this project")
        
    if task.assigned_to:
        user = db.query(models.User).filter(models.User.id == task.assigned_to).first()
        if not user:
             raise HTTPException(status_code=404, detail="Assigned user not found")

    new_task = models.Task(**task.model_dump(), project_id=project_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/projects/{project_id}/tasks", response_model=List[schemas.TaskResponse])
def get_tasks_for_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.id and not any(m.id == current_user.id for m in project.members):
        raise HTTPException(status_code=403, detail="Not authorized to view tasks of this project")
        
    tasks = db.query(models.Task).filter(models.Task.project_id == project_id).all()
    return tasks

@router.get("/tasks", response_model=List[schemas.TaskResponse])
def get_my_tasks(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == models.RoleEnum.admin:
        tasks = db.query(models.Task).join(models.Project).filter(
            (models.Project.owner_id == current_user.id) | 
            (models.Project.members.any(models.User.id == current_user.id))
        ).all()
    else:
        tasks = db.query(models.Task).filter(models.Task.assigned_to == current_user.id).all()
    return tasks


@router.put("/tasks/{task_id}", response_model=schemas.TaskResponse)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    is_owner_or_member = project.owner_id == current_user.id or any(m.id == current_user.id for m in project.members)
    if not is_owner_or_member:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")
        
    if task_update.status is not None:
        if task.assigned_to != current_user.id:
            raise HTTPException(status_code=403, detail="Only the assigned task member can change the status of this task")
        task.status = task_update.status
        
    if task_update.assigned_to is not None:
        if current_user.role != models.RoleEnum.admin:
            raise HTTPException(status_code=403, detail="Only administrators can assign tasks to members")
        task.assigned_to = task_update.assigned_to


    db.commit()
    db.refresh(task)
    return task

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
    if project.owner_id != current_user.id and not any(m.id == current_user.id for m in project.members):
        raise HTTPException(status_code=403, detail="Not authorized to delete tasks in this project")
        
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}

