# Rol: Generador de Código — DeepSeek Chat

DeepSeek generará código limpio y funcional.

## Responsabilidades
- Generar código para servicios, componentes y lógica de negocio.
- Seguir las convenciones de estilo de PATTERNS.md (código y comentarios en español, imports absolutos desde `app`, docstrings triple-quoted, type hints).

## Cuándo usarlo
Después de seleccionar una fase con `/plan-phase`, usar el prompt P-DEEPSEEK-1 para generar cada archivo del módulo.

## Prompt de referencia (P-DEEPSEEK-1)
```
Genera el archivo [ruta/archivo.py] del módulo [módulo] de la Fase [N].
Requisitos funcionales: [descripción].
Sigue la metodología SDD y las convenciones de PATTERNS.md.
Añade type hints en firmas y docstrings.
No añadas imports relativos.
Usa logging con get_logger(__name__).
```