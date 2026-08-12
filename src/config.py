from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # TikTok
    tiktok_client_key: str
    tiktok_client_secret: str
    tiktok_access_token: str
    tiktok_app_id: str

    # MiniMax
    minimax_api_key: str
    minimax_api_url: str = "https://api.minimax.chat/v1"

    # OpenAI
    openai_api_key: str

    # Database
    database_url: str = "postgresql://postgres:postgres@db:5432/armaterra"

    # Redis
    redis_url: str = "redis://redis:6379"

    # Langfuse
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "http://langfuse:3000"

    # Link Bi
    link_bi_api_key: str = ""
    link_bi_api_url: str = "https://api.link.bi/v1"

    # N8N
    n8n_webhook_url: str = "http://n8n:5678/webhook"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
