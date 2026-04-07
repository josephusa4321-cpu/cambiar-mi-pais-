# workers/graph_builder.py
"""
LUPA Graph Builder — Construye el grafo de contratación pública.
Cada contrato es una arista entre Entidad y Proveedor.
Lee de Supabase (contratos_raw) y retorna un NetworkX Graph.
"""

import os
import json
import logging
from datetime import datetime, timezone

import networkx as nx
import pandas as pd
from supabase import create_client, Client

logger = logging.getLogger("lupa.graph_builder")


def get_supabase_client() -> Client:
    """Crea cliente Supabase desde variables de entorno."""
    url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SERVICE_ROLE_KEY")
    if not url or not key:
        raise EnvironmentError("SUPABASE_URL y SUPABASE_SERVICE_KEY deben estar configurados")
    return create_client(url, key)


def fetch_contratos(supabase: Client, modo: str = "delta") -> pd.DataFrame:
    """
    Obtiene contratos de Supabase para construir el grafo.

    modo:
        "delta" → solo contratos desde última ejecución
        "full" → todo el histórico
    """
    logger.info(f"Obteniendo contratos para grafo | Modo: {modo}")

    # Query de contratos con las columnas mínimas necesarias
    query = supabase.table("contratos_raw").select(
        "id_contrato,"
        "nit_entidad,"
        "nombre_entidad,"
        "documento_proveedor,"
        "proveedor_adjudicado,"
        "valor_del_contrato,"
        "modalidad_de_contratacion,"
        "fecha_de_firma,"
        "objeto_del_contrato,"
        "sector"
    )

    if modo == "delta":
        try:
            res_meta = supabase.table("meta_pipeline") \
                .select("ultima_ejecucion_exitosa") \
                .eq("nombre_pipeline", "graph_builder") \
                .execute()
            if res_meta.data:
                ultimo_run = res_meta.data[0].get("ultima_ejecucion_exitosa")
                if ultimo_run:
                    query = query.gt("ultima_actualizacion", ultimo_run)
                    logger.info(f"Delta desde: {ultimo_run}")
        except Exception as e:
            logger.warning(f"No se pudo leer meta_pipeline para delta: {e}")

    try:
        res = query.execute()
        df = pd.DataFrame(res.data)
    except Exception as e:
        logger.error(f"Error obteniendo contratos: {e}")
        return pd.DataFrame()

    if df.empty:
        logger.info("No hay contratos nuevos para el grafo")
        return df

    # Limpiar valores
    df["valor_del_contrato"] = pd.to_numeric(df["valor_del_contrato"], errors="coerce").fillna(0)
    # Bug x100 de SECOP
    mask_bug = df["valor_del_contrato"] > 500_000_000_000
    df.loc[mask_bug, "valor_del_contrato"] = df.loc[mask_bug, "valor_del_contrato"] / 100

    df["nit_entidad"] = df["nit_entidad"].fillna("").astype(str)
    df["documento_proveedor"] = df["documento_proveedor"].fillna("").astype(str)
    df["nombre_entidad"] = df["nombre_entidad"].fillna("").astype(str)
    df["proveedor_adjudicado"] = df["proveedor_adjudicado"].fillna("").astype(str)

    logger.info(f"Contratos obtenidos: {len(df)}")
    return df


