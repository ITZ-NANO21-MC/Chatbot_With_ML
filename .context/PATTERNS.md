# PATTERNS.md — Chatbot_With_ML

Guía de implementación y convenciones extraídas del código existente. Nuevo código debe seguir estas pautas.

## Estilo de Código

- **Código, nombre de variables, funciones y comentarios en español**; docstrings triple-quoted `"""..."""`.
- **Imports:** stdlib → third-party → internal, en grupos separados por líneas en blanco.
- **Rutas absolutas del paquete `app`:** `from app.services.chatbot_engine import ChatbotEngine`.
- **No imports relativos** (`from . import ...`).
- **Naming:** clases `CamelCase`, funciones `snake_case`, constantes `UPPER_SNAKE_CASE` (ver `COMMAND_START`, `STATE_MENU_PRINCIPAL`).
- **Tipos:** funciones con type hints en firmas importantes (p. ej. `Optional[Dict[str, Any]]`, `Tuple[Optional[str], float]`).

## Manejo de Errores

- Guard clauses devolviendo `None`/`False` y manejando el caso en el llamador (patrón en `inventory_service.py` y `_clasificar_con_tfidf`).
- `try/except` con registro en logger (`self.logger.error(...)`, `exc_info=True` en el handler) y respuesta amigable al usuario.
- Validación de entorno antes del arranque: `config.validate_credentials()` en `run.py`.
- Nunca propagar excepciones al usuario final: responder mensaje genérico ("⚠️ Ocurrió un error...").

## Logging

- Todo módulo obtiene su logger con `get_logger(__name__)` (`app/utils/logger.py`).
- Niveles: `info` para eventos normales, `warning` para confianza baja / búsquedas sin coincidencia, `error`/`critical` para fallos.
- Salida: `chatbot_operations.log` + stdout (configurado en `logger.py`).

## Arquitectura por Capas

```
run.py (punto de entrada / orquestador)
├── app/config.py              → variables de entorno, umbrales, rutas, validate_credentials()
├── app/handlers/              → ruteo de notificaciones (comandos, menú por estados, fallback IA)
│   └── message_handler.py     → register_handlers(bot, engine)
├── app/services/              → lógica de negocio
│   ├── chatbot_engine.py      → ChatbotEngine (TF-IDF + fuzzy fallback)
│   ├── inventory_service.py   → buscar_producto() (SQLite/CSV)
│   └── state_manager.py       → estado por usuario (dict en memoria)
├── app/utils/                 → infraestructura compartida (logger)
└── app/data/                  → knowledge_base.json, inventory.db, inventory.csv
```

## Pruebas

- Framework **pytest** (`pytest`, `pytest-mock` en `requirements.txt`).
- Comando: `pytest` desde la raíz del proyecto.
- Fixtures usadas en `tests/`: `tmp_path` (JSON temporal), `monkeypatch` + `importlib.reload` (config), `unittest.mock.MagicMock` (bot/notification/engine).
- **Integridad rota actualmente:** `tests/test_engine.py` importa `app.chatbot.engine` y `tests/test_api.py` importa `app.api.routes`; ambos módulos ya no existen (refactor `c4fb5fa`). Todo test nuevo debe importar desde `app.services.*` y `app.handlers.*`.

## Machine Learning (Motor del Chatbot)

- Carga de conocimiento: `_cargar_conocimiento()` lee `conocimiento` del JSON y expande con sinónimos (`preguntas_expandidas`), mapeando cada pregunta base y sinónimo a su respuesta.
- Entrenamiento: `TfidfVectorizer().fit_transform(preguntas_expandidas)` → `X_train`.
- Clasificación: `cosine_similarity(vector_pregunta, X_train)`; si `confianza > TFIDF_CONFIDENCE_THRESHOLD` (0.3) se responde.
- Fallback: `process.extractOne(pregunta, base_preguntas, scorer=fuzz.token_sort_ratio)`; responde si `puntuacion >= FUZZY_SCORE_THRESHOLD` (70).
- Respuesta fallback final: `"No estoy seguro de entender. ¿Podrías intentar con otras palabras?"`.
- La respuesta del usuario se normaliza con `.lower().strip()` antes de vectorizar.

## Inventario

- `buscar_producto(nombre)` despacha según `config.INVENTORY_SOURCE_TYPE` (`sqlite` | `csv`).
- SQLite: `sqlite3` (stdlib), query `SELECT nombre, precio, stock FROM productos`; búsqueda difusa con `fuzz.WRatio` y `score_cutoff=FUZZY_SCORE_THRESHOLD`.
- CSV: `csv.DictReader`, mismatch de nombre tolerado con la misma búsqueda difusa.
- Precio devuelto como `float`, stock como `int`.

## Estados de Conversación

- `state_manager.py`: dict global `_user_states` keyed por `user_id`.
- Estados: `MENU_PRINCIPAL`, `ESPERANDO_PRODUCTO_STOCK`, `ESPERANDO_PRODUCTO_PRECIO`.
- Flujo: `/start`/`hola`/`menu` → MENU_PRINCIPAL → `1`/`2` → estado de espera de producto → `buscar_producto()` → vuelta a MENU_PRINCIPAL.
- **Advertencia:** dict global sin locks; notificaciones concurrentes podrían pisarse (pendiente Fase 5).

## Notas

- **No exponer `.env`** (credenciales reales) ni `chatbot_operations.log`.
- La base de conocimiento se carga solo al iniciar `ChatbotEngine`; editar `knowledge_base.json` requiere reinicio.
- `AGENTS.md` documenta gotchas y comandos; los `.context/` complementan a `AGENTS.md`.