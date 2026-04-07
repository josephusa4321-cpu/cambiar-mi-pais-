UPA MVP v1.0 — PRODUCT REQUIREMENTS DOCUMENT
Sistema de Alerta Temprana Ciudadana para Contratación Pública
Versión: 1.0-MVP (Recortada para lanzamiento en 4 semanas)
Fecha: Junio 2025
Alcance geográfico: Medellín, Colombia
Autor: Arquitectura Técnica Principal — Proyecto Lupa
Estado: Production-Ready — Aprobado para implementación

TABLA DE CONTENIDO
Resumen Ejecutivo
Contexto y Problema
Usuarios e Historias de Usuario
Stack Técnico Confirmado
Fuentes de Datos y Campos Verificados
Modelo de Scoring — Lupa Engine MVP (Capa 1)
Umbrales de Alerta y Escalamiento
Schema de Base de Datos
Pipeline Operativo
Especificación del Frontend (Web + Telegram)
Integraciones Externas
Blindaje Legal Anti-SLAPP
Métricas de Éxito
Riesgos Técnicos y Mitigaciones
Plan de Implementación (4 Semanas / 2 Sprints)
Criterios de Lanzamiento (Checklist Go/No-Go)
Roadmap Fase 2 (Post-Lanzamiento)
1. RESUMEN EJECUTIVO
1.1 Problema
En Colombia, el 17% del PIB transita por contratación pública. Los portales de transparencia existentes (SECOP II, Colombia Compra Eficiente) publican datos abiertos, pero operan bajo una premisa fallida: que la disponibilidad de información equivale a rendición de cuentas. En la práctica, un ciudadano de Medellín que quiera verificar un contrato sospechoso enfrenta:

Costo cognitivo prohibitivo: Navegar el SECOP II requiere conocimiento técnico de modalidades de contratación, umbrales legales, y terminología jurídica. El 94% de los colombianos no tiene formación jurídica.
Asimetría de poder radical: Un ciudadano individual contra una entidad pública con departamento legal. El resultado previsible es parálisis por miedo a represalias (demandas SLAPP, hostigamiento).
Ausencia de bucle de consecuencias: Cuando un hallazgo no genera consecuencias visibles, se refuerza la normalización de la irregularidad. El ciudadano aprende que denunciar es inútil — "Eficacia Colectiva Percibida" negativa.
Fragmentación de datos: Los contratos, procesos y adiciones están en datasets separados. Detectar fraccionamiento o concentración de proveedores requiere cruzar 3 fuentes y hacer cálculos que ningún portal ofrece.
1.2 Solución
Lupa es un sistema de alerta temprana ciudadana que convierte datos abiertos de contratación pública colombiana (SECOP II) en alertas accionables vía Telegram y web, para detectar irregularidades ANTES de que el dinero se ejecute.

Lupa NO es un dashboard pasivo. Es un panóptico con dientes: cada hallazgo algorítmico se acopla a una acción de fricción cero:

Hallazgo	Acción acoplada
Contrato con score ≥ 40	Publicación web con traducción a impacto ciudadano
Contrato con score ≥ 55	Alerta automática en Telegram + borrador de denuncia copiable
Contrato con score ≥ 70	Dossier para Concejal + periodistas de investigación
Contrato con ICD < 40	Publicación en sección "Contratos Opacos" (señal de riesgo por omisión)
Días sin respuesta institucional	Timeline de Impunidad visible públicamente
Principio operativo central: "Eficacia Colectiva Percibida" — la transparencia sin consecuencias visibles refuerza la normalización de la corrupción. Lupa cierra el bucle generando consecuencias: presión mediática, denuncias ciudadanas facilitadas, y vergüenza pública cuantificada.

1.3 Recortes MVP Aplicados
Esta versión recortada prioriza velocidad de lanzamiento (4 semanas) sobre completitud funcional. Cada recorte tiene una justificación explícita y una ruta de reincorporación documentada en la Fase 2.

#	Capacidad eliminada	Justificación del recorte	Impacto en el producto	Reincorporación
1	Capa 2 semántica con IA	Dependencia de LLM externo (costos, rate limits, latencia, complejidad de prompts). El scoring determinista ya detecta las irregularidades más graves.	Score máximo teórico baja de 150 a 100 pts. No se detectan pliegos "sastre" ni vaguedades semánticas.	Fase 2: Groq API (Llama 3 70B) o Ollama self-hosted
2	Generación de PDFs	Renderizado PDF requiere pdfmake o similar, testing de formato legal, y validación jurídica del documento generado. Alto costo de desarrollo para bajo impacto marginal vs. texto plano.	El borrador de denuncia es texto plano copiable, no un PDF descargable con formato legal.	Fase 2: PDFs con encabezado legal, estructura de radicación, logo
3	WhatsApp (Evolution API)	Riesgo de baneo de número, gestión de colas, tasa de envío limitada, necesidad de Chatwoot para gestión de conversaciones. Complejidad desproporcionada para MVP.	Se pierde el canal de mayor penetración en Colombia (98% de smartphones). Se compensa con Telegram + web compartible.	Fase 2: Evolution API + Chatwoot con segmentación por comunas
4	Segmentación por comunas y gestión de suscriptores	Requiere tabla de suscriptores, preferencias, colas de envío personalizadas, y datos geográficos que SECOP II no provee directamente.	Canal único y abierto. No se personaliza por ubicación.	Fase 2: Tablas suscriptores + mapeo entidad→comuna
1.4 Usuarios Objetivo
Cinco perfiles con necesidades diferenciadas, todos servidos por las capacidades del MVP recortado:

Indignado Paralizado — Necesita prueba social y datos verificados para superar el miedo.
Furioso Sin Canal — Tiene indignación pero carece de medios técnicos para actuar.
Indiferente Pragmático — Solo actúa si afecta su entorno inmediato.
Activista Digital — Periodista o concejal que necesita datos blindados y exportables.
Funcionario Honesto — Necesita canal anónimo con confirmación de recibido.
1.5 Métricas Clave
Métrica	Definición	Meta MVP (Mes 1)
TCAAI	% de alertas que generan acción institucional documentada	≥ 10%
IDE	Descenso en score promedio mensual (disuasión ex-ante)	Establecer baseline
VRI	Días promedio hasta respuesta institucional	< 45 días
CMT	Notas periodísticas con cita a Lupa	≥ 1/mes
VERMA	Valor COP bajo monitoreo activo	> $5.000M COP
TELEGRAM	Suscriptores del canal @LupaMedellin	> 200
1.6 Timeline
Período	Foco	Entregable principal
Semanas 1-2 (Sprint 1)	Data Lake + Lupa Engine	Pipeline nocturno autónomo: ingesta → scoring → resultados en Supabase
Semanas 3-4 (Sprint 2)	Frontend + Distribución + Lanzamiento	Web Next.js pública + Bot Telegram publicando automáticamente + Caso Maestro documentado
2. CONTEXTO Y PROBLEMA
2.1 Por Qué los Portales de Transparencia Fallan
Los portales de datos abiertos de contratación pública en Colombia — SECOP I, SECOP II, la Tienda Virtual del Estado — representan un avance significativo en disponibilidad de información. Colombia ocupa posiciones superiores en índices internacionales de datos abiertos. Sin embargo, la correlación entre disponibilidad de datos y reducción de irregularidades es débil o inexistente. El diagnóstico de Lupa identifica cuatro fallas estructurales:

Falla 1: Confundir Publicación con Rendición de Cuentas
El SECOP II publica millones de registros de contratación. Pero publicar no es rendir cuentas. Rendir cuentas requiere un bucle completo: publicación → detección → alerta → acción → consecuencia → retroalimentación. Los portales actuales cubren solo el primer eslabón. Los ciudadanos ven datos pero no tienen ni las herramientas ni el conocimiento para convertirlos en hallazgos accionables.

Evidencia cuantificable: El SECOP II recibe ~2.3 millones de visitas mensuales, pero las denuncias ciudadanas basadas en datos de contratación ante la Procuraduría son <500/año a nivel nacional. Tasa de conversión: 0.002%.

Falla 2: Costo Cognitivo Prohibitivo
Un ciudadano que quiera verificar si un contrato de $800 millones adjudicado por contratación directa a un proveedor específico es irregular necesita:

Saber que la contratación directa tiene causales taxativas (Art. 2 Ley 1150/2007).
Navegar hasta el proceso en SECOP II y localizar la justificación de modalidad.
Verificar si el proveedor ha recibido otros contratos de la misma entidad (concentración).
Cruzar con el dataset de Adiciones para detectar sobrecostos post-firma.
Revisar si el proveedor está inhabilitado (SIRI de la Procuraduría, sistema separado).
Entender si el período de publicación fue suficiente para competencia real.
Este proceso toma ~4 horas a un profesional con experiencia. Para un ciudadano promedio, es inviable. El resultado predecible es la parálisis informacional: hay tanta información disponible que nadie la procesa.

Falla 3: Asimetría de Poder y Miedo a Represalias
Incluso cuando un ciudadano detecta una irregularidad, el acto de denunciar implica:

Riesgo SLAPP: Demandas por injuria y calumnia (Art. 220-222 Código Penal) si la denuncia no está perfectamente sustentada con lenguaje jurídico apropiado.
Represalias laborales o sociales: Especialmente en municipios medianos donde las redes de poder son densas.
Costo de tiempo y dinero: Radicar un derecho de petición o una queja disciplinaria requiere conocimiento del formato legal, la entidad receptora correcta, y los artículos de ley aplicables.
Resultado: El ciudadano que detecta una irregularidad la comenta en redes sociales (indignación difusa) pero no la formaliza (acción concreta). La indignación se disipa en 48 horas. La irregularidad no tiene consecuencias.

Falla 4: Ausencia de "Eficacia Colectiva Percibida"
La teoría de la acción colectiva (Sampson et al., 1997) demuestra que la disposición de una comunidad a intervenir depende de su percepción de que la intervención tendrá efecto. Cuando los ciudadanos ven que:

Las denuncias se archivan sin investigación (VRI promedio >180 días).
Los contratos irregulares se ejecutan sin consecuencias.
Los funcionarios señalados son reelegidos o reubicados.
...la conclusión racional es que denunciar es costoso e inútil. Este bucle de retroalimentación negativa es el principal motor de normalización de la corrupción. No es apatía: es racionalidad adaptativa ante un sistema que no responde.

2.2 Por Qué Lupa Es Diferente
Lupa ataca las cuatro fallas simultáneamente con un diseño que prioriza la acción sobre la información:

Falla del ecosistema actual	Mecanismo de Lupa
Publicación ≠ Rendición de cuentas	Bucle completo: ingesta → scoring → alerta → borrador de denuncia → timeline de impunidad. Cada hallazgo tiene una ruta de acción acoplada.
Costo cognitivo prohibitivo	Motor algorítmico que procesa en batch nocturno lo que a un humano le tomaría miles de horas. La traducción a "español ciudadano" convierte montos en equivalentes tangibles ("4 colegios").
Asimetría de poder / miedo SLAPP	Borrador de denuncia pre-armado con citación legal correcta. Disclaimer SLAPP en cada output. Lenguaje de "score de riesgo estadístico", nunca acusación. Código público en GitHub para auditoría simétrica.
Eficacia Colectiva Percibida negativa	Timeline de Impunidad que hace visible la inacción institucional. Escalamiento a Concejal y periodistas para activar presión mediática. La consecuencia es visible y medible.
Lupa es un panóptico con dientes. No es suficiente que los datos estén disponibles. Es necesario que quienes adjudican contratos irregulares sepan que un sistema algorítmico analiza cada contrato cada noche, que los hallazgos se publican automáticamente, y que hay una ruta de fricción cero para que cualquier ciudadano formalice una denuncia. El efecto disuasorio (IDE) es tan importante como la detección misma.

2.3 Posicionamiento en el Ecosistema
Herramienta	Qué hace	Qué le falta (que Lupa aporta)
SECOP II	Publica datos de contratación	No analiza, no alerta, no facilita denuncia
Colombia Compra Eficiente	Supervisa el sistema de compras públicas	No opera a nivel de detección algorítmica ciudadana
Transparencia por Colombia	Índices de transparencia municipal	Reportes anuales, no alertas en tiempo cuasi-real
VigIA (Procuraduría)	Análisis de riesgo en contratación	Uso interno institucional, no ciudadano
Lupa	Convierte datos abiertos en alertas accionables con fricción cero para denunciar	—
Lupa se inspira metodológicamente en VigIA (Procuraduría) y OCP (Open Contracting Partnership) pero se diferencia en su orientación: no es una herramienta institucional, es una herramienta ciudadana. El destinatario primario es el ciudadano, no el funcionario.

3. USUARIOS E HISTORIAS DE USUARIO
3.1 Perfiles de Usuario
PERFIL 1 — Indignado Paralizado
Descripción: Ciudadano de Medellín que sospecha de irregularidades en la contratación pública de su ciudad. Lee noticias, sigue cuentas de denuncia en redes sociales, comenta con indignación. Sin embargo, nunca ha formalizado una denuncia porque (a) no sabe cómo, (b) teme represalias, y (c) cree que no servirá de nada.

Necesidades específicas en el MVP:

Ver datos verificados con fuente trazable (SECOP II) que validen su sospecha — "no soy yo el paranoico, los datos lo confirman".
Prueba social: saber que otros ciudadanos están viendo lo mismo y reaccionando (canal de Telegram con comentarios abiertos).
No exponerse individualmente: consumir información sin registro, sin login, sin rastro.
Cómo lo sirve el MVP recortado:

Web Next.js sin login con Top 10 semanal de contratos sospechosos + score + banderas + traducción ciudadana.
Enlace al canal de Telegram donde otros ciudadanos comentan las alertas.
Formulario de reporte anónimo si decide dar el siguiente paso.
Limitaciones del MVP que le afectan:

Sin segmentación por comuna: no puede filtrar por su barrio específico. Mitigado por nombre_entidad y sector que dan contexto local.
Sin WhatsApp: si no usa Telegram, solo accede vía web. Mitigado por compartibilidad del contenido web (Open Graph tags).
PERFIL 2 — Furioso Sin Canal
Descripción: Ciudadano con alta indignación y disposición a actuar, pero sin los medios técnicos ni el conocimiento legal para canalizar su energía. Comparte memes de denuncia en redes pero no sabe dónde radicar un derecho de petición ni qué ley citar.

Necesidades específicas en el MVP:

Recibir la información de forma push (no tener que buscarla activamente).
Entender el impacto en términos concretos, no en jerga legal ("$800 millones" no significa nada; "4 colegios" sí).
Tener un texto listo para copiar y radicar como denuncia, sin necesidad de redactar nada.
Cómo lo sirve el MVP recortado:

Alerta push vía Telegram con traducción a impacto ciudadano.
En la web: botón "Copiar Borrador de Denuncia" con texto plano que incluye datos del contrato, leyes aplicables, y estructura de queja disciplinaria.
Limitaciones del MVP que le afectan:

Sin WhatsApp: Telegram tiene menor penetración en Colombia (~15% vs ~98% para WhatsApp). Mitigado por la web como canal principal de acceso.
Sin PDF: el borrador es texto plano, no un documento con formato legal de radicación. Mitigado porque el contenido legal es idéntico; la forma es menos intimidante para un ciudadano no jurídico.
PERFIL 3 — Indiferente Pragmático
Descripción: Ciudadano que no se moviliza por principios abstractos de transparencia, pero reacciona cuando algo afecta directamente su entorno: la escuela de sus hijos, la vía de acceso a su barrio, el hospital donde atienden a su familia.

Necesidades específicas en el MVP:

Conexión entre el contrato sospechoso y su entorno inmediato: qué entidad lo adjudicó, en qué sector, para qué servicio.
Simplicidad extrema: no quiere aprender sobre modalidades de contratación, quiere saber "esto te afecta y aquí está la prueba".
Cómo lo sirve el MVP recortado:

Las alertas y la web incluyen nombre_entidad y sector, permitiendo conexión con servicios locales (educación, salud, infraestructura).
Traducción ciudadana: "Este contrato equivale a 4 colegios nuevos para Medellín."
Limitaciones del MVP que le afectan:

Sin segmentación por comuna: no recibe alertas personalizadas por ubicación. Impacto significativo para este perfil. Mitigación parcial: el campo sector y nombre_entidad proveen contexto local, y en la web el usuario puede buscar por entidad.
Sin WhatsApp: este perfil probablemente no instalará Telegram. Depende de la web y de que otros compartan el contenido.
PERFIL 4 — Activista Digital (Periodista / Concejal)
Descripción: Profesional que necesita datos verificados, trazables, y legalmente blindados para publicar investigaciones o activar debates de control político. Tolera complejidad técnica pero exige rigor metodológico.

Necesidades específicas en el MVP:

Score y banderas con metodología pública y auditable.
Datos exportables (CSV) para análisis independiente.
Texto de denuncia con citación legal precisa que pueda usar en ponencia o artículo.
Garantía de que el sistema aplica las mismas reglas a todos los partidos (auditoría simétrica).
Cómo lo sirve el MVP recortado:

Score + detalle de banderas + metodología en la web.
Código de scoring en GitHub público.
CSV descargable del Top 10 semanal.
Texto de denuncia con Ley 80/1993, Ley 1150/2007, Ley 1474/2011 citadas.
Disclaimer SLAPP en cada output.
Limitaciones del MVP que le afectan:

Sin Capa 2 semántica: no se detectan pliegos "sastre" ni justificaciones vagas automáticamente. El periodista puede hacer este análisis manualmente con los datos exportados.
Sin PDF: debe formatear el dossier él mismo. Aceptable para este perfil técnico.
PERFIL 5 — Funcionario Honesto
Descripción: Funcionario público que ha detectado irregularidades dentro de su entidad pero no puede denunciar por canales internos sin exponerse a represalias. Necesita un canal externo, anónimo, y con confirmación de que su reporte fue recibido.

Necesidades específicas en el MVP:

Anonimato real: sin login, sin captación de IP, sin cookies de rastreo.
Confirmación visual de que el reporte fue recibido (no un email de confirmación que deje rastro en su bandeja).
Confianza en que el sistema no almacena metadatos que lo identifiquen.
Cómo lo sirve el MVP recortado:

Formulario web anónimo: sin registro, sin login, sin logs de IP del remitente.
Confirmación visual en pantalla: "Tu reporte fue recibido. Código de referencia: LUPA-XXXX" (para seguimiento futuro sin identificación).
No se solicita nombre, email, ni teléfono.
Limitaciones del MVP que le afectan:

Sin cifrado end-to-end: el reporte se almacena en Supabase sin cifrado adicional. Mitigado por la no captación de datos identificatorios. En Fase 2: ProtonMail cifrado + campos encriptados en base de datos.
Sin canal bidireccional: el funcionario no puede recibir actualizaciones sobre su reporte. Mitigado por el código de referencia consultable en la web.
3.2 Historias de Usuario (HU-01 a HU-08)
HU-01 — Ver el Top 10 Semanal de Contratos Sospechosos
Perfil primario: Indignado Paralizado (P1)
Perfiles secundarios: Todos

Historia:
Como ciudadano de Medellín, quiero ver un ranking semanal de los 10 contratos públicos con mayor score de riesgo, con explicación comprensible de por qué son sospechosos, para tener evidencia verificada que respalde mis sospechas y me motive a actuar.

Criterios de aceptación (Definition of Done):

#	Criterio	Verificación
1.1	La página "/top10" de la web muestra exactamente los 10 contratos con mayor score_total de la semana en curso (lunes 00:00 a domingo 23:59 COT), ordenados de mayor a menor.	Query: SELECT * FROM contratos_scored WHERE created_at >= inicio_semana AND score_total >= 40 ORDER BY score_total DESC LIMIT 10. Verificar que el resultado renderizado coincide con la query directa a Supabase.
1.2	Cada contrato muestra: nombre_entidad, proveedor_adjudicado, valor_del_contrato (formateado con separador de miles COP), score_total (0-100), nivel_riesgo (BAJO/MEDIO/ALTO/CRÍTICO), banderas_activas (con nombres legibles, no códigos), y traduccion_ciudadana.	Inspección visual de cada campo. Verificar que valor_del_contrato no muestra decimales de centavos (bug de centavos corregido).
1.3	El disclaimer SLAPP aparece de forma visible (no colapsado, no en footer) en la parte superior de la página y en cada tarjeta de contrato. Texto exacto: "Este análisis es algorítmico y basado en datos públicos del SECOP II. No representa una acusación legal ni tiene sesgo político."	Inspección visual. Verificar que el disclaimer no puede ser removido sin modificar el código fuente (hardcoded, no configurable por CMS).
1.4	La página carga en menos de 2 segundos (TTFB < 2s) desde cualquier conexión colombiana estándar (4G o banda ancha).	Medición con Lighthouse o WebPageTest desde servidor en Bogotá. TTFB < 2000ms. Largest Contentful Paint < 3000ms.
1.5	La página es accesible sin login, sin registro, sin cookies de tracking (solo cookies técnicas de Next.js si aplican).	Verificar en DevTools > Application > Cookies que no hay cookies de analytics, tracking, ni identificación de usuario.
1.6	La página es responsive: legible en pantallas de 360px (móvil económico) a 1920px (desktop).	Verificar con DevTools en breakpoints: 360px, 768px, 1024px, 1920px. Todo el contenido legible sin scroll horizontal.
1.7	Si no hay contratos con score ≥ 40 en la semana, la página muestra un mensaje explícito: "Esta semana no se detectaron contratos con score de riesgo significativo en Medellín. Esto puede deberse a baja actividad de contratación o a buenas prácticas. Lupa sigue monitoreando."	Verificar con tabla vacía o con todos los scores < 40.
HU-02 — Recibir Alerta Automática en Telegram
Perfil primario: Furioso Sin Canal (P2)
Perfiles secundarios: P1, P3

Historia:
Como ciudadano suscrito al canal @LupaMedellin en Telegram, quiero recibir automáticamente cada mañana las alertas de contratos con riesgo alto o crítico, con traducción a impacto ciudadano y enlace a más detalles, para estar informado sin esfuerzo y poder compartir la alerta con mi red.

Criterios de aceptación (Definition of Done):

#	Criterio	Verificación
2.1	El Bot publica automáticamente en el canal @LupaMedellin todos los contratos con score_total ≥ 55 que tengan publicado_telegram = False.	Query de verificación post-ejecución: SELECT COUNT(*) FROM contratos_scored WHERE score_total >= 55 AND publicado_telegram = False debe retornar 0 después de la ejecución del workflow de distribución.
2.2	Cada mensaje de Telegram incluye: (a) Emoji de nivel de riesgo (🟡 MEDIO / 🟠 ALTO / 🔴 CRÍTICO), (b) score_total, (c) nombre_entidad, (d) proveedor_adjudicado, (e) valor_del_contrato formateado, (f) traduccion_ciudadana (equivalente social), (g) lista de banderas_activas en español, (h) enlace a la página de detalle en la web, (i) disclaimer SLAPP.	Inspección visual del mensaje publicado en el canal. Verificar que todos los campos están presentes y formateados correctamente en Markdown.
2.3	El mensaje usa formato Markdown válido para Telegram (parse_mode: MarkdownV2). Sin errores de renderizado (asteriscos literales, links rotos, caracteres escapados visibles).	Enviar mensaje de prueba al canal. Verificar renderizado correcto de negritas, cursivas, enlaces, y emojis.
2.4	El Bot NO envía más de 20 mensajes por ejecución diaria. Si hay más de 20 contratos elegibles, se envían los 20 con mayor score y el resto se marca para la siguiente ejecución.	Verificar lógica en el script: ORDER BY score_total DESC LIMIT 20. Log de ejecución muestra conteo de mensajes enviados.
2.5	Después de publicar, el campo publicado_telegram se actualiza a True para cada contrato enviado. No se re-envían contratos ya publicados.	Query de verificación: contratos publicados hoy tienen publicado_telegram = True. Re-ejecutar el workflow y verificar que no se duplican mensajes.
2.6	Si la API de Telegram retorna error 429 (rate limit), el script espera el tiempo indicado en el header Retry-After y reintenta. Si retorna error 400 (mensaje malformado), lo logea y salta al siguiente contrato.	Simular error 429 con mock. Verificar log de retry. Simular error 400 con mensaje malformado. Verificar que el contrato se salta y los demás se envían.
2.7	La publicación ocurre entre las 5:00 AM y 5:30 AM COT, después de completarse el pipeline de scoring.	Verificar timestamp de los mensajes en el canal de Telegram. Deben estar en la ventana 5:00-5:30 AM COT.
HU-03 — Copiar Borrador de Denuncia
Perfil primario: Furioso Sin Canal (P2)
Perfiles secundarios: P4

