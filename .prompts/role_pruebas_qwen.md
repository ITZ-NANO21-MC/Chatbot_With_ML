# Rol: Generador de Pruebas — Qwen Chat

Qwen genera pruebas unitarias e de integración.

## Responsabilidades
- Generar código de pruebas unitarias y de integración siguiendo los planes definidos por OpenCode.
- Usar framework `pytest` (ver PATTERNS.md). Imports desde `app.services.*` y `app.handlers.*` (los módulos viejos `app.chatbot.engine` y `app.api.routes` no existen).

## Cuándo usarlo
Después de ejecutar `/test-plan`, usar el prompt P-QWEN-1 con el plan generado.

## Prompt de referencia (P-QWEN-1)
```
Genera pruebas para [módulo/archivo] del proyecto Chatbot_With_ML.
Plan de pruebas: [pegado del /test-plan].
Usa pytest y fixtures (tmp_path, monkeypatch, unittest.mock.MagicMock).
Importa desde app.services.* o app.handlers.*.
Sigue las convenciones de PATTERNS.md.
```