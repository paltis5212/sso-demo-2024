import logging
from logging.handlers import TimedRotatingFileHandler
from rich.logging import RichHandler

FORMATTER = logging.Formatter(
    "%(asctime)s | LEVEL: %(levelname)s | MESSAGE: %(message)s\n" + "._" * 40,
    "%Y-%m-%d %H:%M:%S",
)

def get_file_handler(path: str):
    """拿到會自己依日期分割的 handler"""
    file_handler = TimedRotatingFileHandler(
        path,  # type: ignore
        when="D",
        interval=1,
        encoding="utf-8",
        backupCount=7,
    )
    file_handler.setFormatter(FORMATTER)
    return file_handler

def get_rich_handler():
    """輸出美麗的畫面用的 handler"""
    rich_handler = RichHandler()
    return rich_handler