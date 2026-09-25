# CONTEXT.md — Chatbot_With_ML

## Visión Global

**Chatbot_With_ML** es un chatbot para WhatsApp con Machine Learning que automatiza la atención al cliente de una PYME. Comprende lenguaje natural en español mediante un **motor de IA híbrido**: el camino principal usa **TF-IDF + similitud de coseno** sobre una base de conocimiento expandida con sinónimos, y el camino de respaldo usa **RapidFuzz (fuzzy matching)** para tolerar errores tipográficos.

El bot se conecta a WhatsApp vía la API de **Green-API**, responde comandos (`/start`, `/ayuda`, `/stock`, `/precio`, `/contacto`, `/horario`, `/factura`), gestiona un **menú de conversación por estados** y resuelve consultas de **stock y precios** leyendo un inventario local con fuentes intercambiables (SQLite o CSV). Además genera **facturas en PDF** (`/factura`, con `reportlab`) y envía **recordatorios programados** diarios a clientes registrados.

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
| reportlab | >= 4.0 (facturas PDF, Fase 6) |
| pytest | >= 7.0.0 (tests) |
| pytest-mock | >= 3.0.0 |
| pylint | >= 3.0.0 (linter, ejecución manual) |

**Despliegue:** Linux systemd (unidad `chatbot.service`, usuario `chatbot`) o Windows `schtasks` (tarea `ChatbotML`). Scripts en `scripts/`; operación en `docs/DESPLEGUE.md`. Sin contenedores ni orquestación.

## Estructura de Carpetas (real, actualizada en rama `feat/local-testing-repl`)

```
Chatbot_With_ML/
├── run.py                  → Punto de entrada: valida .env → ChatbotEngine → GreenAPIBot → register_handlers → run_forever()
├── scripts/
│   ├── repl_local.py       → REPL local de pruebas (no requiere WhatsApp)
│   ├── install_linux.sh    → Despliegue como servicio systemd (usuario `chatbot`, .env 600, Restart=always)
│   └── install_windows.bat → Despliegue como tarea programada `ChatbotML` (schtasks ONLOGON)
├── docs/
│   └── DESPLEGUE.md        → Operación 24/7 del bot (Linux + Windows, actualización, rollback, seguridad)
├── app/
│   ├── config.py           → Carga .env desde la raíz; expone credenciales, umbrales y rutas (TFIDF_THRESHOLD, FUZZY_THRESHOLD, INVENTORY_SOURCE_TYPE, NEGOCIO_NOMBRE, FACTURAS_PATH, CLIENTES_PATH, OWNER_PHONE, SMTP_*, LOG_MAX_BYTES, LOG_BACKUP_COUNT)
│   ├── handlers/
│   │   └── message_handler.py → register_handlers(bot, engine): ruteo de comandos + menú por estados + fallback IA + envío de PDFs
│   ├── services/
│   │   ├── chatbot_engine.py  → ChatbotEngine: TF-IDF + cosine similarity, fallback RapidFuzz token_sort_ratio + WRatio
│   │   ├── inventory_service.py → buscar_producto(): fuente SQLite o CSV; fuzzy combinado (WRatio + partial_ratio)
│   │   ├── message_processor.py → procesar_mensaje()/procesar_mensaje_con_archivo(): lógica de mensajes y máquina de estados (Respuesta(texto, archivo))
│   │   ├── state_manager.py   → Estado y datos por usuario en memoria (dict, thread-safe con RLock; 4 estados)
│   │   ├── invoice_service.py → generar_factura(FacturaDatos) → PDF en app/data/facturas/ + contador correlativo
│   │   ├── scheduled_notifications.py → enviar_recordatorios_diarios(bot) vía sendMessage
│   │   └── report_service.py  → enviar_reporte_email(): log por SMTP al dueño (smtplib, STARTTLS/SSL)
│   ├── utils/
│   │   ├── logger.py          → get_logger(name): logging centralizado con RotatingFileHandler + stdout
│   │   └── retry.py           → con_reintentos(): backoff exponencial para envíos de salida
│   └── data/
│       ├── knowledge_base.json → "conocimiento": [{pregunta_base, respuesta, sinonimos}]
│       ├── inventory.db        → tabla `productos` (nombre, precio, stock) — sembrado con 4 productos
│       ├── inventory.csv       → columnas nombre, precio, stock
│       ├── facturas/           → PDFs generados + contador.json (gitignored)
│       └── clientes.json       → registro de clientes para recordatorios (gitignored)
├── tests/
│   ├── test_config.py          → importa app.config
│   ├── test_engine.py          → importa app.services.chatbot_engine
│   ├── test_handlers.py        → test_api.py migrado; importa app.handlers.message_handler
│   ├── test_message_processor.py → tests de procesar_mensaje (incl. flujo /stock, /precio y /factura)
│   ├── test_inventory_service.py → tests de buscar_producto en SQLite y CSV
│   ├── test_state_manager.py   → thread-safety de estados y datos
│   ├── test_invoice_service.py → tests de generación de facturas PDF
│   └── test_scheduled_notifications.py → tests de recordatorios programados
├── requirements.txt
├── .env / .env.example     → Credenciales Green-API + umbrales + configuración de inventario
└── AGENTS.md               → Convenciones del proyecto (gitignored)
```

