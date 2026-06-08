from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-6"
    proxycurl_api_key: str = ""
    apollo_api_key: str = ""
    github_token: str = ""
    stackshare_api_key: str = ""
    dry_run: bool = Field(True, description="Log messages instead of sending them")
    score_threshold: int = Field(50, ge=0, le=100, description="Minimum score (0–100) for a lead to qualify")
    max_leads: int = Field(10, ge=1, description="Max leads to process across all companies")
    max_companies: int = Field(10, ge=1, description="Max companies to discover per run")
    database_url: str = "sqlite:///./database.db"
    output_dir: str = "./output"


settings = Settings()
