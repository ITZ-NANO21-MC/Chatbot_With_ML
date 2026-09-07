# STATE.md — Chatbot_With_ML

## Estado Actual

- **Fase activa:** Fase 5 — Estabilización y Deuda Técnica.
- **Módulo activo:** Reparación de tests rotos (imports a módulos inexistentes).
- **Última acción:** Adopción del proyecto legado a Spec-Driven Development (`/adopt`): creación de `.context/` (CONTEXT.md, ROADMAP.md, STATE.md, DECISIONS.md, PATTERNS.md, WORKFLOW.md) y `.prompts/` con roles estándar.
- **Siguiente acción:** Módulo 5.1 — Actualizar imports en `tests/test_engine.py` (`app.chatbot.engine` ➜ `app.services.chatbot_engine`) y `tests/test_api.py` (`app.api.routes` ➜ `app.handlers.message_handler`), y ejecutar `pytest` hasta dejarlo verde.
- **Bloqueos:** Ninguno conocido. Nota: requiere dependencias instaladas (`pip install -r requirements.txt`) y `pytest` para ejecutar la suite.

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