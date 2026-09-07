# DECISIONS.md — Chatbot_With_ML

Registro de Decisiones de Arquitectura (ADR). Cada decisión significativa se documenta aquí con su contexto, alternativas, motivación y estado.

## Formato ADR

```
## ADR-XXX: <Título de la Decisión>
- **Fecha:** YYYY-MM-DD
- **Estado:** Propuesta | Aceptada | Deprecada | Sustituida por ADR-YYY
- **Decisión:** <¿Qué se decidió?>
- **Alternativas:** <Opciones consideradas>
- **Motivación:** <Por qué se eligió>
```

---

## Decisión Archivada: Adopción de metodología SDD
- **Fecha:** 2026-09-05
- **Estado:** Aceptada
- **Decisión:** Adoptar el proyecto legado Chatbot_With_ML en la metodología Spec-Driven Development (SDD) mediante `/adopt`. Se crea la estructura `.context/` (CONTEXT.md, ROADMAP.md, STATE.md, DECISIONS.md, PATTERNS.md, WORKFLOW.md) y `.prompts/` con los roles estándar.
- **Alternativas:** No adoptar (mantener flujo con AGENTS.md y `Upgrade_sistema_inventario_chatbot.md`), o generar solo archivos de contexto sin roles.
- **Motivación:** Formalizar el contexto del proyecto con artefactos reutilizables para la planificación por fases (`/plan-phase`).

---

## ADR-001: Arquitectura modular handlers/services/utils
- **Fecha:** 2026-09-05 (registrado retroactivamente; refactor original en commit `c4fb5fa`)
- **Estado:** Aceptada
- **Decisión:** Reestructurar el proyecto eliminando los viejos `app/api/routes.py` y `app/chatbot/engine.py`, creando `app/handlers/`, `app/services/` y `app/utils/` con responsabilidades separadas, más `app/config.py` para la configuración.
- **Alternativas:** Mantener el monolito original con `routes.py`/`engine.py`.
- **Motivación:** Facilitar la extensión con nuevos comandos y módulos (facturación, jobs) sin acoplar el ruteo a la lógica de negocio.
- **Consecuencia conocida:** los tests quedaron apuntando a los módulos antiguos (imports rotos) — pendiente de corregir en Fase 5.

## ADR-002: Motor de IA híbrido TF-IDF + fuzzy fallback
- **Fecha:** 2026-09-05 (registrado retroactivamente)
- **Estado:** Aceptada
- **Decisión:** Clasificación primaria con `TfidfVectorizer` + `cosine_similarity` sobre preguntas expandidas (base + sinónimos); respaldo con RapidFuzz `token_sort_ratio` contra preguntas base cuando la confianza TF-IDF cae por debajo del umbral.
- **Alternativas:** Solo TF-IDF; solo fuzzy matching; modelos transformer (descartados por alcance/recursos).
- **Motivación:** Equilibrio entre precisión semántica y tolerancia a errores tipográficos en español, sin dependencias pesadas.

## ADR-003: Umbrales de confianza configurables vía `.env`
- **Fecha:** 2026-09-05 (registrado retroactivamente)
- **Estado:** Aceptada
- **Decisión:** Exponer `TFIDF_THRESHOLD` (0.3) y `FUZZY_THRESHOLD` (70) en `app/config.py` como variables de entorno con valores por defecto.
- **Alternativas:** Umbrales fijos en el código.
- **Motivación:** Ajustar sensibilidad sin modificar código, según el comportamiento observado en producción.

## ADR-004: Inventario multi-fuente SQLite/CSV
- **Fecha:** 2026-09-05 (registrado retroactivamente; original en commit `b4aafb1`)
- **Estado:** Aceptada
- **Decisión:** `inventory_service.buscar_producto()` lee de SQLite (por defecto) o CSV según `INVENTORY_SOURCE_TYPE`, con búsqueda difusa RapidFuzz `WRatio` y `score_cutoff=70`.
- **Alternativas:** Google Sheets (descartado por complejidad de OAuth), inventario hardcodeado.
- **Motivación:** Rentabilizar la infraestructura local del cliente PYME y tolerar errores ortográficos en los nombres de producto.

## ADR-005: Estado de conversación en memoria (sin persistencia)
- **Fecha:** 2026-09-05 (registrado retroactivamente)
- **Estado:** Aceptada (limitación conocida)
- **Decisión:** `state_manager.py` mantiene un dict global por `user_id` en RAM, con 3 estados de menú.
- **Alternativas:** Persistencia en SQLite/Redis; estado stateless.
- **Motivación:** Simplicidad en despliegues pequeños; se documenta como limitación (las conversaciones se reinician al apagar el bot).

## ADR-006: Base de conocimiento como archivo JSON externo
- **Fecha:** 2026-09-05 (registrado retroactivamente)
- **Estado:** Aceptada
- **Decisión:** El conocimiento del bot reside en `app/data/knowledge_base.json` (array `conocimiento`), cargado al inicializar `ChatbotEngine`.
- **Alternativas:** Datos en código, en base de datos, o API de administración en caliente.
- **Motivación:** Permite actualizar respuestas sin tocar código, manteniendo la separación dato/lógica. Limitación: editar el JSON exige reiniciar el bot.