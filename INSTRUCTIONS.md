# INSTRUCTIONS.md — Lupa MVP v1.0
Sistema de Alerta Temprana Ciudadana para Contratación Pública — Medellín, Colombia

🧠 ¿Qué es este proyecto?
Lupa convierte datos abiertos del SECOP II en alertas accionables para detectar irregularidades en contratación pública. No es un dashboard pasivo — cada hallazgo tiene una acción acoplada (alerta Telegram, borrador de denuncia, timeline de impunidad).

Principio core: EL FRONTEND NUNCA CONSULTA datos.gov.co en vivo. Todo viene de Supabase. El pipeline nocturno extrae, limpia, puntúa y almacena. La web solo sirve.

🏗️ Arquitectura General Monorepo
lupa/
├── apps/
│   ├── web/                      # Next.js 15 (App Router) + React 19 + Tailwind v4
│   └── api/                      # FastAPI (Backend para reportes y utilidades)
├── workers/                      # Python ETL (Secop ingest, Scoring, Telegram)
├── infra/                        # Configuración Dokploy, n8n, Docker
├── data/                         # CSV de Sancionados (SIRI Procuraduría)
└── docs/                         # Metodología y Marco Legal Anti-SLAPP

🛠️ Stack Técnico (OVERRIDE GLOBAL RULE 1)
- Frontend: Next.js 15 (App Router) + React 19 + Tailwind v4.
- Backend: FastAPI (Python 3.11).
- DB: Supabase (PostgreSQL).
- Workers: Python puro (httpx, pandas, pydantic).

⚠️ Reglas Críticas (NO NEGOCIABLES)
1. SEGURIDAD LEGAL (SLAPP): NUNCA usar "corrupción" o similar. Usar "riesgo algorítmico". DisclaimerSlapp.tsx siempre hardcoded.
2. PRIVACIDAD: El endpoint /api/reportar NO loguea IPs. Cero tracking de usuarios en denuncias anónimas.
3. ZERO LIVE QUERY: El frontend nunca llama a datos.gov.co. Todo via Supabase.
4. SANCIONADOS: Si el CSV de sancionados tiene >14 días, la bandera B1 se desactiva automáticamente.

🔢 Scoring Engine (Niveles)
- 40+: Aparece en Web.
- 55+: Alerta Telegram + Botón "Copiar Denuncia".
- 70+: Dossier prioritario.
