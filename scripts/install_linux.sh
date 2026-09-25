#!/usr/bin/env bash
# =============================================================================
# install_linux.sh — Despliega el Chatbot_With_ML como servicio systemd.
#
# Decide con el dueño (Fase 8):
#   - Ejecución bajo usuario dedicado 'chatbot' (sin login).
#   - .env validado + copiado desde .env.example; nunca se versionan credenciales.
#   - Instalación idempotente; modos: normal, --check (dry-run) y --yes.
#
# Uso:
#   sudo bash scripts/install_linux.sh [--dir /opt/chatbot_ml] [--source DIR]
#       [--repo URL] [--check | --yes]
#
# Opciones:
#   --dir PATH    Directorio de despliegue (default: /opt/chatbot_ml).
#   --source DIR  Copia el código desde DIR (default: la raíz de este repo).
#   --repo URL    Clona el repositorio remoto en el directorio de despliegue.
#   --check       Modo dry-run: solo imprime los pasos, no modifica nada.
#   --yes         Salta las confirmaciones.
# =============================================================================
set -euo pipefail

DEPLOY_DIR="/opt/chatbot_ml"
SOURCE_DIR=""
REPO_URL=""
CHECK="0"
FORCE_YES="0"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dir) DEPLOY_DIR="$2"; shift 2 ;;
        --source) SOURCE_DIR="$2"; shift 2 ;;
        --repo) REPO_URL="$2"; shift 2 ;;
        --check) CHECK="1"; shift ;;
        --yes|-y) FORCE_YES="1"; shift ;;
        *) echo "Opción desconocida: $1"; exit 2 ;;
    esac
done

SERVICE_USER="chatbot"
SERVICE_NAME="chatbot"
VENV_DIR="$DEPLOY_DIR/venv"
PYTHON_BIN="$VENV_DIR/bin/python"

log()  { printf '[install] %s\n' "$*"; }
warn() { printf '[install][AVISO] %s\n' "$*"; }
die()  { printf '[install][ERROR] %s\n' "$*" >&2; exit 1; }

# run() ejecuta los pasos o los muestra en modo --check.
run() {
    if [[ "$CHECK" == "1" ]]; then
        echo "[check] $*"
    else
        ( eval "$*" )
    fi
}

sudo_cmd() {
    if [[ "$CHECK" == "1" ]]; then
        echo "sudo $*"
    elif [[ "$(id -u)" == "0" ]]; then
        eval "$*"
    else
        eval "sudo $*"
    fi
}

confirmar() {
    if [[ "$FORCE_YES" == "1" ]]; then return 0; fi
    local respuesta
    printf '\n%s [s/N] ' "$1"
    read -r respuesta
    [[ "${respuesta,,}" == "s" || "${respuesta,,}" == "si" || "${respuesta,,}" == "sí" ]]
}

# -----------------------------------------------------------------------------
# Resumen del plan
# -----------------------------------------------------------------------------
log "Plan de instalación:"
log "  Usuario del servicio : $SERVICE_USER (sin login)"
log "  Directorio           : $DEPLOY_DIR"
log "  Unidad systemd       : $SERVICE_NAME.service (Restart=always)"
log "  .env                 : se valida; si falta se copia la plantilla y se aborta"
if [[ "$CHECK" == "1" ]]; then log "Modo: --check (dry-run, no se modifica nada)."; fi

confirmar "¿Deseas continuar con la instalación? Se creará el usuario '$SERVICE_USER' y el servicio '$SERVICE_NAME'." \
    || die "Cancelado por el usuario."

# -----------------------------------------------------------------------------
# 1) Crear el usuario dedicado (idempotente)
# -----------------------------------------------------------------------------
if id -u "$SERVICE_USER" >/dev/null 2>&1; then
    log "El usuario '$SERVICE_USER' ya existe."
else
    log "Creando usuario dedicado '$SERVICE_USER'..."
    confirmar "¿Crear el usuario de sistema '$SERVICE_USER'?" || die "Cancelado por el usuario."
    # -r sistema, -M sin home, -s nologin, -d apunta al directorio de despliegue.
    sudo_cmd "useradd --system --no-create-home --shell /usr/sbin/nologin --home-dir '$DEPLOY_DIR' '$SERVICE_USER'"
fi

# -----------------------------------------------------------------------------
# 2) Colocar el código en el directorio de despliegue (idempotente)
# -----------------------------------------------------------------------------
SCRIPT_SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$SCRIPT_SOURCE}"

if [[ -f "$DEPLOY_DIR/run.py" ]]; then
    log "El código ya está desplegado en '$DEPLOY_DIR'."
    if [[ -d "$DEPLOY_DIR/.git" ]]; then
        if confirmar "¿Actualizar desde git (git pull)?"; then
            run "git -C '$DEPLOY_DIR' pull"
        fi
    fi
elif [[ -n "$REPO_URL" ]]; then
    log "Clonando repositorio desde '$REPO_URL'..."
    run "git clone '$REPO_URL' '$DEPLOY_DIR'"
