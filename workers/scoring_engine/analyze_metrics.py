import pandas as pd
import json

df = pd.read_csv('contratos_scored.csv', low_memory=False)
res = {}
providers = ['PROSOSERH', 'VALOR+', 'UT INTERVENCIONES', 'COMITÉ ESTUDIOS']

for p in providers:
    sub = df[df['nombre_proveedor'].str.contains(p, case=False, na=False)]
    if not sub.empty:
        res[p] = {
            'count': int(len(sub)),
            'max_val': float(sub['valor_del_contrato'].max()),
            'avg_score': round(float(sub['score'].mean()), 1),
            'entidades': sub['nombre_entidad'].unique().tolist()[:3]
        }
    else:
        res[p] = 'Not Found'

print(json.dumps(res, indent=2))
