import pandas as pd
import re

VALORM_FILE = "reports/caso_valorm.csv"
ADS_FILE = "reports/valorm_adiciones_analisis.csv"

def extract_money(text):
    if not isinstance(text, str): return 0
    matches = re.findall(r'\$\s?(\d+[\d\.,]*)', text)
    if not matches: return 0
    try:
        val = matches[0].replace('.', '').replace(',', '.')
        return float(val)
    except: return 0

def analize_legality():
    # 1. Leer contratos originales
    df_orig = pd.read_csv(VALORM_FILE)
    df_orig = df_orig[['id_contrato', 'valor_del_contrato', 'nombre_entidad']].copy()
    
    # 2. Leer adiciones y sumar por contrato
    df_ads = pd.read_csv(ADS_FILE)
    df_ads['valor_adicion'] = df_ads['descripcion'].apply(extract_money)
    summary_ads = df_ads.groupby('id_contrato')['valor_adicion'].sum().reset_index()
    
    # 3. Cruzar
    merged = pd.merge(df_orig, summary_ads, on='id_contrato', how='inner')
    
    # 4. Calcular porcentaje
    # Evitar division por cero
    merged = merged[merged['valor_del_contrato'] > 0]
    merged['porcentaje_adicion'] = (merged['valor_adicion'] / merged['valor_del_contrato']) * 100
    
    # 5. Filtrar ilegales (> 50%)
    ilegales = merged[merged['porcentaje_adicion'] > 50].copy()
    ilegales = ilegales.sort_values(by='porcentaje_adicion', ascending=False)
    
    print(f"--- Auditoria de Legalidad (Limite 50% - Ley 80) ---")
    print(f"Contratos analizados con adiciones de dinero: {len(merged)}")
    print(f"Contratos que superan el limite del 50%: {len(ilegales)}")
    
    if not ilegales.empty:
        print("\nTop casos que superan el limite legal:")
        print(ilegales[['id_contrato', 'valor_del_contrato', 'valor_adicion', 'porcentaje_adicion']].head(10).to_string(index=False))
        ilegales.to_csv("reports/valorm_ilegales_50porc.csv", index=False)
        print(f"\nReporte guardado en reports/valorm_ilegales_50porc.csv")

if __name__ == "__main__":
    analize_legality()
