from fastapi import FastAPI
from src.api.student import router as student_router
from src.api.health import router as health_router
from src.api.resume import router as resume_router
from src.api.job_description import router as job_description_router
from src.api.skill_gap import router as skill_gap_router
from src.config.settings import settings
from src.database.session import test_connection
from src.database.connection import engine
from src.database.base import Base

import src.models
Base.metadata.create_all(bind=engine)
test_connection()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.include_router(health_router)
app.include_router(student_router)
app.include_router(resume_router)
app.include_router(job_description_router)
app.include_router(skill_gap_router)



@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}"
    }

@app.get("/config")
async def config():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }