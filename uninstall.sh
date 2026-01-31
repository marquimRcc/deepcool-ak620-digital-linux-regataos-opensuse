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

echo -e "${Y}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════╗
║   DESINSTALADOR - DeepCool Digital                                    ║
╚═══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${N}"

echo -e "${C}▶${N} Parando serviços..."
sudo systemctl stop deepcool-digital.service 2>/dev/null || true
sudo systemctl stop deepcool-digital-restart.service 2>/dev/null || true

echo -e "${C}▶${N} Desabilitando serviços do boot..."
sudo systemctl disable deepcool-digital.service 2>/dev/null || true
sudo systemctl disable deepcool-digital-restart.service 2>/dev/null || true

echo -e "${C}▶${N} Removendo arquivos de serviço..."
sudo rm -f /etc/systemd/system/deepcool-digital.service
sudo rm -f /etc/systemd/system/deepcool-digital-restart.service

echo -e "${C}▶${N} Removendo regras udev..."
sudo rm -f /etc/udev/rules.d/99-deepcool.rules

echo -e "${C}▶${N} Recarregando systemd..."
sudo systemctl daemon-reload
sudo udevadm control --reload-rules 2>/dev/null || true

echo ""
echo -e "${G}╔═══════════════════════════════════════════════════════════════════════╗${N}"
echo -e "${G}║${N}  ${G}✓ DESINSTALAÇÃO COMPLETA!${N}                                          ${G}║${N}"
echo -e "${G}╚═══════════════════════════════════════════════════════════════════════╝${N}"
echo ""
echo -e "${Y}Nota:${N} Os arquivos do repositório não foram removidos."
echo -e "      Para remover completamente, delete a pasta do projeto:"
echo ""
echo -e "      ${C}rm -rf ~/Documentos/git/deepcool-ak620-digital-linux-regataos-opensuse${N}"
echo ""
