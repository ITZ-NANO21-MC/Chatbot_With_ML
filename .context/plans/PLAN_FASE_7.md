# PLAN FASE 7 — Robustez y Observabilidad

**Rama objetivo:** `feat/robustez-observabilidad` (a crear desde `main`, que contiene Fase 6 mergeada `8b09965`)
**Objetivo:** el bot tolera errores transitorios de la API de Green-API (retries), los logs rotan en archivo sin crecer indefinidamente, y el dueño puede pedir `/reporte` para recibir el estado por **email (SMTP)**.
**Prerequisitos:** Fase 6 completada (suite verde: 69 pruebas). Logging centralizado en `app/utils/logger.py` (`FileHandler` simple, a migrar a `RotatingFileHandler`). Envíos de salida en `message_handler.py` (`notification.answer` / `answer_with_file`) y `scheduled_notifications.py` (`bot.api.sending.sendMessage`).
**Decisión de producto (confirmada por el dueño):** el canal de `/reporte` es **email vía SMTP** (stdlib `smtplib`), adjuntando el log rotativo actual. Sin dependencias nuevas.

---

## Módulo 7.1 — Reintentos ante errores de la API de WhatsApp

**Objetivo:** encapsular un patrón de reintento con backoff para los envíos de salida, de modo que errores transitorios de red (timeouts, conexión, 5xx) no descarten respuestas.

**Tareas:**
- [ ] `app/utils/retry.py`: helper `con_reintentos(intentos=3, retraso_base=1.0, factor=2.0)` — decorador que reintenta solo sobre excepciones "transitorias" indicadas (por defecto: `ConnectionError`, `TimeoutError`, `OSError`), con backoff exponencial y log de cada intento; relanza la última excepción al agotar intentos.
- [ ] Aplicarlo en `message_handler.py` alrededor de `notification.answer(...)` y `notification.answer_with_file(...)` (no alrededor de todo el handler: solo el envío, para no reprocesar el mensaje entrante).
- [ ] Aplicarlo en `scheduled_notifications.py` alrededor de `bot.api.sending.sendMessage(...)` (cada envío, respetando el try/except por cliente existente).
- [ ] Tests (`tests/test_retry.py`): función que falla N veces y luego tiene éxito → se ejecuta el número correcto de intentos y no lanza excepción; función que siempre falla → relanza tras `intentos`; excepción no transitoria → no se reintenta.

**Criterio de aceptación:** un fallo transitorio en el envío se reintenta automáticamente (con log) y el mensaje se entrega; suite verde.

---

## Módulo 7.2 — Logs de conversaciones en archivo rotativo

**Objetivo:** sustituir el `FileHandler` estático por `RotatingFileHandler` para que `chatbot_operations.log` no crezca indefinidamente.

**Tareas:**
- [ ] `config.py`: `LOG_MAX_BYTES` (default `5_242_880`, 5 MB) y `LOG_BACKUP_COUNT` (default `3`) vía entorno.
- [ ] `app/utils/logger.py`: `RotatingFileHandler(config.LOG_FILE_PATH, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT, encoding="utf-8")` manteniendo `StreamHandler` y el mismo formato. Evitar registros duplicados si el módulo se importa varias veces (guard para handlers ya vinculados).
- [ ] Tests (`tests/test_logger.py`): los valores de config se parsean correctamente; con `maxBytes` pequeño se rota el archivo y aparece el backup `chatbot_operations.log.1`; el handler no se duplica en el logger raíz al reinicializar.

**Criterio de aceptación:** el log rota por tamaño creando respaldos numerados; suite verde.

---

## Módulo 7.3 — Comando `/reporte` que envía el log por email al dueño

**Objetivo:** el dueño (chat id de WhatsApp configurado) ejecuta `/reporte` y el bot envía el log actual por **email** con `smtplib`.

**Tareas:**
- [ ] `config.py`: `OWNER_PHONE` (chat id de WhatsApp, p. ej. `5891...@c.us`), `OWNER_EMAIL`, `SMTP_HOST`, `SMTP_PORT` (default 587), `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` (fallback `SMTP_USER`), `SMTP_SSL` opcional. Todos por entorno; si faltan credenciales SMTP, `/reporte` queda deshabilitado con log de advertencia.
- [ ] `app/services/report_service.py`: `enviar_reporte_email(destinatario, asunto, adjunto_path=None)` — valida configuración (`ValueError` si faltan datos), construye `MIMEMultipart` (texto de resumen + adjunto del log vía `MIMEText`/`MIMEApplication`, `base64`), envía con `smtplib.SMTP` + `starttls`/`login` (o SSL según config). El adjunto se lee del `LOG_FILE_PATH` actual (o del `.1` más reciente si está vacío).
- [ ] `message_processor.py`: comando `COMMAND_REPORTE` (`/reporte`); **solo** responde al `OWNER_PHONE` (si `OWNER_PHONE` no está configurado o el emisor no es el dueño → respuesta neutra "No disponible"/ignora). Al recibirlo: invoca `report_service.enviar_reporte_email` y responde confirmación; ante error SMTP responde mensaje de error (sin adjuntar directamente al chat).
- [ ] `HELP_MESSAGE` actualizado con `/reporte` (marcado como opción del dueño).
- [ ] `.env.example` con las nuevas variables comentadas.
- [ ] Tests (`tests/test_report_service.py` + `tests/test_message_processor.py`): `enviar_reporte_email` con `smtplib.SMTP` mockeado envía el adjunto y cierra conexión; falta de config → `ValueError`/deshabilitado; `/reporte` del dueño → confirmación y llamada al servicio; `/reporte` de otro usuario → sin llamada y respuesta neutra.

**Criterio de aceptación:** desde el chat del dueño, `/reporte` entrega el log por email (verificado con mock); cualquier otro emisor no recibe el log.

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