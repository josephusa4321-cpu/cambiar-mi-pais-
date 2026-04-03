import os
import asyncio
import logging
import httpx
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lupa.telegram_resumen")

# Config
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN") # Note: using TELEGRAM_TOKEN as per workflow
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHAT_ID", "@LupaMedellin")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def escape_markdown(text: str) -> str:
    if not text: return ""
    special_chars = r'_*[]()~`>#+-=|{}.!'
    for char in special_chars:
        text = str(text).replace(char, f"\\{char}")
    return text

def format_price(value: float) -> str:
    if value >= 1_000_000_000: return f"${value/1e9:.1f}B"
    if value >= 1_000_000: return f"${value/1e6:.0f}M"
    return f"${value:,.0f}"

async def send_telegram_summary(text: str):
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_TOKEN no configurado.")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }
    
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(url, json=payload, timeout=20)
            res.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error enviando resumen a Telegram: {e}")
            return False

async def generate_daily_summary():
    if not supabase: return
    
    logger.info("Generando resumen diario para Telegram...")
    
    # 1. Obtener estadísticas del día
    # Contratos analizados hoy
    res_total = supabase.table("contratos_scored").select("id_contrato", count="exact").execute()
    total_analizados = res_total.count if res_total.count else 0
    
    # Riesgos Críticos
    res_criticos = supabase.table("contratos_scored").select("id_contrato", count="exact").eq("nivel_riesgo", "CRÍTICO").execute()
    total_criticos = res_criticos.count if res_criticos.count else 0
    
    # 2. Obtener Top 3 Sospechosos Nuevos (No publicados)
    res_top = supabase.table("contratos_scored")\
        .select("score_total, nivel_riesgo, traduccion_ciudadana, contratos_raw(nombre_entidad, proveedor_adjudicado, valor_del_contrato)")\
        .order("score_total", desc=True)\
        .limit(3)\
        .execute()
    
    # Formatear Mensaje
    fecha = datetime.now().strftime("%d/%m/%Y")
    
    emoji_header = "🐺"
    msg = f"{emoji_header} *LUPA MEDELLÍN — RESUMEN MATUTINO*\n"
    msg += f"📅 *Fecha:* {escape_markdown(fecha)}\n\n"
    
    msg += f"📈 *Contratos Auditados:* {total_analizados}\n"
    msg += f"🚨 *Alertas Críticas:* {total_criticos}\n\n"
    
    if res_top.data:
        msg += f"🔍 *TOP 3 SOSPECHOSOS DEL DÍA:*\n"
        for i, item in enumerate(res_top.data):
            score = item["score_total"]
            raw = item["contratos_raw"]
            entidad = escape_markdown(raw["nombre_entidad"][:30] + "...")
            valor = escape_markdown(format_price(raw["valor_del_contrato"]))
            razon = escape_markdown(item["traduccion_ciudadana"])
            
            msg += f"{i+1}\\. *{entidad}* — {valor}\n"
            msg += f"    🚩 Score: {score} | _{razon}_\n\n"
    
    msg += f"🔗 [Ver todas las auditorías](https://lupa-medellin.vercel.app/)\n"
    msg += f"⚠️ _Análisis de riesgo algorítmico automatizado\\._"

    # Enviar
    success = await send_telegram_summary(msg)
    if success:
        logger.info("Resumen diario enviado exitosamente.")
    else:
        logger.error("Fallo al enviar resumen diario.")

if __name__ == "__main__":
    asyncio.run(generate_daily_summary())
