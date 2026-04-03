import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "") # Use Service Role for Workers
    
    # SODA API (datos.gov.co)
    SODA_APP_TOKEN: str = os.getenv("SODA_APP_TOKEN", "")
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR: str = os.path.join(os.path.dirname(BASE_DIR), "data")
    SANCIONADOS_CSV: str = os.path.join(DATA_DIR, "sancionados.csv")

    class Config:
        case_sensitive = True

settings = Settings()
