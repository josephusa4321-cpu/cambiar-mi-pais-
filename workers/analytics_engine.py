"""
analytics_engine.py - Tarea 4: Agregacion historica por ano/entidad
Lee contratos_scored y genera metricas_historicas
"""
import os
import logging
import pandas as pd
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

try:
    from workers.constants import BATCH_SIZE_UPSERT
except ImportError:
    from constants import BATCH_SIZE_UPSERT

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lupa.analytics")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_all_contracts_scored():
    """Obtiene todos los contratos scoreados con paginacion."""
    logger.info("📡 Obteniendo contratos_scored...")
    all_data = []
    page_size = 1000
    offset = 0

    while True:
        res = supabase.table("contratos_scored") \
            .select("id_contrato,score_total,nivel_riesgo,flags_detectadas,documento_proveedor") \
            .limit(page_size).offset(offset) \
            .execute()
        if not res.data:
            break
        all_data.extend(res.data)
        if len(res.data) < page_size:
            break
        offset += page_size

    logger.info(f"   ✅ {len(all_data):,} contratos scoreados obtenidos")
    return pd.DataFrame(all_data)


def fetch_all_contratos_raw():
    """Obtiene contratos_raw para agregaciones adicionales."""
    logger.info("📡 Obteniendo contratos_raw...")
    all_data = []
    page_size = 1000
    offset = 0

    while True:
        res = supabase.table("contratos_raw") \
            .select("id_contrato,nombre_entidad,nit_entidad,fecha_de_firma,modalidad_de_contratacion,valor_del_contrato") \
            .limit(page_size).offset(offset) \
            .execute()
        if not res.data:
            break
        all_data.extend(res.data)
        if len(res.data) < page_size:
            break
        offset += page_size

    logger.info(f"   ✅ {len(all_data):,} contratos raw obtenidos")
    return pd.DataFrame(all_data)


def run_analytics():
    """Ejecuta el motor de analytics y guarda en metricas_historicas."""
    logger.info("=" * 70)
    logger.info("   LOTE 5: ANALYTICS ENGINE")
    logger.info("=" * 70)

    # 1. Obtener datos
    df_scored = fetch_all_contracts_scored()
    if df_scored.empty:
        logger.warning("⚠️ No hay datos en contratos_scored")
        return

    df_raw = fetch_all_contratos_raw()
    if df_raw.empty:
        logger.warning("⚠️ No hay datos en contratos_raw")
        return

    # 2. Merge
    df = df_raw.merge(df_scored, on="id_contrato", how="left")
    logger.info(f"📊 Dataset unido: {len(df):,} contratos")

    # 3. Extraer ano de fecha_de_firma
    df["fecha_dt"] = pd.to_datetime(df["fecha_de_firma"], errors="coerce")
    df["anio"] = df["fecha_dt"].dt.year
    df = df.dropna(subset=["anio"])
    df["anio"] = df["anio"].astype(int)

    # 4. Sanitizar valores
    df["valor_del_contrato"] = pd.to_numeric(df["valor_del_contrato"], errors="coerce").fillna(0)
    df["score_total"] = pd.to_numeric(df["score_total"], errors="coerce").fillna(0)

    # 5. Agregar por anio + entidad
    logger.info("📊 Agregando metricas por ano y entidad...")
    metricas = []

    for (anio, entidad), group in df.groupby(["anio", "nombre_entidad"]):
        nit = group["nit_entidad"].iloc[0]
        total_contratos = len(group)
        valor_total = group["valor_del_contrato"].sum()

        # Modalidad directa
        directas = group[group["modalidad_de_contratacion"].str.contains("directa", case=False, na=False)]
        pct_directos = (len(directas) / total_contratos * 100) if total_contratos > 0 else 0
        valor_directos = directas["valor_del_contrato"].sum()

        # Score promedio
        score_promedio = group["score_total"].mean()

        # Contratos alto riesgo (score >= 55)
        contratos_alto_riesgo = len(group[group["score_total"] >= 55])

        metricas.append({
            "anio": anio,
            "nombre_entidad": str(entidad)[:200],
            "total_contratos": total_contratos,
            "valor_total": int(valor_total),
            "pct_directos": round(pct_directos, 2),
            "valor_directos": int(valor_directos),
            "score_promedio": round(score_promedio, 2),
            "contratos_alto_riesgo": contratos_alto_riesgo,
            "actualizado_en": datetime.now(timezone.utc).isoformat()
        })

    logger.info(f"   ✅ {len(metricas):,} combinaciones anio/entidad generadas")

    # 6. Upsert en metricas_historicas
    if not metricas:
        logger.info("   ⚠️ No hay metricas para insertar")
        return

    exitosos, fallidos = 0, 0
    total_batches = (len(metricas) + BATCH_SIZE_UPSERT - 1) // BATCH_SIZE_UPSERT
    logger.info(f"📦 Insertando {len(metricas):,} metricas ({total_batches} batches)...")

    for i in range(0, len(metricas), BATCH_SIZE_UPSERT):
        batch = metricas[i:i + BATCH_SIZE_UPSERT]
        batch_num = (i // BATCH_SIZE_UPSERT) + 1
        try:
            supabase.table("metricas_historicas").upsert(
                batch, on_conflict=["anio", "nombre_entidad"]
            ).execute()
            exitosos += 1
            logger.info(f"   📊 {batch_num:>4}/{total_batches}   | ✅ OK        | {exitosos * BATCH_SIZE_UPSERT:>8,} regs")
        except Exception as e:
            fallidos += 1
            logger.error(f"   📊 {batch_num:>4}/{total_batches}   | ❌ FALLÓ     | {e}")

    logger.info(f"{'-'*50}")
    logger.info(f"✅ Analytics completado: {len(metricas):,} metricas insertadas")


if __name__ == "__main__":
    run_analytics()
