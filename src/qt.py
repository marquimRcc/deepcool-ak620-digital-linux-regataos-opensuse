# -*- coding: utf-8 -*-
"""
Camada de compatibilidade transparente entre PyQt5 e PyQt6.
Permite que o aplicativo funcione perfeitamente em distribuições modernas
(com PyQt6 nativo) e em sistemas com PyQt5.
"""

try:
    from PyQt5.QtWidgets import (
        QApplication, QMessageBox, QSystemTrayIcon, QMenu, QAction,
        QActionGroup, QColorDialog
    )
    from PyQt5.QtGui import (
        QColor, QPixmap, QIcon, QPainter, QBrush, QPen, QConicalGradient, QFont
    )
    from PyQt5.QtCore import Qt, pyqtSignal, QObject
    IS_PYQT6 = False
except ImportError:
    from PyQt6.QtWidgets import (
        QApplication, QMessageBox, QSystemTrayIcon, QMenu, QColorDialog
    )
    from PyQt6.QtGui import (
        QAction, QActionGroup, QColor, QPixmap, QIcon, QPainter, QBrush, QPen, QConicalGradient, QFont
    )
    from PyQt6.QtCore import Qt, pyqtSignal, QObject
    IS_PYQT6 = True


# Aliases compatíveis para Enums do Qt
if IS_PYQT6:
    ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter
    NO_PEN = Qt.PenStyle.NoPen
    ANTIALIASING = QPainter.RenderHint.Antialiasing
    FONT_BOLD = QFont.Weight.Bold
else:
    ALIGN_CENTER = Qt.AlignCenter
    NO_PEN = Qt.NoPen
    ANTIALIASING = QPainter.Antialiasing
    FONT_BOLD = QFont.Bold
