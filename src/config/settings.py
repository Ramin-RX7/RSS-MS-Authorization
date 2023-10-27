import os
from pydantic_settings import BaseSettings



class _Config(BaseSettings):
    MONGODB_URL : str = os.environ.get("MONGODB_URL")

    ACCOUNTS_SERVICE_API_KEY :str = os.environ.get("ACCOUNTS_SERVICE_API_KEY")
    ACCOUNTS_SERVICE_BASE_URL : str= os.environ.get("ACCOUNTS_SERVICE_BASE_URL")

    class Config:
        env_file = ".env"
        extra = "ignore"


SETTINGS = _Config()
