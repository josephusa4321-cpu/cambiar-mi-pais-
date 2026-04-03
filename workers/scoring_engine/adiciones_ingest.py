import os
import logging
import httpx
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lupa.ingest_adiciones")

# Config
SODA_TOKEN = os.environ.get("SODA_APP_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Dataset ID: cb9c-h8sn (Adiciones SECOP II)
ADICIONES_URL = "https://www.datos.gov.co/resource/cb9c-h8sn.json"

# Filtro Medellín (Nit: 890905378)
FILTRO_ENTIDADES = "nit_entidad = '890905378'"

def fetch_adiciones(offset=0, limit=1000):
    params = {
        "$limit": limit,
        "$offset": offset,
        "$where": FILTRO_ENTIDADES,
        "$order": ":id ASC"
    }
    headers = {"X-App-Token": SODA_TOKEN} if SODA_TOKEN else {}
    
    try:
        with httpx.Client() as client:
            res = client.get(ADICIONES_URL, params=params, headers=headers, timeout=60)
            res.raise_for_status()
            return res.json()
    except Exception as e:
        logger.error(f"Error fetching adiciones: {e}")
        return []

def run_ingest():
    if not supabase: 
        logger.error("Supabase client not initialized.")
        return
    
    logger.info("🎯 Iniciando ingesta de ADICIONES para Medellín...")
    
    offset = 0
    total_procesados = 0
    
    while True:
        data = fetch_adiciones(offset)
        if not data:
            break
            
        df = pd.DataFrame(data)
        
        # Mapping API -> Database
        # API: id_modificacion, id_contrato, tipo, descripcion, valor_modificacion, dias_modificacion
        records = []
        for _, row in df.iterrows():
            records.append({
                "id_adicion": str(row.get("id_modificacion", f"gen_{offset}_{_}")),
                "id_contrato": str(row.get("id_contrato")),
                "tipo": str(row.get("tipo", "N/A")),
                "descripcion": str(row.get("descripcion", "")),
                "valor_adicionado": float(row.get("valor_modificacion", 0) or 0),
                "dias_adicionados": int(row.get("dias_modificacion", 0) or 0)
            })
            
        # Batch Upsert
        try:
            supabase.table("contratos_adiciones").upsert(records, on_conflict="id_adicion").execute()
            total_procesados += len(records)
            logger.info(f"Procesadas {total_procesados} adiciones...")
        except Exception as e:
            logger.error(f"Error in batch upsert: {e}")
            
        if len(data) < 1000:
            break
        offset += 1000

    logger.info(f"✅ Ingesta de adiciones completada: {total_procesados} registros.")

if __name__ == "__main__":
    run_ingest()
