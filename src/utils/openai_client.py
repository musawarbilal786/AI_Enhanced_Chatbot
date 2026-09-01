from typing import Any
from src.config import get_settings


def get_openai_client() -> Any:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Copy .env.example to .env and add your key.")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("The 'openai' package is not installed. Run: pip install -r requirements.txt") from exc
    return OpenAI(api_key=settings.openai_api_key)
