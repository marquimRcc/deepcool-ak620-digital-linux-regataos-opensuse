# -*- coding: utf-8 -*-
"""Interface System Tray - menu de contexto e interação com o usuário."""

import time
import subprocess

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QActionGroup
from PyQt5.QtCore import Qt

from .config import VERSION, VENDOR_ID, ALARM_TEMPS, GITHUB_URL
from .i18n import tr
from .icons import create_deepcool_icon, create_status_icon
from .driver import DeepCoolDriver, DriverSignals
from . import autostart


class DeepCoolTray:
    """Gerencia o ícone na bandeja e o menu de contexto."""

    def __init__(self, app, product_id, model, sensor):
        self.app = app
        self.product_id = product_id
        self.model = model
        self.sensor = sensor

        # Estado
        self.connected = False
        self.current_temp = 0.0
        self.current_cpu = 0

        # Sinais
        self.signals = DriverSignals()
        self.signals.status_updated.connect(self._on_status_updated)
        self.signals.connection_changed.connect(self._on_connection_changed)

        # Driver
        self.driver = DeepCoolDriver(self.signals, product_id, sensor)

        # System Tray Icon
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(create_deepcool_icon(False))
        self.tray.setToolTip(f"DeepCool Digital - {tr('connecting')}")

        # Menu
        self.menu = QMenu()
        self._build_menu()
        self.tray.setContextMenu(self.menu)

    def start(self):
        """Mostra o ícone e inicia o driver."""
        self.tray.show()
        self.driver.start()

    def _build_menu(self):
        """Constrói o menu de contexto completo."""
        self.menu.clear()

        self.menu.setStyleSheet("""
            QMenu {
                background-color: palette(window);
                border: 1px solid palette(mid);
                padding: 5px 0px;
            }
            QMenu::item {
                padding: 7px 35px 7px 20px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QMenu::item:disabled {
                color: palette(dark);
            }
            QMenu::separator {
                height: 1px;
                background: palette(mid);
                margin: 5px 12px;
            }
        """)

        # ── Dispositivo ──
        device_menu = self.menu.addMenu(f"  {self.model}")
        self._add_disabled(device_menu, f"Vendor: 0x{VENDOR_ID:04X}")
        self._add_disabled(device_menu, f"Product: 0x{self.product_id:04X}")
        self._add_disabled(device_menu, f"Sensor: {self.sensor}")

        self.menu.addSeparator()

        # ── Status (atualiza em tempo real) ──
        self.status_action = self._add_disabled(self.menu, "  🌡️ --°C │ 📊 --%")
        self.connection_action = self._add_disabled(self.menu, f"  ⏳ {tr('connecting')}")

        self.menu.addSeparator()

        # ── Display Switch ──
        display_menu = self.menu.addMenu(f"  {tr('display_switch')}")
        self.display_group = QActionGroup(self.menu)
        self.display_group.setExclusive(True)

        for mode, key in [("temp", "temperature"), ("util", "utilization"), ("auto", "automatic")]:
            action = QAction(tr(key), self.menu, checkable=True)
            action.setData(mode)
            action.setChecked(mode == self.driver.display_mode)
            action.triggered.connect(lambda _, m=mode: self._set_display_mode(m))
            self.display_group.addAction(action)
            display_menu.addAction(action)

        # ── Temperature Display ──
        temp_menu = self.menu.addMenu(f"  {tr('temp_display')}")
        self.temp_group = QActionGroup(self.menu)
        self.temp_group.setExclusive(True)

        for unit, label in [("C", "Celsius (°C)"), ("F", "Fahrenheit (°F)")]:
            action = QAction(label, self.menu, checkable=True)
            action.setChecked(unit == self.driver.temp_unit)
            action.triggered.connect(lambda _, u=unit: self._set_temp_unit(u))
            self.temp_group.addAction(action)
            temp_menu.addAction(action)

        # ── Alarm Control ──
        alarm_menu = self.menu.addMenu(f"  {tr('alarm_control')}")
        self.alarm_group = QActionGroup(self.menu)
        self.alarm_group.setExclusive(True)

        alarm_off = QAction(tr("alarm_off"), self.menu, checkable=True)
        alarm_off.setChecked(not self.driver.alarm_enabled)
        alarm_off.triggered.connect(lambda: self._set_alarm(False, 0))
        self.alarm_group.addAction(alarm_off)
        alarm_menu.addAction(alarm_off)

        alarm_menu.addSeparator()

        for temp_val in ALARM_TEMPS:
            label = f"{temp_val}°C"
            if self.driver.temp_unit == 'F':
                label = f"{round((temp_val * 9/5) + 32)}°F ({temp_val}°C)"
            action = QAction(label, self.menu, checkable=True)
            action.setChecked(self.driver.alarm_enabled and self.driver.alarm_temp == temp_val)
            action.triggered.connect(lambda _, t=temp_val: self._set_alarm(True, t))
            self.alarm_group.addAction(action)
            alarm_menu.addAction(action)

        self.menu.addSeparator()

        # ── Launch at startup ──
        self.autostart_action = QAction(f"  {tr('launch_startup')}", self.menu, checkable=True)
        self.autostart_action.setChecked(autostart.is_enabled())
        self.autostart_action.triggered.connect(self._toggle_autostart)
        self.menu.addAction(self.autostart_action)

        # ── Support ──
        support_menu = self.menu.addMenu(f"  {tr('support')}")

        website = QAction(tr("website"), self.menu)
        website.triggered.connect(self._open_website)
        support_menu.addAction(website)

        self._add_disabled(support_menu, f"{tr('version')}: {VERSION}")

        self.menu.addSeparator()

        # ── Restart ──
        restart_action = QAction(f"  {tr('restart')}", self.menu)
        restart_action.triggered.connect(self._restart_driver)
        self.menu.addAction(restart_action)

        # ── Exit ──
        quit_action = QAction(f"  {tr('exit')}", self.menu)
        quit_action.triggered.connect(self._quit)
        self.menu.addAction(quit_action)

    # ── Helpers ──

    @staticmethod
    def _add_disabled(menu, text):
        """Adiciona item desabilitado (info) ao menu."""
        action = QAction(text, menu)
        action.setEnabled(False)
        menu.addAction(action)
        return action

    # ── Ações do menu ──

    def _set_display_mode(self, mode):
        self.driver.display_mode = mode

    def _set_temp_unit(self, unit):
        self.driver.temp_unit = unit
        self._build_menu()  # Rebuild para atualizar labels do alarme

    def _set_alarm(self, enabled, temp):
        self.driver.alarm_enabled = enabled
        self.driver.alarm_temp = temp

    def _toggle_autostart(self):
        if self.autostart_action.isChecked():
            autostart.enable()
        else:
            autostart.disable()

    def _open_website(self):
        """Abre o repositório GitHub no navegador."""
        try:
            subprocess.Popen(['xdg-open', GITHUB_URL])
        except Exception:
            pass

    def _restart_driver(self):
        settings = self.driver.get_settings()
        self.driver.stop()
        time.sleep(1)
        self.driver = DeepCoolDriver(self.signals, self.product_id, self.sensor)
        self.driver.apply_settings(settings)
        self.driver.start()

    def _quit(self):
        self.driver.stop()
        self.tray.hide()
        self.app.quit()

    # ── Callbacks dos sinais ──

    def _on_status_updated(self, mode, temp_c, cpu):
        self.current_temp = temp_c
        self.current_cpu = cpu

        if self.driver.temp_unit == 'F':
            temp_display = round((temp_c * 9 / 5) + 32)
            unit = '°F'
        else:
            temp_display = round(temp_c)
            unit = '°C'

        self.status_action.setText(f"  🌡️ {temp_display}{unit} │ 📊 {cpu}%")
        self.tray.setToolTip(f"DeepCool {self.model}\n{temp_display}{unit} │ CPU: {cpu}%")
        self.tray.setIcon(create_status_icon(temp_c, self.connected))

    def _on_connection_changed(self, connected):
        self.connected = connected
        if connected:
            self.connection_action.setText(f"  ✅ {tr('connected')}")
        else:
            self.connection_action.setText(f"  ❌ {tr('disconnected')}")
            self.tray.setIcon(create_deepcool_icon(False))
