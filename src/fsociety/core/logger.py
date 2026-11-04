"""Logging setup."""

import logging
from pathlib import Path


def configure_logging(data_dir: Path, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("fsociety")
    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    data_dir.joinpath("logs").mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(data_dir / "logs" / "fsociety.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
    return logger
