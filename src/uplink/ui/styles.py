UPLINK_STYLE = """
QWidget#root {
    background:
        qlineargradient(
            x1: 0,
            y1: 0,
            x2: 1,
            y2: 1,
            stop: 0 #070a12,
            stop: 0.42 #0d1220,
            stop: 1 #111a2b
        );

    border: 1px solid rgba(255, 255, 255, 18);
    border-radius: 24px;
}

QFrame#glassCard {
    background: rgba(20, 27, 43, 185);
    border: 1px solid rgba(255, 255, 255, 24);
    border-radius: 18px;
}

QFrame#glassCard[ipChanged="true"] {
    background: rgba(55, 43, 20, 185);
    border: 1px solid rgba(251, 191, 36, 100);
}

QLabel#logo {
    color: #7dd3fc;
    font-size: 32px;
    font-weight: bold;
}

QLabel#statusDotStopped {
    color: #64748b;
    font-size: 13px;
}

QLabel#statusDotRunning {
    color: #4ade80;
    font-size: 13px;
}

QPushButton {
    background: rgba(255, 255, 255, 8);
    color: #cbd5e1;
    border: 1px solid rgba(255, 255, 255, 15);
    border-radius: 9px;
    padding: 8px 13px;
    font-size: 11px;
    font-weight: 600;
}

QPushButton:hover {
    background: rgba(255, 255, 255, 15);
    border: 1px solid rgba(125, 211, 252, 60);
}

QPushButton:pressed {
    background: rgba(125, 211, 252, 20);
}

QPushButton#startButton {
    background:
        qlineargradient(
            x1: 0,
            y1: 0,
            x2: 1,
            y2: 0,
            stop: 0 #38bdf8,
            stop: 1 #818cf8
        );

    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton#startButton:hover {
    background:
        qlineargradient(
            x1: 0,
            y1: 0,
            x2: 1,
            y2: 0,
            stop: 0 #67e8f9,
            stop: 1 #a5b4fc
        );
}

QPushButton#startButton:pressed {
    background: #2563eb;
}

QPushButton#smallButton {
    padding: 6px 12px;
    border-radius: 8px;
}

QPushButton#windowButton,
QPushButton#closeButton {
    background: transparent;
    border: none;
    color: #718096;
    font-size: 17px;
    padding: 2px;
}

QPushButton#windowButton:hover {
    color: white;
    background: rgba(255, 255, 255, 10);
}

QPushButton#closeButton:hover {
    color: #fca5a5;
    background: rgba(248, 113, 113, 15);
}

QLineEdit,
QSpinBox {
    background: rgba(4, 8, 18, 175);
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 15);
    border-radius: 9px;
    padding: 9px;
    selection-background-color: #3b82f6;
}

QLineEdit:focus,
QSpinBox:focus {
    border: 1px solid rgba(125, 211, 252, 100);
}

QCheckBox {
    color: #aeb9ca;
    font-size: 11px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 15px;
    height: 15px;
    border-radius: 5px;
    background: rgba(255, 255, 255, 8);
    border: 1px solid rgba(255, 255, 255, 25);
}

QCheckBox::indicator:checked {
    background: #38bdf8;
    border: 1px solid #38bdf8;
}

QPlainTextEdit {
    background: rgba(3, 7, 15, 160);
    color: #91a0b7;
    border: 1px solid rgba(255, 255, 255, 10);
    border-radius: 12px;
    padding: 12px;
    font-family:
        "JetBrains Mono",
        "Cascadia Code",
        "Consolas",
        monospace;
    font-size: 10px;
}

/*
 * Keep the entire configuration scroll hierarchy
 * transparent so the glass card remains visible.
 */

QScrollArea#settingsScroll {
    background: transparent;
    border: none;
}

QScrollArea#settingsScroll > QWidget {
    background: transparent;
    border: none;
}

QScrollArea#settingsScroll > QWidget > QWidget {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    background: transparent;
    width: 7px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 25);
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(125, 211, 252, 60);
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: transparent;
    height: 7px;
}

QScrollBar::handle:horizontal {
    background: rgba(255, 255, 255, 25);
    border-radius: 4px;
}
"""