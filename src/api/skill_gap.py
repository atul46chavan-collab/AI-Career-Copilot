from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.schemas.skill_gap import SkillGapRequest, SkillGapResponse
from src.services.skill_gap_service import SkillGapService

router = APIRouter(
    prefix="/skill-gaps",
    tags=["Skill Gaps"]
)

# Instantiate the domain service
skill_gap_service = SkillGapService()


@router.post(
    "/analyze",
    response_model=SkillGapResponse,
    status_code=status.HTTP_200_OK
)
async def analyze_skill_gap_endpoint(
    payload: SkillGapRequest,
    db: Session = Depends(get_db)
):
    """
    Compares a candidate's resume analysis and a job description.
    Retrieves the extracted skills, performs deterministic set matching in Python,
    calculates an overlap gap score, and utilizes Gemini to prioritize missing skills
    and generate career guidance recommendations.
    """
    return await skill_gap_service.generate_skill_gap(
        db=db,
        resume_analysis_id=payload.resume_analysis_id,
        job_description_id=payload.job_description_id
    )
