import asyncio
from pydantic import BaseModel
from src.services.gemini_service import GeminiService


class TestSchema(BaseModel):
    message: str
    skills: list[str]


async def main():
    print("Initializing GeminiService...")
    service = GeminiService()
    print("Calling Gemini API with structured request...")
    try:
        result = await service.generate_structured_content(
            prompt="Hello! List three essential technical skills for a backend software engineer.",
            response_schema=TestSchema,
            system_instruction="You are a helpful and technical career advisor assistant."
        )
        print("\n--- Connection Success ---")
        print(f"Response Object: {result}")
        print(f"Message: {result.message}")
        print(f"Skills: {result.skills}")
    except Exception as e:
        print(f"\n--- Connection Failure ---")
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
