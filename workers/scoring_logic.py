import pandas as pd
import re
import logging
try:
    from workers.constants import (
        SMMLV_2026, UMBRAL_MINIMA, UMBRAL_LICIT,
        UMBRAL_NIVEL1, UMBRAL_NIVEL2, UMBRAL_NIVEL3,
        UMBRAL_BUG_CENTAVOS,
        PESO_A1, 
        PESO_B1, PESO_B3, PESO_C1_MAX, PESO_C1_MED, PESO_C1_MIN, 
        PESO_C2, PESO_D1, PESO_D2, PESO_BONUS,
        UMBRAL_C1_CRITICO, UMBRAL_C1_MEDIO, UMBRAL_C1_MINIMO,
        MODALIDADES_ACTT
    )
except ImportError:
    from constants import (
        SMMLV_2026, UMBRAL_MINIMA, UMBRAL_LICIT,
        UMBRAL_NIVEL1, UMBRAL_NIVEL2, UMBRAL_NIVEL3,
        UMBRAL_BUG_CENTAVOS,
        PESO_A1, 
        PESO_B1, PESO_B3, PESO_C1_MAX, PESO_C1_MED, PESO_C1_MIN, 
        PESO_C2, PESO_D1, PESO_D2, PESO_BONUS,
        UMBRAL_C1_CRITICO, UMBRAL_C1_MEDIO, UMBRAL_C1_MINIMO,
        MODALIDADES_ACTT
    )

logger = logging.getLogger("lupa.scoring_logic")

# --- NIVEL DE RIESGO ---
UMBRAL_BAJO = 0
UMBRAL_MEDIO = 40
UMBRAL_ALTO = 55
UMBRAL_CRITICO = 70

# Listas de NITs para Atenuación ACTT (PRD §6.5)
NITS_ACTT = [
    "890980040", # Universidad de Antioquia
    "890980093", # SENA
    "800116569", # ITM
    "800147663", # Pascual Bravo
    "800155139", # Colegio Mayor
    "890905156", # Politécnico JIC
]

ICD_FIELDS = [
    "nombre_entidad", "nit_entidad", "modalidad_de_contratacion", 
    "valor_del_contrato", "documento_proveedor", "proveedor_adjudicado", 
    "fecha_de_firma", "numero_de_oferentes", "objeto_del_contrato"
]

def sanitizar_valor(valor) -> float:
    """Consistencia con el ingestor: corta el bug x100."""
    if valor is None or valor == "": return 0.0
    try:
        num = float(valor)
        if num > UMBRAL_BUG_CENTAVOS: return num / 100
        return num
    except (ValueError, TypeError): return 0.0

def extraer_valor_adicion(descripcion: str) -> float:
    """Extrae valor monetario del texto de descripción de adición (PRD §6.2 Fix)."""
    if not descripcion or not isinstance(descripcion, str):
        return 0.0
    
    # Patrones recomendados por Auditoría
    patterns = [
        r'(?:suma|valor|adiciona[r]?|incrementa[r]?)\s+(?:de\s+)?\$?\s*([\d.,]+)',
        r'\$\s*([\d.,]+)',
        r'([\d.]{7,})',  # fallback: número largo > 7 dígitos
    ]
    
    for pattern in patterns:
        match = re.search(pattern, descripcion, re.IGNORECASE)
        if match:
            # Limpiar puntos y comas para conversión a float
            val_str = match.group(1).replace('.', '').replace(',', '')
            try:
                v = float(val_str)
                # Sanity check: $1M - $500B
                if 1_000_000 <= v <= 500_000_000_000:
                    return v
            except: continue
    return 0.0

def _flag_siri_blocked(documento: str, df_siri: pd.DataFrame) -> tuple[bool, int, str]:
    """
    B1 SIRI (S1.7): Proveedor con antecedentes en Procuraduría.
    """
    if df_siri is None or df_siri.empty or not documento:
        return False, 0, ""
    
    # Limpieza agresiva de strings para el cruce
    doc_str = str(documento).strip()
    # SIRI CSV tiene numero_identificacion como columna
    match = df_siri[df_siri["numero_identificacion"].astype(str).str.strip() == doc_str]
    
    if not match.empty:
        return True, PESO_B1, "B1: Proveedor registrado en el boletín de sanciones e inhabilitades (SIRI)."
    return False, 0, ""

