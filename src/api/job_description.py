from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.schemas.job_description import (
    JobDescriptionRequest,
    JobDescriptionResponse
)
from src.services.jd_service import JobDescriptionService

router = APIRouter(
    prefix="/job-descriptions",
    tags=["Job Descriptions"]
)

# Instantiate the domain service
jd_service = JobDescriptionService()


@router.post(
    "/analyze",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_200_OK
)
async def analyze_jd_endpoint(
    payload: JobDescriptionRequest,
    db: Session = Depends(get_db)
):
    """
    Receives raw job description text and student_id, invokes the AI Recruiter Agent,
    persists both raw text and extracted parameters in PostgreSQL, and returns structured feedback.
    """
    return await jd_service.analyze_and_persist_jd(
        db=db,
        student_id=payload.student_id,
        jd_text=payload.job_description
    )
