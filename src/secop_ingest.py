# secop_ingest.py
import requests
import pandas as pd
from datetime import datetime

SECOP_URL = "https://www.datos.gov.co/resource/jbjy-vk9h.json"

FIELD_MAP = {
    "ciudad": "ciudad", "nombre_entidad": "nombre_entidad",
    "documento_proveedor": "nit_proveedor", "proveedor_adjudicado": "nombre_proveedor",
    "valor_del_contrato": "valor_del_contrato", "modalidad_de_contratacion": "modalidad",
    "objeto_del_contrato": "objeto", "fecha_de_firma": "fecha_firma",
    "fecha_de_inicio_del_contrato": "fecha_inicio", "fecha_de_fin_del_contrato": "fecha_fin",
    "tipo_de_contrato": "tipo_contrato", "estado_contrato": "estado",
    "urlproceso": "url_proceso", "descripcion_del_proceso": "descripcion",
    "referencia_del_contrato": "id_contrato", "valor_de_pago_adelantado": "valor_anticipo",
    "dias_adicionados": "dias_adicionados", "justificacion_modalidad_de": "justificacion_modalidad",
    "saldo_cdp": "saldo_cdp", "proceso_de_compra": "proceso_de_compra",
}

def extraer_contratos(limite=5000):
    todos, offset = [], 0
    while True:
        r = requests.get(SECOP_URL, params={
            "$where": "upper(ciudad) LIKE '%MEDELL%'",
            "$limit": limite, "$offset": offset
        }, timeout=30)
        if r.status_code != 200: break
        batch = r.json()
        if not batch: break
        todos.extend(batch)
        print(f"  → {len(todos)} contratos...")
        if len(batch) < limite: break
        offset += limite
    return pd.DataFrame(todos)

def normalizar(df):
    rename = {k: v for k, v in FIELD_MAP.items() if k in df.columns}
    df = df.rename(columns=rename)
    for col in ["valor_del_contrato", "valor_anticipo", "saldo_cdp"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in ["fecha_firma", "fecha_inicio", "fecha_fin"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    if "dias_adicionados" in df.columns:
        df["dias_adicionados"] = pd.to_numeric(df["dias_adicionados"], errors="coerce").fillna(0)
    if "id_contrato" in df.columns:
        df = df.drop_duplicates(subset=["id_contrato"], keep="last")
    df["_lupa_ingested_at"] = datetime.utcnow().isoformat()
    print(f"✅ {len(df)} contratos normalizados")
    return df

if __name__ == "__main__":
    print("🔍 Extrayendo contratos de Medellín...")
    df = normalizar(extraer_contratos())
    df.to_csv("contratos_medellin_raw.csv", index=False)
    print(f"💾 Guardado: contratos_medellin_raw.csv ({len(df)} filas)")