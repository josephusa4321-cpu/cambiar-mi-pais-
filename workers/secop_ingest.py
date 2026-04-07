import os
import logging
import time
import re
from datetime import datetime, timezone
import pandas as pd
from sodapy import Socrata
from supabase import create_client, Client
from dotenv import load_dotenv

try:
    from workers.constants import REGEX_DURATION, UMBRAL_BUG_CENTAVOS
except ImportError:
    from constants import REGEX_DURATION, UMBRAL_BUG_CENTAVOS

load_dotenv()

# Logging Config
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lupa.ingest")

# --- Constantes de Performance y Blindaje ---
SODA_LIMIT_MAX = 5000     # Aumentado para eficiencia en loop
BATCH_SIZE_UPSERT = 500  # Optimizado para Supabase
HTTP_TIMEOUT = 90

try:
    from workers.constants import DIAS_POR_UNIDAD
except ImportError:
    from constants import DIAS_POR_UNIDAD

# Config de Entorno
SODA_TOKEN = os.environ.get("API_SOCRATA")
SODA_USER = os.environ.get("SODA_USER")
SODA_PASS = os.environ.get("SODA_PASS")
SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SERVICE_ROLE_KEY")

# Variables Globales
supabase: Client = None
soda_client: Socrata = None

def init_clients():
    global supabase, soda_client
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("⚠️ SUPABASE_URL o SERVICE_ROLE_KEY no configurados.")
        return False
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        soda_client = Socrata(
            "www.datos.gov.co",
            SODA_TOKEN if SODA_TOKEN != "REEMPLAZAR" else None,
            username=SODA_USER,
            password=SODA_PASS,
            timeout=HTTP_TIMEOUT
        )
        return True
    except Exception as e:
        logger.error(f"❌ Error en init_clients: {e}")
        return False

if __name__ == "__main__" or os.environ.get("LUPA_ENV") == "prod":
    init_clients()

# --- Datasets de SECOP II Medellín (Sprint 3 Schema) ---
DATASETS = {
    "contratos": {
        "url": "https://www.datos.gov.co/resource/jbjy-vk9h.json",
        "table": "contratos_raw",
        "id_col": "id_contrato",
        "soda_date_col": "fecha_de_firma"
    },
    "adiciones": {
        "url": "https://www.datos.gov.co/resource/cb9c-h8sn.json",
        "table": "adiciones_raw",  # Auditor Approved Table
        "id_col": "numero_contrato", # PK Compuesta en DB, pero pivotamos por contrato
        "soda_date_col": "fecharegistro"
    }
}

NIT_MEDELLIN = "890905211"

def sanitizar_valor(valor) -> float:
    if valor is None or str(valor).lower() in ["", "null", "na"]: return 0.0
    try:
        num = float(valor)
        if num > UMBRAL_BUG_CENTAVOS: return num / 100
        return num
    except (ValueError, TypeError): return 0.0

def extract_duration(text: str) -> int:
    if not text or not isinstance(text, str): return 0
    total = 0
    for match in REGEX_DURATION.finditer(text.upper()):
        try:
            # Grupo 1: "3 (TRES)" | Grupo 2: "TRES (3)" | Grupo 3: Unidad
            num_str = match.group(1) or match.group(2)
            cantidad = int(num_str)
            unidad   = match.group(3).upper() # El mapa DIAS_POR_UNIDAD ya maneja plurales y acentos
            total   += cantidad * DIAS_POR_UNIDAD.get(unidad, 0)
        except (ValueError, AttributeError, TypeError): continue
    return total

