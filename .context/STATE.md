# STATE.md — Chatbot_With_ML

## Estado Actual

- **Fase actual:** Fase 6 — Facturación y Mensajes Programados.
- **Módulo activo:** 6.2 — Comando `/factura` (flujo por estados + envío del PDF).
- **Última acción:** Módulo 6.1 completado — `reportlab` (5.0.1) instalado; `invoice_service.generar_factura()` con número correlativo persistente, validaciones y tests (`tests/test_invoice_service.py`). Config ampliada (`NEGOCIO_NOMBRE`, `FACTURAS_PATH`) y `app/data/facturas/` gitignored. Suite: **53 passed**; PDF de prueba generado correctamente.
- **Siguiente acción:** 6.2 — definir respuesta estructurada `Respuesta(texto, archivo)` y el estado `ESPERANDO_DETALLE_FACTURA`; `/factura` guía por 4 pasos y envía el PDF con `answer_with_file`.
- **Bloqueos:** Ninguno. Entorno de pruebas: venv `/home/nano/Documentos/dev-env` (Python 3.12.3, pytest 9.0.2).
- **Cambios pendientes sin commitear:** `.context/` (STATE/ROADMAP/plans) — planificación de Fase 6.

## Plan Fase 6 — Facturación y Mensajes Programados

| # | Tarea | Descripción | Estado |
| :-- | :--- | :--- | :--- |
| 6.1 | Servicio de factura PDF | `reportlab` en requirements; `invoice_service.generar_factura()`: cliente, cédula/rif, concepto, monto, fecha → PDF | ⬜ **Siguiente** |
| 6.2 | Comando `/factura` | Estado `ESPERANDO_DETALLE_FACTURA`; recoger datos por menú en `message_processor.py`; generar PDF y enviarlo con `answer_with_file` en `message_handler.py` | ⬜ Pendiente |
| 6.3 | Job diario de recordatorios | `scheduled_notifications.py`: tarea diaria que recuerda/emite recibos a usuarios activos (registro pluggable de chat_ids) | ⬜ Pendiente |

## Repositorio

- **Rama:** `main` (activa tras merge de Fase 5). Propuesta para Fase 6: `feat/facturacion` (desde `main`).
- **Remoto:** `origin` — ramas `main` y `feat/local-testing-repl`.
- **Últimos commits (main):** `2a20a30` (merge Fase 5) → `e0c0167` (thread-safety + recarga) → `dade28f` (inventario unificado) → `837a0a6` (SDD + limpieza).

## Pendiente / No trackeado (por decisión del usuario)

- `AGENTS.md`, `Upgrade_sistema_inventario_chatbot.md`, `tareas_opencode.md`, `instrucciones_gemini.md`, `PLAN_MONETIZACION.md` están en `.gitignore`.
- `chatbot_operations.log`, `__pycache__/`, `.env` e `inventory.db` no se versionan.
- `docs/` no existe pese a aparecer en versiones antiguas del README.