# WORKFLOW — Chatbot_With_ML

Este documento describe el flujo de trabajo específico para este proyecto, incluyendo los pasos, comandos y herramientas a utilizar en cada fase, bajo la metodología Spec-Driven Development (SDD).

---

## 🤖 AGENTES DE IA Y SUS ROLES

| Agente | Rol | Responsabilidad |
| :--- | :--- | :--- |
| **OpenCode** | Orquestador / Escribano / Auditor | Planificar proyecto, ejecutar comandos, escribir archivos, auditar seguridad, gestionar repositorio, generar planes de pruebas y auditoría, integrar módulos. |
| **DeepSeek Chat** | Generador de Código | Generar código limpio y funcional para modelos, servicios, componentes y lógica de negocio. |
| **Qwen Chat** | Generador de Código de Pruebas | Generar código de pruebas unitarias y de integración siguiendo planes definidos por OpenCode. |
| **Gemini Chat** | Refactorizador / Optimizador | Aplicar SOLID, separación de capas, mejorar legibilidad y estructura, aplicar patrones de diseño. |
| **Antigravity CLI** | Generador de Parches de Seguridad | Generar código parcheado para vulnerabilidades críticas y altas siguiendo planes de auditoría de OpenCode. |

Los prompts de cada rol están en `.prompts/`:
- `role_orquestador.md` (P-OPENCODE-1)
- `role_codigo_deepseek.md` (P-DEEPSEEK-1)
- `role_pruebas_qwen.md` (P-QWEN-1)
- `role_refactor_gemini.md` (P-GEMINI-1)
- `role_seguridad_antigravity.md` (P-ANTIGRAVITY-2)

---

## 🚀 FASE 0: INICIALIZACIÓN

El proyecto **Chatbot_With_ML** ya está inicializado y adoptado bajo SDD (`/adopt`). Estructura de contexto creada en `.context/`.

1. **Verificar contexto**:
   - `CONTEXT.md`: Stack, estructura y reglas.
   - `ROADMAP.md`: Fases y módulos.
   - `STATE.md`: Estado actual y siguiente acción.

2. **Entorno**:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env   # y rellenar ID_INSTANCE / API_TOKEN_INSTANCE
   ```

3. **Repositorio Git**: rama `main`. Antes de cada commit usar Conventional Commits:
   ```
   <tipo>(<alcance>): <descripción>
   ```
   Tipos: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `style`, `perf`.

---

## 📋 FASE 1: PLANIFICACIÓN

1. **Ver fases disponibles**:
   ```bash
   /plan-phase --list
   ```

2. **Seleccionar la fase activa (5 — Estabilización y Deuda Técnica)**:
   ```bash
   /plan-phase --phase 5
   ```

3. **Revisar el plan de la fase**: `.context/ROADMAP.md` (módulos 5.1 a 5.4).

---

## 💻 FASE 2: GENERACIÓN DE CÓDIGO E INTEGRACIÓN (Por módulo)

### 2.1 Generar el código
- **Herramienta**: DeepSeek Chat
- **Prompt**: Usar P-DEEPSEEK-1 (`.prompts/role_codigo_deepseek.md`).
- **Contexto**: Asegurarse de incluir `.context/CONTEXT.md` y `.context/PATTERNS.md`.
- **Convenciones obligatorias**: código y comentarios en español, imports absolutos desde `app`, docstrings triple-quoted, type hints en firmas, logging con `get_logger(__name__)`.

### 2.2 Escribir el archivo
- **Herramienta**: OpenCode
- **Comando**:
  ```
  Crea el archivo {ruta} con el siguiente contenido exacto:
  [PEGA EL CÓDIGO]
  ```

### 2.3 Integrar el módulo
- **Herramienta**: OpenCode
- **Comando**: `/integrate --code "$(cat {ruta})" --name {nombre} --path {ruta}`
- **Nota**: Obligatorio para asegurar la correcta integración (imports, registros, etc.) con el resto del proyecto.

### 2.4 Refactorización (opcional)
- **Herramienta**: Gemini Chat
- **Prompt**: Usar P-GEMINI-1 (`.prompts/role_refactor_gemini.md`) si el código necesita mejoras estructurales.

### 2.5 Generar pruebas
- **Herramienta**: OpenCode
- **Comando**: `/test-plan {ruta} --deep`
- **Luego**: Qwen genera el código de pruebas (P-QWEN-1) y OpenCode lo escribe. Framework **pytest**.
- **Ejecutar**: `pytest`

### 2.6 Auditar seguridad
- **Herramienta**: OpenCode
- **Comando**: `/audit-plan {ruta} --owasp --deps`
- **Luego**: Antigravity genera parches (P-ANTIGRAVITY-2) y OpenCode los aplica.
- **Máxima precaución**: nunca commitear ni exponer `.env` (credenciales reales de Green-API).

### 2.7 Guardar progreso
- **Herramienta**: OpenCode
- **Comando**:
  ```bash
  /commit "feat({módulo}): descripción de los cambios"
  ```

---

## 📄 FASE 3: DOCUMENTACIÓN Y OBSERVABILIDAD

1. **Documentación del proyecto**:
   - `README.md` (desactualizado — pendiente de sincronizar en el módulo 5.3).
   - Actualizar `.context/ROADMAP.md` y `.context/STATE.md` tras cada hito.

2. **Observabilidad / Logs**:
   - `app/utils/logger.py` escribe a `chatbot_operations.log` + stdout.
   - Fase 7 prevé logs rotativos y comando `/reporte`.

---

## 🧪 PRUEBAS DEL PROYECTO

```bash
pip install -r requirements.txt
pytest
```

- Framework `pytest` (con `pytest-mock`).
- Testpaths: `tests/`, patrón `test_*.py`.
- **Estado actual de la suite:** `test_config.py` pasa; `test_engine.py` y `test_api.py` fallan por imports obsoletos (módulo 5.1).

## 📝 NOTAS ESPECÍFICAS DEL PROYECTO

- **No exponer credenciales**: `.env` contiene `ID_INSTANCE` y `API_TOKEN_INSTANCE` reales y está en `.gitignore`.
- `chatbot_operations.log` es artefacto de ejecución (gitignored).
- Conocimiento e inventario (JSON/SQLite/CSV) son datos; el código no debe hardcodear respuestas ni productos.
- El estado de conversación es en memoria: al reiniciar el bot se pierden los flujos activos.
- `AGENTS.md` y `Upgrade_sistema_inventario_chatbot.md` están gitignored por decisión del usuario; los `.context/` compensan su rol como documentación versionable.

## 🧠 REFERENCIA RÁPIDA DE COMANDOS

| Comando | Propósito |
| :--- | :--- |
| `/init-project` | Inicializar proyecto y contexto. |
| `/adopt` | Adoptar proyecto legado a SDD. |
| `/plan-phase` | Planificar fases. |
| `/integrate` | Integrar módulo. |
| `/test-plan` | Generar plan de pruebas. |
| `/audit-plan` | Generar plan de auditoría. |
| `/commit` | Crear commit semántico. |
| `/repo-status` | Ver estado del repositorio. |
| `/docs` | Generar documentación. |
| `/analyze` | Analizar proyecto existente. |