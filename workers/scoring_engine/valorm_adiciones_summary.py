import pandas as pd
import re

FILE = "reports/valorm_adiciones_analisis.csv"

def extract_money(text):
    # Buscar patrones de moneda: $ 1.000.000 o numeros grandes seguidos de pesos
    if not isinstance(text, str): return 0
    matches = re.findall(r'\$\s?(\d+[\d\.,]*)', text)
    if not matches:
        return 0
    # Limpiar el numero (quitar puntos de miles)
    try:
        val = matches[0].replace('.', '').replace(',', '.')
        return float(val)
    except:
        return 0

def summarize():
    df = pd.read_csv(FILE)
    df['valor_detectado'] = df['descripcion'].apply(extract_money)
    
    # Filtrar solo las que tienen dinero detectado (> 1M para evitar ruidos de fechas)
    df_money = df[df['valor_detectado'] > 1_000_000].copy()
    
    print(f"--- Hallazgos de Sobrecostos en VALOR+ ---")
    print(f"Total de modificaciones analizadas: {len(df)}")
    print(f"Modificaciones con impacto econ\u00f3mico detectado: {len(df_money)}")
    
    summary = df_money.groupby('id_contrato')['valor_detectado'].sum().reset_index()
    summary = summary.sort_values(by='valor_detectado', ascending=False)
    
    print("\nTop 5 Contratos con mayores Adiciones detectadas:")
    print(summary.head(10).to_string(index=False))
    
    print("\nEjemplos de descripciones de adici\u00f3n:")
    for i, row in df_money.head(3).iterrows():
        print(f"- [{row['id_contrato']}]: {row['descripcion'][:200]}...")

if __name__ == "__main__":
    summarize()
