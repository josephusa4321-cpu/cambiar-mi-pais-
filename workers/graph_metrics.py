# workers/graph_metrics.py
"""
LUPA Graph Metrics — Detecta patrones sospechosos en el grafo.
Clique cerradas, brokers, nodos críticos, concentración.
"""

import logging
import networkx as nx
from collections import Counter

logger = logging.getLogger("lupa.graph_metrics")


def detect_brokers(G: nx.Graph, min_entidades: int = 3) -> list[dict]:
    """
    Brokers: proveedores conectados a muchas entidades distintas.
    Son intermediarios potenciales o empresas con acceso privilegiado.
    """
    brokers = []
    for node_id, data in G.nodes(data=True):
        if data.get("type") != "proveedor":
            continue
        vecinos = list(G.neighbors(node_id))
        entidades = [v for v in vecinos if G.nodes[v].get("type") == "entidad"]
        if len(entidades) >= min_entidades:
            # Calcular valor total de contratos
            valor_total = 0
            num_contratos = 0
            for ent in entidades:
                if G.has_edge(ent, node_id):
                    valor_total += G[ent][node_id].get("valor_total", 0)
                    num_contratos += G[ent][node_id].get("num_contratos", 0)

            brokers.append({
                "node_id": node_id,
                "nombre": data.get("nombre", "Desconocido"),
                "documento": data.get("documento", ""),
                "num_entidades": len(entidades),
                "entidades": [G.nodes[e].get("nombre", e) for e in entidades],
                "num_contratos": num_contratos,
                "valor_total": round(valor_total, 2),
                "riesgo_max": data.get("riesgo_max", 0),
                "sancionado": data.get("sancionado", False)
            })

    brokers.sort(key=lambda x: x["num_entidades"], reverse=True)
    logger.info(f"Brokers detectados: {len(brokers)} (conectados a {min_entidades}+ entidades)")
    return brokers


def detect_cliques(G: nx.Graph, min_size: int = 3) -> list[dict]:
    """
    Cliques cerrados: grupos de proveedores que comparten las mismas entidades.
    Patrón: 5 proveedores que se reparten el 80% de contratos de una entidad.

    Buscamos cliques en el grafo de proyección de proveedores.
    """
    # Proyección: grafo donde nodos son proveedores y se conectan si
    # comparten al menos una entidad
    proveedores = [n for n, d in G.nodes(data=True) if d.get("type") == "proveedor"]
    H = nx.Graph()
    H.add_nodes_from(proveedores)

    for entidad in [n for n, d in G.nodes(data=True) if d.get("type") == "entidad"]:
        provs_conectados = [v for v in G.neighbors(entidad) if v in proveedores]
        # Conectar todos los proveedores de esta entidad entre sí
        for i in range(len(provs_conectados)):
            for j in range(i + 1, len(provs_conectados)):
                p1, p2 = provs_conectados[i], provs_conectados[j]
                if H.has_edge(p1, p2):
                    H[p1][p2]["entidades_compartidas"].add(entidad)
                else:
                    H.add_edge(p1, p2, entidades_compartidas={entidad})

    # Detectar cliques
    cliques = list(nx.find_cliques(H))
    cliques_grandes = [c for c in cliques if len(c) >= min_size]

    results = []
    for clique in cliques_grandes:
        # Obtener entidades compartidas por todos los miembros del clique
        edge_data = []
        for i in range(len(clique)):
            for j in range(i + 1, len(clique)):
                if H.has_edge(clique[i], clique[j]):
                    edge_data.append(H[clique[i]][clique[j]])

        entidades_compartidas = set()
        for ed in edge_data:
            entidades_compartidas.update(ed.get("entidades_compartidas", set()))

        # Calcular valor total del grupo
        valor_total = 0
        num_contratos = 0
        for prov in clique:
            for ent in G.neighbors(prov):
                if ent in entidades_compartidas and G.has_edge(ent, prov):
                    valor_total += G[ent][prov].get("valor_total", 0)
                    num_contratos += G[ent][prov].get("num_contratos", 0)

        results.append({
            "proveedores": [
                {
                    "node_id": p,
                    "nombre": G.nodes[p].get("nombre", "Desconocido"),
                    "documento": G.nodes[p].get("documento", "")
                }
                for p in clique
            ],
            "num_proveedores": len(clique),
            "entidades_afectadas": [
                G.nodes[e].get("nombre", e) for e in entidades_compartidas
            ],
            "num_entidades": len(entidades_compartidas),
            "num_contratos": num_contratos,
            "valor_total": round(valor_total, 2),
        })

    results.sort(key=lambda x: x["valor_total"], reverse=True)
    logger.info(f"Cliques detectados: {len(results)} (tamaño mínimo {min_size})")
    return results


