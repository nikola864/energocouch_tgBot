from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    bot_token: SecretStr = "7993289579:AAHYqJgnNjC6JcdyWBTlDgstXIXJyPHe1as"

    model_config = SettingsConfigDict(env_file='../../main/.env', env_file_encoding='utf_8')


config = Settings()