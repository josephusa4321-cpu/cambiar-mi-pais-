import os
import logging
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lupa.scoring_v2")

# Config
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# LUPA Constants
SMMLV_2026 = 1_423_500
UMBRAL_MINIMA = 28 * SMMLV_2026   # ~$39.8M
UMBRAL_LICIT = 1000 * SMMLV_2026 # ~$1,423M

# --- RISK FLAGS ---

def flag_A1_contratacion_directa(row):
    """A1: Abuso de la contratación directa."""
    modalidad = str(row.get('modalidad_de_contratacion','')).lower()
    valor = float(row.get('valor_del_contrato', 0) or 0)
    
    if 'directa' not in modalidad: return 0, None
    
    if valor > UMBRAL_LICIT: return 30, f"Contratación directa de gran magnitud (${valor/1e9:.1f}B)"
    if valor > 500_000_000: return 20, f"Contratación directa de alto valor (${valor/1e6:.0f}M)"
    return 12, "Contratación directa sin competencia"

def flag_B1_sobrecosto_adicion(row, adiciones_sum):
    """B1: Adición presupuestal > 50% (Flag crítica legal)."""
    valor_original = float(row.get('valor_del_contrato', 1) or 1)
    ratio = adiciones_sum / valor_original
    
    if ratio > 0.50: return 40, f"⚠️ ADICIÓN ILEGAL: Supera el 50% del valor original ({ratio:.1%})"
    if ratio > 0.30: return 20, f"Adición sustancial del {ratio:.1%}"
    if ratio > 0.10: return 10, f"Adición del {ratio:.1%}"
    return 0, None

def flag_C2_prorroga_tiempo(row, dias_adicionados):
    """C2: Prórrogas excesivas en tiempo."""
    if dias_adicionados > 365: return 10, f"Contrato prorrogado más de 1 año ({dias_adicionados} días)"
    if dias_adicionados > 180: return 5, f"Contrato prorrogado más de 6 meses ({dias_adicionados} días)"
    return 0, None

def flag_D1_objeto_vago(row):
    """D1: Objeto del contrato sospechosamente genérico."""
    objeto = str(row.get('objeto_del_contrato', '') or '').lower()
    valor = float(row.get('valor_del_contrato', 0) or 0)
    VAGAS = ['apoyo a la gestion', 'servicios de apoyo', 'actividades administrativas']
    
    if any(p in objeto for p in VAGAS) and valor > 100_000_000:
        return 10, "Objeto genérico (Apoyo a la gestión) con valor alto"
    return 0, None

def calcular_score_total(row, ads_row):
    ads_valor = ads_row.get("valor_adicionado", 0) if pd.notna(ads_row) else 0
    ads_dias = ads_row.get("dias_adicionados", 0) if pd.notna(ads_row) else 0
    
    flags_list = []
    
    # Evaluar Flags
    f1_pts, f1_desc = flag_A1_contratacion_directa(row)
    if f1_pts > 0: flags_list.append({"cod": "A1", "pts": f1_pts, "desc": f1_desc})
    
    f2_pts, f2_desc = flag_B1_sobrecosto_adicion(row, ads_valor)
    if f2_pts > 0: flags_list.append({"cod": "B1", "pts": f2_pts, "desc": f2_desc})
    
    f3_pts, f3_desc = flag_C2_prorroga_tiempo(row, ads_dias)
    if f3_pts > 0: flags_list.append({"cod": "C2", "pts": f3_pts, "desc": f3_desc})
    
    f4_pts, f4_desc = flag_D1_objeto_vago(row)
    if f4_pts > 0: flags_list.append({"cod": "D1", "pts": f4_pts, "desc": f4_desc})
    
    total_score = sum(f['pts'] for f in flags_list)
    # Multiplicador por sistemática (si hay más de 3 flags, sumamos 10 puntos extra)
    if len(flags_list) >= 3: total_score += 10
    
    total_score = min(total_score, 100)
    
    nivel = "CRÍTICO" if total_score >= 80 else "ALTO" if total_score >= 60 else "MEDIO" if total_score >= 30 else "BAJO"
    
    return {
        "id_contrato": row["id_contrato"],
        "score_total": int(total_score),
        "nivel_riesgo": nivel,
        "flags_detectadas": [f['cod'] for f in flags_list],
        "traduccion_ciudadana": flags_list[0]['desc'] if flags_list else "Sin riesgos detectados",
        "documento_proveedor": str(row.get("documento_proveedor", ""))
    }

def run_scoring():
    if not supabase: return
    
    logger.info("🧠 Iniciando MOTOR DE SCORING V2 (Brain Mode)...")
    
    # 1. Obtener Contratos Raw
    res_contratos = supabase.table("contratos_raw").select("*").execute()
    df_contratos = pd.DataFrame(res_contratos.data)
    
    # 2. Obtener Agregado de Adiciones
    res_ads = supabase.table("contratos_adiciones").select("id_contrato, valor_adicionado, dias_adicionados").execute()
    df_ads = pd.DataFrame(res_ads.data)
    
    if not df_ads.empty:
        df_ads_grouped = df_ads.groupby("id_contrato").agg({
            "valor_adicionado": "sum",
            "dias_adicionados": "sum"
        }).reset_index()
    else:
        df_ads_grouped = pd.DataFrame(columns=["id_contrato", "valor_adicionado", "dias_adicionados"])
        
    # 3. Join y Scoring
    logger.info(f"Procesando scores para {len(df_contratos)} contratos...")
    
    scored_records = []
    for _, row in df_contratos.iterrows():
        # Buscar adiciones para este contrato
        ads_row = df_ads_grouped[df_ads_grouped["id_contrato"] == row["id_contrato"]]
        ads_data = ads_row.iloc[0] if not ads_row.empty else None
        
        score_data = calcular_score_total(row, ads_data)
        scored_records.append(score_data)
        
    # 4. Upsert a contratos_scored
    if scored_records:
        batch_size = 100
        for i in range(0, len(scored_records), batch_size):
            batch = scored_records[i : i + batch_size]
            supabase.table("contratos_scored").upsert(batch, on_conflict="id_contrato").execute()
            
    logger.info(f"✅ Scoring completado para {len(scored_records)} registros.")

if __name__ == "__main__":
    run_scoring()