import pandas as pd
import sys
import io

# UTF-8 for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

df = pd.read_csv("contratos_scored.csv", low_memory=False)

print("=== DISTRIBUCIÓN DE SCORES LUPA v1.1 ===")
print(df['score'].value_counts().head(10))
print("\n" + df['nivel'].value_counts().to_string())

print("\n" + "="*100)
print("=== ANÁLISIS DE PROVEEDORES PRIORITARIOS ===")
print("="*100)

providers = ['PROSOSERH', 'VALOR+', 'UT INTERVENCIONES', 'COMITÉ ESTUDIOS']
cols = ['nombre_entidad', 'nombre_proveedor', 'valor_del_contrato', 'modalidad', 'fecha_firma', 'objeto', 'score']

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 60)

for p in providers:
    mask = df['nombre_proveedor'].str.contains(p, case=False, na=False)
    sub = df[mask][cols].copy()
    print(f"\nPROVEEDOR: {p} — {len(sub)} contratos detectados")
    if not sub.empty:
        sub['fecha_firma'] = pd.to_datetime(sub['fecha_firma'], errors='coerce')
        print(sub.sort_values('fecha_firma').to_string(index=False))
    print("-" * 100)
