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
    model = os.getenv("LLM_MODEL", config.models.llm_model)
    base_url = config.api.openai_base_url
    profile = os.getenv("MODEL_PROFILE")
    api_key = config.api.openai_api_key
    max_tokens_env = os.getenv("LLM_MAX_TOKENS")
    max_tokens = None
    if max_tokens_env:
        try:
            max_tokens = int(max_tokens_env)
        except ValueError:
            print(f"Invalid LLM_MAX_TOKENS: {max_tokens_env}. Ignoring.")

    def _mask_key(value: str) -> str:
        if not value:
            return "missing"
        if len(value) <= 10:
            return "***"
        return f"{value[:6]}...{value[-4:]}"

    print(f"Using model: {model}")
    if profile:
        print(f"Model profile: {profile}")
    print(f"Base URL: {base_url}")
    print(f"API key: {_mask_key(api_key)}")

    if not api_key:
        print("OPENAI_API_KEY is missing. Set it in .env or the environment.")
        return

    prompt = "hello, how are you?"

    try:
        kwargs = {}
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        result = await openai_complete_if_cache(
            model,
            prompt,
            system_prompt="Reply briefly to confirm the API key works.",
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )
    except Exception as exc:
        print(f"OpenAI call failed: {exc}")
        return

    print("OpenAI OK")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
