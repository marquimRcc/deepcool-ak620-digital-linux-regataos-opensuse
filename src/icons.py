# -*- coding: utf-8 -*-
"""Geração de ícones para o system tray compatível com PyQt5 e PyQt6."""

from typing import Optional, Union
from src.qt import (
    QIcon, QPixmap, QPainter, QColor, QFont,
    ALIGN_CENTER, NO_PEN, ANTIALIASING, FONT_BOLD
)


def create_deepcool_icon(connected: bool = True) -> QIcon:
    """Cria ícone com símbolo + (inspirado no logo DeepCool)."""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(ANTIALIASING)

    # Fundo
    bg = QColor(0, 137, 123) if connected else QColor(120, 120, 120)
    painter.setBrush(bg)
    painter.setPen(NO_PEN)
    painter.drawRoundedRect(2, 2, 60, 60, 14, 14)

    # Símbolo +
    painter.setBrush(QColor(255, 255, 255))
    painter.drawRoundedRect(26, 12, 12, 40, 3, 3)  # Vertical
    painter.drawRoundedRect(12, 26, 40, 12, 3, 3)  # Horizontal

    painter.end()
    return QIcon(pixmap)


def create_status_icon(
    display_value: Union[int, float],
    unit: str = "°C",
    connected: bool = True,
    temp_celsius: Optional[float] = None
) -> QIcon:
    """
    Cria ícone com temperatura e cor baseada no nível térmico.
    Suporta exibição tanto em °C quanto em °F mantendo as cores coerentes.
    """
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(ANTIALIASING)

    # Nível térmico de referência em Celsius
    celsius_ref = temp_celsius if temp_celsius is not None else float(display_value)

    # Cor por temperatura
    if not connected:
        bg = QColor(120, 120, 120)
    elif celsius_ref >= 80:
        bg = QColor(211, 47, 47)     # Vermelho
    elif celsius_ref >= 60:
        bg = QColor(245, 124, 0)     # Laranja
    else:
        bg = QColor(0, 137, 123)     # Teal

    painter.setBrush(bg)
    painter.setPen(NO_PEN)
    painter.drawRoundedRect(2, 2, 60, 60, 14, 14)

    # Número
    painter.setPen(QColor(255, 255, 255))
    painter.setFont(QFont("Arial", 18, FONT_BOLD))
    painter.drawText(2, 2, 60, 50, ALIGN_CENTER, str(round(display_value)))

    # Unidade (°C ou °F)
    painter.setFont(QFont("Arial", 9))
    painter.drawText(2, 36, 60, 24, ALIGN_CENTER, unit)

    painter.end()
    return QIcon(pixmap)
