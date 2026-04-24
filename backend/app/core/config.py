from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://travel_user:travel_pass@localhost:5432/travel_db"
    ollama_base_url: str = "http://localhost:11434"
    chroma_server_host: str = "localhost"
    chroma_server_http_port: int = 8001

    jwt_secret_key: str = "changeme-use-strong-secret-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
