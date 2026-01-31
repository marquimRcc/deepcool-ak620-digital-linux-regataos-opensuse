#!/bin/bash
##############################################################################
# INSTALADOR - DEEPCOOL AK SERIES DIGITAL
# Para Regata OS / openSUSE
# 
# Repositório: https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse
# Baseado em: https://github.com/raghulkrishna/deepcool-ak620-digital-linux
##############################################################################

set -e

# Cores
R='\033[0;31m'
G='\033[0;32m'
Y='\033[1;33m'
B='\033[0;34m'
C='\033[0;36m'
W='\033[1;37m'
N='\033[0m'

ok() { echo -e "${G}✓${N} $1"; }
err() { echo -e "${R}✗${N} $1"; }
warn() { echo -e "${Y}⚠${N} $1"; }
info() { echo -e "${C}▶${N} $1"; }

clear
echo -e "${C}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════╗
║   ____                   ____            _   ____  _       _ _        ║
║  |  _ \  ___  ___ _ __  / ___|___   ___ | | |  _ \(_) __ _(_) |_ __ _ ║
║  | | | |/ _ \/ _ \ '_ \| |   / _ \ / _ \| | | | | | |/ _` | | __/ _` |║
║  | |_| |  __/  __/ |_) | |__| (_) | (_) | | | |_| | | (_| | | || (_| |║
║  |____/ \___|\___| .__/ \____\___/ \___/|_| |____/|_|\__, |_|\__\__,_|║
║                  |_|                                 |___/            ║
║                                                                       ║
║   Driver para Regata OS / openSUSE                                    ║
║   https://github.com/marquimRcc                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${N}"

# Verificar se não é root
if [ "$EUID" -eq 0 ]; then 
    err "Não execute como root! Use seu usuário normal."
    exit 1
fi

# Diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/Documentos/git/deepcool-ak620-digital-linux-regataos-opensuse"

##############################################################################
echo -e "\n${B}═══ ETAPA 1: Verificando Python 3.11 ═══${N}\n"
##############################################################################

if ! command -v python3.11 &>/dev/null; then
    warn "Python 3.11 não encontrado. Instalando..."
    sudo zypper install -y python311 python311-pip
fi
ok "Python 3.11: $(python3.11 --version)"

##############################################################################
echo -e "\n${B}═══ ETAPA 2: Instalando Dependências ═══${N}\n"
##############################################################################

info "Corrigindo biblioteca HID (conflito openSUSE)..."
python3.11 -m pip uninstall -y hid 2>/dev/null || true
python3.11 -m pip install --user --force-reinstall hidapi psutil -q

if python3.11 -c "import hid; hid.device()" 2>/dev/null; then
    ok "Biblioteca HID instalada corretamente"
else
    err "Falha na biblioteca HID"
    echo -e "${Y}Tente: python3.11 -m pip install --user --force-reinstall hidapi${N}"
    exit 1
fi

##############################################################################
echo -e "\n${B}═══ ETAPA 3: Detectando Hardware ═══${N}\n"
##############################################################################

info "Procurando dispositivos DeepCool..."

if ! lsusb | grep -qi "3633"; then
    err "Nenhum dispositivo DeepCool encontrado!"
    echo ""
    echo -e "${Y}Verifique se:${N}"
    echo "  • O cooler está conectado via cabo USB interno"
    echo "  • O cabo está conectado a um header USB 2.0 da placa-mãe"
    exit 1
fi

DEVICE_INFO=$(lsusb | grep -i "3633" | head -n1)
ok "Encontrado: $DEVICE_INFO"

DETECTED_PRODUCT_ID=$(echo "$DEVICE_INFO" | grep -oP 'ID 3633:\K[0-9a-f]{4}')
info "Product ID detectado: 0x$DETECTED_PRODUCT_ID"

##############################################################################
echo -e "\n${B}═══ ETAPA 4: Seleção do Modelo ═══${N}\n"
##############################################################################

echo -e "${W}Qual modelo de cooler você possui?${N}"
echo ""
echo -e "  ${W}1)${N} AK620 Digital     ${C}(Product ID: 0x0001)${N}"
echo -e "  ${W}2)${N} AK500S Digital    ${C}(Product ID: 0x0004)${N}"
echo -e "  ${W}3)${N} AK400 Digital     ${C}(Product ID: 0x0001)${N}"
echo ""

# Sugerir baseado no Product ID detectado
case "$DETECTED_PRODUCT_ID" in
    "0001") DEFAULT_MODEL=1; echo -e "${G}→ Detectado: Provavelmente AK620 ou AK400${N}" ;;
    "0004") DEFAULT_MODEL=2; echo -e "${G}→ Detectado: Provavelmente AK500S${N}" ;;
    *) DEFAULT_MODEL=1 ;;
