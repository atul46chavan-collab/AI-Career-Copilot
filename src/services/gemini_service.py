from typing import Type, TypeVar
from pydantic import BaseModel
from google import genai
from google.genai import types

from src.config.settings import settings

T = TypeVar("T", bound=BaseModel)


class GeminiService:
    """
    Service responsible for interacting with the Google Gemini API.
    Handles client initialization and exposes async helpers for structured outputs.
    """

    def __init__(self):
        # We pass the validated key from settings to ensure configuration safety
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def generate_structured_content(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: str | None = None,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.2
    ) -> T:
        """
        Queries Gemini with a prompt and strictly enforces the output to match 
        the provided Pydantic schema using Gemini's native JSON schema generator.
        Implements an asynchronous retry loop with exponential backoff to handle 
        transient server overloads (503) and rate limits (429).
        """
        import asyncio

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=temperature,
            system_instruction=system_instruction
        )

        max_retries = 5
        base_delay = 8.0  # seconds

        for attempt in range(max_retries):
            try:
                # Query the model asynchronously to prevent blocking the FastAPI event loop
                response = await self.client.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config
                )
                # Parse response.text directly into the requested Pydantic model
                return response_schema.model_validate_json(response.text)
            except Exception as e:
                # Check if it's the last attempt, if so re-raise
                if attempt == max_retries - 1:
                    raise e
                
                # Wait with exponential backoff (e.g. 8s, 16s, 24s, 32s)
                sleep_duration = base_delay * (attempt + 1)
                await asyncio.sleep(sleep_duration)


