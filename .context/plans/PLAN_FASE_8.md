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
- [x] Crear (si no existe) el usuario dedicado: `chatbot`, sin shell (`/usr/sbin/nologin`) y sin login, `--system --no-create-home` opcional según distro.
- [x] Copiar el repo a un destino de producción configurable (`DEPLOY_DIR`, default `/opt/chatbot_ml`): si ya existe, `git pull` en vez de re-clonar.
- [x] Crear venv (`python3 -m venv`) e instalar `requirements.txt` (si está desactualizado).
- [x] **`.env`**: si no existe en destino, copiar `.env.example` y abortar con mensaje claro pidiendo completar credenciales; si existe, validar con `python -c "from app import config; validate_credentials()"`. `chmod 600` sobre `.env`.
- [x] Permisos: `chown -R chatbot:chatbot $DEPLOY_DIR` (incluye `app/data`: facturas, contador, clientes, DDBB) y `chmod 660` sobre `app/data/inventory.db`/`.csv` si aplica.
- [x] Generar unidad `systemd` `chatbot.service` (`/etc/systemd/system/chatbot.service`): `User=chatbot`, `WorkingDirectory`, `EnvironmentFile`, `ExecStart=venv/bin/python run.py`, `Restart=always`, `RestartSec=5`, endurecimiento (`NoNewPrivileges`, `PrivateTmp`, `ProtectSystem=full`, `ReadWritePaths`).
- [x] `systemctl daemon-reload && systemctl enable --now chatbot` con verificación de estado (`is-active`).
- [x] Mostrar resumen final: estado del servicio, logs (`journalctl`), ruta del `.env`.

### Windows `scripts/install_windows.bat`
- [x] Crear tarea al iniciar sesión con `schtasks /Create /F /SC ONLOGON` (tarea `ChatbotML`).
- [x] Crear venv con `py -3 -m venv` (o `python`) e instalar `requirements.txt`.
- [x] `.env`: copiar `.env.example` si no existe y abortar pidiendo credenciales; validar de igual forma; ocultar con `attrib +h`.
- [x] Ejecutar `run.py` con `pythonw.exe` (sin consola); logs en `chatbot_operations.log`.
- [x] Idempotente: re-crea la tarea con `/F` si ya existe; resumen y pasos de operación.

### Verificación (8.1)
- [x] Sintaxis `bash -n` + dry-run real `scripts/install_linux.sh --check --yes` (solo imprime pasos; no modifica nada).
- [x] Windows: entregado conservador e idempotente; validación en máquina real queda como checklist en `docs/DESPLEGUE.md`.

---

## Módulo 8.2 — Documentación de operación 24/7 (`docs/DESPLEGUE.md`)

- [x] **Crear el directorio `docs/`** (existe en el README histórico pero nunca fue creado) con `DESPLEGUE.md`.
- [x] **Linux**: `systemctl status chatbot`, `systemctl restart chatbot`, `journalctl -u chatbot -f`, actualización (pull + restart), ubicación de datos (facturas/contador/clientes), respaldo de `app/data`.
- [x] **Windows**: iniciar/verificar tarea (`schtasks /Query /TN ChatbotML`), logs, reinicio manual, actualización.
- [x] **Seguridad/operación**: credenciales en `.env` (chmod 600), usuarios dedicados, qué NO hacer (ejecutar `run.py` como root/administrador), política de retención mínima de facturas/logs.
- [x] **Rollback / troubleshooting**: credenciales inválidas, puerto/red bloqueado, rotación de logs, dependencias faltantes.

---

## Cierre de Fase 8

- [x] README actualizado (despliegue, `docs/DESPLEGUE.md`, árbol con `scripts/` y `docs/`).
- [x] `.context/` sincronizado: CONTEXT (árbol `docs/`, scripts, ADR), ROADMAP (Fase 8 ✅), STATE.
- [x] `DECISIONS.md`: ADR-009 (servicio dedicado `systemd` con usuario `chatbot` y `.env` protegido).
- [x] Suite completa en verde; merge `feat/despliegue-servicio` → `main` con PR #4.

---

## Criterios de aceptación

1. ✅ Ejecutar `install_linux.sh` en una máquina Linux limpia → bot arranca solo, sobrevive reinicios y cae+revive (Restart=always). *(verificado dry-run + bash -n; despliegue real queda como rutina del dueño)*
2. ✅ `install_windows.bat` crea una tarea que lanza el bot al encender (documentado).
3. ✅ El `.env` se copia desde la plantilla, se valida y queda con permisos 600; las credenciales reales no se versionan.
4. ✅ `docs/DESPLEGUE.md` permite operar 24/7 a un no-experto (estado, logs, actualización, rollback).

---

## Riesgos

- **Crear usuarios/servicios requiere privilegios**: el script pide `sudo` solo donde hace falta y avisa antes de cada paso destructivo.
- **Entorno de prueba Linux**: no hay contenedor disponible garantizado → verificación con `bash -n`, `shellcheck` si existe, y dry-run `--check`.
- **Windows**: no hay máquina Windows para testear el `.bat` → entregar checklist manual y script conservador (idempotente, con pausas y mensajes claros).