# workers/graph_entity_resolution.py
"""
Entity Resolution para el grafo LUPA.
Resuelve entidades duplicadas antes de construir el grafo.
Estrategia: NIT primero → luego fuzzy matching de nombres.
"""

import logging
import pandas as pd
from rapidfuzz import process, fuzz

logger = logging.getLogger("lupa.graph_entity_resolution")


def normalize_nit(nit_raw) -> str:
    """
    Normaliza NIT: quita puntos, guiones, dígito verificador opcional.
    Retorna NIT limpio para matching exacto.
    Ej: "900.123.456-7" → "900123456"
    """
    if not nit_raw or pd.isna(nit_raw):
        return ""
    raw = str(nit_raw).strip()
    # Quitar puntos, guiones, espacios
    cleaned = raw.replace(".", "").replace("-", "").replace(" ", "")
    # Si termina en dígito después de un guion (DV), quitarlo
    # El NIT base son los primeros 9-10 dígitos
    if cleaned.isdigit():
        # NIT colombiano típico: 9 dígitos + 1 DV
        # Algunos tienen más (históricos), otros menos (naturales)
        return cleaned[:-1] if len(cleaned) >= 2 else cleaned
    # Si no es dígito puro, guardar como está
    return cleaned


def resolve_entities_from_df(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Toma un DataFrame de contratos_raw y resuelve entidades duplicadas.

    Retorna:
        - df_limpio: con columnas nit_entidad_norm, nit_proveedor_norm
        - stats: dict con métricas de resolución
    """
    df = df.copy()

    # Normalizar NITs
    df["nit_entidad_norm"] = df["nit_entidad"].apply(normalize_nit)
    df["nit_proveedor_norm"] = df["documento_proveedor"].apply(normalize_nit)

    # Contar duplicados de nombres (para fuzzy matching posterior)
    nombres_entidad = df.dropna(subset=["nit_entidad_norm", "nombre_entidad"]) \
        .groupby("nit_entidad_norm")["nombre_entidad"].apply(lambda x: x.mode().iloc[0] if not x.mode().empty else "") \
        .to_dict()

    # Detectar NITs múltiples nombres (posibles duplicados)
    nit_multi_nombre = df.dropna(subset=["nit_entidad_norm", "nombre_entidad"]) \
        .groupby("nit_entidad_norm")["nombre_entidad"].nunique() \
        .sort_values(ascending=False)

    nit_con_duplicados = {
        str(nit): int(nombres)
        for nit, nombres in nit_multi_nombre.items()
        if nombres > 1 and nit  # ignorar vacíos
    }

    stats = {
        "total_registros": len(df),
        "entidades_unicas": df["nit_entidad_norm"].nunique(),
        "proveedores_unicos": df["nit_proveedor_norm"].nunique(),
        "entidades_multi_nombre": len(nit_con_duplicados),
        "detalle_entidades_multi": nit_con_duplicados,
    }

    logger.info(
        f"Entity resolution: {stats['entidades_unicas']} entidades únicas, "
        f"{stats['proveedores_unicos']} proveedores únicos, "
        f"{stats['entidades_multi_nombre']} entidades con nombres múltiples"
    )

    return df, stats


def find_similar_entity_names(entity_names: list[str], threshold: int = 85) -> list[dict]:
    """
    Encuentra nombres de entidades similares con fuzzy matching.
    Útil para detectar "EPM ESP" vs "EPM S.A. E.S.P."

    entity_names: lista de nombres únicos de entidades
    threshold: puntuación mínima de similitud (0-100)

    Retorna lista de pares similares.
    """
    similares = []
    seen = set()

    for name in entity_names:
        if not name or len(name) < 3:
            continue

        # Buscar nombres similares
        matches = process.extract(
            name,
            entity_names,
            scorer=fuzz.token_sort_ratio,
            limit=5,
            score_cutoff=threshold
        )

        for match_name, score, _ in matches:
            if match_name == name:
                continue
            # Evitar duplicados (A,B) == (B,A)
            pair_key = tuple(sorted([name, match_name]))
            if pair_key in seen:
                continue
            seen.add(pair_key)

            similares.append({
                "nombre_1": name,
                "nombre_2": match_name,
                "similitud": round(score, 1)
            })

    return sorted(similares, key=lambda x: x["similitud"], reverse=True)


def merge_entity_aliases(df: pd.DataFrame, aliases: dict[str, str]) -> pd.DataFrame:
    """
    Fusiona alias de entidades en un NIT canónico.

    aliases: dict {nit_malo: nit_bueno}
    Ej: {"900123455": "900123456"} → fusiona el NIT malo al bueno

    Retorna df con nit_entidad_norm actualizado.
    """
    df = df.copy()
    merged_count = 0

    for nit_malo, nit_bueno in aliases.items():
        mask = df["nit_entidad_norm"] == nit_malo
        count = mask.sum()
        if count > 0:
            df.loc[mask, "nit_entidad_norm"] = nit_bueno
            merged_count += count
            logger.info(f"Fusionada entidad {nit_malo} → {nit_bueno} ({count} registros)")

    if merged_count > 0:
        logger.info(f"Total registros fusionados: {merged_count}")

    return df
