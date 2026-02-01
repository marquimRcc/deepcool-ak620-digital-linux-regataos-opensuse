#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
DeepCool Digital - System Tray App
Para Regata OS / openSUSE (KDE Plasma)

https://github.com/marquimRcc/deepcool-ak620-digital-linux-regataos-opensuse
"""

import sys
import fcntl

from PyQt5.QtWidgets import QApplication

from src.config import APP_DISPLAY_NAME, LOCK_FILE
from src.i18n import tr
from src.hardware import detect_product_id, detect_model, detect_sensor
from src.tray import DeepCoolTray


def main():
    # Prevenir múltiplas instâncias
    lock = open(LOCK_FILE, 'w')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print(f"{APP_DISPLAY_NAME} {tr('already_running')}")
        sys.exit(1)

    # Qt App
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName(APP_DISPLAY_NAME)

    # Detectar hardware
    product_id = detect_product_id()
    model = detect_model(product_id)
    sensor = detect_sensor()

    # Tray
    tray = DeepCoolTray(app, product_id, model, sensor)
    tray.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
