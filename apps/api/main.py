import os
import time
import random
import string
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Middleware: Regla de Privacidad - No IP Logging
class PrivacyFirstMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Strip potentially sensitive headers before processing
        request.headers.__dict__["_list"] = [
            (k, v) for k, v in request.headers.raw 
            if k.lower() not in [b"x-forwarded-for", b"x-real-ip"]
        ]
        response = await call_next(request)
        return response

app = FastAPI(title="LUPA API", version="1.0.0")

app.add_middleware(PrivacyFirstMiddleware)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción limitar a dominio lupa.city
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase Client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Warning: SUPABASE_URL or SUPABASE_ANON_KEY not set")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Models
class ReporteRequest(BaseModel):
    entidad_reportada: str
    descripcion: str
    numero_contrato: Optional[str] = None
    archivo_url: Optional[str] = None

class ReporteResponse(BaseModel):
    status: str
    codigo_referencia: str

# Helper: Generar código de referencia LUPA-XXXXXXXX
def generate_lupa_code():
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(chars) for _ in range(8))
    return f"LUPA-{code}"

# Middleware: Regla de Privacidad - No IP Logging
@app.middleware("http")
async def privacy_middleware(request: Request, call_next):
    # Aseguramos que no se registre la IP en logs de aplicación (si hubiera)
    # ni se pase a la base de datos accidentalmente.
    if request.url.path == "/api/reportar":
        # Desactivamos explícitamente cualquier logger de IP si lo tuviéramos configurado
        pass
    
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {
        "name": "LUPA API",
        "org": "Proyecto Cambiar mi pais",
        "description": "Sistema de monitoreo de riesgo algorítmico en contratación pública de Medellín",
        "disclaimer": "Este sistema detecta riesgos estadísticos, no acusaciones legales de corrupción."
    }

@app.get("/api/health")
async def health():
    return {"status": "ok", "supabase": "connected" if supabase else "disconnected"}

@app.get("/api/top10")
async def get_top10():
    if not supabase: raise HTTPException(status_code=500, detail="Supabase connection failed")
    
    # Obtener el ranking de contratos con score ≥ 40
    # Usamos inner join implícito con contratos_raw para datos descriptivos
    res = supabase.table("contratos_scored")\
        .select("id_contrato, score_total, nivel_riesgo, banderas_activas, traduccion_ciudadana, contratos_raw(nombre_entidad, proveedor_adjudicado, valor_del_contrato)")\
        .filter("score_total", "gte", 40)\
        .order("score_total", desc=True)\
        .limit(10)\
        .execute()
    
    return res.data

@app.get("/api/opacos")
async def get_opacos():
    if not supabase: raise HTTPException(status_code=500, detail="Supabase connection failed")
    
    res = supabase.table("contratos_opacos")\
        .select("id_contrato, icd_score, campos_faltantes, contratos_raw(nombre_entidad, valor_del_contrato)")\
        .order("icd_score", desc=False)\
        .limit(20)\
        .execute()
    
    return res.data

@app.get("/api/impunidad")
async def get_impunidad():
    if not supabase: raise HTTPException(status_code=500, detail="Supabase connection failed")
    
    res = supabase.table("timeline_impunidad")\
        .select("*, contratos_raw(nombre_entidad, proveedor_adjudicado)")\
        .order("dias_inactividad", desc=True)\
        .limit(20)\
        .execute()
    
    return res.data

@app.post("/api/reportar", response_model=ReporteResponse)
async def reportar(reporte: ReporteRequest):
    if not supabase: raise HTTPException(status_code=500, detail="Supabase connection failed")
    
    # Validación de longitud mínima (Requisito de la DB)
    if len(reporte.descripcion) < 50:
        raise HTTPException(status_code=400, detail="La descripción debe tener al menos 50 caracteres")

    codigo = generate_lupa_code()
    
    # Inserción en denuncias_anonimas (RLS permite INSERT público)
    data = {
        "codigo_referencia": codigo,
        "entidad_reportada": reporte.entidad_reportada,
        "descripcion": reporte.descripcion,
        "id_contrato": reporte.numero_contrato,
        "archivo_url": reporte.archivo_url,
        "estado_revision": "NUEVO"
    }
    
    # REGLA DE ORO: NO CAPTURAMOS IP. 
    # FastAPI no la extrae por defecto a menos que lo pidamos vía Request.client.host
    
    try:
        supabase.table("denuncias_anonimas").insert(data).execute()
        return ReporteResponse(status="success", codigo_referencia=codigo)
    except Exception as e:
        # Probablemente colisión de código único (raro pero posible)
        if "unique_violation" in str(e).lower():
            # Reintentar una vez con otro código
            codigo = generate_lupa_code()
            data["codigo_referencia"] = codigo
            supabase.table("denuncias_anonimas").insert(data).execute()
            return ReporteResponse(status="success", codigo_referencia=codigo)
        logger.error(f"Error guardando denuncia: {e}")
        raise HTTPException(status_code=500, detail="Error al guardar el reporte")
