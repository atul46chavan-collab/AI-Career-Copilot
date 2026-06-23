from pydantic import BaseModel, Field


class SkillGapRequest(BaseModel):
    """
    Validation schema for incoming skill gap analysis requests.
    """
    resume_analysis_id: int = Field(
        ...,
        description="The unique database identifier of the resume analysis record."
    )
    job_description_id: int = Field(
        ...,
        description="The unique database identifier of the job description record."
    )


class SkillGapAgentResponse(BaseModel):
    """
    Validation schema for the structured response returned by the Gemini Skill Gap agent.
    This schema is used strictly by Gemini to guide its token generation output shape.
    """
    learning_priority: list[str] = Field(
        ...,
        description="A prioritized, ordered list of missing skills to focus on first, including brief rationales."
    )
    career_recommendations: list[str] = Field(
        ...,
        description="Actionable career recommendations such as specific project types to build, certifications, or courses."
    )


class SkillGapResponse(BaseModel):
    """
    Validation schema for the final API response returned to the client.
    Combines python-computed deterministic skill match results with the Gemini-generated advisory metrics.
    """
    matching_skills: list[str] = Field(
        ...,
        description="List of skills from the job description that were successfully found in the candidate resume."
    )
    missing_required_skills: list[str] = Field(
        ...,
        description="List of required job skills that are missing from the resume."
    )
    missing_preferred_skills: list[str] = Field(
        ...,
        description="List of optional or preferred job skills that are missing from the resume."
    )
    gap_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="A calculated match percentage (0 to 100) reflecting the overlap of required skills."
    )
    learning_priority: list[str] = Field(
        ...,
        description="A prioritized, ordered list of missing skills to focus on first, including brief rationales."
    )
    career_recommendations: list[str] = Field(
        ...,
        description="Actionable career recommendations such as specific project types to build, certifications, or courses."
    )
