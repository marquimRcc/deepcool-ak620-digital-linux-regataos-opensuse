# -*- coding: utf-8 -*-
"""Geração de ícones para o system tray."""

from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt


def create_deepcool_icon(connected=True):
    """Cria ícone com símbolo + (inspirado no logo DeepCool)."""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Fundo
    bg = QColor(0, 137, 123) if connected else QColor(120, 120, 120)
    painter.setBrush(bg)
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(2, 2, 60, 60, 14, 14)

    # Símbolo +
    painter.setBrush(QColor(255, 255, 255))
    painter.drawRoundedRect(26, 12, 12, 40, 3, 3)  # Vertical
    painter.drawRoundedRect(12, 26, 40, 12, 3, 3)  # Horizontal

    painter.end()
    return QIcon(pixmap)


def create_status_icon(temp_c, connected=True):
    """Cria ícone com temperatura e cor baseada no nível."""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Cor por temperatura
    if not connected:
        bg = QColor(120, 120, 120)
    elif temp_c >= 80:
        bg = QColor(211, 47, 47)     # Vermelho
    elif temp_c >= 60:
        bg = QColor(245, 124, 0)     # Laranja
    else:
        bg = QColor(0, 137, 123)     # Teal

    painter.setBrush(bg)
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(2, 2, 60, 60, 14, 14)

    # Temperatura
    painter.setPen(QColor(255, 255, 255))
    painter.setFont(QFont("Arial", 18, QFont.Bold))
    painter.drawText(2, 2, 60, 50, Qt.AlignCenter, str(round(temp_c)))

    # °C pequeno
    painter.setFont(QFont("Arial", 9))
    painter.drawText(2, 36, 60, 24, Qt.AlignCenter, "°C")

    painter.end()
    return QIcon(pixmap)
