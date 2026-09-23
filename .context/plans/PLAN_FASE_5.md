# PLAN FASE 5 — Estabilización y Deuda Técnica

**Rama objetivo:** `feat/local-testing-repl` (deriva de `main`, contiene refactor a `message_processor` en `02c1bbf`)
**Objetivo:** dejar el proyecto con tests verdes, mensajes coherentes y documentación/código alineados antes de añadir funcionalidad nueva (Fases 6–8).
**Prerequisito de entorno:** `pip install -r requirements.txt` (incluye pytest, pytest-mock) para ejecutar la suite.

---

## Módulo 5.1 — Reparar tests rotos ✅ (parcialmente completo)

**Estado en esta rama:**
- ✅ Hecho en `02c1bbf`: `tests/test_api.py` reemplazado por `tests/test_handlers.py` + `tests/test_message_processor.py` (43 pruebas).
- ❌ Pendiente: `tests/test_engine.py:11` sigue importando `from app.chatbot.engine import ChatbotEngine` (módulo inexistente desde el refactor `c4fb5fa`).

**Tareas:**
- [ ] Corregir import: `from app.services.chatbot_engine import ChatbotEngine`.
- [ ] Verificar resto de fixtures/assericones de `test_engine.py` contra el `ChatbotEngine` real (carga de conocimiento, expansión de sinónimos, TF-IDF, fuzzy, fallback).
- [ ] Ejecutar `pytest` hasta tener la suite verde.

**Criterio de aceptación:** `pytest` pasa al 100% (test_engine + test_handlers + test_message_processor + test_config).

---

## Módulo 5.2 — Limpiar mensajes obsoletos

**Problema:** en `app/services/message_processor.py`, las constantes `STOCK_MESSAGE` y `PRECIO_MESSAGE` (líneas 35-37) dicen *"¡Próximamente estará integrado con nuestro inventario!"*, pero el flujo de menú **ya** consulta el inventario real (`inventory_service.buscar_producto`). Los comandos directos `/stock` y `/precio` (líneas 144-150) son incoherentes con el menú.

**Tareas:**
- [ ] Decidir comportamiento coherente de `/stock` y `/precio` (recomendado: pedir el nombre del producto igual que el flujo de menú, reutilizando los estados `ESPERANDO_PRODUCTO_*`).
- [ ] Actualizar las constantes y su uso; eliminar o reemplazar `STOCK_MESSAGE`/`PRECIO_MESSAGE` si dejan de usarse.
- [ ] Actualizar las pruebas que asercionan esas constantes (`tests/test_message_processor.py:20-21,164-174`).

**Criterio de aceptación:** `/stock` y `/precio` responden con información real del inventario; no hay textos "Próximamente" para funcionalidad ya existente; suite verde.

---

## Módulo 5.3 — Sincronizar README y .env.example

**Problema:** el `README.md` describe una estructura antigua (`app/api/routes.py`, `app/chatbot/engine.py`, `docs/`) y el `.env.example` no documenta los umbrales ni la configuración de inventario que sí lee `app/config.py`.

**Tareas:**
- [ ] Verificar que `.env.example` liste todas las variables leídas por `app/config.py`:
      `ID_INSTANCE`, `API_TOKEN_INSTANCE`, `KNOWLEDGE_BASE_PATH`, `LOG_FILE_PATH`, `TFIDF_THRESHOLD`, `FUZZY_THRESHOLD`, `INVENTORY_SOURCE_TYPE`, `INVENTORY_SQLITE_PATH`, `INVENTORY_CSV_PATH`.
- [ ] Actualizar `README.md`: estructura real (`handlers/services/utils`, `scripts/repl_local.py`), estado de tests, y sección de config/umbrales.
- [ ] (Solo `main` no lo necesita aquí) Ajustar `CONTEXT.md`/`ROADMAP.md` si cambian los módulos del plan.

**Criterio de aceptación:** `.env.example` cubre todas las vars del config; README refleja la estructura y suite real.

---

## Módulo 5.4 — Concurrencia en `state_manager.py`

**Problema:** el dict global `_user_states` (`app/services/state_manager.py:7`) se lee/escribe sin proteger; con notificaciones Green-API concurrentes (mismo o distinto usuario) puede haber lecturas/escrituras entremezcladas.

**Tareas:**
- [ ] Añadir un `threading.RLock` y envolver `get_state`/`set_state`/`clear_state` (la limpieza del dict interno, p. ej. iteraciones si se añaden, también bajo lock).
- [ ] Decidir si conviene un límite de tamaño / TTL (crecimiento incontrolado del dict). Documentar como mejora opcional.
- [ ] Añadir test que ejercite estado multi-usuario bajo concurrencia (hilos) o, al mínimo, un test que verifique atomicidad en operaciones.

**Criterio de aceptación:** operaciones del state_manager thread-safe; suite verde.

---

## Módulo 5.5 — Manejo de edición de `knowledge_base.json`

**Problema:** el conocimiento se carga solo en `ChatbotEngine.__init__`; editar el JSON obliga a reiniciar el proceso.

**Tareas:**
- [ ] Decidir enfoque mínimo: (a) documentar el reinicio (aceptado por ahora) o (b) exponer un método `recargar_conocimiento()` en `ChatbotEngine` con reconversión del vectorizador.
- [ ] Enfoque (b): añadir test de recarga (cambiar JSON + recargar + verificar nueva respuesta).

**Criterio de aceptación:** comportamiento documentado o recarga funcional probada.

---

## Dependencias y orden

1. **5.1 primero** — sin suite verde no se puede validar el resto.
2. **5.2** — cambios de comportamiento; requiere 5.1 para regresión rápida.
3. **5.3** — solo documentación; independiente.
4. **5.4 y 5.5** — independientes; pueden ir en paralelo tras 5.1.

## Archivos afectados

- `tests/test_engine.py` (5.1)
- `app/services/message_processor.py` + `tests/test_message_processor.py` (5.2)
- `.env.example`, `README.md` (5.3)
- `app/services/state_manager.py` + tests nuevos (5.4)
- `app/services/chatbot_engine.py` + tests (5.5)