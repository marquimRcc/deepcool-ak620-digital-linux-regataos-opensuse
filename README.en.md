# DeepCool AK Series Digital - Regata OS / openSUSE

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Regata OS](https://img.shields.io/badge/Regata%20OS-Compatible-green.svg)](https://regataos.com.br/)
[![openSUSE](https://img.shields.io/badge/openSUSE-Compatible-green.svg)](https://www.opensuse.org/)

DeepCool AK Series Digital cooler driver adapted for **Regata OS** and **openSUSE**.

> 🇧🇷 [Versão em Português](README.md)

![DeepCool AK500S Digital](https://img.shields.io/badge/Tested-AK500S%20Digital-blue)
![DeepCool AK620 Digital](https://img.shields.io/badge/Supported-AK620%20Digital-blue)

---

## ✨ Features

- 🎨 **Colored logs** with timestamps in terminal
- 🔄 **Auto-switches** between Temperature and CPU Usage on display
- 🌡️ **Celsius and Fahrenheit** support
- 🚀 **Auto-starts** on system boot
- 😴 **Restarts after suspend/hibernate**
- 🔧 **Auto-detection** of hardware and sensors
- 🐛 **Fixes HID library conflict** on openSUSE

---

## 📋 Supported Devices

| Model | Product ID | Status |
|-------|------------|--------|
| AK620 Digital | 0x0001 | ✅ Supported |
| AK500S Digital | 0x0004 | ✅ Tested |
| AK400 Digital | 0x0001 | ✅ Supported |

---

## 🚀 Installation

### Prerequisites

- Regata OS or openSUSE (Tumbleweed/Leap)
- Python 3.11
- DeepCool cooler connected via USB

### Quick Install

```bash
# Clone the repository
git clone https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse.git
cd deepcool-ak620-digital-linux-regataos-opensuse

# Run the installer
chmod +x install.sh
./install.sh
```

The installer will:
1. Auto-detect your hardware
2. Ask which cooler model you have
3. Ask if you prefer Celsius or Fahrenheit
4. Install all dependencies
5. Configure the service to start on boot

---

## 📖 Usage

### Helper Scripts

After installation, use the helper scripts:

```bash
cd ~/Documentos/git/deepcool-ak620-digital-linux-regataos-opensuse

./status.sh      # Check service status and recent logs
./logs.sh        # View real-time logs (colored!)
./restart.sh     # Restart the service
./test.sh        # Test manually (debug mode)
```

### Systemd Commands

```bash
# Check status
sudo systemctl status deepcool-digital.service

# Stop service
sudo systemctl stop deepcool-digital.service

# Start service
sudo systemctl start deepcool-digital.service

# Disable from boot
sudo systemctl disable deepcool-digital.service
```

---

## 🗑️ Uninstall

```bash
./uninstall.sh
```

Or manually:

```bash
sudo systemctl stop deepcool-digital.service
sudo systemctl disable deepcool-digital.service
sudo rm /etc/systemd/system/deepcool-digital*.service
sudo rm /etc/udev/rules.d/99-deepcool.rules
sudo systemctl daemon-reload
```

---

## 🔧 Troubleshooting

See the full guide at [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

### Common Issues

**Display shows nothing:**
```bash
# Check if device was detected
lsusb | grep -i "3633"

# Check permissions
ls -la /dev/hidraw*
```

**Error "module 'hid' has no attribute 'device'":**
```bash
# Reinstall correct library
python3.11 -m pip uninstall -y hid
python3.11 -m pip install --user --force-reinstall hidapi
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/NewFeature`)
3. Commit your changes (`git commit -m 'Add NewFeature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

---

## 📜 Credits

- **Original project:** [raghulkrishna/deepcool-ak620-digital-linux](https://github.com/raghulkrishna/deepcool-ak620-digital-linux)
- **HID Protocol:** [Algorithm0/deepcool-digital-info](https://github.com/Algorithm0/deepcool-digital-info)
- **Regata OS Adaptation:** [marquimRcc](https://github.com/marquimRcc)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
