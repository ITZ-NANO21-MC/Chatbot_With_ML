# PLAN FASE 6 — Facturación y Mensajes Programados

**Rama objetivo:** `feat/facturacion` (a crear desde `main`, que contiene Fase 5 mergeada `2a20a30`)
**Objetivo:** comando `/factura` que genera y envía un PDF (reportlab) por WhatsApp, y un job diario de recordatorios/recibos a usuarios activos.
**Prerequisitos:** Fase 5 completada (suite verde, base estable). `green-api` (via `whatsapp-chatbot-python`) expone `Notification.answer_with_file(file, file_name=...)` → `sendFileByUpload`.

---

## Módulo 6.1 — Servicio de factura PDF

**Objetivo:** `app/services/invoice_service.py` genera un PDF de factura a partir de datos simples.

**Tareas:**
- [ ] Añadir `reportlab>=4.0.0` a `requirements.txt` e instalarlo en el venv `/home/nano/Documentos/dev-env`.
- [ ] `generar_factura(datos: FacturaDatos) -> str` (o `Path`): recibe cliente, cédula/rif, concepto, monto, fecha; escribe un PDF en `app/data/facturas/` (directorio con `.gitignore` o creado automáticamente) con:
      - Encabezado (nombre del negocio, fecha, número de factura correlativo).
      - Datos del cliente (nombre, cédula/rif).
      - Concepto/servicio y monto total.
- [ ] Valores inválidos (monto negativo, nombre vacío, concepto vacío) → `ValueError` con mensaje claro.
- [ ] Tests unitarios (`tests/test_invoice_service.py`): el PDF se crea y no está vacío (`size > 0`, comienza por `%PDF`), número correlativo incrementa, excepción ante datos inválidos.

**Criterio de aceptación:** `generar_factura` devuelve una ruta válida de PDF; suite verde.

---

## Módulo 6.2 — Comando `/factura`

**Objetivo:** el usuario genera una factura desde WhatsApp `/factura` y recibe el PDF.

**Tareas:**
- [ ] **Decisiones de diseño (resolver al implementar):**
      - [ ] A) Nueva constante/estado `ESPERANDO_DETALLE_FACTURA` en `state_manager.py` (más 2 entradas de datos: cliente/rif y concepto+monto) — coherente con el flujo de menú actual.
      - [ ] B) Estructura de la respuesta: `procesar_mensaje` hoy devuelve `str`. Para entregar el PDF, introducir `Respuesta(texto: str, archivo: Optional[str])` y adaptar `message_handler.py` al envío con `answer_with_file`. Evaluar impacto en tests existentes (aseveran `== str`).
- [ ] `message_processor.py`: reconocer `/factura`, guiar al usuario (cliente → cédula/rif → concepto → monto), invocar `invoice_service.generar_factura`, devolver respuesta con texto + ruta del archivo.
- [ ] `message_handler.py`: si la respuesta trae `archivo`, `notification.answer_with_file(archivo, file_name="factura.pdf", caption=texto)`; si no, `notification.answer(texto)` como hoy.
- [ ] Tests: flujo `/factura` completo (4 pasos) genera PDF y devuelve ruta; validación de monto inválido lleva a mensaje de error; handler envía con `answer_with_file` (mock).

**Criterio de aceptación:** desde el REPL/WhatsApp, `/factura` + datos produce y envía un PDF con costos correctos.

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