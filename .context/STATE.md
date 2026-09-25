# STATE.md — Chatbot_With_ML

## Estado Actual

- **Fase actual:** Fase 6 — Facturación y Mensajes Programados.
- **Módulo activo:** 6.3 — Job diario de recordatorios/recibos.
- **Última acción:** Módulo 6.2 completado — `/factura` con estado `ESPERANDO_DETALLE_FACTURA` (4 pasos), respuesta estructurada `Respuesta(texto, archivo)`, envío del PDF con `answer_with_file`, almacén de datos por usuario en `state_manager`. Flujo real verificado (factura_0002.pdf). Suite: **61 passed**.
- **Siguiente acción:** 6.3 — `scheduled_notifications.py` (recordatorios diarios a clientes registrados), disparador en `run.py` y tests con mock.
- **Bloqueos:** Ninguno. Entorno de pruebas: venv `/home/nano/Documentos/dev-env` (Python 3.12.3, pytest 9.0.2).
- **Cambios pendientes sin commitear:** `.context/` (STATE/ROADMAP/plans) — planificación de Fase 6.

## Plan Fase 6 — Facturación y Mensajes Programados

| # | Tarea | Descripción | Estado |
| :-- | :--- | :--- | :--- |
| 6.1 | Servicio de factura PDF | `reportlab` en requirements; `invoice_service.generar_factura()`: cliente, cédula/rif, concepto, monto, fecha → PDF | ✅ Completado |
| 6.2 | Comando `/factura` | Estado `ESPERANDO_DETALLE_FACTURA`; guía por 4 pasos; respuesta `Respuesta(texto, archivo)`; envío con `answer_with_file` | ✅ Completado |
| 6.3 | Job diario de recordatorios | `scheduled_notifications.py`: tarea diaria que recuerda/emite recibos a usuarios activos (registro pluggable de chat_ids) | ⬜ **Siguiente** |

## Repositorio

- **Rama:** `main` (activa tras merge de Fase 5). Propuesta para Fase 6: `feat/facturacion` (desde `main`).
- **Remoto:** `origin` — ramas `main` y `feat/local-testing-repl`.
- **Últimos commits (main):** `2a20a30` (merge Fase 5) → `e0c0167` (thread-safety + recarga) → `dade28f` (inventario unificado) → `837a0a6` (SDD + limpieza).

## Pendiente / No trackeado (por decisión del usuario)

- `AGENTS.md`, `Upgrade_sistema_inventario_chatbot.md`, `tareas_opencode.md`, `instrucciones_gemini.md`, `PLAN_MONETIZACION.md` están en `.gitignore`.
- `chatbot_operations.log`, `__pycache__/`, `.env` e `inventory.db` no se versionan.
- `docs/` no existe pese a aparecer en versiones antiguas del README.