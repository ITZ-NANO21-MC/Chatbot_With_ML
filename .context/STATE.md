# STATE.md — Chatbot_With_ML

## Estado Actual

- **Fase activa:** ninguna — Fase 5 (Estabilización) **completada** (módulos 5.1–5.5).
- **Módulo activo:** — (pendiente decidir siguiente fase: 6 Facturación, 7 Robustez u 8 Despliegue).
- **Última acción:** Módulos 5.4 y 5.5 completados — `state_manager.py` thread-safe (`threading.RLock` + tests multi-hilo) y `ChatbotEngine.recargar_conocimiento()` (recarga del JSON sin reinicio, test verificado). Suite: **45 passed**. REPL local verificado previamente.
- **Siguiente acción:** Commitear cierre de 5.4–5.5 y decidir en qué rama/orden seguir (Fases 6–8).
- **Bloqueos:** Ninguno. Entorno de pruebas: venv `/home/nano/Documentos/dev-env` (Python 3.12.3, pytest 9.0.2).
- **Cambios pendientes sin commitear en la rama:** `app/services/state_manager.py`, `app/services/chatbot_engine.py`, `tests/test_state_manager.py`, `tests/test_engine.py`, `.context/` (STATE/ROADMAP/plans).

## Plan Fase 5 — Estabilización y Deuda Técnica

| # | Tarea | Descripción | Estado |
| :-- | :--- | :--- | :--- |
| 5.1 | Reparar tests rotos | Actualizar imports en `tests/test_engine.py` y `tests/test_api.py`; `pytest` verde | ⬜ **Siguiente** |
| 5.2 | Limpiar mensajes obsoletos | `STOCK_MESSAGE`/`PRECIO_MESSAGE` duplican el flujo de inventario real | ⬜ Pendiente |
| 5.3 | Sincronizar README y `.env.example` | Estructura real + variables `TFIDF_THRESHOLD`, `FUZZY_THRESHOLD`, `INVENTORY_*` | ⬜ Pendiente |
| 5.4 | Concurrencia en `state_manager.py` | Proteger el dict en memoria ante notificaciones simultáneas | ⬜ Pendiente |

## Repositorio

- **Rama:** `main` (activa); existe `feature/standalone-chatbot` (local, sin trackear en remoto).
- **Remoto:** `origin` — ramas `main` y `feat/local-testing-repl`.
- **Commits recientes:** `0076f80` (chore: dejar de trackear chatbot_operations.log) → `2572455` (chore: gitignore + fixes de handler) → `0b44b14` (docs) → `b4aafb1` (feat: inventario Fase 4) → `4981dd7` (feat: menús Fase 3) → `881eee5` (feat: comandos Fase 2) → `c4fb5fa` (refactor: arquitectura modular).

## Pendiente / No trackeado (por decisión del usuario)

- `AGENTS.md`, `Upgrade_sistema_inventario_chatbot.md`, `tareas_opencode.md`, `instrucciones_gemini.md`, `PLAN_MONETIZACION.md` están en `.gitignore`.
- `PLAN_MONETIZACION.md` aparece **eliminado** en el working tree (`D` en `git status`) sin commitear.
- `chatbot_operations.log`, `__pycache__/`, `.env` y `inventory.db` no se versionan.
- `docs/` no existe pese a aparecer en el README.