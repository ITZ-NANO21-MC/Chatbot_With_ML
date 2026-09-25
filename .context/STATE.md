# STATE.md — Chatbot_With_ML

## Estado Actual

- **Fase actual:** Fase 8 — Despliegue como Servicio.
- **Módulo activo:** Planificación de la Fase 8 (decisiones tomadas; scripts y docs pendientes de implementar).
- **Última acción:** Plan Fase 8 definido — plataformas **Linux systemd + Windows tarea programada**; usuario del servicio **dedicado `chatbot`**; `.env` **validado + copiado desde plantilla**. Detalle en `.context/plans/PLAN_FASE_8.md`.
- **Siguiente acción:** módulo 8.1 — `scripts/install_linux.sh` (unidad `chatbot.service`, usuario `chatbot`, venv, `.env` 600) y `scripts/install_windows.bat` (`schtasks`).
- **Bloqueos:** Ninguno. Entorno de pruebas: venv `/home/nano/Documentos/dev-env` (Python 3.12.3, pytest 9.0.2). Prueba de sistema real requiere confirmación del dueño (crea usuario/servicio).
- **Cambios pendientes sin commitear:** plan Fase 8 + `.context/` (STATE/ROADMAP).

## Plan Fase 8 — Despliegue como Servicio

| # | Tarea | Descripción | Estado |
| :-- | :--- | :--- | :--- |
| 8.1 | Scripts de instalación | `install_linux.sh` (systemd + usuario `chatbot` + `.env` 600) y `install_windows.bat` (tarea programada) | ⬜ Pendiente |
| 8.2 | Documentación de operación | `docs/DESPLEGUE.md` (Linux systemd + Windows, logs, actualización, rollback) | ⬜ Pendiente |

## Repositorio

- **Rama:** `main` (`27c55b6`, merge PR #3 Fase 7). Propuesta para Fase 8: `feat/despliegue-servicio` (desde `main`).
- **Remoto:** `origin` — ramas `main`, `feat/local-testing-repl`, `feature/standalone-chatbot`.
- **Últimos commits (main):** `27c55b6` (merge PR #3 Fase 7) → `6b666c6` (docs Fase 7) → `84d31b3` (/reporte) → `0367fd0` (logs rotativos) → `84d5dd8` (retries).

## Fases Completadas

| Fase | Estado | Detalle |
| :--- | :--- | :--- |
| Fase 5 | ✅ Completada | Estabilización: tests verdes, `/stock`/`/precio` reales, thread-safety, recarga de KB. PR #1 → `2a20a30`. |
| Fase 6 | ✅ Completada | Facturación y recordatorios: PDFs (`reportlab`), `/factura`, job diario. PR #2 → `8b09965`. |
| Fase 7 | ✅ Completada | Robustez: retries (`retry.py`), logs rotativos (`RotatingFileHandler`), `/reporte` por email. ADR-007/008. Rama `feat/robustez-observabilidad`. |

## Pendiente / No trackeado (por decisión del usuario)

- `AGENTS.md`, `Upgrade_sistema_inventario_chatbot.md`, `tareas_opencode.md`, `instrucciones_gemini.md`, `PLAN_MONETIZACION.md` están en `.gitignore`.
- `chatbot_operations.log`, `__pycache__/`, `.env`, `inventory.db`, `app/data/facturas/` y `app/data/clientes.json` no se versionan.
- `docs/` no existe pese a aparecer en versiones antiguas del README.