def fetch_dataset(dataset_name: str, last_run: str | None = None, full_history: bool = False) -> list:
    """Descarga datos con paginación SODA (Fix BUG-01)."""
    config = DATASETS[dataset_name]
    resource_id = config["url"].split("/")[-1].split(".")[0]

    all_data = []
    offset = 0
    limit = SODA_LIMIT_MAX

    # Construcción de query robusta
    # Filtro específico para cada dataset (Sprint 3 Blindaje)
    if dataset_name == "adiciones":
        # cb9c-h8sn no tiene columna 'ciudad' o 'nit_entidad' estructurada.
        # Filtramos por texto en la descripción (Medellín o NIT Alcaldía)
        where = "(upper(descripcion) like '%MEDELL%N%' OR upper(descripcion) like '%890905211%')"
    else:
        # jbjy-vk9h: Filtro robusto para Medellín (con/sin tilde)
        where = "upper(ciudad) LIKE '%MEDELL%N%'"

    if last_run and not full_history:
        clean_last = last_run.split('+')[0].split('.')[0]
        where += f" AND {config['soda_date_col']} > '{clean_last}'"

    mode_label = "FULL-HISTORY" if full_history else "DELTA"
    logger.info(f"📡 Iniciando fetch paginado [{mode_label}]: {dataset_name} | Where: {where}")
    logger.info(f"📊 Página   | Registros   | Total Acumulado")
    logger.info(f"{'-'*50}")
    pagina = 0

    while True:
        try:
            data = soda_client.get(resource_id, where=where, limit=limit, offset=offset, order=f"{config['soda_date_col']} ASC")
            pagina += 1
            count = len(data) if data else 0
            logger.info(f"📊 Pág {pagina:>4}   | {count:>6} regs   | {len(all_data) + count:>8,}")
            if not data: break
            all_data.extend(data)
            if len(data) < limit: break
            # Safety limit only in delta mode; full-history fetches everything
            if not full_history and len(all_data) >= 5000:
                logger.info("   - Límite de seguridad de 5,000 registros alcanzado.")
                break
            offset += limit
        except Exception as e:
            logger.error(f"❌ Error en paginación offset {offset}: {e}")
            if full_history:
                wait = 15
                logger.info(f"   ⏳ Retrying in {wait}s...")
                time.sleep(wait)
                continue
            break

    logger.info(f"{'-'*50}")
    logger.info(f"✅ [{dataset_name.upper()}] Total descargado: {len(all_data):,} registros")
    return all_data

def clean_data(df: pd.DataFrame, dataset_name: str, adiciones_cache: dict = None) -> pd.DataFrame:
    if df.empty: return df

    # BUG-04: Resiliencia de Schema (Ciudad)
    if "ciudad" not in df.columns:
        df["ciudad"] = "Medellín" # Default para este dataset

    # Mapeo de columnas según estándar de Auditoría Sprint 3
    if dataset_name == "adiciones":
        df.rename(columns={
            "id_contrato": "numero_contrato",
            "fecharegistro": "fecha_adicion",
        }, inplace=True)

        # El API cb9c-h8sn NO tiene columna valor_adicionado
        # El valor está embebido en descripcion — extraerlo con regex
        if "descripcion" in df.columns:
            try:
                from workers.scoring_logic import extraer_valor_adicion
            except ImportError:
                from scoring_logic import extraer_valor_adicion
            df["valor_adicion"] = df["descripcion"].apply(extraer_valor_adicion)
        else:
            df["valor_adicion"] = 0.0

        # C2: Extracción de duración de prórrogas
        df["dias_adicionados"] = df["descripcion"].apply(extract_duration)

        # Agregar múltiples adiciones por contrato (sumar valores y días)
        # y deduplicar para evitar ON CONFLICT duplicates en Supabase
        if "numero_contrato" in df.columns:
            df = df.groupby("numero_contrato").agg({
                "valor_adicion": "sum",
                "dias_adicionados": "sum",
                "descripcion": "first",
                "fecha_adicion": "first",
                "tipo": "first",
            }).reset_index()

    else:
        df.rename(columns={"ultima_actualizacion": "fecha_de_ultima_actualizacion"}, inplace=True)

    # Inyección de B1 Estructurado (Phase 1)
    if dataset_name == "contratos" and adiciones_cache is not None:
        df["valor_contrato_con_adiciones"] = df["id_contrato"].map(adiciones_cache).fillna(0)
        df["valor_contrato_con_adiciones"] += df["valor_del_contrato"].apply(sanitizar_valor)

    # 4. BUG-02: Sanitización total
    val_cols = ["valor_del_contrato", "valor_adicion"]
    for col in val_cols:
        if col in df.columns:
            df[col] = df[col].apply(sanitizar_valor)

    return df

def update_meta(pipeline_name: str, records: int, exito: int, fallo: int):
    # BUG-03: Precisión de Meta OK/PARCIAL
    now = datetime.now(timezone.utc).isoformat()
    estado = "OK" if fallo == 0 and records > 0 else "PARCIAL"
    if records == 0: estado = "SIN_DATOS"
    
    try:
        supabase.table("meta_pipeline").upsert({
            "nombre_pipeline": pipeline_name,
            "ultima_ejecucion_exitosa": now,
            "registros_procesados": records,
            "batches_exitosos": exito,
            "batches_fallidos": fallo,
            "estado": estado
        }, on_conflict="nombre_pipeline").execute()
    except Exception as e:
        logger.error(f"Error meta_pipeline: {e}")

