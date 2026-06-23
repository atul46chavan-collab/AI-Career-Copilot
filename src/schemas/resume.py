from pydantic import BaseModel, Field


class ResumeAnalysisRequest(BaseModel):
    """
    Validation schema for incoming resume analysis requests.
    """
    student_id: int = Field(
        ...,
        description="The unique database identifier of the student who owns the resume."
    )
    resume_text: str = Field(
        ..., 
        description="The raw text parsed from the candidate's resume file."
    )


class ResumeAgentResponse(BaseModel):
    """
    Validation schema for the structured response returned by the Gemini AI agent.
    This schema is used strictly by Gemini to guide its token generation output shape.
    """
    resume_score: int = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Overall quality score from 0 (very poor) to 100 (excellent) assessing structure, clarity, and impact."
    )
    strengths: list[str] = Field(
        ..., 
        description="Key professional strengths, achievements, and formatting highlights."
    )
    weaknesses: list[str] = Field(
        ..., 
        description="Core flaws, missing standard sections, formatting errors, or vague descriptions."
    )
    skills_found: list[str] = Field(
        ..., 
        description="Technical, domain, or soft skills detected in the text."
    )
    missing_skills: list[str] = Field(
        ..., 
        description="Highly standard industry skills for their profile type that are conspicuously absent."
    )
    recommendations: list[str] = Field(
        ..., 
        description="Actionable, prioritized steps they can take to upgrade their resume and stand out to recruiters."
    )


class ResumeAnalysisResponse(ResumeAgentResponse):
    """
    Validation schema for the final API response returned to the client,
    including database record identifiers.
    """
    resume_id: int = Field(
        ...,
        description="The database autoincremented identifier of the saved resume record."
    )
    analysis_id: int = Field(
        ...,
        description="The database autoincremented identifier of the saved analysis record."
    )

