# 🐺 LUPA - Guia de Ejecucion Rapida

## 📋 Comandos para tu Terminal

### Lote 1: Ingesta completa de contratos (~50,000)
```bash
py workers/secop_ingest.py full-history
```
**Duracion estimada**: 20-30 minutos
**Que veras**: Progreso pagina a pagina + batch por batch

### Lote 2: Adiciones (CSV directo + fallback SODA)
```bash
py workers/adiciones_ingest.py
```
**Duracion estimada**: 5-15 minutos

### Lote 3: Scoring FULL (todos los contratos)
```bash
py workers/scoring_engine.py full
```
**Duracion estimada**: 15-25 minutos
**Que veras**: Progreso cada 100 contratos con score/nivel/banderas

### Lote 4: Crear tabla metricas_historicas
```bash
py workers/crear_metricas.py
```
**Nota**: Te mostrara el SQL para ejecutar en Supabase si la tabla no existe

### Lote 5: Analytics Engine
```bash
py workers/analytics_engine.py
```
**Duracion estimada**: 3-5 minutos

### Lote 6: Verificar B3
```bash
py workers/verificar_b3.py
```
**Que veras**: Top 20 proveedores con mas contratos directos

---

## 🚀 Opcion Facil: Menu Interactivo

Solo ejecuta en tu terminal:
```bash
run_lotes.bat
```

Te dara un menu para elegir que lote correr.

---

## 📊 Que esperar en la terminal

### Ingesta Contratos:
```
📊 Página   | Registros   | Total Acumulado
--------------------------------------------------
📊 Pág    1   |   5000 regs   |    5,000
📊 Pág    2   |   5000 regs   |   10,000
📊 Pág    3   |   5000 regs   |   15,000
...
📦 Insertando 50,000 registros en contratos_raw (100 batches de 500)...
📊 Batch    | Estado      | Acumulado
--------------------------------------------------
📊    1/100   | ✅ OK        |      500 regs
📊    2/100   | ✅ OK        |    1,000 regs
...
✅ FINALIZADO: CONTRATOS — OK: 100 batches | Fallidos: 0
```

### Scoring:
```
📊 Contrato  | Score | Nivel  | Bandas | Acumulado
-----------------------------------------------------------------
📊    100/50,000 |    12 | BAJO   | A1                   |    100
📊    200/50,000 |    36 | BAJO   | A1,C2,D2,BONUS       |    200
📊    300/50,000 |    46 | MEDIO  | A1,B1,D2,BONUS       |    300
...
```

---

## ✅ Verificacion rapida

Despues de correr Lote 1 + 3:
```bash
py -c "from supabase import create_client; import os; from dotenv import load_dotenv; load_dotenv(); sb=create_client(os.environ.get('NEXT_PUBLIC_SUPABASE_URL'), os.environ.get('SERVICE_ROLE_KEY')); print('Contratos raw:', len(sb.table('contratos_raw').select('id_contrato').limit(1).execute().data)); print('Scored:', len(sb.table('contratos_scored').select('id_contrato').limit(1).execute().data))"
```
