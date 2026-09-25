# DESPLEGUE.md — Operación 24/7 del Chatbot_With_ML

Guía para desplegar y operar el bot como **servicio permanente**. Al terminar la
instalación el bot arranca automáticamente al encender la máquina y se recupera
solo ante caídas.

- **Linux + systemd**: unidad `chatbot.service` bajo el usuario dedicado `chatbot`.
- **Windows**: tarea programada `ChatbotML` al iniciar sesión.

> **Antes de empezar:** necesitas las credenciales de Green-API
> (`ID_INSTANCE`, `API_TOKEN_INSTANCE`) y, si quieres `/reporte`, las de SMTP.
> El archivo `.env` **nunca se versiona**; lo crea el instalador desde `.env.example`.

---

## 1. Linux (systemd)

### 1.1 Instalar

```bash
# Desde la raíz del repositorio (copiará el código actual a /opt/chatbot_ml)
sudo bash scripts/install_linux.sh

# Alternativas:
#   sudo bash scripts/install_linux.sh --repo https://github.com/ITZ-NANO21-MC/Chatbot_With_ML.git   # clona
#   sudo bash scripts/install_linux.sh --dir /srv/chatbot                                              # otro directorio
#   bash scripts/install_linux.sh --check --yes                                                        # vista previa sin cambios
```

El instalador (idempotente):
1. Crea el usuario de sistema `chatbot` (sin login) si no existe.
2. Copia/clona el código a `/opt/chatbot_ml`.
3. Crea `venv` e instala `requirements.txt`.
4. Si falta `.env`, copia `.env.example` y **aborta** pidiendo completar
   credenciales (re-ejecuta después de editarlo). Si existe, lo valida.
5. Aplica permisos: el `.env` queda con `600`; `app/data/` (facturas, contador,
   clientes, inventario) con permisos de escritura para `chatbot`.
6. Genera `/etc/systemd/system/chatbot.service` (`Restart=always`,
   `RestartSec=5`, arranque con `multi-user.target`) y lo habilita.

### 1.2 Estado y logs

```bash
systemctl status chatbot            # estado completo
systemctl is-active chatbot         # solo activo/inactivo (para scripts)
journalctl -u chatbot -f            # logs del servicio en vivo
journalctl -u chatbot --since "1 hour ago"
```

El bot además rota sus propios logs en `/opt/chatbot_ml/chatbot_operations.log`.

### 1.3 Re-iniciar / detener / arrancar

```bash
sudo systemctl restart chatbot
sudo systemctl stop chatbot
sudo systemctl start chatbot
```

### 1.4 Actualizar el bot

```bash
cd /opt/chatbot_ml && sudo -- bash -c ' \
    su chatbot -s /bin/sh -c "cd /opt/chatbot_ml && git pull" && \
    /opt/chatbot_ml/venv/bin/python -m pip install -r requirements.txt -q && \
    systemctl restart chatbot'
```

> Al actualizar, respalda primero `app/data/` (ver 3.3). No toques `.env` (no se
> sobreescribe por `install_linux.sh`).

### 1.5 Desinstalar

```bash
sudo systemctl disable --now chatbot
sudo systemctl daemon-reload
sudo rm -f /etc/systemd/system/chatbot.service         # opcional
sudo userdel chatbot                                     # opcional
sudo rm -rf /opt/chatbot_ml                              # opcional (borra datos)
```

---

## 2. Windows (tarea programada)

### 2.1 Instalar

1. Descomprime el repositorio en un directorio estable (ej. `C:\chatbot_ml`).
2. Ejecuta `scripts\install_windows.bat` con doble clic (o clic derecho → *Ejecutar como administrador*).
3. Si no existía `.env`, el instalador lo crea y pide completar credenciales;
   vuelve a ejecutarlo después.

