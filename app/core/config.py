from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    database_url:     str
    mistral_api_key:  str
    groq_api_key:     str = ""
    secret_key:       str = ""
    redis_url:        str
    debug:            bool = False

    model_config = ConfigDict(env_file=".env")

settings = Settings()