def _flag_c1_adiciones(contrato: dict) -> tuple[bool, int, str]:
    """
    C1: Adiciones Graduadas (PRD §6.2).
    Aplica escala: >50% (10), >30% (6), >15% (3).
    """
    valor_original = sanitizar_valor(contrato.get("valor_del_contrato")) or 0.0

    # Try valor_contrato_con_adiciones first (from ingest), then valor_adicionado (from scoring engine join)
    valor_con_adicion = sanitizar_valor(contrato.get("valor_contrato_con_adiciones")) or 0.0
    valor_adicionado = float(contrato.get("valor_adicionado", 0) or 0)

    # If no real addition was computed at ingest, use the adiciones_raw sum from the engine join
    if valor_con_adicion <= valor_original and valor_adicionado > 0:
        valor_con_adicion = valor_original + valor_adicionado

    if valor_original <= 0 or valor_con_adicion <= valor_original:
        return False, 0, ""

    ratio = (valor_con_adicion - valor_original) / valor_original
    
    if ratio > UMBRAL_C1_CRITICO:
        return True, PESO_C1_MAX, f"C1: Adición crítica ({ratio:.1%}) supera el 50% del valor original."
    if ratio > UMBRAL_C1_MEDIO:
        return True, PESO_C1_MED, f"C1: Adición elevada ({ratio:.1%}) supera el 30% del valor original."
    if ratio > UMBRAL_C1_MINIMO:
        return True, PESO_C1_MIN, f"C1: Adición significativa ({ratio:.1%}) supera el 15% del valor original."
        
    return False, 0, ""

def calculate_icd(contrato: dict):
    faltantes = [f for f in ICD_FIELDS if not contrato.get(f)]
    score = int(((len(ICD_FIELDS) - len(faltantes)) / len(ICD_FIELDS)) * 100)
    return score, faltantes

def get_citizen_translation(flags: list):
    """Recibe lista de IDs de banderas (A1, B1, etc.)"""
    if not flags: return "No se detectaron riesgos algorítmicos significativos."
    t = []
    if "A1" in flags: t.append("Contratación directa de gran magnitud sin competencia.")
    if "C1" in flags: t.append("Adición que supera el umbral estadístico sobre el valor original.")
    if "B3" in flags: t.append("Concentración inusual de contratos en este contratista.")
    if "C2" in flags: t.append("Posible fraccionamiento (múltiples contratos en ventana corta).")
    if "D1" in flags: t.append("La descripción del contrato es vaga para el monto ejecutado.")
    if "D2" in flags: t.append("Entidad con uso histórico excesivo de contratación directa.")
    if "BONUS" in flags: t.append("Patrón sistémico: múltiples alertas detectadas simultáneamente.")
    return " ".join(t[:2])