El instalador (idempotente):
1. Crea `venv` (`py -3 -m venv` o `python -m venv`) e instala dependencias.
2. Valida `.env` (o lo copia de `.env.example` y aborta). Lo oculta (`attrib +h`).
3. Crea la tarea programada `ChatbotML` (`schtasks /Create /F /SC ONLOGON`)
   que lanza `venv\Scripts\pythonw.exe run.py` sin ventana de consola.
4. Si la tarea ya existe, se re-crea (`/F`) sin duplicar.

### 2.2 Estado, logs, inicio manual

```bat
schtasks /Query /TN ChatbotML
schtasks /Run /TN ChatbotML
schtasks /End /TN ChatbotML
schtasks /Delete /TN ChatbotML /F
```

Logs de la aplicación en `chatbot_operations.log`, dentro del directorio de despliegue.

### 2.3 Actualizar el bot

Detén la tarea, reemplaza los archivos (o `git pull`), re-ejecuta
`install_windows.bat` (re-crea la tarea) y vuelve a lanzarla.

---

## 3. Operación y buenas prácticas

### 3.1 Credenciales

- `.env` vive solo en el servidor (`600` en Linux, oculto en Windows).
- **Nunca** lo subas al repositorio ni lo copies fuera del servidor.
- Con `INVENTORY_SOURCE_TYPE=csv` el inventario se lee de `app/data/inventory.csv`;
  con `sqlite` (default) de `app/data/inventory.db`. Edítalo con el bot detenido o
  reinícialo después.

### 3.2 Qué NO hacer

- No ejecutar `run.py` como `root`/admin permanente: usa el servicio/tarea.
- No editar `knowledge_base.json` y esperar efecto sin reiniciar el bot.
- No borrar `venv` o `app/data` sin respaldo.

### 3.3 Respaldo y retención

Respaldo recomendado (diario) — directorio:

```bash
/opt/chatbot_ml/app/data/     # facturas/, contador.json, clientes.json, inventory.*
/opt/chatbot_ml/.env          # credenciales (guárdalo cifrado)
```

Windows: copia la carpeta `app\data` y el `.env`.

> La rotación de logs conserva `LOG_BACKUP_COUNT` (default 3) respaldos de
> `LOG_MAX_BYTES` (default 5 MB) cada uno. Definir una política de retención de
> facturas/clientes es responsabilidad del negocio.

### 3.4 Solución de problemas

| Síntoma | Causa probable | Acción |
| :--- | :--- | :--- |
| `is-active` = failed | Credenciales inválidas o excepción al arrancar | `journalctl -u chatbot -n 50`; revisar `.env` |
| El bot no responde en WhatsApp | Instancia/API limitada, red | Ver logs; verificar suscripción Green-API |
| `/reporte` dice "no configurado" | Falta `SMTP_*`/`OWNER_PHONE` en `.env` | Completar `.env` y `systemctl restart chatbot` |
| No llegan recordatorios | Sin clientes en `clientes.json` | Revisar `app/data/clientes.json` |
| Redis no aplica | — | Este proyecto no usa Redis |

### 3.5 Verificación de humo tras instalar

```bash
systemctl is-active chatbot                     # → active
curl -s https://api.green-api.com/...           # con credenciales, salud de API
journalctl -u chatbot -f                        # sin excepciones al arrancar
```

Envía `/start` desde WhatsApp y verifica la respuesta del menú.

---

## 4. Arquitectura del despliegue

```
Internet ── WhatsApp/Green-API API
                │  (webhook HTTPS)
                ▼
  systemd chatbot.service / tarea ChatbotML
                ├── venv/bin/python run.py   → ChatbotEngine + GreenAPIBot
                ├── app/data/                → KB, inventario, facturas, clientes, contador
                └── chatbot_operations.log   → rotación (LOG_MAX_BYTES/LOG_BACKUP_COUNT)
```

El usuario del servicio (Linux) solo puede escribir en `/opt/chatbot_ml`
(`ProtectSystem=full`, `ReadWritePaths`, `NoNewPrivileges=true`, `PrivateTmp=true`).