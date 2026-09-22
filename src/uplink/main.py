import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from config import APP_NAME
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setStyle("Fusion")
    app.setFont(QFont("Inter", 10))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()