from src.services.gemini_service import GeminiService
from src.schemas.job_description import JobDescriptionAgentResponse


class JobDescriptionAgent:
    """
    Agent responsible for analyzing job descriptions.
    Combines the personas of a Technical Recruiter, Hiring Manager,
    and Engineering Lead to dissect unstructured job listings.
    """

    def __init__(self, gemini_service: GeminiService | None = None):
        self.gemini_service = gemini_service or GeminiService()

    async def analyze_jd(self, jd_text: str) -> JobDescriptionAgentResponse:
        """
        Analyzes the unstructured job post and returns structured metrics.
        """
        system_instruction = (
            "You are a Senior Technical Recruiter, Hiring Manager, and Engineering Lead. "
            "Your objective is to read a verbose, unstructured job description posting "
            "and extract the concrete, high-signal recruitment parameters. "
            "Filter out corporate boilerplate and marketing buzzwords. Focus strictly on "
            "identifying core skills, required vs. preferred technologies, education, "
            "experience years, and primary day-to-day responsibilities."
        )

        prompt = (
            "Dissect the following job description text:\n\n"
            "--- BEGIN JOB DESCRIPTION ---\n"
            f"{jd_text}\n"
            "--- END JOB DESCRIPTION ---\n\n"
            "Evaluate the text and populate the response schema. "
            "Ensure required_skills and preferred_skills lists are clean, deduplicated, and lowercase."
        )

        # Execute structured LLM generation
        analysis_result = await self.gemini_service.generate_structured_content(
            prompt=prompt,
            response_schema=JobDescriptionAgentResponse,
            system_instruction=system_instruction,
            temperature=0.1  # Low temperature for precise extraction compliance
        )

        return analysis_result
