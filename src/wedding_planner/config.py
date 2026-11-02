"""Settings read from environment variables (and a local .env file)."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    llm_model: str
    llm_max_retries: int
    mcp_url: str
    mcp_max_result_chars: int
    mcp_max_retries: int
    max_venue_searches: int
    recursion_limit: int
    chinook_db_path: Path


def get_settings() -> Settings:
    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "groq"),
        llm_model=os.getenv("LLM_MODEL", "openai/gpt-oss-120b"),
        llm_max_retries=int(os.getenv("LLM_MAX_RETRIES", "8")),
        mcp_url=os.getenv("KIWI_MCP_URL", "https://mcp.kiwi.com"),
        mcp_max_result_chars=int(os.getenv("MCP_MAX_RESULT_CHARS", "3000")),
        mcp_max_retries=int(os.getenv("MCP_MAX_RETRIES", "3")),
        max_venue_searches=int(os.getenv("MAX_VENUE_SEARCHES", "12")),
        recursion_limit=int(os.getenv("RECURSION_LIMIT", "40")),
        chinook_db_path=Path(os.getenv("CHINOOK_DB_PATH", str(ROOT / "data" / "Chinook.db"))),
    )
