import os
from dotenv import load_dotenv
load_dotenv()


class Config:
    
    gemini_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    gemini_model = "gemini-2.0-flash-lite"
    gemini_embed_model = "models/text-embedding-004"
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")