def build_graph(df: pd.DataFrame) -> nx.Graph:
    """
    Construye un grafo bipartito Entidad ↔ Proveedor.

    Cada contrato es una arista con metadatos.
    Si el mismo proveedor tiene múltiples contratos con la misma entidad,
    la arista acumula los valores y cuenta los contratos.
    """
    logger.info(f"Construyendo grafo con {len(df)} contratos...")

    G = nx.Graph()
    edges_added = 0

    for _, row in df.iterrows():
        entidad_id = f"ENT:{row['nit_entidad']}" if row['nit_entidad'] else f"ENT:DESCONOCIDO_{row['nombre_entidad']}"
        proveedor_id = f"PROV:{row['documento_proveedor']}" if row['documento_proveedor'] else f"PROV:DESCONOCIDO_{row['proveedor_adjudicado']}"

        # Agregar nodos con metadatos si no existen
        if not G.has_node(entidad_id):
            G.add_node(
                entidad_id,
                type="entidad",
                nombre=row["nombre_entidad"],
                nit=row["nit_entidad"]
            )

        if not G.has_node(proveedor_id):
            G.add_node(
                proveedor_id,
                type="proveedor",
                nombre=row["proveedor_adjudicado"],
                documento=row["documento_proveedor"]
            )

        # Agregar o acumular arista
        if G.has_edge(entidad_id, proveedor_id):
            # Acumular contrato existente
            edge = G[entidad_id][proveedor_id]
            edge["num_contratos"] = edge.get("num_contratos", 1) + 1
            edge["valor_total"] = edge.get("valor_total", 0) + row["valor_del_contrato"]
            edge["contratos_ids"].append(row["id_contrato"])
            # Modalidades usadas
            modalidades = set(edge.get("modalidades", []))
            modalidades.add(row["modalidad_de_contratacion"])
            edge["modalidades"] = list(modalidades)
        else:
            G.add_edge(
                entidad_id,
                proveedor_id,
                num_contratos=1,
                valor_total=row["valor_del_contrato"],
                contratos_ids=[row["id_contrato"]],
                modalidades=[row["modalidad_de_contratacion"]],
                primer_contrato=row.get("fecha_de_firma", ""),
                ultimo_contrato=row.get("fecha_de_firma", ""),
                sector=row.get("sector", "")
            )
            edges_added += 1

    logger.info(f"Grafo construido: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")
    return G


def enrich_with_scores(G: nx.Graph, supabase: Client) -> nx.Graph:
    """
    Enriquece el grafo con scores de riesgo de contratos_scored.
    Agrega atributo 'riesgo_max' a nodos de proveedor.
    """
    logger.info("Enriqueciendo grafo con scores de riesgo...")

    try:
        res = supabase.table("contratos_scored").select(
            "id_contrato, score_total, nivel_riesgo"
        ).execute()

        if not res.data:
            logger.info("No hay scores para enriquecer")
            return G

        # Indexar scores por contrato
        score_map = {r["id_contrato"]: r for r in res.data}

        for node_id, node_data in G.nodes(data=True):
            if node_data.get("type") != "proveedor":
                continue

            # Obtener todos los contratos de este proveedor
            contratos_proveedor = []
            for neighbor in G.neighbors(node_id):
                edge_data = G[node_id][neighbor]
                for cid in edge_data.get("contratos_ids", []):
                    if cid in score_map:
                        contratos_proveedor.append(score_map[cid])

            if contratos_proveedor:
                max_score = max(c["score_total"] for c in contratos_proveedor)
                high_risk_count = sum(1 for c in contratos_proveedor if c["nivel_riesgo"] in ("ALTO", "CRÍTICO"))
                G.nodes[node_id]["riesgo_max"] = max_score
                G.nodes[node_id]["contratos_alto_riesgo"] = high_risk_count
                G.nodes[node_id]["total_contratos_scored"] = len(contratos_proveedor)

    except Exception as e:
        logger.warning(f"No se pudieron cargar scores: {e}")

    return G


def enrich_with_sancionados(G: nx.Graph, sancionados_path: str) -> nx.Graph:
    """
    Marca nodos de proveedores que están en lista de sancionados.
    """
    import os as _os
    if not _os.path.exists(sancionados_path):
        logger.warning(f"Archivo de sancionados no encontrado: {sancionados_path}")
        return G

    try:
        df_san = pd.read_csv(sancionados_path)
        # Asumir columna 'nit' o similar
        nit_col = None
        for col in df_san.columns:
            if "nit" in col.lower():
                nit_col = col
                break

        if not nit_col:
            logger.warning("No se encontró columna NIT en sancionados.csv")
            return G

        sancionados_nits = set(df_san[nit_col].fillna("").astype(str).str.replace(".", "").str.replace("-", ""))

        marcados = 0
        for node_id, node_data in G.nodes(data=True):
            if node_data.get("type") != "proveedor":
                continue
            nit_prov = str(node_data.get("documento", "")).replace(".", "").replace("-", "")
            if nit_prov and nit_prov in sancionados_nits:
                G.nodes[node_id]["sancionado"] = True
                marcados += 1

        if marcados > 0:
            logger.info(f"🔴 {marcados} proveedores marcados como sancionados")
        else:
            logger.info("No se encontraron proveedores sancionados en el grafo actual")

    except Exception as e:
        logger.warning(f"Error procesando sancionados: {e}")

    return G


