import pandas as pd
import sys

# Forzar salida en UTF-8 para evitar errores en Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

df = pd.read_csv("contratos_scored.csv", low_memory=False)
df['valor_del_contrato'] = pd.to_numeric(df['valor_del_contrato'], errors='coerce').fillna(0)

# 1. Proveedores con más contratos directos — detecta fraccionamiento R055
directos = df[df['modalidad'].str.contains('directa', case=False, na=False)]
concentracion = directos.groupby('nombre_proveedor').agg(
    n_contratos   = ('id_contrato', 'count'),
    valor_total   = ('valor_del_contrato', 'sum'),
    valor_max     = ('valor_del_contrato', 'max'),
    entidades     = ('nombre_entidad', 'nunique'),
    score_promedio= ('score', 'mean')
).sort_values('valor_total', ascending=False).head(20)

print("🔍 Top 20 proveedores por valor total en contratación directa:")
print(concentracion.to_string())
concentracion.to_csv("concentracion_proveedores.csv")

# 2. Entidades que más contratan directamente — detecta abuso institucional
abuso = directos.groupby('nombre_entidad').agg(
    n_contratos = ('id_contrato', 'count'),
    valor_total = ('valor_del_contrato', 'sum'),
    proveedores_distintos = ('nombre_proveedor', 'nunique'),
).sort_values('valor_total', ascending=False).head(20)

print("\n🏛️ Top 20 entidades por valor total en contratación directa:")
print(abuso.to_string())
abuso.to_csv("concentracion_entidades.csv")

# 3. Valor+ específico — suma total real
# Usamos una búsqueda más flexible para VALOR+
valorm = df[df['nombre_proveedor'].str.contains('VALOR', case=False, na=False)]
print(f"\n💰 VALOR+ S.A.S — total acumulado: ${valorm['valor_del_contrato'].sum()/1e9:.1f}B en {len(valorm)} contratos")
print(f"   ¿Supera umbral de licitación (~$1,423M)? {'✅ SÍ' if valorm['valor_del_contrato'].sum() > 1_423_000_000 else '❌ No'}")
