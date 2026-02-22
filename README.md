# DeepCool AK Series Digital - Regata OS / openSUSE

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Regata OS](https://img.shields.io/badge/Regata%20OS-Compatible-green.svg)](https://regataos.com.br/)
[![openSUSE](https://img.shields.io/badge/openSUSE-Compatible-green.svg)](https://www.opensuse.org/)
[![KDE Plasma](https://img.shields.io/badge/KDE%20Plasma-Compatible-blue.svg)](https://kde.org/)

Aplicativo system tray para coolers DeepCool da série AK Digital no **Regata OS** e **openSUSE** com **KDE Plasma**.
## 🎬 Demo

<div align="center">
  <img src="docs/demo.gif" alt="DeepCool Digital - Demo" width="600">
  <br>
  <em>Controle de temperatura, uso de CPU e cores LED pelo system tray</em>
</div>

> 🇺🇸 [English version](README.en.md)

---

## ✨ Características

- 🖥️ **Ícone na bandeja** do KDE com menu completo por clique direito
- 🔄 **Alterna automaticamente** entre Temperatura e Uso de CPU no display
- 🌡️ **Celsius e Fahrenheit** selecionáveis pelo menu
- ⏰ **Controle de alarme** — display pisca ao atingir temperatura definida
- 🎨 **Controle de cores LED** — mude as cores da borda ARGB do display via OpenRGB
- 🚀 **Autostart** — inicia junto com o KDE Plasma
- 🌍 **Idioma automático** — Português ou Inglês conforme o sistema
- 🔧 **Detecção automática** de hardware e sensores
- 🐛 **Correção do conflito** da biblioteca HID no openSUSE

---

## 📋 Dispositivos Suportados

| Modelo | Product ID | Status |
|--------|------------|--------|
| AK620 Digital | 0x0001 | ✅ Suportado |
| AK500S Digital | 0x0004 | ✅ Testado |
| AK400 Digital | 0x0005 | ✅ Suportado |
| AG400 Digital | 0x0008 | ✅ Suportado |

---

## 🚀 Instalação

### Pré-requisitos

- Regata OS ou openSUSE (Tumbleweed/Leap)
- KDE Plasma
- Python 3.8+
- Cooler DeepCool conectado via USB
- **OpenRGB** *(opcional — necessário para controlar as cores da borda LED)*

### Instalação Rápida

```bash
git clone https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse.git
cd deepcool-ak620-digital-linux-regataos-opensuse
chmod +x install.sh
./install.sh
```

O instalador irá:
1. Instalar Python 3, PyQt5 e dependências
2. Corrigir o conflito da biblioteca HID no openSUSE
3. Configurar permissões USB (udev)
4. **Perguntar se deseja instalar o OpenRGB** (para controle de cores LED)
5. Perguntar se deseja iniciar automaticamente com o sistema
6. Iniciar o aplicativo

Após a instalação, o ícone **DeepCool Digital** aparecerá na bandeja do KDE.

---

## 🎨 Controle de Cores da Borda LED

O cooler DeepCool AK Series Digital possui fitas **LED ARGB** nas bordas superior e inferior do display. Essas LEDs são conectadas ao **header ARGB 3-pin da placa-mãe** e podem ser controladas pelo aplicativo através do [OpenRGB](https://openrgb.org/).

### Como funciona

```
Seu App (tray.py)  →  src/colors.py  →  OpenRGB CLI  →  Placa-mãe  →  LEDs ARGB
```

O app chama o OpenRGB via linha de comando para aplicar as cores. Não precisa manter o OpenRGB rodando em segundo plano.

### Instalando o OpenRGB

O instalador pergunta automaticamente. Para instalar manualmente:

```bash
# openSUSE / Regata OS
sudo zypper install openrgb

# Flatpak (qualquer distro)
flatpak install flathub org.openrgb.OpenRGB

# AppImage / Manual
# Baixe em https://openrgb.org/#downloads
```

> ⚠️ Se o OpenRGB não estiver instalado, o menu "Cor da borda" ficará desabilitado, mas todas as outras funções continuam normalmente.

### Menu de cores

Clique com o botão direito no ícone e acesse **🎨 Cor da borda**:

```
🎨 Cor da borda          ►  🔴 Vermelho    ✓
                             🔵 Azul
                             🟢 Verde
                             🟣 Roxo
                             🔵 Ciano
                             🟡 Amarelo
                             🟠 Laranja
                             ⚪ Branco
                             🩷 Rosa
                             🌈 Arco-íris
                             ⚫ Desligado
                             ─────────────
                             🎨 Personalizar...
```

- **9 cores rápidas** — Seleção instantânea com ícones coloridos
- **Arco-íris** — Modo animado que alterna entre cores
- **Desligado** — Apaga as LEDs
- **Personalizar...** — Abre seletor de cores completo (QColorDialog) para qualquer cor

A cor escolhida é **salva automaticamente** e reaplicada ao iniciar o app.

### Problemas com cores LED

| Problema | Solução |
|----------|---------|
| Menu desabilitado | Instale o OpenRGB: `sudo zypper install openrgb` |
| Não detecta dispositivos | `sudo openrgb --list-devices` — pode precisar de `sudo modprobe i2c-dev` |
| Cores não mudam | Verifique se o cabo ARGB 3-pin está conectado ao header da placa-mãe |
| Apenas algumas cores funcionam | Verifique [compatibilidade](https://openrgb.org/devices) da sua placa-mãe |

---

## 📖 Uso

### Menu (clique direito no ícone)

```
  AK500S Digital          ►  Vendor / Product ID / Sensor
  ─────────────────
  🌡️ 30°C │ 📊 4%            ← atualiza em tempo real
  ✅ Conectado
  ─────────────────
  Exibir                  ►  ○ Temperatura  ○ Uso de CPU  ● Automático
  Mostrador de temperatura ►  ● Celsius (°C)  ○ Fahrenheit (°F)
  Controle de alarme       ►  ● Desligado  ○ 60°C / 70°C / 80°C / 90°C
  ─────────────────
  🎨 Cor da borda          ►  9 cores + Arco-íris + Personalizar...
  ─────────────────
  ☐ Executar na inicialização
  Suporte                  ►  Website / Versão
  ─────────────────
  Reiniciar
  Sair
```

### Ícone dinâmico

O ícone na bandeja muda de cor conforme a temperatura:
- 🟢 **Verde** — abaixo de 60°C (normal)
- 🟠 **Laranja** — 60°C a 79°C (atenção)
- 🔴 **Vermelho** — 80°C ou mais (quente)

---

## 🗑️ Desinstalação

```bash
./uninstall.sh
```

---

## 🏗️ Estrutura do Projeto

```
├── main.py              # Ponto de entrada
├── install.sh           # Instalador
├── uninstall.sh         # Desinstalador
├── requirements.txt     # Dependências Python
├── src/
│   ├── __init__.py      # Pacote Python
│   ├── config.py        # Constantes e configuração
│   ├── i18n.py          # Traduções (PT/EN)
│   ├── hardware.py      # Detecção de hardware
│   ├── protocol.py      # Protocolo HID DeepCool
│   ├── driver.py        # Thread de comunicação USB
│   ├── icons.py         # Geração de ícones
│   ├── autostart.py     # Autostart no KDE
│   ├── settings.py      # Persistência de configurações
│   ├── utils.py         # Funções utilitárias
│   ├── colors.py        # Controle de cores LED ARGB (via OpenRGB)
│   └── tray.py          # Interface system tray
├── docs/
│   └── TROUBLESHOOTING.md
├── CHANGELOG.md
├── INSTALL_GUIDE.md
├── LICENSE
├── README.md
└── README.en.md
```

---

## 🔧 Solução de Problemas

Veja o guia completo em [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

---

## 🤝 Contribuindo

Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

---

## 📜 Créditos

- **Projeto original:** [raghulkrishna/deepcool-ak620-digital-linux](https://github.com/raghulkrishna/deepcool-ak620-digital-linux)
- **Protocolo HID:** [Algorithm0/deepcool-digital-info](https://github.com/Algorithm0/deepcool-digital-info)
- **Controle LED:** [OpenRGB](https://openrgb.org/)
- **Adaptação Regata OS / System Tray:** [marquimRcc with Claude Opus 4.6](https://github.com/marquimRcc)

---

## 📄 Licença

MIT — veja [LICENSE](LICENSE).