def run_dataset_ingest(name: str, full_history: bool = False):
    logger.info(f"🚀 INGESTA: {name.upper()}")

    if full_history:
        last_run = None
    else:
        res_meta = supabase.table("meta_pipeline").select("ultima_ejecucion_exitosa").eq("nombre_pipeline", f"ingesta_{name}").execute()
        last_run = res_meta.data[0].get("ultima_ejecucion_exitosa") if res_meta.data else None

    data = fetch_dataset(name, last_run, full_history=full_history)
    if not data:
        logger.info(f"   - Sin novedades para {name}.")
        update_meta(f"ingesta_{name}", 0, 0, 0)
        return

    # Cache de adiciones para B1
    adiciones_map = {}
    if name == "contratos":
        logger.info("📡 Pre-cargando adiciones para B1...")
        ads_raw = fetch_dataset("adiciones")
        for ad in ads_raw:
            cid = ad.get("id_contrato")
            # El API no tiene valor_adicionado — extraer de descripcion
            val = sanitizar_valor(ad.get("valor_adicionado", 0))
            if val == 0 and ad.get("descripcion"):
                try:
                    from workers.scoring_logic import extraer_valor_adicion
                    val = extraer_valor_adicion(ad.get("descripcion", ""))
                except ImportError:
                    from scoring_logic import extraer_valor_adicion
                    val = extraer_valor_adicion(ad.get("descripcion", ""))
            if cid: adiciones_map[cid] = adiciones_map.get(cid, 0) + val

    df = clean_data(pd.DataFrame(data), name, adiciones_cache=adiciones_map if name == "contratos" else None)
    
    target_table = DATASETS[name]["table"]
    # Columnas según Schema de Auditoría de Sprint 3
    supabase_cols = {
        "contratos_raw": ["id_contrato", "nombre_entidad", "nit_entidad", "ciudad", "sector", "objeto_del_contrato", "modalidad_de_contratacion", "valor_del_contrato", "documento_proveedor", "proveedor_adjudicado", "fecha_de_firma", "estado_contrato", "valor_contrato_con_adiciones"],
        "adiciones_raw": ["numero_contrato", "valor_adicion", "fecha_adicion", "descripcion", "dias_adicionados", "tipo"]
    }

    logger.info(f"📊 Columnas en DataFrame: {list(df.columns)}")
    cols = [c for c in supabase_cols.get(target_table, []) if c in df.columns]
    logger.info(f"📊 Columnas filtradas para Supabase: {cols}")
    records = df[cols].to_dict(orient="records")

    b_exitosos, b_fallidos = 0, 0
    # Each table has a different PK for on_conflict
    pk_col = {
        "contratos_raw": "id_contrato",
        "adiciones_raw": "numero_contrato",
    }

    total_batches = (len(records) + BATCH_SIZE_UPSERT - 1) // BATCH_SIZE_UPSERT
    logger.info(f"📦 Insertando {len(records):,} registros en {target_table} ({total_batches} batches de {BATCH_SIZE_UPSERT})...")
    logger.info(f"📊 Batch    | Estado      | Acumulado")
    logger.info(f"{'-'*50}")

    for i in range(0, len(records), BATCH_SIZE_UPSERT):
        batch = records[i:i + BATCH_SIZE_UPSERT]
        batch_num = (i // BATCH_SIZE_UPSERT) + 1
        try:
            res = supabase.table(target_table).upsert(batch, on_conflict=pk_col.get(target_table, "id")).execute()
            b_exitosos += 1
            logger.info(f"📊 {batch_num:>4}/{total_batches}   | ✅ OK        | {b_exitosos * BATCH_SIZE_UPSERT:>8,} regs")
        except Exception as e:
            b_fallidos += 1
            logger.error(f"📊 {batch_num:>4}/{total_batches}   | ❌ FALLÓ     | {e}")

    logger.info(f"{'-'*50}")

    update_meta(f"ingesta_{name}", len(records), b_exitosos, b_fallidos)
    logger.info(f"✅ FINALIZADO: {name.upper()} — OK: {b_exitosos} batches | Fallidos: {b_fallidos}")

if __name__ == "__main__":
    import sys
    modo = sys.argv[1] if len(sys.argv) > 1 else "delta"
    full = modo == "full-history"
    # Orden Auditor: Contratos primero (mapea B1), luego Adiciones (viste C2)
    for ds in ["contratos", "adiciones"]:
        run_dataset_ingest(ds, full_history=full)
