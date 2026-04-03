import os
import logging
import time
from datetime import datetime, timezone
import httpx
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lupa.ingest")

# Config
SODA_TOKEN = os.environ.get("SODA_APP_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Endpoints Dataset SECOP II (Integrado)
CONTRATOS_URL = "https://www.datos.gov.co/resource/jbjy-vk9h.json"

def get_last_run():
    res = supabase.table("meta_pipeline").select("ultima_ejecucion_exitosa").eq("nombre_pipeline", "ingesta_contratos").execute()
    if res.data and res.data[0]["ultima_ejecucion_exitosa"]:
        return res.data[0]["ultima_ejecucion_exitosa"]
    return None

def fetch_secop(last_run=None):
    # Medellín Filter: upper(ciudad) = 'MEDELLÍN'
    # Incremental: ultima_actualizacion > {last_run}
    where = "upper(ciudad) LIKE '%MEDELL%'"
    if last_run:
        where += f" AND ultima_actualizacion > '{last_run}'"
    
    params = {
        "$where": where,
        "$limit": 1000,
        "$order": "ultima_actualizacion ASC"
    }
    
    headers = {"X-App-Token": SODA_TOKEN} if SODA_TOKEN else {}
    
    logger.info(f"Fetching SECOP II with filter: {where}")
    
    try:
        with httpx.Client() as client:
            res = client.get(CONTRATOS_URL, params=params, headers=headers, timeout=60)
            res.raise_for_status()
            return res.json()
    except Exception as e:
        logger.error(f"Error fetching SECOP: {e}")
        return []

def clean_data(df: pd.DataFrame):
    # Rename columns to match Supabase schema if necessary
    # SECOP column names are often lowercase with underscores in the API
    # Some common mapping:
    column_map = {
        "nombre_entidad": "nombre_entidad",
        "nit_entidad": "nit_entidad",
        "ciudad": "ciudad",
        "sector": "sector",
        "id_contrato": "id_contrato",
        "referencia_del_contrato": "referencia_del_contrato",
        "proceso_de_compra": "proceso_de_compra",
        "modalidad_de_contratacion": "modalidad_de_contratacion",
        "valor_del_contrato": "valor_del_contrato",
        "documento_proveedor": "documento_proveedor",
        "proveedor_adjudicado": "proveedor_adjudicado",
        "fecha_de_firma": "fecha_de_firma",
        "estado_contrato": "estado_contrato",
        "ultima_actualizacion": "ultima_actualizacion"
    }
    
    # Filter only columns we have/want
    available_cols = [c for c in column_map.keys() if c in df.columns]
    df = df[available_cols].copy()
    
    # Numerical Conversion
    if "valor_del_contrato" in df.columns:
        df["valor_del_contrato"] = pd.to_numeric(df["valor_del_contrato"], errors="coerce")
    
    # String Cleaning
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()

    # Medellín Specific: sometimes 'MEDELLIN' vs 'MEDELLÍN'
    df = df[df["ciudad"].str.upper().str.contains("MEDELL", na=False)]
    
    return df

def run_ingest():
    if not supabase: return
    
    last_run = get_last_run()
    raw_data = fetch_secop(last_run)
    
    if not raw_data:
        logger.info("No hay datos nuevos en SECOP II.")
        return

    df = pd.DataFrame(raw_data)
    df_clean = clean_data(df)
    
    records = df_clean.to_dict(orient="records")
    
    logger.info(f"Procesando {len(records)} registros para UPSERT en Supabase...")
    
    # Batch UPSERT (100 at a time)
    batch_size = 100
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        try:
            supabase.table("contratos_raw").upsert(batch, on_conflict="id_contrato").execute()
            logger.info(f"Batch {i//batch_size + 1} completado.")
        except Exception as e:
            logger.error(f"Error en batch {i//batch_size + 1}: {e}")

    # Update meta_pipeline
    now = datetime.now(timezone.utc).isoformat()
    supabase.table("meta_pipeline").update({
        "ultima_ejecucion_exitosa": now,
        "registros_procesados": len(records),
        "estado": "OK"
    }).eq("nombre_pipeline", "ingesta_contratos").execute()
    
    logger.info("Ingesta completada exitosamente.")

if __name__ == "__main__":
    run_ingest()
