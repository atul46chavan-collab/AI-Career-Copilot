from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.models.student import Student
from src.models.resume import Resume
from src.models.analysis import ResumeAnalysis
from src.agents.resume_agent import ResumeAgent


class ResumeService:
    """
    Service layer responsible for handling resume parsing business rules,
    invoking the Resume Agent, and managing database persistence.
    """

    def __init__(self, resume_agent: ResumeAgent | None = None):
        self.resume_agent = resume_agent or ResumeAgent()

    async def analyze_and_persist_resume(
        self,
        db: Session,
        student_id: int,
        resume_text: str
    ) -> dict:
        """
        Orchestrates the resume analysis and database persistence lifecycle:
        1. Validates that the target student exists in the database.
        2. Saves the raw resume text into the `resumes` table.
        3. Calls the ResumeAgent to analyze the resume via Gemini API.
        4. Saves the generated critique in the `resume_analyses` table.
        5. Returns the combined analysis alongside generated DB identifiers.
        """
        # 1. Verify student exists in the database
        db_student = db.query(Student).filter(Student.id == student_id).first()
        if not db_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student with ID {student_id} does not exist in the system."
            )

        # 2. Persist raw resume details
        db_resume = Resume(
            student_id=student_id,
            filename="unstructured_text.txt",
            file_path="db://unstructured",
            raw_text=resume_text
        )
        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)

        try:
            # 3. Request Gemini evaluation from Agent
            agent_response = await self.resume_agent.analyze_resume(resume_text)

            # 4. Persist analysis results in the database
            db_analysis = ResumeAnalysis(
                resume_id=db_resume.id,
                jd_id=None,  # No job description targeted in this sprint
                strengths=agent_response.strengths,
                weaknesses=agent_response.weaknesses,
                suggestions=agent_response.recommendations,
                skills_extracted={
                    "found": agent_response.skills_found,
                    "missing": agent_response.missing_skills
                },
                score=agent_response.resume_score
            )
            db.add(db_analysis)
            db.commit()
            db.refresh(db_analysis)

        except Exception as e:
            # Roll back raw resume write if LLM or second write fails to maintain database consistency
            db.delete(db_resume)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to generate or persist resume analysis: {str(e)}"
            )

        # 5. Return combined schema response
        return {
            "resume_id": db_resume.id,
            "analysis_id": db_analysis.id,
            "resume_score": agent_response.resume_score,
            "strengths": agent_response.strengths,
            "weaknesses": agent_response.weaknesses,
            "skills_found": agent_response.skills_found,
            "missing_skills": agent_response.missing_skills,
            "recommendations": agent_response.recommendations
        }
