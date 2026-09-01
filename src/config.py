from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    top_k: int = 5
    min_relevance_score: float = 0.25
    max_revisions: int = 1
    raw_data_path: Path = ROOT_DIR / "data" / "raw" / "ulster_london_policies.json"
    pdf_dir: Path = ROOT_DIR / "data" / "pdfs"
    pdf_manifest_path: Path = ROOT_DIR / "data" / "pdf_manifest.json"
    use_manual_dataset: bool = False
    index_dir: Path = ROOT_DIR / "data" / "faiss_index"

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
