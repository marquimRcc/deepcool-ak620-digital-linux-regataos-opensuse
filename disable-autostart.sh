#!/bin/bash
##############################################################################
# Script para desabilitar o autostart do DeepCool Digital no KDE Plasma / Linux
##############################################################################

set -e

AUTOSTART_FILE="$HOME/.config/autostart/deepcool-digital.desktop"

if [ -f "$AUTOSTART_FILE" ]; then
    rm -f "$AUTOSTART_FILE"
    if command -v systemctl &>/dev/null; then
        systemctl --user daemon-reload 2>/dev/null || true
    fi
    echo "✓ Autostart desabilitado com sucesso."
else
    echo "Autostart já não estava habilitado."
fi
