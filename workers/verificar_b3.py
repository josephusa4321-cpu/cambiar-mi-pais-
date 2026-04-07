"""
verificar_b3.py - Tarea 5: Verificar B3 con query de concentracion
"""
import os
import logging
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lupa.b3_verify")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_all_contratos():
    """Obtiene todos los contratos_raw."""
    logger.info("📡 Obteniendo contratos_raw...")
    all_data = []
    page_size = 1000
    offset = 0

    while True:
        res = supabase.table("contratos_raw") \
            .select("documento_proveedor,nit_entidad,valor_del_contrato,fecha_de_firma,modalidad_de_contratacion") \
            .limit(page_size).offset(offset) \
            .execute()
        if not res.data:
            break
        all_data.extend(res.data)
        if len(res.data) < page_size:
            break
        offset += page_size

    logger.info(f"   ✅ {len(all_data):,} contratos obtenidos")
    return pd.DataFrame(all_data)


def verificar_b3():
    """Verifica concentracion de proveedores (query SQL equivalente)."""
    logger.info("=" * 70)
    logger.info("   LOTE 6: VERIFICAR B3 - Query de Concentracion")
    logger.info("=" * 70)

    df = fetch_all_contratos()
    if df.empty:
        logger.warning("⚠️ No hay datos")
        return

    # Filtrar contratacion directa
    df["valor_del_contrato"] = pd.to_numeric(df["valor_del_contrato"], errors="coerce").fillna(0)
    df_directas = df[df["modalidad_de_contratacion"].str.contains("directa", case=False, na=False)]

    logger.info(f"📊 Contratos directos: {len(df_directas):,} de {len(df):,} totales")

    # Agrupar por proveedor + entidad
    concentracion = df_directas.groupby(["documento_proveedor", "nit_entidad"]).agg(
        contratos=("documento_proveedor", "count"),
        valor_total=("valor_del_contrato", "sum")
    ).reset_index()

    # Filtrar proveedores con >= 3 contratos
    top = concentracion[concentracion["contratos"] >= 3].sort_values("contratos", ascending=False)

    logger.info("")
    logger.info(f"Proveedores con >= 3 contratos directos: {len(top):,}")
    logger.info("")
    logger.info(f"{'Proveedor':<16} {'NIT Entidad':<16} {'Contratos':>10} {'Valor Total':>25}")
    logger.info("-" * 70)

    for _, row in top.head(20).iterrows():
        doc = str(row["documento_proveedor"])[:14]
        nit = str(row["nit_entidad"])[:14]
        contratos = row["contratos"]
        valor = f"${row['valor_total']:,.0f}"
        logger.info(f"{doc:<16} {nit:<16} {contratos:>10,} {valor:>25}")

    if len(top) > 20:
        logger.info(f"   ... y {len(top) - 20:,} mas")

    logger.info("")
    logger.info("=" * 70)
    if len(top) > 0:
        logger.info(f"✅ B3: {len(top):,} proveedores con concentracion detectada")
        logger.info("   Si B3 en scoring_engine muestra 0 → HAY BUG")
        logger.info("   Si B3 muestra > 0 → FUNCIONANDO OK")
    else:
        logger.info("⚠️ No se encontro concentracion significativa")
    logger.info("=" * 70)


if __name__ == "__main__":
    verificar_b3()
