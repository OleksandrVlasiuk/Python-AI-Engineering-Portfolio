from sqlalchemy import and_
from sqlalchemy.orm import Session
from typing import List
from schemas.schemas import UserAuthBackend
from models.model import User, Task
from schemas.schemas import TaskCreate


def get_user_by_id(db: Session, user_id):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email):
    return db.query(User).filter(User.email == email).first()


def get_task_by_id(db: Session, task_id: int) -> Task:
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks_by_user_id(db: Session, user_id: int) -> List[Task]:
    return db.query(Task).filter(Task.user_id == user_id).all()


def get_all_tasks(db: Session) -> List[Task]:
    return db.query(Task).filter().all()


def get_all_not_started_tasks(db: Session) -> List[Task]:
    return db.query(Task).filter(
        and_(
            Task.status == "Not started",
            Task.file_name.isnot(None)
        )
    ).all()


def get_all_user_not_started_tasks(db: Session, user_id: int) -> List[Task]:
    return db.query(Task).filter(
        and_(
            Task.status == "Not started",
            Task.user_id == user_id
        )
    ).all()


def create_task(db: Session, task_create: TaskCreate) -> Task:
    task_create_obj = Task(**task_create.dict())
    db.add(task_create_obj)
    db.commit()
    db.refresh(task_create_obj)
    return task_create_obj


def create_user(db: Session, user_create: UserAuthBackend):
    user_create_obj = User(**user_create.dict())
    db.add(user_create_obj)
    db.commit()
    db.refresh(user_create_obj)
    return user_create_obj


def update_task_file_name(db: Session, task_id: int, file_name: str) -> Task:
    db_task = db.query(Task).filter(Task.id == task_id).first()
    db_task.file_name = file_name
    db.commit()
    return db_task


def update_task_status(db: Session, task_id: int, status: str):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    db_task.status = status
    db.commit()
    return db_task


def delete_task_by_id(db: Session, task_id: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return True
    return False

