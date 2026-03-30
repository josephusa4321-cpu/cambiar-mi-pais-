# quality_gate.py
import pandas as pd
import numpy as np

def calcular_icd_batch(df):
    campos = {
        'nit_proveedor': 15, 'nombre_proveedor': 10, 'valor_del_contrato': 20,
        'nombre_entidad': 10, 'modalidad': 15, 'objeto': 15,
        'fecha_firma': 10, 'tipo_contrato': 5,
    }
    
    # Pre-calcular validez de campos (vectorizado es más rápido para algunos tipos)
    score = np.zeros(len(df))
    faltantes_col = [[] for _ in range(len(df))]
    
    invalidos = ['', 'nan', 'none', '0', 'n/a', 'no definido']
    
    print("📊 Procesando calidad de datos...")
    total = len(df)
    
    for i, (campo, peso) in enumerate(campos.items()):
        if campo in df.columns:
            # Convertir a string y minúsculas para comparar uniformemente
            vals = df[campo].astype(str).str.strip().str.lower()
            mask = ~vals.isin(invalidos) & vals.notna()
            score += mask * peso
            
            # Registrar faltantes para las filas donde la máscara es falsa
            for idx in np.where(~mask)[0]:
                faltantes_col[idx].append(campo)
        else:
            for idx in range(total):
                faltantes_col[idx].append(campo)
                
    return score, [str(f) for f in faltantes_col]

if __name__ == "__main__":
    print("📖 Cargando datos (251k+ registros)...")
    df = pd.read_csv("contratos_medellin_raw.csv", low_memory=False)
    
    scores, faltantes = calcular_icd_batch(df)
    df['icd'] = scores
    df['campos_faltantes'] = faltantes
    
    aptos  = df[df['icd'] >= 40]
    opacos = df[df['icd'] < 40]
    
    print(f"✅ Aptos: {len(aptos)} | 🔴 Opacos: {len(opacos)}")
    
    print("💾 Guardando resultados...")
    aptos.to_csv("contratos_aptos.csv", index=False)
    opacos.to_csv("contratos_opacos.csv", index=False)
    print("✨ Guardado: contratos_aptos.csv y contratos_opacos.csv")