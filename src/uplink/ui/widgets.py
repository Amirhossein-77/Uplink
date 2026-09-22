from __future__ import annotations

from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QWidget,
)


def make_label(
    text: str = "",
    size: int = 12,
    color: str = "#e8edf7",
    bold: bool = False,
) -> QLabel:
    label = QLabel(text)

    font = QFont()
    font.setPointSize(size)
    font.setBold(bold)

    label.setFont(font)
    label.setStyleSheet(
        f"color: {color};"
    )

    return label


def apply_shadow(
    widget: QWidget,
    blur: int = 35,
    opacity: int = 85,
):
    shadow = QGraphicsDropShadowEffect()

    shadow.setBlurRadius(blur)
    shadow.setOffset(0, 7)
    shadow.setColor(
        QColor(0, 0, 0, opacity)
    )

    widget.setGraphicsEffect(shadow)


def make_card() -> QFrame:
    card = QFrame()

    card.setObjectName("glassCard")

    apply_shadow(card)

    return card