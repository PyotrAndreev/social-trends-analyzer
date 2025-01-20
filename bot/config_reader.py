from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    bot_token: SecretStr
    admin_id: int
    postgres_password: SecretStr
    postgres_user: str
    db_users_name: str
    postgres_host: str
    postgres_port: int
    youtube_api_key: SecretStr
    db_name: str
    messages_path: str
    openai_api_key: str

    class Config:
        env_file = '/Users/leonidserbin/PycharmProjects/social-trends-analyzer/.env'
        env_file_encoding = 'utf-8'


settings = Settings()
