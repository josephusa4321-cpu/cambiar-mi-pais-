import pandas as pd
import sys
import io

# Forzar salida en UTF-8 para evitar errores en Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Cargamos el archivo generado en el paso anterior
df = pd.read_csv("caso_valorm.csv", low_memory=False)
df['valor_del_contrato'] = pd.to_numeric(df['valor_del_contrato'], errors='coerce').fillna(0)

# Separar arrendamientos de contratos de servicios
arrendamientos = df[df['objeto'].str.contains('arrendamiento|Arrendamiento', case=False, na=False)]
servicios      = df[~df['objeto'].str.contains('arrendamiento|Arrendamiento', case=False, na=False)]

print(f"=== FICHA REAL VALOR+ S.A.S ===")
print(f"Total contratos en el archivo: {len(df)}")
print(f"  → Arrendamientos (espacio CAD): {len(arrendamientos)}")
print(f"  → Contratos de servicios:       {len(servicios)}")
print(f"\nValor total (servicios):    ${servicios['valor_del_contrato'].sum()/1e9:.3f}B COP")
print(f"Valor total (arrendamientos): ${arrendamientos['valor_del_contrato'].sum()/1e9:.3f}B COP")
print(f"Valor TOTAL acumulado:      ${df['valor_del_contrato'].sum()/1e9:.3f}B COP")

print(f"\nTop 5 contratos por valor:")
top5 = servicios.nlargest(5,'valor_del_contrato')
print(top5[['nombre_entidad','valor_del_contrato','fecha_firma','objeto']].to_string(index=False))

# Detección R048 — proveedor heterogéneo
print(f"\nTipos de objeto detectados (R048 — proveedor heterogéneo):")
categorias = {
    'Catastro/Valorización': ['catastro','valorización','valorizacion'],
    'IT/Hosting/Mesa servicios': ['hosting','mesa de servicios','plataforma tecnológica','TIC'],
    'Seguridad electrónica': ['seguridad','cámaras','convivencia','TESCC'],
    'Contact Center/BPO': ['contact center','BPO','cobranza','gestión de cartera'],
    'Gestión documental': ['gestión documental','documental','archivo'],
    'Conectividad/Internet': ['conectividad','internet'],
    'Arrendamiento': ['arrendamiento'],
}

for cat, keywords in categorias.items():
    mask = df['objeto'].str.contains('|'.join(keywords), case=False, na=False)
    n = df[mask]
    if len(n) > 0:
        print(f"  {cat:25}: {len(n):2} contratos — ${n['valor_del_contrato'].sum()/1e9:.3f}B")

# Análisis R044 - Contratista Cautivo (Arrendamientos repetidos)
if len(arrendamientos) > 0:
    print(f"\n🚨 Alerta R044 (Contratista Cautivo):")
    print(f"  La empresa arrienda espacios físicos a la entidad {arrendamientos['nombre_entidad'].iloc[0]} recurrentemente.")
