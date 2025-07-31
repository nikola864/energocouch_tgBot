from pydantic_settings import BaseSettings
from pydantic import SecretStr

class Settings(BaseSettings):
    bot_token: SecretStr
    app_name: str  # например: "my-awesome-bot" — имя сервиса на Render
    port: int = 8080  # Render передаст PORT, но можно указать по умолчанию

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

config = Settings()