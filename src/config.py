# -*- coding: utf-8 -*-
"""Configuração e constantes globais."""

from pathlib import Path

# Versão
VERSION = "1.1.0"
APP_NAME = "deepcool-digital"
APP_DISPLAY_NAME = "DeepCool Digital"

# USB
VENDOR_ID = 0x3633

# Display
INTERVAL = 2  # segundos entre atualizações

# Modelos conhecidos
KNOWN_MODELS = {
    0x0001: "AK620 Digital",
    0x0002: "AK620 Digital",
    0x0003: "AK500 Digital",
    0x0004: "AK500S Digital",
    0x0005: "AK400 Digital",
    0x0008: "AG400 Digital",
}

# Temperaturas de alarme disponíveis (Celsius)
ALARM_TEMPS = [60, 70, 80, 90]

# Caminhos
AUTOSTART_DIR = Path.home() / ".config" / "autostart"
AUTOSTART_FILE = AUTOSTART_DIR / f"{APP_NAME}.desktop"
LOCK_FILE = f"/tmp/{APP_NAME}.lock"

# GitHub
GITHUB_URL = "https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse"
