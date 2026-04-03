# scoring_engine.py — LUPA MVP v1.1 — con flags VigIA + OCP
import pandas as pd
import sys
import io

# Forzar UTF-8 en Windows para evitar errores de codificación en consola
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SMMLV_2026      = 1_423_500
UMBRAL_MINIMA   = 28  * SMMLV_2026   # ~$39.8M
UMBRAL_LICIT    = 1000 * SMMLV_2026  # ~$1,423M

ENTIDADES_PUBLICAS = {
    '800194096','890905378','900602106','800153898',
    '890904996','900006094','890900608','811021514',
    '890903790','890904153','890904635','890980040','800025606',
}

def flag_A1(row):
    modalidad = str(row.get('modalidad','')).lower()
    valor     = float(row.get('valor_del_contrato', 0) or 0)
    nit       = str(row.get('nit_proveedor','') or '').strip()

    if 'directa' not in modalidad and 'minima cuant' not in modalidad:
        return 0, None
    if 'minima cuant' in modalidad:
        return (12, "Mínima cuantía por valor superior al umbral") if valor > UMBRAL_MINIMA else (0, None)

    if valor > 2_000_000_000:   pts, desc = 30, f"Contratación directa ${valor/1e9:.1f}B sin licitación"
    elif valor > 1_000_000_000: pts, desc = 22, f"Contratación directa ${valor/1e6:.0f}M sin licitación"
    elif valor > 500_000_000:   pts, desc = 16, f"Contratación directa ${valor/1e6:.0f}M sin licitación"
    else:                        pts, desc = 12, "Contratación directa sin competencia"

    if nit in ENTIDADES_PUBLICAS:
        just = str(row.get('justificacion_modalidad','') or '')
        return (int(pts*0.5), f"[INTERADM] {desc}") if len(just)>20 else (int(pts*0.8), f"[INTERADM SIN JUSTIF] {desc}")
    return pts, desc

def flag_A5(row):
    modalidad = str(row.get('modalidad','')).lower()
    just      = str(row.get('justificacion_modalidad','') or '').strip()
    valor     = float(row.get('valor_del_contrato', 0) or 0)
    if 'directa' not in modalidad: return 0, None
    sin_just = just in ['','nan','None','No Definido','Sin Descripcion','No definido'] or len(just)<20
    if sin_just and valor > 200_000_000:
        return 8, "Contratación directa sin justificación documentada"
    return 0, None

def flag_IRIC_firma_tardia(row):
    """Hallazgo clave de VigIA — contrato firmado DESPUÉS de su inicio."""
    firma = row.get('fecha_firma')
    inicio = row.get('fecha_inicio')
    if pd.isna(firma) or pd.isna(inicio):
        return 8, "Fechas de firma o inicio ausentes — opacidad crítica"
    try:
        dias = (firma - inicio).days
        if dias > 20: return 15, f"Contrato firmado {dias} días DESPUÉS de su inicio (señal VigIA)"
        if dias > 0:  return 8,  f"Contrato firmado {dias} días después de su inicio"
    except: pass
    return 0, None

def flag_R031(row):
    """Precio adjudicado = presupuesto oficial → posible fuga de información."""
    valor = float(row.get('valor_del_contrato', 0) or 0)
    saldo = float(row.get('saldo_cdp', 0) or 0)
    if saldo == 0 or valor == 0: return 0, None
    ratio = valor / saldo
    if ratio >= 0.99: return 10, f"Precio adjudicado es {ratio:.1%} del presupuesto oficial — posible fuga de info"
    if ratio >= 0.96: return 5,  f"Precio muy cercano al presupuesto oficial ({ratio:.1%})"
    return 0, None

def flag_R054(row):
    """Contrato directo + anticipo superan umbral de licitación."""
    if 'directa' not in str(row.get('modalidad','')).lower(): return 0, None
    valor    = float(row.get('valor_del_contrato', 0) or 0)
    anticipo = float(row.get('valor_anticipo', 0) or 0)
    if (valor + anticipo) > UMBRAL_LICIT and valor < UMBRAL_LICIT:
        return 15, f"Contrato directo + adiciones = ${(valor+anticipo)/1e9:.1f}B — supera umbral de licitación"
    return 0, None

def flag_C1(row):
    original = float(row.get('valor_del_contrato', 0) or 0)
    anticipo = float(row.get('valor_anticipo', 0) or 0)
    if original == 0: return 0, None
    ratio = anticipo / original
    if ratio > 0.5: return 10, f"Anticipo del {ratio:.0%} del valor total"
    if ratio > 0.3: return 6,  f"Anticipo del {ratio:.0%} del valor total"
    if ratio > 0.15: return 3, f"Anticipo del {ratio:.0%} del valor total"
    return 0, None

def flag_C2(row):
    dias  = float(row.get('dias_adicionados', 0) or 0)
    valor = float(row.get('valor_del_contrato', 0) or 0)
    if dias > 365 and valor > 500_000_000: return 8, f"Prorrogado {dias:.0f} días — revisión recomendada"
    if dias > 180: return 4, f"Prorrogado {dias:.0f} días"
    return 0, None