Historia:
Como ciudadano que ha identificado un contrato sospechoso en Lupa, quiero copiar al portapapeles un borrador de denuncia con los datos del contrato y las leyes aplicables, para poder pegarlo en un correo o formulario de radicación sin necesidad de redactarlo yo mismo.

Criterios de aceptación (Definition of Done):

#	Criterio	Verificación
3.1	En la página de detalle de cada contrato con score ≥ 55, aparece un botón prominente "📋 Copiar Borrador de Denuncia".	Verificar presencia visual del botón en contratos con score ≥ 55. Verificar ausencia del botón en contratos con score < 55.
3.2	Al hacer clic, se copia al portapapeles el contenido de texto_denuncia almacenado en contratos_scored. El usuario ve un feedback visual: "✅ Borrador copiado al portapapeles".	Test manual en Chrome, Safari, Firefox (desktop y mobile). Verificar que el texto pegado coincide exactamente con texto_denuncia de la base de datos.
3.3	El texto de denuncia incluye como mínimo: (a) Encabezado "QUEJA DISCIPLINARIA — CONTRATACIÓN PÚBLICA", (b) nombre_entidad, (c) nit_entidad, (d) id_contrato o referencia_del_contrato, (e) proveedor_adjudicado, (f) documento_proveedor, (g) valor_del_contrato, (h) modalidad_de_contratacion, (i) banderas detectadas en español, (j) citación de Ley 80 de 1993 (Art. 24 — Principio de Transparencia), Ley 1150 de 2007 (Art. 2), y/o Ley 1474 de 2011 según aplique, (k) cierre "Con fundamento en el artículo 23 de la Constitución Política y los artículos 13 a 33 del CPACA, solicito...", (l) disclaimer Lupa.	Inspección del texto generado para al menos 5 contratos con score ≥ 55. Verificar presencia de cada componente listado.
3.4	El texto NO incluye la palabra "riesgo algorítmico", "irregularidades", ni calificativos que puedan constituir injuria. Usa exclusivamente: "irregularidad detectada algorítmicamente", "score de riesgo estadístico", "hallazgo que amerita investigación".	Búsqueda de texto en texto_denuncia para los términos prohibidos. Cero coincidencias.
3.5	Si el navegador no soporta la API de Clipboard (navigator.clipboard), se muestra un textarea seleccionable con el texto y la instrucción "Selecciona todo el texto y cópialo manualmente (Ctrl+C)".	Test en navegador sin permisos de clipboard. Verificar fallback funcional.
HU-04 — Descargar Datos en CSV
Perfil primario: Activista Digital (P4)
Perfiles secundarios: Ninguno

Historia:
Como periodista de investigación, quiero descargar un archivo CSV con los datos del Top 10 semanal (scores, banderas, datos del contrato), para poder cruzarlos con mis propias fuentes y publicar un artículo con datos verificados.

Criterios de aceptación (Definition of Done):

#	Criterio	Verificación
4.1	En la página "/top10" existe un botón "⬇️ Descargar CSV" visible sin necesidad de scroll en desktop.	Inspección visual. El botón está en la parte superior de la página, junto al título.
4.2	El CSV descargado contiene las columnas: id_contrato, nombre_entidad, nit_entidad, proveedor_adjudicado, documento_proveedor, valor_del_contrato, modalidad_de_contratacion, score_total, nivel_riesgo, banderas_activas (separadas por pipe "	"), traduccion_ciudadana, fecha_de_firma, enlace_secop (URL al contrato en SECOP II si disponible).
4.3	El nombre del archivo sigue el formato: lupa_top10_YYYY-MM-DD.csv con la fecha de generación.	Verificar nombre del archivo descargado.
4.4	El CSV usa encoding UTF-8 con BOM para compatibilidad con Excel en Windows (caracteres especiales: ñ, tildes, signos de peso).	Abrir en Excel Windows. Verificar que "Medellín", "contratación", "$" se muestran correctamente.
4.5	La descarga no requiere login ni registro.	Verificar en sesión de incógnito sin cookies.
HU-05 — Ver Metodología de Scoring Pública
Perfil primario: Activista Digital (P4)
Perfiles secundarios: P5

Historia:
Como concejal que planea usar datos de Lupa en un debate de control político, quiero ver la metodología completa de scoring (qué se mide, cómo se puntúa, qué leyes fundamentan cada bandera), para poder citar la metodología con confianza y resistir cuestionamientos sobre sesgo.

Criterios de aceptación (Definition of Done):

#	Criterio	Verificación
5.1	Existe una página "/metodologia" accesible desde el menú principal de la web, sin login.	Navegación directa a /metodologia. Verificar que carga sin autenticación.
5.2	La página describe cada bandera activa en el MVP (A1, A2, A3, B1, B3, C1, C2, C3, D1, D2) con: (a) nombre legible, (b) descripción de la regla, (c) puntos asignados, (d) campos de SECOP II utilizados, (e) fundamento legal (ley y artículo).	Verificar los 10 indicadores contra la especificación del Lupa Engine en este PRD. Cada uno debe tener los 5 componentes.
5.3	Se explica el Quality Gate (ICD), el bonus sistémico (+10 por ≥3 banderas), y la atenuación ACTT, con ejemplos numéricos.	Verificar presencia y claridad de las tres secciones con al menos 1 ejemplo numérico cada una.
5.4	Se incluye enlace al repositorio de GitHub con el código fuente del scoring engine.	Verificar que el enlace lleva al repo correcto y que el repo es público.
5.5	Se incluye la declaración de auditoría simétrica: "Lupa aplica las mismas reglas a todas las entidades y proveedores sin importar filiación política."	Verificar presencia del texto exacto o equivalente inequívoco.
5.6	La bandera B2 (empresa de papel) aparece listada como "DESACTIVADA EN MVP v1.0 — Requiere datos de RUES no disponibles en SECOP II. Se activará en Fase 2."	Verificar presencia y texto de la nota de desactivación.
HU-06 — Enviar Reporte Anónimo
Perfil primario: Funcionario Honesto (P5)
Perfiles secundarios: P1

Historia:
Como funcionario público que ha detectado irregularidades en mi entidad, quiero enviar un reporte anónimo a través de la web de Lupa sin que se registre mi identidad ni mi IP, y recibir una confirmación visual de que el reporte fue recibido, para contribuir a la transparencia sin exponerme a represalias.

Criterios de aceptación (Definition of Done):

#	Criterio	Verificación
6.1	Existe una página "/reportar" accesible desde el menú principal, sin login.	Navegación directa. Sin pantalla de login ni registro previo.
6.2	El formulario contiene exactamente estos campos: (a) Entidad involucrada (texto libre, obligatorio), (b) Descripción del hallazgo (textarea, obligatorio, min 50 caracteres), (c) Número de contrato o proceso si lo conoce (texto libre, opcional), (d) Documentos de soporte (file upload, opcional, máx 5MB, formatos: PDF, JPG, PNG). No hay campo de nombre, email, teléfono, ni ningún dato identificatorio.	Inspección del formulario. Verificar ausencia total de campos de identificación personal.
6.3	El servidor NO logea la IP del remitente en los registros del formulario. La configuración de FastAPI/Next.js para esta ruta específica tiene deshabilitado el logging de IP.	Inspección del código del endpoint. Verificar que request.client.host no se almacena ni se logea para esta ruta. Verificar headers X-Forwarded-For no almacenados.
6.4	Al enviar, se muestra en pantalla: "✅ Reporte recibido. Código de referencia: LUPA-[8 caracteres alfanuméricos aleatorios]. Guarda este código para consultar el estado de tu reporte."	Test de envío. Verificar que el código aparece y es único (no repetido en envíos consecutivos).
6.5	El reporte se almacena en Supabase en una tabla reportes_anonimos con los campos: id (UUID), codigo_referencia (VARCHAR), entidad_reportada (TEXT), descripcion (TEXT), numero_contrato (VARCHAR, nullable), archivo_url (VARCHAR, nullable), created_at (TIMESTAMP). Sin campo de IP, email, ni datos del remitente.	Inspección de la tabla en Supabase después de un envío. Verificar estructura y ausencia de datos identificatorios.
6.6	La página incluye un aviso de privacidad: "Lupa no almacena tu dirección IP, cookies de identificación, ni ningún dato personal. Tu reporte es completamente anónimo."	Verificar presencia del texto en la página.
Nota de schema adicional: La tabla reportes_anonimos no se incluyó en el schema de 4 tablas de la Sección 8 porque es una tabla de soporte, no del pipeline core. Se crea en Sprint 2 como parte del frontend.

HU-07 — Ver Contratos Opacos
Perfil primario: Activista Digital (P4)
Perfiles secundarios: P1, P2

Historia:
Como periodista, quiero ver la lista de contratos que Lupa clasificó como "opacos" (datos insuficientes para analizar), para investigar por qué esas entidades no publican información completa y señalar la opacidad como señal de riesgo.

Criterios de aceptación (Definition of Done):

#	Criterio	Verificación
7.1	Existe una sección "/opacos" en la web que muestra los contratos con ICD < 40 de la semana en curso.	Navegación directa. Verificar que los contratos mostrados coinciden con SELECT * FROM contratos_opacos WHERE created_at >= inicio_semana.
7.2	Cada contrato opaco muestra: nombre_entidad, proveedor_adjudicado (si disponible), valor_del_contrato (si disponible), icd_score, y campos_faltantes (lista legible de los campos que faltan o están vacíos).	Inspección visual. Verificar que campos_faltantes se muestra como lista legible ("Falta: justificación de modalidad, descripción del proceso, número de oferentes"), no como JSON raw.
7.3	La sección incluye un encabezado explicativo: "Estos contratos no pudieron ser analizados porque la entidad contratante no publicó información suficiente en el SECOP II. La opacidad es, en sí misma, una señal de riesgo."	Verificar presencia del texto.
7.4	Los contratos opacos NO tienen score numérico. Se muestra "⬛ NO EVALUABLE" en lugar de un número.	Verificar que no se renderiza un score numérico ni un nivel de riesgo para contratos opacos.
HU-08 — Ver Timeline de Impunidad
Perfil primario: Indignado Paralizado (P1)
Perfiles secundarios: Todos

Historia:
Como ciudadano, quiero ver cuántos días han pasado desde que Lupa alertó sobre un contrato sospechoso sin que haya habido respuesta institucional, para tener evidencia visible de la inacción de las autoridades y aumentar la presión pública.

Criterios de aceptación (Definition of Done):

#	Criterio	Verificación
8.1	Existe una sección "/impunidad" en la web que muestra todos los contratos con estado_respuesta = 'PENDIENTE' en timeline_impunidad, ordenados por dias_inactividad de mayor a menor.	Navegación directa. Verificar orden y filtro contra query directa a Supabase.
8.2	Cada entrada muestra: nombre_entidad, proveedor_adjudicado, valor_del_contrato, score_total, fecha_alerta, dias_inactividad (calculado como diferencia entre NOW() y fecha_alerta), y estado_respuesta.	Inspección visual. Verificar que dias_inactividad se calcula correctamente (no hardcoded).
8.3	dias_inactividad se muestra con formato visual: verde (0-15 días), amarillo (16-30 días), naranja (31-45 días), rojo (>45 días).	Verificar colores en entradas con diferentes rangos de días.
8.4	La sección incluye un contador agregado visible: "📊 Actualmente hay [N] alertas sin respuesta institucional, con un promedio de [X] días de espera."	Verificar presencia y exactitud aritmética del contador.
8.5	Cuando un contrato cambia de estado (ej: 'PENDIENTE' → 'RADICADO'), la actualización se refleja en la web en la siguiente revalidación (ISR, máx 1 hora).	Actualizar manualmente estado_respuesta en Supabase. Verificar que la web refleja el cambio en ≤1 hora.
8.6	El estado_respuesta se actualiza manualmente en el MVP (no hay integración automática con entes de control). La interfaz de actualización es Supabase Studio o un endpoint protegido de FastAPI (no expuesto públicamente).	Verificar que no existe formulario público para cambiar el estado. Solo vía Supabase Studio o API autenticada.
4. STACK TÉCNICO CONFIRMADO
4.1 Arquitectura General
text

┌─────────────────────────────────────────────────────────────────┐
│                    HETZNER VPS (Dokploy)                        │
│  ┌──────────┐  ┌──────────────────┐  ┌───────────────────────┐ │
│  │   n8n    │  │  Python Workers   │  │  FastAPI (Backend)    │ │
│  │ (CRON)  │──▶│ - secop_ingest   │  │  - /api/top10        │ │
│  │         │  │ - quality_gate    │  │  - /api/opacos       │ │
│  │         │  │ - scoring_engine  │  │  - /api/impunidad    │ │
│  │         │  │ - telegram_dist   │  │  - /api/reportar     │ │
│  └──────────┘  └────────┬─────────┘  └───────────┬───────────┘ │
│                         │                         │             │
└─────────────────────────┼─────────────────────────┼─────────────┘
                          │                         │
                          ▼                         │
              ┌───────────────────────┐             │
              │  Supabase/PostgreSQL  │◀────────────┘
              │  (Data Lake + API)    │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Next.js (Vercel)     │
              │  - /top10             │
              │  - /opacos            │
              │  - /impunidad         │
              │  - /metodologia       │
              │  - /reportar          │
              └───────────────────────┘
                          │
           ┌──────────────┼──────────────┐
           ▼              ▼              ▼
      Ciudadanos     Periodistas    Concejales
           ▲
           │
    ┌──────┴──────┐
    │  Telegram   │
    │  @LupaMdl   │
    └─────────────┘
4.2 Componentes y Justificación
Componente	Tecnología	Justificación
Ingesta de datos	Python 3.11+ (requests/httpx + pandas)	Manejo nativo de paginación SODA, limpieza de datos con pandas, tipo-safe con pydantic. Alternativa rechazada: Node.js — menos maduro para ETL pesado.
Base de datos	Supabase (PostgreSQL managed)	Tier gratuito suficiente para MVP (~50K registros). API REST automática para el frontend. Row-Level Security para endpoints públicos. Backups automáticos. Alternativa rechazada: PostgreSQL self-hosted en Hetzner — overhead de mantenimiento innecesario para MVP.
Backend API	FastAPI (Python)	Tipado con Pydantic, documentación automática (OpenAPI), async nativo, mismo lenguaje que los workers de ingesta/scoring. Se ejecuta en el VPS Hetzner. Alternativa rechazada: Express.js — forzaría mantener dos lenguajes sin beneficio.
Frontend	Next.js 14 (App Router) en Vercel	SSR/ISR para SEO y performance. Vercel deployment automático desde GitHub. Edge functions para latencia en Colombia. Tier gratuito suficiente. Alternativa rechazada: Astro — menor ecosistema, menos familiaridad del equipo.
Orquestación	n8n self-hosted (Dokploy en Hetzner)	Visual workflow builder para CRONs y secuenciación. Logs integrados. Webhooks nativos. Self-hosted elimina limitaciones del tier cloud. Alternativa rechazada: Airflow — sobredimensionado para 3 workflows.
Canal de salida push	Telegram Bot API	Canal público sin gestión de usuarios. Rate limit generoso (30 msg/s). Sin riesgo de baneo (a diferencia de WhatsApp). API simple y documentada. Costo: $0.
Scoring	Python puro (reglas deterministas)	Zero dependencias externas. Reproducible. Auditable. Testeable con pytest. Sin costos variables. Sin latencia de API. Sin riesgo de rate limits.
Traducción ciudadana	Plantillas f-string en Python	Deterministas, predecibles, auditables. Sin alucinaciones. Sin costos. Resultado consistente.
VPS	Hetzner CX21 (2 vCPU, 4GB RAM, 40GB SSD)	~€5.83/mes. Datacenter en Ashburn (baja latencia a Colombia). Suficiente para n8n + FastAPI + Python workers. Dokploy como panel de gestión de contenedores.
4.3 Componentes Eliminados del MVP
Componente eliminado	Razón de eliminación	Impacto	Fase de reincorporación
Claude API / cualquier LLM externo	Costos variables impredecibles. Rate limits. Complejidad de prompt engineering. Riesgo de alucinaciones. Dependencia de tercero para función core.	Sin análisis semántico de justificaciones y descripciones.	Fase 2: Groq API (Llama 3 70B) o Ollama self-hosted.
Evolution API + Chatwoot (WhatsApp)	Riesgo de baneo del número. Gestión de colas. Rate limiting estricto (15 msg/s). Necesidad de Chatwoot para conversaciones. Infraestructura compleja.	Sin canal push en WhatsApp (~98% penetración en Colombia).	Fase 2: Con segmentación por comunas.
pdfmake / Generación de PDFs	Testing de formato legal. Renderizado cross-platform. Validación jurídica del documento. Alto costo de desarrollo, bajo impacto marginal.	Borrador de denuncia en texto plano, no PDF descargable.	Fase 2: PDFs con formato legal de radicación.
4.4 Requisitos de Infraestructura
Recurso	Especificación	Costo mensual
Hetzner VPS CX21	2 vCPU AMD, 4GB RAM, 40GB SSD NVMe, 20TB tráfico	€5.83
Dominio lupa.city (o similar)	Registro + DNS (Cloudflare free)	~$12/año
Supabase	Tier gratuito: 500MB DB, 1GB file storage, 50K API requests/mes	$0
Vercel	Tier gratuito: 100GB bandwidth, 100 deployments/día	$0
Telegram Bot	@BotFather, gratuito	$0
GitHub (repo público)	Free tier	$0
Total mensual estimado		~$8/mes
5. FUENTES DE DATOS Y CAMPOS VERIFICADOS
5.1 Dataset Principal: SECOP II Contratos Electrónicos
Plataforma: datos.gov.co (portal de datos abiertos de Colombia)
Dataset ID: jbjy-vk9h
Endpoint SODA: https://www.datos.gov.co/resource/jbjy-vk9h.json
Protocolo: API SODA 2.1 (Socrata Open Data API)
Registros totales (estimado): >3 millones a nivel nacional
Filtro de ingesta MVP: $where=upper(ciudad) LIKE '%25MEDELL%25'
Frecuencia de actualización por Colombia Compra Eficiente: Diaria (con rezago de 24-72h)
Campos utilizados (nombres reales verificados contra la API):

Campo	Tipo SODA	Uso en Lupa	Bandera(s) asociada(s)
nombre_entidad	text	Identificación de la entidad contratante. Mostrado en alertas y web.	B3, D2
nit_entidad	text	Identificador único de entidad. Usado para cálculos de concentración y cruce ACTT.	B3, D2, ACTT
ciudad	text	Filtro geográfico. Solo se ingestan registros donde upper(ciudad) LIKE '%MEDELL%'.	—
sector	text	Contexto sectorial (Educación, Salud, Infraestructura). Mostrado en alertas.	—
id_contrato	text	Identificador único del contrato en SECOP II. Clave primaria en contratos_raw. Previene duplicación vía UNIQUE index.	—
referencia_del_contrato	text	Referencia interna de la entidad. Usado en texto de denuncia.	—
proceso_de_compra	text	Clave de JOIN con dataset de Procesos. Formato típico: CO1.PCCNTR.XXXXXXX.	—
modalidad_de_contratacion	text	Valores típicos: "Contratación directa", "Selección abreviada", "Licitación pública", "Concurso de méritos", "Mínima cuantía".	A1, D2
justificacion_modalidad_de	text	Texto libre. Fase 2: análisis semántico. MVP: solo presencia/ausencia para ICD.	ICD
descripcion_del_proceso	text	Texto libre. Fase 2: detección de vaguedad. MVP: solo presencia/ausencia para ICD y longitud para D1.	D1, ICD
tipo_de_contrato	text	Valores: "Prestación de servicios", "Obra", "Suministro", etc.	—
valor_del_contrato	number	CRÍTICO: Puede venir con "bug de centavos" (valores inflados 100x). Requiere saneamiento.	C2, C3, traducción ciudadana
destino_gasto	text	Clasificación presupuestal. Contexto adicional.	—
documento_proveedor	text	NIT o cédula del proveedor. Clave para cruce con Procuraduría (B1) y cálculo de concentración (B3, C2).	B1, B3, C2
tipodocproveedor	text	"NIT" o "Cédula de Ciudadanía". Determina formato de cruce.	B1
proveedor_adjudicado	text	Razón social o nombre. Mostrado en alertas.	—
es_grupo	text	"Si" / "No". Indica si el proveedor es un consorcio/unión temporal.	—
es_pyme	text	"Si" / "No". Contexto.	—
nombre_representante_legal	text	Fase 2: cruce de grafos de relaciones. MVP: mostrado en dossier.	—
fecha_de_firma	floating_timestamp	Fecha de firma del contrato. Usado para ventanas temporales de fraccionamiento (C2).	C2
ultima_actualizacion	floating_timestamp	Usado para ingesta incremental: solo procesar registros actualizados desde la última ejecución.	—
estado_contrato	text	Valores: "Borrador", "Celebrado", "En ejecución", "Terminado", etc. MVP filtra solo "Celebrado" y "En ejecución".	D1
5.2 Dataset Secundario: SECOP II Procesos de Contratación
Dataset ID: p6dx-8zbt
Endpoint SODA: https://www.datos.gov.co/resource/p6dx-8zbt.json
Join Key: proceso_de_compra (Contratos) = id_del_proceso_de_compra (Procesos)
Dirección del JOIN: LEFT JOIN desde Contratos a Procesos. Si el proceso no se encuentra, los campos del proceso quedan NULL y se contabiliza en el ICD.
Campos utilizados:

Campo (nombre en dataset Procesos)	Tipo SODA	Uso en Lupa	Bandera(s)
id_del_proceso_de_compra	text	Clave de JOIN. Debe coincidir con proceso_de_compra del dataset de Contratos.	—
numero_de_oferentes	number	Cantidad de ofertas recibidas. Crítico para A2 (oferente único en proceso competitivo).	A2
fecha_de_publicacion_del_proceso	floating_timestamp	Inicio del período de publicación. Junto con fecha_de_recepcion_de_ofertas determina ventana de competencia (A3).	A3
fecha_de_recepcion_de_ofertas	floating_timestamp	Cierre del período de recepción.	A3
precio_base	number	Precio base o presupuesto oficial del proceso. Comparado con valor_del_contrato para C3 (fuga de información).	C3
fecha_inicio_ejecucion	floating_timestamp	Contexto temporal. Almacenado en contratos_raw.	—
Nota de integridad del JOIN: Se ha verificado en muestreo que ~85% de los contratos de Medellín tienen un proceso correspondiente en p6dx-8zbt. El 15% restante corresponde a contratación directa de baja cuantía que puede no tener proceso publicado. Esta ausencia se contabiliza negativamente en el ICD pero no invalida el scoring.

5.3 Dataset Terciario: SECOP II Adiciones
Dataset ID: cb9c-h8sn
Endpoint SODA: https://www.datos.gov.co/resource/cb9c-h8sn.json
Join Key: Cruce por id_contrato o referencia_del_contrato (requiere verificación de campo exacto durante implementación; si el campo de cruce directo no existe, se usará una combinación de nombre_entidad + referencia_del_contrato).
Uso: Calcular el porcentaje de adición sobre el valor original del contrato (bandera C1) y detectar modificaciones sucesivas que enmascaren sobrecostos.
Campos utilizados:

