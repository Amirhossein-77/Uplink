from __future__ import annotations

import json
import platform
import socket
import subprocess
import urllib.request

from config import IP_CHECK_URLS


def ping_host(host: str, timeout: int = 4) -> bool:
    """Send a single ICMP ping."""

    if platform.system().lower() == "windows":
        command = [
            "ping",
            "-n",
            "1",
            "-w",
            str(timeout * 1000),
            host,
        ]
    else:
        command = [
            "ping",
            "-c",
            "1",
            "-W",
            str(timeout),
            host,
        ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout + 2,
        )

        return result.returncode == 0

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def tcp_probe(
    host: str,
    port: int = 53,
    timeout: int = 4,
) -> bool:
    """Try to establish a TCP connection."""

    try:
        with socket.create_connection(
            (host, port),
            timeout=timeout,
        ):
            return True

    except OSError:
        return False


def get_public_ip(timeout: int = 5) -> str | None:
    """Try several services to determine the current public IP."""

    for url in IP_CHECK_URLS:
        try:
            with urllib.request.urlopen(
                url,
                timeout=timeout,
            ) as response:
                data = json.loads(
                    response.read().decode()
                )

                ip = data.get("ip") or data.get("ip_addr")

                if ip:
                    return str(ip)

        except (
            OSError,
            json.JSONDecodeError,
            ValueError,
        ):
            continue

    return None