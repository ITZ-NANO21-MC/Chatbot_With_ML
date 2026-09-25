# PLAN_FASE_8.md — Despliegue como Servicio

**Fecha:** 2026-09-24 · **Rama:** `feat/despliegue-servicio` (desde `main`)

---

## Contexto de decisión

| Pregunta | Decisión (con el dueño) |
| :--- | :--- |
| Plataformas de despliegue | **Ambas**: Linux (`systemd`) + Windows (tarea programada) |
| Usuario del servicio | **Usuario dedicado `chatbot`** (sin login, permisos mínimos sobre `app/data/`) |
| Manejo del `.env` | **Validar + copiar plantilla** (nunca versionar credenciales reales) |

**Objetivo:** que el bot arranque automáticamente al encender la máquina del cliente y se recupere solo ante caídas, con documentación de operación 24/7.

---

## Módulo 8.1 — Scripts de instalación y servicio

### Linux `scripts/install_linux.sh` (idempotente, bash, `set -euo pipefail`)
- [ ] Crear (si no existe) el usuario dedicado: `chatbot`, sin shell (`/usr/sbin/nologin`) y sin login, `--system --no-create-home` opcional según distro.
- [ ] Copiar el repo a un destino de producción configurable (`DEPLOY_DIR`, default `/opt/chatbot_ml`): si ya existe, `git pull` en vez de re-clonar.
- [ ] Crear venv (`python3 -m venv`) e instalar `requirements.txt` (si está desactualizado).
- [ ] **`.env`**: si no existe en destino, copiar `.env.example` y abortar con mensaje claro pidiendo completar credenciales; si existe, validar con `python -m app.config.__main__`-equivalente (`validate_credentials`). `chmod 600` sobre `.env`.
- [ ] Permisos: `chown -R chatbot:chatbot $DEPLOY_DIR/app/data` (facturas, contador, clientes, DDBB) y `chmod 640` sobre `app/data/inventory.db`/`.csv` si aplica. El resto en modo lectura/ejecución para el usuario del servicio.
- [ ] Generar unidad `systemd` `chatbot.service` (`/etc/systemd/system/chatbot.service`, requiere `sudo`):
  - `User=chatbot`, `WorkingDirectory=$DEPLOY_DIR`, `EnvironmentFile=$DEPLOY_DIR/.env` alternativo a leer config, `ExecStart=$DEPLOY_DIR/venv/bin/python run.py`,
  - `Restart=always`, `RestartSec=5`, manejo de `SIGTERM`/`StopTimeoutSec` razonable.
- [ ] `systemctl daemon-reload && systemctl enable --now chatbot` con verificación de estado (`is-active`).
- [ ] Mostrar resumen final: estado del servicio, cómo ver logs (`journalctl -u chatbot -f`), ruta del `.env`.

### Windows `scripts/install_windows.bat`
- [ ] Crear tarea **al iniciar sesión/arranque** con `schtasks` (consumir moderadamente de SYSTEM; si el cliente inicia sesión manual, usar `ONSTART` con cuenta del usuario o `ONLOGON`).
- [ ] Crear venv con `py -3.12 -m venv` (o Python instalado) e instalar `requirements.txt`.
- [ ] `.env`: copiar `.env.example` si no existe y pausar pidiendo credenciales; validar de igual forma.
- [ ] Ejecutar `run.py` con `pythonw.exe`/`start` para no bloquear consola; registrar logs en `%DEPLOY_DIR%\chatbot_operations.log` (ya lo hace el logger).
- [ ] Idempotente: si la tarea ya existe, avisar y no duplicar (o re-crear con `/F`).

### Tests / verificación (8.1)
- [ ] Verificación **con pruebas** del script Linux en un contenedor/VM o `bash -n` + dry-run en modo `--check` (no tocar la máquina real sin confirmación del dueño).
- [ ] Verificación manual documentada del flujo Windows (checklist en docs).
- [ ] Validaciones unitarias de las partes Python del script si se extraen funciones (p. ej. helper de validación del `.env`).

---

## Módulo 8.2 — Documentación de operación 24/7 (`docs/DESPLEGUE.md`)

- [ ] **Crear el directorio `docs/`** (existe en el README histórico pero nunca fue creado) con `DESPLEGUE.md`.
- [ ] **Linux**: `systemctl status chatbot`, `systemctl restart chatbot`, `journalctl -u chatbot -f`, actualización (pull + restart), ubicación de datos (facturas/contador/clientes), respaldo de `app/data`.
- [ ] **Windows**: iniciar/verificar tarea (`schtasks /query /tn chatbot`), logs, reinicio manual, actualización.
- [ ] **Seguridad/operación**: credenciales en `.env` (chmod 600), usuarios dedicados, qué NOT hacer (ejecutar `run.py` como root/administrador), política de retención mínima de facturas/logs.
- [ ] **Rollback / troubleshooting**: credenciales inválidas, puerto/red bloqueado, rotación de logs, dependencias faltantes.

---

## Cierre de Fase 8

- [ ] README actualizado (despliegue, `docs/DESPLEGUE.md`, suite de pruebas actualizada).
- [ ] `.context/` sincronizado: CONTEXT (árbol `docs/`, scripts), ROADMAP (Fase 8 ✅), STATE.
- [ ] `DECISIONS.md`: ADR-009 (servicio dedicado `systemd` con usuario `chatbot` y `.env` protegido).
- [ ] Suite completa en verde; merge `feat/despliegue-servicio` → `main` con PR #4.

---

## Criterios de aceptación

1. Ejecutar `install_linux.sh` en una máquina Linux limpia → bot arranca solo, sobrevive reinicios y cae+revive (Restart=always).
2. `install_windows.bat` crea una tarea que lanza el bot al encender (documentado).
3. El `.env` se copia desde la plantilla, se valida y queda con permisos 600; las credenciales reales no se versionan.
4. `docs/DESPLEGUE.md` permite operar 24/7 a un no-experto (estado, logs, actualización, rollback).

---

## Riesgos

- **Crear usuarios/servicios requiere privilegios**: el script pide `sudo` solo donde hace falta y avisa antes de cada paso destructivo.
- **Entorno de prueba Linux**: no hay contenedor disponible garantizado → verificación con `bash -n`, `shellcheck` si existe, y dry-run `--check`.
- **Windows**: no hay máquina Windows para testear el `.bat` → entregar checklist manual y script conservador (idempotente, con pausas y mensajes claros).