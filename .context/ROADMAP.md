# ROADMAP.md — Chatbot_With_ML

## Progreso General

| Fase | Estado | Descripción |
| :--- | :--- | :--- |
| Fase 1 | ✅ Completada | Arquitectura modular: `app/handlers`, `app/services`, `app/utils`, `config.py`, logging centralizado (refactor `c4fb5fa`). |
| Fase 2 | ✅ Completada | Comandos básicos `/stock`, `/precio`, `/contacto`, `/horario` (commit `881eee5`). |
| Fase 3 | ✅ Completada | Conversación con menús y gestión de estado por usuario (commit `4981dd7`). |
| Fase 4 | ✅ Completada | Inventario multi-fuente SQLite/CSV (commit `b4aafb1`). |
| Fase 5 | 🚧 **En curso** | Estabilización y deuda técnica (tests rotos, mensajes obsoletos, docs). |
| Fase 6 | ⬜ Pendiente | Facturación y mensajes programados. |
| Fase 7 | ⬜ Pendiente | Robustez, logs rotativos y reportes. |
| Fase 8 | ⬜ Pendiente | Despliegue como servicio (systemd). |

---

## Fase 5 — Estabilización y Deuda Técnica (en curso)

**Objetivo:** Dejar el proyecto con tests verdes y documentación alineada al código real antes de añadir funcionalidad nueva. Es prerequisito para Fases 6–8.

### Módulos
- [ ] **Reparar tests rotos** — `tests/test_engine.py` ➜ `from app.services.chatbot_engine import ChatbotEngine`; `tests/test_api.py` ➜ `from app.handlers.message_handler import register_handlers`. Verificar `pytest` verde.
- [ ] **Limpiar mensajes obsoletos** — `STOCK_MESSAGE`/`PRECIO_MESSAGE` en `message_handler.py` dicen "Próximamente", pero el menú ya integra inventario real. Unificar respuestas.
- [ ] **Sincronizar README y .env.example** — estructura real (`handlers/services/utils`), variables `TFIDF_THRESHOLD`, `FUZZY_THRESHOLD`, `INVENTORY_SOURCE_TYPE`, `INVENTORY_*`, y estado de los tests.
- [ ] **Concurrencia en `state_manager.py`** — el dict global en memoria no tiene protección para múltiples notificaciones simultáneas.
- [ ] **Manejo de edición de `knowledge_base.json`** — documentar/automatizar recarga sin reinicio o dejar claro el reinicio.

### Dependencias
- Tests reparados ✅ (bloqueo principal: nada ejecutará `pytest` hasta arreglar los imports).

---

## Fase 6 — Facturación y Mensajes Programados (pendiente)

**Objetivo:** Comando `/factura` que genere un PDF (reportlab) y job diario de recordatorios/recibos a usuarios activos. *(Referencia: Fase 5 del plan original.)*

### Módulos
- [ ] `app/services/invoice_service.py` — generación de PDF.
- [ ] Comando `/factura` en `message_handler.py` con envío de documento por WhatsApp.
- [ ] Job diario de recordatorios a usuarios activos.

### Dependencias
- Fase 5 completada (tests verdes, base estable).

---

## Fase 7 — Robustez y Observabilidad (pendiente)

**Objetivo:** Reintentos ante errores de red en la API, logs rotativos y comando `/reporte` para el dueño. *(Referencia: Fase 6 del plan original.)*

### Módulos
- [ ] Captura de excepciones de la API de WhatsApp con reintento.
- [ ] Logs de conversaciones en archivo rotativo (`RotatingFileHandler`).
- [ ] Comando `/reporte` que envíe los logs por email al dueño.

### Dependencias
- Fase 5 completada.

---

## Fase 8 — Despliegue como Servicio (pendiente)

**Objetivo:** El bot arranca automáticamente al encender la máquina del cliente. *(Referencia: Fase 7 del plan original.)*

### Módulos
- [ ] `install.sh` que configure `systemd` (Linux) o tarea programada (Windows).
- [ ] Documentación de operación 24/7 (`systemctl status chatbot`).

### Dependencias
- Fases 6–7 completadas (funcionalidad estabilizada).

---

## Fases Completadas (referencia)

### Fase 4 — Inventario Multi-Fuente (completada)
- `app/services/inventory_service.py` con `buscar_producto()` y arquitectura SQLite/CSV vía `INVENTORY_SOURCE_TYPE`.
- Búsqueda difusa con RapidFuzz `WRatio` y `score_cutoff=70`.
- Datos de ejemplo: `app/data/inventory.db`, `app/data/inventory.csv`.

### Fase 3 — Conversación con Menús (completada)
- `app/services/state_manager.py` con 3 estados (`MENU_PRINCIPAL`, `ESPERANDO_PRODUCTO_STOCK`, `ESPERANDO_PRODUCTO_PRECIO`).
- Menú numérico (1 stock, 2 precio, 3 contacto/horario, 4 IA).

### Fase 2 — Comandos Básicos (completada)
- Comandos `/start`, `/ayuda`, `/stock`, `/precio`, `/contacto`, `/horario` con respuestas estáticas.

### Fase 1 — Arquitectura Modular (completada)
- Separación en `handlers/`, `services/`, `utils/` tras refactor `c4fb5fa`.
- `app/config.py` con variable de entorno y `validate_credentials()`.
- `app/utils/logger.py` con logging centralizado.