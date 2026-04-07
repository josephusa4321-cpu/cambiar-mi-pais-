import os
import sys
import time
import random
import string
import logging
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("lupa.api")

# Agregar workers al path para importar graph modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
WORKERS_DIR = os.path.join(PROJECT_ROOT, "workers")
if WORKERS_DIR not in sys.path:
    sys.path.insert(0, WORKERS_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

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

# Supabase Client — intenta múltiples nombres de variables
SUPABASE_URL = (
    os.environ.get("SUPABASE_URL")
    or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
)
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_KEY")
    or os.environ.get("SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_ANON_KEY")
    or os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
)

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
        "disclaimer": "Este sistema detecta riesgos estadísticos, no constituye una acusación legal."
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


# ============================================================
# GRAFO DE CONTRATACIÓN PÚBLICA — /api/red
# ============================================================

@app.get("/api/red/topologia")
async def get_red_topologia():
    """
    Retorna el grafo completo para visualización web.
    {nodes: [...], links: [...], stats: {...}}
    """
    if not supabase:
        return {
            "nodes": [],
            "links": [],
            "stats": {
                "nodos_total": 0,
                "entidades": 0,
                "proveedores": 0,
                "aristas": 0,
                "note": "Supabase no configurado. El grafo se mostrará vacío hasta que conectes los datos."
            }
        }
    try:
        from graph_builder import run_graph_pipeline
        resultado = run_graph_pipeline(modo="full")
        return {
            "nodes": resultado["graph_data"]["nodes"],
            "links": resultado["graph_data"]["links"],
            "stats": resultado["stats"]
        }
    except Exception as e:
        logger.error(f"Error en /api/red/topologia: {e}")
        return {
            "nodes": [],
            "links": [],
            "stats": {"error": str(e)},
        }


@app.get("/api/red/brokers")
async def get_red_brokers(min_entidades: int = 3):
    """
    Proveedores conectados a múltiples entidades (intermediarios).
    """
    if not supabase:
        return {"brokers": [], "total": 0, "note": "Supabase no configurado"}
    try:
        from graph_builder import build_graph, fetch_contratos, get_supabase_client
        from graph_metrics import detect_brokers
        s = get_supabase_client()
        df = fetch_contratos(s, modo="full")
        G = build_graph(df)
        brokers = detect_brokers(G, min_entidades=min_entidades)
        return {"brokers": brokers, "total": len(brokers)}
    except Exception as e:
        logger.error(f"Error en /api/red/brokers: {e}")
        return {"brokers": [], "total": 0, "error": str(e)}


@app.get("/api/red/cliques")
async def get_red_cliques(min_size: int = 3):
    """
    Grupos cerrados de proveedores que comparten entidades.
    """
    if not supabase:
        return {"cliques": [], "total": 0, "note": "Supabase no configurado"}
    try:
        from graph_builder import build_graph, fetch_contratos, get_supabase_client
        from graph_metrics import detect_cliques
        s = get_supabase_client()
        df = fetch_contratos(s, modo="full")
        G = build_graph(df)
        cliques = detect_cliques(G, min_size=min_size)
        return {"cliques": cliques, "total": len(cliques)}
    except Exception as e:
        logger.error(f"Error en /api/red/cliques: {e}")
        return {"cliques": [], "total": 0, "error": str(e)}


@app.get("/api/red/criticos")
async def get_red_criticos(top_n: int = 10):
    """
    Nodos críticos (betweenness centrality más alta).
    """
    if not supabase:
        return {"nodos_criticos": [], "note": "Supabase no configurado"}
    try:
        from graph_builder import build_graph, fetch_contratos, get_supabase_client
        from graph_metrics import detect_critical_nodes
        s = get_supabase_client()
        df = fetch_contratos(s, modo="full")
        G = build_graph(df)
        criticos = detect_critical_nodes(G, top_n=top_n)
        return {"nodos_criticos": criticos}
    except Exception as e:
        logger.error(f"Error en /api/red/criticos: {e}")
        return {"nodos_criticos": [], "error": str(e)}


@app.get("/api/red/concentracion")
async def get_red_concentracion():
    """
    Concentración de contratación por entidad.
    """
    if not supabase:
        return {"concentracion": [], "note": "Supabase no configurado"}
    try:
        from graph_builder import build_graph, fetch_contratos, get_supabase_client
        from graph_metrics import detect_concentration
        s = get_supabase_client()
        df = fetch_contratos(s, modo="full")
        G = build_graph(df)
        concentracion = detect_concentration(G)
        return {"concentracion": concentracion}
    except Exception as e:
        logger.error(f"Error en /api/red/concentracion: {e}")
        return {"concentracion": [], "error": str(e)}


@app.get("/api/red/stats")
async def get_red_stats():
    """
    Estadísticas rápidas del grafo (sin construir el grafo completo).
    """
    if not supabase:
        return {
            "total_contratos": 0,
            "entidades_unicas": 0,
            "proveedores_unicos": 0,
            "contratos_alto_riesgo": 0,
            "note": "Supabase no configurado. Agrega NEXT_PUBLIC_SUPABASE_URL y NEXT_PUBLIC_SUPABASE_ANON_KEY al .env"
        }
    try:
        # Conteos directos de Supabase — mucho más rápido
        res_contratos = supabase.table("contratos_raw") \
            .select("id_contrato", count="exact") \
            .execute()

        res_entidades = supabase.table("contratos_raw") \
            .select("nit_entidad") \
            .execute()
        entidades_unicas = len(set(r["nit_entidad"] for r in res_entidades.data if r.get("nit_entidad")))

        res_proveedores = supabase.table("contratos_raw") \
            .select("documento_proveedor") \
            .execute()
        proveedores_unicos = len(set(r["documento_proveedor"] for r in res_proveedores.data if r.get("documento_proveedor")))

        # Scores
        res_alto = supabase.table("contratos_scored") \
            .select("id_contrato", count="exact") \
            .filter("score_total", "gte", 55) \
            .execute()

        return {
            "total_contratos": res_contratos.count if res_contratos.count else 0,
            "entidades_unicas": entidades_unicas,
            "proveedores_unicos": proveedores_unicos,
            "contratos_alto_riesgo": res_alto.count if res_alto.count else 0,
        }
    except Exception as e:
        logger.error(f"Error en /api/red/stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo stats: {str(e)}")
