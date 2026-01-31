# DeepCool AK Series Digital - Regata OS / openSUSE

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Regata OS](https://img.shields.io/badge/Regata%20OS-Compatible-green.svg)](https://regataos.com.br/)
[![openSUSE](https://img.shields.io/badge/openSUSE-Compatible-green.svg)](https://www.opensuse.org/)

Driver para coolers DeepCool da série AK Digital adaptado para **Regata OS** e **openSUSE**.

> 🇺🇸 [English version](README.en.md)

![DeepCool AK500S Digital](https://img.shields.io/badge/Testado-AK500S%20Digital-blue)
![DeepCool AK620 Digital](https://img.shields.io/badge/Suportado-AK620%20Digital-blue)

---

## ✨ Características

- 🎨 **Logs coloridos** com timestamps no terminal
- 🔄 **Alterna automaticamente** entre Temperatura e Uso de CPU no display
- 🌡️ **Suporte a Celsius e Fahrenheit**
- 🚀 **Inicia automaticamente** no boot do sistema
- 😴 **Reinicia após suspend/hibernate**
- 🔧 **Detecção automática** de hardware e sensores
- 🐛 **Correção do conflito** da biblioteca HID no openSUSE

---

## 📋 Dispositivos Suportados

| Modelo | Product ID | Status |
|--------|------------|--------|
| AK620 Digital | 0x0001 | ✅ Suportado |
| AK500S Digital | 0x0004 | ✅ Testado |
| AK400 Digital | 0x0001 | ✅ Suportado |

---

## 🚀 Instalação

### Pré-requisitos

- Regata OS ou openSUSE (Tumbleweed/Leap)
- Python 3.11
- Cooler DeepCool conectado via USB

### Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse.git
cd deepcool-ak620-digital-linux-regataos-opensuse

# Execute o instalador
chmod +x install.sh
./install.sh
```

O instalador irá:
1. Detectar seu hardware automaticamente
2. Perguntar qual modelo de cooler você possui
3. Perguntar se prefere Celsius ou Fahrenheit
4. Instalar todas as dependências
5. Configurar o serviço para iniciar no boot

---

## 📖 Uso

### Comandos Úteis

Após a instalação, use os scripts auxiliares:

```bash
cd ~/Documentos/git/deepcool-ak620-digital-linux-regataos-opensuse

./status.sh      # Ver status do serviço e logs recentes
./logs.sh        # Ver logs em tempo real (coloridos!)
./restart.sh     # Reiniciar o serviço
./test.sh        # Testar manualmente (modo debug)
```

### Comandos Systemd

```bash
# Ver status
sudo systemctl status deepcool-digital.service

# Parar serviço
sudo systemctl stop deepcool-digital.service

# Iniciar serviço
sudo systemctl start deepcool-digital.service

# Desabilitar do boot
sudo systemctl disable deepcool-digital.service
```

---

## 🗑️ Desinstalação

```bash
./uninstall.sh
```

Ou manualmente:

```bash
sudo systemctl stop deepcool-digital.service
sudo systemctl disable deepcool-digital.service
sudo rm /etc/systemd/system/deepcool-digital*.service
sudo rm /etc/udev/rules.d/99-deepcool.rules
sudo systemctl daemon-reload
```

---

## 🔧 Solução de Problemas

Veja o guia completo em [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

### Problemas Comuns

**Display não mostra nada:**
```bash
# Verificar se o dispositivo foi detectado
lsusb | grep -i "3633"

# Verificar permissões
ls -la /dev/hidraw*
```

**Erro "module 'hid' has no attribute 'device'":**
```bash
# Reinstalar biblioteca correta
python3.11 -m pip uninstall -y hid
python3.11 -m pip install --user --force-reinstall hidapi
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um Fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abrir um Pull Request

---

## 📜 Créditos

- **Projeto original:** [raghulkrishna/deepcool-ak620-digital-linux](https://github.com/raghulkrishna/deepcool-ak620-digital-linux)
- **Protocolo HID:** [Algorithm0/deepcool-digital-info](https://github.com/Algorithm0/deepcool-digital-info)
- **Adaptação Regata OS:** [marquimRcc](https://github.com/marquimRcc)

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 📊 Exemplo de Logs

```
══════════════════════════════════════════════════════
  DeepCool Digital v2.4 - Regata OS
  Sensor: coretemp │ Device: 0x3633:0x4
  Modo:   TEMP(2s) ↔ CPU%(2s)
══════════════════════════════════════════════════════

[14:32:15] ▶ Conectando (0x3633:0x4)...
[14:32:15] ✓ Conectado!

[14:32:16] [🌡️ TEMP] Display:  32°C │ Barra: [███░░░░░░░]
[14:32:18] [📊 CPU%] Display:  45 % │ Barra: [████░░░░░░]
[14:32:20] [🌡️ TEMP] Display:  33°C │ Barra: [███░░░░░░░]
[14:32:22] [📊 CPU%] Display:  38 % │ Barra: [███░░░░░░░]
```