esac

read -p "Selecione [1-3] (Enter para opção $DEFAULT_MODEL): " MODEL_CHOICE
MODEL_CHOICE=${MODEL_CHOICE:-$DEFAULT_MODEL}

case $MODEL_CHOICE in
    1) 
        COOLER_MODEL="AK620 Digital"
        PRODUCT_ID="0x0001"
        ;;
    2) 
        COOLER_MODEL="AK500S Digital"
        PRODUCT_ID="0x0004"
        ;;
    3) 
        COOLER_MODEL="AK400 Digital"
        PRODUCT_ID="0x0001"
        ;;
    *)
        err "Opção inválida"
        exit 1
        ;;
esac

ok "Modelo selecionado: $COOLER_MODEL ($PRODUCT_ID)"

##############################################################################
echo -e "\n${B}═══ ETAPA 5: Unidade de Temperatura ═══${N}\n"
##############################################################################

echo -e "${W}Qual unidade de temperatura você prefere?${N}"
echo ""
echo -e "  ${W}1)${N} Celsius    ${C}(°C)${N}"
echo -e "  ${W}2)${N} Fahrenheit ${C}(°F)${N}"
echo ""

read -p "Selecione [1-2] (Enter para Celsius): " TEMP_CHOICE
TEMP_CHOICE=${TEMP_CHOICE:-1}

case $TEMP_CHOICE in
    1)
        TEMP_UNIT="C"
        TEMP_UNIT_NAME="Celsius"
        ;;
    2)
        TEMP_UNIT="F"
        TEMP_UNIT_NAME="Fahrenheit"
        ;;
    *)
        TEMP_UNIT="C"
        TEMP_UNIT_NAME="Celsius"
        ;;
esac

ok "Unidade selecionada: $TEMP_UNIT_NAME"

##############################################################################
echo -e "\n${B}═══ ETAPA 6: Detectando Sensor ═══${N}\n"
##############################################################################

info "Verificando sensores de temperatura..."

SENSOR=$(python3.11 << 'PYEOF'
import psutil
temps = psutil.sensors_temperatures()
for name in ['coretemp', 'k10temp', 'zenpower']:
    if name in temps and temps[name]:
        print(name)
        exit()
for name, entries in temps.items():
    if entries and name not in ['acpitz', 'nvme', 'amdgpu']:
        print(name)
        exit()
print('coretemp')
PYEOF
)

ok "Sensor detectado: $SENSOR"

