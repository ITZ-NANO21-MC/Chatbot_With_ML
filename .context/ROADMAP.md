# ROADMAP.md — Chatbot_With_ML

## Progreso General

| Fase | Estado | Descripción |
| :--- | :--- | :--- |
| Fase 1 | ✅ Completada | Arquitectura modular: `app/handlers`, `app/services`, `app/utils`, `config.py`, logging centralizado (refactor `c4fb5fa`). |
| Fase 2 | ✅ Completada | Comandos básicos `/stock`, `/precio`, `/contacto`, `/horario` (commit `881eee5`). |
| Fase 3 | ✅ Completada | Conversación con menús y gestión de estado por usuario (commit `4981dd7`). |
| Fase 4 | ✅ Completada | Inventario multi-fuente SQLite/CSV (commit `b4aafb1`). |
| Fase 5 | ✅ Completada | Estabilización y deuda técnica (tests verdes, mensajes coherentes, docs sincronizadas). |
| Fase 6 | ✅ Completada | Facturación y mensajes programados (PDFs, `/factura`, recordatorios). |
| Fase 7 | ✅ Completada | Robustez, logs rotativos y reportes. |
| Fase 8 | ⬜ Pendiente | Despliegue como servicio (systemd). |

---

## Fase 5 — Estabilización y Deuda Técnica (completada)

**Objetivo:** Dejar el proyecto con tests verdes y documentación alineada al código real antes de añadir funcionalidad nueva. Es prerequisito para Fases 6–8.

### Módulos
- [x] **Reparar tests rotos** — `tests/test_engine.py` ➜ import a `app.services.chatbot_engine`; `test_api.py` reemplazado por `test_handlers.py`/`test_message_processor.py`. Bug de mensajes solo-espacios corregido.
- [x] **Limpiar mensajes obsoletos** — `/stock` y `/precio` inician el flujo de inventario real (estados `ESPERANDO_PRODUCTO_*`); eliminadas `STOCK_MESSAGE`/`PRECIO_MESSAGE`. Fuzzy de inventario robustecido (WRatio + partial_ratio) con `tests/test_inventory_service.py`.
- [x] **Sincronizar README y .env.example** — README reescrito con estructura real y `CONTEXT.md` actualizado (árbol, entidades, madurez).
- [x] **Concurrencia en `state_manager.py`** — `threading.RLock` protege get/set/clear; tests multi-hilo (`tests/test_state_manager.py`). Mejora opcional no aplicada: TTL/límite de tamaño.
- [x] **Recarga de `knowledge_base.json`** — `ChatbotEngine.recargar_conocimiento()` reentrena el vectorizador sin reiniciar; test de recarga que refleja ediciones del JSON.

**Cierre:** Suite completa: **45 pruebas en verde**. REPL local verificado. Commits: `dade28f` (5.1–5.3) y cierre 5.4–5.5.

### Dependencias
- Tests reparados ✅ (bloqueo principal resuelto).

---

## Fase 6 — Facturación y Mensajes Programados (completada)

**Objetivo:** Comando `/factura` que genere un PDF (reportlab) y job diario de recordatorios a usuarios activos. *(Referencia: Fase 5 del plan original.)*

### Módulos
- [x] `app/services/invoice_service.py` — generación de PDF con `reportlab` (5.0.1), número correlativo persistido en `contador.json`, validaciones → `ValueError`. Tests: `tests/test_invoice_service.py`. *(commit `c979e3b`)*
- [x] Comando `/factura` — flujo por estados de 4 pasos (cliente → cédula/RIF → concepto → monto) en `message_processor.py`; respuesta estructurada `Respuesta(texto, archivo)`; envío del PDF con `answer_with_file` en `message_handler.py`. Tests: `tests/test_message_processor.py`, `tests/test_handlers.py`. *(commit `57807f5`)*
- [x] Job diario de recordatorios — `scheduled_notifications.py` envía vía `sendMessage` a `clientes.json` (gitignored); disparador `threading.Timer` de 24 h en `run.py`. Tests: `tests/test_scheduled_notifications.py`. *(commit `f43cb58`)*

