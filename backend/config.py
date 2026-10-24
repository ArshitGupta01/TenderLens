"""
TenderLens - Backend Configuration & Settings
==============================================
Manages environment variables, API keys, and operational limits.
"""

import os
from typing import List
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # API Keys
    TINYFISH_API_KEY: str = Field(default="", description="TinyFish Web Intelligence API key")
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key for structured clause auditing")
    GEMINI_MODEL: str = Field(default="gemini-3.8-flash", description="Gemini model name for clause & conflict analysis")
    TAVILY_API_KEY: str = Field(default="", description="Tavily search API key for live web search fallback")
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key (optional fallback)")

    # Server Settings
    BACKEND_PORT: int = Field(default=8000, description="FastAPI server port")
    BACKEND_HOST: str = Field(default="0.0.0.0", description="FastAPI server host")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, test, production")

    # Indian Procurement Web Intelligence Defaults
    ALLOWED_DOMAINS: str = Field(
        default="gem.gov.in,eprocure.gov.in,tenders.bhel.com,icmr.nic.in,etenders.hry.nic.in",
        description="Comma-separated target domains for TinySearch include_domains"
    )
    DEFAULT_LOCATION: str = Field(default="IN", description="Geographic location filter")
    DEFAULT_LANGUAGE: str = Field(default="en", description="Search language filter")

    # Crawling & Circuit Breaker Limits
    MAX_CRAWL_DEPTH: int = Field(default=2, description="Max depth limit for recursive ATC discovery")
    MAX_BATCH_URLS: int = Field(default=10, description="Max URLs per TinyFetch batch request")
    TINYAGENT_MAX_STEPS: int = Field(default=10, description="Cost circuit breaker for TinyAgent browser runs")
    TINYAGENT_MAX_DURATION_SECONDS: int = Field(default=60, description="Max duration in seconds for TinyAgent runs")

    # Document Cache & Storage Paths
    CACHE_DIR: Path = Field(default=ROOT_DIR / "data" / "cache")
    RAW_TENDERS_DIR: Path = Field(default=ROOT_DIR / "data" / "raw_tenders")

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instantiate singleton settings
settings = Settings()

# Ensure local directories exist
settings.CACHE_DIR.mkdir(parents=True, exist_ok=True)
settings.RAW_TENDERS_DIR.mkdir(parents=True, exist_ok=True)
