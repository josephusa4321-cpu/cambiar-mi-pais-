import os
import logging
import json
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lupa.scoring")

# Config
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# 10 Indicators Weight Map (A1-D2)
WEIGHTS = {
    "A1": 20, # Unico Oferente
    "A2": 15, # Velocidad (Apertura-Cierre < 48h)
    "B1": 15, # Adición > 45%
    "B3": 10, # Iterativo (Directa recurrente)
    "C1": 30, # Sancionado
    "C3": 5,  # Objeto Vago
    "D1": 10, # Precio Inusual (vs Promedio Sector) - Mocked logic
    "D2": 5,  # Sector de Alto Riesgo (Logística/Eventos)
}

# ICD Mandatory Fields (12)
ICD_FIELDS = [
    "nombre_entidad", "nit_entidad", "modalidad_de_contratacion", 
    "justificacion_modalidad_de", "valor_del_contrato", "documento_proveedor", 
    "proveedor_adjudicado", "fecha_de_firma", "numero_de_oferentes",
    "precio_base", "fecha_de_publicacion_del_proceso", "descripcion_del_proceso"
]

def normalize_valor(valor):
    """Bug de centavos: Truncar a entero para evitar inconsistencias en comparaciones."""
    try:
        return int(float(valor))
    except (TypeError, ValueError):
        return 0

def calculate_icd(contrato: dict):
    faltantes = [f for f in ICD_FIELDS if not contrato.get(f)]
    # Normalize valor field specifically
    if contrato.get("valor_del_contrato"):
        contrato["valor_del_contrato"] = normalize_valor(contrato["valor_del_contrato"])
    
    score = int(((len(ICD_FIELDS) - len(faltantes)) / len(ICD_FIELDS)) * 100)
    return score, faltantes

def get_citizen_translation(banderas: list):
    if not banderas: return "No se detectaron riesgos significativos en los datos analizados."
    
    translations = []
    if "A1" in banderas: translations.append("Este contrato se entregó con un único competidor, limitando la transparencia.")
    if "A2" in banderas: translations.append("El proceso se abrió y cerró tan rápido que parece estar dirigido.")
    if "B1" in banderas: translations.append("Se adicionó casi el 50% del valor inicial, lo cual es una alerta de planeación pobre o sobrecosto.")
    if "C1" in banderas: translations.append("El proveedor tiene antecedentes de sanciones en otros entes de control.")
    if "C3" in banderas: translations.append("La descripción es tan vaga que no es posible saber qué se está comprando exactamente.")
    if "B3" in banderas: translations.append("Este contratista es recurrente en contratos de alto riesgo, lo que indica un posible patrón sistémico.")
    if "D1" in banderas: translations.append("El valor de este contrato supera el promedio histórico aceptado para este tipo de bienes o servicios.")
    if "D2" in banderas: translations.append("Este sector (Eventos/Logística) es históricamente propenso a riesgos algorítmicos altos.")
    
    return " ".join(translations[:2]) # Max 2 or joined

