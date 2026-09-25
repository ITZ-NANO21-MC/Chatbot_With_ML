# STATE.md — Chatbot_With_ML

## Estado Actual

- **Fase actual:** Fase 8 — Despliegue como Servicio.
- **Módulo activo:** Cierre de Fase 8 (docus sincronizadas; verificación y merge a `main`).
- **Última acción:** Módulo 8.2 completado — `docs/DESPLEGUE.md` (operación 24/7 Linux + Windows, actualización, rollback, seguridad) y `docs/` creado por fin. Scripts 8.1 verificados con `bash -n` + dry-run `--check`. Suite: **90 passed**.
- **Siguiente acción:** cierre de la Fase 8: commit docs, merge `feat/despliegue-servicio` → `main` con PR #4.
- **Bloqueos:** Ninguno. Despliegue real del servicio (crea usuario/servicio) queda como rutina opcional del dueño; el dry-run confirmó el flujo sin tocar la máquina.
- **Cambios pendientes sin commitear:** `docs/` + `.context/` + README (cierre 8.2).

## Plan Fase 8 — Despliegue como Servicio

| # | Tarea | Descripción | Estado |
| :-- | :--- | :--- | :--- |
| 8.1 | Scripts de instalación | `install_linux.sh` (systemd + usuario `chatbot` + `.env` 600) y `install_windows.bat` (tarea `ChatbotML`) | ✅ Completado |
| 8.2 | Documentación de operación | `docs/DESPLEGUE.md` (Linux systemd + Windows, logs, actualización, rollback) | ✅ Completado |

## Repositorio

- **Rama:** `main` (`27c55b6`, merge PR #3 Fase 7). Propuesta para Fase 8: `feat/despliegue-servicio` (desde `main`, plan en `5c9a8d0`).
- **Remoto:** `origin` — ramas `main`, `feat/local-testing-repl`, `feature/standalone-chatbot`.
- **Últimos commits (main):** `27c55b6` (merge PR #3 Fase 7) → `6b666c6` (docs Fase 7) → `84d31b3` (/reporte). Rama Fase 8: `5c9a8d0` (plan) → `d3f1da5` (scripts 8.1) → docs 8.2 (pendiente).

## Fases Completadas

| Fase | Estado | Detalle |
| :--- | :--- | :--- |
| Fase 5 | ✅ Completada | Estabilización: tests verdes, `/stock`/`/precio` reales, thread-safety, recarga de KB. PR #1 → `2a20a30`. |
| Fase 6 | ✅ Completada | Facturación y recordatorios: PDFs (`reportlab`), `/factura`, job diario. PR #2 → `8b09965`. |
| Fase 7 | ✅ Completada | Robustez: retries (`retry.py`), logs rotativos (`RotatingFileHandler`), `/reporte` por email. ADR-007/008. Rama `feat/robustez-observabilidad`. |
| Fase 8 | ✅ Completada | Despliegue: `install_linux.sh` (systemd, usuario `chatbot`) + `install_windows.bat` (tarea `ChatbotML`), `docs/DESPLEGUE.md`. ADR-009. Rama `feat/despliegue-servicio`. |

## Pendiente / No trackeado (por decisión del usuario)

- `AGENTS.md`, `Upgrade_sistema_inventario_chatbot.md`, `tareas_opencode.md`, `instrucciones_gemini.md`, `PLAN_MONETIZACION.md` están en `.gitignore`.
- `chatbot_operations.log`, `__pycache__/`, `.env`, `inventory.db`, `app/data/facturas/` y `app/data/clientes.json` no se versionan.
- `docs/` no existe pese a aparecer en versiones antiguas del README.