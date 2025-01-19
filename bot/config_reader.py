from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    admin_id: int

    db_user: str
    db_name: str
    db_host: str
    db_port: int

    messages_path: str

    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'


settings = Settings()
