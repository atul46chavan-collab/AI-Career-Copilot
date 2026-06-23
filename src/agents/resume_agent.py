from src.services.gemini_service import GeminiService
from src.schemas.resume import ResumeAgentResponse


class ResumeAgent:
    """
    Agent responsible for analyzing resumes.
    Acts as a specialized technical recruiter persona that evaluates
    formatting, skills representation, and quality of project/work history.
    """

    def __init__(self, gemini_service: GeminiService | None = None):
        # We allow injecting the service to facilitate unit testing and mocking
        self.gemini_service = gemini_service or GeminiService()

    async def analyze_resume(self, resume_text: str) -> ResumeAgentResponse:
        """
        Analyzes the candidate's resume text and outputs structured feedback.
        """
        system_instruction = (
            "You are a Principal Tech Recruiter and Technical Staff Engineer. "
            "Your objective is to analyze a candidate's resume with high rigor, "
            "identifying its strengths, critical weaknesses, formatting flaws, and gaps. "
            "Be constructive but extremely honest. Give actionable feedback suitable for "
            "securing interviews at top tier tech firms."
        )

        prompt = (
            "Evaluate the following resume text:\n\n"
            "--- BEGIN RESUME TEXT ---\n"
            f"{resume_text}\n"
            "--- END RESUME TEXT ---\n\n"
            "Evaluate the text and populate the response schema. "
            "Highlight formatting concerns, word choice, missing metrics, and technical skill gaps."
        )

        # Force structured execution using gemini_service
        analysis_result = await self.gemini_service.generate_structured_content(
            prompt=prompt,
            response_schema=ResumeAgentResponse,
            system_instruction=system_instruction,
            temperature=0.15  # Low temperature for analytical consistency
        )

        return analysis_result