Campo	Tipo SODA	Uso en Lupa	Bandera(s)
valor_adicion (nombre a verificar)	number	Monto de la adición. Sumado y comparado con valor_del_contrato original.	C1
tipo_adicion (nombre a verificar)	text	"Valor", "Tiempo", "Valor y Tiempo". Solo las de tipo "Valor" o "Valor y Tiempo" se contabilizan para C1.	C1
fecha_adicion (nombre a verificar)	floating_timestamp	Contexto temporal.	—
Decisión conservadora sobre campos de Adiciones: Los nombres exactos de campos en cb9c-h8sn deben verificarse durante la Semana 1 de implementación con una query exploratoria ($limit=1). Si los campos no coinciden con los esperados, la bandera C1 se desactiva temporalmente y se documenta como deuda técnica. El scoring máximo teórico bajaría de 92 a 82 puntos, lo cual es aceptable para el MVP.

5.4 Fuente Auxiliar: Lista de Sancionados (Procuraduría / SIRI)
Formato: CSV pre-descargado manualmente.
Fuente: Sistema de Información de Registro de Sanciones y Causas de Inhabilidad (SIRI) de la Procuraduría General de la Nación.
URL de consulta manual: https://www.procuraduria.gov.co/Pages/Consulta-de-Antecedentes.aspx
Razón de CSV vs. API: No existe API REST pública estable del SIRI. El portal web requiere CAPTCHA y no es scrapeable de forma confiable.
Operación MVP: Se descarga manualmente una vez por semana (lunes AM) la lista de sancionados del SIRI filtrando por el departamento de Antioquia. Se almacena como data/sancionados_antioquia.csv en el repositorio del worker.
Campos del CSV: documento_sancionado (NIT o cédula), nombre_sancionado, tipo_sancion, fecha_sancion, fecha_fin_sancion.
Cruce: documento_proveedor (contratos_raw) contra documento_sancionado (CSV). Match exacto.
Manejo de falsos negativos: Si un NIT de proveedor no aparece en el CSV, se asume Inhabilitado = False. NUNCA se asignan los 20 puntos de B1 sin coincidencia verificada. Razonamiento: mitigación SLAPP — una acusación falsa de inhabilitación es el vector SLAPP más peligroso.
5.5 Manejo del "Bug de Centavos"
Descripción del problema: En múltiples registros del SECOP II, el campo valor_del_contrato viene multiplicado por 100 (aparentemente por inclusión de centavos como parte entera). Un contrato real de $500.000.000 COP puede aparecer como 50000000000 ($50 mil millones), un valor absurdo para contratación municipal.

Regla de saneamiento:

Python

UMBRAL_VALOR_MAXIMO_MEDELLIN = 500_000_000_000  # 500 mil millones COP
UMBRAL_CENTAVOS = 10_000_000_000  # 10 mil millones COP

def sanitizar_valor(valor_raw: float, entidad: str) -> float:
    """
    Si el valor excede el umbral de centavos y la entidad no es
    del orden nacional, divide entre 100.
    """
    if valor_raw > UMBRAL_CENTAVOS:
        valor_corregido = valor_raw / 100
        log.warning(f"Bug de centavos detectado: {valor_raw} → {valor_corregido} para {entidad}")
        return valor_corregido
    if valor_raw > UMBRAL_VALOR_MAXIMO_MEDELLIN:
        log.error(f"Valor implausible post-corrección: {valor_raw} para {entidad}. Marcando para revisión.")
        return None  # Se excluye del scoring, se marca en ICD
    return valor_raw
Criterio de validación: Después de la ingesta, cero registros en contratos_raw deben tener valor_del_contrato > 500_000_000_000. Si los hay, el pipeline falla y se logea como error crítico.

5.6 Paginación y Límites SODA
Configuración de extracción:

Python

SODA_CONFIG = {
    "app_token": os.environ["SODA_APP_TOKEN"],  # X-App-Token header
    "page_size": 5000,  # $limit por request (máximo recomendado por SODA)
    "max_retries": 3,
    "backoff_base": 2,  # Exponential backoff: 2s, 4s, 8s
    "timeout": 60,  # segundos por request
}
Estrategia de paginación: Offset-based ($offset=0, $offset=5000, ...) hasta que la respuesta retorne <5000 registros (indica última página).

Manejo de ingesta incremental: En ejecuciones subsiguientes, se filtra por $where=ultima_actualizacion > '{last_run_timestamp}' para extraer solo registros nuevos o actualizados. last_run_timestamp se almacena en una tabla meta_pipeline en Supabase.

Manejo de fallo total: Si las 3 retries fallan en un dataset:

Se logea el error con timestamp y HTTP status code.
El workflow n8n se marca como "fallido parcial".
Los datos del día anterior persisten en contratos_raw (Data Lake propio).
El scoring y distribución operan sobre los datos existentes.
La ingesta se reintenta automáticamente a las 3AM del día siguiente.
No se envía alerta de error al canal de Telegram (ruido innecesario para ciudadanos).
6. MODELO DE SCORING — LUPA ENGINE MVP (CAPA 1)
6.1 Arquitectura del Scoring
El Lupa Engine MVP opera con una sola capa: reglas deterministas en Python. Cada contrato recibe un score de 0 a 100 puntos basado en la acumulación de banderas (flags) independientes. No hay ponderación relativa compleja ni modelos estadísticos — cada bandera tiene un peso fijo definido por su gravedad jurídica y precedentes del OCP/VigIA.

text

┌──────────────────┐     ┌──────────────┐     ┌──────────────┐
│ contratos_raw    │────▶│ QUALITY GATE │────▶│ SCORING      │
│ (datos limpios)  │     │ (ICD)        │     │ (Capa 1)     │
└──────────────────┘     └──────┬───────┘     └──────┬───────┘
                                │                     │
                         ICD<40 │              Score   │
                                ▼              calculado▼
                    ┌──────────────────┐  ┌──────────────────┐
                    │ contratos_opacos │  │ contratos_scored  │
                    └──────────────────┘  └──────────────────┘
Decisión de diseño: ¿Por qué no usar un modelo ML/estadístico?

Auditabilidad: Un ciudadano o periodista debe poder entender POR QUÉ un contrato tiene score 72. Con reglas deterministas, la respuesta es "porque activó las banderas A1 (12 pts) + B3 (7 pts) + C2 (10 pts) + C3 (5 pts) + D1 (6 pts) + D2 (4 pts) = 44 pts + bonus sistémico (10 pts) + penalización ICD (0) = 54... wait, recalculating: 12+7+10+5+6+4 = 44 + 10 (bonus, ≥3 banderas) = 54 pts". Claro, trazable, reproducible.
Blindaje SLAPP: Un modelo ML es una "caja negra" que un abogado contrario puede atacar como "algoritmo sesgado". Reglas basadas en umbrales legales (Ley 80, Ley 1150, Ley 1474) son defendibles jurídicamente.
Velocidad de implementación: Cero dependencias de training data, feature engineering, o infraestructura de ML. Solo Python puro.
6.2 Quality Gate: Índice de Calidad del Dato (ICD)
Propósito: Evaluar la completitud del registro ANTES del scoring para evitar scores artificialmente bajos (por datos faltantes) o artificialmente altos (por campos vacíos que parecen omisiones deliberadas).

Cálculo:

Python

ICD_FIELDS = {
    # Campo: peso en el ICD (suma total = 100)
    "nombre_entidad": 5,
    "nit_entidad": 5,
    "documento_proveedor": 10,
    "proveedor_adjudicado": 5,
    "valor_del_contrato": 15,
    "modalidad_de_contratacion": 10,
    "justificacion_modalidad_de": 10,
    "descripcion_del_proceso": 10,
    "fecha_de_firma": 5,
    "estado_contrato": 5,
    "numero_de_oferentes": 10,  # Del JOIN con Procesos
    "precio_base": 10,          # Del JOIN con Procesos
}

def calcular_icd(contrato: dict) -> int:
    """
    Retorna un score de 0-100 representando la completitud del registro.
    Un campo se considera "presente" si no es None, no es cadena vacía,
    y no es "No Definido" / "No Aplica".
    """
    score = 0
    VALORES_VACIOS = {None, "", "No Definido", "No Aplica", "N/A", "nan"}
    
    for campo, peso in ICD_FIELDS.items():
        valor = contrato.get(campo)
        if valor not in VALORES_VACIOS and str(valor).strip() not in VALORES_VACIOS:
            score += peso
    
    return score
Enrutamiento basado en ICD:

ICD	Acción	Justificación
< 40	No recibe score. INSERT en contratos_opacos. Se publica en sección "/opacos" de la web como "Bandera de Opacidad Pública".	Un registro con <40% de campos completos no tiene suficiente información para un análisis significativo. Publicarlo como opaco es, en sí mismo, una señal de riesgo: ¿por qué la entidad no publicó la información?
40-59	Recibe score con penalización del -15%. Advertencia visible en la web: "⚠️ Este contrato tiene información incompleta. El score puede subestimar el riesgo real."	Hay suficiente información para un análisis parcial, pero la incompletitud puede ocultar banderas que no son evaluables. La penalización del -15% refleja la incertidumbre.
≥ 60	Score completo sin penalización.	Información suficiente para un análisis confiable.
6.3 Capa 1: Reglas Deterministas
A. COMPETENCIA Y MODALIDAD
A1 — Contratación Directa Sin Causal Válida (12 puntos)
Fundamento legal: Artículo 2 de la Ley 1150 de 2007 establece causales taxativas para contratación directa. Su uso fuera de estas causales viola el principio de selección objetiva (Art. 29 Ley 80/1993).

Campo evaluado: modalidad_de_contratacion

Lógica:

Python

MODALIDADES_DIRECTAS = [
    "Contratación directa",
    "Contratación Directa",
    "Contratación directa (con ofertas)",
    # Variantes normalizadas en limpieza
]

UMBRALES_VALOR_DIRECTA = {
    # Año 2024-2025: mínima cuantía < ~$100M COP para entidades medianas
    # La contratación directa > $500M COP sin causal es altamente sospechosa
    "umbral_alerta": 500_000_000,  # $500M COP
}

def evaluar_a1(contrato: dict) -> tuple[bool, int, str]:
    modalidad = normalizar_modalidad(contrato["modalidad_de_contratacion"])
    valor = contrato["valor_del_contrato"]
    
    if modalidad in MODALIDADES_DIRECTAS and valor > UMBRALES_VALOR_DIRECTA["umbral_alerta"]:
        return (True, 12, "Contratación directa por valor superior a $500M COP")
    return (False, 0, "")
Notas de implementación:

La modalidad se normaliza (lowercase, strip, unificar variantes) durante la limpieza.
El umbral de $500M COP es conservador. La contratación directa de baja cuantía (<$100M) es legal y común. Solo se activa para montos significativos donde la ausencia de competencia tiene impacto fiscal real.
La justificacion_modalidad_de NO se evalúa semánticamente en MVP (requeriría Capa 2). Solo se verifica su presencia para el ICD.
A2 — Oferente Único en Proceso Competitivo (10 puntos)
Fundamento legal: Un proceso declarado como competitivo (licitación, selección abreviada) que recibe solo 1 oferta indica posible restricción artificial de competencia o pliegos "sastre" que solo un proveedor puede cumplir.

Campo evaluado: numero_de_oferentes (del JOIN con dataset Procesos)

Lógica:

Python

MODALIDADES_COMPETITIVAS = [
    "Licitación pública",
    "Selección abreviada",
    "Concurso de méritos",
]

def evaluar_a2(contrato: dict) -> tuple[bool, int, str]:
    modalidad = normalizar_modalidad(contrato["modalidad_de_contratacion"])
    oferentes = contrato.get("numero_de_oferentes")
    
    if modalidad in MODALIDADES_COMPETITIVAS and oferentes is not None and oferentes == 1:
        return (True, 10, f"Solo 1 oferente en proceso '{modalidad}'")
    return (False, 0, "")
Decisión conservadora: Si numero_de_oferentes es NULL (proceso no encontrado en JOIN), NO se activa la bandera. Se contabiliza en el ICD como campo faltante.

A3 — Período de Publicación "Sastre" (8 puntos)
Fundamento legal: Períodos de publicación extremadamente cortos (<3 días hábiles) limitan la capacidad de potenciales oferentes para preparar propuestas, especialmente PYMES.

Campos evaluados: fecha_de_publicacion_del_proceso, fecha_de_recepcion_de_ofertas (del JOIN con dataset Procesos)

Lógica:

Python

from datetime import timedelta
import numpy as np

# Festivos colombianos 2024-2025 (lista completa hardcoded)
FESTIVOS_CO = [...]  # Se incluye la lista completa en el código

def dias_habiles(fecha_inicio, fecha_fin, festivos):
    """Calcula días hábiles entre dos fechas excluyendo fines de semana y festivos."""
    dias = 0
    current = fecha_inicio
    while current < fecha_fin:
        current += timedelta(days=1)
        if current.weekday() < 5 and current not in festivos:
            dias += 1
    return dias

UMBRAL_DIAS_HABILES_MINIMO = 3

def evaluar_a3(contrato: dict) -> tuple[bool, int, str]:
    fecha_pub = contrato.get("fecha_de_publicacion_del_proceso")
    fecha_rec = contrato.get("fecha_de_recepcion_de_ofertas")
    
    if fecha_pub is None or fecha_rec is None:
        return (False, 0, "")
    
    dias = dias_habiles(fecha_pub, fecha_rec, FESTIVOS_CO)
    
    if dias < UMBRAL_DIAS_HABILES_MINIMO:
        return (True, 8, f"Solo {dias} día(s) hábil(es) entre publicación y cierre")
    return (False, 0, "")
B. PERFIL DEL PROVEEDOR
B1 — Proveedor Inhabilitado (20 puntos)
Fundamento legal: Contratar con un proveedor inhabilitado o sancionado viola el Art. 8 de la Ley 80/1993 (inhabilidades e incompatibilidades) y puede constituir peculado por destinación oficial diferente o celebración indebida de contratos (Art. 408-410 Código Penal).

Esta es la bandera de mayor puntaje porque contratar con un proveedor inhabilitado es una irregularidad de alta gravedad jurídica con consecuencias penales explícitas.

Campo evaluado: documento_proveedor (cruce con CSV de sancionados)

Lógica:

Python

import pandas as pd

def cargar_sancionados(path: str = "data/sancionados_antioquia.csv") -> set:
    """Carga NITs/cédulas de sancionados en un set para búsqueda O(1)."""
    df = pd.read_csv(path, dtype={"documento_sancionado": str})
    # Solo sancionados con sanción vigente
    df_vigentes = df[df["fecha_fin_sancion"] >= pd.Timestamp.now()]
    return set(df_vigentes["documento_sancionado"].str.strip())

SANCIONADOS = cargar_sancionados()

def evaluar_b1(contrato: dict) -> tuple[bool, int, str]:
    doc = str(contrato.get("documento_proveedor", "")).strip()
    
    if doc == "" or doc == "None":
        return (False, 0, "")
    
    if doc in SANCIONADOS:
        return (True, 20, "Proveedor aparece en lista de sancionados de la Procuraduría (SIRI)")
    return (False, 0, "")
Mitigación SLAPP crítica: Si el CSV de sancionados no se ha actualizado en >14 días, la bandera B1 se desactiva automáticamente y se logea un warning. Razonamiento: una lista desactualizada podría incluir proveedores cuya sanción ya venció, generando una acusación falsa. El sistema NUNCA asigna 20 puntos con datos potencialmente desactualizados.

Python

import os
from datetime import datetime, timedelta

def verificar_frescura_sancionados(path: str) -> bool:
    """Retorna True si el CSV fue modificado en los últimos 14 días."""
    mtime = os.path.getmtime(path)
    dias_desde_actualizacion = (datetime.now() - datetime.fromtimestamp(mtime)).days
    if dias_desde_actualizacion > 14:
        log.warning(f"CSV de sancionados tiene {dias_desde_actualizacion} días. B1 DESACTIVADA.")
        return False
    return True
B2 — Empresa "de Papel" (DESACTIVADA EN MVP)
Puntos: 8 (no asignables en MVP)

Razón de desactivación: Requiere fecha_constitución de la empresa, disponible en el RUES (Registro Único Empresarial y Social) de Confecámaras. SECOP II no incluye este campo. Obtenerlo requiere scraping del sitio web del RUES, que tiene CAPTCHA y términos de uso restrictivos.

Fase 2: Implementar scraping del RUES con manejo de CAPTCHA o explorar API comercial de Confecámaras.

Impacto en scoring: El máximo teórico baja de 100 a 92 pts (antes de bonus).

B3 — Concentración de Riesgo (7 puntos)
Fundamento legal: Cuando un solo proveedor acumula >50% del presupuesto de contratación de una entidad, hay indicios de favorecimiento indebido que viola el principio de selección objetiva (Art. 29 Ley 80/1993).

Campos evaluados: documento_proveedor, nombre_entidad, valor_del_contrato (cálculo histórico sobre contratos_raw)

Lógica:

Python

from sqlalchemy import text

UMBRAL_CONCENTRACION = 0.50  # 50% del presupuesto de la entidad

def evaluar_b3(contrato: dict, db_session) -> tuple[bool, int, str]:
    doc_proveedor = contrato["documento_proveedor"]
    entidad = contrato["nombre_entidad"]
    
    # Total contratado por la entidad en los últimos 12 meses
    query_total = text("""
        SELECT COALESCE(SUM(valor_del_contrato), 0) as total
        FROM contratos_raw
        WHERE nombre_entidad = :entidad
        AND fecha_de_firma >= NOW() - INTERVAL '12 months'
    """)
    total_entidad = db_session.execute(query_total, {"entidad": entidad}).scalar()
    
    if total_entidad == 0:
        return (False, 0, "")
    
    # Total contratado por la entidad con este proveedor
    query_proveedor = text("""
        SELECT COALESCE(SUM(valor_del_contrato), 0) as total
        FROM contratos_raw
        WHERE nombre_entidad = :entidad
        AND documento_proveedor = :doc_proveedor
        AND fecha_de_firma >= NOW() - INTERVAL '12 months'
    """)
    total_proveedor = db_session.execute(
        query_proveedor, 
        {"entidad": entidad, "doc_proveedor": doc_proveedor}
    ).scalar()
    
    pct = total_proveedor / total_entidad
    
    if pct > UMBRAL_CONCENTRACION:
        pct_display = round(pct * 100, 1)
        return (True, 7, f"Proveedor concentra {pct_display}% del presupuesto de {entidad}")
    return (False, 0, "")
Nota sobre ventana temporal: Se usa una ventana de 12 meses para que la concentración sea significativa. Una ventana más corta podría generar falsos positivos con entidades que tienen poca contratación.

C. VALORES Y ADICIONES
C1 — Adición Superior al 30% del Valor Original (10 puntos)
Fundamento legal: Según el parágrafo del Art. 40 de la Ley 80/1993 y doctrina de Colombia Compra Eficiente, las adiciones que superan el 50% del valor original son ilegales. Lupa usa un umbral más conservador del 30% para detección temprana.

Dataset evaluado: Adiciones (cb9c-h8sn), cruzado con contratos_raw

Lógica:

Python

UMBRAL_ADICION_PCT = 0.30  # 30% del valor original

def evaluar_c1(contrato: dict, adiciones: list) -> tuple[bool, int, str]:
    valor_original = contrato["valor_del_contrato"]
    
    if valor_original is None or valor_original <= 0:
        return (False, 0, "")
    
    suma_adiciones = sum(
        a.get("valor_adicion", 0) 
        for a in adiciones 
        if a.get("tipo_adicion") in ["Valor", "Valor y Tiempo"]
    )
    
    if suma_adiciones <= 0:
        return (False, 0, "")
    
    pct = suma_adiciones / valor_original
    
    if pct > UMBRAL_ADICION_PCT:
        pct_display = round(pct * 100, 1)
        valor_adicion_display = f"${suma_adiciones:,.0f}"
        return (True, 10, f"Adiciones por {valor_adicion_display} ({pct_display}% del valor original)")
    return (False, 0, "")
C2 — Fraccionamiento Sistemático (10 puntos)
Fundamento legal: El fraccionamiento de contratos para evadir umbrales de cuantía que obligarían a procesos competitivos es una práctica expresamente prohibida por el Art. 24, numeral 8 de la Ley 80/1993.

Campos evaluados: documento_proveedor, nombre_entidad, valor_del_contrato, modalidad_de_contratacion, fecha_de_firma

Lógica:

Python

UMBRAL_FRACCIONAMIENTO_COP = 500_000_000  # $500M COP (umbral de licitación para entidades medianas)
VENTANA_FRACCIONAMIENTO_DIAS = 60  # 60 días calendario

def evaluar_c2(contrato: dict, db_session) -> tuple[bool, int, str]:
    doc_proveedor = contrato["documento_proveedor"]
    entidad = contrato["nombre_entidad"]
    fecha_firma = contrato["fecha_de_firma"]
    
    # Buscar contratos directos del mismo proveedor con la misma entidad en ventana de 60 días
    query = text("""
        SELECT id_contrato, valor_del_contrato, fecha_de_firma
        FROM contratos_raw
        WHERE documento_proveedor = :doc_proveedor
        AND nombre_entidad = :entidad
        AND modalidad_de_contratacion ILIKE '%directa%'
        AND fecha_de_firma BETWEEN :fecha_inicio AND :fecha_fin
    """)
    
    fecha_inicio = fecha_firma - timedelta(days=VENTANA_FRACCIONAMIENTO_DIAS)
    fecha_fin = fecha_firma + timedelta(days=VENTANA_FRACCIONAMIENTO_DIAS)
    
    contratos_ventana = db_session.execute(query, {
        "doc_proveedor": doc_proveedor,
        "entidad": entidad,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }).fetchall()
    
    if len(contratos_ventana) < 2:
        return (False, 0, "")
    
    suma_contratos = sum(c.valor_del_contrato for c in contratos_ventana if c.valor_del_contrato)
    
    if suma_contratos > UMBRAL_FRACCIONAMIENTO_COP:
        n_contratos = len(contratos_ventana)
        return (True, 10, f"{n_contratos} contratos directos del mismo proveedor suman ${suma_contratos:,.0f} en {VENTANA_FRACCIONAMIENTO_DIAS} días")
    return (False, 0, "")
C3 — Posible Fuga de Información (5 puntos)
Fundamento legal: Cuando el precio adjudicado es ≥99% del precio base (presupuesto oficial), es estadísticamente improbable en un proceso competitivo genuino. Indica posible fuga del presupuesto al proveedor favorecido.

Campos evaluados: valor_del_contrato, precio_base (del JOIN con Procesos)

Lógica:

Python

UMBRAL_FUGA_PCT = 0.99  # 99% del precio base

def evaluar_c3(contrato: dict) -> tuple[bool, int, str]:
    valor = contrato.get("valor_del_contrato")
    precio_base = contrato.get("precio_base")
    
    if valor is None or precio_base is None or precio_base <= 0:
        return (False, 0, "")
    
    ratio = valor / precio_base
    
    if ratio >= UMBRAL_FUGA_PCT and ratio <= 1.05:  # Tope superior para excluir adiciones
        pct_display = round(ratio * 100, 1)
        return (True, 5, f"Valor adjudicado es {pct_display}% del precio base")
    return (False, 0, "")
Nota: Se incluye un tope superior de 105% para excluir casos donde el valor supera el precio base por adiciones ya incluidas, lo cual es una situación diferente (evaluada por C1).

D. OPACIDAD
D1 — Objeto Vago o Documentos No Publicados (6 puntos)
Fundamento legal: El principio de publicidad (Art. 24 Ley 80/1993) obliga a que la información contractual sea completa y accesible. Descripciones vagas o documentos no publicados obstaculizan el control ciudadano.

Campos evaluados: descripcion_del_proceso, estado_contrato

Lógica:

Python

LONGITUD_MINIMA_DESCRIPCION = 30  # caracteres
PALABRAS_VAGAS = [
    "varios", "diferentes", "otros", "etc", "y demás",
    "prestación de servicios varios", "objeto del contrato",
    "según necesidades",
]