def export_graph_for_web(G: nx.Graph) -> dict:
    """
    Exporta el grafo en formato JSON para react-force-graph.
    Retorna dict con 'nodes' y 'links'.
    """
    nodes = []
    node_id_map = {}  # original_id → index

    for idx, (node_id, data) in enumerate(G.nodes(data=True)):
        node_id_map[node_id] = idx
        nodes.append({
            "id": node_id,
            "label": data.get("nombre", node_id),
            "type": data.get("type", "unknown"),
            "nit": data.get("nit", data.get("documento", "")),
            "riesgo_max": data.get("riesgo_max", 0),
            "sancionado": data.get("sancionado", False),
            "val": data.get("contratos_alto_riesgo", 0) + 1,  # Tamaño del nodo
            **{k: v for k, v in data.items() if k not in ("nombre", "nit", "documento", "type", "sancionado")}
        })

    links = []
    for u, v, data in G.edges(data=True):
        links.append({
            "source": node_id_map[u],
            "target": node_id_map[v],
            "num_contratos": data.get("num_contratos", 1),
            "valor_total": data.get("valor_total", 0),
            "width": min(data.get("num_contratos", 1), 10),  # Grosor visual
            "contratos_ids": data.get("contratos_ids", []),
        })

    return {"nodes": nodes, "links": links}


def run_graph_pipeline(modo: str = "full") -> dict:
    """
    Pipeline completo: fetch → build → enrich → export.

    Retorna dict con:
        - graph_data: {nodes, links} para frontend
        - stats: métricas del grafo
        - execution_time: segundos
    """
    import time
    start = time.time()

    supabase = get_supabase_client()

    # 1. Fetch
    df = fetch_contratos(supabase, modo=modo)
    if df.empty:
        return {"graph_data": {"nodes": [], "links": []}, "stats": {"error": "no data"}, "execution_time": 0}

    # 2. Build
    G = build_graph(df)

    # 3. Enrich con scores
    G = enrich_with_scores(G, supabase)

    # 4. Enrich con sancionados
    sancionados_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "sancionados.csv"
    )
    G = enrich_with_sancionados(G, sancionados_path)

    # 5. Calcular métricas básicas
    try:
        from workers.graph_metrics import compute_graph_metrics
    except ImportError:
        from graph_metrics import compute_graph_metrics
    stats = compute_graph_metrics(G)
    stats["contratos_procesados"] = len(df)

    # 6. Exportar para web
    graph_data = export_graph_for_web(G)

    # 7. Actualizar meta_pipeline
    elapsed = round(time.time() - start, 2)
    try:
        supabase.table("meta_pipeline").upsert({
            "nombre_pipeline": "graph_builder",
            "ultima_ejecucion_exitosa": datetime.now(timezone.utc).isoformat(),
            "registros_procesados": len(df),
            "estado": "OK",
            "metricas_json": json.dumps(stats, default=str)
        }, on_conflict="nombre_pipeline").execute()
    except Exception as e:
        logger.warning(f"No se pudo actualizar meta_pipeline: {e}")

    stats["execution_time"] = elapsed
    logger.info(f"✅ Graph pipeline completado en {elapsed}s")

    return {
        "graph_data": graph_data,
        "stats": stats,
        "execution_time": elapsed
    }


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    modo = sys.argv[1] if len(sys.argv) > 1 else "full"
    resultado = run_graph_pipeline(modo=modo)
    print(json.dumps(resultado["stats"], indent=2, default=str))
    print(f"\n📊 Nodos: {len(resultado['graph_data']['nodes'])}")
    print(f"🔗 Aristas: {len(resultado['graph_data']['links'])}")
