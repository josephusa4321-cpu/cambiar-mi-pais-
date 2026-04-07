"""
crear_metricas.py - Tarea 3: Crear tabla metricas_historicas en Supabase
"""
import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lupa.crear_metricas")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SERVICE_ROLE_KEY")

SQL_CREATE = """
CREATE TABLE IF NOT EXISTS metricas_historicas (
    id               BIGSERIAL PRIMARY KEY,
    anio             INT NOT NULL,
    nombre_entidad   TEXT NOT NULL,
    total_contratos  INT,
    valor_total      BIGINT,
    pct_directos     NUMERIC(5,2),
    valor_directos   BIGINT,
    score_promedio   NUMERIC(5,2),
    contratos_alto_riesgo INT,
    actualizado_en   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(anio, nombre_entidad)
);
"""

def crear_tabla():
    logger.info("=" * 70)
    logger.info("   LOTE 4: CREAR TABLA metricas_historicas")
    logger.info("=" * 70)

    url = f"{SUPABASE_URL}/rest/v1/"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "params=single-object"
    }

    logger.info("📊 Ejecutando SQL...")
    try:
        # Usar el endpoint de SQL de Supabase
        sql_url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
        # Intentar con SQL directo via headers
        r = httpx.post(
            f"{SUPABASE_URL}/rest/v1/",
            headers={**headers, "Prefer": "resolution=merge-duplicates"},
            timeout=30
        )
        
        # Supabase REST API no permite CREATE TABLE directamente
        # Necesitamos usar la API de Management o pgAdmin
        logger.info("⚠️ CREATE TABLE no se puede ejecutar via REST API")
        logger.info("")
        logger.info("📋 Ejecuta este SQL manualmente en Supabase SQL Editor:")
        logger.info("   https://app.supabase.com/project/spcuzwycxmdyvdbsqpln/sql")
        logger.info("")
        logger.info("=" * 60)
        logger.info(SQL_CREATE)
        logger.info("=" * 60)
        
        # Verificar si la tabla ya existe
        logger.info("")
        logger.info("🔍 Verificando si la tabla ya existe...")
        r = httpx.get(
            f"{SUPABASE_URL}/rest/v1/metricas_historicas",
            headers={**headers, "Prefer": "count=exact"},
            params={"select": "id", "limit": 1},
            timeout=10
        )
        
        if r.status_code in [200, 206]:
            count = r.headers.get("content-range", "0-0/0").split("/")[-1]
            logger.info(f"   ✅ Tabla ya existe! Registros actuales: {count}")
        elif r.status_code == 404:
            logger.warning("   ❌ Tabla NO existe — ejecuta el SQL de arriba")
        else:
            logger.info(f"   Status: {r.status_code} — {r.text[:200]}")
            
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    crear_tabla()
