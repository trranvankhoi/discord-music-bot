from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path



def setup_logging(level: str = "INFO") -> None:
    log_dir = Path("bot/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level.upper())

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(fmt)

    file_handler = RotatingFileHandler(log_dir / "bot.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(fmt)

    root.handlers.clear()
    root.addHandler(console)
    root.addHandler(file_handler)
