# -*- coding: utf-8 -*-
"""Interface System Tray - menu de contexto e interação com o usuário."""

import time
import threading
import subprocess
import logging
from typing import Optional

from PyQt5.QtWidgets import (
    QSystemTrayIcon, QMenu, QAction, QActionGroup,
    QApplication, QColorDialog,
)
from PyQt5.QtGui import (
    QColor, QPixmap, QIcon, QPainter, QBrush, QPen, QConicalGradient,
)
from PyQt5.QtCore import Qt

from .config import VERSION, VENDOR_ID, ALARM_TEMPS, GITHUB_URL
from .i18n import tr
from .icons import create_deepcool_icon, create_status_icon
from .driver import DeepCoolDriver, DriverSignals
from .settings import SettingsManager
from .utils import format_temperature
from .colors import (
    is_openrgb_available, apply_color_setting,
    PRESET_COLORS, COLOR_RAINBOW, COLOR_OFF, COLOR_DEFAULT,
)
from . import autostart

logger = logging.getLogger(__name__)


def _make_color_icon(
    hex_color: Optional[str] = None,
    size: int = 16,
    is_rainbow: bool = False,
    is_off: bool = False,
) -> QIcon:
    """
    Cria um QIcon circular preenchido com a cor especificada.

    Args:
        hex_color: Cor hex (ignorado se is_rainbow ou is_off)
        size: Tamanho do ícone em pixels
        is_rainbow: True para ícone arco-íris
        is_off: True para ícone desligado

    Returns:
        QIcon com o ícone colorido
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    if is_off:
        # Círculo cinza com X
        painter.setBrush(QBrush(QColor("#333333")))
        painter.setPen(QPen(QColor("#555555"), 1))
        painter.drawEllipse(1, 1, size - 2, size - 2)
        painter.setPen(QPen(QColor("#666666"), 1.5))
        painter.drawLine(4, 4, size - 4, size - 4)
        painter.drawLine(size - 4, 4, 4, size - 4)
    elif is_rainbow:
        # Gradiente cônico arco-íris
        gradient = QConicalGradient(size / 2, size / 2, 0)
        gradient.setColorAt(0.0, QColor("#FF0000"))
        gradient.setColorAt(0.17, QColor("#FF9900"))
        gradient.setColorAt(0.33, QColor("#FFFF00"))
        gradient.setColorAt(0.50, QColor("#00FF00"))
        gradient.setColorAt(0.67, QColor("#0099FF"))
        gradient.setColorAt(0.83, QColor("#6633FF"))
        gradient.setColorAt(1.0, QColor("#FF0000"))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(1, 1, size - 2, size - 2)
    else:
        # Cor sólida
        color = QColor(hex_color or "#FF0000")
        painter.setBrush(QBrush(color))
        # Borda cinza no branco para visibilidade
        if hex_color and hex_color.upper() in ("#FFFFFF", "#FFF"):
            painter.setPen(QPen(QColor("#AAAAAA"), 1))
        else:
            painter.setPen(Qt.NoPen)
        painter.drawEllipse(1, 1, size - 2, size - 2)

    painter.end()
    return QIcon(pixmap)


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

        # Estado da cor LED (carregado do settings)
        saved = self.settings_manager.load()
        self._led_color: str = saved.get('led_color', COLOR_DEFAULT)
        self._openrgb_device_id: Optional[int] = saved.get(
            'openrgb_device_id', None
        )
        self._openrgb_zone_id: Optional[int] = saved.get(
            'openrgb_zone_id', None
        )
        self._openrgb_led_count: Optional[int] = saved.get(
            'openrgb_led_count', None
        )

        # Aplicar cor salva ao iniciar (sem bloquear startup)
        self._apply_led_color_async()

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
        """Salva configurações atuais do driver + cor LED."""
        current_settings = self.driver.get_settings()
        current_settings['led_color'] = self._led_color
        current_settings['openrgb_device_id'] = self._openrgb_device_id
        current_settings['openrgb_zone_id'] = self._openrgb_zone_id
        current_settings['openrgb_led_count'] = self._openrgb_led_count
        if self.settings_manager.save(current_settings):
            logger.info("Configurações salvas com sucesso")
        else:
            logger.error("Falha ao salvar configurações")

    def _apply_led_color_async(self) -> None:
        """Aplica a cor LED salva em background (não bloqueia startup)."""
        def _apply():
            if is_openrgb_available():
                success = apply_color_setting(
                    self._led_color, self._openrgb_device_id
                )
                if success:
                    logger.info(
                        f"Cor LED aplicada ao iniciar: {self._led_color}"
                    )
                else:
                    logger.warning(
                        f"Falha ao aplicar cor LED ao iniciar: "
                        f"{self._led_color}"
                    )

        thread = threading.Thread(target=_apply, daemon=True)
        thread.start()

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
        self.status_action: QAction = self._add_disabled(
            self.menu, "  🌡️ --°C │ 📊 --%"
        )
        self.connection_action: QAction = self._add_disabled(
            self.menu, f"  ⏳ {tr('connecting')}"
        )

        self.menu.addSeparator()

        # ── Display Switch ──
        display_menu: QMenu = self.menu.addMenu(f"  {tr('display_switch')}")
        self.display_group: QActionGroup = QActionGroup(self.menu)
        self.display_group.setExclusive(True)

        for mode, key in [("temp", "temperature"), ("util", "utilization"),
                          ("auto", "automatic")]:
            action: QAction = QAction(tr(key), self.menu, checkable=True)
            action.setData(mode)
            action.setChecked(mode == self.driver.display_mode)
            action.triggered.connect(
                lambda _, m=mode: self._set_display_mode(m)
            )
            self.display_group.addAction(action)
            display_menu.addAction(action)

        # ── Temperature Display ──
        temp_menu: QMenu = self.menu.addMenu(f"  {tr('temp_display')}")
        self.temp_group: QActionGroup = QActionGroup(self.menu)
        self.temp_group.setExclusive(True)

        for unit, label in [("C", "Celsius (°C)"), ("F", "Fahrenheit (°F)")]:
            action = QAction(label, self.menu, checkable=True)
            action.setChecked(unit == self.driver.temp_unit)
            action.triggered.connect(
                lambda _, u=unit: self._set_temp_unit(u)
            )
            self.temp_group.addAction(action)
            temp_menu.addAction(action)

        # ── Alarm Control ──
        alarm_menu: QMenu = self.menu.addMenu(f"  {tr('alarm_control')}")
        self.alarm_group: QActionGroup = QActionGroup(self.menu)
        self.alarm_group.setExclusive(True)

        alarm_off: QAction = QAction(
            tr("alarm_off"), self.menu, checkable=True
        )
        alarm_off.setChecked(not self.driver.alarm_enabled)
        alarm_off.triggered.connect(lambda: self._set_alarm(False, 0))
        self.alarm_group.addAction(alarm_off)
        alarm_menu.addAction(alarm_off)

        alarm_menu.addSeparator()

        for temp_val in ALARM_TEMPS:
            temp_display, unit = format_temperature(
                float(temp_val), self.driver.temp_unit
            )
            label: str = f"{temp_display}{unit}"
            if self.driver.temp_unit == 'F':
                label += f" ({temp_val}°C)"

            action = QAction(label, self.menu, checkable=True)
            action.setChecked(
                self.driver.alarm_enabled
                and self.driver.alarm_temp == temp_val
            )
            action.triggered.connect(
                lambda _, t=temp_val: self._set_alarm(True, t)
            )
            self.alarm_group.addAction(action)
            alarm_menu.addAction(action)

        self.menu.addSeparator()

        # ── Cor da borda LED ──
        self._build_color_menu()

        self.menu.addSeparator()

        # ── Launch at startup ──
        self.autostart_action: QAction = QAction(
            f"  {tr('launch_startup')}", self.menu, checkable=True
        )
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

    # ── Submenu de cores da borda LED ──

    def _build_color_menu(self) -> None:
        """
        Constrói o submenu 'Cor da borda' com cores predefinidas,
        arco-íris, desligado e personalizar.
        """
        openrgb_ok = is_openrgb_available()
        is_rainbow = self._led_color == COLOR_RAINBOW
        is_off = self._led_color == COLOR_OFF

        if not openrgb_ok:
            disabled_menu: QMenu = self.menu.addMenu(
                f"  🎨 {tr('color_menu_disabled')}"
            )
            disabled_menu.setEnabled(False)
            return

        color_menu: QMenu = QMenu(
            f"  🎨 {tr('color_menu_title')}", self.menu
        )
        color_menu.setIcon(_make_color_icon(
            self._led_color if not is_rainbow and not is_off else None,
            is_rainbow=is_rainbow,
            is_off=is_off,
        ))
        self.menu.addMenu(color_menu)

        color_group = QActionGroup(color_menu)
        color_group.setExclusive(True)

        # Cores predefinidas
        for i18n_key, hex_color in PRESET_COLORS:
            action = QAction(tr(i18n_key), color_menu, checkable=True)
            action.setIcon(_make_color_icon(hex_color))
            action.setChecked(
                not is_rainbow and not is_off
                and self._led_color.upper() == hex_color.upper()
            )
            action.triggered.connect(
                lambda _, c=hex_color: self._on_color_selected(c)
            )
            color_group.addAction(action)
            color_menu.addAction(action)

        # Arco-íris
        rainbow_action = QAction(
            tr("color_rainbow"), color_menu, checkable=True
        )
        rainbow_action.setIcon(_make_color_icon(is_rainbow=True))
        rainbow_action.setChecked(is_rainbow)
        rainbow_action.triggered.connect(
            lambda: self._on_color_selected(COLOR_RAINBOW)
        )
        color_group.addAction(rainbow_action)
        color_menu.addAction(rainbow_action)

        # Desligado
        off_action = QAction(tr("color_off"), color_menu, checkable=True)
        off_action.setIcon(_make_color_icon(is_off=True))
        off_action.setChecked(is_off)
        off_action.triggered.connect(
            lambda: self._on_color_selected(COLOR_OFF)
        )
        color_group.addAction(off_action)
        color_menu.addAction(off_action)

        color_menu.addSeparator()

        # Personalizar...
        custom_action = QAction(
            f"🎨 {tr('color_customize')}", color_menu
        )
        custom_action.triggered.connect(self._on_custom_color)
        color_menu.addAction(custom_action)

    def _on_color_selected(self, color_value: str) -> None:
        """Callback quando uma cor é selecionada no submenu."""
        self._led_color = color_value

        def _apply():
            success = apply_color_setting(
                color_value, self._openrgb_device_id
            )
            if success:
                logger.info(f"Cor da borda alterada: {color_value}")
            else:
                logger.warning(f"Falha ao aplicar cor: {color_value}")

        thread = threading.Thread(target=_apply, daemon=True)
        thread.start()

        self._save_settings()
        self._build_menu()

    def _on_custom_color(self) -> None:
        """Abre o QColorDialog para escolher uma cor personalizada."""
        if self._led_color in (COLOR_RAINBOW, COLOR_OFF):
            initial = QColor(COLOR_DEFAULT)
        else:
            initial = QColor(self._led_color)

        color = QColorDialog.getColor(
            initial, None, tr('color_dialog_title')
        )

        if color.isValid():
            hex_color = color.name().upper()
            self._on_color_selected(hex_color)

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
        """Define o modo de exibição."""
        self.driver.display_mode = mode
        self._save_settings()
        logger.info(f"Modo de exibição alterado para: {mode}")

    def _set_temp_unit(self, unit: str) -> None:
        """Define a unidade de temperatura."""
        self.driver.temp_unit = unit
        self._save_settings()
        self._build_menu()  # Rebuild para atualizar labels do alarme
        logger.info(f"Unidade de temperatura alterada para: {unit}")

    def _set_alarm(self, enabled: bool, temp: int) -> None:
        """Configura o alarme de temperatura."""
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
        self.driver = DeepCoolDriver(
            self.signals, self.product_id, self.sensor
        )
        self.driver.apply_settings(settings)
        self.driver.start()
        logger.info("Driver reiniciado")

    def _quit(self) -> None:
        """Encerra o aplicativo."""
        logger.info("Encerrando aplicativo...")
        self._save_settings()
        self.driver.stop()
        self.tray.hide()
        self.app.quit()

    # ── Callbacks dos sinais ──

    def _on_status_updated(self, mode: str, temp_c: float, cpu: int) -> None:
        """Callback quando o status é atualizado."""
        self.current_temp = temp_c
        self.current_cpu = cpu

        temp_display, unit = format_temperature(temp_c, self.driver.temp_unit)

        self.status_action.setText(
            f"  🌡️ {temp_display}{unit} │ 📊 {cpu}%"
        )
        self.tray.setToolTip(
            f"DeepCool {self.model}\n{temp_display}{unit} │ CPU: {cpu}%"
        )
        self.tray.setIcon(create_status_icon(temp_c, self.connected))

    def _on_connection_changed(self, connected: bool) -> None:
        """Callback quando o status de conexão muda."""
        self.connected = connected
        if connected:
            self.connection_action.setText(f"  ✅ {tr('connected')}")
            logger.info("Dispositivo conectado")
        else:
            self.connection_action.setText(f"  ❌ {tr('disconnected')}")
            self.tray.setIcon(create_deepcool_icon(False))
            logger.warning("Dispositivo desconectado")
