import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file from the workspace root (two levels up from this file)
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(root_dir, '.env')
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    port: int = 8000
    host: str = "127.0.0.1"
    database_url: str = "sqlite:///./code_review.db"
    gemini_api_key: str = ""
    openai_api_key: str = ""
    deepseek_api_key: str = ""
    morphllm_api_key: str = ""

    class Config:
        env_file = env_path
        extra = "ignore"

settings = Settings()