def calculate_score(contrato: dict):
    banderas = []
    score_total = 0
    categories = set()
    doc_id = contrato.get("documento_proveedor")

    # B3: Recurrencia Automática (Network Graph Basic)
    if doc_id and supabase:
        try:
            # Query if this provider has other HIGH risk contracts (Score > 40)
            res = supabase.table("contratos_scored").select("id_contrato", count="exact").eq("documento_proveedor", doc_id).execute()
            if res.count and res.count >= 2:
                banderas.append("B3")
                score_total += WEIGHTS["B3"]
                categories.add("B")
                logger.info(f"B3 Detectado: El contratista {doc_id} ya tiene {res.count} alertas previas.")
        except Exception as e:
            logger.error(f"Error checking B3 recurrence: {e}")

    # A1: Unico Oferente
    if contrato.get("numero_de_oferentes", 0) == 1:
        banderas.append("A1")
        score_total += WEIGHTS["A1"]
        categories.add("A")

    # A2: Velocidad < 48h
    if contrato.get("fecha_de_publicacion_del_proceso") and contrato.get("fecha_de_recepcion_de_ofertas"):
        try:
            pub = datetime.fromisoformat(contrato["fecha_de_publicacion_del_proceso"])
            rec = datetime.fromisoformat(contrato["fecha_de_recepcion_de_ofertas"])
            if (rec - pub).total_seconds() < 172800: # 48 hours
                banderas.append("A2")
                score_total += WEIGHTS["A2"]
                categories.add("A")
        except: pass

    # B1: Adición > 45% (Calculado si existe dato de adición)
    # Mocked simplified check: Si el valor actual es > 1.45 * valor base (si tuviéramos histórico)
    # Por ahora solo activamos si el flag de adición masiva está presente
    
    # C1: Sancionado (Cruce con lista externa)
    # dummy_sancionados = ["800123456", "900555666"]
    # if contrato.get("documento_proveedor") in dummy_sancionados:
    #    banderas.append("C1")
    #    score_total += WEIGHTS["C1"]
    #    categories.add("C")

    # C3: Objeto Vago
    desc = contrato.get("descripcion_del_proceso", "")
    if desc and len(desc.split()) < 8:
        banderas.append("C3")
        score_total += WEIGHTS["C3"]
        categories.add("C")

    # D1: Precio Inusual (Backend simple threshold by sector)
    sector = contrato.get("sector", "").upper()
    total = normalize_valor(contrato.get("valor_del_contrato", 0))
    if sector == "SALUD" and total > 500000000: # Example logic for demo
        banderas.append("D1")
        score_total += WEIGHTS["D1"]
        categories.add("D")

    # D2: Sector de Alto Riesgo (Logística/Eventos/Educación)
    if any(s in sector for s in ["LOGÍSTICA", "EVENTOS", "ALIMENTOS", "RECREACIÓN"]):
        banderas.append("D2")
        score_total += WEIGHTS["D2"]
        categories.add("D")

    # Bonus Sistémico (+10 si ≥3 banderas de categorías diferentes)
    if len(categories) >= 3:
        score_total += 10
        banderas.append("BONUS-SISTEMICO")

    # Cap at 100
    score_total = min(score_total, 100)
    
    nivel = "BAJO"
    if score_total >= 70: nivel = "CRÍTICO"
    elif score_total >= 55: nivel = "ALTO"
    elif score_total >= 40: nivel = "MEDIO"

    return score_total, nivel, banderas

def process_scoring():
    if not supabase: return
    
    logger.info("Iniciando ciclo de Scoring...")
    
    # Obtener contratos pendientes (en contratos_raw pero no en scored/opacos)
    # O actualizados recientemente
    res = supabase.table("contratos_raw").select("*").limit(100).execute()
    
    for contrato in res.data:
        id_c = contrato["id_contrato"]
        
        # 1. ICD Check
        icd_score, faltantes = calculate_icd(contrato)
        
        if icd_score < 40:
            # Move to opacos
            supabase.table("contratos_opacos").upsert({
                "id_contrato": id_c,
                "icd_score": icd_score,
                "campos_faltantes": faltantes
            }).execute()
            # Eliminar de scored si existía
            supabase.table("contratos_scored").delete().eq("id_contrato", id_c).execute()
            logger.info(f"Contrato {id_c} clasificado como OPACO (ICD: {icd_score})")
            continue

        # 2. Risk Calculation
        score, nivel, banderas = calculate_score(contrato)
        traduccion = get_citizen_translation(banderas)
        
        # 3. Upsert into scored
        scored_data = {
            "id_contrato": id_c,
            "documento_proveedor": contrato.get("documento_proveedor"),
            "score_total": score,
            "nivel_riesgo": nivel,
            "banderas_activas": banderas,
            "traduccion_ciudadana": traduccion,
            "publicado_telegram": False
        }
        
        supabase.table("contratos_scored").upsert(scored_data).execute()
        
        # 4. Timeline de Impunidad (Nivel 2: Score >= 55)
        if score >= 55:
            supabase.table("timeline_impunidad").upsert({
                "id_contrato": id_c,
                "estado_respuesta": "PENDIENTE"
            }, on_conflict="id_contrato").execute()
            
        logger.info(f"Contrato {id_c} procesado. Score: {score}, Nivel: {nivel}")

if __name__ == "__main__":
    process_scoring()
