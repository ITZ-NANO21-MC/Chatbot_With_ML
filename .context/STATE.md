# STATE.md — Chatbot_With_ML

## Estado Actual

- **Fase actual:** Fase 6 — Facturación y Mensajes Programados.
- **Módulo activo:** 6.1 — `app/services/invoice_service.py` (generación de PDF con reportlab).
- **Última acción:** Fase 5 completada y mergeada en `main` (PR #1, commit `2a20a30`). Suite: **45 passed**. Fase 6 seleccionada vía `/plan-phase --phase 6`.
- **Siguiente acción:** 6.1 — añadir `reportlab` a `requirements.txt`, crear `invoice_service.py` (generación de factura PDF) y sus tests.
- **Bloqueos:** Ninguno. Entorno de pruebas: venv `/home/nano/Documentos/dev-env` (Python 3.12.3, pytest 9.0.2). Determinado que `green-api` expone `answer_with_file(file, file_name)` para el envío de documentos.
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