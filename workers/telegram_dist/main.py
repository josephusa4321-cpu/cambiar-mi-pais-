import os
import asyncio
import logging
import httpx
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import html

load_dotenv()

# Logging Config
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lupa.telegram_dist")

# Config de Entorno
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SERVICE_ROLE_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHAT_ID", "@LupaMedellin")

# Umbral de Auditoría - Sprint 3
UMBRAL_ALERTA_SCORE = 55

DRY_RUN = os.environ.get("LUPA_DRY_RUN", "false").lower() == "true"

def init_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY: return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def escape_html(text: str) -> str:
    return html.escape(str(text or "N/A"))

def format_currency(value: float) -> str:
    try:
        return f"${float(value):,.0f}"
    except (ValueError, TypeError):
        return "$0"

async def send_telegram_msg(text: str):
    if not TELEGRAM_BOT_TOKEN and not DRY_RUN:
        logger.error("❌ TELEGRAM_TOKEN no configurado.")
        return False
    
    if DRY_RUN:
        logger.info(f"🚧 [DRY RUN] Mensaje que se enviaría:\n{text}")
        return True
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(url, json=payload, timeout=20)
            res.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"❌ Error en Telegram API: {e}")
            return False

async def generate_alerts():
    supabase = init_supabase()
    if not supabase: return
    
    logger.info("🕵️ Corriendo Auditoría de Alertas para Telegram...")
    
    # 1. Filtro estricto: Score >= 55. Nomenclatura normalizada: flags_detectadas
    res = supabase.table("contratos_scored")\
        .select("score_total, nivel_riesgo, traduccion_ciudadana, flags_detectadas, id_contrato, contratos_raw(nombre_entidad, objeto_del_contrato, valor_del_contrato)")\
        .gte("score_total", UMBRAL_ALERTA_SCORE)\
        .order("score_total", desc=True)\
        .limit(5)\
        .execute()
    
    if not res.data:
        logger.info("✅ No se detectaron riesgos críticos en esta ventana.")
        return

    for item in res.data:
        score = item["score_total"]
        nivel = item["nivel_riesgo"]
        razon = item["traduccion_ciudadana"]
        raw = item["contratos_raw"]
        
        ent_name = escape_html(raw.get("nombre_entidad", "Entidad Desconocida"))
        obj_name = escape_html(raw.get("objeto_del_contrato", "Objeto no especificado"))[:100] + "..."
        valor    = format_currency(raw.get("valor_del_contrato", 0))
        id_c = item.get("id_contrato", "N/A")
        # Generar link de búsqueda en SECOP II por ID de contrato
        url = f"https://community.secop.gov.co/Public/Tendering/OpportunityDetail/Index?noticeAnalyzerCode={id_c}"

        # Template Auditoría Sprint 3
        msg =  f"🔍 <b>ALERTA DE RIESGO ESTADÍSTICO</b>\n"
        msg += f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += f"🏢 <b>Entidad:</b> {ent_name}\n"
        msg += f"📝 <b>Objeto:</b> <i>{obj_name}</i>\n"
        msg += f"💰 <b>Valor:</b> <code>{valor} COP</code>\n"
        msg += f"📊 <b>Base Score:</b> <b>{score}/100 — {nivel}</b>\n\n"
        
        msg += f"📋 <b>Indicadores detectados:</b>\n"
        msg += f"<i>{escape_html(razon)}</i>\n\n"
        
        msg += f"🔗 <a href='{url}'>Ver en SECOP II (Fuente)</a>\n\n"
        
        # MANDATORY LEGAL DISCLAIMER - L6 Anti-SLAPP
        msg += f"⚖️ <b>AVISO LEGAL:</b> <i>Este análisis es algorítmico y basado en datos públicos del SECOP II. No representa una acusación legal ni tiene sesgo político.</i>\n"
        msg += f"📌 Metodología: <a href='https://lupa.city/metodología'>lupa.city/metodología</a>"

        await send_telegram_msg(msg)
        logger.info(f"📤 Alerta enviada: {ent_name}")

if __name__ == "__main__":
    asyncio.run(generate_alerts())
