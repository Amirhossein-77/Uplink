from __future__ import annotations

from dataclasses import dataclass


APP_NAME = "Uplink"

DEFAULT_HOSTS = [
    "1.1.1.1",
    "8.8.8.8",
    "9.9.9.9",
]

IP_CHECK_URLS = [
    "https://api.ipify.org?format=json",
    "https://ifconfig.me/all.json",
    "https://ipinfo.io/json",
]


@dataclass
class WorkerConfig:
    interval: int
    hosts: list[str]
    tcp_fallback: bool
    check_ip: bool
    ip_check_every: int