from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import (
    QThread,
    QTimer,
    Qt,
    Slot,
)

from PySide6.QtWidgets import (
    QBoxLayout,
    QCheckBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QLabel
)

from config import APP_NAME, DEFAULT_HOSTS, WorkerConfig
from ui.styles import UPLINK_STYLE
from ui.widgets import make_card, make_label
from worker import KeepAliveWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.worker: KeepAliveWorker | None = None
        self.thread: QThread | None = None

        self.running = False
        self.elapsed = 0
        self.drag_position = None
        self.stats_columns = 4

        self.setWindowTitle(APP_NAME)
        self.resize(1180, 760)
        self.setMinimumSize(820, 600)

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Window
        )
        self.setAttribute(
            Qt.WA_TranslucentBackground
        )

        self.build_ui()
        self.apply_styles()

        self.timer = QTimer(self)
        self.timer.timeout.connect(
            self.update_countdown
        )

        QTimer.singleShot(
            0,
            self.update_responsive_layout,
        )

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def build_ui(self):
        root = QWidget()
        root.setObjectName("root")

        self.setCentralWidget(root)

        main = QVBoxLayout(root)
        main.setContentsMargins(
            26,
            22,
            26,
            22,
        )
        main.setSpacing(15)

        main.addLayout(
            self.build_header()
        )

        main.addWidget(
            self.build_hero()
        )

        self.build_stats()
        main.addWidget(
            self.stats_widget
        )

        self.build_content()
        main.addLayout(
            self.content_layout,
            1,
        )

        main.addLayout(
            self.build_footer()
        )

    def build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(9)

        logo = QLabel("◉")
        logo.setObjectName("logo")

        header.addWidget(logo)

        title_box = QVBoxLayout()
        title_box.setSpacing(0)

        title_box.addWidget(
            make_label(
                "UPLINK",
                21,
                "#ffffff",
                True,
            )
        )

        title_box.addWidget(
            make_label(
                "Network connection guardian",
                10,
                "#7f8ba3",
            )
        )

        header.addLayout(title_box)
        header.addStretch()

        self.status_dot = QLabel("●")
        self.status_dot.setObjectName(
            "statusDotStopped"
        )

        self.status_label = make_label(
            "Stopped",
            11,
            "#aab3c5",
            True,
        )

        status_box = QHBoxLayout()
        status_box.setSpacing(7)

        status_box.addWidget(
            self.status_dot
        )
        status_box.addWidget(
            self.status_label
        )

        header.addLayout(status_box)
        header.addSpacing(14)

        minimize = QPushButton("—")
        minimize.setObjectName(
            "windowButton"
        )
        minimize.setFixedSize(32, 30)
        minimize.clicked.connect(
            self.showMinimized
        )

        self.maximize_button = QPushButton("□")
        self.maximize_button.setObjectName(
            "windowButton"
        )
        self.maximize_button.setFixedSize(
            32,
            30,
        )
        self.maximize_button.clicked.connect(
            self.toggle_maximize
        )

        close = QPushButton("×")
        close.setObjectName("closeButton")
        close.setFixedSize(32, 30)
        close.clicked.connect(self.close)

        header.addWidget(minimize)
        header.addWidget(
            self.maximize_button
        )
        header.addWidget(close)

        return header

    def build_hero(self) -> QFrame:
        hero = make_card()

        layout = QHBoxLayout(hero)
        layout.setContentsMargins(
            24,
            19,
            24,
            19,
        )
        layout.setSpacing(20)

        left = QVBoxLayout()
        left.setSpacing(4)

        self.hero_status = make_label(
            "Ready to protect your connection",
            21,
            "#ffffff",
            True,
        )

        self.hero_description = make_label(
            (
                "Start the monitor to begin "
                "sending periodic network traffic."
            ),
            11,
            "#8e99ad",
        )
        self.hero_description.setWordWrap(True)

        left.addWidget(
            self.hero_status
        )
        left.addWidget(
            self.hero_description
        )
        left.addSpacing(10)

        target_row = QHBoxLayout()
        target_row.setSpacing(10)

        target_row.addWidget(
            make_label(
                "TARGET",
                8,
                "#68758e",
                True,
            )
        )

        self.target_label = make_label(
            "—",
            12,
            "#dbe3f2",
            True,
        )

        target_row.addWidget(
            self.target_label
        )
        target_row.addStretch()

        left.addLayout(target_row)
        layout.addLayout(left, 1)

        countdown = QVBoxLayout()
        countdown.setAlignment(
            Qt.AlignCenter
        )

        countdown.addWidget(
            make_label(
                "NEXT PROBE",
                8,
                "#68758e",
                True,
            ),
            alignment=Qt.AlignCenter,
        )

        self.countdown_label = make_label(
            "—",
            34,
            "#7dd3fc",
            True,
        )

        countdown.addWidget(
            self.countdown_label,
            alignment=Qt.AlignCenter,
        )

        layout.addLayout(countdown)

        return hero

    def build_stats(self):
        self.stats_widget = QWidget()

        self.stats_layout = QGridLayout(
            self.stats_widget
        )
        self.stats_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        self.stats_layout.setHorizontalSpacing(12)
        self.stats_layout.setVerticalSpacing(12)

        self.cycle_card = self.create_stat_card(
            "CYCLES",
            "0",
            "#c4b5fd",
        )

        self.success_card = self.create_stat_card(
            "SUCCESS",
            "0",
            "#86efac",
        )

        self.failure_card = self.create_stat_card(
            "FAILED",
            "0",
            "#fca5a5",
        )

        self.ip_card = self.create_stat_card(
            "PUBLIC IP",
            "—",
            "#7dd3fc",
        )

        self.stat_cards = [
            self.cycle_card,
            self.success_card,
            self.failure_card,
            self.ip_card,
        ]

    def create_stat_card(
        self,
        title: str,
        value: str,
        color: str,
    ) -> QFrame:
        card = make_card()
        card.setMinimumHeight(70)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(
            16,
            11,
            16,
            11,
        )
        layout.setSpacing(2)

        layout.addWidget(
            make_label(
                title,
                8,
                "#69758a",
                True,
            )
        )

        value_label = make_label(
            value,
            18,
            color,
            True,
        )

        layout.addWidget(value_label)

        card.value_label = value_label

        return card

    def build_content(self):
        self.content_layout = QBoxLayout(
            QBoxLayout.LeftToRight
        )
        self.content_layout.setSpacing(14)
        self.content_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.build_settings()
        self.build_activity()

        self.content_layout.addWidget(
            self.settings_card,
            0,
        )
        self.content_layout.addWidget(
            self.log_card,
            1,
        )

    def build_settings(self):
        self.settings_card = make_card()

        layout = QVBoxLayout(
            self.settings_card
        )
        layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )
        layout.setSpacing(10)

        layout.addWidget(
            make_label(
                "Configuration",
                15,
                "#ffffff",
                True,
            )
        )

        scroll = QScrollArea()
        scroll.setObjectName(
            "settingsScroll"
        )
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )
        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAsNeeded
        )

        settings_content = QWidget()

        settings_content.setAttribute(
            Qt.WA_TranslucentBackground
        )
        settings_content.setStyleSheet(
            "background: transparent;"
        )

        settings_layout = QVBoxLayout(
            settings_content
        )
        settings_layout.setContentsMargins(
            2,
            4,
            8,
            4,
        )
        settings_layout.setSpacing(11)

        settings_layout.addWidget(
            make_label(
                "Probe interval",
                9,
                "#7d889d",
                True,
            )
        )

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(
            5,
            86400,
        )
        self.interval_spin.setValue(60)
        self.interval_spin.setSuffix(
            " sec"
        )

        settings_layout.addWidget(
            self.interval_spin
        )

        settings_layout.addWidget(
            make_label(
                "Hosts",
                9,
                "#7d889d",
                True,
            )
        )

        self.host_input = QLineEdit()
        self.host_input.setText(
            ", ".join(DEFAULT_HOSTS)
        )
        self.host_input.setPlaceholderText(
            "1.1.1.1, 8.8.8.8, 9.9.9.9"
        )

        settings_layout.addWidget(
            self.host_input
        )

        settings_layout.addWidget(
            make_label(
                "Separate multiple hosts with commas.",
                8,
                "#58657b",
            )
        )

        self.tcp_checkbox = QCheckBox(
            "Use TCP fallback"
        )
        self.tcp_checkbox.setChecked(True)

        settings_layout.addWidget(
            self.tcp_checkbox
        )

        self.ip_checkbox = QCheckBox(
            "Monitor public IP"
        )
        self.ip_checkbox.setChecked(True)
        self.ip_checkbox.stateChanged.connect(
            self.ip_setting_changed
        )

        settings_layout.addWidget(
            self.ip_checkbox
        )

        settings_layout.addWidget(
            make_label(
                "IP check frequency",
                9,
                "#7d889d",
                True,
            )
        )

        self.ip_every_spin = QSpinBox()
        self.ip_every_spin.setRange(
            1,
            1000,
        )
        self.ip_every_spin.setValue(1)
        self.ip_every_spin.setSuffix(
            " cycles"
        )

        settings_layout.addWidget(
            self.ip_every_spin
        )

        settings_layout.addStretch()

        scroll.setWidget(
            settings_content
        )

        layout.addWidget(
            scroll,
            1,
        )

        self.start_button = QPushButton(
            "▶   Start Uplink"
        )
        self.start_button.setObjectName(
            "startButton"
        )
        self.start_button.setMinimumHeight(46)
        self.start_button.clicked.connect(
            self.toggle_worker
        )

        layout.addWidget(
            self.start_button
        )

    def build_activity(self):
        self.log_card = make_card()

        layout = QVBoxLayout(
            self.log_card
        )
        layout.setContentsMargins(
            20,
            20,
            20,
            20,
        )
        layout.setSpacing(10)

        header = QHBoxLayout()

        header.addWidget(
            make_label(
                "Activity",
                15,
                "#ffffff",
                True,
            )
        )

        header.addStretch()

        self.clear_button = QPushButton(
            "Clear"
        )
        self.clear_button.setObjectName(
            "smallButton"
        )
        self.clear_button.clicked.connect(
            self.clear_logs
        )

        header.addWidget(
            self.clear_button
        )

        layout.addLayout(header)

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(
            1000
        )

        layout.addWidget(
            self.log_view
        )

    def build_footer(self) -> QHBoxLayout:
        footer = QHBoxLayout()

        footer.addWidget(
            make_label(
                "UPLINK",
                8,
                "#566176",
                True,
            )
        )

        footer.addStretch()

        footer.addWidget(
            make_label(
                "PySide6 • Network Monitor",
                8,
                "#566176",
            )
        )

        return footer

    # ------------------------------------------------------------------
    # Responsive layout
    # ------------------------------------------------------------------

    def update_responsive_layout(self):
        width = self.width()

        if width < 1000:
            self.content_layout.setDirection(
                QBoxLayout.TopToBottom
            )

            self.settings_card.setMinimumWidth(0)
            self.settings_card.setMaximumWidth(
                16777215
            )

            self.settings_card.setMinimumHeight(
                280
            )
            self.settings_card.setMaximumHeight(
                360
            )

            self.log_card.setMinimumWidth(0)
            self.log_card.setMaximumWidth(
                16777215
            )

        else:
            self.content_layout.setDirection(
                QBoxLayout.LeftToRight
            )

            self.settings_card.setMinimumWidth(
                285
            )
            self.settings_card.setMaximumWidth(
                340
            )

            self.settings_card.setMinimumHeight(0)
            self.settings_card.setMaximumHeight(
                16777215
            )

            self.log_card.setMinimumWidth(0)
            self.log_card.setMaximumWidth(
                16777215
            )

        if width < 650:
            columns = 1
        elif width < 900:
            columns = 2
        else:
            columns = 4

        if columns != self.stats_columns:
            self.stats_columns = columns
            self.rebuild_stats_layout(
                columns
            )

        elif self.stats_layout.count() == 0:
            self.rebuild_stats_layout(
                columns
            )

    def rebuild_stats_layout(
        self,
        columns: int,
    ):
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.setParent(
                    self.stats_widget
                )

        for index, card in enumerate(
            self.stat_cards
        ):
            row = index // columns
            column = index % columns

            self.stats_layout.addWidget(
                card,
                row,
                column,
            )

        for column in range(columns):
            self.stats_layout.setColumnStretch(
                column,
                1,
            )

    # ------------------------------------------------------------------
    # Window controls
    # ------------------------------------------------------------------

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.maximize_button.setText("□")
        else:
            self.showMaximized()
            self.maximize_button.setText("❐")

    # ------------------------------------------------------------------
    # Worker control
    # ------------------------------------------------------------------

    def toggle_worker(self):
        if self.running:
            self.stop_worker()
        else:
            self.start_worker()

    def start_worker(self):
        hosts = [
            host.strip()
            for host in self.host_input.text().split(",")
            if host.strip()
        ]

        if not hosts:
            self.add_log(
                "error",
                "No hosts configured.",
            )
            return

        config = WorkerConfig(
            interval=self.interval_spin.value(),
            hosts=hosts,
            tcp_fallback=self.tcp_checkbox.isChecked(),
            check_ip=self.ip_checkbox.isChecked(),
            ip_check_every=self.ip_every_spin.value(),
        )

        self.worker = KeepAliveWorker(
            config
        )
        self.thread = QThread()

        self.worker.moveToThread(
            self.thread
        )

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.log.connect(
            self.on_log
        )
        self.worker.status.connect(
            self.on_status
        )
        self.worker.cycle_finished.connect(
            self.on_cycle
        )
        self.worker.ip_updated.connect(
            self.on_ip
        )
        self.worker.ip_changed.connect(
            self.on_ip_changed
        )

        self.worker.finished.connect(
            self.thread.quit
        )
        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )
        self.thread.finished.connect(
            self.on_thread_finished
        )

        self.running = True
        self.elapsed = 0

        self.set_settings_enabled(False)

        self.start_button.setText(
            "■   Stop Uplink"
        )

        self.hero_status.setText(
            "Connection guardian is active"
        )

        self.hero_description.setText(
            (
                "Network traffic is being generated "
                "according to your configuration."
            )
        )

        self.timer.start(1000)
        self.thread.start()

    def stop_worker(self):
        if self.worker:
            self.worker.stop()

        self.running = False
        self.timer.stop()

        self.countdown_label.setText("—")
        self.start_button.setText(
            "▶   Start Uplink"
        )

        self.set_settings_enabled(True)

        self.hero_status.setText(
            "Uplink stopped"
        )

        self.hero_description.setText(
            "The connection monitor is currently idle."
        )

        self.on_status("Stopped")

    def on_thread_finished(self):
        self.worker = None
        self.thread = None

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def set_settings_enabled(
        self,
        enabled: bool,
    ):
        self.interval_spin.setEnabled(
            enabled
        )
        self.host_input.setEnabled(
            enabled
        )
        self.tcp_checkbox.setEnabled(
            enabled
        )
        self.ip_checkbox.setEnabled(
            enabled
        )

        self.ip_every_spin.setEnabled(
            enabled
            and self.ip_checkbox.isChecked()
        )

    def ip_setting_changed(self):
        self.ip_every_spin.setEnabled(
            self.ip_checkbox.isChecked()
            and not self.running
        )

    # ------------------------------------------------------------------
    # Worker events
    # ------------------------------------------------------------------

    @Slot(str, str)
    def on_log(
        self,
        level: str,
        message: str,
    ):
        self.add_log(
            level,
            message,
        )

    def add_log(
        self,
        level: str,
        message: str,
    ):
        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )

        prefixes = {
            "info": "INFO",
            "success": " OK ",
            "warning": "WARN",
            "error": "ERR ",
        }

        prefix = prefixes.get(
            level,
            "INFO",
        )

        self.log_view.appendPlainText(
            f"[{timestamp}] "
            f"[{prefix}] "
            f"{message}"
        )

        scrollbar = (
            self.log_view.verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.maximum()
        )

    @Slot(str)
    def on_status(self, status: str):
        self.status_label.setText(
            status
        )

        self.status_dot.setObjectName(
            (
                "statusDotRunning"
                if status == "Running"
                else "statusDotStopped"
            )
        )

        self.status_dot.style().unpolish(
            self.status_dot
        )
        self.status_dot.style().polish(
            self.status_dot
        )

    @Slot(bool, str, int, int, int)
    def on_cycle(
        self,
        success: bool,
        host: str,
        cycle: int,
        successes: int,
        failures: int,
    ):
        self.target_label.setText(
            host
        )

        self.cycle_card.value_label.setText(
            str(cycle)
        )
        self.success_card.value_label.setText(
            str(successes)
        )
        self.failure_card.value_label.setText(
            str(failures)
        )

        self.elapsed = 0

        self.countdown_label.setText(
            f"{self.interval_spin.value()}s"
        )

    @Slot(str)
    def on_ip(self, ip: str):
        self.ip_card.value_label.setText(
            ip
        )

        self.ip_card.setProperty(
            "ipChanged",
            False,
        )

        self.ip_card.style().unpolish(
            self.ip_card
        )
        self.ip_card.style().polish(
            self.ip_card
        )

    @Slot(str, str)
    def on_ip_changed(
        self,
        old_ip: str,
        new_ip: str,
    ):
        self.ip_card.setProperty(
            "ipChanged",
            True,
        )

        self.ip_card.style().unpolish(
            self.ip_card
        )
        self.ip_card.style().polish(
            self.ip_card
        )

        self.add_log(
            "warning",
            (
                f"Public IP changed • "
                f"{old_ip} → {new_ip}"
            ),
        )

    # ------------------------------------------------------------------
    # Countdown
    # ------------------------------------------------------------------

    def update_countdown(self):
        if not self.running:
            return

        self.elapsed += 1

        remaining = max(
            self.interval_spin.value()
            - self.elapsed,
            0,
        )

        self.countdown_label.setText(
            f"{remaining}s"
        )

    # ------------------------------------------------------------------
    # Logs
    # ------------------------------------------------------------------

    def clear_logs(self):
        self.log_view.clear()

    # ------------------------------------------------------------------
    # Window events
    # ------------------------------------------------------------------

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_responsive_layout()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            event.buttons() & Qt.LeftButton
            and self.drag_position is not None
        ):
            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )

        super().mouseMoveEvent(event)

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()

        if self.thread:
            self.thread.quit()
            self.thread.wait(2000)

        event.accept()

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------

    def apply_styles(self):
        self.setStyleSheet(
            UPLINK_STYLE
        )