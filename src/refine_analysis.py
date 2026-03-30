import pandas as pd
import sys
import io

# Forzar salida en UTF-8 para evitar errores en Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

df = pd.read_csv("contratos_scored.csv", low_memory=False)
df['valor_del_contrato'] = pd.to_numeric(df['valor_del_contrato'], errors='coerce').fillna(0)
df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0)
df['fecha_firma'] = pd.to_datetime(df['fecha_firma'], errors='coerce')
df['tipodocproveedor'] = df['tipodocproveedor'].astype(str)

print("--- TIPO 1: ERRORES DE DATOS (PERSONAS NATURALES > $1,000M) ---")
# Contratos de personas naturales con valor > $1,000M son sospechosos de error
personas_naturales = df[
    (df['tipodocproveedor'].str.contains('Cédula', case=False, na=False)) &
    (df['valor_del_contrato'] > 1_000_000_000)
]
print(f"Hallazgos sospechosos de error (centavos): {len(personas_naturales)}")
print(personas_naturales[['nombre_proveedor','valor_del_contrato','nombre_entidad','objeto']].head(10).to_string())

print("\n--- TIPO 2: RUIDO INSTITUCIONAL (ITM Y PRESTACIÓN DE SERVICIOS < $20M) ---")
# Contratos de prestación de servicios < $20M no son prioritarios para Lupa
# Filtramos el ruido de ITM y similares
df_filtrado = df[~(
    (df['tipo_contrato'].str.contains('Prestación de servicios', case=False, na=False)) &
    (df['valor_del_contrato'] < 20_000_000)
)]
print(f"Contratos relevantes tras filtro: {len(df_filtrado)} (de {len(df)})")

print("\n--- TIPO 3: FICHA DE CASO - VALOR+ S.A.S ---")
valorm = df[df['nombre_proveedor'].str.contains('VALOR', case=False, na=False)].copy()
valorm = valorm.sort_values('fecha_firma')

print(f"TOTAL CONTRATOS:     {len(valorm)}")
print(f"VALOR ACUMULADO:     ${valorm['valor_del_contrato'].sum()/1e9:.2f}B COP")
print(f"ENTIDADES DISTINTAS: {valorm['nombre_entidad'].nunique()}")
print(f"PRIMER CONTRATO:     {valorm['fecha_firma'].min()}")
print(f"ÚLTIMO CONTRATO:     {valorm['fecha_firma'].max()}")

print(f"\nCONTRATOS POR ENTIDAD:")
print(valorm.groupby('nombre_entidad')['valor_del_contrato'].agg(['count','sum']).sort_values('sum', ascending=False).to_string())

print(f"\nOBJETOS MÁS FRECUENTES:")
print(valorm['objeto'].value_counts().head(5).to_string())

valorm[['nombre_entidad','valor_del_contrato','fecha_firma','objeto',
        'modalidad','score','justificacion_modalidad']].to_csv("caso_valorm.csv", index=False)
print("\n💾 Guardado: caso_valorm.csv")
