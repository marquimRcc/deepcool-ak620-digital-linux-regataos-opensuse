# Solução de Problemas / Troubleshooting

## 🇧🇷 Português

### Problema: Display não mostra nada

**1. Verificar se o dispositivo foi detectado:**
```bash
lsusb | grep -i "3633"
```

Se não aparecer nada, o cooler não está conectado ou não é reconhecido.

**2. Verificar conexão física:**
- O cabo USB do cooler deve estar conectado a um header USB 2.0 interno da placa-mãe
- Alguns headers USB 3.0 podem não funcionar corretamente

**3. Verificar permissões:**
```bash
ls -la /dev/hidraw*
```

Se as permissões não forem `crw-rw-rw-`, reconfigure o udev:
```bash
sudo tee /etc/udev/rules.d/99-deepcool.rules > /dev/null << EOF
SUBSYSTEM=="hidraw", ATTRS{idVendor}=="3633", MODE="0666"
SUBSYSTEM=="usb", ATTRS{idVendor}=="3633", MODE="0666"
EOF
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

### Problema: Erro "module 'hid' has no attribute 'device'"

Este erro acontece porque o openSUSE tem um pacote `hid` do sistema que conflita com a biblioteca Python.

**Solução:**
```bash
python3.11 -m pip uninstall -y hid
python3.11 -m pip install --user --force-reinstall hidapi
```

**Verificar se funcionou:**
```bash
python3.11 -c "import hid; print(hid.device())"
```

Deve mostrar algo como `<hid.device object at 0x...>`

---

### Problema: Serviço não inicia no boot

**1. Verificar se está habilitado:**
```bash
systemctl is-enabled deepcool-digital.service
```

Se mostrar `disabled`:
```bash
sudo systemctl enable deepcool-digital.service
```

**2. Verificar status:**
```bash
sudo systemctl status deepcool-digital.service
```

**3. Ver logs de erro:**
```bash
sudo journalctl -u deepcool-digital.service -n 50
```

---

### Problema: Temperatura mostra 0 ou valor errado

**1. Verificar sensores disponíveis:**
```bash
python3.11 -c "import psutil; print(psutil.sensors_temperatures())"
```

**2. Identificar o sensor correto:**
- Intel: geralmente `coretemp`
- AMD Ryzen: geralmente `k10temp` ou `zenpower`

**3. Editar o serviço com o sensor correto:**
```bash
sudo systemctl edit deepcool-digital.service
```

Adicione:
```ini
[Service]
Environment="SENSOR=k10temp"
```

Depois reinicie:
```bash
sudo systemctl daemon-reload
sudo systemctl restart deepcool-digital.service
```

---

### Problema: Display não alterna entre TEMP e CPU%

Verifique se o serviço está rodando corretamente:
```bash
./test.sh
```

Se funcionar em modo teste mas não como serviço, verifique os logs:
```bash
sudo journalctl -u deepcool-digital.service -f
```

---

### Problema: Display trava após suspend/hibernate

O serviço de restart deve resolver isso automaticamente. Verifique se está habilitado:
```bash
systemctl is-enabled deepcool-digital-restart.service
```

Se não estiver:
```bash
sudo systemctl enable deepcool-digital-restart.service
```

---

## 🇺🇸 English

### Issue: Display shows nothing

**1. Check if device is detected:**
```bash
lsusb | grep -i "3633"
```

**2. Check physical connection:**
- The cooler USB cable must be connected to an internal USB 2.0 header on the motherboard

**3. Check permissions:**
```bash
ls -la /dev/hidraw*
```

---

### Issue: Error "module 'hid' has no attribute 'device'"

openSUSE has a system `hid` package that conflicts with the Python library.

**Solution:**
```bash
python3.11 -m pip uninstall -y hid
python3.11 -m pip install --user --force-reinstall hidapi
```

---

### Issue: Service doesn't start on boot

**1. Check if enabled:**
```bash
systemctl is-enabled deepcool-digital.service
```

**2. Enable if needed:**
```bash
sudo systemctl enable deepcool-digital.service
```

---

### Issue: Temperature shows 0 or wrong value

**1. Check available sensors:**
```bash
python3.11 -c "import psutil; print(psutil.sensors_temperatures())"
```

**2. Common sensor names:**
- Intel: `coretemp`
- AMD Ryzen: `k10temp` or `zenpower`

---

## 📞 Ainda precisa de ajuda? / Still need help?

Abra uma issue no GitHub: https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse/issues
