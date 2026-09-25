# PLAN FASE 7 — Robustez y Observabilidad

**Rama objetivo:** `feat/robustez-observabilidad` (a crear desde `main`, que contiene Fase 6 mergeada `8b09965`)
**Objetivo:** el bot tolera errores transitorios de la API de Green-API (retries), los logs rotan en archivo sin crecer indefinidamente, y el dueño puede pedir `/reporte` para recibir el estado por **email (SMTP)**.
**Prerequisitos:** Fase 6 completada (suite verde: 69 pruebas). Logging centralizado en `app/utils/logger.py` (`FileHandler` simple, a migrar a `RotatingFileHandler`). Envíos de salida en `message_handler.py` (`notification.answer` / `answer_with_file`) y `scheduled_notifications.py` (`bot.api.sending.sendMessage`).
**Decisión de producto (confirmada por el dueño):** el canal de `/reporte` es **email vía SMTP** (stdlib `smtplib`), adjuntando el log rotativo actual. Sin dependencias nuevas.

---

## Módulo 7.1 — Reintentos ante errores de la API de WhatsApp ✅

**Objetivo:** encapsular un patrón de reintento con backoff para los envíos de salida, de modo que errores transitorios de red (timeouts, conexión, 5xx) no descarten respuestas.

**Tareas:**
- [x] `app/utils/retry.py`: `con_reintentos(intentos=3, retraso_base=1.0, factor=2.0, excepciones=...)` — decorador que reintenta solo sobre excepciones "transitorias" indicadas (por defecto: `ConnectionError`, `TimeoutError`, `OSError`), con backoff exponencial y log de cada intento; relanza la última excepción al agotar intentos; rechaza `intentos < 1` con `ValueError`; tolera funciones sin `__name__` (p. ej. mocks).
- [x] Aplicado en `message_handler.py` alrededor de `notification.answer(...)` y `notification.answer_with_file(...)` (solo el envío, sin reprocesar el mensaje entrante) — también en el mensaje de error de respaldo.
- [x] Aplicado en `scheduled_notifications.py` alrededor de `bot.api.sending.sendMessage(...)` (cada envío, respetando el try/except por cliente existente).
- [x] Tests (`tests/test_retry.py`): éxito al primer intento (sin reintento), fallo transitorio → éxito (intentos contados), siempre falla → relanza tras agotar, excepción no transitoria → sin reintento, `intentos < 1` → `ValueError`, backoff exponencial (esperas `[1.0, 2.0, 4.0]`), excepciones personalizadas.

**Criterio de aceptación:** ✅ un fallo transitorio en el envío se reintenta automáticamente (con log) y el mensaje se entrega. Suite: 76 tests.

---

## Módulo 7.2 — Logs de conversaciones en archivo rotativo ✅

**Objetivo:** sustituir el `FileHandler` estático por `RotatingFileHandler` para que `chatbot_operations.log` no crezca indefinidamente.

**Tareas:**
- [x] `config.py`: `LOG_MAX_BYTES` (default `5_242_880`, 5 MB) y `LOG_BACKUP_COUNT` (default `3`) vía entorno.
- [x] `app/utils/logger.py`: refactorizado con `configurar_logging(raiz)` idempotente (no duplica handlers), handler de archivo `RotatingFileHandler` (maxBytes/backupCount/encoding utf-8) + `StreamHandler`; configuración inicial en el import. Los loggers `app.*` (hijos del raíz "app") heredan los handlers.
- [x] `.env.example` documenta `LOG_MAX_BYTES` y `LOG_BACKUP_COUNT`.
- [x] Tests (`tests/test_logger.py`): valores de config parseados como enteros válidos; escritura al archivo configurado; rotación por tamaño crea respaldos `.1`/`.2` (maxBytes pequeño); `configurar_logging` no duplica handlers.

**Criterio de aceptación:** ✅ el log rota por tamaño creando respaldos numerados (verificado: `demo.log.1`, `demo.log.2`); suite: 80 tests.

---

## Módulo 7.3 — Comando `/reporte` que envía el log por email al dueño ✅

**Objetivo:** el dueño (chat id de WhatsApp configurado) ejecuta `/reporte` y el bot envía el log actual por **email** con `smtplib`.

**Tareas:**
- [x] `config.py`: `OWNER_PHONE`, `OWNER_EMAIL`, `SMTP_HOST`, `SMTP_PORT` (default 587), `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` (fallback `SMTP_USER`), `SMTP_SSL` (bool parseado). Credenciales solo en `.env`.
- [x] `app/services/report_service.py`: `enviar_reporte_email(destinatario, asunto, ruta_adjunto)` — valida config (`ValueError` si incompleta), construye `MIMEMultipart` con adjunto del log (`_seleccionar_log`: prefiere el actual; si está vacío usa el respaldo `.1` más reciente), conecta con `SMTP`+STARTTLS o `SMTP_SSL`, cierra conexión siempre (`finally`).
- [x] `message_processor.py`: comando `COMMAND_REPORTE` (`/reporte`); responde solo al `OWNER_PHONE` (sin config → `REPORTE_DESACTIVADO`; otro usuario → `REPORTE_NO_AUTORIZADO`); invoca `report_service` y responde confirmación o `REPORTE_ERROR`.
- [x] `HELP_MESSAGE` actualizado con `/reporte`.
- [x] `.env.example` documenta las variables SMTP/owner.
- [x] Tests (`tests/test_report_service.py` + `tests/test_message_processor.py`): SMTP mockeado envía adjunto y cierra conexión; `SMTP_SSL` usa `SMTP_SSL`; destinatario/asunto personalizados; `_seleccionar_log` prioriza actual/no-vacío; `/reporte` desactivado/no autorizado/dueno/error.

**Criterio de aceptación:** ✅ desde el chat del dueño, `/reporte` entrega el log por email (verificado con mock); cualquier otro emisor no recibe el log. Suite: 90 tests.

---

## Dependencias y orden

1. **7.1 primero** — infraestructura transparente de envíos; se integra en los dos puntos de salida existentes.
2. **7.2** — independiente, pero 7.3 adjunta el log rotativo (requiere que exista).
3. **7.3** — requiere 7.2 (adjunto del log) y la config SMTP/owner.

## Archivos afectados

- `app/utils/retry.py` + `tests/test_retry.py` (7.1)
- `app/handlers/message_handler.py`, `app/services/scheduled_notifications.py` (7.1)
- `app/utils/logger.py` + `tests/test_logger.py` (7.2)
- `app/services/report_service.py` + `tests/test_report_service.py` (7.3)
- `app/services/message_processor.py`, `app/config.py`, `.env.example`, `tests/test_message_processor.py` (7.3)
- `README.md` / `.context` (CONTEXT, ROADMAP, STATE, DECISIONS con ADR-007/008) (cierre)