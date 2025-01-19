from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    admin_id: int

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
