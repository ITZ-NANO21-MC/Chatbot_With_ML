# Rol: Refactorizador / Optimizador — Gemini Chat

Gemini aplica SOLID, separación de capas y mejora legibilidad/estructura.

## Responsabilidades
- Aplicar principios SOLID.
- Separar capas (handlers, services, utils).
- Mejorar legibilidad y estructura del código.
- Aplicar patrones de diseño.
- No romper los imports ya establecidos (`app.services.*`, `app.handlers.*`, `app.utils.*`, `app.config`).

## Cuándo usarlo
Después de integrar el código, usar el prompt P-GEMINI-1 para aplicar SOLID.

## Prompt de referencia (P-GEMINI-1)
```
Refactoriza [archivo/módulo] aplicando principios SOLID.
Mantén el comportamiento funcional sin cambios.
Respeta las convenciones de PATTERNS.md (código y comentarios en español, logging centralizado).
```