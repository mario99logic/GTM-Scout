from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-5"
    proxycurl_api_key: str = ""
    github_token: str = ""
    stackshare_api_key: str = ""
    dry_run: bool = True
    score_threshold: int = Field(50, ge=0, le=100)
    max_leads: int = Field(10, ge=1)
    database_url: str = "sqlite:///./gtm_hunter.db"
    output_dir: str = "./output"


settings = Settings()
