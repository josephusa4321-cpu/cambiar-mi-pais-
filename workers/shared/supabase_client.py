from supabase import create_client, Client
from .config import settings

def get_supabase_client() -> Client:
    """
    Returns an authenticated Supabase client for Service Role access.
    Mandatory for data ingestion and scoring updates in workers.
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados en el .env")
    
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Singleton instance
supabase: Client = get_supabase_client()