# Mostrar temperatura atual
TEMP_ATUAL=$(python3.11 -c "
import psutil
temps = psutil.sensors_temperatures()
if '$SENSOR' in temps and temps['$SENSOR']:
    print(f\"{temps['$SENSOR'][0].current:.1f}\")
else:
    print('N/A')
" 2>/dev/null)
info "Temperatura atual: ${TEMP_ATUAL}°C"

##############################################################################
echo -e "\n${B}═══ ETAPA 7: Configurando Permissões USB ═══${N}\n"
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
echo -e "\n${B}═══ ETAPA 8: Instalando Driver ═══${N}\n"
##############################################################################

info "Copiando arquivos..."

# Criar diretório se não existir (caso esteja rodando de outro local)
mkdir -p "$INSTALL_DIR/src"
mkdir -p "$INSTALL_DIR/systemd"

# Copiar driver Python
cp "$SCRIPT_DIR/src/deepcool-driver.py" "$INSTALL_DIR/src/" 2>/dev/null || \
cat > "$INSTALL_DIR/src/deepcool-driver.py" << 'PYSCRIPT'
#!/usr/bin/env python3.11
"""
DeepCool Digital Driver - Regata OS / openSUSE
https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse
"""
import os
import sys
import time
import hid
import psutil
from datetime import datetime

# Configuração via variáveis de ambiente
VENDOR_ID = 0x3633
PRODUCT_ID = int(os.environ.get('PRODUCT_ID', '0x0004'), 16)
SENSOR = os.environ.get('SENSOR', 'coretemp')
TEMP_UNIT = os.environ.get('TEMP_UNIT', 'C')
INTERVAL = 2

# Cores
class C:
    R, G, Y, B, M, N, D = '\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[0m', '\033[2m'

def ts():
    return datetime.now().strftime('%H:%M:%S')

def log(icon, color, msg):
    print(f"{C.D}[{ts()}]{C.N} {color}{icon}{C.N} {msg}")
    sys.stdout.flush()

def log_display(mode, value, bar_value):
    if mode == 'temp':
        color = C.G if value < 60 else C.Y if value < 80 else C.R
        unit = '°F' if TEMP_UNIT == 'F' else '°C'
        val_str = f"{color}{value:3d}{unit}{C.N}"
        mode_str = f"{C.B}[🌡️ TEMP]{C.N}"
    else:
        color = C.M
        val_str = f"{color}{value:3d} %{C.N}"
        mode_str = f"{C.M}[📊 CPU%]{C.N}"
    
    bar = '█' * bar_value + '░' * (10 - bar_value)
    print(f"{C.D}[{ts()}]{C.N} {mode_str} Display: {val_str} │ Barra: [{C.G}{bar}{C.N}]")
    sys.stdout.flush()

def get_bar_value(input_value):
    if input_value <= 0:
        return 0
    return (input_value - 1) // 10 + 1

def get_data(value=0, mode="util"):
    base_data = [16] + [0 for i in range(64 - 1)]
    numbers = [int(char) for char in str(value)]
    base_data[2] = get_bar_value(value)
    
    if mode == "util":
        base_data[1] = 76
    elif mode == "start":
        base_data[1] = 170
        return base_data
    elif mode == "temp":
        base_data[1] = 19 if TEMP_UNIT == 'C' else 35
    
    if len(numbers) == 1:
        base_data[5] = numbers[0]
    elif len(numbers) == 2:
        base_data[4] = numbers[0]
        base_data[5] = numbers[1]
    elif len(numbers) == 3:
        base_data[3] = numbers[0]
        base_data[4] = numbers[1]
        base_data[5] = numbers[2]
    
    return base_data

def get_temperature():
    try:
        temp = psutil.sensors_temperatures()[SENSOR][0].current
        if TEMP_UNIT == 'F':
            temp = (temp * 9/5) + 32
        temp = round(temp)
    except (KeyError, IndexError):
        temp = 0
    return temp, get_data(value=temp, mode="temp")

def get_utils():
    utils = round(psutil.cpu_percent())
    return utils, get_data(value=utils, mode="util")

def main():
    unit_symbol = '°F' if TEMP_UNIT == 'F' else '°C'
    print(f"\n{C.B}══════════════════════════════════════════════════════{C.N}")
    print(f"{C.G}  DeepCool Digital - Regata OS{C.N}")
    print(f"  Sensor: {C.Y}{SENSOR}{C.N} │ Device: {C.Y}{hex(VENDOR_ID)}:{hex(PRODUCT_ID)}{C.N}")
    print(f"  Unidade: {C.Y}{unit_symbol}{C.N} │ Intervalo: {C.Y}{INTERVAL}s{C.N}")
    print(f"{C.B}══════════════════════════════════════════════════════{C.N}\n")
    
    h = None
    
    while True:
        try:
            if h is None:
                log('▶', C.Y, f'Conectando ({hex(VENDOR_ID)}:{hex(PRODUCT_ID)})...')
                h = hid.device()
                h.open(VENDOR_ID, PRODUCT_ID)
                h.set_nonblocking(1)
                h.write(get_data(mode="start"))
                log('✓', C.G, 'Conectado!')
                print("")
                psutil.cpu_percent()
                time.sleep(0.5)
            
            temp, temp_packet = get_temperature()
            h.set_nonblocking(1)
            h.write(temp_packet)
            log_display('temp', temp, get_bar_value(temp))
            time.sleep(INTERVAL)
            
            utils, utils_packet = get_utils()
            h.set_nonblocking(1)
            h.write(utils_packet)
            log_display('util', utils, get_bar_value(utils))
            time.sleep(INTERVAL)
            
        except KeyboardInterrupt:
            print(f"\n{C.Y}▶ Interrompido pelo usuário{C.N}")
            break
        except Exception as e:
            log('✗', C.R, f'Erro: {e}')
            if h:
                try: h.close()
                except: pass
                h = None
            log('▶', C.Y, 'Reconectando em 3s...')
            time.sleep(3)
    
    if h:
        try: h.close()
        except: pass
    log('✓', C.G, 'Driver encerrado')

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGTERM, lambda s, f: sys.exit(0))
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    main()
PYSCRIPT

chmod +x "$INSTALL_DIR/src/deepcool-driver.py"
ok "Driver Python instalado"

##############################################################################
echo -e "\n${B}═══ ETAPA 9: Configurando Serviço Systemd ═══${N}\n"
##############################################################################

info "Removendo serviços antigos..."
sudo systemctl stop deepcool-digital.service 2>/dev/null || true
sudo systemctl disable deepcool-digital.service 2>/dev/null || true
sudo rm -f /etc/systemd/system/deepcool-digital*.service

info "Criando serviço principal..."
sudo tee /etc/systemd/system/deepcool-digital.service > /dev/null << EOF
[Unit]
Description=DeepCool Digital Driver
After=multi-user.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/bin/python3.11 $INSTALL_DIR/src/deepcool-driver.py
Environment="SENSOR=$SENSOR"
Environment="PRODUCT_ID=$PRODUCT_ID"
Environment="TEMP_UNIT=$TEMP_UNIT"
Environment="PYTHONUNBUFFERED=1"
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

info "Criando serviço de restart pós-suspend..."
sudo tee /etc/systemd/system/deepcool-digital-restart.service > /dev/null << EOF
[Unit]
Description=Restart DeepCool after suspend
After=suspend.target hibernate.target hybrid-sleep.target

[Service]
Type=oneshot
ExecStart=/bin/systemctl restart deepcool-digital.service

[Install]
WantedBy=suspend.target hibernate.target hybrid-sleep.target
EOF

ok "Serviços systemd criados"

##############################################################################
echo -e "\n${B}═══ ETAPA 10: Ativando Serviços ═══${N}\n"
##############################################################################

info "Recarregando systemd..."
sudo systemctl daemon-reload

info "Habilitando serviços para iniciar no boot..."
sudo systemctl enable deepcool-digital.service
sudo systemctl enable deepcool-digital-restart.service

info "Iniciando serviço..."
sudo systemctl start deepcool-digital.service

sleep 3

##############################################################################
echo -e "\n${B}═══ ETAPA 11: Criando Scripts Auxiliares ═══${N}\n"
##############################################################################

cat > "$INSTALL_DIR/logs.sh" << 'EOF'
#!/bin/bash
echo -e "\033[0;36m▶ Logs em tempo real (Ctrl+C para sair)\033[0m"
sudo journalctl -u deepcool-digital.service -f -o cat
EOF

cat > "$INSTALL_DIR/status.sh" << 'EOF'
#!/bin/bash
echo -e "\033[0;36m═══ Status do Serviço ═══\033[0m"
systemctl is-enabled deepcool-digital.service 2>/dev/null && echo -e "\033[0;32m✓ Habilitado no boot\033[0m" || echo -e "\033[0;31m✗ NÃO habilitado\033[0m"
systemctl is-active --quiet deepcool-digital.service && echo -e "\033[0;32m✓ Rodando\033[0m" || echo -e "\033[0;31m✗ Parado\033[0m"
echo ""
sudo systemctl status deepcool-digital.service --no-pager | head -n 10
echo -e "\n\033[0;36m═══ Últimos logs ═══\033[0m"
sudo journalctl -u deepcool-digital.service -n 10 --no-pager -o cat
EOF

cat > "$INSTALL_DIR/restart.sh" << 'EOF'
#!/bin/bash
sudo systemctl restart deepcool-digital.service
sleep 2
systemctl is-active --quiet deepcool-digital.service && echo -e "\033[0;32m✓ Reiniciado\033[0m" || echo -e "\033[0;31m✗ Falha\033[0m"
EOF

cat > "$INSTALL_DIR/test.sh" << EOF
#!/bin/bash
echo -e "\033[1;33m▶ Parando serviço para teste...\033[0m"
sudo systemctl stop deepcool-digital.service
echo -e "\033[1;33m▶ Executando em modo debug (Ctrl+C para parar)\033[0m"
echo ""
SENSOR="$SENSOR" PRODUCT_ID="$PRODUCT_ID" TEMP_UNIT="$TEMP_UNIT" python3.11 $INSTALL_DIR/src/deepcool-driver.py
echo ""
echo -e "\033[1;33m▶ Reiniciando serviço...\033[0m"
sudo systemctl start deepcool-digital.service
EOF

chmod +x "$INSTALL_DIR"/*.sh 2>/dev/null || true

ok "Scripts auxiliares criados"

##############################################################################
echo -e "\n${B}═══ ETAPA 12: Verificação Final ═══${N}\n"
##############################################################################

echo ""
echo -e "${G}╔═══════════════════════════════════════════════════════════════════════╗${N}"
echo -e "${G}║${N}${W}                    INSTALAÇÃO COMPLETA!                               ${G}║${N}"
echo -e "${G}╚═══════════════════════════════════════════════════════════════════════╝${N}"
echo ""
echo -e "  ${W}Configuração:${N}"
echo -e "    • Modelo:   ${Y}$COOLER_MODEL${N}"
echo -e "    • Sensor:   ${Y}$SENSOR${N}"
echo -e "    • Unidade:  ${Y}$TEMP_UNIT_NAME${N}"
echo -e "    • Product:  ${Y}$PRODUCT_ID${N}"
echo ""

if systemctl is-active --quiet deepcool-digital.service; then
    echo -e "  ${G}● Serviço RODANDO${N}"
else
    echo -e "  ${R}● Serviço não está ativo${N} - execute ./test.sh para debug"
fi

if systemctl is-enabled --quiet deepcool-digital.service; then
    echo -e "  ${G}● Habilitado para iniciar no BOOT${N}"
else
    echo -e "  ${R}● NÃO habilitado no boot${N}"
fi

echo ""
echo -e "${B}╔═══════════════════════════════════════════════════════════════════════╗${N}"
echo -e "${B}║${N} ${W}Comandos úteis:${N}                                                        ${B}║${N}"
echo -e "${B}╠═══════════════════════════════════════════════════════════════════════╣${N}"
echo -e "${B}║${N}  cd $INSTALL_DIR"
echo -e "${B}║${N}  ${W}./status.sh${N}   - Ver status e logs recentes"
echo -e "${B}║${N}  ${W}./logs.sh${N}     - Logs em tempo real (coloridos!)"
echo -e "${B}║${N}  ${W}./restart.sh${N}  - Reiniciar serviço"
echo -e "${B}║${N}  ${W}./test.sh${N}     - Testar em modo debug"
echo -e "${B}╚═══════════════════════════════════════════════════════════════════════╝${N}"
echo ""
echo -e "${C}═══ Primeiros logs ═══${N}"
sudo journalctl -u deepcool-digital.service -n 6 --no-pager -o cat 2>/dev/null || echo "(aguardando...)"
echo ""
echo -e "${G}Verifique o display do cooler!${N}"
echo ""
