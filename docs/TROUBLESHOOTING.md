# Solução de Problemas / Troubleshooting

## 🇧🇷 Português

### O ícone não aparece na bandeja

**1. Verificar se o app está rodando:**
```bash
pgrep -f "python3.11.*main.py"
```

**2. Iniciar manualmente:**
```bash
python3.11 ~/.local/share/deepcool-digital/main.py
```

**3. Verificar erros no terminal:**
Se iniciado manualmente, erros serão exibidos no terminal.

---

### Display do cooler não mostra nada

**1. Verificar se o dispositivo foi detectado:**
```bash
lsusb | grep -i "3633"
```

Se não aparecer: verifique a conexão USB do cooler na placa-mãe.

**2. Verificar permissões:**
```bash
ls -la /dev/hidraw*
```

Reconfigure se necessário:
```bash
sudo tee /etc/udev/rules.d/99-deepcool.rules > /dev/null << EOF
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="3633", MODE="0666"
SUBSYSTEM=="usb", ATTRS{idVendor}=="3633", MODE="0666"
EOF
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

### Erro "module 'hid' has no attribute 'device'"

O openSUSE tem um pacote `hid` do sistema que conflita com `hidapi`.

**Solução:**
```bash
python3.11 -m pip uninstall -y hid
python3.11 -m pip install --user --force-reinstall hidapi
```

**Verificar:**
```bash
python3.11 -c "import hid; print(hid.device())"
# Deve mostrar: <hid.device object at 0x...>
```

---

### Temperatura mostra 0 ou valor errado

**1. Ver sensores disponíveis:**
```bash
python3.11 -c "import psutil; print(psutil.sensors_temperatures())"
```

**2. Sensores comuns:**
- Intel: `coretemp`
- AMD Ryzen: `k10temp` ou `zenpower`

O app detecta automaticamente, mas se necessário, edite `src/config.py`.

---

### App não inicia com o sistema

**1. Verificar autostart:**
```bash
ls ~/.config/autostart/deepcool-digital.desktop
```

**2. Ativar pelo menu:**
Clique direito no ícone → "Executar na inicialização" ✓

**3. Criar manualmente:**
```bash
cat > ~/.config/autostart/deepcool-digital.desktop << EOF
[Desktop Entry]
Type=Application
Name=DeepCool Digital
Exec=/usr/bin/python3.11 $HOME/.local/share/deepcool-digital/main.py
Terminal=false
EOF
```

---

### Conflito com serviço systemd antigo

Se você usou uma versão anterior com systemd:
```bash
sudo systemctl stop deepcool-digital.service
sudo systemctl disable deepcool-digital.service
sudo rm -f /etc/systemd/system/deepcool-digital*.service
sudo systemctl daemon-reload
```

---

## 🇺🇸 English

### Tray icon doesn't appear

**1. Check if app is running:**
```bash
pgrep -f "python3.11.*main.py"
```

**2. Start manually:**
```bash
python3.11 ~/.local/share/deepcool-digital/main.py
```

---

### Display shows nothing

```bash
# Check device
lsusb | grep -i "3633"

# Check permissions
ls -la /dev/hidraw*
```

---

### Error "module 'hid' has no attribute 'device'"

```bash
python3.11 -m pip uninstall -y hid
python3.11 -m pip install --user --force-reinstall hidapi
```

---

### App doesn't start with system

Enable via right-click menu → "Launch at startup" ✓

---

## 📞 Ainda precisa de ajuda? / Still need help?

Abra uma issue: https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse/issues
