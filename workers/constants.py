# workers/constants.py
# Única fuente de verdad para constantes de LUPA
import re

SMMLV_2026 = 1_423_500
UMBRAL_MINIMA = 28 * SMMLV_2026    # ~$39.8M COP
UMBRAL_LICIT  = 1_000 * SMMLV_2026 # ~$1,423M COP

# Umbrales Certificados (LUPA v1.1 Audit)
UMBRAL_NIVEL1 = 40   # MEDIO
UMBRAL_NIVEL2 = 55   # ALTO
UMBRAL_NIVEL3 = 70   # CRÍTICO

# Pesos de Riesgo Originales (PRD §6.1)
PESO_A1 = 12

PESO_B1 = 20  # Activado (SIRI CSV Local)
PESO_B3 = 7

# C1: Sobrecosto por adición (auditor scale)
PESO_C1_MIN = 3    # 10-30%
PESO_C1_MED = 6    # 30-50%
PESO_C1_MAX = 10   # > 50%

PESO_C2 = 10
PESO_D1 = 6
PESO_D2 = 4
PESO_BONUS = 10

# ACTT: Modalidades que califican para atenuación (PRD §6.5)
MODALIDADES_ACTT = frozenset({
    "convenio interadministrativo",
    "convenio de asociación",
    "contrato interadministrativo",
})

# Umbrales C1 (Adiciones Graduadas)
UMBRAL_C1_CRITICO = 0.50  # >50%
UMBRAL_C1_MEDIO   = 0.30  # >30%
UMBRAL_C1_MINIMO  = 0.15  # >15%

BATCH_SIZE_UPSERT = 500
HTTP_TIMEOUT      = 60
SODA_LIMIT_MAX    = 1_000
UMBRAL_BUG_CENTAVOS = 500_000_000_000  # 500B COP (Corta el bug de SECOP x100)

# Columnas mínimas necesarias del engine (evitar select *)
COLUMNAS_SCORING = [
    "id_contrato", "modalidad_de_contratacion", "valor_del_contrato",
    "objeto_del_contrato", "documento_proveedor",
    "nit_entidad", "nombre_entidad", "sector", "ultima_actualizacion",
    "fecha_de_firma", "valor_contrato_con_adiciones"
]

# Regex C2: detecta prórrogas de tiempo en texto libre de SECOP II
# Patrón robusto: Maneja "TRES (3) MESES", "3 (TRES) MESES" y "15 MESES"
REGEX_DURATION = re.compile(
    r'(?:(\d+)(?:\s*\([^)]+\))?|[A-Z\s-]+\s*\((\d+)\))\s*(MES(?:ES)?|D[IÍ]A(?:S)?|A[NÑ]O(?:S)?|SEMANA(?:S)?)',
    re.IGNORECASE
)

DIAS_POR_UNIDAD = {
    "MES": 30, "MESES": 30,
    "DIA": 1,  "DIAS": 1, "DÍA": 1, "DÍAS": 1,
    "ANO": 365, "AÑOS": 365, "AÑO": 365, "AÑOS": 365,
}
