# STATE.md — Chatbot_With_ML

## Estado Actual

- **Fase actual:** Fase 7 — Robustez y Observabilidad (planificada).
- **Módulo activo:** 7.1 — Reintentos ante errores de la API de WhatsApp.
- **Última acción:** Fase 6 completada y mergeada a `main` (`8b09965`, PR #2): `/factura` con PDFs, `/factura` + `Respuesta(texto, archivo)`, recordatorios diarios (`scheduled_notifications`), docs sincronizadas. Suite: **69 passed**.
- **Siguiente acción:** implementar 7.1 (`app/utils/retry.py` + integración en `message_handler.py` y `scheduled_notifications.py` + tests).
- **Bloqueos:** Ninguno. Entorno de pruebas: venv `/home/nano/Documentos/dev-env` (Python 3.12.3, pytest 9.0.2).
- **Cambios pendientes sin commitear:** `.context/` (STATE/ROADMAP/plans) — planificación de Fase 7.

## Plan Fase 7 — Robustez y Observabilidad

| # | Tarea | Descripción | Estado |
| :-- | :--- | :--- | :--- |
| 7.1 | Reintentos en envíos | `app/utils/retry.py` (`con_reintentos`, backoff exp.), aplicado a `answer`/`answer_with_file` y `sendMessage` | ⬜ **Siguiente** |
| 7.2 | Logs rotativos | `RotatingFileHandler` en `logger.py` (`LOG_MAX_BYTES`, `LOG_BACKUP_COUNT`) | ⬜ Pendiente |
| 7.3 | Comando `/reporte` | Envía log por **email SMTP** al dueño (solo `OWNER_PHONE`); `report_service.py` + config SMTP | ⬜ Pendiente |

## Repositorio

- **Rama:** `main` (`8b09965`, merge PR #2 Fase 6). Propuesta para Fase 7: `feat/robustez-observabilidad` (desde `main`).
- **Remoto:** `origin` — ramas `main`, `feat/local-testing-repl`, `feature/standalone-chatbot`.
- **Últimos commits (main):** `8b09965` (merge PR #2 Fase 6) → `f3591b0` (docs Fase 6) → `f43cb58` (recordatorios) → `57807f5` (/factura) → `2a20a30` (merge Fase 5).

## Fases Completadas

| Fase | Estado | Detalle |
| :--- | :--- | :--- |
| Fase 5 | ✅ Completada | Estabilización: tests verdes, `/stock`/`/precio` reales, thread-safety, recarga de KB. PR #1 → `2a20a30`. |
| Fase 6 | ✅ Completada | Facturación y recordatorios: PDFs (`reportlab`), `/factura`, job diario. PR #2 → `8b09965`. |

## Pendiente / No trackeado (por decisión del usuario)

- `AGENTS.md`, `Upgrade_sistema_inventario_chatbot.md`, `tareas_opencode.md`, `instrucciones_gemini.md`, `PLAN_MONETIZACION.md` están en `.gitignore`.
- `chatbot_operations.log`, `__pycache__/`, `.env`, `inventory.db`, `app/data/facturas/` y `app/data/clientes.json` no se versionan.
- `docs/` no existe pese a aparecer en versiones antiguas del README.