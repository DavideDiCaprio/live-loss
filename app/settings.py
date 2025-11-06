from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Encapsulates all application configuration settings.

    Attributes:
        APP_TITLE (str): The title of the application, used in OpenAPI docs.
        APP_DESCRIPTION (str): The description of the application, used in OpenAPI docs.
        APP_VERSION (str) = The current version of the application.
        DATABASE_URL (str): The connection string for the primary database.
        REDIS_URL (str): The connection string for the Redis instance.
    """
    APP_TITLE: str = "live-loss API"
    APP_DESCRIPTION: str = "live-Loss project"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str = ""
    REDIS_URL: str = ""

    class Config:
        pass

settings = Settings()