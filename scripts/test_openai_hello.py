import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from lightrag.llm.openai import openai_complete_if_cache

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import Config


async def main() -> None:
    load_dotenv()
    config = Config.load()
    print("=== OpenAI Hello Test ===\n")
    print("Checking OpenAI API Key...")
    print(f"Using model: {os.getenv('OPENAI_API_KEY', config.api.openai_api_key)}")

    if not config.api.openai_api_key:
        print("OPENAI_API_KEY is missing. Set it in .env or the environment.")
        return

    model = os.getenv("LLM_MODEL", config.models.llm_model)
    prompt = "hello"

    try:
        result = await openai_complete_if_cache(
            model,
            prompt,
            system_prompt="Reply briefly to confirm the API key works.",
            api_key=config.api.openai_api_key,
            base_url=config.api.openai_base_url,
        )
    except Exception as exc:
        print(f"OpenAI call failed: {exc}")
        return

    print("OpenAI OK")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