def detect_critical_nodes(G: nx.Graph, top_n: int = 10) -> list[dict]:
    """
    Nodos críticos cuya eliminación desconectaría la red.
    Usamos betweenness centrality — nodos que son "puente" entre componentes.
    """
    if G.number_of_edges() == 0:
        return []

    betweenness = nx.betweenness_centrality(G, weight="num_contratos")

    # Ordenar por betweenness
    sorted_nodes = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:top_n]

    results = []
    for node_id, score in sorted_nodes:
        data = G.nodes[node_id]
        results.append({
            "node_id": node_id,
            "nombre": data.get("nombre", "Desconocido"),
            "type": data.get("type", "unknown"),
            "betweenness": round(score, 6),
            "grado": G.degree(node_id),
            "documento": data.get("documento", data.get("nit", ""))
        })

    logger.info(f"Nodos críticos detectados: top {len(results)} por betweenness centrality")
    return results


def detect_concentration(G: nx.Graph) -> list[dict]:
    """
    Para cada entidad, detecta si un proveedor domina >30% del presupuesto.
    Similar a flag B3 pero a nivel de grafo completo.
    """
    results = []

    entidades = [n for n, d in G.nodes(data=True) if d.get("type") == "entidad"]

    for entidad_id in entidades:
        # Valor total de la entidad
        valor_total_entidad = 0
        proveedores = []

        for prov in G.neighbors(entidad_id):
            if G.has_edge(entidad_id, prov):
                edge_val = G[entidad_id][prov].get("valor_total", 0)
                num_contratos = G[entidad_id][prov].get("num_contratos", 0)
                valor_total_entidad += edge_val
                proveedores.append({
                    "node_id": prov,
                    "nombre": G.nodes[prov].get("nombre", "Desconocido"),
                    "documento": G.nodes[prov].get("documento", ""),
                    "valor": round(edge_val, 2),
                    "num_contratos": num_contratos,
                })

        if valor_total_entidad == 0 or not proveedores:
            continue

        # Calcular concentración
        proveedores.sort(key=lambda x: x["valor"], reverse=True)

        top_3_valor = sum(p["valor"] for p in proveedores[:3])
        top_3_pct = top_3_valor / valor_total_entidad

        top_1 = proveedores[0]
        top_1_pct = top_1["valor"] / valor_total_entidad

        results.append({
            "entidad_id": entidad_id,
            "entidad_nombre": G.nodes[entidad_id].get("nombre", "Desconocida"),
            "valor_total": round(valor_total_entidad, 2),
            "num_proveedores": len(proveedores),
            "top_1_proveedor": top_1,
            "top_1_concentracion": round(top_1_pct, 3),
            "top_3_concentracion": round(top_3_pct, 3),
            "concentrado": top_1_pct > 0.30,  # Umbral B3
        })

    # Ordenar por concentración del top 1
    results.sort(key=lambda x: x["top_1_concentracion"], reverse=True)
    logger.info(f"Concentración calculada para {len(results)} entidades")
    return results


def compute_temporal_metrics(G: nx.Graph) -> dict:
    """
    Métricas temporales del grafo.
    Antigüedad de conexiones, frecuencia de interacción.
    """
    fechas = []
    for u, v, data in G.edges(data=True):
        primer = data.get("primer_contrato")
        ultimo = data.get("ultimo_contrato")
        if primer:
            fechas.append(primer)
        if ultimo:
            fechas.append(ultimo)

    return {
        "earliest_contract": min(fechas) if fechas else None,
        "latest_contract": max(fechas) if fechas else None,
        "total_edges": G.number_of_edges(),
        "avg_contracts_per_edge": round(
            sum(d.get("num_contratos", 1) for _, _, d in G.edges(data=True)) / max(G.number_of_edges(), 1),
            2
        )
    }


def compute_graph_metrics(G: nx.Graph) -> dict:
    """
    Resume todas las métricas del grafo en un solo dict.
    """
    # Métricas globales
    num_entidades = sum(1 for _, d in G.nodes(data=True) if d.get("type") == "entidad")
    num_proveedores = sum(1 for _, d in G.nodes(data=True) if d.get("type") == "proveedor")
    num_sancionados = sum(1 for _, d in G.nodes(data=True) if d.get("sancionado"))
    num_alto_riesgo = sum(
        1 for _, d in G.nodes(data=True)
        if d.get("riesgo_max", 0) >= 55
    )

    densidad = nx.density(G)
    num_componentes = nx.number_connected_components(G)

    # Componente gigante
    componentes = list(nx.connected_components(G))
    componente_gigante = max(componentes, key=len) if componentes else set()

    return {
        "nodos_total": G.number_of_nodes(),
        "entidades": num_entidades,
        "proveedores": num_proveedores,
        "aristas": G.number_of_edges(),
        "densidad": round(densidad, 6),
        "componentes_conectados": num_componentes,
        "componente_gigante_nodos": len(componente_gigante),
        "proveedores_sancionados_en_red": num_sancionados,
        "proveedores_alto_riesgo": num_alto_riesgo,
        "promedio_grado": round(
            sum(dict(G.degree()).values()) / max(G.number_of_nodes(), 1), 2
        ),
    }
