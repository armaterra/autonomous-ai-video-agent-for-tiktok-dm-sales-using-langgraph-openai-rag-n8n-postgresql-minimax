from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # TikTok (Mapeo explícito a tus nombres de variable)
    tiktok_client_key: str = Field(..., alias="TIKTOK_CLIENT_KEY")
    tiktok_client_secret: str = Field(..., alias="TIKTOK_CLIENT_SECRET")
    tiktok_access_token: str = Field(..., alias="TIKTOK_ACCESS_TOKEN")
    tiktok_app_id: str = Field(..., alias="TIKTOK_APP_ID")

    # MiniMax
    minimax_api_key: str = Field(..., alias="MINIMAX_API_KEY")
    minimax_api_url: str = Field("https://api.minimax.chat/v1", alias="MINIMAX_API_URL")

    # OpenAI
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")

    # Database
    database_url: str = Field("postgresql://postgres:password@localhost:5432/armaterra", alias="DATABASE_URL")

    # Redis
    redis_url: str = Field("redis://localhost:6379", alias="REDIS_URL")

    # Langfuse
    langfuse_public_key: str = Field("", alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field("", alias="LANGFUSE_SECRET_KEY")
    langfuse_tracing_environment: str = Field("default", alias="LANGFUSE_TRACING_ENVIRONMENT")
    langfuse_host: str = Field("http://localhost:3000", alias="LANGFUSE_HOST")

    # Link Bi
    link_bi_api_key: str = Field("", alias="LINK_BI_API_KEY")
    link_bi_api_url: str = Field("https://api.link.bi/v1", alias="LINK_BI_API_URL")

    # N8N
    n8n_webhook_url: str = Field("http://localhost:5678/webhook", alias="N8N_WEBHOOK_URL")
    n8n_secure_cookie: bool = Field(False, alias="N8N_SECURE_COOKIE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True # Permite usar el nombre del alias o el campo
    )

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()