# -*- coding: utf-8 -*-
"""Configuração e constantes globais."""

import os
from pathlib import Path
from typing import Dict

# Versão
VERSION: str = "1.5.0"
APP_NAME: str = "deepcool-digital"
APP_DISPLAY_NAME: str = "DeepCool Digital"

# USB
VENDOR_ID: int = 0x3633

# Display
INTERVAL: int = 2  # segundos entre atualizações

# Modelos conhecidos
KNOWN_MODELS: Dict[int, str] = {
    0x0001: "AK620 Digital",
    0x0002: "AK620 Digital",
    0x0003: "AK500 Digital",
    0x0004: "AK500S Digital",
    0x0005: "AK400 Digital",
    0x0008: "AG400 Digital",
}

# Temperaturas de alarme disponíveis (Celsius)
ALARM_TEMPS: list[int] = [60, 70, 80, 90]

# Caminhos
CONFIG_DIR: Path = Path.home() / ".config" / APP_NAME
AUTOSTART_DIR: Path = Path.home() / ".config" / "autostart"
AUTOSTART_FILE: Path = AUTOSTART_DIR / f"{APP_NAME}.desktop"

# Lock file seguro: prefere XDG_RUNTIME_DIR do usuário, com fallback para CONFIG_DIR
_runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
if _runtime_dir and os.path.isdir(_runtime_dir):
    LOCK_FILE: str = str(Path(_runtime_dir) / f"{APP_NAME}.lock")
else:
    LOCK_FILE: str = str(CONFIG_DIR / f"{APP_NAME}.lock")

LOG_FILE: Path = CONFIG_DIR / f"{APP_NAME}.log"
SETTINGS_FILE: Path = CONFIG_DIR / "settings.json"

# GitHub
GITHUB_URL: str = "https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse"