**Cierre:** Suite completa: **69 pruebas en verde**. Flujo de factura verificado con PDF real (factura_0002.pdf). Rama: `feat/facturacion`.

### Dependencias
- Fase 5 completada (tests verdes, base estable).

---

## Fase 7 — Robustez y Observabilidad (completada)

**Objetivo:** Reintentos ante errores de red en la API, logs rotativos y comando `/reporte` para el dueño. *(Referencia: Fase 6 del plan original.)* Detalle en `.context/plans/PLAN_FASE_7.md`.

### Módulos
- [x] **Planificación** — canal de `/reporte` decidido con el dueño: **email SMTP** (stdlib `smtplib`, sin dependencias nuevas); módulos 7.1 (retries), 7.2 (logs rotativos), 7.3 (`/reporte` por email). Rama `feat/robustez-observabilidad`.
- [x] **7.1 Reintentos en envíos** — `app/utils/retry.py` (`con_reintentos`, backoff exp.; excepciones transitorias) aplicado a `answer`/`answer_with_file` y `sendMessage`. Tests: `tests/test_retry.py`. *(commit `84d5dd8`)*
- [x] **7.2 Logs rotativos** — `RotatingFileHandler` en `app/utils/logger.py` (`configurar_logging()` idempotente, `LOG_MAX_BYTES`/`LOG_BACKUP_COUNT`). Tests: `tests/test_logger.py`. *(commit `0367fd0`)*
- [x] **7.3 Comando `/reporte`** — `app/services/report_service.py` (email SMTP adjuntando el log; STARTTLS/SSL; cierre garantizado), restringido a `OWNER_PHONE`. Config `SMTP_*`/owner en `.env`. Tests: `tests/test_report_service.py`. *(commit `84d31b3`)*

**Cierre:** Suite completa: **90 pruebas en verde**. ADR-007 (retry policy) y ADR-008 (canal email) documentados. Rama: `feat/robustez-observabilidad`.

### Dependencias
- Fase 5 completada.

---

## Fase 8 — Despliegue como Servicio (pendiente)

**Objetivo:** El bot arranca automáticamente al encender la máquina del cliente. *(Referencia: Fase 7 del plan original.)*

### Módulos
- [ ] `install.sh` que configure `systemd` (Linux) o tarea programada (Windows).
- [ ] Documentación de operación 24/7 (`systemctl status chatbot`).

### Dependencias
- Fases 6–7 completadas (funcionalidad estabilizada).

---

## Fases Completadas (referencia)

### Fase 4 — Inventario Multi-Fuente (completada)
- `app/services/inventory_service.py` con `buscar_producto()` y arquitectura SQLite/CSV vía `INVENTORY_SOURCE_TYPE`.
- Búsqueda difusa combinada (WRatio + partial_ratio) con `FUZZY_SCORE_THRESHOLD`.
- Datos de ejemplo: `app/data/inventory.db`, `app/data/inventory.csv`.

### Fase 3 — Conversación con Menús (completada)
- `app/services/state_manager.py` con 3 estados (`MENU_PRINCIPAL`, `ESPERANDO_PRODUCTO_STOCK`, `ESPERANDO_PRODUCTO_PRECIO`).
- Menú numérico (1 stock, 2 precio, 3 contacto/horario, 4 IA).

### Fase 2 — Comandos Básicos (completada)
- Comandos `/start`, `/ayuda`, `/stock`, `/precio`, `/contacto`, `/horario` con respuestas estáticas.

### Fase 1 — Arquitectura Modular (completada)
- Separación en `handlers/`, `services/`, `utils/` tras refactor `c4fb5fa`.
- `app/config.py` con variable de entorno y `validate_credentials()`.
- `app/utils/logger.py` con logging centralizado.