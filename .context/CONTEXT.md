# CONTEXT.md — Chatbot_With_ML

## Visión Global

**Chatbot_With_ML** es un chatbot para WhatsApp con Machine Learning que automatiza la atención al cliente de una PYME. Comprende lenguaje natural en español mediante un **motor de IA híbrido**: el camino principal usa **TF-IDF + similitud de coseno** sobre una base de conocimiento expandida con sinónimos, y el camino de respaldo usa **RapidFuzz (fuzzy matching)** para tolerar errores tipográficos.

El bot se conecta a WhatsApp vía la API de **Green-API**, responde comandos (`/start`, `/ayuda`, `/stock`, `/precio`, `/contacto`, `/horario`), gestiona un **menú de conversación por estados** y resuelve consultas de **stock y precios** leyendo un inventario local con fuentes intercambiables (SQLite o CSV).

Objetivo de producto (según el plan en `Upgrade_sistema_inventario_chatbot.md`): entregar un **chatbot autónomo vendible a PYMEs** para facturación, consultas y automatización de atención.

## Stack Tecnológico

| Tecnología | Versión mínima |
| :--- | :--- |
| Python | 3.12 (entorno actual; README declara 3.8+) |
| scikit-learn | >= 1.3.0 (TF-IDF + cosine similarity) |
| numpy | >= 1.24.0 |
| rapidfuzz | >= 3.0.0 (fuzzy matching) |
| whatsapp-chatbot-python | >= 0.4.0 (GreenAPIBot, Green-API) |
| python-dotenv | >= 0.21.0 |
| pytest | >= 7.0.0 (tests) |
| pytest-mock | >= 3.0.0 |
| pylint | >= 3.0.0 (linter, ejecución manual) |

## Estructura de Carpetas (real, el README está desactualizado)

```
Chatbot_With_ML/
├── run.py                  → Punto de entrada: valida .env → ChatbotEngine → GreenAPIBot → register_handlers → run_forever()
├── app/
│   ├── config.py           → Carga .env desde la raíz; expone credenciales, umbrales y rutas (TFIDF_THRESHOLD, FUZZY_THRESHOLD, INVENTORY_SOURCE_TYPE)
│   ├── handlers/
│   │   └── message_handler.py → register_handlers(bot, engine): ruteo de comandos + menú por estados + fallback IA
│   ├── services/
│   │   ├── chatbot_engine.py  → ChatbotEngine: TF-IDF + cosine similarity, fallback RapidFuzz token_sort_ratio
│   │   ├── inventory_service.py → buscar_producto(): fuente SQLite o CSV (INVENTORY_SOURCE_TYPE)
│   │   └── state_manager.py   → Estado por usuario en memoria (dict), 3 estados
│   ├── utils/
│   │   └── logger.py          → get_logger(name): escribe a chatbot_operations.log + stdout
│   └── data/
│       ├── knowledge_base.json → "conocimiento": [{pregunta_base, respuesta, sinonimos}]
│       ├── inventory.db        → tabla `productos` (nombre, precio, stock)
│       └── inventory.csv       → columnas nombre, precio, stock
├── tests/
│   ├── test_config.py      → ✅ Funciona (importa app.config)
│   ├── test_engine.py      → ❌ ROTO (importa app.chatbot.engine; debe ser app.services.chatbot_engine)
│   └── test_api.py         → ❌ ROTO (importa app.api.routes; debe ser app.handlers.message_handler)
├── requirements.txt
├── .env / .env.example     → Credenciales Green-API + configuración
└── AGENTS.md               → Convenciones del proyecto (gitignored)
```

## Entidades de Datos Principales

- **Base de conocimiento** — `app/data/knowledge_base.json`: array `conocimiento` con 5-14 preguntas expandidas. Entradas: `pregunta_base`, `respuesta`, `sinonimos` (list). Se carga al inicio; editar exige reinicio.
- **Inventario** — tabla `productos` en `inventory.db` (SQLite) **o** `inventory.csv`: columnas `nombre`, `precio`, `stock`. La fuente activa la define `INVENTORY_SOURCE_TYPE` (`sqlite` por defecto).
- **Estado de conversación** — dict en memoria en `state_manager.py` keyed por `user_id` (teléfono). Estados: `MENU_PRINCIPAL`, `ESPERANDO_PRODUCTO_STOCK`, `ESPERANDO_PRODUCTO_PRECIO`. **Sin persistencia entre reinicios.**

## Reglas de Negocio Fijas

- Código, nombres y comentarios en **español**; docstrings triple-quoted.
- Configuración vía variables de entorno en `.env` (cargado desde la raíz por `app/config.py`). **No versionar ni exponer `.env`** (contiene credenciales reales).
- Logging centralizado: todo módulo usa `get_logger(__name__)` → `chatbot_operations.log` + stdout.
- Conocimiento externo en JSON (separación dato/código).
- Umbrales configurables: `TFIDF_THRESHOLD` (0.3) y `FUZZY_THRESHOLD` (70).
- Pruebas obligatorias con **pytest** (`tests/`, patrón `test_*.py`).
- Imports: absolutos desde la raíz del paquete `app` (sin imports relativos).
- Validación previa al arranque: `config.validate_credentials()`.

## Estado de Madurez

- **Estable para producción a pequeña escala** (declarado en README, 85% cobertura declarada).
- Plan original Fases 0–4 **completadas** (estructura modular, comandos, menús, inventario multi-fuente).
- Fases 5–7 pendientes (facturación, robustez/logs, despliegue como servicio).
- Deuda técnica crítica: **tests rotos** (imports a módulos inexistentes tras el refactor `c4fb5fa`) y **README desactualizado**.

## Referencias

- Plan de fases original: `Upgrade_sistema_inventario_chatbot.md` (gitignored).
- Convenciones/commits: `AGENTS.md` (gitignored) y git history.