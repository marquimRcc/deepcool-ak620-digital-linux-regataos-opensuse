#!/bin/bash
##############################################################################
# DESINSTALADOR - DEEPCOOL AK SERIES DIGITAL
# Para Regata OS / openSUSE
##############################################################################

R='\033[0;31m'
G='\033[0;32m'
Y='\033[1;33m'
C='\033[0;36m'
N='\033[0m'

APP_NAME="deepcool-digital"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
AUTOSTART_DIR="$HOME/.config/autostart"

echo -e "${Y}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════╗
║   DESINSTALADOR - DeepCool Digital                                    ║
╚═══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${N}"

echo -e "  ${C}▶${N} Encerrando aplicativo..."
pkill -f "python3.11.*$APP_NAME.*main.py" 2>/dev/null || true
pkill -f "python3.11.*deepcool-tray.py" 2>/dev/null || true
sleep 1

echo -e "  ${C}▶${N} Removendo serviços systemd antigos (se existirem)..."
sudo systemctl stop deepcool-digital.service 2>/dev/null || true
sudo systemctl disable deepcool-digital.service 2>/dev/null || true
sudo rm -f /etc/systemd/system/deepcool-digital*.service
sudo systemctl daemon-reload 2>/dev/null || true

echo -e "  ${C}▶${N} Removendo autostart..."
rm -f "$AUTOSTART_DIR/$APP_NAME.desktop"

echo -e "  ${C}▶${N} Removendo regras udev..."
sudo rm -f /etc/udev/rules.d/99-deepcool.rules
sudo udevadm control --reload-rules 2>/dev/null || true

echo -e "  ${C}▶${N} Removendo arquivos instalados..."
rm -rf "$INSTALL_DIR"

echo -e "  ${C}▶${N} Removendo lock file..."
rm -f "/tmp/$APP_NAME.lock"

echo ""
echo -e "${G}╔═══════════════════════════════════════════════════════════════════════╗${N}"
echo -e "${G}║${N}  ${G}✓ DESINSTALAÇÃO COMPLETA!${N}                                          ${G}║${N}"
echo -e "${G}╚═══════════════════════════════════════════════════════════════════════╝${N}"
echo ""
echo -e "  ${Y}Nota:${N} O repositório clonado não foi removido."
echo -e "  Para remover: ${C}rm -rf $(pwd)${N}"
echo ""