def flag_D1(row):
    objeto = str(row.get('objeto','') or '').lower()
    valor  = float(row.get('valor_del_contrato', 0) or 0)
    VAGAS  = ['apoyo a la gestión','apoyo a la gestion','servicios de apoyo',
              'actividades administrativas','gestión administrativa']
    if any(p in objeto for p in VAGAS) and valor > 100_000_000:
        return 4, "Objeto vago ('apoyo a la gestión') para valor alto"
    if len(objeto) < 50 and valor > 100_000_000:
        return 2, f"Objeto muy corto ({len(objeto)} chars) para ${valor/1e6:.0f}M"
    return 0, None

def flag_D2(row):
    url   = str(row.get('url_proceso','') or '')
    valor = float(row.get('valor_del_contrato', 0) or 0)
    if url in ['nan','None','','{}'] and valor > 50_000_000:
        return 4, "Contrato sin URL de proceso publicada"
    return 0, None

def flag_R047(row):
    nombre = str(row.get('nombre_proveedor','') or '').lower()
    valor  = float(row.get('valor_del_contrato', 0) or 0)
    VAGAS  = ['servicios generales','soluciones integrales','comercializadora',
              'inversiones y','grupo empresarial','asesorias y','consultoria y']
    if any(p in nombre for p in VAGAS) and valor > 100_000_000:
        return 6, f"Proveedor con nombre genérico difícil de rastrear"
    return 0, None

TRADUCCION = {
    3_000_000_000: lambda v: f"{v/3e9:.1f} colegios nuevos",
    350_000_000:   lambda v: f"{v/350e6:.0f} ambulancias equipadas",
    70_000_000:    lambda v: f"{v/70e6:.0f} canchas deportivas",
    0:             lambda v: f"refrigerio de {int(v/3650 or 0):,} niños por 1 año",
}
def impacto_ciudadano(valor):
    for umbral, fn in sorted(TRADUCCION.items(), reverse=True):
        if valor >= umbral: return fn(valor)
    return "N/A"

def calcular_score(row):
    flags = []
    # Usamos una lista de funciones para facilitar el bucle
    flag_functions = [
        (flag_A1,'A1'),(flag_A5,'A5'),(flag_IRIC_firma_tardia,'IRIC'),
        (flag_R031,'R031'),(flag_R054,'R054'),(flag_C1,'C1'),
        (flag_C2,'C2'),(flag_D1,'D1'),(flag_D2,'D2'),(flag_R047,'R047')
    ]
    for fn, cod in flag_functions:
        pts, desc = fn(row)
        if pts > 0:
            flags.append({'codigo': cod, 'descripcion': desc, 'puntos': pts})

    total = min(sum(f['puntos'] for f in flags), 100)
    if len(flags) >= 3: 
        total = min(total + 10, 100)  # bonus patrón sistémico

    nivel = 'CRÍTICO' if total>=80 else 'ALTO' if total>=65 else 'MEDIO' if total>=40 else 'BAJO'
    return {
        'score': total, 'nivel': nivel, 'n_flags': len(flags),
        'razon_principal': flags[0]['descripcion'] if flags else "Sin señales",
        'flags_detalle': str([f['codigo'] for f in sorted(flags, key=lambda x: x['puntos'], reverse=True)]),
    }

if __name__ == "__main__":
    print("⚙️  Calculando scores LUPAVigIA v1.1...")
    try:
        df = pd.read_csv("contratos_aptos.csv", low_memory=False)
    except FileNotFoundError:
        print("❌ Error: No se encuentra contratos_aptos.csv. Ejecuta quality_gate.py primero.")
        sys.exit(1)

    # Conversión de fechas una sola vez al inicio (Optimización crítica)
    print("🕒 Convirtiendo fechas...")
    for col in ['fecha_firma','fecha_inicio','fecha_fin']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    print(f"📊 Procesando {len(df)} registros con lógica LUPA v1.1...")
    # El apply sigue siendo necesario por la complejidad de las reglas, 
    # pero sin pd.to_datetime interno es mucho más rápido.
    df_results = df.apply(lambda r: pd.Series(calcular_score(r.to_dict())), axis=1)
    df = pd.concat([df, df_results], axis=1)
    
    print("💰 Calculando impacto ciudadano...")
    df['impacto_ciudadano'] = df['valor_del_contrato'].apply(lambda v: impacto_ciudadano(float(v or 0)))
    
    print("💾 Guardando resultados...")
    df.to_csv("contratos_scored.csv", index=False)

    print("\n📊 Distribución de niveles:")
    if 'nivel' in df.columns:
        print(df['nivel'].value_counts())
    
    print("\n🚨 Top 10 contratos más sospechosos:")
    cols_top = ['nombre_entidad','nombre_proveedor','valor_del_contrato','score','nivel','razon_principal','impacto_ciudadano']
    top10 = df.nlargest(10, 'score')
    print(top10[cols_top].to_string(index=False))
    
    top10[cols_top].to_csv("top10_sospechosos.csv", index=False)
    print("\n✨ Proceso completado exitosamente.")