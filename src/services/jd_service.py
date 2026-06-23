from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.models.student import Student
from src.models.job_description import JobDescription
from src.agents.jd_agent import JobDescriptionAgent


class JobDescriptionService:
    """
    Service responsible for coordinating job description parsing,
    invoking the JD Agent, and managing database operations.
    """

    def __init__(self, jd_agent: JobDescriptionAgent | None = None):
        self.jd_agent = jd_agent or JobDescriptionAgent()

    async def analyze_and_persist_jd(
        self,
        db: Session,
        student_id: int,
        jd_text: str
    ) -> dict:
        """
        Processes a raw job description post:
        1. Validates that the target student exists in the database.
        2. Calls the JDAgent to extract structured parameters via Gemini API.
        3. Persists the raw text and JSON-serialized metadata in the `job_descriptions` table.
        4. Returns the combined response schema including the generated `jd_id`.
        """
        # 1. Verify student exists in the database
        db_student = db.query(Student).filter(Student.id == student_id).first()
        if not db_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} does not exist in the system."
            )

        try:
            # 2. Extract structured details from job post via Agent
            agent_response = await self.jd_agent.analyze_jd(jd_text)

            # 3. Store raw text and structured metadata in database
            db_jd = JobDescription(
                student_id=student_id,
                title=agent_response.job_title,
                company=agent_response.company_name,
                jd_text=jd_text,
                extracted_data={
                    "required_skills": agent_response.required_skills,
                    "preferred_skills": agent_response.preferred_skills,
                    "experience_required": agent_response.experience_required,
                    "education_requirements": agent_response.education_requirements,
                    "responsibilities": agent_response.responsibilities
                }
            )
            db.add(db_jd)
            db.commit()
            db.refresh(db_jd)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to generate or persist job description analysis: {str(e)}"
            )

        # 4. Map and return response properties
        return {
            "jd_id": db_jd.id,
            "job_title": db_jd.title,
            "company_name": db_jd.company,
            "required_skills": agent_response.required_skills,
            "preferred_skills": agent_response.preferred_skills,
            "experience_required": agent_response.experience_required,
            "education_requirements": agent_response.education_requirements,
            "responsibilities": agent_response.responsibilities
        }
