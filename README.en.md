# DeepCool AK Series Digital - Regata OS / openSUSE

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Regata OS](https://img.shields.io/badge/Regata%20OS-Compatible-green.svg)](https://regataos.com.br/)
[![openSUSE](https://img.shields.io/badge/openSUSE-Compatible-green.svg)](https://www.opensuse.org/)
[![KDE Plasma](https://img.shields.io/badge/KDE%20Plasma-Compatible-blue.svg)](https://kde.org/)

System tray application for DeepCool AK Series Digital coolers on **Regata OS** and **openSUSE** with **KDE Plasma**.

> 🇧🇷 [Versão em Português](README.md)

---

## 🎬 Demo

<div align="center">
  <img src="docs/demo.gif" alt="DeepCool Digital - Demo" width="600">
  <br>
  <em>Temperature, CPU usage and LED color control from the system tray</em>
</div>

---

## ✨ Features

- 🖥️ **System tray icon** with full right-click menu on KDE
- 🔄 **Auto-switches** between Temperature and CPU Usage on display
- 🌡️ **Celsius and Fahrenheit** selectable from menu
- ⏰ **Alarm control** — display blinks when temperature threshold is reached
- 🎨 **LED color control** — change the ARGB border colors via OpenRGB
- 🚀 **Autostart** — launches with KDE Plasma
- 🌍 **Auto language** — Portuguese or English based on system locale
- 🔧 **Auto-detection** of hardware and sensors
- 🐛 **Fixes HID library conflict** on openSUSE

---

## 📋 Supported Devices

| Model | Product ID | Status |
|-------|------------|--------|
| AK620 Digital | 0x0001 | ✅ Supported |
| AK500S Digital | 0x0004 | ✅ Tested |
| AK400 Digital | 0x0005 | ✅ Supported |
| AG400 Digital | 0x0008 | ✅ Supported |

---

## 🚀 Installation

### Prerequisites

- Regata OS or openSUSE (Tumbleweed/Leap)
- KDE Plasma
- Python 3.8+
- DeepCool cooler connected via USB
- **OpenRGB** *(optional — only needed for LED border color control)*

### Quick Install

```bash
git clone https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse.git
cd deepcool-ak620-digital-linux-regataos-opensuse
chmod +x install.sh
./install.sh
```

The installer will:
1. Install Python 3, PyQt5, and dependencies
2. Fix the HID library conflict on openSUSE
3. Configure USB permissions (udev)
4. **Ask if you want to install OpenRGB** (for LED color control)
5. Ask if you want to launch at startup
6. Start the application

---

## 🎨 LED Border Color Control

The DeepCool AK Series Digital cooler has **ARGB LED strips** on the top and bottom edges of the display. These LEDs are connected to the **motherboard's 3-pin ARGB header** and can be controlled through [OpenRGB](https://openrgb.org/).

### How it works

```
Your App (tray.py)  →  src/colors.py  →  OpenRGB CLI  →  Motherboard  →  ARGB LEDs
```

The app calls OpenRGB via command line to apply colors. No need to keep OpenRGB running in the background.

### Installing OpenRGB

The installer will ask automatically. To install manually:

```bash
# openSUSE / Regata OS
sudo zypper install openrgb

# Flatpak (any distro)
flatpak install flathub org.openrgb.OpenRGB
```

> ⚠️ If OpenRGB is not installed, the "Border color" menu will be disabled, but all other features work normally.

### Color menu

Right-click the tray icon and open **🎨 Border color**:

```
🎨 Border color          ►  🔴 Red         ✓
                             🔵 Blue
                             🟢 Green
                             🟣 Purple
                             🔵 Cyan
                             🟡 Yellow
                             🟠 Orange
                             ⚪ White
                             🩷 Pink
                             🌈 Rainbow
                             ⚫ Off
                             ─────────────
                             🎨 Customize...
```

- **9 quick colors** — Instant selection with colored icons
- **Rainbow** — Animated color cycling mode
- **Off** — Turns off the LEDs
- **Customize...** — Opens full color picker (QColorDialog) for any color

Your color choice is **saved automatically** and reapplied when the app starts.

### Troubleshooting LED colors

| Issue | Solution |
|-------|----------|
| Menu is disabled | Install OpenRGB: `sudo zypper install openrgb` |
| No devices detected | Run `sudo openrgb --list-devices` — may need `sudo modprobe i2c-dev` |
| Colors don't change | Check if the 3-pin ARGB cable is connected to the motherboard header |

---

## 📖 Usage

### Menu (right-click on tray icon)

```
  AK500S Digital          ►  Vendor / Product ID / Sensor
  ─────────────────
  🌡️ 30°C │ 📊 4%            ← updates in real-time
  ✅ Connected
  ─────────────────
  Display Switch          ►  ○ Temperature  ○ Utilization  ● Automatic
  Temperature Display     ►  ● Celsius (°C)  ○ Fahrenheit (°F)
  Alarm Control           ►  ● Off  ○ 60°C / 70°C / 80°C / 90°C
  ─────────────────
  🎨 Border color          ►  9 colors + Rainbow + Customize...
  ─────────────────
  ☐ Launch at startup
  Support                 ►  Website / Version
  ─────────────────
  Restart
  Exit
```

### Dynamic Icon

The tray icon changes color based on temperature:
- 🟢 **Green** — below 60°C (normal)
- 🟠 **Orange** — 60°C to 79°C (warm)
- 🔴 **Red** — 80°C or above (hot)

---

## 🗑️ Uninstall

```bash
./uninstall.sh
```

---

## 🏗️ Project Structure

```
├── main.py              # Entry point
├── install.sh           # Installer
├── uninstall.sh         # Uninstaller
├── requirements.txt     # Python dependencies
├── src/
│   ├── __init__.py      # Python package
│   ├── config.py        # Constants and configuration
│   ├── i18n.py          # Translations (PT/EN)
│   ├── hardware.py      # Hardware detection
│   ├── protocol.py      # DeepCool HID protocol
│   ├── driver.py        # USB communication thread
│   ├── icons.py         # Icon generation
│   ├── autostart.py     # KDE autostart
│   ├── settings.py      # Settings persistence
│   ├── utils.py         # Utility functions
│   ├── colors.py        # ARGB LED color control (via OpenRGB)
│   └── tray.py          # System tray interface
├── docs/
│   ├── demo.gif         # Demo GIF
│   └── TROUBLESHOOTING.md
├── CHANGELOG.md
├── INSTALL_GUIDE.md
├── LICENSE
├── README.md
└── README.en.md
```

---

## 🔧 Troubleshooting

See the full guide at [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the project
2. Create a branch (`git checkout -b feature/NewFeature`)
3. Commit your changes (`git commit -m 'Add NewFeature'`)
4. Push (`git push origin feature/NewFeature`)
5. Open a Pull Request

---

## 📜 Credits

- **Original project:** [raghulkrishna/deepcool-ak620-digital-linux](https://github.com/raghulkrishna/deepcool-ak620-digital-linux)
- **HID Protocol:** [Algorithm0/deepcool-digital-info](https://github.com/Algorithm0/deepcool-digital-info)
- **LED control:** [OpenRGB](https://openrgb.org/)
- **Regata OS Adaptation / System Tray:** [marquimRcc](https://github.com/marquimRcc)

---

## 📄 License

MIT — see [LICENSE](LICENSE).