"""
adiciones_ingest.py - Tarea 2: Descarga CSV directa + fallback SODA
"""
import os
import logging
import time
import pandas as pd
import httpx
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

try:
    from workers.constants import BATCH_SIZE_UPSERT
except ImportError:
    from constants import BATCH_SIZE_UPSERT

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lupa.adiciones")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SERVICE_ROLE_KEY")

CSV_URL = "https://www.datos.gov.co/api/views/cb9c-h8sn/rows.csv?accessType=DOWNLOAD&bom=true"
CSV_LOCAL_PATH = os.path.join("workers", "data", "adiciones_raw.csv")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def descargar_csv_directo(max_reintentos=3):
    """Intenta descargar el CSV directo primero (mas rapido que SODA)."""
    logger.info("📥 Intentando descarga CSV directa...")
    logger.info(f"   URL: {CSV_URL[:80]}...")

    for intento in range(1, max_reintentos + 1):
        logger.info(f"   Intento {intento}/{max_reintentos}...")
        try:
            with httpx.stream("GET", CSV_URL, timeout=300, follow_redirects=True) as response:
                if response.status_code != 200:
                    logger.warning(f"   Status: {response.status_code} — CSV directo fallo")
                    return False

                total = 0
                start = time.time()
                with open(CSV_LOCAL_PATH, "wb") as f:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        f.write(chunk)
                        total += len(chunk)
                        elapsed = time.time() - start
                        mb = total / (1024 * 1024)
                        speed = mb / elapsed if elapsed > 0 else 0
                        logger.info(f"   ⬇️ Descargando: {mb:.1f} MB ({speed:.2f} MB/s)...")

                elapsed = time.time() - start
                logger.info(f"   ✅ CSV descargado: {total / (1024*1024):.1f} MB en {elapsed:.0f}s")
                return True

        except Exception as e:
            logger.warning(f"   ❌ Error intento {intento}: {e}")
            if intento < max_reintentos:
                wait = intento * 30
                logger.info(f"   ⏳ Esperando {wait}s antes de reintentar...")
                time.sleep(wait)

    return False


def procesar_csv_adiciones(csv_path):
    """Procesa el CSV de adiciones y lo inserta en Supabase."""
    logger.info(f"📂 Procesando {csv_path}...")

    df = pd.read_csv(csv_path)
    logger.info(f"   Filas leidas: {len(df):,}")
    logger.info(f"   Columnas: {list(df.columns)}")

    # Normalizar columnas
    if "id_contrato" not in df.columns:
        logger.error("❌ Columna id_contrato no encontrada en CSV")
        return 0

    if "fecharegistro" in df.columns:
        df.rename(columns={"fecharegistro": "fecha_adicion"}, inplace=True)

    if "tipo" in df.columns:
        df.rename(columns={"tipo": "tipo_adicion"}, inplace=True)

    # Extraer valor de descripcion
    from scoring_logic import extraer_valor_adicion
    if "descripcion" in df.columns:
        logger.info("   🔍 Extrayendo valores de descripciones...")
        df["valor_adicion"] = df["descripcion"].apply(extraer_valor_adicion)
    else:
        df["valor_adicion"] = 0.0

    # Extraer duracion (dias adicionados)
    import re
    try:
        from workers.constants import REGEX_DURATION, DIAS_POR_UNIDAD
    except ImportError:
        from constants import REGEX_DURATION, DIAS_POR_UNIDAD

    def extract_duration(text):
        if not text or not isinstance(text, str): return 0
        total = 0
        for match in REGEX_DURATION.finditer(text.upper()):
            try:
                num_str = match.group(1) or match.group(2)
                cantidad = int(num_str)
                unidad = match.group(3).upper()
                total += cantidad * DIAS_POR_UNIDAD.get(unidad, 0)
            except (ValueError, AttributeError, TypeError):
                continue
        return total

    if "descripcion" in df.columns:
        logger.info("   📅 Extrayendo duraciones...")
        df["dias_adicionados"] = df["descripcion"].apply(extract_duration)

    # Renombrar para Supabase
    if "id_contrato" in df.columns:
        df.rename(columns={"id_contrato": "numero_contrato"}, inplace=True)

    # Columnas para Supabase
    cols = ["numero_contrato", "valor_adicion", "fecha_adicion", "descripcion", "dias_adicionados", "tipo_adicion"]
    cols = [c for c in cols if c in df.columns]

    # Asegurar que numero_contrato no sea nulo
    df = df[df["numero_contrato"].notna()]
    df = df.drop_duplicates(subset=["numero_contrato", "fecha_adicion"], keep="last")

    records = df[cols].to_dict(orient="records")
    logger.info(f"   📦 {len(records):,} registros listos para insertar")

    # Upsert en batches
    exitosos, fallidos = 0, 0
    total_batches = (len(records) + BATCH_SIZE_UPSERT - 1) // BATCH_SIZE_UPSERT
    logger.info(f"   Insertando en {total_batches} batches de {BATCH_SIZE_UPSERT}...")

    for i in range(0, len(records), BATCH_SIZE_UPSERT):
        batch = records[i:i + BATCH_SIZE_UPSERT]
        batch_num = (i // BATCH_SIZE_UPSERT) + 1
        try:
            supabase.table("adiciones_raw").upsert(batch).execute()
            exitosos += 1
            if batch_num % 10 == 0 or batch_num == total_batches:
                logger.info(f"   📊 {batch_num:>4}/{total_batches}   | ✅ OK        | {exitosos * BATCH_SIZE_UPSERT:>8,} regs")
        except Exception as e:
            fallidos += 1
            logger.error(f"   📊 {batch_num:>4}/{total_batches}   | ❌ FALLÓ     | {e}")

    logger.info(f"   ✅ FINALIZADO: {len(records):,} adiciones insertadas")
    return len(records)


def main():
    logger.info("=" * 70)
    logger.info("   LOTE 2: INGESTA DE ADICIONES")
    logger.info("=" * 70)

    # Estrategia 1: CSV directo
    if descargar_csv_directo():
        if os.path.exists(CSV_LOCAL_PATH):
            procesar_csv_adiciones(CSV_LOCAL_PATH)
            return

    # Estrategia 2: Verificar si ya existe CSV local
    if os.path.exists(CSV_LOCAL_PATH):
        logger.info("📂 Usando CSV local existente...")
        procesar_csv_adiciones(CSV_LOCAL_PATH)
        return

    logger.warning("⚠️ No se pudo descargar CSV. Los datos de adiciones pueden estar incompletos.")


if __name__ == "__main__":
    main()
