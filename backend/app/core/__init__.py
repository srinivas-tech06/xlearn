from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./antigravity.db"

    # Cloud LLM
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4"
    LLM_PROVIDER: str = "openai"  # openai | gemini

    # Ollama / Local LLM
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"          # llama3 | mistral | codellama
    OLLAMA_ENABLED: bool = True
    OLLAMA_TIMEOUT: int = 30              # seconds

    # Hybrid Routing
    # auto | ollama_only | cloud_only | fallback_only
    LLM_ROUTING_MODE: str = "auto"
    PRIVACY_MODE: bool = False            # if True, forces Ollama, disables cloud

    # Response Cache
    CACHE_ENABLED: bool = True
    CACHE_MAX_SIZE: int = 256             # max cached responses
    CACHE_TTL_SECONDS: int = 3600         # 1 hour

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def llm_available(self) -> bool:
        return bool(self.LLM_API_KEY and len(self.LLM_API_KEY) > 5)

    @property
    def cloud_available(self) -> bool:
        """Cloud is available only when not in privacy mode AND API key is set."""
        return self.llm_available and not self.PRIVACY_MODE

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
