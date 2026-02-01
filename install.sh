#!/bin/bash
##############################################################################
# INSTALADOR - DEEPCOOL AK SERIES DIGITAL
# Para Regata OS / openSUSE (KDE Plasma)
#
# https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse
##############################################################################

set -e

R='\033[0;31m'
G='\033[0;32m'
Y='\033[1;33m'
B='\033[0;34m'
C='\033[0;36m'
W='\033[1;37m'
N='\033[0m'

ok()   { echo -e "  ${G}✓${N} $1"; }
err()  { echo -e "  ${R}✗${N} $1"; }
warn() { echo -e "  ${Y}⚠${N} $1"; }
info() { echo -e "  ${C}▶${N} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="deepcool-digital"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
AUTOSTART_DIR="$HOME/.config/autostart"

clear
echo -e "${C}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════╗
║   ____                   ____            _   ____  _       _ _       ║
║  |  _ \  ___  ___ _ __  / ___|___   ___ | | |  _ \(_) __ _(_) |_    ║
║  | | | |/ _ \/ _ \ '_ \| |   / _ \ / _ \| | | | | | |/ _` | | __|  ║
║  | |_| |  __/  __/ |_) | |__| (_) | (_) | | | |_| | | (_| | | |_   ║
║  |____/ \___|\___| .__/ \____\___/ \___/|_| |____/|_|\__, |_|\__|   ║
║                  |_|                                  |___/          ║
║                                                                      ║
║   System Tray App - Regata OS / openSUSE (KDE Plasma)               ║
║   https://github.com/marquimRcc                                      ║
╚═══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${N}"

# Verificar se não é root
if [ "$EUID" -eq 0 ]; then
    err "Não execute como root! Use seu usuário normal."
    exit 1
fi

##############################################################################
echo -e "\n${B}═══ ETAPA 1: Verificando Python 3.11 ═══${N}\n"
##############################################################################

if ! command -v python3.11 &>/dev/null; then
    warn "Python 3.11 não encontrado. Instalando..."
    sudo zypper install -y python311 python311-pip
fi
ok "Python $(python3.11 --version 2>&1 | cut -d' ' -f2)"

##############################################################################
echo -e "\n${B}═══ ETAPA 2: Instalando Dependências ═══${N}\n"
##############################################################################

# PyQt5
if ! python3.11 -c "from PyQt5.QtWidgets import QSystemTrayIcon" 2>/dev/null; then
    info "Instalando PyQt5..."
    sudo zypper install -y python311-qt5 python311-qt5-sip
fi
ok "PyQt5"

# hidapi + psutil
info "Instalando bibliotecas Python..."
python3.11 -m pip uninstall -y hid 2>/dev/null || true
python3.11 -m pip install --user --force-reinstall hidapi psutil -q

if python3.11 -c "import hid; hid.device()" 2>/dev/null; then
    ok "hidapi (biblioteca HID corrigida)"
else
    err "Falha na biblioteca HID"
    echo -e "  ${Y}Tente: python3.11 -m pip install --user --force-reinstall hidapi${N}"
    exit 1
fi
ok "psutil"

##############################################################################
echo -e "\n${B}═══ ETAPA 3: Detectando Hardware ═══${N}\n"
##############################################################################

if ! lsusb | grep -qi "3633"; then
    err "Nenhum dispositivo DeepCool encontrado!"
    echo ""
    echo -e "  ${Y}Verifique se:${N}"
    echo "    • O cooler está conectado via cabo USB interno"
    echo "    • O cabo está em um header USB 2.0 da placa-mãe"
    exit 1
fi

DEVICE_INFO=$(lsusb | grep -i "3633" | head -n1)
ok "Hardware: $DEVICE_INFO"

##############################################################################
echo -e "\n${B}═══ ETAPA 4: Configurando Permissões USB ═══${N}\n"
##############################################################################

info "Criando regras udev..."
sudo tee /etc/udev/rules.d/99-deepcool.rules > /dev/null << EOF
# DeepCool Digital - Permissões HID
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="3633", MODE="0666"
SUBSYSTEM=="usb", ATTRS{idVendor}=="3633", MODE="0666"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger
ok "Regras udev configuradas"

##############################################################################
echo -e "\n${B}═══ ETAPA 5: Instalando Aplicativo ═══${N}\n"
##############################################################################

info "Removendo serviços systemd antigos (se existirem)..."
sudo systemctl stop deepcool-digital.service 2>/dev/null || true
sudo systemctl disable deepcool-digital.service 2>/dev/null || true
sudo rm -f /etc/systemd/system/deepcool-digital*.service
sudo systemctl daemon-reload 2>/dev/null || true

info "Copiando arquivos para $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR/src"

cp "$SCRIPT_DIR/main.py"    "$INSTALL_DIR/"
cp "$SCRIPT_DIR/src/"*.py   "$INSTALL_DIR/src/"
chmod +x "$INSTALL_DIR/main.py"

ok "Aplicativo instalado em $INSTALL_DIR"

##############################################################################
echo -e "\n${B}═══ ETAPA 6: Autostart no KDE ═══${N}\n"
##############################################################################

echo -e "  ${W}Deseja iniciar automaticamente com o sistema?${N}"
echo ""
echo -e "    ${W}1)${N} Sim (recomendado)"
echo -e "    ${W}2)${N} Não"
echo ""
read -p "  Selecione [1-2] (Enter para Sim): " AUTO_CHOICE
AUTO_CHOICE=${AUTO_CHOICE:-1}

if [ "$AUTO_CHOICE" == "1" ]; then
    mkdir -p "$AUTOSTART_DIR"
    cat > "$AUTOSTART_DIR/$APP_NAME.desktop" << EOF
[Desktop Entry]
Type=Application
Name=DeepCool Digital
Comment=DeepCool AK Series Digital cooler driver
Exec=/usr/bin/python3.11 $INSTALL_DIR/main.py
Icon=deepcool-digital
Terminal=false
Categories=System;Monitor;
StartupNotify=false
X-KDE-autostart-after=panel
EOF
    ok "Autostart habilitado"
else
    rm -f "$AUTOSTART_DIR/$APP_NAME.desktop"
    info "Autostart não habilitado (pode ativar pelo menu do app)"
fi

##############################################################################
echo -e "\n${B}═══ ETAPA 7: Iniciando ═══${N}\n"
##############################################################################

info "Iniciando DeepCool Digital..."

# Matar instância anterior se existir
pkill -f "python3.11.*$APP_NAME.*main.py" 2>/dev/null || true
sleep 1

# Iniciar em background
nohup python3.11 "$INSTALL_DIR/main.py" > /dev/null 2>&1 &
sleep 2

if pgrep -f "python3.11.*main.py" > /dev/null; then
    ok "Aplicativo rodando!"
else
    warn "Não foi possível iniciar automaticamente."
    echo -e "  Execute manualmente: ${C}python3.11 $INSTALL_DIR/main.py${N}"
fi

##############################################################################
echo ""
echo -e "${G}╔═══════════════════════════════════════════════════════════════════════╗${N}"
echo -e "${G}║${N}${W}                    INSTALAÇÃO COMPLETA!                               ${G}║${N}"
echo -e "${G}╚═══════════════════════════════════════════════════════════════════════╝${N}"
echo ""
echo -e "  O ícone ${C}DeepCool Digital${N} deve aparecer na bandeja do KDE."
echo -e "  Clique com o ${W}botão direito${N} para acessar as opções."
echo ""
echo -e "${B}╔═══════════════════════════════════════════════════════════════════════╗${N}"
echo -e "${B}║${N} ${W}Comandos úteis:${N}                                                        ${B}║${N}"
echo -e "${B}╠═══════════════════════════════════════════════════════════════════════╣${N}"
echo -e "${B}║${N}  Iniciar:       ${C}python3.11 $INSTALL_DIR/main.py${N}"
echo -e "${B}║${N}  Desinstalar:   ${C}./uninstall.sh${N}"
echo -e "${B}╚═══════════════════════════════════════════════════════════════════════╝${N}"
echo ""
