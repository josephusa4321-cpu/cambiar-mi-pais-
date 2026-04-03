import requests
import pandas as pd
import sys
import io
import os

# Forzar salida en UTF-8 para evitar errores en Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Dataset ID: cb9c-h8sn (Adiciones SECOP II)
ADICIONES_URL = "https://www.datos.gov.co/resource/cb9c-h8sn.json"
OUTPUT_FILE = "data/raw/adiciones_raw.csv"

# Filtrar por los Nits que nos interesan para el MVP
# 890905378: Distrito de Medellín
# 890900286: Gobernación de Antioquia
FILTRO_ENTIDADES = "nit_entidad IN ('890905378','890900286')"

def extraer_adiciones_optimizadas(limite=10000):
    os.makedirs("data/raw", exist_ok=True)
    offset = 0
    primera_vez = True
    
    # Reiniciamos el archivo para tener la data limpia de Medellín/Antioquia
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    print(f"🎯 Iniciando descarga OPTIMIZADA (Solo Medellín/Antioquia) en {OUTPUT_FILE}...")

    total_descargado = 0
    while True:
        try:
            # Socrata query: $where para filtrar en el servidor
            params = {
                "$limit": limite, 
                "$offset": offset,
                "$where": FILTRO_ENTIDADES
            }
            r = requests.get(ADICIONES_URL, params=params, timeout=60)
            
            if r.status_code != 200:
                print(f"Error {r.status_code}: {r.text[:200]}")
                break
            
            batch = r.json()
            if not batch: 
                print("\n✅ Final de la tabla alcanzado para estas entidades.")
                break
            
            df_batch = pd.DataFrame(batch)
            df_batch.to_csv(OUTPUT_FILE, mode='a', index=False, header=primera_vez, encoding='utf-8')
            
            primera_vez = False
            total_descargado += len(batch)
            offset += limite
            
            print(f"  → {total_descargado} adiciones de interés guardadas...")
            
        except Exception as e:
            print(f"\n❌ Error en la petición: {e}")
            import time
            time.sleep(5)
            continue
            
    return total_descargado

if __name__ == "__main__":
    print("🔍 LUPA Sprint 2: Radar de Sobrecostos Seleccionado")
    total = extraer_adiciones_optimizadas()
    print(f"\n✅ Proceso finalizado. Total registros de interés: {total}")
