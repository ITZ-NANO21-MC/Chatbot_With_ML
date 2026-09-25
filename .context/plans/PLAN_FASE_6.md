# PLAN FASE 6 — Facturación y Mensajes Programados

**Rama objetivo:** `feat/facturacion` (a crear desde `main`, que contiene Fase 5 mergeada `2a20a30`)
**Objetivo:** comando `/factura` que genera y envía un PDF (reportlab) por WhatsApp, y un job diario de recordatorios/recibos a usuarios activos.
**Prerequisitos:** Fase 5 completada (suite verde, base estable). `green-api` (via `whatsapp-chatbot-python`) expone `Notification.answer_with_file(file, file_name=...)` → `sendFileByUpload`.

---

## Módulo 6.1 — Servicio de factura PDF ✅

**Objetivo:** `app/services/invoice_service.py` genera un PDF de factura a partir de datos simples.

**Tareas:**
- [x] Añadir `reportlab>=4.0.0` a `requirements.txt` e instalarlo en el venv `/home/nano/Documentos/dev-env` (instalado 5.0.1).
- [x] `generar_factura(datos: FacturaDatos) -> str`: recibe cliente, cédula/rif, concepto, monto, fecha; escribe un PDF en `app/data/facturas/` (dir gitignored, auto-creado) con:
      - Encabezado (`NEGOCIO_NOMBRE`, fecha, número de factura correlativo 0001, 0002…).
      - Datos del cliente (nombre, cédula/rif → "N/A" si vacío).
      - Concepto/servicio y monto total (`$1,234.50`).
- [x] Número correlativo persistido en `contador.json` dentro del directorio de salida (sobrevive reinicios).
- [x] Valores inválidos (monto <= 0 / no numérico, nombre vacío, concepto vacío) → `ValueError` con mensaje claro.
- [x] Tests unitarios (`tests/test_invoice_service.py`): PDF empieza por `%PDF` y no está vacío, número correlativo incrementa, contador persiste, excepción ante datos inválidos.

**Criterio de aceptación:** ✅ `generar_factura` devuelve ruta de PDF válido; suite verde (53 tests).

---

## Módulo 6.2 — Comando `/factura` ✅

**Objetivo:** el usuario genera una factura desde WhatsApp `/factura` y recibe el PDF.

**Tareas:**
- [x] **Decisiones de diseño (resueltas):**
      - [x] A) Estado `ESPERANDO_DETALLE_FACTURA` en `state_manager.py` + almacén de datos por usuario (`get_datos`/`set_datos`/`clear_datos`, lock RLock). Flujo de 4 pasos: cliente → cédula/rif → concepto → monto.
      - [x] B) Respuesta estructurada `Respuesta(texto, archivo)`; `procesar_mensaje` queda como wrapper de texto (compatible hacia atrás) y se expone `procesar_mensaje_con_archivo`. `message_handler.py` envía el archivo con `notification.answer_with_file(...)` o texto con `answer()`.
- [x] `message_processor.py`: comando `/factura`, prompts `FACTURA_PROMPT_*`, validación de monto (acepta "," como decimal), generación con `invoice_service.generar_factura` y adjunto de la ruta; limpieza de estado/datos al terminar o ante error.
- [x] `HELP_MESSAGE` actualizado con `/factura`.
- [x] Tests: inicio del flujo, flujo completo (4 pasos → PDF adjunto), monto inválido mantiene el flujo, monto no positivo cierra con error; handler envía con `answer_with_file` (mock) y tests de datos en `state_manager`.

**Criterio de aceptación:** ✅ desde el REPL/WhatsApp, `/factura` + datos produce y envía un PDF (verificado localmente: factura_0002.pdf). Suite: 61 tests.

---

## Módulo 6.3 — Job diario de recordatorios/recibos

**Objetivo:** una tarea diaria recuerda/emite recibos a usuarios activos.

**Tareas:**
- [ ] `app/services/scheduled_notifications.py`: `enviar_recordatorios_diarios(bot)` recorre un registro de chat_ids (fuente pluggable: `app/config.py` → `CLIENTES_PATH`, default `app/data/clientes.json`) y envía un mensaje ─o recibo generado por `invoice_service`─ a cada uno.
- [ ] Disparador diario en `run.py`: utilizar `threading.Timer` (reloj diario simple, sin dependencias nuevas) o documentar alternativa `APScheduler/schedule` si el cron no basta.
- [ ] El job se registra tras `register_handlers` y se ejecuta cada 24 h sin bloquear `bot.run_forever()`.
- [ ] Tests (`tests/test_scheduled_notifications.py`): con `clientes.json` temporal y bot mockeado, `enviar_recordatorios_diarios` llama al envío correcto por cliente; no crashea con lista vacía.

**Criterio de aceptación:** el job envía recordatorios a todos los clientes registrados; destaca bajo tests con mock.

---

## Dependencias y orden

1. **6.1 primero** — el servicio PDF es base del comando y del job.
2. **6.2** — requiere 6.1; introduce la respuesta estructurada (mayor impacto en tests).
3. **6.3** — independiente tras 6.1; requiere decisión de registro de clientes.

## Archivos afectados

- `requirements.txt` (nueva deps: reportlab) (6.1)
- `app/services/invoice_service.py` + `app/data/facturas/` (6.1)
- `tests/test_invoice_service.py` (6.1)
- `app/services/message_processor.py`, `app/services/state_manager.py`, `app/handlers/message_handler.py`, `tests/test_message_processor.py`, `tests/test_handlers.py` (6.2)
- `app/services/scheduled_notifications.py`, `run.py`, `tests/test_scheduled_notifications.py` (6.3)
- `README.md` / `.context` (cierre)