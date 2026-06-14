"""Runtime config via pydantic-settings, layered .env > process env > defaults.

App settings are KG_-prefixed; Google Cloud settings use the standard GOOGLE_* names
so they're shared with gcloud / ADC and the genai client.
"""
from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- pipeline ---
    backend: str = Field("mock", validation_alias="KG_BACKEND")  # mock | vertex
    gemini_model: str = Field("gemini-2.5-flash", validation_alias="KG_GEMINI_MODEL")
    # prose tier — point at a larger model once judgment matters (SPEC §12.1 tiering)
    profile_model: str = Field("gemini-3.1-flash-lite", validation_alias="KG_PROFILE_MODEL")
    list_path: Path = Field(Path("list.md"), validation_alias="KG_LIST_PATH")
    out_path: Path = Field(Path("data/graph.json"), validation_alias="KG_OUT_PATH")
    review_path: Path = Field(Path("_review.json"), validation_alias="KG_REVIEW_PATH")
    log_level: str = Field("INFO", validation_alias="KG_LOG_LEVEL")
    # min catalog papers an external paper must connect to earn a cocitation node
    # (SPEC §6.2 friction). 2 = inclusive; raise to trim tangential connectors.
    cocite_min: int = Field(2, validation_alias="KG_COCITE_MIN")
    # citation-based agent discovery (ADR 0003). rounds=0 disables; cap bounds candidates.
    discover_rounds: int = Field(0, validation_alias="KG_DISCOVER_ROUNDS")
    discover_cap: int | None = Field(None, validation_alias="KG_DISCOVER_CAP")

    # --- Google Cloud (shared with gcloud / ADC) ---
    project: str | None = Field(None, validation_alias="GOOGLE_CLOUD_PROJECT")
    location: str = Field("us-central1", validation_alias="GOOGLE_CLOUD_LOCATION")
    google_api_key: str | None = Field(None, validation_alias="GOOGLE_API_KEY")