## Entidades de Datos Principales

- **Base de conocimiento** — `app/data/knowledge_base.json`: array `conocimiento` con 5 entradas base expandidas (5 → 17 preguntas). Entradas: `pregunta_base`, `respuesta`, `sinonimos` (list). Se carga al inicio; editar exige reinicio.
- **Inventario** — tabla `productos` en `inventory.db` (SQLite) **o** `inventory.csv`: columnas `nombre`, `precio`, `stock`. Fuente activa: `INVENTORY_SOURCE_TYPE` (`sqlite` por defecto). Búsqueda difusa combinada (WRatio + partial_ratio) sobre `FUZZY_SCORE_THRESHOLD` (70).
- **Estado de conversación** — dict en memoria en `state_manager.py` keyed por `user_id` (teléfono). Estados: `MENU_PRINCIPAL`, `ESPERANDO_PRODUCTO_STOCK`, `ESPERANDO_PRODUCTO_PRECIO`, `ESPERANDO_DETALLE_FACTURA`. Datos acumulados por usuario (`get_datos`/`set_datos`/`clear_datos`). Acceso protegido con `threading.RLock`. **Sin persistencia entre reinicios.**
- **Facturas** — `app/services/invoice_service.py`: `FacturaDatos(cliente, cedula_rif, concepto, monto, fecha)` → PDF en `app/data/facturas/` (gitignored), número correlativo persistido en `contador.json`. `NEGOCIO_NOMBRE` en el encabezado.
- **Clientes para recordatorios** — `app/data/clientes.json` (gitignored): lista `[{"chat_id": "...@c.us", "nombre": "..."}]`. `scheduled_notifications.enviar_recordatorios_diarios(bot)` envía el recordatorio a cada `chat_id` vía `sendMessage`, reprogramable con `threading.Timer` en `run.py`.
- **Reportes** — `app/services/report_service.py`: `enviar_reporte_email()` envía el log (`chatbot_operations.log` o su respaldo rotativo no vacío) al `OWNER_EMAIL` por SMTP (STARTTLS o SSL, configurable). `OWNER_PHONE` restringe el comando `/reporte`. Logs rotativos: `LOG_MAX_BYTES` (5 MB) y `LOG_BACKUP_COUNT` (3).

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

- **Estable para producción a pequeña escala** (suite completa en verde: 90 pruebas; flujo verificado con REPL local y factura real generada; despliegue 24/7 documentado en `docs/DESPLEGUE.md`).
- Plan original Fases 0–4 **completadas** (estructura modular, comandos, menús, inventario multi-fuente).
- Fase 5 (estabilización) **completada**: tests reparados, `/stock`/`/precio` integrados con inventario real, fuzzy de inventario robustecido, state_manager thread-safe, recarga de knowledge base, README sincronizado.
- Fase 6 (facturación y recordatorios) **completada**: PDFs con `reportlab` + contador correlativo, comando `/factura` en 4 pasos con envío del PDF (`Respuesta(texto, archivo)`), recordatorios diarios con `threading.Timer`, registro de clientes gitignored.
- Fase 7 (robustez y observabilidad) **completada**: reintentos con backoff exponencial en envíos (`retry.py`), logs rotativos (`RotatingFileHandler`), comando `/reporte` por email SMTP restringido al dueño.
- Fase 8 (despliegue como servicio) **completada**: `scripts/install_linux.sh` (unidad `chatbot.service` systemd con usuario dedicado `chatbot`, `.env` validado con permisos 600) y `scripts/install_windows.bat` (tarea programada `ChatbotML`); documentación de operación 24/7 en `docs/DESPLEGUE.md`.
- Deuda técnica remanente: estados sin persistencia entre reinicios, conocimiento sin TTL de caché, sin límite de tamaño en el dict de estados (mejora opcional), conversaciones y facturas sin retención/privacy policy documentada.

## Referencias

- Plan de fases original: `Upgrade_sistema_inventario_chatbot.md` (gitignored).
- Convenciones/commits: `AGENTS.md` (gitignored) y git history.