from src.services.gemini_service import GeminiService
from src.schemas.skill_gap import SkillGapAgentResponse


class SkillGapAgent:
    """
    Agent responsible for analyzing the skill gaps between a candidate's resume and a job description.
    Acts as a Technical Mentor and Career Coach to prioritize learning and provide project recommendations.
    """

    def __init__(self, gemini_service: GeminiService | None = None):
        self.gemini_service = gemini_service or GeminiService()

    async def analyze_gap(
        self,
        matching_skills: list[str],
        missing_required_skills: list[str],
        missing_preferred_skills: list[str]
    ) -> SkillGapAgentResponse:
        """
        Analyzes the skill gap data using Gemini to generate prioritized learning paths and career recommendations.
        """
        system_instruction = (
            "You are a Principal Software Engineer, Technical Mentor, and Career Coach. "
            "Your goal is to guide a candidate on how to bridge the skill gaps between their resume and a target job. "
            "Provide highly actionable, technical advice. Be realistic and precise. "
            "Prioritize which missing skills to learn first based on industry demand and role importance, "
            "and suggest concrete, resume-worthy projects or learning actions the candidate can take."
        )

        prompt = (
            "Review the skill overlap between the candidate's resume and the target job description requirements:\n\n"
            f"1. Matching Skills: {matching_skills}\n"
            f"2. Missing Required Skills: {missing_required_skills}\n"
            f"3. Missing Preferred Skills: {missing_preferred_skills}\n\n"
            "Please analyze this data and generate:\n"
            "- A prioritized learning sequence for the missing skills (both required and preferred) with a short technical explanation/rationale of why it is critical.\n"
            "- Practical, hands-on career recommendations, such as specific project architectures they should build to showcase these missing skills, or highly regarded industry courses/certifications.\n\n"
            "Strictly populate the response schema."
        )

        # Force structured content generation
        analysis_result = await self.gemini_service.generate_structured_content(
            prompt=prompt,
            response_schema=SkillGapAgentResponse,
            system_instruction=system_instruction,
            temperature=0.2  # Low temperature for analytical advice
        )

        return analysis_result
