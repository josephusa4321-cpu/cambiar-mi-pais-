import requests
import json

ADICIONES_URL = "https://www.datos.gov.co/resource/cb9c-h8sn.json"

def check_schema():
    try:
        r = requests.get(ADICIONES_URL, params={"$limit": 1}, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if data:
                print("--- Primer registro de Adiciones SECOP II ---")
                print(json.dumps(data[0], indent=2))
                print("\n--- Todas las columnas detectadas ---")
                print(list(data[0].keys()))
            else:
                print("No hay datos en el dataset.")
        else:
            print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
