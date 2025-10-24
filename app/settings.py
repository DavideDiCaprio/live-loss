from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_TITLE: str = "live-loss API"
    APP_DESCRIPTION: str = "live-Loss project"
    DATABASE_URL: str = ""
    REDIS_URL: str = "' 


settings = Settings()