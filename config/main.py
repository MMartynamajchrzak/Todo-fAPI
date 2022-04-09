from fastapi import FastAPI

from apps.Todos import todos
from apps.Users import auth, models
from config.db import engine
from starlette.staticfiles import StaticFiles

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(todos.router)