def score_single_contract(contrato: dict, history_df: pd.DataFrame, adiciones_df: pd.DataFrame, siri_df: pd.DataFrame = None):
    """
    contrato: dict del contrato actual
    history_df: historial de la entidad (vacío por ahora para B3)
    adiciones_df: adiciones (Phase 2 logic)
    siri_df: base de datos de sancionados (SIRI)
    """
    flags_detalle = []
    score_total = 0
    categories = set()
    
    valor = sanitizar_valor(contrato.get("valor_del_contrato"))
    modalidad = str(contrato.get("modalidad_de_contratacion", "")).lower()
    
    # --- A1: Contratación Directa (PRD §6.1) ---
    if "directa" in modalidad:
        # Revertido a flat 12 pts según instrucción del usuario
        puntos = PESO_A1
        desc = f"A1: Contratación directa de magnitud significativa ($ {valor:,.0f})."
        
        flags_detalle.append({"bandera": "A1", "puntos": puntos, "desc": desc})
        score_total += puntos
        categories.add("A")

    # --- B1: SIRI (Antecedentes) ---
    doc_id = str(contrato.get("documento_proveedor", ""))
    activa, puntos, desc = _flag_siri_blocked(doc_id, siri_df)
    if activa:
        flags_detalle.append({"bandera": "B1", "puntos": puntos, "desc": desc})
        score_total += puntos
        categories.add("B")

    # --- B3: Concentración (>50% en 12m) ---
    doc_id = str(contrato.get("documento_proveedor", ""))
    if not history_df.empty and doc_id:
        # Use contract date as reference point, not "today"
        current_date = pd.to_datetime(contrato.get("fecha_de_firma"), errors="coerce", utc=True)
        if pd.isnull(current_date):
            current_date = pd.Timestamp.now(tz='UTC')

        # Convertir fechas para filtros temporales
        history_df = history_df.copy()
        history_df["fecha_dt"] = pd.to_datetime(history_df["fecha_de_firma"], errors="coerce", utc=True)

        # Ventana 12 meses desde la fecha del contrato
        h12m = history_df[history_df["fecha_dt"] >= (current_date - pd.DateOffset(months=12))]
        h12m = h12m[h12m["fecha_dt"] <= current_date]
        
        total_entidad = h12m["valor_del_contrato"].sum()
        total_proveedor = h12m[h12m["documento_proveedor"] == doc_id]["valor_del_contrato"].sum()
        
        if total_entidad > 0 and (total_proveedor / total_entidad) > 0.50:
            puntos = PESO_B3
            desc = f"B3: Contratista concentra el {(total_proveedor / total_entidad):.1%} del presupuesto de la entidad en los últimos 12 meses."
            flags_detalle.append({"bandera": "B3", "puntos": puntos, "desc": desc})
            score_total += puntos
            categories.add("B")

    # --- C1: Adiciones Graduadas ---
    activa, puntos, desc = _flag_c1_adiciones(contrato)
    if activa:
        flags_detalle.append({"bandera": "C1", "puntos": puntos, "desc": desc})
        score_total += puntos
        categories.add("C")

    # --- C2: Fraccionamiento (60 días) ---
    if not history_df.empty and doc_id:
        entidad = contrato.get("nit_entidad")
        current_date = pd.to_datetime(contrato.get("fecha_de_firma"), errors="coerce", utc=True)
        
        if pd.notnull(current_date):
            # Buscar otros contratos directos al mismo proveedor en < 60 días
            recent = history_df[
                (history_df["nit_entidad"] == entidad) & 
                (history_df["documento_proveedor"] == doc_id) &
                (pd.to_datetime(history_df["fecha_de_firma"], errors="coerce", utc=True) >= (current_date - pd.DateOffset(days=60))) &
                (pd.to_datetime(history_df["fecha_de_firma"], errors="coerce", utc=True) <= current_date)
            ]
            if len(recent) >= 2:
                puntos = PESO_C2
                desc = f"C2: Detectados {len(recent)} contratos directos a este contratista en ventana de 60 días (Posible fraccionamiento)."
                flags_detalle.append({"bandera": "C2", "puntos": puntos, "desc": desc})
                score_total += puntos
                categories.add("C")

    # --- D1: Objeto Vago (6 pts) ---
    desc_obj = str(contrato.get("objeto_del_contrato") or contrato.get("descripcion_del_proceso", "")).lower()
    if len(desc_obj.split()) < 8 and valor > 100_000_000:
        puntos = PESO_D1
        desc = "D1: Descripción del objeto vaga para un monto superior a 100M COP."
        flags_detalle.append({"bandera": "D1", "puntos": puntos, "desc": desc})
        score_total += puntos
        categories.add("D")

    # --- D2: Historical Ratio (80%) ---
    if not history_df.empty:
        total_entidad = len(history_df)
        if total_entidad >= 5: # Guard min 5 contratos
            directas = len(history_df[history_df["modalidad_de_contratacion"].str.contains("directa", case=False, na=False)])
            ratio = directas / total_entidad
            if ratio > 0.80:
                puntos = PESO_D2
                desc = f"D2: Entidad usa contratación directa en el {ratio:.1%} de su historial (Umbral 80%)."
                flags_detalle.append({"bandera": "D2", "puntos": puntos, "desc": desc})
                score_total += puntos
                categories.add("D")

    # --- BONUS SISTÉMICO (+10) ---
    if len(categories) >= 3:
        puntos = PESO_BONUS
        desc = "BONUS: Riesgo Sistémico (Alertas en 3 o más categorías)."
        flags_detalle.append({"bandera": "BONUS", "puntos": puntos, "desc": desc})
        score_total += puntos

    # Lista plana de IDs para verificar flags activas (C1, C2) y para retorno
    banderas_ids = [f["bandera"] for f in flags_detalle]

    # --- ACTT: Atenuación por Convenios (Recalibración v1.1) ---
    # ACTT atenúa solo en modalidades de convenio y SI NO hay C1 (Sobrecosto) o C2 (Fraccionamiento)
    es_modalidad_actt = any(m in modalidad for m in MODALIDADES_ACTT)
    flag_c1_activa = "C1" in banderas_ids
    flag_c2_activa = "C2" in banderas_ids

    if es_modalidad_actt and not flag_c1_activa and not flag_c2_activa:
        score_total = int(score_total * 0.5)
        flags_detalle.append({
            "bandera": "ACTT", 
            "puntos": 0, 
            "desc": "Atenuación ACTT (50%): El contrato es un convenio interadministrativo sin riesgos algorítmicos detectados (sin C1 ni C2)."
        })
        # Actualizamos banderas_ids después de aplicar ACTT
        banderas_ids.append("ACTT")

    score_total = min(score_total, 100)
    nivel = "BAJO"
    if score_total >= UMBRAL_NIVEL3: nivel = "CRÍTICO" 
    elif score_total >= UMBRAL_NIVEL2: nivel = "ALTO"
    elif score_total >= UMBRAL_NIVEL1: nivel = "MEDIO"
    
    return {
        "score_total": int(score_total),
        "nivel_riesgo": nivel,
        "banderas": banderas_ids,
        "flags_detalle": flags_detalle,
        "traduccion": get_citizen_translation(banderas_ids)
    }

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🧠 LUPA Scoring Logic v1.2 (Auditor Approved)")
