# Guia de Instalação - DeepCool AK Series Digital v1.2.0

## Novidades desta Versão

Esta versão traz melhorias significativas em relação à versão anterior, focando em **robustez**, **portabilidade** e **facilidade de diagnóstico**. As principais mudanças incluem um tratamento de exceções mais específico e informativo, um arquivo `requirements.txt` para gerenciamento padronizado de dependências, e a generalização da versão do Python para suportar desde o Python 3.8 até as versões mais recentes.

Além disso, foi implementado um sistema de logging estruturado que facilita enormemente o diagnóstico de problemas. Todos os eventos importantes são registrados em um arquivo de log, permitindo que tanto usuários quanto desenvolvedores identifiquem rapidamente a causa de qualquer comportamento inesperado.

---

## Requisitos do Sistema

O aplicativo foi projetado para funcionar em sistemas Linux com ambiente de desktop KDE Plasma. Os requisitos específicos são:

- **Sistema Operacional:** Regata OS, openSUSE (Tumbleweed/Leap), Debian, Ubuntu ou Fedora
- **Ambiente Desktop:** KDE Plasma (recomendado)
- **Python:** Versão 3.8 ou superior
- **Hardware:** Cooler DeepCool da série AK Digital conectado via USB

### Modelos de Cooler Suportados

| Modelo | Product ID | Status de Teste |
|--------|------------|-----------------|
| AK620 Digital | 0x0001, 0x0002 | ✅ Testado |
| AK500 Digital | 0x0003 | ✅ Suportado |
| AK500S Digital | 0x0004 | ✅ Testado |
| AK400 Digital | 0x0005 | ✅ Suportado |
| AG400 Digital | 0x0008 | ✅ Suportado |

---

## Instalação Automática

A forma mais simples de instalar o aplicativo é usando o script de instalação automatizado. Este script detecta automaticamente sua distribuição Linux, instala as dependências necessárias e configura o aplicativo para iniciar automaticamente com o sistema.

### Passo a Passo

Abra um terminal e execute os seguintes comandos:

```bash
# Clonar o repositório
git clone https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse.git

# Entrar no diretório
cd deepcool-ak620-digital-linux-regataos-opensuse

# Tornar o instalador executável
chmod +x install.sh

# Executar o instalador
./install.sh
```

O instalador irá realizar as seguintes operações:

1. **Verificar a versão do Python** instalada (3.8 ou superior)
2. **Instalar dependências** do sistema (PyQt5, hidapi, psutil)
3. **Detectar o hardware** DeepCool conectado
4. **Configurar permissões USB** via regras udev
5. **Instalar o aplicativo** em `~/.local/share/deepcool-digital`
6. **Configurar autostart** (opcional, você será perguntado)
7. **Iniciar o aplicativo** automaticamente

Após a instalação bem-sucedida, o ícone do DeepCool Digital aparecerá na bandeja do sistema do KDE Plasma.

---

## Instalação Manual (Avançado)

Se você preferir ter mais controle sobre o processo de instalação, ou se estiver usando uma distribuição não suportada pelo instalador automático, pode realizar a instalação manualmente.

### 1. Instalar Python e Dependências

```bash
# Para openSUSE/Regata OS
sudo zypper install python3 python3-pip python3-qt5

# Para Debian/Ubuntu
sudo apt install python3 python3-pip python3-pyqt5

# Para Fedora
sudo dnf install python3 python3-pip python3-qt5
```

### 2. Instalar Bibliotecas Python

```bash
# Remover conflito do pacote hid (se existir)
python3 -m pip uninstall -y hid

# Instalar dependências via requirements.txt
python3 -m pip install --user -r requirements.txt
```

### 3. Configurar Permissões USB

Crie o arquivo de regras udev:

```bash
sudo tee /etc/udev/rules.d/99-deepcool.rules > /dev/null << EOF
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="3633", TAG+="uaccess"
SUBSYSTEM=="usb", ATTRS{idVendor}=="3633", TAG+="uaccess"
EOF

# Recarregar regras
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 4. Executar o Aplicativo

```bash
python3 main.py
```

---

## Configuração de Autostart

Se você deseja que o aplicativo inicie automaticamente com o sistema, crie um arquivo `.desktop` no diretório de autostart do KDE:

```bash
mkdir -p ~/.config/autostart

cat > ~/.config/autostart/deepcool-digital.desktop << EOF
[Desktop Entry]
Type=Application
Name=DeepCool Digital
Comment=DeepCool AK Series Digital cooler driver
Exec=python3 $HOME/.local/share/deepcool-digital/main.py
Icon=deepcool-digital
Terminal=false
Categories=System;Monitor;
StartupNotify=false
X-KDE-autostart-after=panel
EOF
```

Alternativamente, você pode ativar/desativar o autostart diretamente pelo menu do aplicativo (clique direito no ícone da bandeja).

---

## Verificação da Instalação

Para verificar se a instalação foi bem-sucedida, execute os seguintes comandos:

### Verificar se o dispositivo está conectado

```bash
lsusb | grep 3633
```

Você deve ver uma linha similar a:
```
Bus 001 Device 002: ID 3633:0004 ...
```

### Verificar se o aplicativo está rodando

```bash
pgrep -f "python.*deepcool.*main.py"
```

Se retornar um número (PID), o aplicativo está rodando.

### Verificar logs

```bash
cat ~/.config/deepcool-digital/deepcool-digital.log
```

Os logs devem mostrar mensagens de inicialização e detecção de hardware.

---

## Solução de Problemas

### O ícone não aparece na bandeja

Verifique se o aplicativo está rodando e se há erros nos logs. Tente iniciar manualmente:

```bash
python3 ~/.local/share/deepcool-digital/main.py
```

### Display do cooler não mostra nada

Verifique as permissões USB e se o dispositivo foi detectado. Consulte o arquivo `docs/TROUBLESHOOTING.md` para mais detalhes.

### Erro de dependências

Certifique-se de que todas as dependências estão instaladas:

```bash
python3 -m pip install --user -r requirements.txt
```

---

## Desinstalação

Para remover completamente o aplicativo do sistema:

```bash
./uninstall.sh
```

Este script irá remover o aplicativo, configurações, regras udev e arquivos de autostart.

---

## Suporte

Se você encontrar problemas não cobertos neste guia, consulte:

- **Troubleshooting:** `docs/TROUBLESHOOTING.md`
- **Issues no GitHub:** https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse/issues
- **Logs do aplicativo:** `~/.config/deepcool-digital/deepcool-digital.log`

Ao reportar um problema, sempre inclua:
1. Distribuição Linux e versão
2. Versão do Python (`python3 --version`)
3. Output do comando `lsusb | grep 3633`
4. Conteúdo do arquivo de log
