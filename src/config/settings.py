from pydantic_settings import BaseSettings



class _Settings(BaseSettings):
    ACCOUNTS_SERVICE_API_KEY : str
    ACCOUNTS_SERVICE_BASE_URL : str

    REDIS_URL : str
    REDIS_KEY_TTL : int

    class Config:
        # env_file = ".env"
        extra = "ignore"


SETTINGS = _Settings()
