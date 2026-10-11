#!/bin/bash
##############################################################################
# Script para configurar e habilitar o autostart do DeepCool Digital no KDE Plasma / Linux
##############################################################################

set -e

APP_NAME="deepcool-digital"
AUTOSTART_DIR="$HOME/.config/autostart"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
DESKTOP_FILE="$AUTOSTART_DIR/$APP_NAME.desktop"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Detectar interpretador Python (prioridade para venv do app)
if [ -x "$INSTALL_DIR/venv/bin/python3" ]; then
    PYTHON_BIN="$INSTALL_DIR/venv/bin/python3"
elif [ -x "$SCRIPT_DIR/venv/bin/python3" ]; then
    PYTHON_BIN="$SCRIPT_DIR/venv/bin/python3"
else
    PYTHON_BIN="$(command -v python3)"
fi

# Detectar script principal
if [ -f "$INSTALL_DIR/main.py" ]; then
    MAIN_SCRIPT="$INSTALL_DIR/main.py"
elif [ -f "$SCRIPT_DIR/main.py" ]; then
    MAIN_SCRIPT="$SCRIPT_DIR/main.py"
else
    MAIN_SCRIPT="$INSTALL_DIR/main.py"
fi

mkdir -p "$AUTOSTART_DIR"

cat > "$DESKTOP_FILE" << DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=DeepCool Digital
Comment=DeepCool AK Series Digital cooler driver
Exec=$PYTHON_BIN $MAIN_SCRIPT
Icon=deepcool-digital
Terminal=false
Categories=System;Monitor;
StartupNotify=false
X-KDE-autostart-after=panel
DESKTOP_EOF

chmod +x "$DESKTOP_FILE"

# Notificar o systemd de usuário se ativo (KDE Plasma 6)
if command -v systemctl &>/dev/null; then
    systemctl --user daemon-reload 2>/dev/null || true
fi

echo "✓ Autostart habilitado com sucesso!"
echo "  Arquivo: $DESKTOP_FILE"
echo "  Exec:    $PYTHON_BIN $MAIN_SCRIPT"
