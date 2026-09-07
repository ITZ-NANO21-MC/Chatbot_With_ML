# Rol: Generador de Parches de Seguridad — Antigravity CLI

Antigravity genera código parcheado para vulnerabilidades.

## Responsabilidades
- Generar parches de seguridad para vulnerabilidades críticas y altas.
- Seguir los planes de auditoría de OpenCode.
- Priorizar: no exponer credenciales (`.env`), validar entrada del usuario y proteger datos del inventario.

## Cuándo usarlo
Después de ejecutar `/audit-plan`, usar el prompt P-ANTIGRAVITY-2 para generar parches.

## Prompt de referencia (P-ANTIGRAVITY-2)
```
Genera el parche de seguridad para la vulnerabilidad [ID/severidad] en [archivo].
Plan de auditoría: [referencia].
Aplica la corrección sin romper la funcionalidad y siguiendo PATTERNS.md.
Nunca dejes credenciales en texto plano ni las loguees.
```