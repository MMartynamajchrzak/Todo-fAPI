from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import models
from app.db import engine, SessionLocal

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


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


"""Get all todos"""
@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.ToDos).all()


"""get specific todo"""
@app.get("/todo/{todo_id}")
async def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.ToDos).filter(models.ToDos.id == todo_id).first()

    if todo_model:
        return todo_model
    raise http_exception()


"""create todo"""
@app.post("/")
async def create_todo(todo: Todo, db: Session = Depends(get_db)):
    todo_model = models.ToDos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    # add to db
    db.add(todo_model)
    db.commit()

    return successful_response(201)


@app.put("/{todo_id}")
async def update_todo(todo_id: int, todo: Todo, db: Session = Depends(get_db)):
    todo_model = db.query(models.ToDos).filter(models.ToDos.id == todo_id).first()

    if not todo_model:
        raise http_exception()

    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete

    db.add(todo_model)
    db.commit()

    return successful_response(200)


@app.delete("/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.ToDos).filter(models.ToDos.id == todo_id).first()

    if not todo_model:
        raise http_exception()

    db.query(models.ToDos).filter(models.ToDos.id == todo_id).delete()
    db.commit()

    return successful_response(204)


def successful_response(status_code: int) -> dict:
    return {
        "status_code": status_code,
        "transaction": "Successful"
    }


def http_exception():
    return HTTPException(status_code=404, detail="Todo not found!")
