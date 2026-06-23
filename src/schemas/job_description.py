from pydantic import BaseModel, Field


class JobDescriptionRequest(BaseModel):
    """
    Validation schema for incoming job description analysis requests.
    """
    student_id: int = Field(
        ...,
        description="The unique database identifier of the student analyzing the JD."
    )
    job_description: str = Field(
        ...,
        description="The raw unstructured text of the job post copied from careers boards."
    )


class JobDescriptionAgentResponse(BaseModel):
    """
    Validation schema for the structured response returned by the Gemini JD agent.
    This schema is used strictly by Gemini to guide its token generation output shape.
    """
    job_title: str = Field(
        ...,
        description="The parsed professional role title (e.g., Senior backend engineer, AI Engineer)."
    )
    company_name: str = Field(
        ...,
        description="The extracted name of the company hiring for this role."
    )
    required_skills: list[str] = Field(
        ...,
        description="Must-have technical, hard, or domain skills explicitly required by the listing."
    )
    preferred_skills: list[str] = Field(
        ...,
        description="Nice-to-have skills, qualifications, or certifications listed as optional."
    )
    experience_required: str = Field(
        ...,
        description="Extracted experience requirements (e.g., 3+ years, entry level, senior)."
    )
    education_requirements: list[str] = Field(
        ...,
        description="Academic degrees or equivalent credentials specified by the listing."
    )
    responsibilities: list[str] = Field(
        ...,
        description="Core day-to-day duties, expectations, and project roles described."
    )


class JobDescriptionResponse(JobDescriptionAgentResponse):
    """
    Validation schema for the final API response returned to the client,
    including database record identifiers.
    """
    jd_id: int = Field(
        ...,
        description="The database autoincremented identifier of the saved job description record."
    )
