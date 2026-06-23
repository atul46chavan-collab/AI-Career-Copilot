from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.schemas.resume import (
    ResumeAnalysisRequest,
    ResumeAnalysisResponse
)
from src.services.resume_service import ResumeService

router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)

# Instantiate the domain service
resume_service = ResumeService()


@router.post(
    "/analyze",
    response_model=ResumeAnalysisResponse,
    status_code=status.HTTP_200_OK
)
async def analyze_resume_endpoint(
    payload: ResumeAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Receives raw resume text and student_id, persists the resume, invokes the AI Recruiter Agent,
    persists the structured results in the database, and returns the analysis.
    """
    return await resume_service.analyze_and_persist_resume(
        db=db,
        student_id=payload.student_id,
        resume_text=payload.resume_text
    )

