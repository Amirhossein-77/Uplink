from __future__ import annotations

import time

from PySide6.QtCore import QObject, Signal, Slot

from config import WorkerConfig
from network import get_public_ip, ping_host, tcp_probe


class KeepAliveWorker(QObject):
    log = Signal(str, str)
    status = Signal(str)
    cycle_finished = Signal(bool, str, int, int, int)
    ip_updated = Signal(str)
    ip_changed = Signal(str, str)
    finished = Signal()

    def __init__(self, config: WorkerConfig):
        super().__init__()

        self.config = config
        self.running = False

        self.cycle = 0
        self.successes = 0
        self.failures = 0
        self.host_index = 0
        self.last_ip: str | None = None

    @Slot()
    def run(self):
        self.running = True
        self.status.emit("Running")

        self.log.emit(
            "info",
            (
                f"Uplink started • interval={self.config.interval}s • "
                f"hosts={', '.join(self.config.hosts)}"
            ),
        )

        while self.running:
            host = self.config.hosts[
                self.host_index % len(self.config.hosts)
            ]
            self.host_index += 1
            self.cycle += 1

            self.log.emit(
                "info",
                f"Probing {host}...",
            )

            success = ping_host(host)

            if (
                not success
                and self.config.tcp_fallback
                and self.running
            ):
                self.log.emit(
                    "warning",
                    (
                        f"ICMP failed for {host} • "
                        "trying TCP fallback"
                    ),
                )

                success = tcp_probe(host)

            if success:
                self.successes += 1

                self.log.emit(
                    "success",
                    f"{host} responded successfully",
                )
            else:
                self.failures += 1

                self.log.emit(
                    "error",
                    f"{host} did not respond",
                )

            self.cycle_finished.emit(
                success,
                host,
                self.cycle,
                self.successes,
                self.failures,
            )

            if (
                self.running
                and self.config.check_ip
                and self.cycle % self.config.ip_check_every == 0
            ):
                self.check_public_ip()

            # Sleep in short increments so Stop remains responsive.
            for _ in range(self.config.interval * 10):
                if not self.running:
                    break

                time.sleep(0.1)

        self.status.emit("Stopped")
        self.log.emit("info", "Uplink stopped.")
        self.finished.emit()

    def check_public_ip(self):
        self.log.emit(
            "info",
            "Checking public IP...",
        )

        current_ip = get_public_ip()

        if current_ip is None:
            self.log.emit(
                "warning",
                "Unable to determine public IP",
            )
            return

        if self.last_ip is None:
            self.last_ip = current_ip

            self.ip_updated.emit(current_ip)

            self.log.emit(
                "success",
                f"Public IP detected • {current_ip}",
            )

            return

        if current_ip != self.last_ip:
            old_ip = self.last_ip
            self.last_ip = current_ip

            self.ip_updated.emit(current_ip)
            self.ip_changed.emit(
                old_ip,
                current_ip,
            )

            self.log.emit(
                "warning",
                (
                    f"PUBLIC IP CHANGED • "
                    f"{old_ip} → {current_ip}"
                ),
            )

            return

        self.ip_updated.emit(current_ip)

        self.log.emit(
            "info",
            f"Public IP unchanged • {current_ip}",
        )

    def stop(self):
        self.running = False