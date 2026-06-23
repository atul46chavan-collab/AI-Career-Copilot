from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from src.models.analysis import ResumeAnalysis
from src.models.job_description import JobDescription
from src.agents.skill_gap_agent import SkillGapAgent
from src.schemas.skill_gap import SkillGapResponse


class SkillGapService:
    """
    Service layer responsible for executing the skill gap analysis:
    1. Retrieves resume analysis and job description records.
    2. Performs case-insensitive deterministic set matching in Python.
    3. Calculates a skill overlap gap score.
    4. Triggers the Skill Gap Agent for prioritized learning and recommendations.
    5. Returns the combined SkillGapResponse structure.
    """

    def __init__(self, skill_gap_agent: SkillGapAgent | None = None):
        self.skill_gap_agent = skill_gap_agent or SkillGapAgent()

    async def generate_skill_gap(
        self,
        db: Session,
        resume_analysis_id: int,
        job_description_id: int
    ) -> dict:
        """
        Calculates the skill gap between a resume analysis and a job description.
        """
        # 1. Retrieve records from the database
        resume_analysis = db.query(ResumeAnalysis).filter(ResumeAnalysis.id == resume_analysis_id).first()
        if not resume_analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume analysis with ID {resume_analysis_id} does not exist."
            )

        job_description = db.query(JobDescription).filter(JobDescription.id == job_description_id).first()
        if not job_description:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job description with ID {job_description_id} does not exist."
            )

        # 2. Extract skills from records
        # resume_analysis.skills_extracted is stored as {"found": [...], "missing": [...]}
        resume_skills_data = resume_analysis.skills_extracted or {}
        resume_skills = resume_skills_data.get("found", [])
        if not isinstance(resume_skills, list):
            resume_skills = []

        # job_description.extracted_data is stored as:
        # {"required_skills": [...], "preferred_skills": [...], ...}
        jd_data = job_description.extracted_data or {}
        jd_required = jd_data.get("required_skills", [])
        jd_preferred = jd_data.get("preferred_skills", [])
        if not isinstance(jd_required, list):
            jd_required = []
        if not isinstance(jd_preferred, list):
            jd_preferred = []

        # 3. Perform case-insensitive set matching with case preservation
        resume_set_lower = {s.lower(): s for s in resume_skills}
        required_set_lower = {s.lower(): s for s in jd_required}
        preferred_set_lower = {s.lower(): s for s in jd_preferred}

        # Create a casing mapping where Job Description casing takes priority over Resume casing
        casing_map = {**resume_set_lower, **preferred_set_lower, **required_set_lower}

        # Sets of lowercased keys for mathematical operations
        resume_keys = set(resume_set_lower.keys())
        required_keys = set(required_set_lower.keys())
        preferred_keys = set(preferred_set_lower.keys())

        # Intersections and differences
        matching_required = resume_keys & required_keys
        matching_preferred = resume_keys & preferred_keys
        
        missing_required = required_keys - resume_keys
        missing_preferred = preferred_keys - resume_keys

        # Restore original casing and sort lists
        matching_skills = [casing_map[s] for s in sorted(matching_required | matching_preferred)]
        missing_required_skills = [casing_map[s] for s in sorted(missing_required)]
        missing_preferred_skills = [casing_map[s] for s in sorted(missing_preferred)]

        # 4. Calculate Gap Score (percentage of required skills met)
        total_required = len(required_keys)
        if total_required > 0:
            gap_score = int((len(matching_required) / total_required) * 100)
        else:
            total_preferred = len(preferred_keys)
            if total_preferred > 0:
                gap_score = int((len(matching_preferred) / total_preferred) * 100)
            else:
                gap_score = 100

        # Ensure score is within valid [0, 100] bounds
        gap_score = max(0, min(100, gap_score))

        # 5. Call the Skill Gap Agent for advisory enrichment
        agent_response = await self.skill_gap_agent.analyze_gap(
            matching_skills=matching_skills,
            missing_required_skills=missing_required_skills,
            missing_preferred_skills=missing_preferred_skills
        )

        # 6. Return combined payload
        return {
            "matching_skills": matching_skills,
            "missing_required_skills": missing_required_skills,
            "missing_preferred_skills": missing_preferred_skills,
            "gap_score": gap_score,
            "learning_priority": agent_response.learning_priority,
            "career_recommendations": agent_response.career_recommendations
        }
