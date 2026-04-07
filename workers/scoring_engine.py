import os
import logging
import pandas as pd
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

# Importar el ÚNICO cerebro certificado
# Se asume ejecución desde la raíz del proyecto para resolver el paquete
try:
    from workers.scoring_logic import score_single_contract
    from workers.constants import (
        SMMLV_2026, UMBRAL_LICIT, UMBRAL_MINIMA,
        COLUMNAS_SCORING, BATCH_SIZE_UPSERT
    )
except ImportError:
    # Fallback para ejecución directa desde la carpeta workers/
    from scoring_logic import score_single_contract
    from constants import (
        SMMLV_2026, UMBRAL_LICIT, UMBRAL_MINIMA,
        COLUMNAS_SCORING, BATCH_SIZE_UPSERT
    )

load_dotenv()
logger = logging.getLogger("lupa.engine")

SUPABASE_URL = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError("SUPABASE_URL o SUPABASE_SERVICE_KEY no configurados")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def run_scoring(modo: str = "delta") -> None:
    """
    Orquestador de scoring. Lee contratos_raw, hace JOIN con adiciones,
    llama al motor puro score_single_contract(), y persiste en contratos_scored.
    
    modo: "delta" (default) — solo contratos nuevos desde último run
          "full" — reprocesa todo el histórico
    """
    logger.info(f"🧠 LUPA Engine iniciando | Modo: {modo.upper()}")

    # --- 1. Delta: obtener timestamp del último run ---
    ultimo_run = None
    if modo == "delta":
        try:
            res_meta = supabase.table("meta_pipeline") \
                .select("ultima_ejecucion_exitosa") \
                .eq("nombre_pipeline", "scoring_engine") \
                .execute()
            if res_meta.data:
                ultimo_run = res_meta.data[0].get("ultima_ejecucion_exitosa")
                logger.info(f"Delta desde: {ultimo_run}")
        except Exception as e:
            logger.warning(f"No se pudo leer meta_pipeline: {e} — procesando todo")

    # --- 1.2 Carga de base de datos SIRI (Procuraduría) ---
    df_siri = pd.DataFrame()
    siri_path = os.path.join("workers", "data", "siri_total.csv")
    if os.path.exists(siri_path):
        try:
            df_siri = pd.read_csv(siri_path, dtype={"numero_identificacion": str})
            df_siri["numero_identificacion"] = df_siri["numero_identificacion"].str.strip()
            logger.info(f"📁 SIRI Cache: {len(df_siri)} registros cargados correctamente.")
        except Exception as e:
            logger.error(f"❌ Error cargando SIRI CSV: {e}")
    else:
        logger.warning(f"⚠️ SIRI Cache no encontrado en {siri_path}. B1 permanecerá inactiva.")

    # --- 2. Cargar contratos (solo columnas necesarias) ---
    try:
        # COLUMNAS_SCORING es una lista en constants.py, Supabase select() espera string
        select_cols = ",".join(COLUMNAS_SCORING)
        all_contracts = []
        page_size = 1000
        offset = 0
        while True:
            query = supabase.table("contratos_raw").select(select_cols).limit(page_size).offset(offset)
            if ultimo_run:
                query = query.gt("ultima_actualizacion", ultimo_run)
            res = query.execute()
            if not res.data:
                break
            all_contracts.extend(res.data)
            if len(res.data) < page_size:
                break
            offset += page_size
        df_contratos = pd.DataFrame(all_contracts)
    except Exception as e:
        logger.error(f"❌ Error leyendo contratos_raw: {e}")
        return

    if df_contratos.empty:
        logger.info("No hay contratos nuevos para procesar.")
        return

    logger.info(f"Contratos a procesar: {len(df_contratos)}")

    # --- 3. Cargar adiciones (resiliente si tabla no existe) ---
    try:
        all_adiciones = []
        page_size = 1000
        offset = 0
        while True:
            res_ads_page = supabase.table("adiciones_raw") \
                .select("numero_contrato, valor_adicion, dias_adicionados, descripcion") \
                .limit(page_size).offset(offset) \
                .execute()
            if not res_ads_page.data:
                break
            all_adiciones.extend(res_ads_page.data)
            if len(res_ads_page.data) < page_size:
                break
            offset += page_size
        df_ads = pd.DataFrame(all_adiciones)

        if not df_ads.empty:
            # FIX C1: Extraer valor de la descripción si valor_adicion es 0 o nulo
            from scoring_logic import extraer_valor_adicion  # Import local para evitar circularidad
            
            df_ads["valor_adicionado_raw"] = pd.to_numeric(df_ads["valor_adicion"], errors="coerce").fillna(0)
            df_ads["valor_adicionado_regex"] = df_ads["descripcion"].apply(extraer_valor_adicion)
            
            # Si el raw es 0, usamos el regex (Prioridad: Raw > Regex si Raw > 0)
            df_ads["valor_final_adicion"] = df_ads.apply(
                lambda x: x["valor_adicionado_raw"] if x["valor_adicionado_raw"] > 0 else x["valor_adicionado_regex"],
                axis=1
            )
            df_ads["dias_adicionados"] = pd.to_numeric(
                df_ads["dias_adicionados"], errors="coerce"
            ).fillna(0)

            df_ads_grouped = df_ads.groupby("numero_contrato").agg(
                valor_adicionado=("valor_final_adicion", "sum"),
                dias_adicionados=("dias_adicionados", "sum")
            ).reset_index()
            df_ads_grouped.rename(columns={"numero_contrato": "id_contrato"}, inplace=True)
        else:
            df_ads_grouped = pd.DataFrame(
                columns=["id_contrato", "valor_adicionado", "dias_adicionados"]
            )

    except Exception as e:
        logger.warning(f"contratos_adiciones no disponible: {e} — B1/C2 inactivas")
        df_ads_grouped = pd.DataFrame(
            columns=["id_contrato", "valor_adicionado", "dias_adicionados"]
        )

    # --- 4. JOIN MAESTRO (O(N log N), no O(N²)) ---
    # Un solo merge antes del loop — jamás filtrar dentro del loop
    df_merged = df_contratos.merge(df_ads_grouped, on="id_contrato", how="left")
    df_merged["valor_adicionado"] = df_merged.get("valor_adicionado", pd.Series(dtype=float)).fillna(0)
    df_merged["dias_adicionados"] = df_merged.get("dias_adicionados", pd.Series(dtype=float)).fillna(0)

    # --- 5. Cargar historial de entidad para flags contextuales (B3, C2, D2) ---
    try:
        all_history = []
        page_size = 1000
        offset = 0
        while True:
            res_hist_page = supabase.table("contratos_raw") \
                .select("documento_proveedor, valor_del_contrato, nit_entidad, fecha_de_firma, modalidad_de_contratacion") \
                .limit(page_size).offset(offset) \
                .execute()
            if not res_hist_page.data:
                break
            all_history.extend(res_hist_page.data)
            if len(res_hist_page.data) < page_size:
                break
            offset += page_size
        df_historial = pd.DataFrame(all_history)
        df_historial["valor_del_contrato"] = pd.to_numeric(
            df_historial["valor_del_contrato"], errors="coerce"
        ).fillna(0)
    except Exception as e:
        logger.warning(f"No se pudo cargar historial para B3: {e}")
        df_historial = pd.DataFrame()

    # --- 6. Loop de scoring (solo transporte de datos) ---
    scored_records = []
    total_contracts = len(df_merged)
    logger.info(f"🧠 Iniciando scoring de {total_contracts:,} contratos...")
    logger.info(f"📊 Contrato  | Score | Nivel  | Bandas | Acumulado")
    logger.info(f"{'-'*65}")

    for idx, (_, row) in enumerate(df_merged.iterrows(), 1):
        contrato_dict = row.to_dict()

        # Construir adiciones_df para este contrato (ya agregado, 1 fila max)
        adiciones_dict = {
            "valor_adicionado": row.get("valor_adicionado", 0),
            "dias_adicionados": row.get("dias_adicionados", 0)
        }
        adiciones_df = pd.DataFrame([adiciones_dict]) if adiciones_dict["valor_adicionado"] > 0 \
                       else pd.DataFrame()

        # Filtrar historial de la entidad del contrato actual (en memoria, no query)
        nit = str(contrato_dict.get("nit_entidad", ""))
        history_df = df_historial[df_historial["nit_entidad"] == nit].copy() \
                     if not df_historial.empty and nit else pd.DataFrame()

        # ÚNICO CEREBRO CERTIFICADO (v1.1 con SIRI B1)
        resultado = score_single_contract(contrato_dict, history_df, adiciones_df, df_siri)

        scored_records.append({
            "id_contrato":         contrato_dict["id_contrato"],
            "score_total":         resultado["score_total"],
            "nivel_riesgo":        resultado["nivel_riesgo"],
            "flags_detectadas":    resultado["banderas"],
            "traduccion_ciudadana": resultado["traduccion"],
            "documento_proveedor": str(contrato_dict.get("documento_proveedor", "")),
            "scored_at":           datetime.now(timezone.utc).isoformat()
        })

        # Log progress cada 100 contratos o si es alto riesgo
        if idx % 100 == 0 or resultado["score_total"] >= 40:
            flags_str = ",".join(resultado["banderas"]) if resultado["banderas"] else "-"
            logger.info(f"📊 {idx:>6,}/{total_contracts:,} | {resultado['score_total']:>5} | {resultado['nivel_riesgo']:<6} | {flags_str:<20} | {idx:>6,}")

    logger.info(f"{'-'*65}")
    logger.info(f"✅ Scoring completado: {len(scored_records):,} contratos procesados")

    # --- 7. Batch UPSERT (500 por transacción) ---
    exitosos, fallidos = 0, 0
    total_batches = (len(scored_records) + BATCH_SIZE_UPSERT - 1) // BATCH_SIZE_UPSERT
    logger.info(f"📦 Guardando {len(scored_records):,} scores en Supabase ({total_batches} batches)...")
    logger.info(f"📊 Batch    | Estado      | Acumulado")
    logger.info(f"{'-'*50}")

    for i in range(0, len(scored_records), BATCH_SIZE_UPSERT):
        batch = scored_records[i : i + BATCH_SIZE_UPSERT]
        batch_num = (i // BATCH_SIZE_UPSERT) + 1
        try:
            supabase.table("contratos_scored") \
                .upsert(batch, on_conflict="id_contrato") \
                .execute()
            exitosos += 1
            logger.info(f"📊 {batch_num:>4}/{total_batches}   | ✅ OK        | {exitosos * BATCH_SIZE_UPSERT:>8,} regs")
        except Exception as e:
            fallidos += 1
            logger.error(f"📊 {batch_num:>4}/{total_batches}   | ❌ FALLÓ     | {e}")

    logger.info(f"{'-'*50}")

    # --- 8. Actualizar meta_pipeline ---
    estado = "OK" if fallidos == 0 else "PARCIAL"
    try:
        supabase.table("meta_pipeline").upsert({
            "nombre_pipeline":            "scoring_engine",
            "ultima_ejecucion_exitosa":   datetime.now(timezone.utc).isoformat(),
            "registros_procesados":       len(scored_records),
            "batches_exitosos":           exitosos,
            "batches_fallidos":           fallidos,
            "estado":                     estado
        }, on_conflict="nombre_pipeline").execute()
    except Exception as e:
        logger.error(f"Error actualizando meta_pipeline: {e}")

    logger.info(
        f"✅ Engine completado | Modo: {modo} | "
        f"Procesados: {len(scored_records)} | "
        f"Batches OK: {exitosos} | Fallidos: {fallidos}"
    )


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    modo = sys.argv[1] if len(sys.argv) > 1 else "delta"
    run_scoring(modo=modo)
