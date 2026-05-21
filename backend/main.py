from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import users, projects, tasks
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager API", redirect_slashes=False)

import os
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(users.users_router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    return {"message": "Welcome to the Task Manager API"}
