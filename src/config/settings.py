import os
# from pydantic_settings import BaseSettings, SettingsConfigDict



class _Config():
    MONGODB_URL : str = os.environ.get("MONGODB_URL")

    ACCOUNTS_SERVICE_API_KEY = os.environ.get("ACCOUNTS_SERVICE_API_KEY")
    ACCOUNTS_SERVICE_BASE_URL = os.environ.get("ACCOUNTS_SERVICE_BASE_URL")



SETTINGS = _Config()