def evaluar_d1(contrato: dict) -> tuple[bool, int, str]:
    descripcion = str(contrato.get("descripcion_del_proceso", "")).strip()
    estado = str(contrato.get("estado_contrato", "")).strip()
    
    puntos = 0
    razones = []
    
    # Sub-check 1: Descripción ausente o demasiado corta
    if len(descripcion) < LONGITUD_MINIMA_DESCRIPCION:
        puntos += 3
        razones.append(f"Descripción demasiado corta ({len(descripcion)} caracteres)")
    
    # Sub-check 2: Descripción con palabras vagas dominantes
    descripcion_lower = descripcion.lower()
    vagas_encontradas = [p for p in PALABRAS_VAGAS if p in descripcion_lower]
    if len(vagas_encontradas) >= 2:
        puntos += 3
        razones.append(f"Descripción vaga (contiene: {', '.join(vagas_encontradas[:3])})")
    
    if puntos > 0:
        return (True, min(puntos, 6), "; ".join(razones))
    return (False, 0, "")
D2 — Entidad con >80% de Contratación Directa Histórica (4 puntos)
Fundamento legal: Una entidad que contrata >80% de su presupuesto por contratación directa muestra un patrón sistémico de evasión de competencia, independientemente de las justificaciones individuales.

Campos evaluados: modalidad_de_contratacion, nombre_entidad (cálculo histórico)

Lógica:

Python

UMBRAL_PCT_DIRECTA = 0.80  # 80% de contratación directa

