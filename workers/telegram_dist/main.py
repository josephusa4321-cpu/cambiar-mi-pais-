import os
import time
import logging
import asyncio
import httpx
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lupa.telegram")

# Config
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") # Necesitamos Service Key para escribir
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("TELEGRAM_CHANNEL_ID", "@LupaMedellin")

if not SUPABASE_URL or not SUPABASE_KEY or not TELEGRAM_BOT_TOKEN:
    logger.error("Missing configuration: SUPABASE_URL, SUPABASE_SERVICE_KEY, or TELEGRAM_BOT_TOKEN")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

async def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": "MarkdownV2" # Usamos MarkdownV2 para mejor formato
    }
    
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(url, json=payload, timeout=20)
            res.raise_for_status()
            logger.info(f"Mensaje enviado a {TELEGRAM_CHANNEL_ID}")
            return True
        except Exception as e:
            logger.error(f"Error enviando a Telegram: {e}")
            if res := getattr(e, 'response', None):
                logger.error(f"Respuesta de Telegram: {res.text}")
            return False

def escape_markdown(text: str) -> str:
    """Escapa caracteres especiales para MarkdownV2 de Telegram"""
    if not text: return ""
    special_chars = r'_*[]()~`>#+-=|{}.!'
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text

def format_price(value: float) -> str:
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.1f} mil millones"
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f} millones"
    return f"{value:,.0f}"

async def process_distribution():
    if not supabase: return

    logger.info("Iniciando ciclo de distribución Telegram...")
    
    # 1. Obtener contratos elegibles (score_total >= 55 y no publicados)
    res = supabase.table("contratos_scored")\
        .select("id_contrato, score_total, nivel_riesgo, banderas_activas, traduccion_ciudadana, contratos_raw(nombre_entidad, proveedor_adjudicado, valor_del_contrato)")\
        .filter("score_total", "gte", 55)\
        .filter("publicado_telegram", "eq", False)\
        .order("score_total", desc=True)\
        .limit(10)\
        .execute()
    
    if not res.data:
        logger.info("No hay nuevos contratos de alto riesgo para publicar.")
        return

    logger.info(f"Procesando {len(res.data)} alertas SOS...")

    for item in res.data:
        id_contrato = item["id_contrato"]
        entidad = item["contratos_raw"]["nombre_entidad"]
        proveedor = item["contratos_raw"]["proveedor_adjudicado"]
        valor = item["contratos_raw"]["valor_del_contrato"]
        score = item["score_total"]
        nivel = item["nivel_riesgo"]
        traduccion = item["traduccion_ciudadana"]
        banderas = item["banderas_activas"]
        
        # Emoji por nivel
        emoji = "🔴" if nivel == "CRÍTICO" else "🟠" if nivel == "ALTO" else "🟡"
        
        # Formatear Mensaje
        # Nota: Telegram MarkdownV2 es quisquilloso, escapamos todo.
        msg = f"""{emoji} *ALERTA LUPA — RIESGO {nivel}*

📊 *Score:* {score}/100
🏛️ *Entidad:* {escape_markdown(entidad)}
🏢 *Proveedor:* {escape_markdown(proveedor)}
💰 *Valor:* {escape_markdown(format_price(valor))} COP

🚩 *Banderas:* {escape_markdown(', '.join(banderas))}

💡 *En lenguaje ciudadano:*
_{escape_markdown(traduccion)}_

👉 [Ver auditoría completa](https://lupa.city/contrato/{id_contrato})

⚠️ _Análisis algorítmico basado en datos públicos del SECOP II. No es una acusación legal._"""

        # Enviar
        success = await send_telegram_message(msg)
        
        if success:
            # 3. Marcar como publicado
            supabase.table("contratos_scored")\
                .update({"publicado_telegram": True})\
                .eq("id_contrato", id_contrato)\
                .execute()
            logger.info(f"Contrato {id_contrato} marcado como publicado.")
            
            # Rate limit para no saturar el canal (2 seg entre mensajes)
            await asyncio.sleep(2)
        else:
            logger.error(f"Fallo al distribuir contrato {id_contrato}. Se reintentará en el próximo ciclo.")

async def main():
    while True:
        try:
            await process_distribution()
        except Exception as e:
            logger.error(f"Error inesperado en el worker: {e}")
        
        # Esperar 1 hora entre revisiones (o configurar vía cron externo)
        logger.info("Ciclo terminado. Esperando 60 minutos...")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
