import json
from pydantic import BaseModel
from src.config import get_settings
from src.utils.openai_client import get_openai_client


def structured_call(system: str, user: str, schema: type[BaseModel]) -> BaseModel:
    client = get_openai_client()
    response = client.responses.parse(
        model=get_settings().openai_chat_model,
        input=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        text_format=schema,
    )
    return response.output_parsed


def text_call(system: str, user: str) -> str:
    client = get_openai_client()
    response = client.responses.create(
        model=get_settings().openai_chat_model,
        input=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    )
    return response.output_text.strip()


def to_json(data: object) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)