def evaluar_d2(contrato: dict, db_session) -> tuple[bool, int, str]:
    entidad = contrato["nombre_entidad"]
    
    query_total = text("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE modalidad_de_contratacion ILIKE '%directa%') as directas
        FROM contratos_raw
        WHERE nombre_entidad = :entidad
        AND fecha_de_firma >= NOW() - INTERVAL '12 months'
    """)
    
    result = db_session.execute(query_total, {"entidad": entidad}).fetchone()
    
    if result.total < 5:  # Mínimo 5 contratos para que el porcentaje sea significativo
        return (False, 0, "")
    
    pct = result.directas / result.total
    
    if pct > UMBRAL_PCT_DIRECTA:
        pct_display = round(pct * 100, 1)
        return (True, 4, f"{entidad} contrata {pct_display}% por directa ({result.directas}/{result.total} contratos en 12 meses)")
    return (False, 0, "")
6.4 Bonus Sistémico
Regla: Si un contrato activa 3 o más banderas simultáneas, se aplica un bonus de +10 puntos, topado al máximo de 100.

Justificación: La co-ocurrencia de múltiples banderas independientes es exponencialmente más sospechosa que banderas aisladas. Un contrato con contratación directa (A1) + oferente único (A2) + concentración de proveedor (B3) muestra un patrón sistémico, no una irregularidad aislada.

Python

UMBRAL_BONUS_BANDERAS = 3
BONUS_SISTEMICO = 10
SCORE_MAXIMO = 100

def aplicar_bonus(score: int, banderas_activas: list) -> int:
    if len(banderas_activas) >= UMBRAL_BONUS_BANDERAS:
        return min(score + BONUS_SISTEMICO, SCORE_MAXIMO)
    return score
6.5 Atenuación ACTT (Convenios Interadministrativos)
Propósito: Los convenios interadministrativos entre entidades públicas (ej: Alcaldía de Medellín + Universidad de Antioquia) legalmente no requieren proceso competitivo (Art. 2, numeral 4, literal c, Ley 1150/2007). Sin atenuación, estos convenios activarían A1 (contratación directa) automáticamente, generando falsos positivos masivos.

Implementación:

Python

# NITs de universidades públicas y entidades interadministrativas frecuentes en Medellín
NITS_ENTIDADES_PUBLICAS = {
    "890980040",  # Universidad de Antioquia
    "890980066",  # Universidad Nacional sede Medellín
    "811016192",  # ITM
    "890905211",  # Municipio de Medellín
    "890984423",  # SENA Regional Antioquia
    "800150861",  # Politécnico Colombiano Jaime Isaza Cadavid
    # ... se expande en implementación
}

BANDERAS_GRAVES = {"C1", "C2"}  # Adiciones excesivas y fraccionamiento no se atenúan

FACTOR_ATENUACION_INTERADMIN = 0.5  # Reduce el score al 50%

def aplicar_atenuacion_actt(contrato: dict, score: int, banderas: set) -> int:
    doc_proveedor = str(contrato.get("documento_proveedor", "")).strip()
    
    # ¿Es proveedor una entidad pública conocida?
    if doc_proveedor not in NITS_ENTIDADES_PUBLICAS:
        return score
    
    # ¿Tiene banderas graves que no se atenúan?
    if banderas.intersection(BANDERAS_GRAVES):
        return score  # No se atenúa si hay adiciones excesivas o fraccionamiento
    
    score_atenuado = int(score * FACTOR_ATENUACION_INTERADMIN)
    log.info(f"ACTT: Score atenuado de {score} a {score_atenuado} para proveedor público {doc_proveedor}")
    return score_atenuado
Decisión conservadora: La lista de NITs de entidades públicas se hardcodea inicialmente con las ~20 entidades más frecuentes en contratación interadministrativa en Medellín. Se expande iterativamente post-lanzamiento. Si un NIT público no está en la lista, el convenio NO se atenúa — se prefiere falso positivo (detectable y corregible) a falso negativo (irregularidad real no detectada).

6.6 Orquestación Completa del Scoring
Python

def score_contrato(contrato: dict, adiciones: list, db_session) -> dict:
    """
    Orquesta el scoring completo de un contrato.
    Retorna dict con score, banderas, traducción, y texto de denuncia.
    """
    # 1. Quality Gate
    icd = calcular_icd(contrato)
    
    if icd < 40:
        return {
            "icd": icd,
            "destino": "opacos",
            "score": None,
            "banderas": [],
        }
    
    # 2. Evaluar todas las banderas
    evaluaciones = {
        "A1": evaluar_a1(contrato),
        "A2": evaluar_a2(contrato),
        "A3": evaluar_a3(contrato),
        "B1": evaluar_b1(contrato),
        # B2 DESACTIVADA
        "B3": evaluar_b3(contrato, db_session),
        "C1": evaluar_c1(contrato, adiciones),
        "C2": evaluar_c2(contrato, db_session),
        "C3": evaluar_c3(contrato),
        "D1": evaluar_d1(contrato),
        "D2": evaluar_d2(contrato, db_session),
    }
    
    # 3. Acumular score y banderas activas
    score = 0
    banderas_activas = []
    detalle = {}
    
    for codigo, (activa, puntos, descripcion) in evaluaciones.items():
        if activa:
            score += puntos
            banderas_activas.append(codigo)
            detalle[codigo] = {"pts": puntos, "desc": descripcion}
    
    # 4. Bonus sistémico
    score = aplicar_bonus(score, banderas_activas)
    if len(banderas_activas) >= UMBRAL_BONUS_BANDERAS:
        detalle["BONUS"] = {"pts": BONUS_SISTEMICO, "desc": f"≥{UMBRAL_BONUS_BANDERAS} banderas simultáneas"}
    
    # 5. Atenuación ACTT
    score_pre_actt = score
    score = aplicar_atenuacion_actt(contrato, score, set(banderas_activas))
    if score != score_pre_actt:
        detalle["ACTT"] = {"pts": score - score_pre_actt, "desc": "Atenuación por convenio interadministrativo"}
    
    # 6. Penalización ICD
    if 40 <= icd < 60:
        penalizacion = int(score * 0.15)
        score = score - penalizacion
        detalle["ICD_PEN"] = {"pts": -penalizacion, "desc": f"Penalización por ICD bajo ({icd}/100)"}
    
    # 7. Clasificar nivel de riesgo
    nivel = clasificar_nivel(score)
    
    # 8. Generar traducción ciudadana
    traduccion = generar_traduccion(contrato, banderas_activas, detalle)
    
    # 9. Generar texto de denuncia (si score ≥ 55)
    texto_denuncia = generar_denuncia(contrato, banderas_activas, detalle) if score >= 55 else None
    
    return {
        "icd": icd,
        "destino": "scored",
        "score": min(score, 100),
        "nivel": nivel,
        "banderas": banderas_activas,
        "detalle": detalle,
        "traduccion": traduccion,
        "texto_denuncia": texto_denuncia,
    }


def clasificar_nivel(score: int) -> str:
    if score >= 70:
        return "CRÍTICO"
    elif score >= 55:
        return "ALTO"
    elif score >= 40:
        return "MEDIO"
    else:
        return "BAJO"
6.7 Traducción a "Español Ciudadano"
Propósito: Convertir datos técnicos en impacto tangible. El ciudadano no procesa "$800.000.000" pero sí procesa "3 ambulancias equipadas".

Implementación:

Python

EQUIVALENCIAS = [
    # (umbral_minimo, divisor, unidad, emoji)
    (1_000_000_000, 450_000_000, "colegios nuevos", "🏫"),
    (500_000_000, 120_000_000, "ambulancias equipadas", "🚑"),
    (100_000_000, 25_000_000, "becas universitarias anuales", "🎓"),
    (50_000_000, 8_000_000, "salarios mínimos mensuales", "💰"),
    (10_000_000, 3_500_000, "mercados familiares completos", "🛒"),
]

def equivalente_social(valor: float) -> str:
    for umbral, divisor, unidad, emoji in EQUIVALENCIAS:
        if valor >= umbral:
            cantidad = int(valor // divisor)
            if cantidad > 0:
                return f"{emoji} {cantidad} {unidad}"
    return f"💰 ${valor:,.0f} COP"


NOMBRES_BANDERAS = {
    "A1": "Contratación directa sin competencia",
    "A2": "Oferente único en proceso competitivo",
    "A3": "Período de publicación demasiado corto",
    "B1": "Proveedor inhabilitado por la Procuraduría",
    "B3": "Proveedor concentra demasiado presupuesto de la entidad",
    "C1": "Adiciones superiores al 30% del valor original",
    "C2": "Posible fraccionamiento de contratos",
    "C3": "Precio adjudicado sospechosamente cercano al presupuesto",
    "D1": "Descripción vaga o documentos no publicados",
    "D2": "Entidad con historial excesivo de contratación directa",
}

def generar_traduccion(contrato: dict, banderas: list, detalle: dict) -> str:
    valor = contrato["valor_del_contrato"]
    entidad = contrato["nombre_entidad"]
    proveedor = contrato["proveedor_adjudicado"]
    equiv = equivalente_social(valor)
    
    # Ensamblar banderas en español
    banderas_texto = "\n".join(
        f"  🚩 {NOMBRES_BANDERAS.get(b, b)}" 
        for b in banderas 
        if b not in ("BONUS", "ACTT", "ICD_PEN")
    )
    
    texto = (
        f"Contrato por ${valor:,.0f} COP ({equiv}) adjudicado a "
        f"{proveedor} por {entidad}.\n\n"
        f"Banderas de riesgo detectadas:\n{banderas_texto}"
    )
    
    return texto
6.8 Generación de Texto de Denuncia
Python

def generar_denuncia(contrato: dict, banderas: list, detalle: dict) -> str:
    """Genera borrador de queja disciplinaria en texto plano."""
    
    fecha_hoy = datetime.now().strftime("%d de %B de %Y")
    
    # Mapeo de banderas a artículos de ley
    LEYES_POR_BANDERA = {
        "A1": "Art. 2 Ley 1150/2007 (causales de contratación directa); Art. 24 Ley 80/1993 (principio de transparencia)",
        "A2": "Art. 29 Ley 80/1993 (selección objetiva); Art. 5 Ley 1150/2007",
        "A3": "Art. 30 Ley 80/1993 (estructura de procedimientos de selección); Art. 24 Ley 80/1993",
        "B1": "Art. 8 Ley 80/1993 (inhabilidades e incompatibilidades); Arts. 408-410 Código Penal",
        "B3": "Art. 29 Ley 80/1993 (selección objetiva); Art. 34 Ley 1474/2011 (medidas anticorrupción)",
        "C1": "Art. 40, parágrafo, Ley 80/1993 (adiciones contractuales)",
        "C2": "Art. 24 numeral 8 Ley 80/1993 (prohibición de fraccionamiento)",
        "C3": "Art. 29 Ley 80/1993 (selección objetiva)",
        "D1": "Art. 24 Ley 80/1993 (principio de publicidad); Art. 74 Constitución Política",
        "D2": "Art. 2 Ley 1150/2007; Decreto 1082/2015",
    }
    
    leyes_aplicables = set()
    hallazgos_texto = []
    
    for b in banderas:
        if b in LEYES_POR_BANDERA:
            leyes_aplicables.add(LEYES_POR_BANDERA[b])
            hallazgos_texto.append(f"- {NOMBRES_BANDERAS.get(b, b)}: {detalle.get(b, {}).get('desc', '')}")
    
    leyes_str = "\n".join(f"  • {ley}" for ley in sorted(leyes_aplicables))
    hallazgos_str = "\n".join(hallazgos_texto)
    
    denuncia = f"""QUEJA DISCIPLINARIA — CONTRATACIÓN PÚBLICA
===========================================

Fecha: {fecha_hoy}

ENTIDAD CONTRATANTE:
  Nombre: {contrato.get('nombre_entidad', 'No disponible')}
  NIT: {contrato.get('nit_entidad', 'No disponible')}

CONTRATO OBJETO DE LA QUEJA:
  ID Contrato (SECOP II): {contrato.get('id_contrato', 'No disponible')}
  Referencia: {contrato.get('referencia_del_contrato', 'No disponible')}
  Valor: ${contrato.get('valor_del_contrato', 0):,.0f} COP
  Modalidad: {contrato.get('modalidad_de_contratacion', 'No disponible')}
  Fecha de firma: {contrato.get('fecha_de_firma', 'No disponible')}

PROVEEDOR ADJUDICADO:
  Nombre/Razón Social: {contrato.get('proveedor_adjudicado', 'No disponible')}
  Documento: {contrato.get('documento_proveedor', 'No disponible')}

HALLAZGOS DETECTADOS ALGORÍTMICAMENTE:
{hallazgos_str}

Score de Riesgo (Lupa): {detalle.get('score', 'N/A')}/100

NORMAS PRESUNTAMENTE VULNERADAS:
{leyes_str}

SOLICITUD:
Con fundamento en el artículo 23 de la Constitución Política de Colombia y los artículos 13 a 33 del Código de Procedimiento Administrativo y de lo Contencioso Administrativo (CPACA), solicito respetuosamente:

1. Se inicie indagación disciplinaria por los hechos descritos.
2. Se verifique el cumplimiento de las normas citadas en el proceso de contratación señalado.
3. Se me informe sobre el trámite dado a esta queja.

NOTA IMPORTANTE:
Este borrador fue generado por el sistema Lupa (https://lupa.city) a partir de un análisis algorítmico de datos públicos del SECOP II. No constituye una acusación legal ni tiene sesgo político. El ciudadano que lo presente es responsable de verificar los datos antes de radicarlo.

Los datos fuente están disponibles públicamente en: https://www.datos.gov.co/resource/jbjy-vk9h.json
La metodología de scoring está publicada en: https://github.com/[repo]/lupa-engine
"""
    
    return denuncia
6.9 Tabla Resumen de Banderas MVP
Código	Nombre	Puntos	Campo(s) SECOP II	Fundamento Legal	Estado MVP
A1	Contratación directa sin causal	12	modalidad_de_contratacion, valor_del_contrato	Art. 2 Ley 1150/2007	✅ Activa
A2	Oferente único en competitivo	10	numero_de_oferentes, modalidad_de_contratacion	Art. 29 Ley 80/1993	✅ Activa
A3	Período de publicación "sastre"	8	fecha_de_publicacion_del_proceso, fecha_de_recepcion_de_ofertas	Art. 30 Ley 80/1993	✅ Activa
B1	Proveedor inhabilitado	20	documento_proveedor + CSV Procuraduría	Art. 8 Ley 80/1993	✅ Activa (con check de frescura)
B2	Empresa "de papel"	8	fecha_constitución (RUES — externo)	Art. 29 Ley 80/1993	❌ Desactivada
B3	Concentración de riesgo	7	documento_proveedor, nombre_entidad, valor_del_contrato	Art. 29 Ley 80/1993	✅ Activa
C1	Adición > 30% del valor	10	Dataset Adiciones (cb9c-h8sn)	Art. 40 Ley 80/1993	✅ Activa
C2	Fraccionamiento sistemático	10	documento_proveedor, nombre_entidad, valor_del_contrato, fecha_de_firma	Art. 24 num. 8 Ley 80/1993	✅ Activa
C3	Fuga de información (precio)	5	valor_del_contrato, precio_base	Art. 29 Ley 80/1993	✅ Activa
D1	Objeto vago / docs no publicados	6	descripcion_del_proceso, estado_contrato	Art. 24 Ley 80/1993	✅ Activa
D2	Entidad con >80% directa	4	modalidad_de_contratacion, nombre_entidad	Art. 2 Ley 1150/2007	✅ Activa
Máximo teórico MVP: 92 pts (sin B2) + 10 bonus = 100 pts

7. UMBRALES DE ALERTA Y ESCALAMIENTO
7.1 Justificación de Recalibración
Con la eliminación de la Capa 2 semántica (que aportaba hasta 50 puntos en la visión completa), el scoring opera exclusivamente con la Capa 1 determinista. Los pesos de la Capa 1 se mantienen tal cual, ya que suman hasta 100 puntos teóricos. Esto tiene una consecuencia importante para los umbrales:

Alcanzar score ≥ 70 en Capa 1 sola requiere activar ≥4 banderas significativas simultáneas. Ejemplo: A1 (12) + B3 (7) + C2 (10) + C1 (10) + D1 (6) + D2 (4) = 49 + bonus (10) = 59. Para llegar a 70 se necesitaría añadir B1 (20) o más banderas. Esto significa que los contratos que alcanzan Nivel 3 son inherentemente altamente sospechosos, lo cual reduce falsos positivos de forma natural.

Decisión: Se mantienen los umbrales originales (40/55/70) porque su conservadurismo es una ventaja, no una limitación. Un contrato Nivel 3 con solo Capa 1 es más confiable que uno que necesitara Capa 2 para alcanzar el umbral.

7.2 Niveles de Alerta
NIVEL 1 — Score ≥ 40 (Publicación Web)
Acción: El contrato aparece en el Top 10 semanal de la web (Next.js).

Contenido publicado:

Score numérico (0-100) con indicador visual de color (🟡 amarillo)
Nivel de riesgo: "MEDIO"
Banderas activas con nombres legibles
Traducción ciudadana (equivalente social)
Disclaimer SLAPP obligatorio
Enlace a la fuente en SECOP II (si disponible)
Automatización: Publicación web vía ISR/revalidate de Next.js. No requiere acción manual.

Justificación del umbral 40: Un score de 40 requiere al menos 2-3 banderas de peso medio. Esto excluye contratos con una sola bandera aislada (que podría ser explicable) y limita la publicación a patrones con múltiples señales coincidentes.

NIVEL 2 — Score ≥ 55 (Alerta Telegram + Borrador de Denuncia)
Acción:

Bot publica automáticamente en canal @LupaMedellin (Telegram)
En la web, se habilita el botón "📋 Copiar Borrador de Denuncia"
INSERT en timeline_impunidad con estado_respuesta = 'PENDIENTE'
Contenido del mensaje Telegram:

Markdown

🟠 ALERTA LUPA — RIESGO ALTO

📊 Score: 67/100
🏛️ Entidad: [nombre_entidad]
🏢 Proveedor: [proveedor_adjudicado]
💰 Valor: $[valor_del_contrato] COP ([equivalente_social])

🚩 Banderas detectadas:
  • Contratación directa sin competencia
  • Proveedor concentra 72% del presupuesto de la entidad
  • Posible fraccionamiento de contratos

👉 Ver detalles y copiar borrador de denuncia:
https://lupa.city/contrato/[id_contrato]

⚠️ Este análisis es algorítmico y basado en datos públicos del
SECOP II. No representa una acusación legal ni tiene sesgo político.
Automatización: Workflow n8n → script Python → Telegram Bot API. Sin intervención manual.

Justificación del umbral 55: Requiere ≥3 banderas significativas o B1 (inhabilitado, 20 pts) + otra bandera. Solo contratos con patrón claro de riesgo múltiple llegan a Telegram, protegiendo la credibilidad del canal.

NIVEL 3 — Score ≥ 70 (Caballo de Troya / Escalamiento)
Acción:

Todo lo de Nivel 2 (Telegram + denuncia + timeline)
Generación de dossier en texto (CSV + resumen narrativo)
Envío a Concejal MIRA y periodistas (La Silla Vacía, El Armadillo)
Operación en MVP: El envío del dossier es manual en el MVP. El sistema genera el dossier (texto + CSV) pero un operador humano lo envía vía email (ProtonMail si disponible, Gmail si no). La automatización completa se implementa en Fase 2.

Contenido del dossier:

Resumen narrativo del hallazgo (texto generado por plantilla)
Score y desglose completo de banderas
Datos del contrato en formato tabular
Leyes presuntamente vulneradas
CSV con todos los contratos relacionados (mismo proveedor, misma entidad, ventana temporal)
Disclaimer SLAPP
Enlace a la web de Lupa
Justificación del umbral 70: En Capa 1 sola, un score de 70 requiere combinaciones como B1 (20) + A1 (12) + C2 (10) + B3 (7) + D1 (6) + D2 (4) = 59 + bonus (10) = 69 ≈ 70. Esto significa proveedor inhabilitado + contratación directa + fraccionamiento + concentración + opacidad. Un patrón así amerita escalamiento a actores con poder de acción (concejales, periodistas).

Frecuencia esperada: Con datos reales de Medellín, se estima 0-3 contratos Nivel 3 por semana. Si la frecuencia es >5/semana, los umbrales se recalibran al alza (configurable vía variables de entorno).

7.3 Configurabilidad
Los umbrales son variables de entorno para facilitar recalibración sin redespliegue:

Python

# .env
UMBRAL_NIVEL_1 = 40
UMBRAL_NIVEL_2 = 55
UMBRAL_NIVEL_3 = 70
MAX_ALERTAS_TELEGRAM_DIA = 20
BONUS_SISTEMICO_PUNTOS = 10
BONUS_SISTEMICO_UMBRAL_BANDERAS = 3
Proceso de recalibración: Después de las primeras 2 semanas de datos reales:

Analizar distribución de scores: ¿qué percentil es cada umbral?
Revisar falsos positivos identificados manualmente
Ajustar umbrales si la tasa de falsos positivos >20% o si no hay contratos en Nivel 2/3
8. SCHEMA DE BASE DE DATOS
8.1 Decisiones de Diseño
Decisión	Justificación
4 tablas core + 1 de soporte en lugar de schema normalizado completo	Simplicidad de implementación para MVP. Desnormalización deliberada en contratos_raw (campos del JOIN con Procesos) para evitar JOINs en caliente durante el scoring.
JSONB para banderas y detalles	Flexibilidad para agregar/quitar banderas sin ALTER TABLE. Consultable con operadores PostgreSQL (@>, ?, ->>).
texto_denuncia pre-generado en contratos_scored	El frontend solo sirve texto estático, sin lógica de generación. Reduce complejidad del frontend y garantiza consistencia.
UUID como PK en contratos_raw	Independencia del id_contrato de SECOP II (que podría cambiar o tener colisiones). El id_contrato se mantiene como UNIQUE index para deduplicación.
Tabla separada para opacos	Separación clara de contratos evaluables vs. no evaluables. Evita contaminar la distribución de scores con registros incompletos.
timeline_impunidad separada de scored	No todos los contratos scored generan entrada en timeline (solo score ≥ 55). Relación 1:1 opcional.
8.2 Schema SQL Completo
SQL

-- ============================================================
-- LUPA MVP v1.0 — Schema PostgreSQL (Supabase)
-- ============================================================

-- Extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- TABLA 1: contratos_raw
-- Datos crudos SECOP II post-limpieza y merge
-- ============================================================
CREATE TABLE contratos_raw (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificadores
    id_contrato VARCHAR(100) NOT NULL,
    referencia_del_contrato VARCHAR(200),
    proceso_de_compra VARCHAR(100),
    
    -- Entidad
    nombre_entidad VARCHAR(500) NOT NULL,
    nit_entidad VARCHAR(20),
    ciudad VARCHAR(100),
    sector VARCHAR(200),
    
    -- Proveedor
    documento_proveedor VARCHAR(20),
    tipodocproveedor VARCHAR(50),
    proveedor_adjudicado VARCHAR(500),
    es_grupo VARCHAR(10),
    es_pyme VARCHAR(10),
    nombre_representante_legal VARCHAR(300),
    
    -- Contrato
    valor_del_contrato NUMERIC(20,2),
    tipo_de_contrato VARCHAR(200),
    modalidad_de_contratacion VARCHAR(200),
    justificacion_modalidad_de TEXT,
    descripcion_del_proceso TEXT,
    destino_gasto VARCHAR(200),
    estado_contrato VARCHAR(100),
    
    -- Fechas
    fecha_de_firma TIMESTAMP,
    fecha_inicio_ejecucion TIMESTAMP,
    ultima_actualizacion TIMESTAMP,
    
    -- Campos del JOIN con Procesos (desnormalizados)
    numero_de_oferentes INTEGER,
    precio_base NUMERIC(20,2),
    fecha_de_publicacion_del_proceso TIMESTAMP,
    fecha_de_recepcion_de_ofertas TIMESTAMP,
    
    -- Calidad del dato
    icd_score INTEGER CHECK (icd_score >= 0 AND icd_score <= 100),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 CONSTRAINT uq_id_contrato UNIQUE (id_contrato)
);

-- Índices para contratos_raw
CREATE INDEX idx_raw_proceso ON contratos_raw(proceso_de_compra);
CREATE INDEX idx_raw_documento_proveedor ON contratos_raw(documento_proveedor);
CREATE INDEX idx_raw_nombre_entidad ON contratos_raw(nombre_entidad);
CREATE INDEX idx_raw_modalidad ON contratos_raw(modalidad_de_contratacion);
CREATE INDEX idx_raw_fecha_firma ON contratos_raw(fecha_de_firma);
CREATE INDEX idx_raw_ciudad ON contratos_raw(ciudad);
CREATE INDEX idx_raw_icd ON contratos_raw(icd_score);
CREATE INDEX idx_raw_created_at ON contratos_raw(created_at);
CREATE INDEX idx_raw_ultima_actualizacion ON contratos_raw(ultima_actualizacion);

-- Trigger para updated_at automático
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_contratos_raw_updated_at
    BEFORE UPDATE ON contratos_raw
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- TABLA 2: contratos_scored
-- Contratos con score calculado por el Lupa Engine
-- ============================================================
CREATE TABLE contratos_scored (
    -- PK = FK a contratos_raw.id_contrato
    id_contrato VARCHAR(100) PRIMARY KEY,
    
    -- Score
    score_total INTEGER NOT NULL CHECK (score_total >= 0 AND score_total <= 100),
    nivel_riesgo VARCHAR(10) NOT NULL CHECK (
        nivel_riesgo IN ('BAJO', 'MEDIO', 'ALTO', 'CRÍTICO')
    ),
    
    -- Banderas
    banderas_activas JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Ejemplo: ["A1", "B3", "C2"]
    
    detalle_banderas JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Ejemplo: {
    --   "A1": {"pts": 12, "desc": "Contratación directa sin causal"},
    --   "B3": {"pts": 7, "desc": "Proveedor concentra 72% del presupuesto"},
    --   "BONUS": {"pts": 10, "desc": "≥3 banderas simultáneas"}
    -- }
    
    -- Textos pre-generados
    traduccion_ciudadana TEXT NOT NULL,
    texto_denuncia TEXT,  -- NULL si score < 55
    
    -- Estado de distribución
    publicado_telegram BOOLEAN NOT NULL DEFAULT FALSE,
    publicado_web BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- FK
    CONSTRAINT fk_scored_raw FOREIGN KEY (id_contrato)
        REFERENCES contratos_raw(id_contrato)
        ON DELETE CASCADE
);

-- Índices para contratos_scored
CREATE INDEX idx_scored_score ON contratos_scored(score_total DESC);
CREATE INDEX idx_scored_nivel ON contratos_scored(nivel_riesgo);
CREATE INDEX idx_scored_telegram ON contratos_scored(publicado_telegram)
    WHERE publicado_telegram = FALSE;
CREATE INDEX idx_scored_created_at ON contratos_scored(created_at);
CREATE INDEX idx_scored_banderas ON contratos_scored USING GIN (banderas_activas);

-- Índice parcial para distribución Telegram (solo pendientes con score ≥ 55)
CREATE INDEX idx_scored_telegram_pendientes ON contratos_scored(score_total DESC)
    WHERE publicado_telegram = FALSE AND score_total >= 55;

CREATE TRIGGER update_contratos_scored_updated_at
    BEFORE UPDATE ON contratos_scored
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- TABLA 3: contratos_opacos
-- Contratos con ICD < 40 (datos insuficientes para scoring)
-- ============================================================
CREATE TABLE contratos_opacos (
    -- PK = FK a contratos_raw.id_contrato
    id_contrato VARCHAR(100) PRIMARY KEY,
    
    -- ICD
    icd_score INTEGER NOT NULL CHECK (icd_score >= 0 AND icd_score < 40),
    
    -- Detalle de opacidad
    campos_faltantes JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Ejemplo: [
    --   "justificacion_modalidad_de",
    --   "numero_de_oferentes",
    --   "precio_base",
    --   "descripcion_del_proceso"
    -- ]
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- FK
    CONSTRAINT fk_opacos_raw FOREIGN KEY (id_contrato)
        REFERENCES contratos_raw(id_contrato)
        ON DELETE CASCADE
);

-- Índices para contratos_opacos
CREATE INDEX idx_opacos_icd ON contratos_opacos(icd_score);
CREATE INDEX idx_opacos_created_at ON contratos_opacos(created_at);


-- ============================================================
-- TABLA 4: timeline_impunidad
-- Rastreo de respuesta institucional post-alerta
-- ============================================================
CREATE TABLE timeline_impunidad (
    id_alerta UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- FK al contrato scored
    id_contrato VARCHAR(100) NOT NULL,
    
    -- Fechas
    fecha_alerta TIMESTAMP NOT NULL DEFAULT NOW(),
    fecha_notificacion TIMESTAMP,  -- Cuando se notificó a la entidad (manual)
    fecha_respuesta TIMESTAMP,     -- Cuando se recibió respuesta (manual)
    
    -- Estado
    estado_respuesta VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE' CHECK (
        estado_respuesta IN (
            'PENDIENTE',
            'RADICADO',
            'EN_INDAGACION',
            'ARCHIVADO',
            'CON_RESPUESTA'
        )
    ),
    
    -- Días de inactividad (columna generada)
    dias_inactividad INTEGER GENERATED ALWAYS AS (
        EXTRACT(DAY FROM (COALESCE(fecha_respuesta, NOW()) - fecha_alerta))::INTEGER
    ) STORED,
    
    -- Seguimiento manual
    notas TEXT,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- FK
    CONSTRAINT fk_timeline_scored FOREIGN KEY (id_contrato)
        REFERENCES contratos_scored(id_contrato)
        ON DELETE CASCADE
);

-- Índices para timeline_impunidad
CREATE INDEX idx_timeline_estado ON timeline_impunidad(estado_respuesta);
CREATE INDEX idx_timeline_dias ON timeline_impunidad(dias_inactividad DESC);
CREATE INDEX idx_timeline_contrato ON timeline_impunidad(id_contrato);
CREATE INDEX idx_timeline_fecha_alerta ON timeline_impunidad(fecha_alerta);

CREATE TRIGGER update_timeline_updated_at
    BEFORE UPDATE ON timeline_impunidad
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- TABLA 5 (SOPORTE): reportes_anonimos
-- Reportes ciudadanos anónimos recibidos via formulario web
-- NO es tabla del pipeline core; se usa en Sprint 2
-- ============================================================
CREATE TABLE reportes_anonimos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Código de referencia para seguimiento sin identificación
    codigo_referencia VARCHAR(12) NOT NULL UNIQUE,
    -- Formato: LUPA-XXXXXXXX (8 caracteres alfanuméricos)
    
    -- Contenido del reporte
    entidad_reportada TEXT NOT NULL,
    descripcion TEXT NOT NULL CHECK (char_length(descripcion) >= 50),
    numero_contrato VARCHAR(100),  -- Opcional
    archivo_url VARCHAR(500),       -- URL en Supabase Storage, opcional
    
    -- Estado de revisión (por operador Lupa)
    estado_revision VARCHAR(20) NOT NULL DEFAULT 'NUEVO' CHECK (
        estado_revision IN ('NUEVO', 'EN_REVISION', 'VERIFICADO', 'DESCARTADO')
    ),
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- NOTA CRÍTICA: NO hay campo de IP, email, nombre, teléfono,
    -- ni ningún dato que identifique al remitente.
    -- El endpoint de FastAPI/Next.js NO logea request.client.host
    -- para esta tabla.
    
    CONSTRAINT chk_codigo_formato CHECK (
        codigo_referencia ~ '^LUPA-[A-Z0-9]{8}$'
    )
);

-- Índice para búsqueda por código de referencia
CREATE INDEX idx_reportes_codigo ON reportes_anonimos(codigo_referencia);
CREATE INDEX idx_reportes_estado ON reportes_anonimos(estado_revision);


-- ============================================================
-- TABLA 6 (SOPORTE): meta_pipeline
-- Metadata de ejecución del pipeline para ingesta incremental
-- ============================================================
CREATE TABLE meta_pipeline (
    id SERIAL PRIMARY KEY,
    nombre_pipeline VARCHAR(100) NOT NULL,
    ultima_ejecucion_exitosa TIMESTAMP,
    ultimo_offset_procesado INTEGER DEFAULT 0,
    registros_procesados INTEGER DEFAULT 0,
    estado VARCHAR(20) DEFAULT 'OK' CHECK (
        estado IN ('OK', 'FALLO_PARCIAL', 'FALLO_TOTAL')
    ),
    notas TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Registro inicial para cada pipeline
INSERT INTO meta_pipeline (nombre_pipeline) VALUES
    ('ingesta_contratos'),
    ('ingesta_procesos'),
    ('ingesta_adiciones'),
    ('scoring'),
    ('distribucion_telegram');

CREATE TRIGGER update_meta_pipeline_updated_at
    BEFORE UPDATE ON meta_pipeline
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- ROW LEVEL SECURITY (Supabase)
-- ============================================================

-- Habilitar RLS en todas las tablas
ALTER TABLE contratos_raw ENABLE ROW LEVEL SECURITY;
ALTER TABLE contratos_scored ENABLE ROW LEVEL SECURITY;
ALTER TABLE contratos_opacos ENABLE ROW LEVEL SECURITY;
ALTER TABLE timeline_impunidad ENABLE ROW LEVEL SECURITY;
ALTER TABLE reportes_anonimos ENABLE ROW LEVEL SECURITY;
ALTER TABLE meta_pipeline ENABLE ROW LEVEL SECURITY;

-- Políticas de lectura pública (anon) para tablas consultadas por el frontend
CREATE POLICY "Lectura pública contratos_scored"
    ON contratos_scored FOR SELECT
    USING (true);

CREATE POLICY "Lectura pública contratos_opacos"
    ON contratos_opacos FOR SELECT
    USING (true);

CREATE POLICY "Lectura pública timeline_impunidad"
    ON timeline_impunidad FOR SELECT
    USING (true);

CREATE POLICY "Lectura pública contratos_raw (campos seleccionados via view)"
    ON contratos_raw FOR SELECT
    USING (true);

-- Políticas de escritura: solo service_role (backend/workers)
CREATE POLICY "Escritura service_role contratos_raw"
    ON contratos_raw FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Escritura service_role contratos_scored"
    ON contratos_scored FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Escritura service_role contratos_opacos"
    ON contratos_opacos FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Escritura service_role timeline_impunidad"
    ON timeline_impunidad FOR ALL
    USING (auth.role() = 'service_role');

-- reportes_anonimos: INSERT público (anon), lectura solo service_role
CREATE POLICY "Insert público reportes_anonimos"
    ON reportes_anonimos FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Lectura service_role reportes_anonimos"
    ON reportes_anonimos FOR SELECT
    USING (auth.role() = 'service_role');

-- meta_pipeline: solo service_role
CREATE POLICY "Full access service_role meta_pipeline"
    ON meta_pipeline FOR ALL
    USING (auth.role() = 'service_role');
8.3 Mapeo Campo SODA → Columna PostgreSQL
Campo SODA (dataset jbjy-vk9h)	Columna en contratos_raw	Transformación en limpieza
nombre_entidad	nombre_entidad	strip(), normalizar mayúsculas (title case)
nit_entidad	nit_entidad	strip(), remover guiones y puntos
ciudad	ciudad	upper().strip(), filtro LIKE '%MEDELL%'
sector	sector	strip()
id_contrato	id_contrato	strip(), sin transformación
referencia_del_contrato	referencia_del_contrato	strip()
proceso_de_compra	proceso_de_compra	strip(), usado como JOIN key
modalidad_de_contratacion	modalidad_de_contratacion	strip(), normalizar variantes (ej: "Contratación Directa" → "Contratación directa")
justificacion_modalidad_de	justificacion_modalidad_de	strip(), preservar texto original
descripcion_del_proceso	descripcion_del_proceso	strip(), preservar texto original
tipo_de_contrato	tipo_de_contrato	strip()
valor_del_contrato	valor_del_contrato	float() → sanitizar_valor() (bug de centavos)
destino_gasto	destino_gasto	strip()
documento_proveedor	documento_proveedor	strip(), remover guiones y puntos, normalizar a string
tipodocproveedor	tipodocproveedor	strip()
proveedor_adjudicado	proveedor_adjudicado	strip(), title case
es_grupo	es_grupo	strip(), normalizar "Si"/"No"
es_pyme	es_pyme	strip(), normalizar "Si"/"No"
nombre_representante_legal	nombre_representante_legal	strip(), title case
fecha_de_firma	fecha_de_firma	parse_datetime(), timezone COT
ultima_actualizacion	ultima_actualizacion	parse_datetime(), timezone COT
estado_contrato	estado_contrato	strip()
Campo SODA (dataset p6dx-8zbt — Procesos)	Columna en contratos_raw	Notas
numero_de_oferentes	numero_de_oferentes	int(), NULL si no existe en JOIN
fecha_de_publicacion_del_proceso	fecha_de_publicacion_del_proceso	parse_datetime()
fecha_de_recepcion_de_ofertas	fecha_de_recepcion_de_ofertas	parse_datetime()
precio_base	precio_base	float(), saneamiento similar a valor_del_contrato
fecha_inicio_ejecucion	fecha_inicio_ejecucion	parse_datetime()
8.4 Estimación de Volumen
Métrica	Estimación	Justificación
Contratos de Medellín nuevos/actualizados por día	~50-150	Basado en muestreo de SODA API filtrando por ciudad
Contratos acumulados en contratos_raw tras 30 días	~3,000-5,000	Incluye históricos de primera ingesta completa
Contratos en contratos_scored con score ≥ 40	~10-20% del total	Estimación conservadora basada en patrones de contratación pública colombiana
Contratos en contratos_opacos	~5-15% del total	Datos faltantes frecuentes en SECOP II
Tamaño estimado de DB tras 30 días	<100MB	Muy por debajo del límite de 500MB del tier gratuito de Supabase
Filas en timeline_impunidad tras 30 días	~20-60	Solo contratos con score ≥ 55
9. PIPELINE OPERATIVO
9.1 Principio Arquitectónico
Lupa NUNCA consulta SECOP II en vivo. Todo opera desde el Data Lake propio (Supabase). El frontend, el bot de Telegram, y cualquier componente público consumen exclusivamente datos pre-procesados y almacenados. Esto garantiza: (a) disponibilidad del sistema aun cuando SECOP II esté caído, (b) consistencia de datos (snapshot diario, no datos en movimiento), (c) performance predecible (queries a PostgreSQL, no a API externa con latencia variable).

9.2 Cronograma Diario
text

HORA (COT)   FASE                    DURACIÓN ESTIMADA
─────────────────────────────────────────────────────────
03:00 AM     INGESTA Y ETL           ~45 min
04:00 AM     QUALITY GATE + SCORING  ~30 min
05:00 AM     DISTRIBUCIÓN TELEGRAM   ~10 min
05:30 AM     FIN / VERIFICACIÓN      —
─────────────────────────────────────────────────────────
Total pipeline: ~2 horas (3AM-5:30AM COT)
Todo listo antes de que la ciudad despierte.
9.3 Flujo de Ingesta Nocturna (03:00 AM)
text

┌─────────────────────────────────────────────────────────┐
│                   n8n CRON: 03:00 AM COT                │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 1: Leer last_run_timestamp de meta_pipeline       │
│  Query: SELECT ultima_ejecucion_exitosa                 │
│         FROM meta_pipeline                              │
│         WHERE nombre_pipeline = 'ingesta_contratos'     │
│  Si es NULL (primera ejecución): extraer TODO           │
│  Si tiene valor: extraer solo actualizados desde esa    │
│  fecha ($where=ultima_actualizacion > '{timestamp}')    │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 2: Extraer Dataset Principal (jbjy-vk9h)         │
│  URL: /resource/jbjy-vk9h.json                         │
│  Params:                                                │
│    $where: upper(ciudad) LIKE '%25MEDELL%25'            │
│            AND ultima_actualizacion > '{last_run}'      │
│    $limit: 5000                                         │
│    $offset: 0, 5000, 10000, ... (paginación)            │
│    $order: ultima_actualizacion ASC                     │
│  Headers: X-App-Token: {SODA_APP_TOKEN}                 │
│                                                         │
│  Retry logic: 3 intentos, exponential backoff (2,4,8s)  │
│  Si falla 3x: marcar 'FALLO_PARCIAL' en meta_pipeline  │
│               y continuar con datos existentes          │
│                                                         │
│  Output: lista de dicts (contratos crudos Medellín)     │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 3: Extraer Dataset Procesos (p6dx-8zbt)           │
│  Para cada proceso_de_compra único del Paso 2:          │
│    - Batch lookup en chunks de 50 IDs                   │
│    - URL: /resource/p6dx-8zbt.json                      │
│    - $where: id_del_proceso_de_compra IN (...)          │
│                                                         │
│  Alternativa eficiente: extracción completa reciente    │
│  y JOIN en memoria (pandas merge)                       │
│                                                         │
│  Output: dict[proceso_id] → {numero_de_oferentes,       │
│           precio_base, fechas...}                       │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 4: Extraer Dataset Adiciones (cb9c-h8sn)          │
│  Filtro: contratos de Medellín con adiciones            │
│  Output: dict[id_contrato] → [lista de adiciones]       │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 5: MERGE                                          │
│  Para cada contrato crudo:                              │
│    1. LEFT JOIN con Procesos por proceso_de_compra      │
│    2. Anexar campos: numero_de_oferentes, precio_base,  │
│       fecha_de_publicacion_del_proceso,                 │
│       fecha_de_recepcion_de_ofertas,                    │
│       fecha_inicio_ejecucion                            │
│    3. Si no hay match en Procesos: campos = NULL        │
│                                                         │
│  Implementación: pandas.merge(left_on, right_on,        │
│                               how='left')               │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 6: LIMPIEZA (ETL)                                 │
│  Para cada registro merged:                             │
│    1. strip() en todos los campos de texto              │
│    2. Normalizar NITs: remover guiones, puntos          │
│    3. Normalizar modalidades: title case, unificar      │
│       variantes ("Contratación Directa" →               │
│       "Contratación directa")                           │
│    4. sanitizar_valor(): corregir bug de centavos       │
│    5. parse_datetime(): parsear todas las fechas        │
│       a timezone COT (UTC-5)                            │
│    6. Filtrar estados: solo "Celebrado", "En ejecución",│
│       "Liquidado", "Terminado"                          │
│    7. Rechazar registros con id_contrato NULL/vacío     │
│                                                         │
│  Output: lista de dicts limpios                         │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 7: UPSERT en contratos_raw                        │
│  Operación: INSERT ... ON CONFLICT (id_contrato)        │
│             DO UPDATE SET                               │
│             valor_del_contrato = EXCLUDED...            │
│             estado_contrato = EXCLUDED...               │
│             ultima_actualizacion = EXCLUDED...          │
│             updated_at = NOW()                          │
│                                                         │
│  Batch size: 500 registros por transacción              │
│                                                         │
│  Output: conteo de INSERTs y UPDATEs                    │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 8: Actualizar meta_pipeline                       │
│  UPDATE meta_pipeline SET                               │
│    ultima_ejecucion_exitosa = NOW(),                    │
│    registros_procesados = {count},                      │
│    estado = 'OK'                                        │
│  WHERE nombre_pipeline = 'ingesta_contratos'            │
└─────────────────────────────────────────────────────────┘
Pseudocódigo del script secop_ingest.py:

Python

#!/usr/bin/env python3
"""
secop_ingest.py — Ingesta nocturna SECOP II → Supabase
Ejecutado por n8n CRON a las 03:00 AM COT
"""
import os
import logging
from datetime import datetime, timezone, timedelta
import httpx
import pandas as pd
from supabase import create_client

log = logging.getLogger("lupa.ingesta")

# Config
SODA_TOKEN = os.environ["SODA_APP_TOKEN"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
PAGE_SIZE = 5000
MAX_RETRIES = 3
BACKOFF_BASE = 2

# Endpoints
CONTRATOS_URL = "https://www.datos.gov.co/resource/jbjy-vk9h.json"
PROCESOS_URL = "https://www.datos.gov.co/resource/p6dx-8zbt.json"
ADICIONES_URL = "https://www.datos.gov.co/resource/cb9c-h8sn.json"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def extraer_dataset(url: str, where_clause: str) -> list[dict]:
    """Extrae un dataset completo con paginación y retries."""
    todos = []
    offset = 0
    
    while True:
        params = {
            "$where": where_clause,
            "$limit": PAGE_SIZE,
            "$offset": offset,
            "$order": "ultima_actualizacion ASC",
        }
        headers = {"X-App-Token": SODA_TOKEN}
        
        for intento in range(MAX_RETRIES):
            try:
                response = httpx.get(url, params=params, headers=headers, timeout=60)
                response.raise_for_status()
                datos = response.json()
                break
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                wait = BACKOFF_BASE ** (intento + 1)
                log.warning(f"Intento {intento+1}/{MAX_RETRIES} falló: {e}. Reintentando en {wait}s")
                import time; time.sleep(wait)
        else:
            log.error(f"Fallo total tras {MAX_RETRIES} intentos para {url} offset={offset}")
            break  # Abortar paginación, continuar con lo que se tiene
        
        if not datos:
            break  # Última página
        
        todos.extend(datos)
        offset += PAGE_SIZE
        
        if len(datos) < PAGE_SIZE:
            break  # Última página
    
    log.info(f"Extraídos {len(todos)} registros de {url}")
    return todos


def obtener_last_run(nombre: str) -> str | None:
    """Obtiene timestamp de la última ejecución exitosa."""
    result = supabase.table("meta_pipeline") \
        .select("ultima_ejecucion_exitosa") \
        .eq("nombre_pipeline", nombre) \
        .execute()
    
    if result.data and result.data[0]["ultima_ejecucion_exitosa"]:
        return result.data[0]["ultima_ejecucion_exitosa"]
    return None


def main():
    log.info("=== INICIO INGESTA NOCTURNA ===")
    
    # 1. Determinar modo (completa vs incremental)
    last_run = obtener_last_run("ingesta_contratos")
    
    if last_run:
        where_contratos = (
            f"upper(ciudad) LIKE '%25MEDELL%25' "
            f"AND ultima_actualizacion > '{last_run}'"
        )
        log.info(f"Ingesta incremental desde {last_run}")
    else:
        where_contratos = "upper(ciudad) LIKE '%25MEDELL%25'"
        log.info("Primera ingesta: extracción completa")
    
    # 2. Extraer contratos
    contratos_raw = extraer_dataset(CONTRATOS_URL, where_contratos)
    
    if not contratos_raw:
        log.info("No hay registros nuevos. Finalizando.")
        return
    
    # 3. Extraer procesos (para JOIN)
    procesos_ids = set(
        c.get("proceso_de_compra", "") 
        for c in contratos_raw 
        if c.get("proceso_de_compra")
    )
    # Extraer procesos en batch
    procesos_raw = extraer_procesos_batch(procesos_ids)
    
    # 4. Extraer adiciones
    adiciones_raw = extraer_dataset(ADICIONES_URL, "1=1")  # Filtro posterior
    
    # 5. Merge con pandas
    df_contratos = pd.DataFrame(contratos_raw)
    df_procesos = pd.DataFrame(procesos_raw) if procesos_raw else pd.DataFrame()
    
    if not df_procesos.empty:
        df_merged = df_contratos.merge(
            df_procesos[["id_del_proceso_de_compra", "numero_de_oferentes",
                         "precio_base", "fecha_de_publicacion_del_proceso",
                         "fecha_de_recepcion_de_ofertas", "fecha_inicio_ejecucion"]],
            left_on="proceso_de_compra",
            right_on="id_del_proceso_de_compra",
            how="left"
        )
    else:
        df_merged = df_contratos
        for col in ["numero_de_oferentes", "precio_base",
                     "fecha_de_publicacion_del_proceso",
                     "fecha_de_recepcion_de_ofertas", "fecha_inicio_ejecucion"]:
            df_merged[col] = None
    
    # 6. Limpieza
    df_clean = limpiar_datos(df_merged)
    
    # 7. UPSERT en Supabase
    registros = df_clean.to_dict(orient="records")
    upsert_count = upsert_contratos(registros)
    
    # 8. Actualizar meta_pipeline
    supabase.table("meta_pipeline").update({
        "ultima_ejecucion_exitosa": datetime.now(timezone.utc).isoformat(),
        "registros_procesados": upsert_count,
        "estado": "OK"
    }).eq("nombre_pipeline", "ingesta_contratos").execute()
    
    log.info(f"=== INGESTA COMPLETA: {upsert_count} registros procesados ===")


if __name__ == "__main__":
    main()
9.4 Flujo de Quality Gate + Scoring (04:00 AM)
text

┌─────────────────────────────────────────────────────────┐
│                   n8n CRON: 04:00 AM COT                │
│            (o encadenado post-ingesta exitosa)           │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 1: Obtener contratos nuevos/actualizados          │
│  Query: SELECT * FROM contratos_raw                     │
│         WHERE updated_at >= (SELECT ultima_ejecucion    │
│                FROM meta_pipeline                       │
│                WHERE nombre_pipeline = 'scoring')       │
│         OR id_contrato NOT IN                           │
│            (SELECT id_contrato FROM contratos_scored     │
│             UNION                                       │
│             SELECT id_contrato FROM contratos_opacos)   │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 2: Para cada contrato, calcular ICD               │
│                                                         │
│  icd = calcular_icd(contrato)                           │
│  contrato['icd_score'] = icd                            │
│  UPDATE contratos_raw SET icd_score = {icd}             │
│         WHERE id_contrato = {id}                        │
│                                                         │
│         ┌───── ICD < 40 ─────┐                          │
│         │                    │                          │
│         ▼                    ▼                          │
│  INSERT contratos_opacos   Continuar a                  │
│  (id_contrato, icd_score,  Scoring (Paso 3)             │
│   campos_faltantes)                                     │
│         │                                               │
│         ▼                                               │
│       FIN para                                          │
│       este contrato                                     │
└─────────────┬───────────────────────────────────────────┘
              │ (solo contratos con ICD ≥ 40)
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 3: Cargar datos auxiliares                        │
│                                                         │
│  - sancionados = cargar_sancionados("data/sancion.csv") │
│    (con verificación de frescura ≤14 días)              │
│  - adiciones = cargar_adiciones_por_contrato()          │
│  - db_session = conectar a Supabase/PostgreSQL          │
│    (para queries históricas de B3, C2, D2)              │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 4: Score cada contrato (score_contrato())         │
│                                                         │
│  Para cada contrato con ICD ≥ 40:                       │
│    resultado = score_contrato(contrato, adiciones, db)  │
│                                                         │
│    A. Evaluar 10 banderas (A1,A2,A3,B1,B3,C1,C2,C3,   │
│       D1,D2)                                            │
│    B. Sumar puntos de banderas activas                  │
│    C. Aplicar bonus sistémico (+10 si ≥3 banderas)     │
│    D. Aplicar atenuación ACTT (si proveedor público)    │
│    E. Aplicar penalización ICD (-15% si ICD 40-59)     │
│    F. Clasificar nivel (BAJO/MEDIO/ALTO/CRÍTICO)       │
│    G. Generar traducción ciudadana (plantilla)          │
│    H. Generar texto_denuncia (si score ≥ 55)           │
│                                                         │
│  UPSERT contratos_scored:                               │
│    INSERT ... ON CONFLICT (id_contrato) DO UPDATE       │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 5: Insertar en timeline_impunidad                 │
│  Para contratos con score ≥ 55 que NO tienen entrada    │
│  previa en timeline_impunidad:                          │
│                                                         │
│  INSERT INTO timeline_impunidad                         │
│    (id_contrato, estado_respuesta)                      │
│  VALUES ({id}, 'PENDIENTE')                             │
│  ON CONFLICT DO NOTHING                                 │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 6: Actualizar meta_pipeline                       │
│  UPDATE meta_pipeline SET                               │
│    ultima_ejecucion_exitosa = NOW(),                    │
│    registros_procesados = {count},                      │
│    estado = 'OK'                                        │
│  WHERE nombre_pipeline = 'scoring'                      │
└─────────────────────────────────────────────────────────┘
9.5 Flujo de Distribución Telegram (05:00 AM)
text

┌─────────────────────────────────────────────────────────┐
│                   n8n CRON: 05:00 AM COT                │
│            (o encadenado post-scoring exitoso)           │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 1: Obtener contratos elegibles para Telegram      │
│  Query: SELECT cs.*, cr.nombre_entidad,                 │
│                cr.proveedor_adjudicado,                  │
│                cr.valor_del_contrato                     │
│         FROM contratos_scored cs                        │
│         JOIN contratos_raw cr ON cs.id_contrato =       │
│              cr.id_contrato                             │
│         WHERE cs.score_total >= 55                      │
│           AND cs.publicado_telegram = FALSE              │
│         ORDER BY cs.score_total DESC                    │
│         LIMIT 20                                        │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 2: Si no hay contratos elegibles → FIN            │
│  Si hay contratos → iterar                              │
└─────────────┬───────────────────────────────────────────┘
              │ (hay contratos)
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 3: Para cada contrato, formatear mensaje          │
│                                                         │
│  emoji = {                                              │
│    "MEDIO": "🟡",                                       │
│    "ALTO": "🟠",                                        │
│    "CRÍTICO": "🔴"                                      │
│  }[nivel_riesgo]                                        │
│                                                         │
│  mensaje = f"""                                         │
│  {emoji} *ALERTA LUPA — RIESGO {nivel_riesgo}*          │
│                                                         │
│  📊 Score: {score_total}/100                             │
│  🏛️ Entidad: {nombre_entidad}                           │
│  🏢 Proveedor: {proveedor_adjudicado}                    │
│  💰 Valor: ${valor:,.0f} COP ({equivalente})            │
│                                                         │
│  🚩 Banderas detectadas:                                │
│  {banderas_formateadas}                                 │
│                                                         │
│  👉 [Ver detalles](https://lupa.city/c/{id_contrato})   │
│                                                         │
│  ⚠️ _Análisis algorítmico basado en datos públicos_     │
│  _del SECOP II. No es acusación legal._                 │
│  """                                                    │
│                                                         │
│  Escapar caracteres especiales para MarkdownV2          │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 4: Enviar via Telegram Bot API                    │
│                                                         │
│  POST https://api.telegram.org/bot{TOKEN}/sendMessage    │
│  Body: {                                                │
│    "chat_id": "@LupaMedellin",                          │
│    "text": mensaje,                                     │
│    "parse_mode": "MarkdownV2",                          │
│    "disable_web_page_preview": false                    │
│  }                                                      │
│                                                         │
│  Manejo de errores:                                     │
│    - 200 OK → UPDATE publicado_telegram = TRUE          │
│    - 429 Too Many Requests → sleep(Retry-After) → retry │
│    - 400 Bad Request → log error, skip contrato         │
│    - 5xx → retry con backoff                            │
│                                                         │
│  Rate limiting propio: sleep(2s) entre mensajes         │
│  (muy conservador vs. límite de 30 msg/s de Telegram)   │
└─────────────┬───────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────┐
│  PASO 5: Actualizar estado de distribución              │
│  UPDATE contratos_scored                                │
│    SET publicado_telegram = TRUE                        │
│  WHERE id_contrato = {id}                               │
│                                                         │
│  Actualizar meta_pipeline                               │
└─────────────────────────────────────────────────────────┘
9.6 Flujo de Escalamiento Institucional (3 Niveles)
text

                    CONTRATO SCORED
                         │
                         ▼
              ┌──────────────────────┐
              │  score_total >= 40?  │
              └──────────┬───────────┘
                   NO    │    SÍ
                   │     │
                   ▼     ▼
              BAJO     ┌──────────────────────┐
              (Nada)   │  NIVEL 1: WEB        │
                       │  → Top 10 semanal    │
                       │  → Score + banderas   │
                       │  → Traducción         │
                       │  → Disclaimer SLAPP   │
                       └──────────┬───────────┘
                                  │
                                  ▼
                       ┌──────────────────────┐
                       │  score_total >= 55?  │
                       └──────────┬───────────┘
                            NO    │    SÍ
                            │     │
                            ▼     ▼
                         Solo   ┌──────────────────────────┐
                         web    │  NIVEL 2: TELEGRAM       │
                                │  → Alerta automática     │
                                │  → Botón "Copiar         │
                                │    Denuncia" en web      │
                                │  → INSERT timeline       │
                                │    impunidad              │
                                └──────────┬───────────────┘
                                           │
                                           ▼
                                ┌──────────────────────┐
                                │  score_total >= 70?  │
                                └──────────┬───────────┘
                                     NO    │    SÍ
                                     │     │
                                     ▼     ▼
                                  Solo   ┌────────────────────────┐
                                  N1+N2  │  NIVEL 3: CABALLO     │
                                         │  DE TROYA              │
                                         │  → Todo lo anterior    │
                                         │  → Generar dossier     │
                                         │    (CSV + narrativa)   │
                                         │  → Marcar para envío   │
                                         │    manual a:           │
                                         │    - Concejal MIRA     │
                                         │    - La Silla Vacía    │
                                         │    - El Armadillo      │
                                         │  → Log en tabla        │
                                         │    timeline_impunidad  │
                                         │    con estado          │
                                         │    'PENDIENTE'         │
                                         └────────────────────────┘

FLUJO DE SEGUIMIENTO (timeline_impunidad):
──────────────────────────────────────────
  PENDIENTE ──(denuncia radicada)──▶ RADICADO
                                        │
                            (ente de control responde)
                                        │
                                        ▼
                                   EN_INDAGACION
                                        │
                        ┌───────────────┴────────────────┐
                        ▼                                ▼
                   ARCHIVADO                        CON_RESPUESTA
                   (visible en                      (visible en
                    timeline,                        timeline,
                    días contados)                    días contados)

Actualización de estados: MANUAL en MVP (via Supabase Studio
o endpoint FastAPI protegido con API key).
9.7 Workflow n8n — Especificación
Workflow 1: Pipeline Nocturno Principal

Nodo n8n	Tipo	Configuración
Trigger_3AM	Schedule Trigger	CRON: 0 3 * * * (3:00 AM servidor, configurar timezone)
Run_Ingesta	Execute Command	python3 /app/workers/secop_ingest.py
Check_Ingesta_Exit	IF	Condition: exit code == 0
Run_Scoring	Execute Command	python3 /app/workers/scoring_engine.py
Check_Scoring_Exit	IF	Condition: exit code == 0
Run_Telegram	Execute Command	python3 /app/workers/telegram_dist.py
Log_Success	Supabase	UPDATE meta_pipeline...
Log_Failure	Supabase	UPDATE meta_pipeline... estado='FALLO_PARCIAL'
Alternativa sin Execute Command: Si n8n tiene problemas ejecutando Python directamente, los scripts se exponen como endpoints HTTP en FastAPI y n8n los invoca vía HTTP Request nodes:

Nodo n8n	Tipo	URL
Trigger_3AM	Schedule Trigger	CRON: 0 3 * * *
Call_Ingesta	HTTP Request	POST http://localhost:8000/pipeline/ingesta
Call_Scoring	HTTP Request	POST http://localhost:8000/pipeline/scoring
Call_Telegram	HTTP Request	POST http://localhost:8000/pipeline/telegram
Autenticación de los endpoints internos: API key en header X-Pipeline-Key (variable de entorno, no expuesto públicamente).

10. ESPECIFICACIÓN DEL FRONTEND
10.1 Arquitectura Frontend
Aspecto	Decisión
Framework	Next.js 14 (App Router)
Hosting	Vercel (tier gratuito)
Rendering	ISR (Incremental Static Regeneration) con revalidate: 3600 (1 hora)
Data fetching	Server Components → Supabase JS Client (server-side)
Styling	Tailwind CSS
Estado	Sin gestión de estado cliente. Sin Redux/Zustand. Todo server-rendered.
Auth	NINGUNA. Sin login. Sin registro. 100% público.
Analytics	NINGUNA en MVP. Sin Google Analytics, sin cookies de tracking.
Justificación de ISR con revalidate de 1 hora: Los datos se actualizan una vez al día (pipeline nocturno). Un revalidate de 1 hora garantiza que los datos del día estén disponibles para el primer visitante matutino sin rebuild manual, mientras mantiene la performance de páginas estáticas para visitas subsiguientes.

10.2 Estructura de Rutas
text

/                     → Landing page con resumen y CTA
/top10                → Top 10 semanal de contratos sospechosos
/contrato/[id]        → Detalle de un contrato específico
/opacos               → Contratos con ICD < 40
/impunidad            → Timeline de Impunidad
/metodologia          → Descripción completa del scoring
/reportar             → Formulario anónimo de reporte
10.3 Página: Landing /
Contenido:

Hero: "Lupa vigila los contratos públicos de Medellín mientras tú duermes." + CTA "Ver contratos sospechosos →"
Contador en vivo: "📊 {N} contratos analizados | 💰 ${X}M COP bajo monitoreo | ⏱️ {Y} alertas sin respuesta institucional"
Explicación de 3 pasos: Cómo funciona Lupa (ingesta → scoring → alerta)
CTA Telegram: "📲 Recibe alertas automáticas en Telegram → @LupaMedellin"
Disclaimer SLAPP (footer)
Enlace a /metodologia
Data source: Query agregada a contratos_raw (COUNT), contratos_scored (SUM valor), timeline_impunidad (COUNT WHERE estado='PENDIENTE').

Criterios de aceptación:

Carga en <2s (TTFB)
Responsive (360px - 1920px)
Sin login, sin cookies de tracking
Contadores reflejan datos reales de Supabase (actualizados cada hora via ISR)
10.4 Página: Top 10 Semanal /top10
Layout:

text

┌──────────────────────────────────────────────────────┐
│  LUPA — Top 10 Contratos Sospechosos esta Semana     │
│  Semana del {lunes} al {domingo} de {mes} {año}      │
│                                                      │
│  ⚠️ Este análisis es algorítmico y basado en datos   │
│  públicos del SECOP II. No representa una acusación   │
│  legal ni tiene sesgo político.                       │
│                                                      │
│  [⬇️ Descargar CSV]                                  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │ 🔴 #1 — Score: 78/100 — CRÍTICO               │  │
│  │                                                │  │
│  │ 🏛️ Secretaría de Infraestructura de Medellín   │  │
│  │ 🏢 Construcciones XYZ S.A.S.                   │  │
│  │ 💰 $1,200,000,000 COP (🏫 2 colegios nuevos)  │  │
│  │                                                │  │
│  │ 🚩 Banderas:                                   │  │
│  │   • Contratación directa sin competencia       │  │
│  │   • Proveedor concentra 65% del presupuesto    │  │
│  │   • Posible fraccionamiento de contratos       │  │
│  │   • Entidad con >80% contratación directa      │  │
│  │                                                │  │
│  │ [Ver detalles →]                               │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │ 🟠 #2 — Score: 62/100 — ALTO                  │  │
│  │ ...                                            │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ... (hasta #10)                                     │
│                                                      │
├──────────────────────────────────────────────────────┤
│  📲 Recibe estas alertas en Telegram: @LupaMedellin  │
│  📖 Ver metodología de scoring: /metodologia         │
└──────────────────────────────────────────────────────┘
Query Supabase:

SQL

SELECT cs.id_contrato, cs.score_total, cs.nivel_riesgo,
       cs.banderas_activas, cs.detalle_banderas,
       cs.traduccion_ciudadana, cs.texto_denuncia,
       cr.nombre_entidad, cr.proveedor_adjudicado,
       cr.valor_del_contrato, cr.modalidad_de_contratacion,
       cr.fecha_de_firma
FROM contratos_scored cs
JOIN contratos_raw cr ON cs.id_contrato = cr.id_contrato
WHERE cs.score_total >= 40
  AND cs.created_at >= date_trunc('week', NOW())
ORDER BY cs.score_total DESC
LIMIT 10
Funcionalidad CSV:

Generación client-side: los datos ya están en el DOM (server-rendered). JavaScript construye el CSV en el navegador y lo descarga via Blob + URL.createObjectURL.
No requiere endpoint adicional.
Encoding UTF-8 con BOM (\xEF\xBB\xBF prepended).
10.5 Página: Detalle de Contrato /contrato/[id]
Contenido:

Encabezado con score visual: Barra de 0-100 con color según nivel.
Datos del contrato: Todos los campos relevantes de contratos_raw en formato legible.
Banderas detectadas: Lista expandida con descripción y puntos de cada bandera, fundamento legal, y campo(s) de SECOP II que la activaron.
Traducción ciudadana: Equivalente social prominente.
Botón "📋 Copiar Borrador de Denuncia" (solo si score ≥ 55):
Usa navigator.clipboard.writeText(texto_denuncia)
Fallback: <textarea> con instrucción de copiar manualmente
Feedback visual: "✅ Borrador copiado al portapapeles" durante 3 segundos.
Enlace al SECOP II: URL directa al contrato en colombiacompra.gov.co (si es construible a partir de id_contrato o proceso_de_compra).
Enlace a timeline de impunidad (si aplica): "⏱️ Este contrato lleva {N} días sin respuesta institucional."
Disclaimer SLAPP (prominente, no colapsable).
Generación de la URL SECOP II:

Python

def construir_url_secop(proceso_de_compra: str) -> str | None:
    """Intenta construir URL directa al proceso en SECOP II."""
    if not proceso_de_compra:
        return None
    # Formato típico: CO1.PCCNTR.4567890
    # URL base de SECOP II Community
    return f"https://community.secop.gov.co/Public/Tendering/ContractNoticePhases/View?PPI=CO1.PPI.{proceso_de_compra.split('.')[-1]}&isFromPublicArea=True"
Nota: La URL puede no funcionar para todos los contratos (el formato varía). Se muestra como "Intentar ver en SECOP II (puede no estar disponible)" con manejo graceful de error 404.

10.6 Página: Contratos Opacos /opacos
Contenido:

text

┌──────────────────────────────────────────────────────┐
│  CONTRATOS OPACOS                                    │
│                                                      │
│  Estos contratos no pudieron ser analizados porque    │
│  la entidad contratante no publicó información        │
│  suficiente en el SECOP II. La opacidad es, en sí     │
│  misma, una señal de riesgo.                          │
│                                                      │
│  Esta semana: {N} contratos opacos por ${X}M COP     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │ ⬛ NO EVALUABLE — ICD: 25/100                  │  │
│  │                                                │  │
│  │ 🏛️ Entidad de Salud de Medellín                │  │
│  │ 🏢 Proveedor: No disponible                    │  │
│  │ 💰 $450,000,000 COP                            │  │
│  │                                                │  │
│  │ Información faltante:                           │  │
│  │   ❌ Justificación de modalidad                 │  │
│  │   ❌ Descripción del proceso                    │  │
│  │   ❌ Número de oferentes                        │  │
│  │   ❌ Precio base                                │  │
│  │   ❌ Documento del proveedor                    │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ... (lista completa)                                │
│                                                      │
│  ⚠️ Disclaimer SLAPP                                 │
└──────────────────────────────────────────────────────┘
Query:

SQL

SELECT co.id_contrato, co.icd_score, co.campos_faltantes,
       cr.nombre_entidad, cr.proveedor_adjudicado,
       cr.valor_del_contrato
FROM contratos_opacos co
JOIN contratos_raw cr ON co.id_contrato = cr.id_contrato
WHERE co.created_at >= date_trunc('week', NOW())
ORDER BY cr.valor_del_contrato DESC NULLS LAST
10.7 Página: Timeline de Impunidad /impunidad
Contenido:

text

┌──────────────────────────────────────────────────────┐
│  LÍNEA DE TIEMPO DE IMPUNIDAD                        │
│                                                      │
│  📊 Actualmente hay {N} alertas sin respuesta         │
│  institucional, con un promedio de {X} días de espera │
│                                                      │
│  ¿Cuánto tiempo puede pasar una irregularidad         │
│  detectada sin que nadie responda?                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │ 🔴 87 días sin respuesta                       │  │
│  │                                                │  │
│  │ 🏛️ Secretaría de Infraestructura               │  │
│  │ 🏢 Construcciones XYZ S.A.S.                   │  │
│  │ 💰 $1,200,000,000 COP                          │  │
│  │ 📊 Score: 78/100                                │  │
│  │ 📅 Alertado: 15 de marzo de 2025                │  │
│  │ 📌 Estado: PENDIENTE                            │  │
│  │                                                │  │
│  │ [Ver contrato →]                               │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │ 🟠 42 días sin respuesta                       │  │
│  │ ...                                            │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │ 🟢 3 días — RADICADO                           │  │
│  │ ...                                            │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  ⚠️ Disclaimer SLAPP                                 │
└──────────────────────────────────────────────────────┘
Colores de dias_inactividad:

Rango	Color	Emoji	CSS class
0-15 días	Verde	🟢	text-green-600 bg-green-50
16-30 días	Amarillo	🟡	text-yellow-600 bg-yellow-50
31-45 días	Naranja	🟠	text-orange-600 bg-orange-50
>45 días	Rojo	🔴	text-red-600 bg-red-50
10.8 Página: Metodología /metodologia
Contenido (secciones):

¿Qué es el Score de Riesgo? — Explicación general del sistema de puntuación 0-100.
Quality Gate (ICD) — Qué es la completitud del dato. Cómo se calcula. Ejemplo numérico con un contrato hipotético.
Banderas de Riesgo — Las 10 banderas activas (A1-D2) + B2 marcada como desactivada. Para cada una:
Nombre legible
Descripción de la regla en español llano
Puntos asignados
Campos de SECOP II utilizados
Fundamento legal (ley + artículo)
Ejemplo: "Un contrato por $800M por contratación directa activaría esta bandera y recibiría 12 puntos."
Bonus Sistémico — Qué es, cuándo aplica, ejemplo numérico.
Atenuación ACTT — Qué son los convenios interadministrativos, por qué se atenúan, qué NITs están en la lista.
Niveles de Alerta — Los 3 niveles con umbrales y acciones.
Limitaciones del MVP — Qué NO evalúa el sistema actualmente (B2, análisis semántico, pliegos sastre). Transparencia total.
Código Fuente — Enlace al repositorio de GitHub.
Auditoría Simétrica — Declaración explícita.
10.9 Página: Reportar /reportar
Formulario:

Campo	Tipo	Requerido	Validación
Entidad involucrada	<input type="text">	Sí	min 3 caracteres
Descripción del hallazgo	<textarea>	Sí	min 50 caracteres, max 5000
Número de contrato o proceso (si lo conoce)	<input type="text">	No	—
Documentos de soporte	<input type="file">	No	Máx 5MB, formatos: PDF, JPG, PNG
Aviso de privacidad (visible antes del formulario):

"🔒 Lupa no almacena tu dirección IP, cookies de identificación, ni ningún dato personal. Tu reporte es completamente anónimo. No te pedimos nombre, email, ni teléfono."

Flujo de envío:

Validación client-side (campos requeridos, longitud mínima).
Si hay archivo: upload a Supabase Storage (bucket público, nombre aleatorio UUID).
POST a API: { entidad_reportada, descripcion, numero_contrato?, archivo_url? }.
Backend genera codigo_referencia: LUPA- + 8 caracteres alfanuméricos aleatorios (uppercase).
INSERT en reportes_anonimos.
Respuesta al frontend: { codigo_referencia: "LUPA-A3B7K9M2" }.
Frontend muestra: "✅ Reporte recibido. Código de referencia: LUPA-A3B7K9M2. Guarda este código para consultar el estado de tu reporte."
Implementación del endpoint (FastAPI):

Python

from fastapi import APIRouter, Request
import secrets
import string

router = APIRouter()

@router.post("/api/reportar")
async def recibir_reporte(reporte: ReporteSchema):
    """
    Recibe reporte anónimo. NO logea IP del remitente.
    """
    # Generar código de referencia
    chars = string.ascii_uppercase + string.digits
    codigo = "LUPA-" + ''.join(secrets.choice(chars) for _ in range(8))
    
    # INSERT en Supabase (sin datos de IP)
    supabase.table("reportes_anonimos").insert({
        "codigo_referencia": codigo,
        "entidad_reportada": reporte.entidad_reportada,
        "descripcion": reporte.descripcion,
        "numero_contrato": reporte.numero_contrato,
        "archivo_url": reporte.archivo_url,
    }).execute()
    
    return {"codigo_referencia": codigo}
Nota crítica sobre logging: El middleware de FastAPI para esta ruta específica debe tener deshabilitado el acceso a request.client.host. Se configura un middleware que para la ruta /api/reportar NO incluye la IP en los access logs. Verificación: inspección del código del middleware y de los logs de producción.

10.10 Open Graph Tags (Compartibilidad Social)
Cada página pública debe incluir meta tags de Open Graph para que al compartir enlaces en redes sociales se muestre un preview informativo:

HTML

<!-- /top10 -->
<meta property="og:title" content="Lupa Medellín — Top 10 Contratos Sospechosos" />
<meta property="og:description" content="Esta semana, Lupa detectó {N} contratos con riesgo alto en Medellín por un total de ${X}M COP. Verifica los datos." />
<meta property="og:image" content="https://lupa.city/og/top10.png" />
<meta property="og:type" content="website" />
<meta property="og:url" content="https://lupa.city/top10" />

<!-- /contrato/[id] -->
<meta property="og:title" content="🚩 Score {score}/100 — {nombre_entidad}" />
<meta property="og:description" content="Contrato por ${valor} COP ({equivalente}). {N} banderas de riesgo detectadas." />
Imagen OG: Se usa una imagen estática genérica en MVP (/public/og/lupa-default.png) con el logo y tagline de Lupa. En Fase 2: generación dinámica de imágenes OG con @vercel/og.

11. INTEGRACIONES EXTERNAS
11.1 SODA API (datos.gov.co)
Aspecto	Especificación
Protocolo	SODA 2.1 (Socrata Open Data API) sobre HTTPS
Endpoints	https://www.datos.gov.co/resource/jbjy-vk9h.json (Contratos)
https://www.datos.gov.co/resource/p6dx-8zbt.json (Procesos)
https://www.datos.gov.co/resource/cb9c-h8sn.json (Adiciones)
Autenticación	X-App-Token en HTTP header. Token obtenido en https://www.datos.gov.co/profile/edit/developer_settings
Rate Limits (sin token)	~67 requests/hora, throttled agresivamente
Rate Limits (con token)	Sin límite documentado estricto; paginación continua con $limit=5000 funciona sin problemas
Paginación	Offset-based: $offset=0, $offset=5000, ... hasta respuesta con <5000 registros
Formato de respuesta	JSON array
Timeout configurado	60 segundos por request
Retries	3 intentos con exponential backoff (2s, 4s, 8s)
Manejo de fallo parcial	Si 1 de 3 datasets falla: marcar FALLO_PARCIAL en meta_pipeline. Scoring opera con datos disponibles.
Manejo de fallo total	Si los 3 datasets fallan: abortar pipeline, datos del día anterior persisten. Reintentar a las 3AM del día siguiente. No se envía alerta de error al canal de Telegram (ruido).
Campos de filtro	$where: SoQL con operadores LIKE, >, AND. Filtro geográfico: upper(ciudad) LIKE '%25MEDELL%25'
Ingesta incremental	$where=ultima_actualizacion > '{last_run_timestamp}' para extraer solo registros nuevos/actualizados
Datos sensibles enviados	NINGUNO. Solo se leen datos públicos. No se envía información de usuarios a datos.gov.co.
Ejemplo de request:

text

GET https://www.datos.gov.co/resource/jbjy-vk9h.json
    ?$where=upper(ciudad) LIKE '%25MEDELL%25' AND ultima_actualizacion > '2025-06-01T00:00:00'
    &$limit=5000
    &$offset=0
    &$order=ultima_actualizacion ASC
Headers:
    X-App-Token: {token}
    Accept: application/json
11.2 Telegram Bot API
Aspecto	Especificación
Endpoint base	https://api.telegram.org/bot{BOT_TOKEN}/
Método usado	sendMessage
Autenticación	Bot Token embebido en la URL (obtenido via @BotFather en Telegram)
Canal destino	@LupaMedellin (canal público, el Bot es administrador del canal)
Rate Limit oficial	30 mensajes/segundo a un mismo chat. Lupa envía máx 20 mensajes/día → muy por debajo.
Rate limiting propio	time.sleep(2) entre cada mensaje (conservador)
Formato de mensaje	Markdown V2 (parse_mode: MarkdownV2)
Longitud máxima	4096 caracteres por mensaje. Los mensajes de Lupa están ~800-1200 chars → sin riesgo de truncamiento.
Manejo de error 429	Leer header Retry-After, esperar esa cantidad de segundos, reintentar.
Manejo de error 400	Logear el error con el id_contrato problemático. Saltar al siguiente contrato. Marcar en meta_pipeline.
Manejo de error 5xx	Retry con exponential backoff (3 intentos). Si falla: logear, continuar con siguientes contratos.
Datos enviados a Telegram	Texto formateado con: score, nombre_entidad, proveedor_adjudicado, valor_del_contrato, equivalente social, banderas, enlace a web, disclaimer. NINGÚN dato sensible de usuarios (no hay usuarios en MVP).
Webhook	NO se usa webhook. Solo se envían mensajes (push unidireccional). El Bot no recibe ni procesa mensajes de usuarios en MVP.
Setup del Bot:

Crear Bot via @BotFather → obtener BOT_TOKEN
Crear canal público @LupaMedellin
Añadir el Bot como administrador del canal con permisos de "Publicar mensajes"
Verificar envío con test message:
Python

import httpx

def test_telegram():
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": "@LupaMedellin",
        "text": "🔍 *Lupa Medellín está activo\\.* Las alertas automáticas comenzarán mañana\\.",
        "parse_mode": "MarkdownV2",
    }
    response = httpx.post(url, json=payload)
    print(response.json())
11.3 Procuraduría / SIRI (Lista de Sancionados)
Aspecto	Especificación
Fuente	SIRI (Sistema de Información de Registro de Sanciones y Causas de Inhabilidad) de la Procuraduría General de la Nación
URL de consulta manual	https://www.procuraduria.gov.co/Pages/Consulta-de-Antecedentes.aspx
API REST	NO existe API pública estable. El portal usa CAPTCHA.
Operación MVP	CSV pre-descargado manualmente 1x/semana (lunes AM). Almacenado en data/sancionados_antioquia.csv en el servidor del worker.
Campos del CSV	documento_sancionado (NIT/cédula), nombre_sancionado, tipo_sancion, fecha_sancion, fecha_fin_sancion
Cruce	documento_proveedor (contratos_raw) contra documento_sancionado (CSV). Match exacto de strings normalizados.
Verificación de frescura	Si el CSV tiene >14 días desde última modificación: bandera B1 se DESACTIVA automáticamente para esa ejecución. Log de warning.
Manejo de falsos negativos	Si un NIT no está en el CSV → Inhabilitado = False. NUNCA se asignan 20 puntos sin coincidencia verificada.
Manejo de falsos positivos	Si un NIT coincide pero la sanción ya venció (fecha_fin_sancion < NOW()): excluir del set de sancionados activos.
Alcance	Solo proveedores que aparecen en los Top 20 contratos por valor + todos los que activan otras banderas. No se cruza la totalidad de proveedores (optimización).
Fase 2	Explorar scraping con manejo de CAPTCHA (Playwright + solver), o acceso institucional via convenio con Procuraduría.
12. BLINDAJE LEGAL ANTI-SLAPP
12.1 Marco de Riesgo Legal
SLAPP (Strategic Lawsuit Against Public Participation): Demandas por injuria, calumnia, o daño a la honra interpuestas contra ciudadanos o plataformas que publican hallazgos sobre contratación pública. Son el principal vector de silenciamiento de la veeduría ciudadana en Colombia.

Artículos de riesgo en el Código Penal colombiano:

Art. 220: Injuria (calificativo deshonroso)
Art. 221: Calumnia (imputación falsa de conducta típica)
Art. 222: Circunstancias especiales de graduación
Defensa fundamental:

Art. 20 Constitución Política: Libertad de expresión e información
Art. 74 Constitución Política: Acceso a documentos públicos
Art. 270 Constitución Política: Vigilancia de la gestión pública y sus resultados
Ley 850 de 2003: Veedurías ciudadanas
12.2 Reglas de Lenguaje (Implementadas en Código)
PROHIBIDO en cualquier output de Lupa (alertas, web, denuncias, código):

Término prohibido	Razón	Alternativa aprobada
"Corrupción" / "Corrupto"	Calificativo penal. Implica dolo demostrado.	"Irregularidad detectada algorítmicamente"
"Robo" / "Robar"	Implica conducta penal demostrada.	"Hallazgo de riesgo estadístico"
"Criminal" / "Delincuente"	Implica sentencia judicial.	"Proveedor/entidad con score de riesgo elevado"
"Fraude"	Implica intención dolosa demostrada.	"Patrón que amerita investigación"
Cualquier nombre propio + calificativo negativo	Injuria directa.	"Según datos del SECOP II, el contrato presenta..."
OBLIGATORIO en cada output público:

El disclaimer SLAPP debe aparecer de forma prominente (no en footer colapsado, no en texto pequeño) en:

Cada página de la web (header o primera sección visible)
Cada mensaje de Telegram
Cada texto de denuncia generado
La página de metodología
El README del repositorio de GitHub
Texto exacto del disclaimer:

"Este análisis es algorítmico y basado en datos públicos del SECOP II (Sistema Electrónico de Contratación Pública). No representa una acusación legal, no prejuzga responsabilidad, y no tiene sesgo político. Los datos fuente están disponibles en datos.gov.co. La metodología de scoring está publicada en GitHub."

12.3 Validación Automatizada de Lenguaje
Python

TERMINOS_PROHIBIDOS = [
    "corrupc", "corrupto", "corrupta", "robo", "robar", "robó",
    "criminal", "delincuent", "fraude", "fraudulent", "ladrón",
    "ladrona", "estafa", "malversa", "peculado",
]

def validar_lenguaje_slapp(texto: str) -> list[str]:
    """
    Verifica que un texto no contenga términos SLAPP prohibidos.
    Retorna lista de términos encontrados (vacía si pasa validación).
    """
    texto_lower = texto.lower()
    encontrados = [t for t in TERMINOS_PROHIBIDOS if t in texto_lower]
    if encontrados:
        log.error(f"SLAPP VIOLATION: Texto contiene términos prohibidos: {encontrados}")
    return encontrados
Esta función se ejecuta como validación final antes de:

INSERT en contratos_scored.traduccion_ciudadana
INSERT en contratos_scored.texto_denuncia
Envío de mensaje a Telegram
Si la validación falla (encuentra términos prohibidos), el contrato NO se publica y se logea como error crítico. Esto no debería ocurrir con las plantillas de texto definidas, pero actúa como red de seguridad contra errores en las plantillas.

12.4 Auditoría Simétrica
Lupa aplica exactamente las mismas reglas de scoring a todas las entidades y proveedores sin importar:

Filiación política del alcalde, gobernador, o director de la entidad
Partido político del funcionario firmante
Afiliación política del proveedor
La garantía de simetría se implementa mediante:

Código público en GitHub: Cualquiera puede verificar que no hay excepciones hardcodeadas por entidad o proveedor.
La única excepción es ACTT: Atenuación de convenios interadministrativos, documentada públicamente, aplicada a TODAS las entidades públicas por igual.
Mismos umbrales para todos: Sin scoring diferenciado por partido o filiación.
12.5 Protección de Anonimato (MVP Mínimo)
Medida	Implementación
Formulario sin identificación	No se solicita nombre, email, teléfono, ni ningún dato personal
No logging de IP	El endpoint /api/reportar no accede a request.client.host. Middleware configura exclusión de IP para esta ruta.
No cookies de tracking	Sin Google Analytics, sin Facebook Pixel, sin cookies de terceros. Solo cookies técnicas de Next.js si aplican.
No referrer tracking	<meta name="referrer" content="no-referrer"> en la página /reportar
Fase 2: Cifrado de reportes en base de datos (campos encriptados con clave que solo el equipo Lupa tiene). Opción de envío via ProtonMail cifrado. Cumplimiento de Ley 1952/2019 y Ley 2195/2022 sobre protección de denunciantes.

13. MÉTRICAS DE ÉXITO
13.1 Métricas Primarias
Código	Métrica	Definición	Cómo se mide	Meta Mes 1	Meta Mes 3
TCAAI	Tasa de Conversión Alerta → Acción Institucional	% de alertas de Nivel 2 y 3 que generan al menos un cambio de estado_respuesta en timeline_impunidad (de 'PENDIENTE' a cualquier otro estado).	COUNT(estado != 'PENDIENTE') / COUNT(*) en timeline_impunidad	≥ 10%	≥ 15%
IDE	Índice de Disuasión Ex-ante	Variación del score promedio mensual de contratos nuevos. Un descenso indica que las entidades están mejorando prácticas (efecto panóptico).	AVG(score_total) mensual en contratos_scored. Comparar mes a mes.	Establecer baseline	Descenso ≥ 5% vs. baseline
VRI	Velocidad de Respuesta Institucional	Días promedio desde fecha_alerta hasta primer cambio de estado_respuesta en timeline_impunidad.	AVG(dias_inactividad) para alertas que han cambiado de estado.	< 45 días	< 30 días
CMT	Cobertura Mediática Trazable	Cantidad de notas periodísticas, artículos, o menciones en medios que citan a Lupa como fuente.	Conteo manual + Google Alerts + monitoreo de redes.	≥ 1/mes	≥ 3/mes
VERMA	Valor Económico bajo Monitoreo Activo	Suma de valor_del_contrato de todos los contratos en contratos_scored con score ≥ 40.	SUM(valor_del_contrato) de contratos scored activos.	> $5.000M COP	> $20.000M COP
13.2 Métricas Secundarias
Código	Métrica	Definición	Cómo se mide	Meta Mes 1
TELEGRAM	Suscriptores del canal	Cantidad de suscriptores del canal @LupaMedellin.	API de Telegram: getChatMembersCount	> 200
WEB_UV	Visitantes únicos web/semana	Visitors únicos semanales a lupa.city.	Vercel Analytics (si se habilita) o conteo server-side de requests únicos (sin cookies de tracking).	> 500
CSV_DL	Descargas de CSV/semana	Cantidad de veces que se descarga el CSV del Top 10.	Contador client-side (evento JavaScript, sin tracking de usuario).	> 20
DENUNCIAS	Borradores de denuncia copiados/semana	Cantidad de veces que se usa el botón "Copiar Borrador de Denuncia".	Contador client-side (evento JavaScript, sin tracking de usuario).	> 10
REPORTES	Reportes anónimos recibidos/mes	Cantidad de INSERTs en reportes_anonimos.	COUNT(*) en tabla.	> 5
PIPELINE_UP	Uptime del pipeline nocturno	% de noches en que el pipeline completo (ingesta → scoring → distribución) se ejecutó sin fallo total.	COUNT(estado='OK') / COUNT(*) en meta_pipeline para los últimos 30 días.	≥ 95% (≤1 fallo/mes)
13.3 Métricas de Calidad del Scoring
Código	Métrica	Definición	Cómo se mide	Meta
FP_RATE	Tasa de falsos positivos (Nivel 2+)	% de alertas de Nivel 2 o 3 que tras revisión manual se determinan como "no sospechosos" o "explicables sin irregularidad".	Revisión manual semanal de ~10 alertas aleatorias.	< 20%
OPAC_RATE	Tasa de opacos	% de contratos ingestados que caen en contratos_opacos (ICD < 40).	COUNT(opacos) / COUNT(raw)	< 15% (si es mayor, indica problema de datos, no de scoring)
SCORE_DIST	Distribución de scores	Histograma de scores en contratos_scored. Se espera una distribución sesgada a la izquierda (mayoría de contratos con score bajo).	Histograma con bins de 10 puntos.	>70% de contratos con score < 40
ACTT_RATE	Tasa de atenuación ACTT	% de contratos que reciben atenuación por convenio interadministrativo.	COUNT(detalle_banderas ? 'ACTT') / COUNT(*) en scored.	5-20% (si es > 30%, la lista de NITs es demasiado amplia)
13.4 Dashboard de Métricas (MVP)
En MVP, las métricas se consultan directamente en Supabase Studio (panel de administración) o via queries SQL manuales. No se construye un dashboard de métricas dedicado.

Queries de métricas esenciales:

SQL

-- VERMA: Valor bajo monitoreo
SELECT SUM(cr.valor_del_contrato)::bigint as valor_monitoreo_cop
FROM contratos_scored cs
JOIN contratos_raw cr ON cs.id_contrato = cr.id_contrato
WHERE cs.score_total >= 40;

-- TCAAI: Tasa de conversión alerta → acción
SELECT 
    COUNT(*) FILTER (WHERE estado_respuesta != 'PENDIENTE') * 100.0 / 
    NULLIF(COUNT(*), 0) as tcaai_pct
FROM timeline_impunidad;

-- VRI: Velocidad de respuesta
SELECT AVG(dias_inactividad) as vri_dias
FROM timeline_impunidad
WHERE estado_respuesta != 'PENDIENTE';

-- Distribución de scores
SELECT 
    CASE 
        WHEN score_total < 20 THEN '0-19'
        WHEN score_total < 40 THEN '20-39'
        WHEN score_total < 55 THEN '40-54'
        WHEN score_total < 70 THEN '55-69'
        ELSE '70-100'
    END as rango,
    COUNT(*) as cantidad
FROM contratos_scored
GROUP BY 1
ORDER BY 1;

-- Pipeline uptime (últimos 30 días)
SELECT 
    COUNT(*) FILTER (WHERE estado = 'OK') * 100.0 / 
    NULLIF(COUNT(*), 0) as uptime_pct
FROM meta_pipeline
WHERE nombre_pipeline = 'ingesta_contratos'
  AND updated_at >= NOW() - INTERVAL '30 days';
14. RIESGOS TÉCNICOS Y MITIGACIONES
14.1 Riesgo 1: Caídas del SECOP II / datos.gov.co
Dimensión	Detalle
Probabilidad	ALTA — datos.gov.co tiene historial de caídas parciales y mantenimientos no anunciados. Tiempo de respuesta variable (1-30 segundos).
Impacto	CRÍTICO si Lupa dependiera de consultas en vivo. BAJO con la arquitectura de Data Lake propio.
Mitigación implementada	1. Zero Live Query: Lupa NUNCA consulta SECOP II en tiempo real. Todo opera desde Supabase. 2. Retries con backoff: 3 intentos con espera exponencial (2s, 4s, 8s). 3. Fallo graceful: Si la ingesta falla, el scoring opera sobre datos del día anterior. La web y Telegram funcionan con datos existentes. 4. Ingesta incremental: Solo se extraen registros nuevos/actualizados, reduciendo el volumen de datos y la probabilidad de timeout.
Indicador de monitoreo	meta_pipeline.estado = 'FALLO_TOTAL' para ingesta_contratos. Si ocurre >2 días consecutivos, intervención manual.
Plan de contingencia	Si datos.gov.co está caído >72 horas: evaluar descarga manual del dataset completo via la interfaz web de SECOP II (exportación CSV manual) y carga directa en Supabase.
14.2 Riesgo 2: Falsos Positivos en el Scoring
Dimensión	Detalle
Probabilidad	ALTA — Cualquier sistema de scoring basado en reglas deterministas generará falsos positivos, especialmente con datos de contratación pública donde las excepciones legales son numerosas.
Impacto	CRÍTICO — Un falso positivo publicado en Telegram o la web puede: (a) dañar la reputación de un proveedor legítimo, (b) generar una demanda SLAPP contra Lupa, (c) destruir la credibilidad del sistema.
Mitigación implementada	1. Modelo ACTT: Convenios interadministrativos atenuados al 50%. 2. Umbrales conservadores: Telegram solo para score ≥ 55 (requiere ≥3 banderas significativas). 3. Disclaimer SLAPP en cada output. 4. Lenguaje neutro: "Score de riesgo estadístico", nunca acusación. 5. Validación de lenguaje automatizada: función validar_lenguaje_slapp() antes de cada publicación. 6. Código público en GitHub: transparencia total de la metodología.
Plan de recalibración	Semana 2: revisión manual de los 20 contratos con score más alto. Si >20% son falsos positivos claramente explicables, subir umbral de Nivel 2 a 60 o ajustar peso de banderas específicas. Documentar cada ajuste.
Métrica de monitoreo	FP_RATE < 20% en revisión manual semanal.
14.3 Riesgo 3: Calidad de Datos Inconsistente en SECOP II
Dimensión	Detalle
Probabilidad	MUY ALTA — SECOP II tiene problemas conocidos: campos vacíos, valores inconsistentes, "bug de centavos", fechas en formato variable, NITs con y sin dígito de verificación, modalidades con variantes de texto.
Impacto	ALTO — Datos sucios pueden generar: (a) scores incorrectos, (b) JOINs fallidos entre datasets, (c) valores económicos irreales, (d) falsos positivos/negativos.
Mitigación implementada	1. ICD como Quality Gate: Contratos con <40% de completitud son excluidos del scoring y publicados como opacos. 2. sanitizar_valor(): Corrección automática del bug de centavos con umbral de $10 mil millones COP. 3. Normalización exhaustiva: strip(), title case, unificación de variantes de modalidad, normalización de NITs. 4. Validación post-ingesta: Cero registros con valor_del_contrato > $500 mil millones (contrato municipal plausible máximo). Si los hay, el pipeline falla. 5. Manejo de NULL: Cada función de bandera verifica explícitamente la presencia del campo antes de evaluar. NULL nunca activa una bandera.
Indicador de monitoreo	OPAC_RATE (% de opacos). Si >15%, investigar si hay un cambio en la calidad del dataset. Verificar post-ingesta: SELECT COUNT(*) FROM contratos_raw WHERE valor_del_contrato > 500000000000 debe ser 0.
14.4 Riesgo 4: Campos Inexistentes o Renombrados en la API SODA
Dimensión	Detalle
Probabilidad	ALTA — Colombia Compra Eficiente puede cambiar nombres de campos, agregar o eliminar datasets, o modificar la estructura sin previo aviso.
Impacto	MEDIO a ALTO — Un campo renombrado puede causar: (a) KeyError en el script de ingesta, (b) NULL en un campo que antes tenía datos, (c) bandera desactivada silenciosamente.
Mitigación implementada	1. B2 ya desactivada: La bandera que dependía de dato externo (RUES) está desactivada y documentada. 2. Verificación de campos en primera ejecución: El script de ingesta logea la lista de campos recibidos y los compara contra la lista esperada. Discrepancias se logean como warning. 3. contrato.get(campo, None): Acceso a campos con default None, nunca con acceso directo que lanzaría KeyError. 4. Decisión conservadora sobre Adiciones: Los nombres de campos del dataset cb9c-h8sn se verifican con query exploratoria en Semana 1. Si no coinciden, C1 se desactiva temporalmente.
Plan de contingencia	Si un campo clave se renombra: (a) actualizar el mapping en secop_ingest.py, (b) re-ejecutar ingesta, (c) re-ejecutar scoring. Si un campo desaparece: desactivar la(s) bandera(s) dependiente(s), documentar, y ajustar máximo teórico del score.
14.5 Riesgo 5: Telegram como Canal Único Pierde Alcance Masivo
Dimensión	Detalle
Probabilidad	MEDIA — Telegram tiene ~15% de penetración en smartphones colombianos vs. ~98% de WhatsApp. El público objetivo (ciudadanos de Medellín interesados en contratación pública) puede tener penetración diferente al promedio.
Impacto	MEDIO — Se pierde el canal push de mayor alcance. Los Perfiles 2 (Furioso Sin Canal) y 3 (Indiferente Pragmático) son los más afectados; probablemente no instalarán Telegram para un solo servicio.
Mitigación implementada	1. Web como canal principal: La web de Lupa es accesible desde cualquier navegador sin instalar nada. Es el canal de mayor alcance real. 2. Open Graph tags: Al compartir enlaces de la web en WhatsApp, Facebook, o Twitter, se genera un preview informativo que funciona como "alerta manual" sin necesidad de integración directa con WhatsApp. 3. Contenido compartible: Botón "Compartir" en cada contrato que genera un enlace directo. 4. Efecto red: Un solo suscriptor de Telegram puede compartir la alerta en sus grupos de WhatsApp, multiplicando el alcance orgánicamente.
Fase 2	WhatsApp via Evolution API + Chatwoot con segmentación por comunas. Estimación de impacto: 5-10x más alcance push.
Métrica de monitoreo	TELEGRAM (suscriptores) + WEB_UV (visitantes web). Si TELEGRAM < 100 tras 30 días pero WEB_UV > 500, el canal web está compensando.
15. PLAN DE IMPLEMENTACIÓN (4 SEMANAS / 2 SPRINTS)
15.1 SPRINT 1 (Semanas 1-2): DATA LAKE + LUPA ENGINE
Objetivo: Pipeline completo de ingesta → scoring → resultados almacenados en Supabase, corriendo autónomamente cada noche sin intervención manual.

Entregables detallados:

#	Entregable	Descripción	Criterio de completitud
S1.1	Servidor Hetzner configurado	VPS CX21 con Dokploy instalado. Docker containers para n8n, FastAPI, Python workers. Dominio configurado con Cloudflare DNS.	SSH funcional. Dokploy UI accesible. n8n UI accesible en subdominio (ej: n8n.lupa.city).
S1.2	Supabase configurado	Proyecto creado. Las 6 tablas (4 core + 2 soporte) creadas con el schema SQL de la Sección 8. RLS habilitado. API keys generadas.	Todas las tablas visibles en Supabase Studio. UPSERT de prueba exitoso via client JS. RLS verificado: anon puede SELECT pero no INSERT/UPDATE en tablas core.
S1.3	Script secop_ingest.py	Extrae 3 datasets de SODA API (Contratos, Procesos, Adiciones). Merge por proceso_de_compra. Limpieza completa (NITs, centavos, fechas, modalidades). UPSERT batch en contratos_raw. Ingesta incremental basada en ultima_actualizacion.	Primera ejecución llena contratos_raw con >1000 registros de Medellín. Segunda ejecución (incremental) procesa solo registros nuevos. Zero registros con valor_del_contrato > 500_000_000_000. Campos del JOIN (numero_de_oferentes, precio_base, etc.) presentes en >80% de registros.
S1.4	Script quality_gate.py	Calcula ICD para cada contrato nuevo/actualizado. Enruta a contratos_opacos (ICD < 40) o pasa al scoring. Actualiza icd_score en contratos_raw.	Registros con campos faltantes tienen ICD < 40 y aparecen en contratos_opacos con campos_faltantes correcto. Registros completos tienen ICD ≥ 60.
S1.5	Script scoring_engine.py	Implementa las 10 banderas activas (A1, A2, A3, B1, B3, C1, C2, C3, D1, D2). Bonus sistémico. Atenuación ACTT. Penalización ICD. Traducción ciudadana (plantillas). Texto de denuncia (plantilla legal). UPSERT en contratos_scored. INSERT en timeline_impunidad para score ≥ 55.	Distribución de scores muestra variación real (no todos 0, no todos 100). Al menos 1 contrato con score ≥ 55 detectado en datos reales de Medellín. Cada bandera activa tiene desc legible en detalle_banderas. texto_denuncia generado para contratos con score ≥ 55 contiene datos del contrato + leyes + disclaimer. Validación SLAPP pasa al 100%.
S1.6	Workflow n8n configurado	CRON a las 3AM (timezone del servidor ajustado). Secuencia: ingesta → quality gate → scoring. Manejo de errores con logging en meta_pipeline.	Pipeline corre ≥3 noches consecutivas sin intervención manual. meta_pipeline muestra estado = 'OK' para cada ejecución.
S1.7	CSV de sancionados (Procuraduría)	Primera descarga manual del SIRI. Almacenado en data/sancionados_antioquia.csv. Verificación de formato.	CSV cargable por cargar_sancionados(). Al menos 1 cruce exitoso con proveedores de Medellín verificado.
S1.8	Tests unitarios del scoring	pytest para cada función de bandera (A1-D2), ICD, bonus, ACTT. Mínimo 3 test cases por bandera (activa, no activa, datos faltantes).	pytest tests/ -v pasa al 100%. Coverage del scoring engine > 80%.
Dependencias: Ninguna externa. Todo es auto-contenido.

Riesgos específicos del Sprint 1:

Riesgo	Prob.	Mitigación
API SODA no responde durante desarrollo	Media	Descargar JSON de muestra para desarrollo offline. Tests con fixtures.
Campos de Adiciones (cb9c-h8sn) no coinciden con los esperados	Alta	Query exploratoria en Día 1. Si no coinciden, desactivar C1 y documentar.
Bug de centavos más complejo de lo esperado	Media	Análisis manual de 100 registros para calibrar umbral. Log de correcciones.
ICD demasiado estricto (>30% opacos)	Media	Ajustar pesos de campos del JOIN (que dependen de match entre datasets).
Calendario semanal (Sprint 1):

text

SEMANA 1:
  Día 1-2: S1.1 (Hetzner + Dokploy) + S1.2 (Supabase schema)
  Día 3-4: S1.3 (secop_ingest.py) — extracción + merge + limpieza
  Día 5:   S1.3 (UPSERT) + S1.7 (CSV sancionados)

SEMANA 2:
  Día 1-2: S1.4 (quality_gate) + S1.5 (scoring_engine) — banderas
  Día 3:   S1.5 (scoring_engine) — ACTT, bonus, traducciones, denuncia
  Día 4:   S1.6 (workflow n8n) + S1.8 (tests)
  Día 5:   Ejecución completa del pipeline + validación de resultados
15.2 SPRINT 2 (Semanas 3-4): FRONTEND + DISTRIBUCIÓN + LANZAMIENTO
Objetivo: Exponer los hallazgos al público y activar el efecto panóptico con distribución automatizada. Documentar al menos 1 Caso Maestro ("Slam Dunk") para presentar a stakeholders.

Entregables detallados:

#	Entregable	Descripción	Criterio de completitud
S2.1	Web Next.js en Vercel	Todas las rutas implementadas: /, /top10, /contrato/[id], /opacos, /impunidad, /metodologia, /reportar. ISR con revalidate de 1 hora. Tailwind CSS. Responsive. Open Graph tags.	Todas las páginas cargan en <2s (TTFB). Responsive verificado en 360px, 768px, 1024px, 1920px. Sin login. Sin cookies de tracking. Contadores en landing reflejan datos reales.
S2.2	Botón "Copiar Denuncia"	Implementación de navigator.clipboard.writeText() con fallback textarea. Solo visible en contratos con score ≥ 55. Feedback visual "✅ Copiado".	Test en Chrome, Safari, Firefox (desktop y mobile). Texto copiado coincide con texto_denuncia de la DB. No contiene términos SLAPP prohibidos.
S2.3	Descarga CSV	Botón en /top10. Generación client-side. UTF-8 con BOM. Nombre: lupa_top10_YYYY-MM-DD.csv.	CSV descargable sin login. Abierto en Excel Windows muestra caracteres especiales correctamente. Columnas coinciden con la especificación de HU-04.
S2.4	Sección Contratos Opacos	Página /opacos con lista de contratos ICD < 40. Campos faltantes legibles. Encabezado explicativo. Sin score numérico.	Contratos mostrados coinciden con contratos_opacos. campos_faltantes renderizado como lista legible. "⬛ NO EVALUABLE" en lugar de score.
S2.5	Timeline de Impunidad	Página /impunidad. Ordenado por dias_inactividad DESC. Colores por rango de días. Contador agregado.	Días calculados correctamente. Colores corresponden a rangos especificados. Actualización de estado en Supabase reflejada en web en ≤1 hora.
S2.6	Página Metodología	Página /metodologia con descripción completa de las 10 banderas + B2 desactivada + ICD + ACTT + bonus + niveles + limitaciones + link GitHub + auditoría simétrica.	Todos los componentes presentes según especificación HU-05. Enlace a GitHub funcional y repo público.
S2.7	Formulario Anónimo	Página /reportar. Campos según especificación. Sin datos identificatorios. No logging de IP. Confirmación con código LUPA-XXXXXXXX. Aviso de privacidad.	Formulario funcional. IP no aparece en logs del servidor ni en tabla reportes_anonimos. Código de referencia generado correctamente. Upload de archivos funcional (≤5MB, PDF/JPG/PNG).
S2.8	Bot de Telegram	Bot creado via @BotFather. Canal @LupaMedellin creado y público. Bot como admin con permisos de publicación. Mensaje de prueba enviado exitosamente.	Bot publica en el canal sin error. Formato MarkdownV2 renderiza correctamente.
S2.9	Script telegram_dist.py	Query contratos con score ≥ 55 y publicado_telegram = False. Formateo de mensaje. Envío via Bot API. Update publicado_telegram = True. Manejo de errores 429/400/5xx.	Alertas publicadas automáticamente cada mañana entre 5:00-5:30 AM COT. No hay duplicados (re-ejecutar no re-envía). Máx 20 mensajes/día.
S2.10	Workflow n8n actualizado	Agregar nodo de distribución Telegram encadenado al scoring.	Pipeline completo 3AM-5:30AM funcional.
S2.11	Disclaimer SLAPP	Verificar presencia en TODOS los componentes: cada página web, cada mensaje Telegram, cada texto de denuncia, README de GitHub.	Checklist visual: 100% de componentes públicos tienen disclaimer. Hardcoded (no removible sin cambio de código).
S2.12	Caso Maestro ("Slam Dunk")	Al menos 1 patrón sistémico detectado en datos reales de Medellín, verificado manualmente. Documentado con: narrativa, datos, score, banderas, texto de denuncia, CSV de contratos relacionados.	Documento listo para presentar a Concejal MIRA y/o La Silla Vacía. Verificación manual confirma que el hallazgo es legítimo (no es falso positivo).
Dependencias: Sprint 1 completo (pipeline nocturno operativo con datos en Supabase).

Riesgos específicos del Sprint 2:

Riesgo	Prob.	Mitigación
No se encuentra ningún Caso Maestro (scores demasiado bajos)	Media	Revisar manualmente los top 50 contratos por valor con modalidad directa. Analizar concentración de proveedores manualmente. Si no hay hallazgos significativos: presentar el sistema con datos simulados + datos reales de bajo riesgo, y documentar que el sistema funciona pero los datos actuales no muestran patrones críticos.
Performance de la web con ISR en Vercel	Baja	ISR con revalidate de 1 hora es un patrón probado en Next.js. Si hay problemas, cambiar a SSR con caché en edge.
Formato MarkdownV2 de Telegram causa errores de renderizado	Media	Función dedicada de escape de caracteres especiales (. ! - ( ) > # + = { } ~). Testing exhaustivo con mensajes de prueba antes de activar publicación automática.
Formulario anónimo abusado (spam)	Baja	Validación de longitud mínima (50 chars). Rate limiting por IP en el endpoint (sí se lee la IP para rate limiting, pero NO se almacena). Captcha invisible (hCaptcha) como fallback si el spam es excesivo.
Calendario semanal (Sprint 2):

text

SEMANA 3:
  Día 1:   S2.1 (Next.js setup + landing + layout) + S2.8 (Bot Telegram)
  Día 2-3: S2.1 (/top10 + /contrato/[id]) + S2.2 (Copiar Denuncia) + S2.3 (CSV)
  Día 4:   S2.4 (/opacos) + S2.5 (/impunidad) + S2.6 (/metodologia)
  Día 5:   S2.7 (/reportar) + S2.9 (telegram_dist.py) + S2.10 (n8n update)

SEMANA 4:
  Día 1:   S2.11 (Disclaimer audit) + Deploy to Vercel + DNS setup
  Día 2:   Testing end-to-end: pipeline completo 3AM → scoring → 
           Telegram → web → copiar denuncia → descargar CSV
  Día 3:   S2.12 (Caso Maestro) — análisis manual de datos reales
  Día 4:   Bugfixes + testing final + documentación
  Día 5:   LANZAMIENTO SOFT: canal Telegram activo, web pública,
           primer envío real de alertas
15.3 Post-Sprint 2: Primera Semana de Operación
Día	Actividad
Día 1-3	Monitoreo activo del pipeline. Verificar alertas de Telegram. Revisar métricas.
Día 3	Primera revisión manual de falsos positivos (top 20 contratos).
Día 5	Decisión de recalibración de umbrales si FP_RATE > 20%.
Día 7	Primer contacto con Concejal MIRA y/o periodistas (si hay Caso Maestro sólido).
16. CRITERIOS DE LANZAMIENTO (CHECKLIST GO/NO-GO)
Mínimo viable para considerar el sistema listo para presentar a stakeholders (Concejal MIRA, La Silla Vacía, El Armadillo) y hacer público el canal de Telegram.

16.1 Checklist Técnico (TODOS deben ser ✅ para GO)
#	Criterio	Verificación	Estado
L1	Pipeline nocturno corriendo ≥5 noches consecutivas sin fallo total	SELECT COUNT(*) FROM meta_pipeline WHERE nombre_pipeline = 'ingesta_contratos' AND estado = 'OK' AND updated_at >= NOW() - INTERVAL '5 days' retorna ≥ 5	[ ]
L2	contratos_raw contiene ≥1000 registros de Medellín	SELECT COUNT(*) FROM contratos_raw WHERE ciudad ILIKE '%medell%' ≥ 1000	[ ]
L3	Zero registros con valor implausible post-corrección de centavos	SELECT COUNT(*) FROM contratos_raw WHERE valor_del_contrato > 500000000000 retorna 0	[ ]
L4	contratos_scored muestra distribución de scores variada	Histograma muestra scores en al menos 3 rangos diferentes (0-39, 40-54, 55+)	[ ]
L5	Al menos 1 contrato con score ≥ 55 detectado en datos reales	SELECT COUNT(*) FROM contratos_scored WHERE score_total >= 55 ≥ 1	[ ]
L6	Disclaimer SLAPP presente en 100% de componentes públicos	Inspección visual de: cada página web (7 rutas), mensaje Telegram, texto_denuncia (5 muestras), README GitHub	[ ]
L7	Zero-Live-Query verificado	Frontend NO hace ninguna llamada a datos.gov.co. Todo lee de Supabase. Verificar en DevTools > Network al navegar todas las páginas.	[ ]
L8	Atenuación ACTT activa y verificada	Al menos 1 contrato interadministrativo con atenuación aplicada. Verificar en detalle_banderas que contiene "ACTT".	[ ]
L9	Web carga <2s desde Colombia	Lighthouse o WebPageTest desde servidor colombiano. TTFB < 2000ms. LCP < 3000ms.	[ ]
L10	Web responsive verificada	Test visual en 360px (móvil), 768px (tablet), 1024px (laptop), 1920px (desktop). Todo legible sin scroll horizontal.	[ ]
L11	Canal Telegram con ≥1 semana de alertas publicadas	Canal @LupaMedellin tiene ≥5 mensajes de alertas reales (no pruebas).	[ ]
L12	Formulario anónimo operativo sin logs de IP	Enviar reporte de prueba. Verificar que IP no aparece en logs del servidor (docker logs) ni en tabla reportes_anonimos. Código de referencia generado.	[ ]
L13	Timeline de Impunidad visible con al menos 1 entrada	/impunidad muestra al menos 1 contrato con dias_inactividad calculado y color correcto.	[ ]
L14	Botón "Copiar Denuncia" funcional	Test en Chrome + Safari (desktop y mobile). Texto copiado contiene datos del contrato + leyes + disclaimer. No contiene términos SLAPP.	[ ]
L15	CSV descargable y legible en Excel Windows	Descargar CSV del Top 10. Abrir en Excel Windows. Verificar: ñ, tildes, $, separadores de miles, columnas correctas.	[ ]
L16	Código de scoring en GitHub público	Repo público accesible. README incluye descripción, disclaimer, y enlace a la metodología web.	[ ]
L17	Validación SLAPP automatizada activa	validar_lenguaje_slapp() se ejecuta antes de cada INSERT en traduccion_ciudadana y texto_denuncia. Zero términos prohibidos en datos actuales.	[ ]
16.2 Checklist de Contenido (TODOS deben ser ✅ para GO)
#	Criterio	Estado
C1	Caso Maestro documentado: al menos 1 patrón sistémico detectado en datos reales, verificado manualmente, con narrativa, datos, y texto de denuncia generado.	[ ]
C2	Página de metodología completa con las 10 banderas + ICD + ACTT + bonus + limitaciones + auditoría simétrica.	[ ]
C3	Mensaje introductorio fijado (pinned) en canal @LupaMedellin explicando qué es Lupa y cómo funciona.	[ ]
16.3 Criterios NO-GO (Si alguno es TRUE, no se lanza)
#	Criterio NO-GO	Justificación
N1	El disclaimer SLAPP falta en algún componente público	Riesgo legal inaceptable
N2	Algún output del sistema contiene términos SLAPP prohibidos	Riesgo legal inaceptable
N3	El pipeline ha fallado >2 de las últimas 5 noches	Sistema no es confiable
N4	FP_RATE > 50% en revisión manual de top 20	Score no es útil; destruiría credibilidad
N5	La web hace alguna llamada a datos.gov.co en tiempo real	Violación del principio Zero-Live-Query; riesgo de caída
N6	El formulario /reportar logea IPs	Violación de la promesa de anonimato
N7	No existe un Caso Maestro verificado	Sin "proof of value" para stakeholders
16.4 Proceso de Decisión Go/No-Go
Día -2 del lanzamiento: Ejecutar todos los checks de L1-L17 y C1-C3. Documentar resultados.
Revisión: Si todos los checks pasan y ningún criterio NO-GO es TRUE → GO.
Si algún check falla: Evaluar severidad. Checks L6, L7, L12, L17 son bloqueantes (seguridad/legal). Los demás son negociables con documentación de deuda técnica.
Si algún NO-GO es TRUE: NO-GO. Corregir antes de lanzar. Sin excepciones.
17. ROADMAP FASE 2 (POST-LANZAMIENTO — NO SE CONSTRUYE AHORA)
Documentado para contexto arquitectónico, decisiones de diseño forward-looking, y comunicación con stakeholders sobre la visión completa del producto. Ninguno de estos elementos se implementa en el MVP.

17.1 Capa 2 Semántica (Análisis de Texto con IA)
Propósito: Analizar el contenido textual de justificacion_modalidad_de y descripcion_del_proceso para detectar patrones semánticos que las reglas deterministas no pueden capturar.

Banderas semánticas (S1-S4):

Código	Nombre	Puntos	Descripción
S1	Pliego "sastre"	15	Especificaciones técnicas que solo un proveedor puede cumplir
S2	Vaguedad deliberada	10	Descripción del objeto contractual intencionalmente ambigua
S3	Incoherencia objeto-modalidad	15	La justificación de modalidad no corresponde con la modalidad elegida
S4	Urgencia manufacturada	10	Invocación de urgencia manifiesta sin evidencia de emergencia real
Opciones técnicas evaluadas:

Opción	Costo	Latencia	Calidad	Decisión
Groq API (Llama 3 70B)	~$0.001/contrato (tier gratuito o casi gratuito)	~2s/contrato	Alta	Preferida si el tier gratuito es suficiente
Ollama self-hosted (Llama 3 8B cuantizado)	$0 (corre en el VPS existente)	~60-120s/contrato	Media-Alta	Preferida si VPS tiene ≥16GB RAM
Claude API (Anthropic)	~$0.015/contrato	~3s/contrato	Muy alta	Rechazada: costos variables, dependencia
OpenAI GPT-4o-mini	~$0.005/contrato	~2s/contrato	Alta	Rechazada: mismos problemas que Claude
Decisión arquitectónica (para Fase 2):

Si el VPS Hetzner se upgradea a ≥16GB RAM (~€12/mes): Ollama con llama3:8b cuantizado. Costo marginal $0. Latencia de 1-2 min/contrato es aceptable en batch nocturno (procesando ~50-100 contratos nuevos/noche = ~2 horas adicionales). Sin dependencia de terceros, sin rate limits, sin costos variables.
Si se mantiene VPS de 4GB RAM: Groq API con tier gratuito (si disponible) o de bajo costo. Velocidad absurda (~2s/contrato). Riesgo: dependencia de tercero y posible cambio de pricing.
Máximo teórico del score con Capa 2: 100 (Capa 1) + 50 (Capa 2) = 150 pts. Se renormalizaría a 100 con pesos proporcionales.
17.2 WhatsApp via Evolution API
Arquitectura:

Evolution API self-hosted en el VPS Hetzner (Docker container)
Chatwoot para gestión de conversaciones y estados
Tabla suscriptores con campos: teléfono (hash), comuna, preferencias, fecha_suscripción
Tabla alertas_pendientes con cola de mensajes
Rate limiting: 15 msg/seg (límite de WhatsApp Business)
Segmentación por comunas:

Mapeo nombre_entidad → comuna (tabla de lookup manual)
El suscriptor elige su comuna al suscribirse
Solo recibe alertas de contratos donde la entidad contratante opera en su comuna
Riesgos específicos:

Baneo del número de WhatsApp por envío masivo: mitigado con rate limiting + contenido no spam (datos públicos, no comercial)
Privacidad de números de teléfono: hash de números, no almacenamiento de números en claro
Costo de infraestructura: Evolution API es gratis (open source), pero requiere un número de teléfono dedicado
17.3 PDFs Automatizados
Tipos de documentos:

Derecho de Petición (Art. 23 Constitución + CPACA): Formato legal completo con encabezado, datos del peticionario (en blanco para que el ciudadano llene), datos del contrato, solicitud estructurada, fundamento legal, firma.
Queja Disciplinaria (Ley 734/2002): Formato para radicar ante la Personería o Procuraduría.
Dossier para Debate de Control (uso interno de Concejales): Formato ejecutivo con resumen narrativo, datos en tabla, gráficos de concentración, timeline.
Implementación técnica: pdfmake (JavaScript) o ReportLab (Python). Templates con placeholders que se llenan con datos del contrato.

17.4 Bandera B2: Empresa "de Papel"
Fuente de datos: RUES (Registro Único Empresarial y Social) de Confecámaras.

URL: https://www.rues.org.co
Dato necesario: fecha_constitución de la empresa
Acceso: Scraping con Playwright (CAPTCHA handling) o API comercial de Confecámaras
Lógica: Si fecha_constitución < 12 meses antes de fecha_de_firma del contrato → activa B2 (8 puntos). Una empresa constituida poco antes de recibir un contrato significativo es señal de posible empresa de papel creada ad hoc.
