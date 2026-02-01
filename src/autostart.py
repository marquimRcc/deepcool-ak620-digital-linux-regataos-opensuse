# -*- coding: utf-8 -*-
"""Gerencia o autostart no KDE Plasma via .desktop file."""

import os
from .config import AUTOSTART_DIR, AUTOSTART_FILE, APP_DISPLAY_NAME


def get_script_path():
    """Retorna caminho absoluto do script principal (main.py)."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main.py'))


def is_enabled():
    """Verifica se autostart está habilitado."""
    return AUTOSTART_FILE.exists()


def enable():
    """Cria arquivo .desktop para iniciar automaticamente no KDE."""
    AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)
    script_path = get_script_path()

    content = f"""[Desktop Entry]
Type=Application
Name={APP_DISPLAY_NAME}
Comment=DeepCool AK Series Digital cooler driver
Exec=/usr/bin/python3.11 {script_path}
Icon=deepcool-digital
Terminal=false
Categories=System;Monitor;
StartupNotify=false
X-KDE-autostart-after=panel
"""
    AUTOSTART_FILE.write_text(content)


def disable():
    """Remove arquivo .desktop do autostart."""
    if AUTOSTART_FILE.exists():
        AUTOSTART_FILE.unlink()
