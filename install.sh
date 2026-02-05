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

# Detectar versão do Python
PYTHON_CMD=""
for cmd in python3.12 python3.11 python3.10 python3.9 python3.8 python3; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON_VERSION=$("$cmd" --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
        MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
        
        # Verificar se é Python 3.8+
        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 8 ]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

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
echo -e "\n${B}═══ ETAPA 1: Verificando Python 3.8+ ═══${N}\n"
##############################################################################

if [ -z "$PYTHON_CMD" ]; then
    err "Python 3.8 ou superior não encontrado!"
    echo ""
    echo -e "  ${Y}Instalando Python 3...${N}"
    
    # Detectar distribuição
    if command -v zypper &>/dev/null; then
        # openSUSE/Regata OS
        sudo zypper install -y python3 python3-pip
    elif command -v apt &>/dev/null; then
        # Debian/Ubuntu
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
    elif command -v dnf &>/dev/null; then
        # Fedora
        sudo dnf install -y python3 python3-pip
    else
        err "Gerenciador de pacotes não suportado. Instale Python 3.8+ manualmente."
        exit 1
    fi
    
    # Tentar novamente
    for cmd in python3.12 python3.11 python3.10 python3.9 python3.8 python3; do
        if command -v "$cmd" &>/dev/null; then
            PYTHON_CMD="$cmd"
            break
        fi
    done
    
    if [ -z "$PYTHON_CMD" ]; then
        err "Falha ao instalar Python 3.8+. Instale manualmente."
        exit 1
    fi
fi

PYTHON_VERSION=$("$PYTHON_CMD" --version 2>&1 | cut -d' ' -f2)
ok "Python $PYTHON_VERSION ($PYTHON_CMD)"

##############################################################################
echo -e "\n${B}═══ ETAPA 2: Instalando Dependências ═══${N}\n"
##############################################################################

# Detectar distribuição para instalar PyQt5
if command -v zypper &>/dev/null; then
    # openSUSE/Regata OS
    info "Detectado: openSUSE/Regata OS"
    
    # PyQt5
    if ! "$PYTHON_CMD" -c "from PyQt5.QtWidgets import QSystemTrayIcon" 2>/dev/null; then
        info "Instalando PyQt5..."
        
        # Tentar instalar pacote específico da versão
        PYTHON_VER_SHORT=$(echo "$PYTHON_VERSION" | cut -d'.' -f1,2 | tr -d '.')
        if ! sudo zypper install -y "python${PYTHON_VER_SHORT}-qt5" 2>/dev/null; then
            # Fallback para pacote genérico
            sudo zypper install -y python3-qt5 python3-qt5-sip
        fi
    fi
    ok "PyQt5"
    
elif command -v apt &>/dev/null; then
    # Debian/Ubuntu
    info "Detectado: Debian/Ubuntu"
    
    if ! "$PYTHON_CMD" -c "from PyQt5.QtWidgets import QSystemTrayIcon" 2>/dev/null; then
        info "Instalando PyQt5..."
        sudo apt install -y python3-pyqt5
    fi
    ok "PyQt5"
    
elif command -v dnf &>/dev/null; then
    # Fedora
    info "Detectado: Fedora"
    
    if ! "$PYTHON_CMD" -c "from PyQt5.QtWidgets import QSystemTrayIcon" 2>/dev/null; then
        info "Instalando PyQt5..."
        sudo dnf install -y python3-qt5
    fi
    ok "PyQt5"
else
    warn "Distribuição não reconhecida. Tentando instalar via pip..."
fi

# Instalar dependências via pip (requirements.txt)
info "Instalando dependências Python..."

# Garantir que pip está disponível
if ! "$PYTHON_CMD" -m pip --version &>/dev/null; then
    info "Instalando pip..."
    "$PYTHON_CMD" -m ensurepip --default-pip 2>/dev/null || true
fi

# Remover conflito do pacote hid (openSUSE)
"$PYTHON_CMD" -m pip uninstall -y hid 2>/dev/null || true

# Instalar via requirements.txt
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    "$PYTHON_CMD" -m pip install --user -r "$SCRIPT_DIR/requirements.txt" -q
else
    # Fallback: instalar manualmente
    "$PYTHON_CMD" -m pip install --user hidapi psutil -q
fi

# Verificar instalação do hidapi
if "$PYTHON_CMD" -c "import hid; hid.device()" 2>/dev/null; then
    ok "hidapi (biblioteca HID corrigida)"
else
    err "Falha na biblioteca HID"
    echo -e "  ${Y}Tente: $PYTHON_CMD -m pip install --user --force-reinstall hidapi${N}"
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
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="3633", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="3633", TAG+="uaccess"
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
cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/" 2>/dev/null || true
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
Exec=$PYTHON_CMD $INSTALL_DIR/main.py
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
pkill -f "$PYTHON_CMD.*$APP_NAME.*main.py" 2>/dev/null || true
sleep 1

# Iniciar em background
nohup "$PYTHON_CMD" "$INSTALL_DIR/main.py" > /dev/null 2>&1 &
sleep 2

if pgrep -f "$PYTHON_CMD.*main.py" > /dev/null; then
    ok "Aplicativo rodando!"
else
    warn "Não foi possível iniciar automaticamente."
    echo -e "  Execute manualmente: ${C}$PYTHON_CMD $INSTALL_DIR/main.py${N}"
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
echo -e "${B}║${N}  Iniciar:       ${C}$PYTHON_CMD $INSTALL_DIR/main.py${N}"
echo -e "${B}║${N}  Desinstalar:   ${C}./uninstall.sh${N}"
echo -e "${B}║${N}  Logs:          ${C}cat ~/.config/$APP_NAME/$APP_NAME.log${N}"
echo -e "${B}╚═══════════════════════════════════════════════════════════════════════╝${N}"
echo ""
