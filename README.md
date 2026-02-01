# DeepCool AK Series Digital - Regata OS / openSUSE

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Regata OS](https://img.shields.io/badge/Regata%20OS-Compatible-green.svg)](https://regataos.com.br/)
[![openSUSE](https://img.shields.io/badge/openSUSE-Compatible-green.svg)](https://www.opensuse.org/)
[![KDE Plasma](https://img.shields.io/badge/KDE%20Plasma-Compatible-blue.svg)](https://kde.org/)

Aplicativo system tray para coolers DeepCool da série AK Digital no **Regata OS** e **openSUSE** com **KDE Plasma**.

> 🇺🇸 [English version](README.en.md)

---

## ✨ Características

- 🖥️ **Ícone na bandeja** do KDE com menu completo por clique direito
- 🔄 **Alterna automaticamente** entre Temperatura e Uso de CPU no display
- 🌡️ **Celsius e Fahrenheit** selecionáveis pelo menu
- ⏰ **Controle de alarme** — display pisca ao atingir temperatura definida
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
- Python 3.11
- Cooler DeepCool conectado via USB

### Instalação Rápida

```bash
git clone https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse.git
cd deepcool-ak620-digital-linux-regataos-opensuse
chmod +x install.sh
./install.sh
```

O instalador irá:
1. Instalar Python 3.11, PyQt5 e dependências
2. Corrigir o conflito da biblioteca HID no openSUSE
3. Configurar permissões USB (udev)
4. Perguntar se deseja iniciar automaticamente com o sistema
5. Iniciar o aplicativo

Após a instalação, o ícone **DeepCool Digital** aparecerá na bandeja do KDE.

---

## 📖 Uso

### Menu (clique direito no ícone)

```
  AK500S Digital          ►  Vendor / Product ID / Sensor
  ─────────────────
  🌡️ 30°C │ 📊 4%            ← atualiza em tempo real
  ✅ Conectado
  ─────────────────
  Chave de exibição       ►  ○ Temperatura
                             ○ Utilização
                             ● Automático
  Mostrador de temperatura ►  ● Celsius (°C)
                              ○ Fahrenheit (°F)
  Controle de alarme       ►  ● Desligado
                              ○ 60°C / 70°C / 80°C / 90°C
  ─────────────────
  ☐ Executar na inicialização
  Suporte                  ►  Website / Versão
  ─────────────────
  Reinicialização
  Saída
```

### Tooltip

Passe o mouse sobre o ícone para ver temperatura e uso de CPU.

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
├── src/
│   ├── config.py        # Constantes e configuração
│   ├── i18n.py          # Traduções (PT/EN)
│   ├── hardware.py      # Detecção de hardware
│   ├── protocol.py      # Protocolo HID DeepCool
│   ├── driver.py        # Thread de comunicação USB
│   ├── icons.py         # Geração de ícones
│   ├── autostart.py     # Autostart no KDE
│   └── tray.py          # Interface system tray
├── docs/
│   └── TROUBLESHOOTING.md
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
- **Adaptação Regata OS / System Tray:** [marquimRcc](https://github.com/marquimRcc)

---

## 📄 Licença

MIT — veja [LICENSE](LICENSE).
