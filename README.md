# 🐺 LUPA MVP v1.0 — Medellín
> "Vigilancia algorítmica para una contratación transparente."

![Sincronización Nocturna](https://github.com/josephusa4321-cpu/cambiar-mi-pais-/actions/workflows/lupa-worker.yml/badge.svg)

LUPA es un sistema de monitoreo automatizado diseñado para detectar riesgos en la contratación pública de Medellín (SECOP II). Utiliza un motor de reglas deterministas para calificar cada contrato y alertar sobre patrones de opacidad, falta de competencia o adiciones inusuales.

---

## ⚡ Enlaces Rápidos
- **Web:** [lupa-medellin.vercel.app](https://lupa-medellin.vercel.app)
- **Canal de Alertas:** [@LupaMedellin](https://t.me/LupaMedellin) (Telegram)
- **Metodología:** [Documentación Técnica](/metodologia)

---

## 🏗️ Stack Tecnológico
- **Frontend:** Next.js 15 (App Router), React 19, Tailwind v4, Zustand.
- **Backend/API:** FastAPI (Python).
- **Base de Datos:** Supabase (PostgreSQL).
- **Workers:** Python (Pandas/Hettpx) para ingesta y scoring batch.

---

## ⚖️ Blindaje Jurídico y Disclaimer (SLAPP)
**IMPORTANTE:** Lupa es un sistema de **análisis de riesgo estadístico**, NO una plataforma de acusación criminal. 

- El término **"corrupción"** no forma parte de los resultados del sistema. Se utiliza estrictamente la categoría **"Riesgo Algorítmico"**. 
- Los datos mostrados provienen de fuentes oficiales (datos.gov.co) y son procesados automáticamente.
- Cualquier hallazgo debe ser validado por entes de control u organismos de periodismo de investigación antes de emitir juicios de valor.

---

## 🚩 Banderas de Riesgo (ICD)
El sistema evalúa cada contrato bajo 10 indicadores clave, incluyendo:
- **A1:** Contratación Directa.
- **A2:** Oferente Único (Falta de competencia).
- **C1:** Adiciones presupuestales inmediatas.
- **B3:** Redes de contratistas recurrentes.
- **D1:** Precios fuera de mercado.

---

## 🛡️ Principio Zero-Live-Query
Para garantizar la independencia y velocidad del sistema, el frontend **nunca** realiza consultas directas a la API del Estado (Socrata). Todos los datos son ingeridos nocturnamente, validados, corregidos (centavos/tildes) y almacenados en nuestro Data Lake propietario.

---

## 🛠️ Contribuir
LUPA es un proyecto de código abierto para la ciudadanía. Si deseas mejorar el motor de scoring o la visualización de datos:
1. Revisa el `README.md` de cada carpeta (`apps/web`, `apps/api`, `workers`).
2. Implementa tus cambios siguiendo el estándar de TDD.

---
**© 2026 LUPA Medellín.** La vigilancia ciudadana es un derecho constitucional (Art. 20 CP).
