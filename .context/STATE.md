# STATE.md — Chatbot_With_ML

## Estado Actual

- **Fase actual:** Fase 6 — Facturación y Mensajes Programados.
- **Módulo activo:** Cierre de Fase 6 (README, verificación final y merge a `main`).
- **Última acción:** Módulo 6.3 completado — `scheduled_notifications.py` (recordatorio diario vía `sendMessage`, registro `clientes.json` gitignored configurable con `CLIENTES_PATH`), disparador `threading.Timer` de 24 h en `run.py`, tests con mock. Suite: **69 passed**.
- **Siguiente acción:** cierre de la Fase 6: sincronizar README y `.context/CONTEXT.md` (nuevos servicios, config, `Respuesta` estructurada), merge de `feat/facturacion` a `main` y push con PR.
- **Bloqueos:** Ninguno. Entorno de pruebas: venv `/home/nano/Documentos/dev-env` (Python 3.12.3, pytest 9.0.2).
- **Cambios pendientes sin commitear:** `.context/` (STATE/ROADMAP/plans) — planificación de Fase 6.

## Plan Fase 6 — Facturación y Mensajes Programados

| # | Tarea | Descripción | Estado |
| :-- | :--- | :--- | :--- |
| 6.1 | Servicio de factura PDF | `reportlab` en requirements; `invoice_service.generar_factura()`: cliente, cédula/rif, concepto, monto, fecha → PDF | ✅ Completado |
| 6.2 | Comando `/factura` | Estado `ESPERANDO_DETALLE_FACTURA`; guía por 4 pasos; respuesta `Respuesta(texto, archivo)`; envío con `answer_with_file` | ✅ Completado |
| 6.3 | Job diario de recordatorios | `scheduled_notifications.py`: recordatorio diario con `threading.Timer` en `run.py`, registro `clientes.json` (gitignored), envía vía `sendMessage` | ✅ Completado |

## Repositorio

- **Rama:** `main` (activa tras merge de Fase 5). Propuesta para Fase 6: `feat/facturacion` (desde `main`).
- **Remoto:** `origin` — ramas `main` y `feat/local-testing-repl`.
- **Últimos commits (main):** `2a20a30` (merge Fase 5) → `e0c0167` (thread-safety + recarga) → `dade28f` (inventario unificado) → `837a0a6` (SDD + limpieza).

## Pendiente / No trackeado (por decisión del usuario)

- `AGENTS.md`, `Upgrade_sistema_inventario_chatbot.md`, `tareas_opencode.md`, `instrucciones_gemini.md`, `PLAN_MONETIZACION.md` están en `.gitignore`.
- `chatbot_operations.log`, `__pycache__/`, `.env` e `inventory.db` no se versionan.
- `docs/` no existe pese a aparecer en versiones antiguas del README.