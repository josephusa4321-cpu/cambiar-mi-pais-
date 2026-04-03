import pandas as pd
import requests
import json
import os

# Archivos de entrada
VALORM_FILE = "reports/caso_valorm.csv"
ADICIONES_URL = "https://www.datos.gov.co/resource/cb9c-h8sn.json"
OUTPUT_REPORT = "reports/valorm_adiciones_analisis.csv"

def analizar_adiciones_valorm():
    if not os.path.exists(VALORM_FILE):
        print(f"Error: {VALORM_FILE} no encontrado.")
        return

    # 1. Leer IDs de VALOR+
    df_valorm = pd.read_csv(VALORM_FILE)
    if 'id_contrato' not in df_valorm.columns:
        print("Error: Columna 'id_contrato' no encontrada.")
        return
    
    ids = df_valorm['id_contrato'].unique().tolist()
    print(f"🔍 Analizando adiciones para {len(ids)} contratos de VALOR+...")

    todas_adiciones = []
    
    # 2. Consultar la API (en batches de 100 IDs para no saturar el URL)
    batch_size = 50
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i + batch_size]
        # Formatear IDs para query Socrata: id_contrato IN ('ID1', 'ID2')
        ids_str = ",".join([f"'{x}'" for x in batch_ids])
        where_clause = f"id_contrato IN ({ids_str})"
        
        try:
            r = requests.get(ADICIONES_URL, params={"$where": where_clause}, timeout=30)
            if r.status_code == 200:
                data = r.json()
                todas_adiciones.extend(data)
                print(f"  → Procesados {i + len(batch_ids)}/{len(ids)} contratos... ({len(data)} adiciones encontradas)")
            else:
                print(f"Error {r.status_code} en batch {i}")
        except Exception as e:
            print(f"Excepción en batch {i}: {e}")

    # 3. Guardar resultados
    if todas_adiciones:
        df_ads = pd.DataFrame(todas_adiciones)
        df_ads.to_csv(OUTPUT_REPORT, index=False, encoding='utf-8')
        print(f"\n✅ Análisis completado. {len(df_ads)} adiciones guardadas en {OUTPUT_REPORT}")
        
        # 4. Resumen rápido
        print("\n--- Resumen por Tipo de Modificación ---")
        print(df_ads['tipo'].value_counts())
        
        # 5. Buscar palabras clave de dinero en la descripción
        if 'descripcion' in df_ads.columns:
            print("\n--- Muestra de Adiciones con presupuesto ---")
            ads_dinero = df_ads[df_ads['descripcion'].str.contains('valor|adicion|pesos|suma', case=False, na=False)]
            print(ads_dinero[['id_contrato', 'tipo', 'descripcion']].head(5).to_string())
    else:
        print("\n⚠️ No se encontraron adiciones registradas para estos contratos en SECOP II.")

if __name__ == "__main__":
    analizar_adiciones_valorm()
