from typing import Optional

from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from apps.Todos import models
from apps.Users.auth import get_current_user
from config.db import engine, SessionLocal
from apps.exceptions import get_user_exception

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={
        404: {"description": "Not found"}
    }
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="Templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description="Priority must be between 1-5")
    complete: bool


@router.get("/test")
async def test(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


"""Get all todos"""
@router.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.ToDos).all()


"""Get all todos for a given user"""
@router.get("/user")
async def read_all_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise get_user_exception()
    return db.query(models.ToDos).filter(models.ToDos.owner_id == user.get("id")).all()


"""Get specific todo"""
@router.get("/{todo_id}")
async def read_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise get_user_exception()

    todo_model = db.query(models.ToDos)\
        .filter(models.ToDos.id == todo_id)\
        .filter(models.ToDos.owner_id == user.get("id"))\
        .first()

    if todo_model:
        return todo_model
    raise http_exception()


"""Create todo"""
@router.post("/")
async def create_todo(todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        get_user_exception()

    todo_model = models.ToDos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get("id")

    # add to db
    db.add(todo_model)
    db.commit()

    return successful_response(201)


"""Update given todo"""
@router.put("/{todo_id}")
async def update_todo(todo_id: int, todo: Todo, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        get_user_exception()

    todo_model = db.query(models.ToDos)\
        .filter(models.ToDos.id == todo_id)\
        .filter(models.ToDos.owner_id == user.get("id"))\
        .first()

    if not todo_model:
        raise http_exception()

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

    return successful_response(200)


"""Delete given todo"""
@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if not user:
        raise get_user_exception()
    todo_model = db.query(models.ToDos).filter(models.ToDos.id == todo_id)\
        .filter(models.ToDos.owner_id == user.get("id"))\
        .first()

    if not todo_model:
        raise http_exception()

    db.query(models.ToDos).filter(models.ToDos.id == todo_id).delete()
    db.commit()

    return successful_response(204)


"""Returns dict with successful response"""
def successful_response(status_code: int) -> dict:
    return {
        "status_code": status_code,
        "transaction": "Successful"
    }


"""Returns Http exception"""
def http_exception():
    return HTTPException(status_code=404, detail="Todo not found!")
