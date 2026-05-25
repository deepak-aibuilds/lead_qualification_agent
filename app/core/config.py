from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    database_url:     str
    mistral_api_key:  str
    groq_api_key:     str = ""
    secret_key:       str = ""
    supabase_url:     str
    supabase_key:     str
    redis_url:        str
    debug:            bool = False
    cohere_api_key:   str

    model_config = ConfigDict(env_file=".env")

settings = Settings()