else
    log "Copiando código desde '$SOURCE_DIR'..."
    confirmar "¿Copiar el código actual a '$DEPLOY_DIR'?" || die "Cancelado por el usuario."
    run "mkdir -p '$DEPLOY_DIR'"
    if command -v rsync >/dev/null 2>&1; then
        run "rsync -a --exclude '.git/' --exclude '.env' --exclude 'venv/' --exclude '__pycache__/' --exclude '*.log*' '$SOURCE_DIR/' '$DEPLOY_DIR/'"
    else
        run "cp -a '$SOURCE_DIR/.' '$DEPLOY_DIR/'"
    fi
fi

# -----------------------------------------------------------------------------
# 3) Entorno virtual e instalación de dependencias
# -----------------------------------------------------------------------------
if [[ ! -x "$PYTHON_BIN" ]]; then
    log "Creando entorno virtual en '$VENV_DIR'..."
    run "python3 -m venv '$VENV_DIR'"
fi
log "Instalando/verificando dependencias (requirements.txt)..."
run "'$PYTHON_BIN' -m pip install --upgrade pip -q"
run "'$PYTHON_BIN' -m pip install -r '$DEPLOY_DIR/requirements.txt' -q"

# -----------------------------------------------------------------------------
# 4) .env: validar o copiar la plantilla (nunca se versionan credenciales)
# -----------------------------------------------------------------------------
if [[ ! -f "$DEPLOY_DIR/.env" ]]; then
    if [[ -f "$DEPLOY_DIR/.env.example" ]]; then
        warn "No existe '$DEPLOY_DIR/.env' — copiando la plantilla desde .env.example."
        run "cp '$DEPLOY_DIR/.env.example' '$DEPLOY_DIR/.env'"
    fi
    die "Completa las credenciales en '$DEPLOY_DIR/.env' (Green-API y, si aplica, SMTP) y vuelve a ejecutar este script."
fi
log "Validando credenciales del .env..."
if [[ "$CHECK" == "1" ]]; then
    echo "[check] $PYTHON_BIN -c 'from app import config; config.validate_credentials()' (en $DEPLOY_DIR)"
else
    ( cd "$DEPLOY_DIR" && "$PYTHON_BIN" -c "from app import config; config.validate_credentials()" ) \
        || die "La validación del .env falló. Revisa ID_INSTANCE/API_TOKEN_INSTANCE."
fi
run "chmod 600 '$DEPLOY_DIR/.env'"

# -----------------------------------------------------------------------------
# 5) Permisos: el usuario del servicio solo escribe en el árbol de despliegue
# -----------------------------------------------------------------------------
log "Ajustando propietario y permisos..."
run "chown -R '$SERVICE_USER:$SERVICE_USER' '$DEPLOY_DIR'"
run "chmod 600 '$DEPLOY_DIR/.env'"
if [[ -f "$DEPLOY_DIR/app/data/inventory.db" ]]; then
    run "chmod 660 '$DEPLOY_DIR/app/data/inventory.db'"
fi
if [[ -f "$DEPLOY_DIR/app/data/inventory.csv" ]]; then
    run "chmod 660 '$DEPLOY_DIR/app/data/inventory.csv'"
fi

# -----------------------------------------------------------------------------
# 6) Unidad systemd (idempotente; regenera el archivo con la config actual)
# -----------------------------------------------------------------------------
log "Generando unidad '$SERVICE_NAME.service'..."
UNIT="/etc/systemd/system/$SERVICE_NAME.service"
UNIT_FILE="$(
cat <<EOF
[Unit]
Description=Chatbot WhatsApp con ML (Green-API)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$DEPLOY_DIR
EnvironmentFile=$DEPLOY_DIR/.env
ExecStart=$PYTHON_BIN run.py
Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ReadWritePaths=$DEPLOY_DIR
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
)"
if [[ "$CHECK" == "1" ]]; then
    echo "[check] Escribir unidad systemd en $UNIT:"
    echo "$UNIT_FILE" | sed 's/^/        /'
else
    echo "$UNIT_FILE" | sudo tee "$UNIT" >/dev/null
fi

log "Recargando systemd y habilitando el servicio..."
run "sudo systemctl daemon-reload"
run "sudo systemctl enable --now '$SERVICE_NAME'"

# -----------------------------------------------------------------------------
# 7) Verificación y resumen de operación
# -----------------------------------------------------------------------------
if [[ "$CHECK" == "1" ]]; then
    echo "[check] sudo systemctl is-active $SERVICE_NAME"
    echo "[check] sudo journalctl -u $SERVICE_NAME -f"
else
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "Estado: ACTIVO."
    else
        systemctl --no-pager status "$SERVICE_NAME" || true
        die "El servicio no quedó activo. Revisa 'systemctl status $SERVICE_NAME'."
    fi
fi

log "Instalación completada."
echo
echo "  Estado:      systemctl status $SERVICE_NAME"
echo "  Logs:        journalctl -u $SERVICE_NAME -f"
echo "  Detener:     systemctl stop $SERVICE_NAME"
echo "  Reiniciar:   systemctl restart $SERVICE_NAME"
echo "  .env:        $DEPLOY_DIR/.env (600, no versionado)"
echo "  Datos:       $DEPLOY_DIR/app/data/ (facturas, contador, clientes)"
echo
echo "Operación 24/7: ver docs/DESPLEGUE.md."