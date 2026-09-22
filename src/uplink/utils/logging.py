from __future__ import annotations

import logging


def setup_logging(
    log_file: str | None = None,
):
    handlers = [
        logging.StreamHandler(),
    ]

    if log_file:
        handlers.append(
            logging.FileHandler(log_file)
        )

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s "
            "[%(levelname)s] "
            "%(message)s"
        ),
        handlers=handlers,
    )