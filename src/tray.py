# -*- coding: utf-8 -*-
"""Interface System Tray - menu de contexto e interação com o usuário."""

import time
import subprocess
import logging
from typing import Optional

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QActionGroup, QApplication
from PyQt5.QtCore import Qt

from .config import VERSION, VENDOR_ID, ALARM_TEMPS, GITHUB_URL
from .i18n import tr
from .icons import create_deepcool_icon, create_status_icon
from .driver import DeepCoolDriver, DriverSignals
from .settings import SettingsManager
from .utils import format_temperature
from . import autostart

logger = logging.getLogger(__name__)


class DeepCoolTray:
    """Gerencia o ícone na bandeja e o menu de contexto."""

    def __init__(self, app: QApplication, product_id: int, model: str, sensor: str):
        """
        Inicializa a interface system tray.
        
        Args:
            app: Aplicação Qt
            product_id: Product ID do dispositivo
            model: Nome do modelo do cooler
            sensor: Nome do sensor de temperatura
        """
        self.app: QApplication = app
        self.product_id: int = product_id
        self.model: str = model
        self.sensor: str = sensor

        # Estado
        self.connected: bool = False
        self.current_temp: float = 0.0
        self.current_cpu: int = 0

        # Gerenciador de configurações
        self.settings_manager: SettingsManager = SettingsManager()

        # Sinais
        self.signals: DriverSignals = DriverSignals()
        self.signals.status_updated.connect(self._on_status_updated)
        self.signals.connection_changed.connect(self._on_connection_changed)

        # Driver
        self.driver: DeepCoolDriver = DeepCoolDriver(self.signals, product_id, sensor)
        
        # Carregar e aplicar configurações salvas
        self._load_settings()

        # System Tray Icon
        self.tray: QSystemTrayIcon = QSystemTrayIcon()
        self.tray.setIcon(create_deepcool_icon(False))
        self.tray.setToolTip(f"DeepCool Digital - {tr('connecting')}")

        # Menu
        self.menu: QMenu = QMenu()
        self._build_menu()
        self.tray.setContextMenu(self.menu)
        
        logger.info("Interface system tray inicializada")

    def _load_settings(self) -> None:
        """Carrega configurações salvas e aplica ao driver."""
        saved_settings = self.settings_manager.load()
        self.driver.apply_settings(saved_settings)
        logger.info(f"Configurações carregadas: {saved_settings}")

    def _save_settings(self) -> None:
        """Salva configurações atuais do driver."""
        current_settings = self.driver.get_settings()
        if self.settings_manager.save(current_settings):
            logger.info("Configurações salvas com sucesso")
        else:
            logger.error("Falha ao salvar configurações")

    def start(self) -> None:
        """Mostra o ícone e inicia o driver."""
        self.tray.show()
        self.driver.start()
        logger.info("System tray iniciado")

    def _build_menu(self) -> None:
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
        device_menu: QMenu = self.menu.addMenu(f"  {self.model}")
        self._add_disabled(device_menu, f"Vendor: 0x{VENDOR_ID:04X}")
        self._add_disabled(device_menu, f"Product: 0x{self.product_id:04X}")
        self._add_disabled(device_menu, f"Sensor: {self.sensor}")

        self.menu.addSeparator()

        # ── Status (atualiza em tempo real) ──
        self.status_action: QAction = self._add_disabled(self.menu, "  🌡️ --°C │ 📊 --%")
        self.connection_action: QAction = self._add_disabled(self.menu, f"  ⏳ {tr('connecting')}")

        self.menu.addSeparator()

        # ── Display Switch ──
        display_menu: QMenu = self.menu.addMenu(f"  {tr('display_switch')}")
        self.display_group: QActionGroup = QActionGroup(self.menu)
        self.display_group.setExclusive(True)

        for mode, key in [("temp", "temperature"), ("util", "utilization"), ("auto", "automatic")]:
            action: QAction = QAction(tr(key), self.menu, checkable=True)
            action.setData(mode)
            action.setChecked(mode == self.driver.display_mode)
            action.triggered.connect(lambda _, m=mode: self._set_display_mode(m))
            self.display_group.addAction(action)
            display_menu.addAction(action)

        # ── Temperature Display ──
        temp_menu: QMenu = self.menu.addMenu(f"  {tr('temp_display')}")
        self.temp_group: QActionGroup = QActionGroup(self.menu)
        self.temp_group.setExclusive(True)

        for unit, label in [("C", "Celsius (°C)"), ("F", "Fahrenheit (°F)")]:
            action = QAction(label, self.menu, checkable=True)
            action.setChecked(unit == self.driver.temp_unit)
            action.triggered.connect(lambda _, u=unit: self._set_temp_unit(u))
            self.temp_group.addAction(action)
            temp_menu.addAction(action)

        # ── Alarm Control ──
        alarm_menu: QMenu = self.menu.addMenu(f"  {tr('alarm_control')}")
        self.alarm_group: QActionGroup = QActionGroup(self.menu)
        self.alarm_group.setExclusive(True)

        alarm_off: QAction = QAction(tr("alarm_off"), self.menu, checkable=True)
        alarm_off.setChecked(not self.driver.alarm_enabled)
        alarm_off.triggered.connect(lambda: self._set_alarm(False, 0))
        self.alarm_group.addAction(alarm_off)
        alarm_menu.addAction(alarm_off)

        alarm_menu.addSeparator()

        for temp_val in ALARM_TEMPS:
            temp_display, unit = format_temperature(float(temp_val), self.driver.temp_unit)
            label: str = f"{temp_display}{unit}"
            if self.driver.temp_unit == 'F':
                label += f" ({temp_val}°C)"
            
            action = QAction(label, self.menu, checkable=True)
            action.setChecked(self.driver.alarm_enabled and self.driver.alarm_temp == temp_val)
            action.triggered.connect(lambda _, t=temp_val: self._set_alarm(True, t))
            self.alarm_group.addAction(action)
            alarm_menu.addAction(action)

        self.menu.addSeparator()

        # ── Launch at startup ──
        self.autostart_action: QAction = QAction(f"  {tr('launch_startup')}", self.menu, checkable=True)
        self.autostart_action.setChecked(autostart.is_enabled())
        self.autostart_action.triggered.connect(self._toggle_autostart)
        self.menu.addAction(self.autostart_action)

        # ── Support ──
        support_menu: QMenu = self.menu.addMenu(f"  {tr('support')}")

        website: QAction = QAction(tr("website"), self.menu)
        website.triggered.connect(self._open_website)
        support_menu.addAction(website)

        self._add_disabled(support_menu, f"{tr('version')}: {VERSION}")

        self.menu.addSeparator()

        # ── Restart ──
        restart_action: QAction = QAction(f"  {tr('restart')}", self.menu)
        restart_action.triggered.connect(self._restart_driver)
        self.menu.addAction(restart_action)

        # ── Exit ──
        quit_action: QAction = QAction(f"  {tr('exit')}", self.menu)
        quit_action.triggered.connect(self._quit)
        self.menu.addAction(quit_action)

    # ── Helpers ──

    @staticmethod
    def _add_disabled(menu: QMenu, text: str) -> QAction:
        """
        Adiciona item desabilitado (info) ao menu.
        
        Args:
            menu: Menu onde adicionar o item
            text: Texto do item
            
        Returns:
            Ação criada
        """
        action: QAction = QAction(text, menu)
        action.setEnabled(False)
        menu.addAction(action)
        return action

    # ── Ações do menu ──

    def _set_display_mode(self, mode: str) -> None:
        """
        Define o modo de exibição.
        
        Args:
            mode: Modo de exibição ('auto', 'temp', 'util')
        """
        self.driver.display_mode = mode
        self._save_settings()
        logger.info(f"Modo de exibição alterado para: {mode}")

    def _set_temp_unit(self, unit: str) -> None:
        """
        Define a unidade de temperatura.
        
        Args:
            unit: Unidade ('C' ou 'F')
        """
        self.driver.temp_unit = unit
        self._save_settings()
        self._build_menu()  # Rebuild para atualizar labels do alarme
        logger.info(f"Unidade de temperatura alterada para: {unit}")

    def _set_alarm(self, enabled: bool, temp: int) -> None:
        """
        Configura o alarme de temperatura.
        
        Args:
            enabled: Se o alarme está habilitado
            temp: Temperatura do alarme em Celsius
        """
        self.driver.alarm_enabled = enabled
        self.driver.alarm_temp = temp
        self._save_settings()
        logger.info(f"Alarme configurado: enabled={enabled}, temp={temp}°C")

    def _toggle_autostart(self) -> None:
        """Alterna o autostart do aplicativo."""
        if self.autostart_action.isChecked():
            autostart.enable()
            logger.info("Autostart habilitado")
        else:
            autostart.disable()
            logger.info("Autostart desabilitado")

    def _open_website(self) -> None:
        """Abre o repositório GitHub no navegador."""
        try:
            subprocess.Popen(['xdg-open', GITHUB_URL])
            logger.info(f"Abrindo website: {GITHUB_URL}")
        except Exception as e:
            logger.error(f"Erro ao abrir website: {e}")

    def _restart_driver(self) -> None:
        """Reinicia o driver mantendo as configurações."""
        logger.info("Reiniciando driver...")
        settings = self.driver.get_settings()
        self.driver.stop()
        time.sleep(1)
        self.driver = DeepCoolDriver(self.signals, self.product_id, self.sensor)
        self.driver.apply_settings(settings)
        self.driver.start()
        logger.info("Driver reiniciado")

    def _quit(self) -> None:
        """Encerra o aplicativo."""
        logger.info("Encerrando aplicativo...")
        self._save_settings()  # Salvar antes de sair
        self.driver.stop()
        self.tray.hide()
        self.app.quit()

    # ── Callbacks dos sinais ──

    def _on_status_updated(self, mode: str, temp_c: float, cpu: int) -> None:
        """
        Callback quando o status é atualizado.
        
        Args:
            mode: Modo atual ('temp' ou 'util')
            temp_c: Temperatura em Celsius
            cpu: Uso da CPU em percentual
        """
        self.current_temp = temp_c
        self.current_cpu = cpu

        temp_display, unit = format_temperature(temp_c, self.driver.temp_unit)

        self.status_action.setText(f"  🌡️ {temp_display}{unit} │ 📊 {cpu}%")
        self.tray.setToolTip(f"DeepCool {self.model}\n{temp_display}{unit} │ CPU: {cpu}%")
        self.tray.setIcon(create_status_icon(temp_c, self.connected))

    def _on_connection_changed(self, connected: bool) -> None:
        """
        Callback quando o status de conexão muda.
        
        Args:
            connected: Se está conectado
        """
        self.connected = connected
        if connected:
            self.connection_action.setText(f"  ✅ {tr('connected')}")
            logger.info("Dispositivo conectado")
        else:
            self.connection_action.setText(f"  ❌ {tr('disconnected')}")
            self.tray.setIcon(create_deepcool_icon(False))
            logger.warning("Dispositivo desconectado")
